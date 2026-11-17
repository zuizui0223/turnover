#!/usr/bin/env python3
"""Post-HOLD source-only missingness audit of predeclared Jena h1+leafN traits.

No new biological effect test, alternative trait pair, imputation or outcome.
"""
from __future__ import annotations
import argparse,collections,json,math
from pathlib import Path
from audit_jena_2020_original_csv_grain_v0_1 import get_orig
from audit_jena_2020_original_canonical_keys_v0_2 import TRAIT,csv_rows,code

SPECIES_EXPECTED=59
SOURCE_MIN=20
FIXED_TRAITS=("h1","leafN")

def state(v):
    s=str(v or "").strip()
    if not s or s.casefold() in {"na","nan","null","-9999"}:
        return "MISSING"
    try:x=float(s)
    except (ValueError,TypeError):return "NONNUMERIC"
    if not math.isfinite(x):return "NONFINITE"
    if x<0:return "NEGATIVE"
    if x==0:return "ZERO"
    return "POSITIVE"

def audit():
    h,rows=csv_rows(TRAIT)
    if len(rows)!=SPECIES_EXPECTED or not {"sp","h1","leafN"}.issubset(h):
        raise ValueError("SOURCE_HOLD: original Jena trait source schema changed")
    source_codes=[code(r["sp"]) for r in rows]
    if len(set(source_codes))!=59 or any(z is None for z in source_codes):
        raise ValueError("SOURCE_HOLD: original Jena trait identity drift")
    counts={axis:collections.Counter(state(r[axis]) for r in rows) for axis in FIXED_TRAITS}
    both=sum(all(state(r[t])=="POSITIVE" for t in FIXED_TRAITS) for r in rows)
    present_1only=sum(state(r["h1"])=="POSITIVE" and state(r["leafN"])!="POSITIVE" for r in rows)
    present_2only=sum(state(r["leafN"])=="POSITIVE" and state(r["h1"])!="POSITIVE" for r in rows)
    none=sum(all(state(r[t])!="POSITIVE" for t in FIXED_TRAITS) for r in rows)
    if both+present_1only+present_2only+none!=59:
        raise AssertionError("SOURCE_HOLD: raw trait original source state accounting inconsistent")
    return {
      "version":"v0.1",
      "status":"JENA_H1_LEAFN_PREDECLARED_RAW_TRAIT_SOURCE_COMPLETE_CASE_HOLD",
      "original_2020_author_Figshare_article":12834350,
      "original_trait_source_file_id":24365039,
      "original_trait_source_filename":TRAIT,
      "original_source_MD5_checked_by_get_orig":True,
      "original_trait_species_total":len(rows),
      "original_trait_column_count":len(h),
      "original_numeric_value_states":{k:dict(sorted(v.items())) for k,v in counts.items()},
      "original_taxa_with_both_h1_and_leafN_positive_finite":both,
      "original_taxa_h1_only_positive":present_1only,
      "original_taxa_leafN_only_positive":present_2only,
      "original_taxa_neither_trait_positive":none,
      "original_source_minimum_joint_species_before_any_prediction":SOURCE_MIN,
      "source_pair_support_pass":both>=SOURCE_MIN,
      "original_prior_biomass_effect_not_estimated":True,
      "trait_pair_and_source_thresholds_not_changed":True,
      "no_names_values_or_raw_original_data_exported":True,
      "no_imputation_added_after_failure":True,
      "original_authors_used_regularized_PCA_imputation_on_trait_table":True,
      "nonclaims":[
        "A source complete-case data shortage is not empirical evidence that FD lacks ecological productivity effects.",
        "Original 2020 paper's imputed trait matrix can be suitable for original published analyses but is not the raw 59 species×trait independent measured full matrix assumed by the frozen no-imputation test.",
        "No alternative trait pair, year split or trait source was selected after observing this null source support."
      ]
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        assert state("NaN")=="MISSING" and state("0")=="ZERO"
        assert state("10.1")=="POSITIVE" and state("-1")=="NEGATIVE"
        assert FIXED_TRAITS==("h1","leafN") and SOURCE_MIN==20
        print("ORIGINAL_JENA_RAW_TRAIT_PRESENCE_FIXTURE_PASS")
    else:
        if not args.out:p.error("--out mandatory")
        r=audit()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("JENA_ORIGINAL_H1_LEAFN_RAW_TRAIT_SOURCE_DIAGNOSTIC",
              json.dumps(r,sort_keys=True),flush=True)
