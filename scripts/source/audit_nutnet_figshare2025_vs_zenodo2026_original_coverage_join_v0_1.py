#!/usr/bin/env python3
"""Source-only cross-release NutNet 2025 Figshare botanical cover and
2026 Zenodo field biomass original site/plot/year ID intersection.

No ecological response calculations, FD or trait-K. Do not alter the
source's plot/season/treatment semantics to force a key match.
Frozen: docs/NUTNET_FIGSHARE_2025_SPECIES_PLOT_CROSSWALK_SOURCE_GATE_20261118.md
"""
from __future__ import annotations

import argparse,collections,csv,hashlib,io,json,math,re
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen

from audit_nutnet_corre_original_source_gate_v0_1 import (
    BASE, ZENODO_ID, FILE_DATA, FILE_META, request,
    verify_files, stable_id, numeric,
)

FIG_ID=52508654
FIG_MD5="2ab0e3bac17f0766265a4fdf23992fce"
FIG_SIZE=374626
FIG_ARTICLE=26412295
ZEN_DATA_MD5="c65e714c78fb2afb401e3b2ed6e625ae"
SOURCE_PLOT_MIN=100
SOURCE_SITE_MIN=15
SOURCE_TAXON_MIN_PER_PLOT=6
SOURCE_TAXON_PROP_MIN=.5
CONTROL_TERMS={"control","ctrl","ambient"}

def original_figshare():
    req=Request("https://api.figshare.com/v2/articles/"+str(FIG_ARTICLE),
                headers={"User-Agent":"turnover-FigshareNutNet2025-Zenodo2026-original-botanical-source-v0.1"})
    with urlopen(req,timeout=70) as r:
        if urlsplit(r.geturl()).hostname!="api.figshare.com":
            raise ValueError("FIGSHARE_METADATA_REDIRECT_HOLD")
        article=json.loads(r.read(1_500_000))
    if article.get("id")!=FIG_ARTICLE or article.get("version")!=4:
        raise ValueError("FIGSHARE_SOURCE_ID_OR_VERSION_HOLD")
    links={x.get("id"):x for x in article.get("files") or []}
    f=links.get(FIG_ID)
    if not f or f.get("computed_md5")!=FIG_MD5 or f.get("size")!=FIG_SIZE:
        raise ValueError("FIGSHARE_SOURCE_ORIGINAL_FILE_MD5_OR_SIZE_HOLD")
    original=str(f.get("download_url") or "")
    if urlsplit(original).hostname!="ndownloader.figshare.com" or urlsplit(original).path!="/files/"+str(FIG_ID):
        raise ValueError("FIGSHARE_ORIGINAL_FILE_ID_LINK_HOLD")
    with urlopen(Request(original,headers={"User-Agent":"turnover-original-nutnet-figshare-source-v0.1"}),timeout=90) as r:
        blob=r.read(FIG_SIZE+1)
    if len(blob)!=FIG_SIZE or hashlib.md5(blob).hexdigest()!=FIG_MD5:
        raise ValueError("FIGSHARE_SOURCE_ORIGINAL_FILE_CHECKSUM_HOLD")
    return blob


def original_zenodo():
    status,blob,hostname,ct=request(BASE+"/api/records/"+str(ZENODO_ID),1_000_000)
    if status!=200:raise ValueError("ZENODO_METADATA_ACCESS_HOLD")
    meta=json.loads(blob)
    if meta.get("id")!=ZENODO_ID:raise ValueError("ZENODO_SOURCE_VERSION_HOLD")
    chk,actual=verify_files(meta)
    if chk["status"]!="SOURCE_CHECKSUMS_PASS" or chk["original_data_md5"]!=ZEN_DATA_MD5:
        raise ValueError("ZENODO_SOURCE_BIOMASS_MD5_DRIFT")
    return actual[FILE_DATA]


def parse_csv(blob):
    reader=csv.DictReader(io.StringIO(blob.decode("utf-8-sig")))
    headers=reader.fieldnames or []
    if not headers or len(headers)!=len(set(headers)):
        raise ValueError("SOURCE_CSV_HEADERS_MALFORMED")
    rows=list(reader)
    if any(None in r for r in rows):raise ValueError("SOURCE_CSV_UNMATCHED_COLUMNS")
    return rows,headers


def has_binomial(value):
    x=" ".join(str(value or "").strip().split())
    # Exact original binomial only, no fuzzy synonyms or inferred taxa.
    return bool(re.fullmatch(r"[A-Z][a-z-]+ [a-z][a-z-]+",x))


def main():
    zen_csv=original_zenodo()
    fig_csv=original_figshare()
    zen,zh=parse_csv(zen_csv)
    fig,fh=parse_csv(fig_csv)
    for c in ("siteID","plotID","year","aboveground_biomass"):
        if c not in zh:raise ValueError("ZENODO_SOURCE_CSV_EXPECTED_COLUMN_MISSING_"+c)
    for c in ("site_code","block","plot","trt","year_trt","year","standard_taxon","max_cover"):
        if c not in fh:raise ValueError("FIGSHARE_SOURCE_CSV_EXPECTED_COLUMN_MISSING_"+c)
    if len(zen)!=1108:raise ValueError("PREVIOUS_ORIGINAL_2026_ZENODO_ROW_COUNT_DRIFT")

    zen_keys=set()
    zen_sy=set()
    zen_sites=set()
    zen_plot_per_site=collections.defaultdict(set)
    for r in zen:
        site=stable_id(r["siteID"])
        plot=stable_id(r["plotID"])
        year=stable_id(r["year"])
        if not all((site,plot,year)) or numeric(r["aboveground_biomass"]) is None or numeric(r["aboveground_biomass"])<0:
            raise ValueError("ZENODO_SOURCE_ORIGINAL_SOURCE_ROWS_INVALID")
        k=(site,plot,year)
        if k in zen_keys:raise ValueError("ZENODO_SOURCE_DUPLICATE_2026_PLOT_YEAR")
        zen_keys.add(k);zen_sy.add((site,year));zen_sites.add(site);zen_plot_per_site[site].add(plot)
    if len(zen_sites)!=130:raise ValueError("ZENODO_SOURCE_ORIGINAL_SITE_COUNT_DRIFT")

    fig_sites=set()
    fig_sy=set()
    fig_plot_year=set()
    trt=collections.Counter()
    yeartrt=collections.Counter()
    taxonomy=collections.Counter()
    badcover=0
    full_control={};baseline_control={}
    source_row_dup=0
    orig_spec_seen=set()
    site_without_2026=set()
    source_cover_row_records=0
    for row in fig:
        s=stable_id(row["site_code"])
        block=stable_id(row["block"])
        plot=stable_id(row["plot"])
        year=stable_id(row["year"])
        sp=" ".join(str(row["standard_taxon"] or "").strip().split())
        tt=str(row["trt"] or "").strip().casefold()
        trtyear=stable_id(row["year_trt"])
        value=numeric(row["max_cover"])
        trt[tt]+=1
        yeartrt[trtyear]+=1
        if not all((s,plot,year,sp)):
            raise ValueError("FIGSHARE_ORIGINAL_COVER_SOURCE_KEY_MISSING")
        fig_sites.add(s);fig_sy.add((s,year));fig_plot_year.add((s,plot,year))
        taxonomy["exact_genus_species_binomial_rows" if has_binomial(sp) else "nonbinomial_source_taxon_rows"]+=1
        if value is None or value<0:badcover+=1
        k=(s,block,plot,year,tt,sp)
        if k in orig_spec_seen:source_row_dup+=1
        orig_spec_seen.add(k)
        if tt in CONTROL_TERMS and value is not None and value>0 and has_binomial(sp):
            source_cover_row_records+=1
            z=(s,plot,year)
            full_control.setdefault(z,set()).add(sp)
            if trtyear in ("0","0.0"):
                baseline_control.setdefault(z,set()).add(sp)
    present_site=zen_sites&fig_sites
    zen_year_overlap=len(zen_sy&fig_sy)
    control_eligible=set(full_control)
    baseline_eligible=set(baseline_control)
    strict_crosswalk=zen_keys&control_eligible
    strict_base=zen_keys&baseline_eligible
    good_site={k[0] for k in strict_crosswalk}
    good_baseline_site={k[0] for k in strict_base}
    n_source_botanical_sites=len({k[0] for k in control_eligible})
    def stats_match(m):
        speciescount=[len(full_control[k]) if k in full_control else len(baseline_control.get(k,[])) for k in m]
        return {"n_original_matched_stand_plot_years":len(m),
                "n_original_matched_sites":len({k[0] for k in m}),
                "n_matching_keys_with_6plus_positive_exact_binomial_species":sum(x>=SOURCE_TAXON_MIN_PER_PLOT for x in speciescount),
                "fraction_matching_keys_with_6plus_species":sum(x>=SOURCE_TAXON_MIN_PER_PLOT for x in speciescount)/len(m) if m else None,
                "all_original_figshare_control_plotkey_time_match_no_fuzzy":True}
    a=stats_match(strict_crosswalk)
    b=stats_match(strict_base)
    qual=(a["n_original_matched_stand_plot_years"]>=SOURCE_PLOT_MIN and
          a["n_original_matched_sites"]>=SOURCE_SITE_MIN and
          a["fraction_matching_keys_with_6plus_species"] is not None and
          a["fraction_matching_keys_with_6plus_species"]>=SOURCE_TAXON_PROP_MIN)
    return {
      "version":"v0.1",
      "status":"ORIGINAL_FIGSHARE_ZENODO_EXACT_SOURCE_COMPOSITION_JOIN_PASS" if qual else "ORIGINAL_FIGSHARE_ZENODO_EXACT_SOURCE_COMPOSITION_JOIN_HOLD",
      "source_original_Figshare_2025":{
          "article_id":FIG_ARTICLE,"original_version":4,"source_approved_file_id":FIG_ID,"md5":FIG_MD5,"bytes":FIG_SIZE,
          "n_original_covered_taxon_rows":len(fig),
          "n_unique_original_source_sites":len(fig_sites),
          "n_unique_original_site_plot_year_keys":len(fig_plot_year),
          "n_source_binomial_taxon_rows":taxonomy["exact_genus_species_binomial_rows"],
          "n_source_unresolved_taxon_rows":taxonomy["nonbinomial_source_taxon_rows"],
          "n_negative_or_nonnumeric_cover":badcover,
          "n_original_duplicate_site_block_plot_year_species_treatment_rows":source_row_dup,
          "published_original_treatment_labels_row_counts":dict(trt),
          "published_original_year_treatment_relative_labels":dict(yeartrt),
          "n_positive_numeric_original_control_species_binomial_rows":source_cover_row_records,
          "n_original_sites_with_positive_botanical_control_rows":n_source_botanical_sites,
      },
      "source_original_Zenodo_2026":{"record_id":ZENODO_ID,"md5":ZEN_DATA_MD5,"n_source_unique_2026_biomass_plot_years":len(zen_keys),
        "n_original_biomass_sites":len(zen_sites),"year":"Original field calendar year","original_raw_species_records_in_Zenodo":False},
      "structural_overlap":{
         "n_site_codes_shared_verbatim":len(present_site),
         "n_shared_original_site_calendar_year_pairs":zen_year_overlap,
         "n_public_figshare_control_plot_year_keys":len(control_eligible),
         "n_public_figshare_control_year_trt_zero_plot_year_keys":len(baseline_eligible),
         "direct_original_site_plot_year_control_overlap":a,
         "direct_original_site_plot_year_control_year_trt0_overlap":b,
         "original_Zenodo_site_plotID_to_Figshare_block_or_plot_mapping_VERIFIED":False,
      },
      "source_only_gate_minima":{"min_direct_plot_year_matches":SOURCE_PLOT_MIN,
             "min_sites":SOURCE_SITE_MIN,"min_species_per_plot":SOURCE_TAXON_MIN_PER_PLOT,
             "min_fraction_matches_six_species":SOURCE_TAXON_PROP_MIN},
      "species_cover_not_species_biomass":True,
      "source_year_trt0_pre_treatment_interpretation_verified":False,
      "original_control_definition_certified_from_field_protocol":False,
      "no_species_taxon_names_or_original_site_plot_keys_exported":True,
      "no_phylogenetic_K_functional_FD_or_biomass_trait_association_estimated":True,
      "no_original_raw_species_dataset_republished":True,
      "next_step":"Use original NutNet plot-ID and treatment-year data dictionary if direct joined keys fail; do not invent block/plot transformations or treat control post-treatment as pretreatment baseline. Independently source original observed trait data before estimating K."
    }


def fixture():
    assert has_binomial("Poa pratensis")
    assert not has_binomial("Poa sp.")
    assert stable_id("005.0")=="5"
    assert SOURCE_PLOT_MIN==100
    return {"status":"NUTNET_2025_2026_BOTANICAL_SOURCE_CROSSWALK_FIXTURE_PASS","checks":4}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.out:p.error("--out required")
        d=main()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("NUTNET_PUBLIC_FIGSHARE_2025_ZENODO_2026_BOTANICAL_SOURCE_CROSSWALK",json.dumps(d,sort_keys=True),flush=True)
