#!/usr/bin/env python3
"""Post-SE-result exploratory two Fox components, fixed original source/folds."""
import importlib.util,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
def run():
    spec=importlib.util.spec_from_file_location("fixed_ce_se",ROOT/"scripts/analysis/divresource_2013_ce_se_transfer.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    rows,audit=mod.audit_source(fox_components=True)
    if audit["source_DE_interval_matches_if_requested"]!=64 or audit["source_TDCE_interval_matches_if_requested"]!=64:
        raise ValueError("all 64 original Fox component identities required")
    previous=json.loads((ROOT/"results/divresource_2013_ce_se_transfer_20261127_v0_1.json").read_text())
    replay=mod.evaluate(rows)
    for k,v in previous["analysis"]["combined_gain"].items():
        if abs(replay["combined_gain"][k]-v)>1e-10:raise ValueError("previous fixed CE/SE result changed")
    X=np.array([r["X"] for r in rows]);Y=np.array([[r["TDCE"],r["DE"]] for r in rows])
    if not np.allclose(Y.sum(axis=1),[r["SE"] for r in rows],rtol=0,atol=1e-10):
        raise ValueError("Fox components do not equal source SE")
    folds=[]
    for p,other in (("A","B"),("B","A")):
        tr=np.array([r["pool"]==p for r in rows]);te=~tr
        scores=[];beta=None
        for k in (6,7):
            a=X[tr,:k]
            if np.linalg.matrix_rank(a)!=k:raise ValueError("frozen source model rank changed")
            beta=np.linalg.lstsq(a,Y[tr],rcond=None)[0]
            e=Y[te]-X[te,:k]@beta
            scores.append({"TDCE":float(e[:,0]@e[:,0]),"DE":float(e[:,1]@e[:,1]),"SE":float(e.sum(axis=1)@e.sum(axis=1)),"twice_cross_product":float(2*(e[:,0]@e[:,1]))})
        delta={k:scores[1][k]-scores[0][k] for k in scores[0]}
        if abs(delta["SE"]-delta["TDCE"]-delta["DE"]-delta["twice_cross_product"])>1e-6:raise ValueError("SE residual identity failed")
        gain={k:1-scores[1][k]/scores[0][k] for k in ("TDCE","DE","SE")}
        folds.append({"train_pool":p,"test_pool":other,"n":int(te.sum()),"SSE_M0":scores[0],"SSE_M1":scores[1],"delta_SSE":delta,"gain":gain,
         "D_coefficients":{"TDCE":float(beta[-1,0]),"DE":float(beta[-1,1]),"SE":float(beta[-1].sum())}})
    combined={k:1-sum(f["SSE_M1"][k] for f in folds)/sum(f["SSE_M0"][k] for f in folds) for k in ("TDCE","DE","SE")}
    if abs(combined["SE"]-replay["combined_gain"]["SE"])>1e-10:raise ValueError("SE prediction arithmetic differs")
    return {"status":"FOX_COMPONENTS_EXPLORATORY_COMPLETE","post_SE_result_followup":True,"source_audit":audit,"folds":folds,"combined_gain":combined,
       "pooled_delta_SSE":{k:sum(f["delta_SSE"][k] for f in folds) for k in folds[0]["delta_SSE"]},
       "same_48_original_pair_plots":True,"original_field_programmes":1,"disjoint_pools":2,
       "population_CI":None,"causal_FD_only":False,"prior_CE_SE_result_unchanged":True}
if __name__=="__main__":
    out=ROOT/"results/divresource_2013_fox_components_20261127_v0_1.json"
    try:result=run()
    except Exception as e:
        result={"status":"SOURCE_OR_MODEL_HOLD","failure_class":type(e).__name__,"reason":str(e)[:160] if isinstance(e,ValueError) else "source/calculation failure"}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
    if result["status"]!="FOX_COMPONENTS_EXPLORATORY_COMPLETE":raise SystemExit(1)
