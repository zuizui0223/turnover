#!/usr/bin/env python3
"""Cadotte 2017: one frozen exploratory source-verified 40-mixture FD/NDE pilot.

Reads only an official public Zenodo CC0 deposit. No raw rows printed or committed.
No effect is admitted unless original source identities and exact denominators pass.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import pathlib
import urllib.error
import urllib.request

import numpy as np

BASE="https://zenodo.org/records/5022435/files/"
RECORD="https://zenodo.org/records/5022435"
SOURCE={
 "comp_select.csv":"079c2ef9fdf62a9b3c6bd40877d3e0d2",
 "planted.csv":"4e2bb17177a7f2be0347182b1f60ce27",
 "raw_biomass.csv":"73de6c8957f5a1c7729898057c4c339b",
 "species_traits_final2016.csv":"c4211aacdf298f9c2bee62dca95ee9f6"
}
MAX_FILE=35_000
MIN_MIX=30
SEED=20261120
N_BOOT=1000

def fail(code):
    raise RuntimeError(code)

def fetch(name):
    req=urllib.request.Request(BASE+name+"?download=1",
        headers={"User-Agent":"turnover-Cadotte-single-study-recovery/0.1",
                 "Accept":"text/csv,application/octet-stream"})
    with urllib.request.urlopen(req,timeout=40) as r:
        if r.status!=200:fail("ORIGINAL_SOURCE_NON_200")
        b=r.read(MAX_FILE+1)
        if len(b)>MAX_FILE:fail("ORIGINAL_SOURCE_SIZE_CAP")
    if hashlib.md5(b).hexdigest()!=SOURCE[name]:
        fail("ORIGINAL_MD5_IDENTITY_HOLD_"+name)
    return b

def csv_rows(name,data):
    s=data.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(s,newline=""))
    if not reader.fieldnames:fail("ORIGINAL_CSV_HEADER_MISSING_"+name)
    return [{(k or "").strip(): (v or "").strip() for k,v in r.items()} for r in reader]

def nfloat(v):
    try:
        x=float(str(v))
        return x if math.isfinite(x) else None
    except (ValueError,TypeError):
        return None

def index_unique(rows,key):
    keys=[r.get(key) for r in rows]
    if any(not x for x in keys) or len(keys)!=len(set(keys)):fail("SOURCE_PLOT_KEY_DUPLICATE_OR_EMPTY_"+key)
    return {r[key]:r for r in rows}

def core_join(source):
    c=csv_rows("comp_select.csv",source["comp_select.csv"])
    p=csv_rows("planted.csv",source["planted.csv"])
    b=csv_rows("raw_biomass.csv",source["raw_biomass.csv"])
    t=csv_rows("species_traits_final2016.csv",source["species_traits_final2016.csv"])
    needc={"COMP","SELECT","DeltaY","SPP_NUM","Biomass"}
    if not all(needc.issubset(r) for r in c):fail("COMP_SELECT_COLUMNS_MISSING")
    if not all({"Plot","biomass"}.issubset(r) for r in b):fail("ORIGINAL_BIOMASS_COLUMNS_MISSING")
    if not all({"SLA","field.height"}.issubset(r) for r in t):fail("TRAIT_COLUMNS_MISSING")
    cindex=index_unique(c,"")
    pindex=index_unique(p,"PLOT")
    bindex=index_unique(b,"Plot")
    trait=index_unique(t,"")
    tax=[k for k in p[0] if k not in ("PLOT","")]
    if len(trait)<10:fail("ORIGINAL_TRAIT_TAXON_COUNT_HOLD")
    if len(cindex)<MIN_MIX:fail("MIXTURE_SAMPLE_SUPPORT_HOLD")
    if len(set(tax))!=len(tax) or not set(tax).issubset(trait):fail("TAXON_CROSSWALK_HOLD")
    joined=[]; mismatches=0; component_mismatch=0; richness_mismatch=0
    for key,row in cindex.items():
        if key not in pindex or key not in bindex:fail("PLOT_JOIN_HOLD_"+key)
        listed=[k for k in tax if (nfloat(pindex[key].get(k)) or 0)>0]
        if not listed:fail("PLANTED_SPECIES_LIST_EMPTY")
        comp=nfloat(row["COMP"]);sel=nfloat(row["SELECT"]);nde=nfloat(row["DeltaY"])
        mass=nfloat(row["Biomass"]);rawmass=nfloat(bindex[key]["biomass"])
        if any(v is None for v in (comp,sel,nde,mass,rawmass)):fail("ORIGINAL_NUMERIC_RESPONSE_MISSING")
        if abs(comp+sel-nde)>1e-5:component_mismatch+=1
        if abs(mass-rawmass)>.15:mismatches+=1
        richness=nfloat(row["SPP_NUM"])
        if richness is None or richness<2:fail("ORIGINAL_NOT_MIXTURE")
        if len(listed)!=int(richness):richness_mismatch+=1
        vals=[]
        for species in listed:
            rowtrait=trait[species]
            sla=nfloat(rowtrait["SLA"]);height=nfloat(rowtrait["field.height"])
            if sla is None or height is None or sla<=0 or height<=0:
                fail("ORIGINAL_PRE_MIX_TRAIT_MISSING")
            vals.append((math.log(sla),math.log(height)))
        joined.append({
            "id":key,"composition":tuple(sorted(listed)),"richness_planted":len(listed),
            "traits":np.asarray(vals,dtype=float),"mass":mass,"NDE":nde,"COMP":comp,"SELECT":sel,
        })
    if mismatches or component_mismatch:fail("ORIGINAL_RESPONSE_COMPONENT_IDENTITY_HOLD")
    if richness_mismatch:fail("PLANTED_VS_REALIZED_RICHNESS_DIFFER_HOLD")
    if len(joined)<MIN_MIX:fail("COMPLETE_CASE_SUPPORT_HOLD")
    if len({z["composition"] for z in joined})<30:fail("COMPOSITION_HOLDOUT_SUPPORT_HOLD")
    return joined,{
        "source_original_comp_select_rows":len(c),
        "source_original_planted_rows":len(p),
        "source_original_biomass_rows":len(b),
        "source_original_trait_taxa":len(trait),
        "source_pre_mixing_named_taxon_columns":len(tax),
        "source_joined_mixture_rows":len(joined),
        "unique_source_composition_groups":len({z["composition"] for z in joined}),
        "component_identity_failures":component_mismatch,
        "biomass_original_cross_source_failures":mismatches,
        "sown_vs_realized_richness_mismatches":richness_mismatch
    }

def build_features(train,test):
    # SOURCE train only defines two trait scales and numerical CWM standardization.
    pool=np.vstack([r["traits"] for r in train])
    std=pool.std(axis=0,ddof=0)
    if np.any(std<=1e-10):fail("TRAIT_AXIS_ZERO_TRAIN_SD")
    def make(rows):
        x=[]
        for r in rows:
            t=r["traits"]/std
            cwm=np.mean(t,axis=0)
            if len(t)<2:fail("SINGLETON_IN_MIXTURE")
            pairs=[np.linalg.norm(t[i]-t[j]) for i in range(len(t)) for j in range(i+1,len(t))]
            fd=sum(pairs)/len(pairs)
            x.append([math.log2(r["richness_planted"]),cwm[0],cwm[1],fd])
        return np.asarray(x,dtype=float)
    tr=make(train);te=make(test)
    # Training-only scale/centering applied to same covariates in M0 and M1.
    mu=tr.mean(axis=0);scale=tr.std(axis=0,ddof=0)
    if np.any(scale<=1e-8):fail("MODEL_DESIGN_SOURCE_SUPPORT_HOLD")
    return (tr-mu)/scale,(te-mu)/scale

def predict_cv(rows):
    groups=collections.defaultdict(list)
    for i,r in enumerate(rows):groups[r["composition"]].append(i)
    keylist=sorted(groups)
    pred={name:{"M0":np.full(len(rows),np.nan),"M1":np.full(len(rows),np.nan)}
        for name in ("mass","NDE","COMP","SELECT")}
    for key in keylist:
        test_idx=groups[key]
        train_idx=[i for i in range(len(rows)) if i not in test_idx]
        tr=[rows[i] for i in train_idx];te=[rows[i] for i in test_idx]
        if len(tr)<MIN_MIX-1:fail("FOLD_LESS_THAN_MIN_TRAIN")
        xt,xs=build_features(tr,te)
        X0=np.column_stack((np.ones(len(tr)),xt[:,:3]))
        X1=np.column_stack((X0,xt[:,3]))
        T0=np.column_stack((np.ones(len(te)),xs[:,:3]))
        T1=np.column_stack((T0,xs[:,3]))
        if np.linalg.matrix_rank(X1)<5:fail("TRAINING_PREDICTOR_RANK_HOLD")
        for y in pred:
            target=np.asarray([r[y] for r in tr])
            for mod,X,T in (("M0",X0,T0),("M1",X1,T1)):
                beta=np.linalg.lstsq(X,target,rcond=None)[0]
                pred[y][mod][test_idx]=T@beta
    return pred,groups

def source_group_bootstrap(rows,pred,groups):
    gains={}
    for endpoint in pred:
        obs=np.array([r[endpoint] for r in rows],float)
        if not all(np.isfinite(pred[endpoint][x]).all() for x in ("M0","M1")):
            fail("NONFINITE_CV_PREDICTION")
        e0=(obs-pred[endpoint]["M0"])**2
        e1=(obs-pred[endpoint]["M1"])**2
        gains[endpoint]={
            "gain":float(1-e1.sum()/e0.sum()),
            "sse_baseline":float(e0.sum()),
            "sse_fd_added":float(e1.sum())
        }
        if e0.sum()<=0:fail("ZERO_BASELINE_SSE")
    ks=list(groups)
    ng=len(ks)
    rng=np.random.default_rng(SEED)
    samples={end:np.empty(N_BOOT) for end in gains}
    for b in range(N_BOOT):
        chosen=rng.integers(0,ng,ng)
        sample_rows=np.concatenate([groups[ks[i]] for i in chosen])
        for end in gains:
            obs=np.array([r[end] for r in rows],float)[sample_rows]
            s0=float(np.sum((obs-pred[end]["M0"][sample_rows])**2))
            s1=float(np.sum((obs-pred[end]["M1"][sample_rows])**2))
            samples[end][b]=1-s1/s0 if s0>0 else np.nan
    for end in gains:
        valid=samples[end][np.isfinite(samples[end])]
        if len(valid)<900:fail("BOOTSTRAP_SUPPORT_HOLD")
        gains[end]["composition_bootstrap_ci95"]=np.quantile(valid,[.025,.975]).tolist()
    diff=float(gains["NDE"]["gain"]-gains["mass"]["gain"])
    diffdraw=samples["NDE"]-samples["mass"]
    diffdraw=diffdraw[np.isfinite(diffdraw)]
    return {
        "source_group_holdout_count":ng,
        "composition_bootstrap_replicates":N_BOOT,
        "descriptive_gain_difference_NDE_minus_absolute_mass":diff,
        "paired_group_bootstrap_ci95":np.quantile(diffdraw,[.025,.975]).tolist(),
        "endpoint_predictive_gain":gains
    }

def run(out):
    result={
        "source":"Cadotte 2017 Ecology Letters original Dryad CC0 Zenodo 5022435",
        "original_source_doi":"10.5061/dryad.627rt",
        "source_url":RECORD,
        "source_status":"SOURCE_ACCESS_HOLD",
        "analysis_status":"NO_MODEL_SOURCE_HOLD",
        "scientific_role":"RETROSPECTIVE_SINGLE_STUDY_PILOT_NOT_INDEPENDENT_CONFIRMATION",
        "outcome_preview_and_published_directions_seen_before_pilot_protocol":True,
        "no_causal_FD_mediation_claim":True,
        "no_global_generalization_claim":True,
        "no_original_species_rows_redistributed":True,
        "original_MD5_provenance":SOURCE,
        "raw_original_numeric_observations_exported":False
    }
    try:
        payload={k:fetch(k) for k in SOURCE}
        joined,coverage=core_join(payload)
        result["source_status"]="ORIGINAL_SOURCE_IDENTITIES_AND_JOIN_PASS"
        result["source_counts"]=coverage
        pred,groups=predict_cv(joined)
        effect=source_group_bootstrap(joined,pred,groups)
        result["effect"]=effect
        result["analysis_status"]="RETROSPECTIVE_EXPLORATORY_CV_PILOT_COMPLETE"
        result["no_new_hypothesis_selection"]=True
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
            RuntimeError,ValueError,OSError) as e:
        result["source_or_analysis_hold_class"]=type(e).__name__
        if isinstance(e,urllib.error.HTTPError):
            result["official_source_download_HTTP"]=e.code
        if isinstance(e,RuntimeError):
            result["scientific_stop_rule"]=str(e)[:100]
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("CADOTTE_2017_PILOT_VERDICT "+json.dumps({
        "status":result["analysis_status"],
        "source_status":result["source_status"],
        "source_http":result.get("official_source_download_HTTP"),
        "source_joined_mixtures":result.get("source_counts",{}).get("source_joined_mixture_rows"),
        "gain_NDE":result.get("effect",{}).get("endpoint_predictive_gain",{}).get("NDE",{}).get("gain"),
        "gain_absolute":result.get("effect",{}).get("endpoint_predictive_gain",{}).get("mass",{}).get("gain"),
        "gain_difference":result.get("effect",{}).get("descriptive_gain_difference_NDE_minus_absolute_mass"),
        "no_causal_claim":True
    },sort_keys=True))

def test():
    assert nfloat("0")==0 and nfloat("1.2")==1.2
    assert nfloat("NA") is None and nfloat("") is None
    assert len(SOURCE)==4
    assert N_BOOT==1000 and SEED==20261120
    # Original-effect identity arithmetic, not fitted data.
    assert abs(22.20427779-3.822325937-18.38195185)<1e-5
    print('{"status":"CADOTTE_SYNTHETIC_AND_SOURCE_SEMANTIC_TEST_PASS","checks":6}')

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=pathlib.Path)
    a=p.parse_args()
    if a.self_test:test()
    elif a.out:run(a.out)
    else:p.error("Specify --out or --self-test")
