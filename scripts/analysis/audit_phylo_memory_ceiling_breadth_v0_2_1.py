#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np

ap=argparse.ArgumentParser()
ap.add_argument("--systems",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--trait-table",type=Path,required=True)
a=ap.parse_args()

df=pd.read_csv(a.systems)
cat=df[df.semantic_class=="nominal_categorical"].copy()
cont=df[df.semantic_class=="continuous_scalar"].copy()

def summarize(g):
    return pd.Series({
      "n":len(g),
      "no_bracket_n":int(g.s3_no_bracket.sum()),
      "no_bracket_rate":float(g.s3_no_bracket.mean()),
      "s3_pass_n":int(g.s3_pass.sum()),
      "s3_pass_rate":float(g.s3_pass.mean()),
      "median_n_species":float(g.n_input_species.median()),
      "median_max_grid_median":float(g.s3_max_grid_median.median())
    })

trait=cat.groupby("trait_name",sort=True).apply(summarize,include_groups=False).reset_index()
trait.to_csv(a.trait_table,index=False)

family_rates=cat.groupby("family").agg(n=("system_id","size"),no_bracket_rate=("s3_no_bracket","mean")).reset_index()
eligible_family=family_rates[family_rates.n>=2]

out={
  "version":"v0.2.1",
  "status":"PHYLO_MEMORY_CALIBRATION_CEILING_BREADTH_AUDITED",
  "outcome_type":"known_truth_recovery_only",
  "real_trait_values_used":False,
  "real_memory_effects_used":False,
  "categorical":{
    "n_traits":int(cat.trait_name.nunique()),
    "trait_no_bracket_rate_min":float(trait.no_bracket_rate.min()),
    "trait_no_bracket_rate_median":float(trait.no_bracket_rate.median()),
    "trait_no_bracket_rate_max":float(trait.no_bracket_rate.max()),
    "n_traits_rate_ge_0_80":int((trait.no_bracket_rate>=0.80).sum()),
    "n_traits_rate_1":int((trait.no_bracket_rate==1).sum()),
    "trait_table":[
      {
        "trait_name":r.trait_name,"n":int(r.n),"no_bracket_rate":float(r.no_bracket_rate),
        "s3_pass_rate":float(r.s3_pass_rate),"median_n_species":float(r.median_n_species),
        "median_max_grid_median":float(r.median_max_grid_median)
      } for r in trait.itertuples()
    ],
    "families_with_ge2_categorical_systems":int(len(eligible_family)),
    "family_no_bracket_rate_median_ge2":float(eligible_family.no_bracket_rate.median()) if len(eligible_family) else None,
    "family_no_bracket_rate_q25_q75_ge2":[
      float(eligible_family.no_bracket_rate.quantile(.25)),float(eligible_family.no_bracket_rate.quantile(.75))
    ] if len(eligible_family) else None
  },
  "interpretation_guard":"Breadth across traits/families supports a representation-wide measurement bottleneck only; it is not a biological categorical-trait effect."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
