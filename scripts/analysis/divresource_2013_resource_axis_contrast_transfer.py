#!/usr/bin/env python3
"""Fixed resource-axis contrast transfer. Original data; aggregate results only."""
from __future__ import annotations
import collections, hashlib, importlib.util, itertools, json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/divresource_2013_resource_axis_contrast_transfer_20261127_v0_1.json"
NAMES=("B","E","NDE","CE","SE","TDCE","DE")
CONTEXTS=list(itertools.product((0,1),repeat=2))  # fertilizer, shade
MODELS={"M0":((),()),"Mmatch":((1,),(0,)),"Mcross":((0,),(1,)),"Mfull":((0,1),(0,1))}
AXES=("height","functional_group")

def check(ok,msg):
    if not ok:raise ValueError(msg)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    check(spec is not None and spec.loader is not None,"required source module absent")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def partition(M,Y):
    M=np.asarray(M,float);Y=np.asarray(Y,float)
    check(np.isfinite(M).all() and np.all(M>0) and np.isfinite(Y).all() and np.all(Y>=0),"invalid original mono or mixture yield")
    B=float(Y.sum());E=float(M.mean());RY=float((Y/M).sum())
    check(RY>0,"zero RYT; Fox partition undefined")
    CE=(RY-1)*E;SE=B-RY*E;DE=B/RY-E;TDCE=SE-DE
    out=np.array([B,E,B-E,CE,SE,TDCE,DE])
    check(abs(out[2]-CE-SE)<1e-8 and abs(SE-TDCE-DE)<1e-8,"source partition identity failure")
    return out,Y/M

def source():
    parent=load("scripts/analysis/divresource_2013_ce_se_transfer.py","parent")
    # Actual source validation, including all 64 original Fox components.
    rows,audit=parent.audit_source(fox_components=True)
    check(all(audit.get(k)==64 for k in ("source_CE_interval_matches","source_SE_interval_matches","source_DE_interval_matches_if_requested","source_TDCE_interval_matches_if_requested")),"original 64 source Fox component gate")
    old=json.loads((ROOT/"results/divresource_2013_ce_se_transfer_20261127_v0_1.json").read_text())
    replay=parent.evaluate(rows)
    check(all(abs(replay["combined_gain"][k]-v)<1e-10 for k,v in old["analysis"]["combined_gain"].items()),"frozen previous CE/SE scores changed")
    oldfox=json.loads((ROOT/"results/divresource_2013_fox_components_20261127_v0_1.json").read_text())
    # Reproduce the frozen TDCE/DE prediction independently with the same rows.
    X=np.array([r["X"] for r in rows]);Y=np.array([[r["TDCE"],r["DE"]] for r in rows])
    sums=np.zeros((2,2))
    for p in ("A","B"):
        tr=np.array([r["pool"]==p for r in rows]);te=~tr
        for i,k in enumerate((6,7)):
            beta=np.linalg.lstsq(X[tr,:k],Y[tr],rcond=None)[0]
            sums[i]+=((Y[te]-X[te,:k]@beta)**2).sum(axis=0)
    check(np.allclose(1-sums[1]/sums[0],[oldfox["combined_gain"][k] for k in ("TDCE","DE")],atol=1e-10,rtol=0),"frozen previous TDCE/DE scores changed")
    a=load("scripts/analysis/divresource_2013_source_adapter.py","adapter")
    m=load("scripts/source/divresource_2013_original_schema.py","source_schema")
    raw=m.get("s008")
    check(hashlib.sha256(raw).hexdigest()==a.S5_SHA,"original S5 source bytes changed")
    data=a.source_records(m,raw,a.H5,96)
    cells=collections.defaultdict(list)
    for r in data:
        sp=tuple(sorted(s for s in a.SP if r[s]!="NA"))
        ctx=(r["Pool"],int(r["F"]),int(r["S"]))
        check(len(sp)==int(r["SR"]),"original species roster changed")
        cells[ctx+(sp,)].append(r)
    contrast=np.empty((2,4,2,len(NAMES)))
    direction=np.empty((2,4,2))
    matching_means=[]
    max_E=max_B_NDE=max_CE_SE=max_TDCE_DE=0.
    n_pairs=0
    for ip,p in enumerate(("A","B")):
        for it,(F,S) in enumerate(CONTEXTS):
            ctx=(p,F,S)
            tax=sorted(s for s in a.SP if len(cells.get(ctx+((s,),),[]))==1)
            check(len(tax)==4 and set(a.CLASSES[s] for s in tax)=={(0,0),(0,1),(1,0),(1,1)},"four original type cells not present")
            mono={s:float(a.decimal(cells[ctx+((s,),)][0][s])) for s in tax}
            matching=collections.defaultdict(list);member=collections.defaultdict(list)
            H=[];G=[]
            for sp in itertools.combinations(tax,2):
                r=cells.get(ctx+(sp,),[])
                check(len(r)==1,"one original pair per context required")
                vals,ry=partition([mono[s] for s in sp],[float(a.decimal(r[0][s])) for s in sp])
                cl=np.asarray([a.CLASSES[s] for s in sp])
                g,h=np.abs(cl[0]-cl[1])
                label={(0,1):"H_only",(1,0):"G_only",(1,1):"HG"}[(int(g),int(h))]
                matching[label].append(vals);member[label].extend(sp)
                if h:H.append(float(ry[cl[:,1]==1][0]-ry[cl[:,1]==0][0]))
                if g:G.append(float(ry[cl[:,0]==1][0]-ry[cl[:,0]==0][0]))
                n_pairs+=1
            for k in ("H_only","G_only","HG"):
                check(len(matching[k])==2 and sorted(member[k])==tax,"matching does not cover each original species exactly once")
            check(len(H)==len(G)==4,"directional relative yield support not four original pairs")
            means={k:np.mean(v,axis=0) for k,v in matching.items()}
            C=np.array([means["HG"]-means["G_only"],means["HG"]-means["H_only"]])
            contrast[ip,it]=C;direction[ip,it]=[np.mean(H),np.mean(G)]
            max_E=max(max_E,float(np.max(np.abs(C[:,1]))))
            max_B_NDE=max(max_B_NDE,float(np.max(np.abs(C[:,0]-C[:,2]))))
            max_CE_SE=max(max_CE_SE,float(np.max(np.abs(C[:,2]-C[:,3]-C[:,4]))))
            max_TDCE_DE=max(max_TDCE_DE,float(np.max(np.abs(C[:,4]-C[:,5]-C[:,6]))))
            matching_means.append({"pool":p,"fertilized":F,"shaded":S,"pair_plots":6,
                "contrasts":{axis:dict(zip(NAMES,map(float,C[i]))) for i,axis in enumerate(AXES)},
                "directional_mean_relative_yield_difference":dict(zip(AXES,map(float,direction[ip,it])))})
    check(n_pairs==48 and max(max_E,max_B_NDE,max_CE_SE,max_TDCE_DE)<1e-8,"source balanced matching contrast arithmetic failure")
    audit.update({"parent_CE_SE_TDCE_DE_scores_replayed":True,"same_48_two_species_original_plots":True,"all_8_balanced_matching_cells":True,
        "max_abs_E_contrast":max_E,"max_abs_B_minus_NDE_contrast":max_B_NDE,
        "max_abs_NDE_minus_CE_SE_contrast":max_CE_SE,"max_abs_SE_minus_TDCE_DE_contrast":max_TDCE_DE})
    return contrast,direction,matching_means,audit

def predictions(y,train,test,model):
    """One pool's four resource contexts -> the other; per-axis fixed models."""
    X=np.array(CONTEXTS,float)
    pred=np.zeros_like(y[test])
    coef=[]
    for axis,cols in enumerate(MODELS[model]):
        d=np.column_stack([np.ones(4),*[X[:,k] for k in cols]])
        check(np.linalg.matrix_rank(d)==d.shape[1],"fixed contrast design rank failure")
        b=np.linalg.lstsq(d,y[train,:,axis,:],rcond=None)[0]
        pred[:,axis,:]=d@b
        coef.append({("intercept" if i==0 else ("fertilizer" if cols[i-1]==0 else "shade")):
            dict(zip(NAMES,map(float,b[i]))) for i in range(len(b))})
    return pred,coef

def safe_gain(n,d):
    return None if d<=1e-12 else float(1-n/d)

def evaluate(y):
    # E is an exact algebraic zero and is intentionally unscored.
    folds=[];totals={k:np.zeros((2,len(NAMES))) for k in MODELS}
    for tr,te in ((0,1),(1,0)):
        scores={};coefs={}
        for model in MODELS:
            pred,b=predictions(y,tr,te,model)
            s=((y[te]-pred)**2).sum(axis=0)
            scores[model]=s;totals[model]+=s;coefs[model]={axis:b[i] for i,axis in enumerate(AXES)}
        g={}
        for j,k in enumerate(NAMES):
            if k=="E":continue
            g[k]={model:{"combined_axes_gain":safe_gain(scores[model][:,j].sum(),scores["M0"][:,j].sum()),
                "axis_gains":{ax:safe_gain(scores[model][i,j],scores["M0"][i,j]) for i,ax in enumerate(AXES)}}
                for model in MODELS if model!="M0"}
        folds.append({"train_pool":"AB"[tr],"test_pool":"AB"[te],"n_heldout_contexts":4,"gains":g,"train_coefficients":coefs})
    combined={}
    for j,k in enumerate(NAMES):
        if k=="E":continue
        g={model:{"combined_axes_gain":safe_gain(totals[model][:,j].sum(),totals["M0"][:,j].sum()),
            "axis_gains":{ax:safe_gain(totals[model][i,j],totals["M0"][i,j]) for i,ax in enumerate(AXES)},
            "axis_SSE":{ax:float(totals[model][i,j]) for i,ax in enumerate(AXES)}}
            for model in MODELS if model!="M0"}
        matched=g["Mmatch"]["combined_axes_gain"];cross=g["Mcross"]["combined_axes_gain"]
        vals=[f["gains"][k]["Mmatch"]["combined_axes_gain"] for f in folds]+list(g["Mmatch"]["axis_gains"].values())
        g["matched_criterion_pass"]=bool(matched is not None and cross is not None and matched>cross and all(v is not None and v>0 for v in vals))
        g["baseline_axis_SSE"]={ax:float(totals["M0"][i,j]) for i,ax in enumerate(AXES)}
        combined[k]=g
    return {"folds":folds,"combined":combined,"one_field_programme":True,"two_disjoint_pools":True,"n_original_pair_plots":48,"population_CI":None,"p_values":None}

def effects(z,names):
    # Average factor difference over other factor, independently for each pool.
    result={}
    for i,p in enumerate(("A","B")):
        result[p]={}
        for k,factor in enumerate(("fertilizer","shade")):
            plus=[t for t,c in enumerate(CONTEXTS) if c[k]==1];minus=[t for t,c in enumerate(CONTEXTS) if c[k]==0]
            d=z[i,plus].mean(axis=0)-z[i,minus].mean(axis=0)
            if z.ndim==4:result[p][factor]={axis:dict(zip(names,map(float,d[j]))) for j,axis in enumerate(AXES)}
            else:result[p][factor]=dict(zip(AXES,map(float,d)))
    return result

def selftest():
    # Exact design: adding arbitrary species main effects cancels in contrasts.
    cl=list(itertools.product((0,1),repeat=2))
    g=collections.defaultdict(list)
    for i,j in itertools.combinations(range(4),2):
        d=tuple(abs(a-b) for a,b in zip(cl[i],cl[j]))
        g[d].append((i,j))
    check(all(sorted(s for pair in v for s in pair)==list(range(4)) for v in g.values()),"synthetic balanced matching identity")
    mono=np.array([1.,10.,20.,80.])
    check(len({sum(mono[i]+mono[j] for i,j in v)/2 for v in g.values()})==1,"synthetic additive cancellation")
    # Known matched signal in both pools and all nonzero endpoints.
    y=np.zeros((2,4,2,len(NAMES)))
    for t,(f,s) in enumerate(CONTEXTS):
        y[:,t,0,:]=1+2*s;y[:,t,1,:]=2+3*f
    r=evaluate(y)
    check(all(v["matched_criterion_pass"] for v in r["combined"].values()),"synthetic known matched model transfer")
    print("SYNTHETIC_BALANCED_MATCHING_AND_KNOWN_TRANSFER_PASS")

def run():
    selftest()
    c,q,cells,audit=source()
    return {"date":"2026-11-27","status":"RESOURCE_AXIS_CONTRAST_TRANSFER_COMPLETE","original_source_DOI":"10.1371/journal.pone.0158110",
        "source_audit":audit,"analysis":evaluate(c),"resource_moderation_of_pair_contrasts_g_m2":effects(c,NAMES),
        "directional_RY_factor_effects":effects(q,AXES),"original_8_cell_aggregate_contrasts":cells,
        "post_result_exploratory":True,"raw_source_rows_redistributed":False,"previous_model_scores_unchanged":True,
        "causal_FD_or_competition_mechanism_claim":False,"root_trait_values_used":False}

if __name__=="__main__":
    try:j=run()
    except Exception as exc:j={"status":"SOURCE_OR_MODEL_HOLD","failure_class":type(exc).__name__,"reason":str(exc)[:180] if isinstance(exc,ValueError) else "source access or numerical gate"}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(j,ensure_ascii=False))
    if j["status"]!="RESOURCE_AXIS_CONTRAST_TRANSFER_COMPLETE":raise SystemExit(1)
