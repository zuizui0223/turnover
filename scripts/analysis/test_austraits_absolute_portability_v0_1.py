#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--predictions",type=Path,required=True)
ap.add_argument("--permutations",type=int,default=9999)
ap.add_argument("--seed",type=int,default=20261006)
a=ap.parse_args()
rows=list(csv.DictReader(a.effects.open(newline="",encoding="utf-8")))
families=sorted({r["family"] for r in rows});traits=sorted({r["trait_name"] for r in rows})
if len(families)<12 or len(traits)<4:raise SystemExit("core below frozen minimum")
fm={f:i for i,f in enumerate(families)};tm={t:i for i,t in enumerate(traits)}
fi=np.array([fm[r["family"]] for r in rows]);ti=np.array([tm[r["trait_name"]] for r in rows])
nf=len(families);nt=len(traits);n=len(rows)
fg=[np.flatnonzero(fi==k) for k in range(nf)]
fc=np.bincount(fi,minlength=nf);tc=np.bincount(ti,minlength=nt)
if fc.min()<2 or tc.min()<5:raise SystemExit("final core degree constraint violated")
rng=np.random.default_rng(a.seed)
orders={f:np.argsort(rng.random((a.permutations,len(idx))),axis=1) for f,idx in enumerate(fg)}

def test(y):
    y=np.asarray(y,float)
    total=y.sum();fs=np.bincount(fi,weights=y,minlength=nf);ts=np.bincount(ti,weights=y,minlength=nt)
    base=(total-fs[fi])/(n-fc[fi]);pred=(ts[ti]-y)/(tc[ti]-1)
    s0=float(np.sum((y-base)**2));s1=float(np.sum((y-pred)**2));gain=1-s1/s0
    null=np.empty(a.permutations)
    yp=np.empty((a.permutations,n),float)
    for f,idx in enumerate(fg):yp[:,idx]=y[idx][orders[f]]
    tsum=np.zeros((a.permutations,nt),float)
    for t in range(nt):tsum[:,t]=yp[:,ti==t].sum(axis=1)
    pp=(tsum[:,ti]-yp)/(tc[ti]-1)
    null=1-np.sum((yp-pp)**2,axis=1)/s0
    p=(1+np.sum(null>=gain))/(a.permutations+1)
    return dict(gain=float(gain),p_one_sided=float(p),null_median=float(np.median(null)),
                null_q025=float(np.quantile(null,.025)),null_q975=float(np.quantile(null,.975)),
                axis_pass=bool(gain>0 and p<=.05)),pred,base

axes={"S3":"S3_rho","prune_only":"prune_only_rho"}
out={"version":"v0.1","austraits_memory_effects_opened":True,"n_systems":n,"n_families":nf,"n_traits":nt,
     "permutations":a.permutations,"seed":a.seed}
predrows=[]
for name,col in axes.items():
    y=np.array([float(r[col]) for r in rows]);res,pred,base=test(y);out[name]=res
    for i,r in enumerate(rows):
        predrows.append({"family":r["family"],"trait_name":r["trait_name"],"axis":name,
                         "observed_rho":y[i],"trait_prediction":pred[i],"global_baseline_prediction":base[i]})
out["robust_portability_pass"]=bool(out["S3"]["axis_pass"] and out["prune_only"]["axis_pass"])
out["status"]="AUSTRAITS_ABSOLUTE_PORTABILITY_PASS" if out["robust_portability_pass"] else "HOLD_AUSTRAITS_ABSOLUTE_PORTABILITY"
a.out.parent.mkdir(parents=True,exist_ok=True);a.predictions.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
with a.predictions.open("w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=list(predrows[0]));w.writeheader();w.writerows(predrows)
print(json.dumps(out,indent=2,sort_keys=True))
