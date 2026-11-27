#!/usr/bin/env python3
"""Fixed original Jena TBE cross-pool component transfer, aggregate only."""
from __future__ import annotations
import collections, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/jena_tbe2012_84plot_pool_fox_transfer_20261127_v0_1.json"
NAMES=("B","E","NDE","CE","SE","TDCE","DE")
def require(ok,msg):
    if not ok:raise ValueError(msg)
def load():
    spec=importlib.util.spec_from_file_location("parent_tbe",ROOT/"scripts/analysis/jena_tbe2012_original_monoculture_CE_SE_partition_v0_1.py")
    require(spec is not None and spec.loader is not None,"parent module unavailable")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def partition(m,y):
    m=np.asarray(m,float);y=np.asarray(y,float)
    require(np.all(np.isfinite(m)) and np.all(m>0) and np.all(np.isfinite(y)) and np.all(y>=0),"invalid original mono or mixture yield")
    B=float(y.sum());E=float(m.mean());RYT=float((y/m).sum())
    require(RYT>0,"Fox DE undefined for zero total relative yield; no row deleted")
    CE=(RYT-1)*E;SE=B-RYT*E;DE=B/RYT-E;TDCE=SE-DE
    out={"B":B,"E":E,"NDE":B-E,"CE":CE,"SE":SE,"TDCE":TDCE,"DE":DE}
    err=max(abs(out["NDE"]-CE-SE),abs(SE-DE-TDCE),abs(TDCE-(RYT-1)*DE))
    require(err<1e-8*max(1.,max(abs(v) for v in out.values())),"component partition arithmetic failed")
    return out,err
def source():
    p=load();selected,mono,info=p.assemble_source()
    old,old_error=p.partition(selected,mono);before=p.fit(old)
    recorded=json.loads((ROOT/"results/jena_tbe2012_mono_based_84plot_NDE_CE_SE_v0_1.json").read_text())
    discrepancy=max(abs(before[k]-recorded["primary"][k+"_high_minus_low_g_dry_m2"]) for k in ("CE","SE","NDE"))
    require(discrepancy<1e-8,"frozen parent coefficient replay changed")
    counts=collections.Counter(s for pool,s in mono)
    require(len(counts)==20 and sum(counts.values())==24 and collections.Counter(counts.values())=={1:16,2:4},"original overlapping pool memberships changed")
    data=[];max_err=0.
    for r,old_r in zip(selected,old):
        names=sorted(r["mass"]);m=[mono[(r["pool"],s)][0] for s in names];y=[r["mass"][s] for s in names]
        vals,err=partition(m,y)
        require(max(abs(vals[k]-old_r[k]) for k in ("CE","SE","NDE"))<1e-8,"independent partition disagrees with source parent")
        data.append({"pool":r["pool"],"rich":r["rich"],"prefix":r["prefix"],"high":int(r["fd"]>=3),"species":tuple(names),**vals})
        max_err=max(max_err,err)
    require(len(data)==84,"frozen source cohort changed")
    info.update({"parent_WLS_coefficients_replayed":True,"max_parent_beta_discrepancy":discrepancy,
                 "all_84_Fox_partitions_qualified":True,"maximum_partition_identity_error":max_err,
                 "source_total_unique_species":20,"source_species_shared_between_pools":4,
                 "original_literal_block_hold_preserved":True})
    return data,info
def weight(rows):
    counts=collections.Counter((r["pool"],r["rich"]) for r in rows)
    return np.asarray([1/counts[(r["pool"],r["rich"])] for r in rows],float)
def evaluate(rows):
    pools=sorted({r["pool"] for r in rows});rich=sorted({r["rich"] for r in rows});pref=sorted({r["prefix"] for r in rows})
    require(len(pools)==3 and len(pref)==3 and len(rich)==2,"expected 3 original pools, 3 prefix codes, 2 shared richness categories")
    def matrix(rr):
        return np.asarray([[1.,*[float(r["rich"]==x) for x in rich[1:]],
                            *[float(r["prefix"]==x) for x in pref[1:]],float(r["high"])] for r in rr])
    folds=[]
    for pool in pools:
        te=[r for r in rows if r["pool"]==pool];all_tr=[r for r in rows if r["pool"]!=pool]
        ts={r["species"] for r in te};tr=[r for r in all_tr if r["species"] not in ts]
        require(len(te)>0 and len(tr)>20 and set(r["rich"] for r in tr)==set(rich)==set(r["rich"] for r in te),"unmatched richness or insufficient original training support")
        require(len({r["pool"] for r in tr})==2,"training trait pool disappeared after roster purge")
        require(all(len({r["high"] for r in tr if (r["pool"],r["rich"])==(p,k)})==2 for p in pools if p!=pool for k in rich),"purge removed a complete FD class")
        require(len({r["prefix"] for r in tr})==3,"training prefix support changed")
        a=matrix(tr);b=matrix(te);w=weight(tr);wt=weight(te)
        Y=np.array([[r[k] for k in NAMES] for r in tr]);Yt=np.array([[r[k] for k in NAMES] for r in te])
        errs=[];sse=[];beta=None
        for cols in (a.shape[1]-1,a.shape[1]):
            d=a[:,:cols]*np.sqrt(w[:,None])
            require(np.linalg.matrix_rank(d)==cols,"fixed transfer model rank HOLD")
            beta=np.linalg.lstsq(d,Y*np.sqrt(w[:,None]),rcond=None)[0]
            e=Yt-b[:,:cols]@beta
            errs.append(e)
            sse.append(dict(zip(NAMES,map(float,(wt[:,None]*e**2).sum(axis=0)))))
        require(all(sse[0][k]>1e-12 for k in NAMES),"baseline SSE zero; no change of score allowed")
        gains={k:1-sse[1][k]/sse[0][k] for k in NAMES}
        cross={}
        for total,left,right in (("NDE","CE","SE"),("SE","TDCE","DE"),("B","E","NDE")):
            i=NAMES.index(left);j=NAMES.index(right)
            d={k:sse[1][k]-sse[0][k] for k in (total,left,right)}
            v=float(2*np.sum(wt*(errs[1][:,i]*errs[1][:,j]-errs[0][:,i]*errs[0][:,j])))
            require(abs(d[total]-d[left]-d[right]-v)<1e-6,"source weighted SSE component cross-term identity failed")
            cross[total]={"left":left,"right":right,"delta_SSE_total":d[total],"delta_SSE_left":d[left],"delta_SSE_right":d[right],"delta_twice_cross_product":v}
        coeff=dict(zip(NAMES,map(float,beta[-1])))
        sp_train=set(s for r in tr for s in r["species"]);sp_test=set(s for r in te for s in r["species"])
        folds.append({"heldout_pool":pool,"n_test":len(te),"n_train":len(tr),
                      "n_train_removed_shared_exact_composition":len(all_tr)-len(tr),
                      "n_shared_train_test_taxa":len(sp_train&sp_test),
                      "n_test_taxa":len(sp_test),"test_richness_counts":dict(collections.Counter(r["rich"] for r in te)),
                      "gain":gains,"SE_minus_CE_gain":gains["SE"]-gains["CE"],"high_FD_training_beta_g_m2":coeff,
                      "weighted_SSE_M0":sse[0],"weighted_SSE_M1":sse[1],"error_decomposition":cross})
    require(sum(f["n_test"] for f in folds)==84,"all original plots must be tested once")
    combined={k:1-sum(f["weighted_SSE_M1"][k] for f in folds)/sum(f["weighted_SSE_M0"][k] for f in folds) for k in NAMES}
    criteria={k:{"positive_folds":sum(f["gain"][k]>0 for f in folds),"pooled_positive":combined[k]>0,
                 "all_three_and_pooled_positive":all(f["gain"][k]>0 for f in folds) and combined[k]>0} for k in NAMES}
    return {"n_original_mixtures":84,"n_field_experiments":1,"n_partially_overlapping_pools":3,
           "richness_levels":rich,"folds":folds,"combined_equal_pool_richness_gain":combined,
           "combined_SE_minus_CE_gain":combined["SE"]-combined["CE"],"criterion":criteria,
           "qualitative_SE_TDCE_DE_transport_reproduced":all(criteria[k]["all_three_and_pooled_positive"] for k in ("SE","TDCE","DE")),
           "population_CI":None,"causal_FD_only":False,"physical_block_certified":False}
def selftest():
    z,err=partition([10,20],[6,8]);require(abs(z["NDE"]+1)<1e-10 and abs(z["CE"])<1e-10 and abs(z["SE"]+1)<1e-10,"known truth partition")
    require(abs(z["TDCE"]+z["DE"]-z["SE"])<1e-10,"Fox identity")
    try:partition([10,20],[0,0])
    except ValueError:pass
    else:raise AssertionError("zero RYT guard")
    print("SYNTHETIC_FOX_PARTITION_PASS")
if __name__=="__main__":
    result={"date":"2026-11-27","status":"SOURCE_OR_MODEL_HOLD","source":"10.1594/PANGAEA.876725","post_DivResource_exploratory":True,"source_rows_redistributed":False,"prior_Jena_association_unchanged":True}
    try:
        selftest()
        rows,info=source()
        result["source_audit"]=info
        result["analysis"]=evaluate(rows)
        result["status"]="JENA_TBE_FIXED_POOL_COMPONENT_TRANSFER_COMPLETE"
    except Exception as exc:
        result["failure_class"]=type(exc).__name__
        result["reason"]=str(exc)[:180] if isinstance(exc,ValueError) else "original source or numerical gate"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]!="JENA_TBE_FIXED_POOL_COMPONENT_TRANSFER_COMPLETE":raise SystemExit(1)
