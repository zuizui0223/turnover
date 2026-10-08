#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()
df=pd.read_csv(a.effects)
log=df[df.log_domain_pass==True].copy()
thresholds=[20,30,50,75,100,150]

def metric(d,col,ncol,thr,minco=10):
    z=d[d[ncol]>=thr].copy()
    traits=sorted(z.trait_name.unique())
    obs=maxobs=den=0;n_pairs=0
    for i,A in enumerate(traits):
        da=z[z.trait_name==A][["family",col]].rename(columns={col:"a"})
        for B in traits[i+1:]:
            db=z[z.trait_name==B][["family",col]].rename(columns={col:"b"})
            m=da.merge(db,on="family")
            if len(m)<minco:continue
            dd=m.a-m.b;pos=int((dd>0).sum());neg=int((dd<0).sum());n=pos+neg
            if n<2:continue
            obs+=pos*neg;maxobs+=(n//2)*(n-n//2);den+=n*(n-1)/2;n_pairs+=1
    return {
      "threshold_species_per_system":thr,
      "n_systems":int(len(z)),"n_families":int(z.family.nunique()),"n_traits":int(z.trait_name.nunique()),
      "n_well_represented_trait_pairs":n_pairs,
      "weighted_reversal_probability":None if den==0 else obs/den,
      "fraction_of_pair_specific_maximum":None if maxobs==0 else obs/maxobs
    }

out={"version":"v0.1","status":"AUSTRAITS_RANK_REORDERING_SUPPORT_SENSITIVITY_ESTIMATED",
     "post_outcome_exploratory":True,
     "population":"254-system matched positive-numeric log core",
     "well_represented_pair_minimum_families":10,
     "threshold_grid":thresholds,
     "S3":[metric(log,"S3_log_rho","n_species_S3",t) for t in thresholds],
     "prune_only":[metric(log,"prune_log_rho","n_species_prune",t) for t in thresholds],
     "interpretation":"Re-ordering remains high as low-species systems are progressively removed. This is a descriptive support sensitivity, not a measurement-error model."}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
