#!/usr/bin/env python3
"""Post-surprise source accounting diagnosis for TreeDivNet DS1 vs DS2 mass.

No original plot/mass/trait numeric values exported, no ecological model,
no post-outcome relabeling. Three candidate accounting identities fixed in
docs/TREEDIVNET_2026_SPECIES_MASS_SCALING_DIAGNOSIS_V0_1.md.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
import statistics
from pathlib import Path
from audit_treedivnet_figshare_original_join_v0_1 import load_table,key,norm,num

TOL_REL=.01
TOL_ABS=.001
KINDS=("direct_species_sum","mean_per_Ds2_species","mean_per_sown_richness")


def passes(y,x)->bool:
    return abs(y-x)<=max(TOL_ABS,TOL_REL*abs(y))


def quantiles(v):
    if not v:return None
    s=sorted(v)
    def q(t):
        i=(len(s)-1)*t
        a=int(i);f=i-a
        return s[a]+f*(s[min(a+1,len(s)-1)]-s[a])
    return {"median":q(.5),"q25":q(.25),"q75":q(.75)}


def assess():
    a,c1,_=load_table("DS1.xlsx")
    b,c2,_=load_table("DS2.xlsx")
    assert len(a)==363 and len(b)==689
    A={key(row):row for row in a}
    B=collections.defaultdict(list)
    for row in b:B[key(row)].append(row)
    if len(A)!=363 or len(B)!=340:raise ValueError("SOURCE_HOLD: original plot keys changed")
    joined=sorted(set(A)&set(B))
    if len(joined)!=328:raise ValueError("SOURCE_HOLD: join structure changed")
    tally=collections.Counter()
    bysite=collections.defaultdict(collections.Counter)
    byr=collections.defaultdict(collections.Counter)
    ratios_by_r=collections.defaultdict(list)
    ratios_by_site=collections.defaultdict(list)
    bad=collections.Counter()
    for identity in joined:
        parent=A[identity];children=B[identity]
        y=num(parent["biomass_woody"])
        vals=[num(c["biomass_woody"]) for c in children]
        if y is None or any(z is None for z in vals):
            bad["numeric_incomplete"]+=1
            continue
        n=len(children)
        species_count=num(parent["species_richness"])
        if not species_count or n==0:raise ValueError("SOURCE_HOLD: invalid richness")
        k=int(round(species_count))
        site=identity[0]
        rich_label=str(k) if k<=4 else "5plus"
        original=sum(vals)
        candidates={"direct_species_sum":original,
                    "mean_per_Ds2_species":original/n,
                    "mean_per_sown_richness":original/k}
        for kind,v in candidates.items():
            if passes(y,v):
                tally[kind]+=1
                bysite[site][kind]+=1
                byr[rich_label][kind]+=1
        tally["eligible_numeric"]+=1
        bysite[site]["eligible_numeric"]+=1
        byr[rich_label]["eligible_numeric"]+=1
        if n!=k:
            tally["species_sown_count_differs"]+=1
            bysite[site]["species_sown_count_differs"]+=1
        if y>0 and original>0:
            ratio=original/y
            ratios_by_r[rich_label].append(ratio)
            ratios_by_site[site].append(ratio)
    denomin=tally["eligible_numeric"]
    bysite_all={s:{"n_numeric":q["eligible_numeric"],
          "sum_match":q["direct_species_sum"],
          "equal_species_count_mean_match":q["mean_per_Ds2_species"],
          "sown_richness_mean_match":q["mean_per_sown_richness"],
          "source_mass_to_species_sum_ratio":quantiles(ratios_by_site[s])} for s,q in sorted(bysite.items())}
    byr_all={s:{"n_numeric":q["eligible_numeric"],
          "sum_match":q["direct_species_sum"],
          "equal_species_count_mean_match":q["mean_per_Ds2_species"],
          "sown_richness_mean_match":q["mean_per_sown_richness"],
          "source_mass_to_species_sum_ratio":quantiles(ratios_by_r[s])} for s,q in sorted(byr.items())}
    original_hierarchy=(tally["direct_species_sum"]/denomin if denomin else 0.)
    preferred={}
    for candidate in KINDS[1:]:
        rate=tally[candidate]/denomin if denomin else 0
        site9=sum(bysite[s][candidate]>=bysite[s]["direct_species_sum"] for s in bysite)
        preferred[candidate]={"original_plot_match_fraction":rate,
                              "sites_with_atleast_as_many_matches_as_sum":site9,
                              "pattern_found":bool(rate>=.9 and site9>=9)}
    if any(x["pattern_found"] for x in preferred.values()):
        status="SOURCE_SCALE_PATTERN_FOUND_UNCONFIRMED_PHYSICAL_MEANING"
    else:status="UNRESOLVED_SOURCE_SCALE_HOLD"
    return {"version":"v0.1","status":status,
       "source":"TreeDivNet Jensen et al 2026 Figshare v1",
       "source_only":True,
       "post_original_sum_failure_diagnostic":True,
       "source_original_plot_keys_joined":len(joined),
       "source_numeric_original_woody_mass_comparable_plots":denomin,
       "source_original_numeric_missingness":dict(bad),
       "original_strict_direct_sum_match_plots":tally["direct_species_sum"],
       "original_strict_direct_sum_match_fraction":original_hierarchy,
       "original_ds2_species_rows_not_equal_planted_richness":tally["species_sown_count_differs"],
       "candidate_matched_plot_totals":{k:tally[k] for k in KINDS},
       "candidate_match_fraction":{k:tally[k]/denomin if denomin else 0 for k in KINDS},
       "source_site_aggregates":bysite_all,
       "original_planted_richness_strata_aggregates":byr_all,
       "conditional_source_normalization_pattern":preferred,
       "source_evidence_not_accepted_as_confirmed_unit_conversion":True,
       "original_mass_source_qa_gate_stays_HOLD":True,
       "no_species_biomass_raw_rows_exported":True,
       "no_ecological_effect_fitted":True,
       "nonclaims":["Scale ratios alone cannot prove original Figshare per-species area representation",
                    "Do not change original woody mass response, reinterpret mass without original author metadata, or test effect with one of three chosen ratios",
                    "No family-specific trait K, FD or biomass association estimated"]}
def fixture():
    assert passes(100,100.9) and not passes(100,102)
    assert quantiles([1.,2.,3.])["median"]==2.
    assert len(KINDS)==3
    return {"status":"SOURCE_MASS_SCALING_DIAGNOSIS_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test: print(json.dumps(fixture()))
    else:
        if not a.out:p.error("--out required")
        d=assess()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("TREE_DIVNET_POST_SOURCE_SCALE_DIAGNOSIS",json.dumps(d,sort_keys=True),flush=True)
