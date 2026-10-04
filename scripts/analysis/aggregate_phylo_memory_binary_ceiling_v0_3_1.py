#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
ap.add_argument("--trait-out",type=Path,required=True)
a=ap.parse_args()

rows=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    if x.get("status")!="PHYLO_MEMORY_EDGE_SPLIT_CEILING_ESTIMATED":
        continue
    rows.append(x)
df=pd.DataFrame(rows)
if len(df)!=276:
    raise SystemExit(f"expected 276 nominal-categorical novel systems, got {len(df)}")
if not (df["real_trait_values_used"].eq(False).all() and df["real_memory_effects_used"].eq(False).all()):
    raise SystemExit("outcome firewall violated")

benchmark=0.15
nb=df[df.original_s3_no_bracket.astype(bool)].copy()
if len(nb)!=220:
    raise SystemExit(f"expected 220 categorical no-bracket systems, got {len(nb)}")
nb["single_transition_structural_limit"]=nb.max_edge_split_rho < benchmark
nb["single_transition_available_but_ou_unreached"]=~nb.single_transition_structural_limit

def q(x,p):
    return float(np.quantile(np.asarray(x,dtype=float),p))

trait=(df.groupby("trait_name",sort=True)
         .agg(n=("system_id","size"),
              no_bracket_rate=("original_s3_no_bracket","mean"),
              median_edge_ceiling=("max_edge_split_rho","median"),
              median_ou_max=("original_ou_max_grid_median","median"),
              edge_reaches_benchmark_rate=("edge_split_reaches_benchmark","mean"))
         .reset_index())
a.trait_out.parent.mkdir(parents=True,exist_ok=True)
trait.to_csv(a.trait_out,index=False)

a.table_out.parent.mkdir(parents=True,exist_ok=True)
df.to_csv(a.table_out,index=False)

out={
  "version":"v0.3.1",
  "status":"PHYLO_MEMORY_EDGE_SPLIT_CEILING_AGGREGATED",
  "outcome_type":"known_truth_geometry_only",
  "real_trait_values_used":False,
  "real_memory_effects_used":False,
  "n_systems":int(len(df)),
  "n_traits":int(df.trait_name.nunique()),
  "n_families":int(df.family.nunique()),
  "benchmark":benchmark,
  "original_no_bracket":{
    "n":int(len(nb)),
    "rate":float(len(nb)/len(df)),
    "n_edge_ceiling_below_benchmark":int(nb.single_transition_structural_limit.sum()),
    "fraction_edge_ceiling_below_benchmark":float(nb.single_transition_structural_limit.mean()),
    "n_edge_ceiling_ge_benchmark_but_ou_unreached":int(nb.single_transition_available_but_ou_unreached.sum()),
    "fraction_edge_ceiling_ge_benchmark_but_ou_unreached":float(nb.single_transition_available_but_ou_unreached.mean())
  },
  "edge_split_ceiling":{
    "median_all":float(df.max_edge_split_rho.median()),
    "q25_q75_all":[q(df.max_edge_split_rho,.25),q(df.max_edge_split_rho,.75)],
    "median_no_bracket":float(nb.max_edge_split_rho.median()),
    "q25_q75_no_bracket":[q(nb.max_edge_split_rho,.25),q(nb.max_edge_split_rho,.75)],
    "fraction_all_reaching_benchmark":float(df.edge_split_reaches_benchmark.mean())
  },
  "generator_accessibility_gap":{
    "median_edge_minus_ou_no_bracket":float(nb.edge_minus_ou_gap.median()),
    "q25_q75_edge_minus_ou_no_bracket":[q(nb.edge_minus_ou_gap,.25),q(nb.edge_minus_ou_gap,.75)],
    "median_ou_max_grid_no_bracket":float(nb.original_ou_max_grid_median.median())
  },
  "superseded_unconstrained_diagnostic":{
    "minimum_upper_bound":float(df.unconstrained_pair_label_upper_bound.min()),
    "median_upper_bound":float(df.unconstrained_pair_label_upper_bound.median()),
    "fraction_below_benchmark":float((df.unconstrained_pair_label_upper_bound<benchmark).mean()),
    "interpretation":"If this fraction is zero or near zero, the old arbitrary pair-label construction is confirmed to be non-discriminating for the 0.15 benchmark."
  },
  "interpretation_guard":"An edge-split ceiling below 0.15 rules out the benchmark for every one-transition clade-vs-rest state on that tree, but not for every possible multi-transition binary pattern."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
