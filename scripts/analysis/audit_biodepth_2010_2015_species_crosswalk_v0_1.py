#!/usr/bin/env python3
"""Verify 2005 480-plot BIODEPTH sowing matrix against 2010 5802 species biomass rows.

Source-only quality contract; no FD or species-biomass ecological model.
Raw source remains temporary on Actions runners, never committed.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import rdata

SHA={
 "design":"a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a",
 "shoots":"cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135",
 "species_biomass":"ebe677c639ef4603bc1ed50d49e7440588683e7696be230c0cbfff7d6b22b816",
 "species_codes":"02ad483f727d4d10c10be7e7fe83e9e66c42803d6d08956d9397001dbf32f11b",
 "species_names":"141d49aa35ac3684c716b1e47e79341f0c3953829028348db0c34f85c259e2af",
 "sown_matrix_RDA":"86f650ca88dd0e91e044744e5c082290d87562044d3022fab05e7a64ab623290",
}
def raw(path,label):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=SHA[label]:raise ValueError("Original source checksum mismatch for "+label)
    return b
def tsv(path,label):
    return list(csv.DictReader(io.StringIO(raw(path,label).decode("utf-8-sig")),delimiter="\t"))
def plain_code(code):
    # 2010 original site/ecotype code: first letter group, second digit site, remainder species abbrev+1.
    if len(code)<7 or code[0].upper() not in ("G","H","L") or code[1] not in "12345678":
        raise ValueError("Unexpected original 2010 species ecotype code "+code[:30])
    return code[2:].upper()

def audit(inputs):
    D=tsv(inputs.design,"design")
    S=tsv(inputs.shoots,"shoots")
    species=tsv(inputs.species_biomass,"species_biomass")
    codes=tsv(inputs.species_codes,"species_codes")
    names=tsv(inputs.species_names,"species_names")
    R=rdata.conversion.convert(rdata.parser.parse_data(raw(inputs.sown_matrix_rda,"sown_matrix_RDA")))["all_biodepth"]
    if len(D)!=480 or len(S)!=1440 or len(species)!=5802 or len(codes)!=186 or len(names)!=103 or len(R)!=480 or len(R.columns)!=128:
        raise ValueError("Frozen source 2005 480x3, 2010 5802 species or 103 species names changed")
    byD={r["plot"]:r for r in D}
    if len(byD)!=480:raise ValueError("Duplicate 2005 plot keys")
    if R["plot"].duplicated().any() or set(R["plot"])!=set(byD):
        raise ValueError("R repackaging plot identifiers cannot exactly join original 2005 source")
    same=0
    guilds=0
    speciescols=list(R.columns)[25:]
    if len(speciescols)!=103:raise ValueError("R repackaging no longer has 103 seeded taxon columns")
    planted=set()
    for _,row in R.iterrows():
        p=str(row["plot"])
        source=byD[p]
        if row["location"]!=source["location"] or int(row["Diversity"])!=int(source["species.richness"]) or int(row["FR"])!=int(source["functional.richness"]) or int(row["Composition"])!=int(source["composition"]):
            raise ValueError("R repackaging design mismatch "+p+" values "+repr({"R_location":str(row["location"]),"D_location":source["location"],"R_diversity":int(row["Diversity"]),"D_diversity":int(source["species.richness"]),"R_FR":int(row["FR"]),"D_FR":int(source["functional.richness"]),"R_Composition":int(row["Composition"]),"D_composition":int(source["composition"])}))
        if int(row["site"])!=int(row["plot"][1:2]):
            # Plot B1P..., site should match numeric site ID 1..8
            raise ValueError("R row site-number inconsistent with encoded original plot ID")
        flags=[int(row["grasses"]),int(row["legumes"]),int(row["herbs"])]
        original_flags=[int(source[c]=="Yes") for c in ("grasses","legumes","forbs")]
        if flags!=original_flags:raise ValueError("Original guild flags vs R sown species matrix differ")
        guilds+=1
        active=[]
        for sp in speciescols:
            v=row[sp]
            if pd.isna(v):raise ValueError("Missing sown species indicator not allowed")
            if int(v) not in (0,1):raise ValueError("Original R planted species incidence must be 0/1")
            if int(v)==1:
                planted.add((p,sp))
                active.append(sp)
        if len(active)!=int(source["species.richness"]):
            raise ValueError("Sown species column sum does not equal original richness "+p)
        same+=1
    if len(planted)!=1934:raise ValueError("Unexpected 1934 original plot-species planted incidence pairs")
    # Original 2010 ecotypes and original 2015 package column abbreviations
    bycode={r["speciescode"]:r for r in codes}
    if len(bycode)!=186 or len({plain_code(k) for k in bycode})!=103:
        raise ValueError("2010 taxonomy coding no longer yields 103 unique species abbreviations")
    short_names={r["abbrevation"].upper()+"1":r for r in names}
    if len(short_names)!=103 or set(short_names)!=set(speciescols):
        raise ValueError("103 Linnaean binomial abbreviations do not match 103 R species incidence columns")
    mismatch_name=[]
    for code,info in bycode.items():
        k=plain_code(code)
        v=short_names.get(k)
        if v is None or info["genus"].strip()!=v["genus"].strip() or info["species"].strip()!=v["species"].strip():
            mismatch_name.append(code)
    # Some taxonomic naming differences are possible; report and HOLD, never silently normalize.
    orig_keys=set()
    duplicate=0;source_missing=Counter();taxon_unique=set()
    byplotyear=defaultdict(set)
    byplotyearbiom=defaultdict(float)
    invalidbiom=Counter()
    site_coded=Counter()
    for r in species:
        code=r["species"].strip()
        plot=r["plot"].strip()
        year=int(r["year"])
        if code not in bycode or year not in (1,2,3):
            raise ValueError("2010 species/ecotype or year unknown")
        if plot not in byD:source_missing["plot"]+=1;continue
        original=byD[plot]
        if r["site"].strip()!=original["location"] or int(r["sr"])!=int(original["species.richness"]) or int(r["fr"])!=int(original["functional.richness"]) or int(r["mix"])!=int(original["composition"]):
            source_missing["design_treatment_mismatch"]+=1
        if int(r["location"])!=int(plot[1]):
            source_missing["numeric_site_mismatch"]+=1
        k=(plot,year,code)
        if k in orig_keys:duplicate+=1
        orig_keys.add(k)
        abbrev=plain_code(code)
        if (plot,abbrev) not in planted:source_missing["not_sown_in_original_R_plants"]+=1
        if abbrev not in speciescols:source_missing["ecotype_abbrev_not_in_R_species_columns"]+=1
        info=bycode[code]
        taxon_unique.add((info["genus"],info["species"]))
        byplotyear[(plot,year)].add(abbrev)
        try:
            x=float(r["biomass"])
        except ValueError:
            invalidbiom["nonnumeric"]+=1
            continue
        if not math.isfinite(x):invalidbiom["nonfinite"]+=1
        elif x==-9999:invalidbiom["source_missing_sentinel"]+=1
        elif x<0:invalidbiom["other_negative"]+=1
        else:
            byplotyearbiom[(plot,year)]+=x
            if x==0:invalidbiom["valid_zero"]+=1
            else:invalidbiom["valid_positive"]+=1
        site_coded[code[1]]+=1
    if duplicate or source_missing:
        raise ValueError("2010 source has duplicated plant plot years or broken source provenance: "+repr((duplicate,dict(source_missing))))
    if len(orig_keys)!=5802 or len(byplotyear)!=1440 or len(taxon_unique)!=103:
        raise ValueError("2010 source keys not exactly 1934 planted species x 3 source years")
    from_year=Counter(k[1] for k in orig_keys)
    if sorted(from_year.items())!=[(1,1934),(2,1934),(3,1934)]:
        raise ValueError("Not exactly 1934 sown species each year")
    if any(len(byplotyear[(p,year)])!=int(byD[p]["species.richness"])
           for p in byD for year in (1,2,3)):
        raise ValueError("Species-level observed source values absent in at least one originally planted plot-year")
    # Test 2010 sown-only species sums against author 2005 aggregate Shoots, for
    # a data-definition compatibility check ONLY, not an ecological effect.
    agg={ (r["plot"].strip(),int(r["year"])):r for r in S}
    if len(agg)!=1440 or set(agg)!=set(byplotyear):
        raise ValueError("Original source 2005 1440 plot-year keys incompatible")
    n_agree=0;n_mismatch=0;n_numeric=0;gaps=[]
    for k,rec in agg.items():
        txt=rec["biomass"].strip()
        if not txt or txt.upper() in ("NA","NAN","NULL"):continue
        v=float(txt)
        if v==-9999 or not math.isfinite(v):continue
        if k not in byplotyearbiom:continue
        d=byplotyearbiom[k]-v
        n_numeric+=1
        if abs(d)<1e-5:n_agree+=1
        else:
            n_mismatch+=1
            gaps.append(abs(d))
    result={
      "version":"v0.1","status":"BIODEPTH_2010_SPECIES_KEY_BRIDGE_PASS" if not mismatch_name else "BIODEPTH_2010_TAXON_NAME_CONFLICT_HOLD",
      "source_hashes":SHA,"same_original_experiment":True,
      "n_original_2005_plots":480,"n_R_plots_exact_treatment_crosswalk":same,
      "n_R_guild_flags_exactly_match_original":guilds,
      "n_R_sown_species_columns":len(speciescols),
      "n_R_unique_species_plot_incidence":len(planted),
      "n_original_2010_ecotype_codes":len(bycode),
      "n_original_2010_species_binomial_pairs":len(taxon_unique),
      "n_original_2010_species_taxa_code_to_names_conflicts":len(mismatch_name),
      "unresolved_name_code_examples":mismatch_name[:10],
      "n_sown_species_codes_observed_for_all_three_years":len(orig_keys),
      "n_original_2010_species_per_year":dict(from_year),
      "n_original_species_plot_years":len(byplotyear),
      "n_species_biomass_missing_invalid_and_zero":dict(invalidbiom),
      "n_site_number_encoded_source_codes":len(site_coded),
      "original_2005_vs_2010_species_sum_biomass_QA":{
          "n_comparable_source_plot_years":n_numeric,
          "n_agree_tolerance_1e-5":n_agree,
          "n_different":n_mismatch,
          "absolute_difference_max_if_any":max(gaps) if gaps else 0,
          "warning":"Source-definitions could differ; no force matching or selecting on biomass."
      },
      "predeclared_tier0_thresholds":{"min_original_plots_with_species":350,
                                     "min_orig_sites":6,"min_years":2,
                                     "min_named_ecotypes":100},
      "raw_species_data_not_committed":True,
      "species_sown_or_realized_interpretation":"Binary R presence cols are original SOWN incidence; 2010 source reports planted species biomass every year including real zeros.",
      "no_traits_or_phylo_effects_opened":True,
      "hard_nonclaims":["2010 and 2005 are the same experiments, not independent sites",
                        "Plot-level sown species incidence is not realized flower/functional trait abundance",
                        "Known original 6-site high-coverage eligibility remains HOLD",
                        "No historical BIEN evolutionary rho relation or global FD-biomass association tested"]
    }
    return result
def fixture():
    assert plain_code("G1ALOPRA1")=="ALOPRA1"
    assert plain_code("L3TRIREP1")=="TRIREP1"
    assert plain_code("H8ACHMIL1")=="ACHMIL1"
    return {"status":"SPECIES_CODE_NORMALIZATION_FIXTURE_PASS","checks":3}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("design","shoots","species-biomass","species-codes","species-names","sown-matrix-rda","out"):
        p.add_argument("--"+name.replace("-","_"),dest=name.replace("-","_"))
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture()))
    else:
        if any(getattr(a,k,None) is None for k in ("design","shoots","species_biomass","species_codes","species_names","sown_matrix_rda","out")):
            p.error("All six source files and --out required")
        r=audit(a)
        out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
        print("BIODEPTH_SPECIES_FULL_KEY_QA",json.dumps(r,sort_keys=True))
        if r["status"]!="BIODEPTH_2010_SPECIES_KEY_BRIDGE_PASS":raise SystemExit(2)
