#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--modules",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()
df=pd.read_csv(a.effects)
m=json.loads(a.modules.read_text())
mod={t:k for k,ts in m["modules"].items() for t in ts}
traits=set(df.trait_name.unique())
if traits-set(mod):raise SystemExit(f"unmapped traits: {sorted(traits-set(mod))}")

def metric(d,col,minco=10):
    within={"obs":0,"max":0,"den":0,"pairs":0};between={"obs":0,"max":0,"den":0,"pairs":0}
    tr=sorted(d.trait_name.unique())
    details=[]
    for i,A in enumerate(tr):
        da=d[d.trait_name==A][["family",col]].rename(columns={col:"a"})
        for B in tr[i+1:]:
            db=d[d.trait_name==B][["family",col]].rename(columns={col:"b"})
            z=da.merge(db,on="family")
            if len(z)<minco:continue
            dd=z.a-z.b;pos=int((dd>0).sum());neg=int((dd<0).sum());n=pos+neg
            if n<2:continue
            grp=within if mod[A]==mod[B] else between
            grp["obs"]+=pos*neg;grp["max"]+=(n//2)*(n-n//2);grp["den"]+=n*(n-1)/2;grp["pairs"]+=1
            details.append({"trait_a":A,"trait_b":B,"module_a":mod[A],"module_b":mod[B],
                            "same_module":mod[A]==mod[B],"n_families":n,
                            "reversal_probability":2*pos*neg/(n*(n-1))})
    def fin(x):
        return {"n_trait_pairs":x["pairs"],
                "weighted_reversal_probability":None if x["den"]==0 else x["obs"]/x["den"],
                "fraction_of_pair_specific_maximum":None if x["max"]==0 else x["obs"]/x["max"]}
    return {"within_module":fin(within),"between_module":fin(between),"pairs":details}

log=df[df.log_domain_pass==True].copy()
out={"version":"v0.1","status":"AUSTRAITS_FUNCTIONAL_MODULE_REORDERING_DESCRIBED",
     "post_outcome_descriptive":True,"well_represented_pair_minimum_families":10,
     "matched_log":{"S3":metric(log,"S3_log_rho"),"prune":metric(log,"prune_log_rho")},
     "source_native":{"S3":metric(df,"S3_rho"),"prune":metric(df,"prune_only_rho")}}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in out.items() if k not in {"matched_log","source_native"}},indent=2))
