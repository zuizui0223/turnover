#!/usr/bin/env python3
"""Outcome-blind structural eligibility of original BIODEPTH 2005 Figshare source.

Consumes source-original Design.txt, Shoots.txt downloaded with byte-pinned MD5.
Never estimates a diversity-biomass association or outputs biomass moments.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from collections import Counter,defaultdict
from pathlib import Path

ORIGINAL={
 "Design.txt":("29e7d05f45b8613d9bead9337da7d3cc",
               "a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a"),
 "Shoots.txt":("76824bf9ce195e84aa17ae4cd6c1a336",
               "cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135")
}
D_FIELDS=["plot","location","block","composition","species.richness","functional.richness","grasses","legumes","forbs"]
S_FIELDS=["year","plot","location","block","composition","species.richness","functional.richness","legumes","biomass"]
KEY_FIELDS=["plot"]
TREAT_FIELDS=["block","composition","species.richness","functional.richness","legumes"]

def get_table(path,filename):
    raw=Path(path).read_bytes()
    md,sha=ORIGINAL[filename]
    if hashlib.md5(raw).hexdigest()!=md or hashlib.sha256(raw).hexdigest()!=sha:
        raise ValueError("Original Figshare checksum mismatch: "+filename)
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")),delimiter="\t")
    fields=list(reader.fieldnames or [])
    if fields != (D_FIELDS if filename=="Design.txt" else S_FIELDS):
        raise ValueError(f"Unexpected original {filename} schema: {fields}")
    rows=list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("Malformed source rows/field widths")
    return rows,{"md5":md,"sha256":sha,"bytes":len(raw),"rows":len(rows),"headers":fields}
def integer(v,label):
    s=str(v).strip()
    if not s.lstrip("-").isdigit():
        raise ValueError(f"Noninteger source design {label}: {s[:30]}")
    return int(s)
def indicator(v,label):
    """The original Figshare 2005 Design.txt uses literal Yes/No fields."""
    text=str(v).strip().casefold()
    if text in ("yes","1"):return 1
    if text in ("no","0"):return 0
    raise ValueError(f"Unrecognized binary original group presence {label}: {text[:40]}")
def key(r):
    return tuple(str(r[c]).strip() for c in KEY_FIELDS)
def main(design_path,shoots_path):
    D,md=get_table(design_path,"Design.txt")
    S,ms=get_table(shoots_path,"Shoots.txt")
    assert indicator("Yes","grasses")==1 and indicator("No","legumes")==0
    if len(D)!=480 or len(S)!=1440:
        raise ValueError("BIODEPTH original expected 480/1440 source rows changed")
    by={}
    sites=defaultdict(list)
    group_values={g:Counter() for g in ("grasses","legumes","forbs")}
    for row in D:
        k=key(row)
        if k in by:raise ValueError("Duplicated original site x plot key")
        if not all(k):raise ValueError("Empty site/plot")
        richness=integer(row["species.richness"],"species.richness")
        fr=integer(row["functional.richness"],"functional.richness")
        flags={g:indicator(row[g],g) for g in group_values}
        if any(v not in (0,1) for v in flags.values()):
            raise ValueError("Original functional-group flag not binary")
        if richness<1 or richness>32 or fr not in (1,2,3) or sum(flags.values())!=fr:
            raise ValueError("Functional richness does not equal original guild flags")
        for g in group_values:group_values[g][flags[g]]+=1
        by[k]=row
        sites[row["location"].strip()].append(row)
    years=Counter()
    source_rows_per_plot=Counter()
    mismatch=Counter()
    response_status=Counter()
    per_site_year=Counter()
    numeric_site_to_named=defaultdict(set)
    named_to_numeric_site=defaultdict(set)
    for row in S:
        k=key(row)
        source_rows_per_plot[k]+=1
        years[str(row["year"]).strip()]+=1
        if k not in by:
            mismatch["unknown_plot"]+=1
            continue
        orig=by[k]
        numeric_site_to_named[str(row["location"]).strip()].add(orig["location"].strip())
        named_to_numeric_site[orig["location"].strip()].add(str(row["location"]).strip())
        per_site_year[(orig["location"].strip(),str(row["year"]).strip())]+=1
        for field in TREAT_FIELDS:
            if str(row[field]).strip()!=str(orig[field]).strip():
                mismatch[field]+=1
        raw=str(row["biomass"]).strip()
        if raw.lower() in ("","nan","na","n/a","null","."):
            response_status["missing_blank_or_NA"]+=1
        else:
            try:b=float(raw)
            except ValueError:response_status["unparseable"]+=1;continue
            if not math.isfinite(b):response_status["nonfinite"]+=1
            elif b==-9999:response_status["negative_missing_sentinel"]+=1
            elif b<0:response_status["other_negative"]+=1
            elif b==0:response_status["valid_zero"]+=1
            else:response_status["valid_positive"]+=1
    if mismatch:
        raise ValueError("Original source design and shoot treatment contradict: "+repr(dict(mismatch)))
    if len(numeric_site_to_named)!=len(sites) or len(named_to_numeric_site)!=len(sites) or\
       any(len(names)!=1 for names in numeric_site_to_named.values()) or\
       any(len(codes)!=1 for codes in named_to_numeric_site.values()):
        raise ValueError("Original Figshare numeric-versus-name location crosswalk is not one-to-one")
    if set(source_rows_per_plot)!=set(by):
        raise ValueError("Some original plot keys have no response rows")
    plot_repeat=Counter(source_rows_per_plot.values())
    eligible={}
    total_supported=0
    for site,rs in sorted(sites.items()):
        by_rich=defaultdict(list)
        for r in rs:by_rich[integer(r["species.richness"],"species.richness")].append(r)
        richness_support=[]
        eligible_plots=set()
        guild_vectors=set()
        for richness,block in sorted(by_rich.items()):
            nFG=len({integer(r["functional.richness"],"functional.richness") for r in block})
            if nFG>1:
                eligible_plots.update(key(r) for r in block)
            richness_support.append({"richness":richness,"n_plots":len(block),
                                    "n_distinct_FG_counts":nFG,
                                    "n_plots_in_within_richness_FG_variation":len(block) if nFG>1 else 0})
            for r in block:
                guild_vectors.add(tuple(indicator(r[g],g) for g in group_values))
        max_single_richness_support=max((item["n_plots"] for item in richness_support if item["n_distinct_FG_counts"]>1),default=0)
        is_eligible=len(rs)>=20 and max_single_richness_support>=20
        eligible[site]={"n_original_plots":len(rs),
                        "n_plots_within_richness_FG_support":len(eligible_plots),
                        "max_single_richness_treatment_support":max_single_richness_support,
                        "n_original_richness_levels":len(by_rich),
                        "n_distinct_guild_vectors":len(guild_vectors),
                        "n_original_blocks":len({r["block"].strip() for r in rs}),
                        "per_richness":richness_support,
                        "support_pass":is_eligible}
        if is_eligible:total_supported+=1
    n_response_valid=response_status["valid_positive"]+response_status["valid_zero"]
    status=("ORIGINAL_BIODEPTH_DESIGN_SOURCE_GATE_PASS"
            if len(sites)>=6 and len(by)>=250 and len(years)>=2
               and total_supported>=6 and n_response_valid>=len(S)*0.8
               and not response_status["other_negative"]
            else "ORIGINAL_BIODEPTH_DESIGN_SOURCE_GATE_HOLD")
    return {
        "version":"v0.1","status":status,"source_DOI":"10.6084/m9.figshare.3565170.v1",
        "license_original_figshare":"CC0",
        "source_files":{"Design.txt":md,"Shoots.txt":ms},
        "n_original_plot_keys":len(by),"n_original_sites":len(sites),
        "n_distinct_year_labels":len(years),"observed_year_labels":sorted(years),
        "original_shoot_rows_by_year":dict(years),
        "original_source_rows_per_plot_count_distribution":dict(plot_repeat),
        "n_original_site_plot_year_records":len(S),
        "numeric_Shoots_location_to_named_Design_location":{key:next(iter(val)) for key,val in sorted(numeric_site_to_named.items())},
        "n_plots_within_exact_site_richness_FG_variation":sum(x["n_plots_within_richness_FG_support"] for x in eligible.values()),
        "grasses_original_source_constantly_present":group_values["grasses"][0]==0,
        "n_complete_source_design_treatment_matches":len(S),
        "n_source_valid_numeric_response_records":n_response_valid,
        "response_quality_counts_no_values":dict(response_status),
        "site_year_record_counts":{str(k[0])+"|"+str(k[1]):v for k,v in sorted(per_site_year.items())},
        "sites_with_one_exact_richness_level_having_20_plus_plots_and_2_FG_levels":total_supported,
        "n_sites_supported_after_collapsing_across_multiple_richness_levels_not_primary":sum(x["n_plots_within_richness_FG_support"]>=20 for x in eligible.values()),
        "site_design_support":eligible,
        "source_gate_thresholds":{"min_sites":6,"min_unique_plots":250,"min_years":2,
                       "min_sites_with_20_single_richness_plots_and_multiple_FG_levels":6,
                       "min_numeric_biomass_response_fraction":0.8},
        "biomass_units_and_measurement_period_not_independently_confirmed":True,
        "important_source_reconciliation":"Design location is text, Shoots location is 1–8 numeric; matched by globally unique plot, source code→site names verified one-to-one.",
        "mainline_eligibility_explanation":"Strict single-richness 20+ replicates per site required; aggregating 10+12+14 across richness strata cannot pass.",
        "ecological_effects_tested":False,
        "source_nominal_480_plot_x_3year_structure_verified":True,
        "hard_nonclaims":["Site-year rows are not independent field sites",
          "Prior paper Spehn et al. 2005 studied richness/FG diversity impacts on biomass",
          "Response biomass values, coefficients and any effects were not examined",
          "Source support is distinct from quality-qualified geographic extrapolation",
          "No original BIEN/NEON source gate was reopened"],
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--design",required=True)
    p.add_argument("--shoots",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result=main(args.design,args.shoots)
    dst=Path(args.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("BIODEPTH_TIER0_SOURCE_GEOMETRY",json.dumps(result,ensure_ascii=False,sort_keys=True))
    if result["status"]!="ORIGINAL_BIODEPTH_DESIGN_SOURCE_GATE_PASS":raise SystemExit(2)
