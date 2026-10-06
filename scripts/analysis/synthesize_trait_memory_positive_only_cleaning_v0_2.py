#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before use.
from __future__ import annotations
import argparse,json
from pathlib import Path

ap=argparse.ArgumentParser()
for flag in ["cleaned-aggregate","measurement","blup","null","original-measurement","original-blup","original-null","out"]:
    ap.add_argument("--"+flag,dest=flag.replace("-","_"),type=Path,required=True)
a=ap.parse_args()

load=lambda p: json.loads(p.read_text())
agg=load(a.cleaned_aggregate)
meas=load(a.measurement)
blup=load(a.blup)
null=load(a.null)
omeas=load(a.original_measurement)
oblup=load(a.original_blup)
onull=load(a.original_null)

if agg["status"]!="TRAIT_MEMORY_POSITIVE_ONLY_CLEANED_EFFECTS_AGGREGATED":
    raise SystemExit("cleaned aggregate not complete")
if not agg["all_201_support_retained"] or not agg["all_201_cleaned_log_available"]:
    raise SystemExit("Stage B all-201 support/log gate failed")
if meas["status"]!="TRAIT_MEMORY_MEASUREMENT_AWARE_ESTIMATED":
    raise SystemExit("cleaned measurement-aware model did not pass")
if blup["status"]!="TRAIT_MEMORY_BLUP_PORTABILITY_SENSITIVITY_ESTIMATED":
    raise SystemExit("cleaned BLUP model did not pass")
if null["status"]!="TRAIT_MEMORY_CORRELATED_TRAIT_NULL_ESTIMATED":
    raise SystemExit("cleaned correlated-trait null did not pass")
if not meas["log_scale"]["complete_all_201"]:
    raise SystemExit("cleaned all-201 log model incomplete")

def total_shares(s):
    fam=float(s["sigma2_family"]); tr=float(s["sigma2_trait"]); sys=float(s["sigma2_system"]); samp=float(s["mean_sampling_variance"])
    den=fam+tr+sys+samp
    return {"family":fam/den,"trait":tr/den,"system_heterogeneity":sys/den,"sampling_error":samp/den}

clean_raw_s3=meas["measurement_aware"]["S3"]
clean_raw_pr=meas["measurement_aware"]["prune_only"]
clean_log_s3=meas["log_scale"]["measurement_aware_S3"]
clean_log_pr=meas["log_scale"]["measurement_aware_prune_only"]

out={
  "version":"v0.2",
  "status":"TRAIT_MEMORY_POSITIVE_ONLY_CLEANING_IMPACT_COMPLETE",
  "data_contract_decision":"CLEANED_POSITIVE_ONLY_BECOMES_PRIMARY",
  "all_201_support_retained":True,
  "all_201_cleaned_log_available":True,
  "effect_impact":agg["impact"],
  "species_removed":agg["species_removed"],
  "cleaned_raw":{
    "naive_repeatability":{
      "S3":meas["recomputed_naive"]["S3"],
      "prune_only":meas["recomputed_naive"]["prune_only"]
    },
    "measurement_aware":{
      "S3":clean_raw_s3,
      "prune_only":clean_raw_pr,
      "S3_total_point_shares":total_shares(clean_raw_s3),
      "prune_total_point_shares":total_shares(clean_raw_pr),
      "S3_cluster_bootstrap":meas["measurement_aware"]["primary_S3_cluster_bootstrap"]
    },
    "portability":{"S3":blup["S3_raw"],"prune_only":blup["prune_raw"]},
    "correlated_trait_null":{"S3":null["S3"],"prune_only":null["prune_only"]}
  },
  "cleaned_log":{
    "naive_repeatability":{
      "S3":meas["log_scale"]["naive_S3"],
      "prune_only":meas["log_scale"]["naive_prune_only"]
    },
    "measurement_aware":{
      "S3":clean_log_s3,
      "prune_only":clean_log_pr,
      "S3_total_point_shares":total_shares(clean_log_s3),
      "prune_total_point_shares":total_shares(clean_log_pr)
    },
    "portability":{"S3":blup["S3_log"],"prune_only":blup["prune_log"]}
  },
  "original_RC3_reference":{
    "measurement_aware_S3_total_point_shares":omeas["measurement_aware"]["S3"]["point_total_variance_shares_using_mean_sampling_variance"],
    "BLUP_gain_S3":oblup["S3_raw"]["gain_blup"],
    "BLUP_gain_prune":oblup["prune_raw"]["gain_blup"],
    "correlated_trait_null_p_S3":onull["S3"]["p_family_ge_observed"],
    "correlated_trait_null_p_prune":onull["prune_only"]["p_family_ge_observed"]
  },
  "interpretation_guard":"Stage B is a data-validity correction triggered by semantically inadmissible raw values, not a robustness analysis selected for favorable manuscript impact. Cleaned positive-only values become the primary data contract because all 201 systems retain support."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
