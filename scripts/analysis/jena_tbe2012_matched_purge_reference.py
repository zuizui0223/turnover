#!/usr/bin/env python3
"""Matched training-subset reference after the Jena species-disjoint result.

Same test plots, model, endpoints, cell counts, and weights; random training
subsets only. Empirical reference ranges are not confidence intervals.
"""
from __future__ import annotations
import collections
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/jena_tbe2012_matched_purge_reference_20261127_v0_1.json"
N=2000
SEED=20261127
TIE=1e-12
NAMES=("B","E","NDE","CE","SE","TDCE","DE")

def check(ok,msg):
    if not ok:raise ValueError(msg)

def load():
    s=importlib.util.spec_from_file_location("parent",ROOT/"scripts/analysis/jena_tbe2012_pool_fox_transfer_20261127.py")
    check(s is not None and s.loader is not None,"parent module missing")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def cell(r):
    return (r["pool"],r["rich"],r["high"],r["prefix"])

def replay(m,rows):
    configs=[
      (False,"jena_tbe2012_84plot_pool_fox_transfer_20261127_v0_1.json"),
      (True,"jena_tbe2012_species_disjoint_sensitivity_20261127_v0_1.json")]
    results=[]
    for strict,name in configs:
        j=json.loads((ROOT/"results"/name).read_text())["analysis"]
        actual=m.evaluate(rows,purge_shared_species=strict)
        for endpoint in NAMES:
            check(abs(j["combined_equal_pool_richness_gain"][endpoint]-actual["combined_equal_pool_richness_gain"][endpoint])<=1e-10,
                  "frozen parent combined score replay failed")
        for a,b in zip(j["folds"],actual["folds"]):
            check(a["heldout_pool"]==b["heldout_pool"] and a["n_train"]==b["n_train"],"frozen source fold replay failed")
            for mod in ("weighted_SSE_M0","weighted_SSE_M1"):
                for k in NAMES:
                    check(np.isclose(a[mod][k],b[mod][k],rtol=1e-10,atol=1e-8),"parent SSE replay failed")
        results.append(actual)
    return results

def prepare(rows,pool,strict_fold):
    te=[r for r in rows if r["pool"]==pool]
    ts={r["species"] for r in te}
    taxa={s for r in te for s in r["species"]}
    ordinary=sorted((r for r in rows if r["pool"]!=pool and r["species"] not in ts),
                    key=lambda r:(cell(r),r["species"]))
    strict=[r for r in ordinary if not set(r["species"])&taxa]
    check(len(te)==28 and len(strict)==strict_fold["n_train"],"strict original fold size changed")
    groups=collections.defaultdict(list)
    for i,r in enumerate(ordinary):groups[cell(r)].append(i)
    target=collections.Counter(cell(r) for r in strict)
    check(set(target)<=set(groups),"strict subset not included in ordinary support")
    specs=[];possible=1
    for k,inds in sorted(groups.items()):
        n=target[k]
        check(0<=n<=len(inds),"invalid matched cell")
        if n:
            specs.append((np.asarray(inds,int),n))
        possible*=math.comb(len(inds),n)
    rich=sorted({r["rich"] for r in rows});pref=sorted({r["prefix"] for r in rows})
    def matrix(rr):
        return np.asarray([[1.,*[float(r["rich"]==v) for v in rich[1:]],
                          *[float(r["prefix"]==v) for v in pref[1:]],float(r["high"])] for r in rr])
    X=matrix(ordinary);T=matrix(te)
    Y=np.array([[r[k] for k in NAMES] for r in ordinary])
    V=np.array([[r[k] for k in NAMES] for r in te])
    overlaps=np.asarray([bool(set(r["species"])&taxa) for r in ordinary])
    counts=collections.Counter((r["pool"],r["rich"]) for r in strict)
    weights=np.asarray([1/counts[(r["pool"],r["rich"])] if counts[(r["pool"],r["rich"])] else 0. for r in ordinary])
    tc=collections.Counter((r["pool"],r["rich"]) for r in te)
    wt=np.asarray([1/tc[(r["pool"],r["rich"])] for r in te])
    # Strict row indices identified without outcome information.
    strict_idx=np.flatnonzero(~overlaps)
    check(len(strict_idx)==len(strict),"strict membership mismatch")
    # Every reference draw has exactly the same design-row multiset and weights.
    def fit(idx):
        w=weights[idx];a=X[idx];y=Y[idx]
        check(len(idx)==len(strict) and len(set(map(int,idx)))==len(idx),"reference row count or replacement violation")
        check(collections.Counter(cell(ordinary[i]) for i in idx)==target,"matched design cell mismatch")
        check(np.isfinite(w).all() and np.all(w>0),"invalid weights")
        score=[]
        for cols in (a.shape[1]-1,a.shape[1]):
            d=a[:,:cols]*np.sqrt(w[:,None])
            check(np.linalg.matrix_rank(d)==cols,"fixed matched design not full rank")
            beta=np.linalg.lstsq(d,y*np.sqrt(w[:,None]),rcond=None)[0]
            e=V-T[:,:cols]@beta
            score.append((wt[:,None]*e**2).sum(axis=0))
        s=np.array(score)
        check(np.isfinite(s).all() and np.all(s[0]>1e-12),"nonfinite or nonpositive matched baseline")
        return s
    observed=fit(strict_idx)
    for i,mod in enumerate(("weighted_SSE_M0","weighted_SSE_M1")):
        check(np.allclose(observed[i],[strict_fold[mod][k] for k in NAMES],rtol=1e-10,atol=1e-8),"strict subset SSE not replayed")
    return {"pool":pool,"n_ordinary":len(ordinary),"n_strict":len(strict),"n_test":len(te),
            "possible_exact_matched_subsets":str(possible),"n_nonempty_target_cells":len(specs),
            "specs":specs,"overlaps":overlaps,"fit":fit,"strict_scores":observed}

def stats(x):
    a=np.asarray(x,float)
    return {"median":float(np.median(a)),"central_95_reference_range":np.quantile(a,[.025,.975]).tolist()}

def summarize(samples,strict,ordinary):
    g=1-samples[:,1,:]/samples[:,0,:]
    gs=1-strict[1]/strict[0]
    go=1-ordinary[1]/ordinary[0]
    res={}
    for i,k in enumerate(NAMES):
        q=stats(g[:,i]);lo,hi=q["central_95_reference_range"]
        res[k]={"ordinary_gain":float(go[i]),"strict_gain":float(gs[i]),
                "reference_gain":q,"strict_minus_reference_median_percentage_points":float(100*(gs[i]-q["median"])),
                "strict_gain_percentile_fraction_le":float(np.mean(g[:,i]<=gs[i]+TIE)),
                "strict_below_reference_range":bool(gs[i]<lo-TIE),
                "strict_above_reference_range":bool(gs[i]>hi+TIE),
                "ordinary_SSE_M0":float(ordinary[0,i]),"ordinary_SSE_M1":float(ordinary[1,i]),
                "strict_SSE_M0":float(strict[0,i]),"strict_SSE_M1":float(strict[1,i]),
                "reference_SSE_M0":stats(samples[:,0,i]),"reference_SSE_M1":stats(samples[:,1,i])}
    return res

def run():
    m=load();rows,source=m.source()
    check(len(rows)==84,"original 84-plot source changed")
    ordinary,strict=replay(m,rows)
    rng=np.random.default_rng(SEED)
    folds=[];combined=np.zeros((N,2,len(NAMES)));strict_total=np.zeros((2,len(NAMES)));ordinary_total=np.zeros_like(strict_total)
    overlap_total=np.zeros(N,dtype=int);train_total=0
    for old,st in zip(ordinary["folds"],strict["folds"]):
        p=prepare(rows,st["heldout_pool"],st)
        samples=np.empty((N,2,len(NAMES)));overlap=np.zeros(N,dtype=int)
        for j in range(N):
            ix=np.sort(np.concatenate([rng.choice(inds,size=n,replace=False) for inds,n in p["specs"]]))
            overlap[j]=int(p["overlaps"][ix].sum())
            samples[j]=p["fit"](ix)
        old_s=np.array([[old[k][x] for x in NAMES] for k in ("weighted_SSE_M0","weighted_SSE_M1")])
        combined+=samples;strict_total+=p["strict_scores"];ordinary_total+=old_s
        overlap_total+=overlap;train_total+=p["n_strict"]
        folds.append({"heldout_pool":p["pool"],"n_train_ordinary":p["n_ordinary"],"n_train_strict_and_matched":p["n_strict"],
                     "n_test":p["n_test"],"possible_exact_matched_subsets":p["possible_exact_matched_subsets"],
                     "nonempty_target_design_cells":p["n_nonempty_target_cells"],
                     "draws_with_no_shared_taxa":int(np.sum(overlap==0)),
                     "shared_taxon_plot_fraction_reference":stats(overlap/p["n_strict"]),
                     "endpoints":summarize(samples,p["strict_scores"],old_s)})
    result={"status":"MATCHED_PURGE_REFERENCE_COMPLETE","date":"2026-11-27",
            "source_audit":source,"both_parent_scores_replayed":True,
            "reference_draws":N,"seed":SEED,"n_field_experiments":1,"n_test_plots":84,
            "same_design_rows_and_weights_in_every_reference_draw":True,
            "reference_range_not_confidence_interval":True,"no_causal_species_overlap_effect":True,
            "raw_source_rows_redistributed":False,"population_CI":None,"p_values":None,
            "folds":folds,"combined_possible_exact_subsets":str(math.prod(int(x["possible_exact_matched_subsets"]) for x in folds)),
            "combined_draws_no_shared_taxa_all_folds":int(np.sum(overlap_total==0)),
            "combined_shared_taxon_plot_fraction_reference":stats(overlap_total/train_total),
            "combined_endpoints":summarize(combined,strict_total,ordinary_total)}
    check(sum(f["n_test"] for f in folds)==84,"not all original test rows retained")
    return result

if __name__=="__main__":
    try:j=run()
    except Exception as e:j={"status":"SOURCE_OR_MODEL_HOLD","failure_class":type(e).__name__,"reason":str(e)[:200] if isinstance(e,ValueError) else "source/replay/calculation error"}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
    # Compact genuine original execution output. Full aggregate JSON artifact.
    print(json.dumps(j,ensure_ascii=False))
    if j["status"]!="MATCHED_PURGE_REFERENCE_COMPLETE":raise SystemExit(1)
