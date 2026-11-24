#!/usr/bin/env python3
"""Original E141 monoculture assignment and independently sourced SLA coverage gate.

NO numerical biomass, cover or trait response values are read. Genuine planted
flags only. Trait presence is a conditional *author script provenance* statement,
NOT an original EDI measurement-source verification, and imputed taxa excluded.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

ORIGINAL_CSV="https://ndownloader.figshare.com/files/54836267"
ORIGINAL_MD5="8185b8effca37c8740ad065c53eb75d2"
AUTHOR_CLEANING_URL=("https://raw.githubusercontent.com/kaitkimmel/FDiv/"
  "e61c8814f3fc8e8fa7cac6141ee462c3e8b22554/R/CDRTraitCleaning.R")
AUTHOR_CLEANING_BLOB="e418bde5f8e09b515c3cd3a3b4f678ae24e97140"
AUTHOR_TREATED_CSVS={
    "cdrnaca_traitsout.csv":"295d760e6cde3102a8e5b4ef325f6ea7d0a8372f",
    "cdrnace_traitsout.csv":"f7fc222803afc40d5759ae5e650f82c9ce36cad9",
    "cdrneca_traitsout.csv":"f7a0b4cd6e20fe1865d134a96c0a256a330a4918",
    "cdrnece_traitsout.csv":"b94f2822a2ff066ce7933af4e075df3e20d845c2",
}
AUTHOR_BASE=("https://raw.githubusercontent.com/kaitkimmel/FDiv/"
 "e61c8814f3fc8e8fa7cac6141ee462c3e8b22554/data/Cleaned/")
MISSING_DIRECT_SLA=("Bouteloua gracilis","Poa pratensis")
SPECIES_4GROUP_SOURCE_N=16
MIN_ORIGINAL_MONOCULTURE_PLOTS_PER_TREATMENT_SPECIES=2
MIN_PLOT_TRAIT_SPECIES_COVERAGE=0.80
SOURCE_YEAR_RANGE=(1998,2021)
OUT=Path("results/biocon_e141_source_mono_SLA_direct_provenance_20261124_v0_1.json")

def fetch(url: str, cap: int=4_000_000) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"turnover-e141-mono-source-gate/1.0"})
    with urllib.request.urlopen(req,timeout=35) as response:
        data=response.read(cap+1)
    if len(data)>cap:raise ValueError("Official source exceeds byte cap")
    return data

def git_blob(content: bytes) -> str:
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\x00"+content).hexdigest()

def flag(raw: str):
    s=(raw or "").strip()
    if s=="1":return 1
    if s=="":return 0
    return None

def assign_counts(data: bytes) -> dict:
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    h=reader.fieldnames or []
    plant_cols=[z for z in h if z.endswith(" planted")]
    if len(plant_cols)!=16:raise ValueError("Original planted indicator design changed")
    # Official CSV contains abbreviated "Ach.mil planted" flags and fully
    # named "Achillea millefolium (g/m^2)" columns in corresponding order.
    # Verify the mapping by unique genus+epithet 3-letter abbreviations;
    # NEVER accept arbitrary positional association without full validation.
    # The 16 original source species biomass columns are the contiguous
    # group AFTER Monogroup and BEFORE AbovegroundTotal Biomass, followed
    # separately by Miscellaneous Litter (g/m^2), not a 17th plant taxon.
    try:
        sp_start=h.index("Monogroup")+1
        sp_end=h.index("AbovegroundTotal Biomass (g/m^2)")
    except ValueError as exc:
        raise ValueError("Missing source Monogroup/total biomass column boundaries") from exc
    raw_species_cols=h[sp_start:sp_end]
    if len(raw_species_cols)!=16 or not all(z.endswith(" (g/m^2)") for z in raw_species_cols):
        raise ValueError("Official source species biomass contiguous 16-column block failed")
    species_full=[z.removesuffix(" (g/m^2)") for z in raw_species_cols]
    if len(species_full)!=len(plant_cols):raise ValueError("Source flag/full-name mapping has unequal lengths")
    def code_of(full):
        parts=full.split()
        if len(parts)!=2 or any(len(x)<3 for x in parts):
            raise ValueError("Unexpected original full species-name tokenization")
        return parts[0][:3].casefold()+"."+parts[1][:3].casefold()
    species_abbrev=[z.removesuffix(" planted").casefold() for z in plant_cols]
    if len(set(species_abbrev))!=16 or len(set(species_full))!=16:
        raise ValueError("Original abbreviation/full-name collisions")
    predicted=[code_of(n) for n in species_full]
    if predicted!=species_abbrev:
        raise ValueError("Source full-name-to-planting-code positional crosswalk failed")
    target=set(MISSING_DIRECT_SLA)
    if not target.issubset(set(species_full)):
        raise ValueError("Original SLA provenance missing-species list conflicts with source full names")
    present_index=[i for i,sp in enumerate(species_full) if sp not in target]
    missing_index=[i for i,sp in enumerate(species_full) if sp in target]
    mono=collections.defaultdict(set)
    combos=collections.defaultdict(set)
    distinct_plots={}
    original_years=set()
    for row in reader:
        plot_id=((row.get("Ring") or "").strip(),(row.get("Plot") or "").strip())
        yr=(row.get("year") or "").strip()
        n=(row.get("CountOfSpecies") or "").strip()
        exp=(row.get("Experiment") or "").strip()
        c=(row.get("CO2 Treatment") or "").strip()
        N=(row.get("Nitrogen Treatment") or "").strip()
        if not all(plot_id) or not all((yr,n,exp,c,N)):raise ValueError("Missing planted design identity")
        vals=[flag(row.get(z)) for z in plant_cols]
        if None in vals:raise ValueError("Unexpected source planting indicator code")
        if sum(vals)!=int(n):raise ValueError("Original count-sown flag mismatch")
        ident=(exp,c,N,tuple(vals))
        if plot_id in distinct_plots:
            if distinct_plots[plot_id]!=ident:raise ValueError("Original plot sown composition/treatment changed over time")
        else:distinct_plots[plot_id]=ident
        if int(n)>0 and n=="1" and exp=="M":
            i=vals.index(1)
            mono[(c,N,i)].add(plot_id)
        if exp=="M" and n in ("4","9","16"):
            combos[(c,N,n,plot_id)]=vals
        original_years.add(yr)
    if original_years!={str(y) for y in range(SOURCE_YEAR_RANGE[0],SOURCE_YEAR_RANGE[1]+1)}:
        raise ValueError("Unexpected source year coverage")
    original_cells=sorted(mono.keys())
    expected_cells={(c,N,i) for c in ("Camb","Cenrich")
                    for N in ("Namb","Nenrich") for i in range(16)}
    missing_monos=sorted(expected_cells-set(mono))
    insuff=[k for k,plots in mono.items() if len(plots)<MIN_ORIGINAL_MONOCULTURE_PLOTS_PER_TREATMENT_SPECIES]
    coverage=collections.Counter()
    coverage_by_group=collections.Counter()
    full_species_mixture=collections.Counter()
    for (c,N,n,plot),vals in combos.items():
        planted=sum(vals)
        sourced=sum(vals[i] for i in present_index)
        fraction=sourced/planted
        ok=sourced>=2 and fraction>=MIN_PLOT_TRAIT_SPECIES_COVERAGE
        coverage[("eligible" if ok else "ineligible",n)]+=1
        coverage_by_group[(c,N,n,"eligible" if ok else "ineligible")]+=1
        full_species_mixture[(n,planted,sourced)]+=1
    return {
        "official_abbrev_full_name_source_crosswalk_16_of_16":True,
        "original_plant_abbrev_n":len(species_abbrev),
        "original_distinct_physical_plots":len(distinct_plots),
        "main_mono_original_treatment_species_cells_observed":len(original_cells),
        "main_mono_expected_original_cells":len(expected_cells),
        "mono_cell_missing_count":len(missing_monos),
        "mono_cells_below_two_source_plots":len(insuff),
        "monoculture_cell_replicate_histogram":dict(sorted(collections.Counter(map(len,mono.values())).items())),
        "original_mono_unique_physical_plots":len(set.union(*mono.values())) if mono else 0,
        "source_main_richness4_9_16_mixture_plot_count":len(combos),
        "author_code_only_direct_SLA_candidate_plant_species_count":len(present_index),
        "author_code_only_externally_substituted_SLA_species_count":len(missing_index),
        "source_coverage_threshold":MIN_PLOT_TRAIT_SPECIES_COVERAGE,
        "source_mixture_support_by_richness": [
            {"richness":n,"n_original_plots":sum(coverage[(z,n)] for z in ("eligible","ineligible")),
             "n_eligible_candidate_direct_SLA":coverage[("eligible",n)],
             "n_ineligible_candidate_direct_SLA":coverage[("ineligible",n)]}
            for n in ("4","9","16")],
        "source_mixture_support_by_CO2_N_richness":[
            {"CO2":c,"N":N,"richness":n,"n_eligible_candidate_SLA":coverage_by_group[(c,N,n,"eligible")],
             "n_ineligible_candidate_SLA":coverage_by_group[(c,N,n,"ineligible")]}
            for c in ("Camb","Cenrich") for N in ("Namb","Nenrich") for n in ("4","9","16")],
        "source_species_coverage_histogram_on_original_planted_mixtures":[
            {"richness":n,"sown":planted,"author_provenance_direct_SLA_count":sourced,"n_unique_source_plots":ct}
            for (n,planted,sourced),ct in sorted(full_species_mixture.items())],
        "numeric_original_biomass_read":False,
        "numeric_species_biomass_read":False,
        "numeric_trait_values_read":False,
        "statistical_models_fitted":0,
    }

def inspect_author_trait_provenance() -> dict:
    raw=fetch(AUTHOR_CLEANING_URL,60_000)
    if git_blob(raw)!=AUTHOR_CLEANING_BLOB:raise ValueError("Author original cleaning code SHA mismatch")
    code=raw.decode("utf-8")
    checks={
        "original_SLA_source_56_of_64": "## SLA (56/64)" in code,
        "original_rootCN_source_61_of_64": "## Root %C & %N (61/64)" in code,
        "original_seedmass_source_44_of_64": "## Seed mass (44/64)" in code,
        "external_bigbio_trait_source": "cdr.bigbiotraits <- read.delim(" in code,
        "direct_SLA_bouteloua_overwritten": 'newdf$SLA[newdf$monospecies == "Bouteloua gracilis"]' in code,
        "direct_SLA_poa_overwritten": 'newdf$SLA[newdf$monospecies == "Poa pratensis"]' in code,
        "rootCN_anemone_other_treatment_copy":'newdf$Root_C[newdf$monospecies == "Anemone cylindrica"]' in code,
        "seedmass_external_five_species":all('newdf$Seed_mass[newdf$monospecies == "'+s+'"]' in code for s in (
            "Achillea millefolium","Amorpha canescens","Anemone cylindrica",
            "Asclepias tuberosa","Petalostemum villosum")),
    }
    if not all(checks.values()):raise ValueError("External imputation markers changed; no silent pass")
    author_rows={}
    for name,want_sha in AUTHOR_TREATED_CSVS.items():
        raw=fetch(AUTHOR_BASE+name,40_000)
        if git_blob(raw)!=want_sha:raise ValueError(f"Author {name} blob changed")
        reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
        names=set()
        raw_rows=0
        numeric_values_read=False
        for row in reader:
            raw_rows+=1
            # Design identity only; original calculated trait numeric columns ignored.
            names.add(row.get("monospecies",""))
        author_rows[name]={"original_rows":raw_rows,"distinct_species_source_labels":len(names),
                           "original_trait_numeric_values_opened":numeric_values_read,
                           "blob_sha":want_sha}
    return {"source_repo_commit":"e61c8814f3fc8e8fa7cac6141ee462c3e8b22554",
            "source_cleaning_code_sha":AUTHOR_CLEANING_BLOB,
            "author_code_explicit_imputation_marks":checks,
            "already_processed_trait_tables":{"note":"treated CSV values include Big Bio substitution and cross-treatment copy; do not use them as wholly observed original data",
                "sources":author_rows},
            "original_EDI_leaf_traits_retrieved":False,
            "trait_observation_years_certified_as_premixing":False}

def selftest():
    assert flag("1")==1 and flag("")==0 and flag("NA") is None
    assert git_blob(b"abc")=="f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f"
    print("SYNTHETIC_PLANTING_MONO_AND_AUTHOR_BLOB_CHECK_PASS")

def main():
    output={
        "as_of_jst":"2026-11-24",
        "original_field_programme":"Cedar Creek E141 BioCON, one experimental site",
        "original_author_trait_code_provenance":"Ohlert et al. (2024) original code, published e61c8814",
        "status":"SOURCE_MIX_MONOCULTURE_TRAIT_PROVENANCE_HOLD",
        "raw_original_response_values_opened":False,
        "raw_original_trait_numeric_values_opened":False,
        "new_ecological_effects_fitted":0,
    }
    try:
        output["last_source_gate"]="retrieve_original_E141_CSV"
        blob=fetch(ORIGINAL_CSV)
        output["last_source_gate"]="validate_original_E141_MD5"
        if hashlib.md5(blob).hexdigest()!=ORIGINAL_MD5:raise ValueError("Original E141 author source MD5 mismatch")
        output["last_source_gate"]="original_mono_and_sown_design_support"
        output["source_mono_and_planting_support"]=assign_counts(blob)
        output["last_source_gate"]="pinned_Ohlert2024_trait_code_and_tables"
        output["author_trait_provenance"]=inspect_author_trait_provenance()
        output["last_source_gate"]="all_source_checks_passed"
        output["status"]="ORIGINAL_MONO_DESIGN_AND_SLA_SOURCE_PROVENANCE_CHECKED_TRAIT_TIME_HOLD"
        output["next_gate"]="Verify originally measured source trait records and acquisition years vs biomass outcomes (authors' completed 16-species trait CSV has imputed E120/Big Bio values). Source assignment eligibility does NOT establish causal FD or cross-site generalization."
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,KeyError,TypeError,
            AssertionError,UnicodeError,csv.Error) as exc:
        output["status"]="SOURCE_ACCESS_OR_PROVENANCE_HOLD"
        output["failure_class"]=type(exc).__name__
        output["failure_reason_source_only"]=str(exc)[:220] if isinstance(exc,ValueError) else "non-ValueError; source endpoint or schema"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=False))

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--selftest",action="store_true")
    a.add_argument("--source",action="store_true")
    opts=a.parse_args()
    if opts.selftest:selftest()
    elif opts.source:main()
    else:a.error("choose --selftest or --source")
