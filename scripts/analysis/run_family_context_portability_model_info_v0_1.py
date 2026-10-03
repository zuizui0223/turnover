#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np

ap=argparse.ArgumentParser()
ap.add_argument("--core-table",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()
a.out.parent.mkdir(parents=True,exist_ok=True)
a.table_out.parent.mkdir(parents=True,exist_ok=True)

d=json.loads(Path("data/family_context_portability_design_v0_1.json").read_text())
rows=list(csv.DictReader(a.core_table.open(newline="")))
if len(rows)!=201: raise SystemExit(f"expected 201 systems, got {len(rows)}")
families=sorted({r["family"] for r in rows})
traits=sorted({r["trait_name"] for r in rows})
if len(families)!=45 or len(traits)!=12: raise SystemExit("unexpected graph shape")
fmap={f:i for i,f in enumerate(families)}
tmap={t:i for i,t in enumerate(traits)}
fi=np.array([fmap[r["family"]] for r in rows],dtype=int)
ti=np.array([tmap[r["trait_name"]] for r in rows],dtype=int)
n=len(rows); nf=len(families); nt=len(traits)
fgroups=[np.flatnonzero(fi==k) for k in range(nf)]
tgroups=[np.flatnonzero(ti==k) for k in range(nt)]
fcounts=np.bincount(fi,minlength=nf)
tcounts=np.bincount(ti,minlength=nt)
if fcounts.min()<2 or tcounts.min()<5: raise SystemExit("degree constraints changed")

def gain(y:np.ndarray)->float:
    y=np.asarray(y,dtype=float)
    if y.shape!=(n,) or not np.all(np.isfinite(y)): return np.nan
    total=y.sum()
    fs=np.bincount(fi,weights=y,minlength=nf)
    ts=np.bincount(ti,weights=y,minlength=nt)
    base=(total-ts[ti])/(n-tcounts[ti])
    denom=fcounts[fi]-1
    if np.any(denom<1): return np.nan
    fp=(fs[fi]-y)/denom
    sse_base=np.sum((y-base)**2)
    if not np.isfinite(sse_base) or sse_base<=0: return np.nan
    sse_family=np.sum((y-fp)**2)
    return float(1.0-sse_family/sse_base)

def permutation_test(y:np.ndarray,rng:np.random.Generator,P:int)->tuple[float,float]:
    obs=gain(y)
    if not np.isfinite(obs): return np.nan,np.nan
    yp=np.tile(y,(P,1))
    for idx in tgroups:
        keys=rng.random((P,len(idx)))
        order=np.argsort(keys,axis=1)
        yp[:,idx]=y[idx][order]
    fs=np.zeros((P,nf),dtype=float)
    for f in range(nf):
        fs[:,f]=yp[:,fi==f].sum(axis=1)
    fp=(fs[:,fi]-yp)/(fcounts[fi]-1)
    total=y.sum()
    ts=np.bincount(ti,weights=y,minlength=nt)
    base=(total-ts[ti])/(n-tcounts[ti])
    sse_base=np.sum((y-base)**2)
    null_sse=np.sum((yp-fp)**2,axis=1)
    null_gain=1.0-null_sse/sse_base
    p=(1.0+float(np.sum(null_gain>=obs)))/(P+1.0)
    return obs,p

def run_benchmark(name:str,pars:dict,seed:int):
    gate=d["known_truth_gate"]; B=int(gate["datasets_per_benchmark"]); P=int(gate["permutations_per_dataset"])
    rng=np.random.default_rng(seed)
    mu=float(pars["intercept"]); vf=float(pars["family_variance"]); vt=float(pars["trait_variance"]); ve=float(pars["residual_variance"])
    rec=[]
    for b in range(B):
        uf=rng.normal(0,math.sqrt(vf),size=nf) if vf>0 else np.zeros(nf)
        ut=rng.normal(0,math.sqrt(vt),size=nt) if vt>0 else np.zeros(nt)
        eps=rng.normal(0,math.sqrt(ve),size=n)
        y=mu+uf[fi]+ut[ti]+eps
        g,p=permutation_test(y,rng,P)
        valid=bool(np.isfinite(g) and np.isfinite(p))
        pos=bool(valid and g>0 and p<=0.05)
        rec.append({"benchmark":name,"replicate":b+1,"valid":valid,"gain":None if not valid else g,"p_value":None if not valid else p,"positive_test":pos})
    valid=[r for r in rec if r["valid"]]
    gains=np.array([r["gain"] for r in valid],dtype=float)
    summ={
      "n_datasets":B,"valid_datasets":len(valid),"valid_fraction":len(valid)/B,
      "positive_test_fraction":float(np.mean([r["positive_test"] for r in rec])),
      "median_gain":None if len(gains)==0 else float(np.median(gains)),
      "gain_q025":None if len(gains)==0 else float(np.quantile(gains,.025)),
      "gain_q975":None if len(gains)==0 else float(np.quantile(gains,.975))
    }
    return summ,rec

g=d["known_truth_gate"]
sig,srec=run_benchmark(g["benchmark_signal"]["name"],g["benchmark_signal"],int(g["master_seed"]))
nul,nrec=run_benchmark(g["benchmark_null"]["name"],g["benchmark_null"],int(g["master_seed"])+1)
adm=g["admission"]
sigpass=(sig["valid_fraction"]>=adm["valid_fraction_min"] and sig["positive_test_fraction"]>=adm["signal_power_min"] and sig["median_gain"] is not None and sig["median_gain"]>adm["signal_median_gain_min"])
nulpass=(nul["valid_fraction"]>=adm["valid_fraction_min"] and nul["positive_test_fraction"]<=adm["null_false_positive_max"])
overall=bool(sigpass and nulpass)

with a.table_out.open("w",newline="") as fh:
    fields=["benchmark","replicate","valid","gain","p_value","positive_test"]
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(srec+nrec)

out={
  "version":"v0.1",
  "status":"FAMILY_CONTEXT_PORTABILITY_MODEL_INFO_PASS" if overall else "HOLD_FAMILY_CONTEXT_PORTABILITY_MODEL_INFO",
  "post_outcome_complementary_design":True,
  "real_family_portability_test_opened":False,
  "graph":{"systems":n,"families":nf,"traits":nt,"min_family_degree":int(fcounts.min()),"min_trait_degree":int(tcounts.min())},
  "signal_benchmark":sig,"null_benchmark":nul,"admission":adm,
  "signal_gate_pass":sigpass,"null_gate_pass":nulpass,"gate_pass":overall,
  "next_gate":"Run the frozen leave-one-trait-out family-context portability test on the already-opened 201 paired effects." if overall else "Stop the complementary family-context portability analysis."
}
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
