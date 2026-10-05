#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
a=ap.parse_args()
a.out_dir.mkdir(parents=True,exist_ok=True)

rows=list(csv.DictReader(a.effects.open(newline="")))
if len(rows)!=201: raise SystemExit(f"expected 201 effects, got {len(rows)}")
families=sorted({r["family"] for r in rows})
traits=sorted({r["trait_name"] for r in rows})
if len(families)!=45 or len(traits)!=12: raise SystemExit("fixed core dimensions changed")

# Figure 1/2 matrix data: deterministic alphabetical ordering only.
with (a.out_dir/"memory_matrix.csv").open("w",newline="") as fh:
    fields=["family"]+traits
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
    lookup={(r["family"],r["trait_name"]):r for r in rows}
    for fam in families:
        rec={"family":fam}
        for tr in traits:
            x=lookup.get((fam,tr))
            rec[tr]="" if x is None else x["S3_rho"]
        w.writerow(rec)

# Figure 2/4 long data.
with (a.out_dir/"memory_effects.csv").open("w",newline="") as fh:
    fields=["family","trait_name","S3_rho","prune_only_rho","n_species_S3","n_species_prune"]
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
    for r in sorted(rows,key=lambda z:(z["family"],z["trait_name"])):
        w.writerow({k:r[k] for k in fields})

# Post-robustness primary figure source tables.
root=Path(".")
rep=json.loads((root/"results/trait_memory_repeatability_v0_2/result.json").read_text())
aware=json.loads((root/"results/trait_memory_measurement_aware_v0_3/result.json").read_text())
corr=json.loads((root/"results/trait_memory_correlated_trait_null_v0_3/result.json").read_text())
blup=json.loads((root/"results/trait_memory_portability_blup_v0_3/result.json").read_text())
geom=json.loads((root/"results/trait_memory_geometry_adjustment_v0_7_2/result.json").read_text())
src=json.loads((root/"results/trait_memory_source_composition_v0_1/result.json").read_text())

# Figure 1A/C: point decomposition.
variance_rows=[]
for axis,naive,aware_axis in [
    ("S3",rep["primary_S3"],aware["measurement_aware"]["S3"]),
    ("prune_only",rep["prune_only_sensitivity"],aware["measurement_aware"]["prune_only"])
]:
    variance_rows.extend([
      {"axis":axis,"model":"naive","component":"family","estimate":naive["R_family"]},
      {"axis":axis,"model":"naive","component":"trait","estimate":naive["R_trait"]},
      {"axis":axis,"model":"naive","component":"residual_unresolved","estimate":naive["R_residual"]},
    ])
    pts=aware_axis["point_total_variance_shares_using_mean_sampling_variance"]
    variance_rows.extend([
      {"axis":axis,"model":"measurement_aware","component":"family","estimate":pts["family"]},
      {"axis":axis,"model":"measurement_aware","component":"trait","estimate":pts["trait"]},
      {"axis":axis,"model":"measurement_aware","component":"system_heterogeneity","estimate":pts["system_heterogeneity"]},
      {"axis":axis,"model":"measurement_aware","component":"sampling_error","estimate":pts["sampling_error"]},
    ])
with (a.out_dir/"figure1_variance_shares.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["axis","model","component","estimate"]); w.writeheader(); w.writerows(variance_rows)

# Figure 1B: measurement-aware heterogeneity shares with crossed-cluster intervals.
ci=aware["measurement_aware"]["S3_two_way_cluster_bootstrap"]
het_rows=[
  {"component":"family","estimate":aware["measurement_aware"]["S3"]["family_share_of_heterogeneity"],"lo":ci["ci95_family_share_of_heterogeneity"][0],"hi":ci["ci95_family_share_of_heterogeneity"][1]},
  {"component":"trait","estimate":aware["measurement_aware"]["S3"]["trait_share_of_heterogeneity"],"lo":ci["ci95_trait_share_of_heterogeneity"][0],"hi":ci["ci95_trait_share_of_heterogeneity"][1]},
  {"component":"system","estimate":aware["measurement_aware"]["S3"]["system_share_of_heterogeneity"],"lo":ci["ci95_system_share_of_heterogeneity"][0],"hi":ci["ci95_system_share_of_heterogeneity"][1]}
]
with (a.out_dir/"figure1_heterogeneity_ci.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["component","estimate","lo","hi"]); w.writeheader(); w.writerows(het_rows)

# Figure 2: family-repeatability null and robustness summaries.
null_rows=[
  {"axis":"S3","observed":corr["S3"]["observed_R_family"],"null_median":corr["S3"]["R_family_null_median"],"lo":corr["S3"]["R_family_null_q025_q975"][0],"hi":corr["S3"]["R_family_null_q025_q975"][1],"p":corr["S3"]["p_family_ge_observed"]},
  {"axis":"prune_only","observed":corr["prune_only"]["observed_R_family"],"null_median":corr["prune_only"]["R_family_null_median"],"lo":corr["prune_only"]["R_family_null_q025_q975"][0],"hi":corr["prune_only"]["R_family_null_q025_q975"][1],"p":corr["prune_only"]["p_family_ge_observed"]}
]
with (a.out_dir/"figure2_correlated_trait_null.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["axis","observed","null_median","lo","hi","p"]); w.writeheader(); w.writerows(null_rows)

rob_rows=[
  {"analysis":"unadjusted","R_family":rep["primary_S3"]["R_family"]},
  {"analysis":"species_count","R_family":geom["coverage_only"]["S3"]["R_family"]},
  {"analysis":"geometry","R_family":geom["geometry_adjusted"]["R_family"]},
  {"analysis":"source","R_family":src["repeatability"]["source_adjusted_R_family"]},
  {"analysis":"citation","R_family":src["repeatability"]["citation_adjusted_R_family"]},
  {"analysis":"five_domains","R_family":corr["trait_domain_sensitivity"]["S3_R_family"]}
]
with (a.out_dir/"figure2_family_robustness.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["analysis","R_family"]); w.writeheader(); w.writerows(rob_rows)

# Figure 3: portability and training variance.
port_rows=[
  {"axis":"S3","predictor":"unshrunk","gain":blup["S3_raw"]["gain_unshrunk"]},
  {"axis":"S3","predictor":"BLUP","gain":blup["S3_raw"]["gain_blup"]},
  {"axis":"prune_only","predictor":"unshrunk","gain":blup["prune_raw"]["gain_unshrunk"]},
  {"axis":"prune_only","predictor":"BLUP","gain":blup["prune_raw"]["gain_blup"]}
]
with (a.out_dir/"figure3_portability.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["axis","predictor","gain"]); w.writeheader(); w.writerows(port_rows)

var_rows=[
  {"axis":"S3","component":"trait","variance":blup["S3_raw"]["median_training_trait_variance"]},
  {"axis":"S3","component":"residual","variance":blup["S3_raw"]["median_training_residual_variance"]},
  {"axis":"prune_only","component":"trait","variance":blup["prune_raw"]["median_training_trait_variance"]},
  {"axis":"prune_only","component":"residual","variance":blup["prune_raw"]["median_training_residual_variance"]}
]
with (a.out_dir/"figure3_training_variance.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["axis","component","variance"]); w.writeheader(); w.writerows(var_rows)

# Supplementary scale-HOLD accounting.
scale=aware["log_scale"]
with (a.out_dir/"supplement_log_hold.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["axis","n_systems_with_nonpositive_state"]); w.writeheader()
    w.writerow({"axis":"S3","n_systems_with_nonpositive_state":scale["n_S3_nonpositive_systems"]})
    w.writerow({"axis":"prune_only","n_systems_with_nonpositive_state":scale["n_prune_nonpositive_systems"]})

out={
 "version":"v0.2",
 "status":"TRAIT_MEMORY_FIGURE_DATA_PREPARED_POST_ROBUSTNESS",
 "n_systems":len(rows),"n_families":len(families),"n_traits":len(traits),
 "ordering":"alphabetical only for observed family x trait matrix; no outcome-based clustering",
 "files":[
   "memory_matrix.csv","memory_effects.csv",
   "figure1_variance_shares.csv","figure1_heterogeneity_ci.csv",
   "figure2_correlated_trait_null.csv","figure2_family_robustness.csv",
   "figure3_portability.csv","figure3_training_variance.csv",
   "supplement_log_hold.csv"
 ]
}
(a.out_dir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
