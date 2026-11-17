#!/usr/bin/env python3
"""Post-source-HOLD original Jena signed h1/leafN trait scale diagnosis only.

No new effect, trait pair change, outcome file open, imputation or result tuning.
Original traits.st.csv 59 species / Figshare #24365039 MD5 verified.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np
from audit_jena_2020_original_canonical_keys_v0_2 import csv_rows,TRAIT,code

AXES=("h1","leafN")
EXPECTED_SPECIES=59
MD5="8045e7ee38f26b212dbe81aed0039765"


def numeric(v):
    s=str(v or "").strip()
    if not s or s.lower() in ("na","nan","null","-9999","-9999.0"):
        return None
    try:
        x=float(s)
        return x if math.isfinite(x) else None
    except Exception:return None


def main():
    head,rows=csv_rows(TRAIT)
    assert len(rows)==EXPECTED_SPECIES and all(x in head for x in (*AXES,"sp"))
    all_names=[code(x["sp"]) for x in rows]
    if len(set(all_names))!=59 or any(x is None for x in all_names):
        raise ValueError("SOURCE_HOLD: original source species identifiers changed")
    counts={}
    vals={}
    for axis in AXES:
        data=[numeric(x[axis]) for x in rows]
        valid=np.asarray([x for x in data if x is not None],dtype=float)
        vals[axis]=data
        if len(valid)==0:raise ValueError("SOURCE_HOLD: missing all original axis values")
        counts[axis]={
            "n_total_original_species":len(data),"n_finite_signed_source_values":len(valid),
            "n_missing_nonfinite_or_non_numeric":len(data)-len(valid),
            "n_negative_finite":int(np.sum(valid<0)),
            "n_zero_finite":int(np.sum(valid==0)),
            "n_positive_finite":int(np.sum(valid>0)),
            "finite_source_mean":float(np.mean(valid)),
            "finite_source_sd_sample":float(np.std(valid,ddof=1)) if len(valid)>1 else 0.,
            "finite_source_sd_population":float(np.std(valid,ddof=0)),
            "finite_source_median":float(np.median(valid)),
            "finite_source_min":float(np.min(valid)),
            "finite_source_max":float(np.max(valid)),
            "source_approximately_centered_and_unit_scaled":bool(
                abs(float(np.mean(valid)))<.075 and .85<float(np.std(valid,ddof=1))<1.15)
        }
    joint=[(a,b) for a,b in zip(vals["h1"],vals["leafN"]) if a is not None and b is not None]
    both_positive=sum(a>0 and b>0 for a,b in joint)
    return {
      "version":"v0.2",
      "status":"ORIGINAL_JENA_H1_LEAFN_SIGNED_SCALE_SOURCE_SEMANTICS_AUDITED",
      "original_2020_author_Figshare_article":12834350,
      "source_file":"traits.st.csv","source_id":24365039,"expected_original_MD5":MD5,
      "source_original_csv_MD5_verified_on_download":True,
      "n_source_original_species":EXPECTED_SPECIES,
      "signed_numeric_field_summary":counts,
      "n_joint_finite_signed_h1_and_leafN_original_species":len(joint),
      "n_joint_strictly_positive_h1_and_leafN_original_species":both_positive,
      "old_original_positive_only_source_GATE_HOLD_preserved":True,
      "source_original_author_main_r_code_reads_traits_st_csv_and_imputesPCA_but_does_not_log_h1_or_leafN_before_FD":True,
      "original_author_full_41trait_imputed_FD_not_reproduced":True,
      "source_semantic_diagnosis":"Original h1 and leafN have many negative numerical values. These are finite signed original-file values, not biological negative meters or percent leaf nitrogen; their physical units and original transform require original metadata. If near-centered/unit-variance, treat as provided transformed source scale, and NEVER apply log again.",
      "no_original_plot_cover_or_biomass_response_values_opened":True,
      "no_new_FD_K_or_biomass_effect_estimated":True,
      "source_predicate_for_possible_separately_frozen_signed_scale_test":bool(len(joint)>=20 and all(counts[x]["source_approximately_centered_and_unit_scaled"] for x in AXES))
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        assert numeric("-1.01")==-1.01
        assert numeric("0")==0
        assert numeric("NaN") is None
        assert AXES==("h1","leafN")
        print(json.dumps({"status":"JENA_SIGNED_SOURCE_TRAITS_FIXTURE_PASS","checks":4}))
    else:
        if not a.out:p.error("--out required")
        r=main()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("JENA_H1_LEAFN_ORIGINAL_SIGNED_SOURCE_SEMANTICS",json.dumps(r,sort_keys=True),flush=True)
