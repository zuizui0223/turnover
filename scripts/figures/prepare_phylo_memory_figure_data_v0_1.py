#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--repo-root",type=Path,default=Path("."))
ap.add_argument("--out-dir",type=Path,required=True)
a=ap.parse_args()
root=a.repo_root
out=a.out_dir
out.mkdir(parents=True,exist_ok=True)

def load(p):
    return json.loads((root/p).read_text())

m=load(Path("results/phylo_memory_measurability_v0_1/result.json"))
c=load(Path("results/phylo_memory_calibration_ceiling_v0_2/result.json"))
e=load(Path("results/phylo_memory_binary_ceiling_v0_3_1/result.json"))
v=load(Path("results/phylo_memory_binary_validity_tradeoff_v0_3_1/result.json"))
k=load(Path("results/phylo_memory_mk2_generator_v0_4_1/result.json"))
b=load(Path("results/phylo_memory_balance_normalized_v0_5/result.json"))

assert m["n_systems"]==722
assert c["semantic_summary"]["nominal_categorical"]["n"]==276
assert e["original_no_bracket"]["n"]==220
assert v["categorical_no_bracket"]["mechanism_counts"]=={"EFFECT_CEILING":195,"VALIDITY_COLLAPSE":25}
assert k["mk2"]["n_no_bracket"]==170
assert b["geometry_availability"]["n_analyzed"]==272
for key in ("continuous_scalar","nominal_categorical"):
    s=c["semantic_summary"][key]
    assert s["n_no_bracket"] + s["n_recovery_fail_after_calibration"] + s["n_s3_pass"] == s["n"]
assert abs(
    c["semantic_summary"]["nominal_categorical"]["no_bracket_rate"]
    - c["semantic_summary"]["continuous_scalar"]["no_bracket_rate"]
    - 0.6496813018552149
) < 1e-12

def write_csv(name,fieldnames,rows):
    p=out/name
    with p.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)

write_csv(
    "fig1_gate_partition.csv",
    ["representation","outcome","n","total","rate"],
    [
      {
        "representation":"Continuous scalar",
        "outcome":"Generator no-bracket",
        "n":c["semantic_summary"]["continuous_scalar"]["n_no_bracket"],
        "total":c["semantic_summary"]["continuous_scalar"]["n"],
        "rate":c["semantic_summary"]["continuous_scalar"]["no_bracket_rate"]
      },
      {
        "representation":"Continuous scalar",
        "outcome":"Assigned, recovery failed",
        "n":c["semantic_summary"]["continuous_scalar"]["n_recovery_fail_after_calibration"],
        "total":c["semantic_summary"]["continuous_scalar"]["n"],
        "rate":c["semantic_summary"]["continuous_scalar"]["n_recovery_fail_after_calibration"]/c["semantic_summary"]["continuous_scalar"]["n"]
      },
      {
        "representation":"Continuous scalar",
        "outcome":"S3 recovery passed",
        "n":c["semantic_summary"]["continuous_scalar"]["n_s3_pass"],
        "total":c["semantic_summary"]["continuous_scalar"]["n"],
        "rate":c["semantic_summary"]["continuous_scalar"]["s3_pass_rate"]
      },
      {
        "representation":"Nominal categorical",
        "outcome":"Generator no-bracket",
        "n":c["semantic_summary"]["nominal_categorical"]["n_no_bracket"],
        "total":c["semantic_summary"]["nominal_categorical"]["n"],
        "rate":c["semantic_summary"]["nominal_categorical"]["no_bracket_rate"]
      },
      {
        "representation":"Nominal categorical",
        "outcome":"Assigned, recovery failed",
        "n":c["semantic_summary"]["nominal_categorical"]["n_recovery_fail_after_calibration"],
        "total":c["semantic_summary"]["nominal_categorical"]["n"],
        "rate":c["semantic_summary"]["nominal_categorical"]["n_recovery_fail_after_calibration"]/c["semantic_summary"]["nominal_categorical"]["n"]
      },
      {
        "representation":"Nominal categorical",
        "outcome":"S3 recovery passed",
        "n":c["semantic_summary"]["nominal_categorical"]["n_s3_pass"],
        "total":c["semantic_summary"]["nominal_categorical"]["n"],
        "rate":c["semantic_summary"]["nominal_categorical"]["s3_pass_rate"]
      }
    ]
)

write_csv(
    "fig2_accessibility.csv",
    ["quantity","value","denominator","note"],
    [
      {"quantity":"Target rho","value":e["benchmark"],"denominator":"","note":"declared target"},
      {"quantity":"Median max edge-split rho","value":e["edge_split_ceiling"]["median_no_bracket"],"denominator":220,"note":"realizable one-transition binary state"},
      {"quantity":"Median max OU-grid rho","value":e["generator_accessibility_gap"]["median_ou_max_grid_no_bracket"],"denominator":220,"note":"frozen latent-OU threshold generator"},
      {"quantity":"Effect ceiling","value":v["categorical_no_bracket"]["mechanism_counts"]["EFFECT_CEILING"],"denominator":220,"note":"never reaches rho=0.15 on finite OU grid"},
      {"quantity":"Validity collapse","value":v["categorical_no_bracket"]["mechanism_counts"]["VALIDITY_COLLAPSE"],"denominator":220,"note":"reaches target only below valid_fraction 0.90"}
    ]
)

write_csv(
    "fig3_sequential.csv",
    ["stage","no_bracket_rate","lower","upper","denominator"],
    [
      {"stage":"Latent-OU threshold","no_bracket_rate":c["semantic_summary"]["nominal_categorical"]["no_bracket_rate"],"lower":c["semantic_summary"]["nominal_categorical"]["no_bracket_rate"],"upper":c["semantic_summary"]["nominal_categorical"]["no_bracket_rate"],"denominator":276},
      {"stage":"Symmetric Mk2","no_bracket_rate":k["mk2"]["no_bracket_rate"],"lower":k["mk2"]["no_bracket_rate"],"upper":k["mk2"]["no_bracket_rate"],"denominator":276},
      {"stage":"Balance-normalized","no_bracket_rate":(b["full_population_bounds_from_geometry_holds"]["balance_normalized_no_bracket_rate_lower_if_all_holds_calibrate"]+b["full_population_bounds_from_geometry_holds"]["balance_normalized_no_bracket_rate_upper_if_all_holds_fail"])/2,"lower":b["full_population_bounds_from_geometry_holds"]["balance_normalized_no_bracket_rate_lower_if_all_holds_calibrate"],"upper":b["full_population_bounds_from_geometry_holds"]["balance_normalized_no_bracket_rate_upper_if_all_holds_fail"],"denominator":276}
    ]
)

write_csv(
    "fig3_paired.csv",
    ["transition","rescued","new_failure"],
    [
      {"transition":"OU → Mk2","rescued":k["paired_generator_comparison"]["ou_no_bracket_mk2_calibrated_rescued_n"],"new_failure":k["paired_generator_comparison"]["ou_calibrated_mk2_no_bracket_new_failure_n"]},
      {"transition":"Mk2 rho → Δrank","rescued":b["paired_balance_comparison_matched_subset"]["rescued_n"],"new_failure":b["paired_balance_comparison_matched_subset"]["new_failure_n"]}
    ]
)

write_csv(
    "fig3_recovery.csv",
    ["outcome","n","denominator"],
    [
      {"outcome":"PASS","n":k["mk2"]["n_s3_pass"],"denominator":k["mk2"]["n_calibrated"]},
      {"outcome":"Recovery fail","n":k["mk2"]["n_recovery_fail_after_calibration"],"denominator":k["mk2"]["n_calibrated"]}
    ]
)

manifest={
  "version":"v0.1",
  "status":"PHYLO_MEMORY_PRIMARY_FIGURE_DATA_PREPARED",
  "sources":[
    "results/phylo_memory_measurability_v0_1/result.json",
    "results/phylo_memory_calibration_ceiling_v0_2/result.json",
    "results/phylo_memory_binary_ceiling_v0_3_1/result.json",
    "results/phylo_memory_binary_validity_tradeoff_v0_3_1/result.json",
    "results/phylo_memory_mk2_generator_v0_4_1/result.json",
    "results/phylo_memory_balance_normalized_v0_5/result.json"
  ],
  "scientific_nonclaim":"Figure preparation introduces no new estimand or inference."
}
(out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps(manifest,indent=2))
