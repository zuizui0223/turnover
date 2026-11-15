#!/usr/bin/env python3
"""Source-only 2005/2010 BIODEPTH biomass hierarchy reconciliation.

Never produce a plant trait or ecological guild effect. This checks whether
the 2010 species/group/community measures share a denominator and whether
the 2005 community Shoots table has numerically identical source values.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics
from pathlib import Path
from collections import Counter,defaultdict

SHA={
 "shoots2005":"cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135",
 "species2010":"ebe677c639ef4603bc1ed50d49e7440588683e7696be230c0cbfff7d6b22b816",
 "mixed2010":"9d95e65295bf6014e753f474dffa09036718b6b54ad5e1d4ee76f886",
}
TOL=1e-5
def source(path,label):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA[label]:
        raise ValueError("Published source byte hash mismatch: "+label)
    t=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")),delimiter="\t")
    rows=list(t)
    if not rows or any(None in r for r in rows):
        raise ValueError("Empty or malformed original tab-delimited "+label)
    return rows
def val(s):
    s=str(s or "").strip()
    if s.upper() in ("","NA","NAN","NULL",".","-9999"):
        return None
    x=float(s)
    if not math.isfinite(x) or x<0:
        raise ValueError("Invalid negative, non-finite source biomass value")
    return x
def key(row):
    return (str(row["plot"]).strip(),int(row["year"]))
def eq(a,b):
    return a is not None and b is not None and abs(a-b)<=TOL

def compare(ref,alt):
    """Aggregate-only numerical reconciliation, never raw source measurements."""
    keys=sorted(set(ref)|set(alt))
    valid=[(ref[k],alt[k]) for k in keys if k in ref and k in alt
           and ref[k] is not None and alt[k] is not None]
    delta=[b-a for a,b in valid]
    absdev=list(map(abs,delta))
    positive=[b/a for a,b in valid if a>0 and b>0]
    return {"source_A_keys":len(ref),"source_B_keys":len(alt),
            "same_source_keys":len(set(ref)&set(alt)),
            "n_numeric_comparable":len(valid),
            "n_exact_equal_1e-5":sum(d<=TOL for d in absdev),
            "n_unequal_1e-5":sum(d>TOL for d in absdev),
            "n_numeric_B_gt_A":sum(d>TOL for d in delta),
            "n_numeric_B_lt_A":sum(d< -TOL for d in delta),
            "median_abs_difference":statistics.median(absdev) if absdev else None,
            "max_abs_difference":max(absdev) if absdev else None,
            "median_positive_ratio_B_over_A":statistics.median(positive) if positive else None,
            "n_positive_ratio_pairs":len(positive)}

def sum_complete(table,source_keys):
    """Return sums only where every expected original child row has numeric biomass."""
    numeric={}
    incomplete=0
    for k,values in table.items():
        if values and all(v is not None for v in values):
            numeric[k]=sum(values)
        else:
            incomplete+=1
    return numeric,{"n_groups":len(table),"n_complete_groups":len(numeric),
                    "n_incomplete_groups":incomplete,
                    "n_expected_keys":len(source_keys)}

def audit(shoots,species,mixed):
    shoots=source(shoots,"shoots2005")
    species=source(species,"species2010")
    mixed=source(mixed,"mixed2010")
    if len(shoots)!=1440 or len(species)!=5802 or len(mixed)!=9816:
        raise ValueError("Original expected 1440/5802/9816 record grain changed")
    Y={}
    site_of={}
    yr_sites=defaultdict(set)
    for r in shoots:
        k=key(r)
        if k in Y:raise ValueError("Duplicated 2005 community plot-year row")
        Y[k]=val(r["biomass"])
        site_of[k]=str(r["location"]).strip()
        yr_sites[(site_of[k],k[1])].add(k)
    if len(Y)!=1440 or set(x[1] for x in Y)!={1,2,3}:
        raise ValueError("2005 source plot year population changed")
    S={}
    children_S=defaultdict(list)
    for r in species:
        k=key(r)
        specieskey=(k[0],k[1],r["species"].strip())
        if specieskey in S:raise ValueError("Duplicated 2010 independent species record")
        v=val(r["biomass"])
        S[specieskey]=v
        children_S[k].append(v)
        if k not in Y:raise ValueError("2010 species row not in original 2005 site plot year")
        if r["site"].strip()!=site_of[k]:
            raise ValueError("2010 species site not same as original 2005 plot site")
    if set(children_S)!=set(Y):
        raise ValueError("Some original 2005 plot-year lacks 2010 planted species records")
    L=Counter()
    mixed_species={}
    mixed_groups={}
    mixed_community={}
    children_g=defaultdict(list)
    children_ms=defaultdict(list)
    group_functors=Counter()
    malformed=Counter()
    for r in mixed:
        lv=str(r["level"]).strip().casefold()
        k=key(r)
        if k not in Y:raise ValueError("2010 mixed hierarchy row has unknown original plot-year")
        v=val(r["biomass"])
        L[lv]+=1
        if lv=="species":
            sp=(k[0],k[1],str(r["species"]).strip())
            if sp in mixed_species:raise ValueError("Duplicated 2010 hierarchy species row")
            mixed_species[sp]=v
            children_ms[k].append(v)
        elif lv=="group":
            fun=str(r["funct"]).strip().casefold()
            if fun not in ("g","f","l"):
                malformed["unknown_group_code"]+=1
            groupkey=(k[0],k[1],fun)
            if groupkey in mixed_groups:raise ValueError("Duplicate 2010 group per plot-year")
            mixed_groups[groupkey]=v
            children_g[k].append(v)
            group_functors[fun]+=1
        elif lv=="community":
            if k in mixed_community:raise ValueError("Duplicate 2010 community per plot-year")
            mixed_community[k]=v
        else:
            malformed["unrecognized_level"]+=1
    if malformed:
        raise ValueError("Mixed source unknown levels or group codes: "+repr(dict(malformed)))
    if set(mixed_species)!=set(S):
        raise ValueError("2010 hierarchy species keys do not equal separate 2010 SpeciesBiomass species keys")
    if len(mixed_community)!=1440 or set(mixed_community)!=set(Y):
        raise ValueError("2010 Community level does not contain exactly 1440 original plot-year keys")
    species_equal=sum(eq(S[k],mixed_species[k]) or
                       (S[k] is None and mixed_species[k] is None) for k in S)
    species_diff=[k for k in S if not (eq(S[k],mixed_species[k]) or
                       (S[k] is None and mixed_species[k] is None))]
    if species_diff:
        raise ValueError(f"Separate 2010 Species and hierarchy Species values disagree ({len(species_diff)} species-year rows)")
    ss,ssq=sum_complete(children_S,Y)
    gs,gsq=sum_complete(children_g,Y)
    ms,msq=sum_complete(children_ms,Y)
    pairs={
      "2010_species_sum_vs_2010_hierarchical_species_sum":compare(ss,ms),
      "2010_species_sum_vs_2010_group_sum":compare(ss,gs),
      "2010_species_sum_vs_2010_Community":compare(ss,mixed_community),
      "2010_group_sum_vs_2010_Community":compare(gs,mixed_community),
      "2010_Community_vs_2005_Shoots":compare(Y,mixed_community),
      "2010_species_sum_vs_2005_Shoots":compare(Y,ss),
    }
    # Separate 2010 3-level source identity, and previous 2005 discrepancy.
    groups_site_year={}
    for (site,year),keys in sorted(yr_sites.items()):
        keys=set(keys)
        pairs0={
          "2010_community_vs_2005":compare(
              {k:Y[k] for k in keys},{k:mixed_community[k] for k in keys}),
          "2010_species_complete_vs_2005":compare(
              {k:Y[k] for k in keys},{k:ss[k] for k in keys if k in ss}),
          "2010_group_complete_vs_2010_community":compare(
              {k:mixed_community[k] for k in keys},
              {k:gs[k] for k in keys if k in gs})
        }
        groups_site_year[f"{site}|year{year}"]=pairs0
    internal={
      "counts_by_original_level":dict(L),
      "2010_species_source_vs_hierarchy_row_count":len(S),
      "n_2010_species_rows_exactly_equal_in_two_files_including_NA":species_equal,
      "2010_group_functor_counts":dict(group_functors),
      "2010_hierarchical_group_rows":len(mixed_groups),
      "n_2010_Community_unique_plot_years":len(mixed_community),
      "numeric_community_values":sum(v is not None for v in mixed_community.values()),
      "2010_species_complete_groups":ssq,"2010_group_complete_groups":gsq,
      "2010_mixed_species_complete_groups":msq}
    within1=pairs["2010_species_sum_vs_2010_Community"]
    between=pairs["2010_Community_vs_2005_Shoots"]
    status=("WITHIN_2010_NUMERIC_HIERARCHY_AND_CROSS_2005_SOURCE_AGREED"
            if within1["n_unequal_1e-5"]==0 and between["n_unequal_1e-5"]==0
            else "WITHIN_2010_SOURCE_CONSISTENT_BUT_2005_RESPONSE_INCOMPATIBLE"
            if within1["n_unequal_1e-5"]==0 and
               pairs["2010_group_sum_vs_2010_Community"]["n_unequal_1e-5"]==0 and
               between["n_unequal_1e-5"]>0
            else "2010_LEVEL_VALUES_DISAGREE_AND_OR_CROSS_2005_INCOMPATIBLE")
    return {"version":"v0.1","status":status,
            "original_study":"BIODEPTH original 2005 Spehn vs original 2010 Hector, same 480 experimental plots",
            "n_distinct_original_plots":len({k[0] for k in Y}),
            "n_original_plot_years":len(Y),
            "source_sha256":SHA,
            "numeric_equality_tolerance":TOL,
            "internal_source_geometry":internal,
            "numeric_reconciliation_pairs":pairs,
            "source_site_year_QA":groups_site_year,
            "outcome_values_or_trait_effects_exported":False,
            "hard_nonclaims":[
               "This is a source consistency audit, not a biological effect or production estimate",
               "The mixed source has duplicate Species, Group and Community hierarchy; they MUST NOT be added together",
               "Missing original species/plant-group measurements are not zero",
               "Annual net productivity and clipped standing biomass cannot be equated without author methods",
               "Do not reconcile numeric disagreement by selecting convenient communities",
               "No quantitative functional diversity RaoQ, phylogenetic memory rho or biomass prediction tested",
               "Original high-support six-site source gate remains HOLD",
            ]}
def selftest():
    assert eq(0.,0.)
    assert not eq(None,0.)
    assert val("NA") is None and val("-9999") is None
    assert val("0")==0 and val("12.5")==12.5
    ok=compare({("a",1):10.,("a",2):None},{("a",1):10.0000001,("a",2):30.})
    assert ok["n_exact_equal_1e-5"]==1 and ok["n_numeric_comparable"]==1
    return {"status":"SELFTEST_SOURCE_HIERARCHY_QA_PASS","checks":5}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--shoots",required=False)
    ap.add_argument("--species",required=False)
    ap.add_argument("--mixed",required=False)
    ap.add_argument("--out",required=False)
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:
        print(json.dumps(selftest()))
    else:
        if not all((args.shoots,args.species,args.mixed,args.out)):
            ap.error("--shoots, --species, --mixed and --out required")
        result=audit(args.shoots,args.species,args.mixed)
        path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
        print("BIODEPTH_ORIGINAL_BIOMASS_HIERARCHY_QA",
              json.dumps({k:v for k,v in result.items() if k!="source_site_year_QA"},sort_keys=True))
