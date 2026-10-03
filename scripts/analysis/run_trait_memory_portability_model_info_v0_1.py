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

design=json.loads(Path("data/trait_memory_portability_design_v0_1.json").read_text())
rows=list(csv.DictReader(a.core_table.open(newline="")))
if len(rows)!=201:
    raise SystemExit(f"expected 201 core systems, got {len(rows)}")
families=sorted({r["family"] for r in rows})
traits=sorted({r["trait_name"] for r in rows})
if len(families)!=45 or len(traits)!=12:
    raise SystemExit(f"unexpected graph shape {len(families)} families {len(traits)} traits")
if any(r.get("semantic_class") not in (None,"","continuous_scalar") for r in rows):
    raise SystemExit("final core is not all continuous scalar")

fmap={f:i for i,f in enumerate(families)}
tmap={t:i for i,t in enumerate(traits)}
fi=np.array([fmap[r["family"]] for r in rows],dtype=int)
ti=np.array([tmap[r["trait_name"]] for r in rows],dtype=int)
n=len(rows); nf=len(families); nt=len(traits)
family_groups=[np.flatnonzero(fi==k) for k in range(nf)]
trait_counts=np.bincount(ti,minlength=nt)
family_counts=np.bincount(fi,minlength=nf)
if family_counts.min()<2:
    raise SystemExit("family degree below 2")
if trait_counts.min()<5:
    raise SystemExit("trait degree below 5")

# Incidence is simple: one edge per family x trait.
for f in range(nf):
    tt=ti[family_groups[f]]
    if len(np.unique(tt))!=len(tt):
        raise SystemExit("duplicate family-trait edge")

def portability_gain(y:np.ndarray)->float:
    y=np.asarray(y,dtype=float)
    if y.shape!=(n,) or not np.all(np.isfinite(y)):
        return np.nan
    total=y.sum()
    fam_sums=np.bincount(fi,weights=y,minlength=nf)
    trait_sums=np.bincount(ti,weights=y,minlength=nt)
    base_pred=(total-fam_sums[fi])/(n-family_counts[fi])
    denom=trait_counts[ti]-1
    if np.any(denom<1):
        return np.nan
    trait_pred=(trait_sums[ti]-y)/denom
    sse_base=np.sum((y-base_pred)**2)
    if not np.isfinite(sse_base) or sse_base<=0:
        return np.nan
    sse_trait=np.sum((y-trait_pred)**2)
    return float(1.0-sse_trait/sse_base)

def permutation_test(y:np.ndarray,rng:np.random.Generator,P:int)->tuple[float,float]:
    obs=portability_gain(y)
    if not np.isfinite(obs):
        return np.nan,np.nan
    # Family-blocked permutation preserves family sums and the incidence graph.
    yp=np.tile(y,(P,1))
    for idx in family_groups:
        # independent random ordering in every permutation row
        random_keys=rng.random((P,len(idx)))
        order=np.argsort(random_keys,axis=1)
        yp[:,idx]=y[idx][order]
    trait_sums=np.zeros((P,nt),dtype=float)
    for t in range(nt):
        trait_sums[:,t]=yp[:,ti==t].sum(axis=1)
    trait_pred=(trait_sums[:,ti]-yp)/(trait_counts[ti]-1)
    total=y.sum()
    fam_sums=np.bincount(fi,weights=y,minlength=nf)
    base_pred=(total-fam_sums[fi])/(n-family_counts[fi])
    sse_base=np.sum((y-base_pred)**2)
    sse_trait=np.sum((yp-trait_pred)**2,axis=1)
    null_gain=1.0-sse_trait/sse_base
    p=(1.0+float(np.sum(null_gain>=obs)))/(P+1.0)
    return obs,p

def run_benchmark(name:str,pars:dict,seed:int)->tuple[dict,list[dict]]:
    B=int(design["known_truth_gate"]["datasets_per_benchmark"])
    P=int(design["known_truth_gate"]["permutations_per_dataset"])
    rng=np.random.default_rng(seed)
    mu=float(pars["intercept"])
    vt=float(pars["trait_variance"])
    vf=float(pars["family_variance"])
    ve=float(pars["residual_variance"])
    records=[]
    for b in range(B):
        ut=rng.normal(0,math.sqrt(vt),size=nt) if vt>0 else np.zeros(nt)
        uf=rng.normal(0,math.sqrt(vf),size=nf) if vf>0 else np.zeros(nf)
        eps=rng.normal(0,math.sqrt(ve),size=n)
        y=mu+ut[ti]+uf[fi]+eps
        gain,p=permutation_test(y,rng,P)
        valid=bool(np.isfinite(gain) and np.isfinite(p))
        positive=bool(valid and gain>0 and p<=0.05)
        records.append({
          "benchmark":name,"replicate":b+1,"valid":valid,
          "gain":None if not valid else gain,
          "p_value":None if not valid else p,
          "positive_test":positive
        })
    valid=[r for r in records if r["valid"]]
    gains=np.array([r["gain"] for r in valid],dtype=float)
    positive=np.array([r["positive_test"] for r in records],dtype=bool)
    summary={
      "n_datasets":B,
      "valid_datasets":len(valid),
      "valid_fraction":len(valid)/B,
      "positive_test_fraction":float(positive.mean()),
      "median_gain":None if len(gains)==0 else float(np.median(gains)),
      "gain_q025":None if len(gains)==0 else float(np.quantile(gains,0.025)),
      "gain_q975":None if len(gains)==0 else float(np.quantile(gains,0.975))
    }
    return summary,records

gate=design["known_truth_gate"]
signal_summary,signal_records=run_benchmark(
    gate["benchmark_signal"]["name"],gate["benchmark_signal"],
    int(gate["master_seed"]))
null_summary,null_records=run_benchmark(
    gate["benchmark_null"]["name"],gate["benchmark_null"],
    int(gate["master_seed"])+1)

adm=gate["admission"]
signal_pass=(
    signal_summary["valid_fraction"]>=float(adm["valid_fraction_min"]) and
    signal_summary["positive_test_fraction"]>=float(adm["signal_power_min"]) and
    signal_summary["median_gain"] is not None and
    signal_summary["median_gain"]>float(adm["signal_median_gain_min"])
)
null_pass=(
    null_summary["valid_fraction"]>=float(adm["valid_fraction_min"]) and
    null_summary["positive_test_fraction"]<=float(adm["null_false_positive_max"])
)
overall=bool(signal_pass and null_pass)

all_records=signal_records+null_records
fields=["benchmark","replicate","valid","gain","p_value","positive_test"]
with a.table_out.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(all_records)

out={
  "version":"v0.1",
  "status":"TRAIT_MEMORY_PORTABILITY_MODEL_INFO_PASS" if overall else "HOLD_TRAIT_MEMORY_PORTABILITY_MODEL_INFO",
  "outcome_blind":True,
  "real_memory_effects_opened":False,
  "graph":{
    "systems":n,"families":nf,"traits":nt,
    "minimum_family_degree":int(family_counts.min()),
    "maximum_family_degree":int(family_counts.max()),
    "minimum_trait_degree":int(trait_counts.min()),
    "maximum_trait_degree":int(trait_counts.max())
  },
  "signal_benchmark":signal_summary,
  "null_benchmark":null_summary,
  "admission":adm,
  "signal_gate_pass":signal_pass,
  "null_gate_pass":null_pass,
  "gate_pass":overall,
  "next_gate":"Open real S3/prune-only memory rho on the frozen 201-system core and execute the predeclared family-blocked portability test." if overall else "Stop before real memory rho; trait portability is not sufficiently calibrated on this graph."
}
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
