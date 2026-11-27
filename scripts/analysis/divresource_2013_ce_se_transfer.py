#!/usr/bin/env python3
"""Fixed exploratory CE/SE transfer using exact parent source and original S6.

No original row values published; no new cohort, trait or response selection.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,itertools,json,math
from decimal import Decimal
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/divresource_2013_ce_se_transfer_20261127_v0_1.json"
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    if spec is None or spec.loader is None:raise ValueError("source module unavailable")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def audit_source():
    a=load("scripts/analysis/divresource_2013_source_adapter.py","original_adapter")
    source=load("scripts/source/divresource_2013_original_schema.py","source_schema")
    core=load("scripts/analysis/divresource_2013_pool_transfer_core.py","original_core")
    raw5=source.get("s008");raw6=source.get("s009")
    if hashlib.sha256(raw5).hexdigest()!=a.S5_SHA or hashlib.sha256(raw6).hexdigest()!=a.S6_SHA:
        raise ValueError("original S5/S6 checksum mismatch")
    # Independently replay parent adapter using exactly these byte buffers.
    # The parent uses only the pinned official get() endpoints; no network
    # replacement or change to its numeric source checks.
    old_load=a.load
    def reuse(path,name):
        if path=="scripts/source/divresource_2013_original_schema.py":
            source.get=lambda suffix:{"s008":raw5,"s009":raw6}[suffix]
            return source
        return old_load(path,name)
    a.load=reuse
    parent_audit,parent_result=a.source_adapter()
    committed=json.loads((ROOT/"results/divresource_2013_pool_transfer_v0_1.json").read_text())
    for endpoint in ("B","NDE"):
        expected=committed["results"]["endpoint_results"][endpoint]
        got=parent_result["endpoint_results"][endpoint]
        if abs(expected["pool_equal_gain"]-got["pool_equal_gain"])>1e-10:
            raise ValueError("parent frozen outcome replay differs")
    s5=a.source_records(source,raw5,a.H5,96);s6=a.source_records(source,raw6,a.H6,64)
    q={r["Plot"]:r for r in s6}
    bycell=collections.defaultdict(list)
    for r in s5:
        s=tuple(sorted(k for k in a.SP if r[k]!="NA"))
        t=f"F{'+' if r['F']=='1' else '-'}S{'+' if r['S']=='1' else '-'}"
        bycell[(r["Pool"],t,s)].append(r)
    def bounds(v,nonnegative=False):
        z=a.decimal(v);d=a.uncertainty(z)
        return (max(Decimal(0),z-d) if nonnegative else z-d,z+d)
    def add(intervals):
        return sum(x[0] for x in intervals),sum(x[1] for x in intervals)
    def mul(x,y):
        vals=[u*v for u in x for v in y];return min(vals),max(vals)
    def div_pos(x,y):
        if y[0]<=0:raise ValueError("source monoculture denominator not positive at printed precision")
        return x[0]/y[1],x[1]/y[0]
    def overlaps(a,b):
        return min(a[1],b[1])+Decimal("0.00000001")>=max(a[0],b[0])
    rows=[];n_ce=n_se=0;max_diff=0.;max_ce_diff=0.;max_se_diff=0.
    for (pool,t,ss),recs in bycell.items():
        k=len(ss)
        if k==1:continue
        for r in recs:
            m=[bycell[(pool,t,(s,))] for s in ss]
            if any(len(z)!=1 for z in m):raise ValueError("one original monoculture per species/context required")
            mi=[bounds(z[0][s],True) for z,s in zip(m,ss)]
            yi=[bounds(r[s],True) for s in ss]
            raw_m=[a.decimal(z[0][s]) for z,s in zip(m,ss)]
            raw_y=[a.decimal(r[s]) for s in ss]
            if any(x<=0 for x in raw_m):raise ValueError("nonpositive source monoculture")
            M=add(mi);M=(M[0]/k,M[1]/k)
            R=add([div_pos(y,z) for y,z in zip(yi,mi)])
            ce=mul(M,(R[0]-1,R[1]-1))
            Y=add(yi)
            se=(Y[0]-M[1]-ce[1],Y[1]-M[0]-ce[0])
            original=q[r["Plot"]]
            if original["Block"]!=r["Block"]:raise ValueError("physical source block mismatch")
            ce_obs=bounds(original["TICE"])
            se_obs=add([bounds(original["TDCE"]),bounds(original["DE"])])
            if not overlaps(ce,ce_obs):raise ValueError("CE reconstructed from species mass does not match published TICE interval")
            if not overlaps(se,se_obs):raise ValueError("SE reconstructed from species mass does not match published TDCE+DE interval")
            n_ce+=1;n_se+=1
            ce_value=a.decimal(original["TICE"])
            se_value=a.decimal(original["TDCE"])+a.decimal(original["DE"])
            mean_m=sum(raw_m)/k
            reconstructed_ce=mean_m*(sum(y/z for y,z in zip(raw_y,raw_m))-1)
            reconstructed_se=sum(raw_y)-mean_m-reconstructed_ce
            max_ce_diff=max(max_ce_diff,float(abs(reconstructed_ce-ce_value)))
            max_se_diff=max(max_se_diff,float(abs(reconstructed_se-se_value)))
            max_diff=max(max_diff,float(abs(ce_value+se_value-(a.decimal(r["BM"])-mean_m))))
            if k!=2:continue
            classes=[a.CLASSES[s] for s in ss]
            gm=(classes[0][0]+classes[1][0])/2
            hm=(classes[0][1]+classes[1][1])/2
            D=(abs(classes[0][0]-classes[1][0])+abs(classes[0][1]-classes[1][1]))/2
            rows.append({"pool":pool,"X":[1.,*(float(t==u) for u in core.TREATMENTS[1:]),gm,hm,D],
                         "CE":float(ce_value),"SE":float(se_value)})
    if (n_ce,n_se)!=(64,64) or len(rows)!=48 or collections.Counter(r["pool"] for r in rows)!={"A":24,"B":24}:
        raise ValueError("fixed original source component cohort changed")
    return rows,{"parent_original_B_NDE_replay":True,"source_CE_interval_matches":n_ce,"source_SE_interval_matches":n_se,
                 "source_max_absolute_CE_central_rounding_difference_g_m2":max_ce_diff,
                 "source_max_absolute_SE_central_rounding_difference_g_m2":max_se_diff,
                 "source_max_abs_NDE_components_minus_B_minus_E_all_64_g_m2":max_diff,
                 "original_source_S5_SHA256":a.S5_SHA,"original_source_S6_SHA256":a.S6_SHA}

def evaluate(rows):
    X=np.array([r["X"] for r in rows])
    Y=np.array([[r["CE"],r["SE"]] for r in rows])
    if X.shape!=(48,7) or Y.shape!=(48,2) or not np.isfinite(Y).all():
        raise ValueError("invalid fixed model design")
    reports=[];max_identity=0.
    for p,other in (("A","B"),("B","A")):
        train=np.array([r["pool"]==p for r in rows]);test=~train
        if train.sum()!=24 or test.sum()!=24:raise ValueError("original balanced pair cohort mismatch")
        errors=[];coefficients=[]
        for k in (6,7):
            x=X[train,:k]
            if np.linalg.matrix_rank(x)!=k:raise ValueError("model rank HOLD")
            beta=np.linalg.lstsq(x,Y[train],rcond=None)[0]
            errors.append(Y[test]-X[test,:k]@beta)
            coefficients.append(beta)
        e0,e1=errors
        sums=[]
        for e in errors:
            sums.append({"CE":float(e[:,0]@e[:,0]),"SE":float(e[:,1]@e[:,1]),
                "NDE_components":float(e.sum(axis=1)@e.sum(axis=1)),
                "twice_cross_product":float(2*(e[:,0]@e[:,1]))})
        change={k:sums[1][k]-sums[0][k] for k in sums[0]}
        error=change["NDE_components"]-change["CE"]-change["SE"]-change["twice_cross_product"]
        max_identity=max(max_identity,abs(error))
        if abs(error)>1e-6:raise ValueError("component residual change identity failed")
        gain={}
        for k in ("CE","SE","NDE_components"):
            if sums[0][k]<=1e-10:raise ValueError("nonpositive heldout baseline SSE")
            gain[k]=1-sums[1][k]/sums[0][k]
        b=coefficients[1][-1]
        reports.append({"train_pool":p,"test_pool":other,"n":24,
            "D_coefficients_g_m2_per_unit":{"CE":float(b[0]),"SE":float(b[1]),"NDE_components":float(b.sum())},
            "SSE_M0":sums[0],"SSE_M1":sums[1],"delta_SSE":change,"gain":gain,
            "CE_minus_SE_gain":gain["CE"]-gain["SE"]})
    combined={}
    for k in ("CE","SE","NDE_components"):
        combined[k]=1-sum(x["SSE_M1"][k] for x in reports)/sum(x["SSE_M0"][k] for x in reports)
    return {"folds":reports,"combined_gain":combined,"combined_CE_minus_SE_gain":combined["CE"]-combined["SE"],
        "max_residual_change_identity_error":max_identity,"number_physical_mixture_plots":48,
        "independent_field_programmes":1,"disjoint_species_pools":2,
        "population_CI":None,"causal_FD_only":False,"source_4species_not_fitted":True,
        "interpretation":"post-result fixed source component prediction, signed statistical accounting; no causal resource process established"}

def main():
    result={"date":"2026-11-27","status":"SOURCE_OR_MODEL_HOLD",
        "original_source_DOI":"10.1371/journal.pone.0158110","raw_source_rows_released":False,
        "prior_B_NDE_result_unchanged":True}
    try:
        rows,audit=audit_source()
        result["source_audit"]=audit
        result["analysis"]=evaluate(rows)
        result["status"]="EXPLORATORY_CE_SE_TRANSFER_COMPLETE"
    except Exception as e:
        result["failure_class"]=type(e).__name__
        result["failure_reason"]=str(e)[:150] if isinstance(e,ValueError) else "source or calculation error"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]!="EXPLORATORY_CE_SE_TRANSFER_COMPLETE":
        raise SystemExit(1)

if __name__=="__main__":main()
