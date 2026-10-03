#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--predictions",type=Path,required=True)
a=ap.parse_args()
a.out.parent.mkdir(parents=True,exist_ok=True)
a.predictions.parent.mkdir(parents=True,exist_ok=True)

d=json.loads(Path("data/family_context_portability_real_execution_v0_2.json").read_text())
m=json.loads(Path("results/family_context_portability_model_info_v0_1/result.json").read_text())
if m["status"]!="FAMILY_CONTEXT_PORTABILITY_MODEL_INFO_PASS" or not m["gate_pass"]:
    raise SystemExit("family-context portability model-info prerequisite did not pass")

rows=list(csv.DictReader(a.effects.open(newline="")))
if len(rows)!=201: raise SystemExit("expected 201 effects")
families=sorted({r["family"] for r in rows}); traits=sorted({r["trait_name"] for r in rows})
if len(families)!=45 or len(traits)!=12: raise SystemExit("graph shape changed")
fmap={f:i for i,f in enumerate(families)}; tmap={t:i for i,t in enumerate(traits)}
fi=np.array([fmap[r["family"]] for r in rows],dtype=int)
ti=np.array([tmap[r["trait_name"]] for r in rows],dtype=int)
nf=len(families);nt=len(traits);n=len(rows)
tgroups=[np.flatnonzero(ti==k) for k in range(nt)]
fcounts=np.bincount(fi,minlength=nf); tcounts=np.bincount(ti,minlength=nt)
if fcounts.min()<2 or tcounts.min()<5: raise SystemExit("frozen degree constraints changed")

def observed_details(y):
    y=np.asarray(y,dtype=float)
    total=y.sum()
    fs=np.bincount(fi,weights=y,minlength=nf)
    ts=np.bincount(ti,weights=y,minlength=nt)
    base=(total-ts[ti])/(n-tcounts[ti])
    fam=(fs[fi]-y)/(fcounts[fi]-1)
    sse_base=float(np.sum((y-base)**2))
    sse_fam=float(np.sum((y-fam)**2))
    if not np.isfinite(sse_base) or sse_base<=0: raise ValueError("invalid baseline SSE")
    gain=1.0-sse_fam/sse_base
    return gain,fam,base,sse_fam,sse_base

P=int(d["portability_test"]["permutations"])
seed=int(d["portability_test"]["master_seed"])
rng=np.random.default_rng(seed)
orders={}
for t,idx in enumerate(tgroups):
    keys=rng.random((P,len(idx)))
    orders[t]=np.argsort(keys,axis=1)

def blocked_test(y):
    y=np.asarray(y,dtype=float)
    obs,fam_pred,base_pred,sse_fam,sse_base=observed_details(y)
    yp=np.tile(y,(P,1))
    for t,idx in enumerate(tgroups):
        yp[:,idx]=y[idx][orders[t]]
    fs=np.zeros((P,nf),dtype=float)
    for f in range(nf):
        fs[:,f]=yp[:,fi==f].sum(axis=1)
    fp=(fs[:,fi]-yp)/(fcounts[fi]-1)
    total=y.sum()
    ts=np.bincount(ti,weights=y,minlength=nt)
    base=(total-ts[ti])/(n-tcounts[ti])
    null_sse=np.sum((yp-fp)**2,axis=1)
    null_gain=1.0-null_sse/sse_base
    p=(1.0+float(np.sum(null_gain>=obs)))/(P+1.0)
    return {
      "gain":float(obs),"p_value":float(p),
      "sse_family":sse_fam,"sse_global":sse_base,
      "null_median_gain":float(np.median(null_gain)),
      "null_q025":float(np.quantile(null_gain,.025)),
      "null_q975":float(np.quantile(null_gain,.975)),
      "axis_pass":bool(obs>0 and p<=0.05)
    },fam_pred,base_pred

s3=np.array([float(r["S3_rho"]) for r in rows],dtype=float)
pr=np.array([float(r["prune_only_rho"]) for r in rows],dtype=float)
s3res,s3pred,s3base=blocked_test(s3)
prres,prpred,prbase=blocked_test(pr)
robust=bool(s3res["axis_pass"] and prres["axis_pass"])

pred=[]
for i,r in enumerate(rows):
    pred.append({
      "family":r["family"],"trait_name":r["trait_name"],"axis":"S3",
      "observed_rho":s3[i],"family_prediction":s3pred[i],"global_baseline_prediction":s3base[i],
      "family_residual":s3[i]-s3pred[i],"baseline_residual":s3[i]-s3base[i]
    })
    pred.append({
      "family":r["family"],"trait_name":r["trait_name"],"axis":"prune_only",
      "observed_rho":pr[i],"family_prediction":prpred[i],"global_baseline_prediction":prbase[i],
      "family_residual":pr[i]-prpred[i],"baseline_residual":pr[i]-prbase[i]
    })
with a.predictions.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(pred[0]));w.writeheader();w.writerows(pred)

out={
  "version":"v0.2",
  "status":"FAMILY_CONTEXT_PORTABILITY_PASS" if robust else "HOLD_FAMILY_CONTEXT_PORTABILITY",
  "post_outcome_complementary_analysis":True,
  "n_systems":n,"n_families":nf,"n_traits":nt,
  "S3":s3res,"prune_only":prres,
  "robust_family_context_portability_pass":robust,
  "permutations":P,"master_seed":seed,
  "same_blocked_permutations_both_axes":True,
  "interpretation":(
    "Family context learned from other traits robustly improves prediction for a completely held-out trait on both phylogenetic treatments."
    if robust else
    "Family context does not meet the frozen robust cross-trait portability criterion on both phylogenetic treatments."
  ),
  "no_family_trait_dominance_test":True
}
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
