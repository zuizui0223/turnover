#!/usr/bin/env python3
"""Source-locked 2025 Chen 452-study original data; prequalified retrospective
study-held-out CE/SE predictive transfer for planted Rao Q leaf N and SLA.

No raw rows, paper names, study labels, plot/species IDs or per-study outcomes
are persisted. No causal parameter, new choice of predictor or P-value search.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

FILES={
 "leafN":{"name":"Data_Mix_LN_no outliers_241019.csv","id":50036712,
          "md5":"cbf1955398018ba892e52abe2ca8c315",
          "n_source":2273,"n_source_studies":213,
          "fd":"RaoQLN","cwm":"CWMLN"},
 "SLA":{"name":"Data_Mix_SLA_no outliers_241019.csv","id":50036718,
        "md5":"df6b948bd892c3a04595e0f8f83c0f8b",
        "n_source":2784,"n_source_studies":247,
        "fd":"RaoQSLA","cwm":"CWMSLA"}
}
TARGETS=["CE","SE","CE_minus_SE"]
SOURCE_FROZEN="docs/CHEN452_LEAFN_FD_CE_SE_STUDY_HOLDOUT_FROZEN_V0_1.md"
B=2000
SEED=20261120
COMMON=["StudyID","ObserveID","Study","SR","StandAge_year","PD","MAT","AI",
        "Eco1","PlantType","FD_WithNFix","CE","SE","DY"]
MISSING={"","na","nan","null","none","n/a","-9999","."}
MAX_DATA_BYTES=1_800_000

class SourceHold(Exception):
    pass

def ensure(c,reason):
    if not c:raise SourceHold(reason)

def maybe_num(value):
    if value is None or str(value).strip().lower() in MISSING:return None
    try:
        x=float(str(value).strip())
        return x if math.isfinite(x) else None
    except (ValueError,OverflowError):return None

def raw_public(name,ident,md5):
    url=f"https://api.figshare.com/v2/file/download/{ident}"
    req=urllib.request.Request(url,headers={
      "User-Agent":"turnover-Chen452-frozen-leafFD-studyholdout/0.1",
      "Accept":"text/csv,application/octet-stream"})
    with urllib.request.urlopen(req,timeout=45) as r:
        if r.status!=200:raise SourceHold("OFFICIAL_SOURCE_HTTP_NOT_200")
        b=r.read(MAX_DATA_BYTES+1)
    ensure(len(b)<=MAX_DATA_BYTES,"ORIGINAL_SOURCE_EXCEEDS_BYTES")
    ensure(hashlib.md5(b).hexdigest()==md5,"ORIGINAL_SOURCE_MD5_CHANGED")
    try:s=b.decode("utf-8-sig")
    except UnicodeDecodeError:s=b.decode("cp1252")
    rd=csv.DictReader(io.StringIO(s,newline=""))
    headers=rd.fieldnames
    ensure(headers is not None,"SOURCE_NO_HEADER")
    rows=list(rd)
    ensure(all(None not in r for r in rows),"SOURCE_CSV_FIELD_COUNT_ERROR")
    return headers,rows,hashlib.sha256(b).hexdigest()

def assemble(which):
    d=FILES[which]
    headers,orig,sha=raw_public(d["name"],d["id"],d["md5"])
    ensure(len(orig)==d["n_source"],"ORIGINAL_ROW_COUNT_DRIFT")
    ensure(set(COMMON+[d["fd"],d["cwm"]]).issubset(headers),"ORIGINAL_VARIABLES_MISSING")
    groups=collections.defaultdict(list)
    studylabel={}
    observes=set()
    cleaned=[]
    bad_additive=0
    source_missing=0
    invalid_domain=0
    for r in orig:
        study=str(r["StudyID"]).strip()
        obs=str(r["ObserveID"]).strip()
        author_label=str(r["Study"]).strip()
        ensure(study and obs and author_label,"SOURCE_STUDY_ID_OR_OBSERVATION_MISSING")
        ensure(obs not in observes,"SOURCE_OBSERVATION_ID_DUPLICATE")
        observes.add(obs)
        if study in studylabel:
            ensure(studylabel[study]==author_label,"STUDY_ID_MULTIPLE_ORIGINAL_LABELS")
        else:studylabel[study]=author_label
        needed=["SR","StandAge_year","PD",d["cwm"],"MAT","AI","FD_WithNFix",
                d["fd"],"CE","SE","DY"]
        val={k:maybe_num(r[k]) for k in needed}
        if any(v is None for v in val.values()) or any(not str(r.get(k,"")).strip() for k in ("Eco1","PlantType")):
            source_missing+=1
            continue
        if val["SR"]<=1 or val["StandAge_year"]<0 or val[d["fd"]]<0:
            invalid_domain+=1
            continue
        if abs(val["CE"]+val["SE"]-val["DY"])>1e-6*max(1,abs(val["DY"])):
            bad_additive+=1
        group_label=study
        row={"group":group_label,"eco":str(r["Eco1"]),"plant":str(r["PlantType"]),
             "rich":val["SR"],"age":val["StandAge_year"],
             "pd":val["PD"],"cwm":val[d["cwm"]],
             "MAT":val["MAT"],"AI":val["AI"],"nfix":val["FD_WithNFix"],
             "FD":val[d["fd"]],"CE":val["CE"],"SE":val["SE"],
             "CE_minus_SE":val["CE"]-val["SE"]}
        groups[group_label].append(len(cleaned))
        cleaned.append(row)
    summary={
      "source_file":d["name"],"source_file_id":d["id"],"source_sha256":sha,
      "published_original_rows":len(orig),"published_original_StudyIDs":len(studylabel),
      "original_distinct_ObserveIDs":len(observes),
      "source_rows_missing_any_fixed_variable":source_missing,
      "source_rows_failing_fixed_physical_support":invalid_domain,
      "original_additive_CE_SE_DY_mismatches":bad_additive,
      "paired_complete_case_mixture_rows":len(cleaned),
      "paired_complete_case_distinct_studies":len(groups),
      "distinct_studies_with_at_least_5_rows":sum(len(v)>=5 for v in groups.values()),
      "categorical_ecosystem_classes":len({r["eco"] for r in cleaned}),
      "categorical_plant_types":len({r["plant"] for r in cleaned}),
      "source_no_author_labels_exported":True
    }
    ensure(len(studylabel)==d["n_source_studies"],"SOURCE_AUTHOR_STUDY_ID_COUNT_DRIFT")
    ensure(bad_additive==0,"ORIGINAL_CE_PLUS_SE_NOT_EQUAL_DY")
    ensure(len(cleaned)>=300,"SOURCE_COHORT_BELOW_300")
    ensure(len(groups)>=30,"SOURCE_DISTINCT_STUDIES_BELOW_30")
    ensure(sum(len(v)>=5 for v in groups.values())>=30,
           "SOURCE_STUDY_REPLICATE_SUPPORT_BELOW_30")
    ensure(len({r["rich"] for r in cleaned})>=2,"SOURCE_RICHNESS_NO_VARIATION")
    ensure(len({r["eco"] for r in cleaned})>=2,"SOURCE_ECOSYSTEM_NO_VARIATION")
    return cleaned,groups,summary

def numeric(r):
    return [math.log2(r["rich"]),math.log1p(r["age"]),r["pd"],
            r["cwm"],r["MAT"],r["AI"]]

def weights_for_train(rows,train_ix):
    n=collections.Counter(rows[i]["group"] for i in train_ix)
    w=np.array([1/n[rows[i]["group"]] for i in train_ix],float)
    return w

def design(rows,train_ix,test_ix):
    tr=[rows[i] for i in train_ix]
    te=[rows[i] for i in test_ix]
    w=weights_for_train(rows,train_ix)
    numer_train=np.array([numeric(x) for x in tr],float)
    numer_test=np.array([numeric(x) for x in te],float)
    mu=np.average(numer_train,axis=0,weights=w)
    sd=np.sqrt(np.average((numer_train-mu)**2,axis=0,weights=w))
    ensure(np.all(sd>1e-10),"MODEL_SOURCE_NUMERIC_VARIANCE_HOLD")
    nt=(numer_train-mu)/sd
    ne=(numer_test-mu)/sd
    categorical_train=[]
    categorical_test=[]
    unseen=0
    for col in ("eco","plant"):
        values=sorted({x[col] for x in tr})
        ensure(len(values)>=2,"MODEL_ORIGINAL_CATEGORY_VARIATION_HOLD")
        for val in values[1:]:
            categorical_train.append([float(x[col]==val) for x in tr])
            categorical_test.append([float(x[col]==val) for x in te])
        unseen+=sum(x[col] not in values for x in te)
    def columns(n,cat):
        return np.column_stack([
            np.ones(len(n)),
            n,
            np.array([r["nfix"] for r in (tr if cat=="train" else te)]),
            *(np.array(v) for v in (categorical_train if cat=="train" else categorical_test))
        ])
    x0=columns(nt,"train")
    t0=columns(ne,"test")
    fd_train=np.array([r["FD"] for r in tr],float)
    fd_test=np.array([r["FD"] for r in te],float)
    fd_mu=np.average(fd_train,weights=w)
    fd_sd=np.sqrt(np.average((fd_train-fd_mu)**2,weights=w))
    ensure(fd_sd>1e-10,"MODEL_ORIGINAL_FD_NEAR_CONSTANT_HOLD")
    x1=np.column_stack((x0,(fd_train-fd_mu)/fd_sd))
    t1=np.column_stack((t0,(fd_test-fd_mu)/fd_sd))
    ensure(np.linalg.matrix_rank(x1)==x1.shape[1],"SOURCE_TRAINING_FOLD_RANK_HOLD")
    cond=np.linalg.cond(x1)
    ensure(math.isfinite(cond) and cond<=1e8,"SOURCE_TRAINING_CONDITION_NUMBER_HOLD")
    return x0,x1,t0,t1,w,unseen,cond

def folds_qualified(rows,groups):
    lookup=sorted(groups)
    all_i=list(range(len(rows)))
    maxcond=0.
    unseen=0
    fixed_feature_counts=set()
    for group in lookup:
        te=groups[group]
        tex=set(te)
        tr=[i for i in all_i if i not in tex]
        ensure(len(tr)>=300,"SOURCE_FOLD_TRAIN_SUPPORT_HOLD")
        x0,x1,t0,t1,w,nu,cond=design(rows,tr,te)
        fixed_feature_counts.add(x1.shape[1])
        maxcond=max(maxcond,cond)
        unseen+=nu
    return {"n_source_holdout_folds":len(lookup),
            "max_train_condition_number":maxcond,
            "different_training_design_column_counts":sorted(fixed_feature_counts),
            "heldout_observations_with_unseen_categorical_level":unseen}

def model_predictions(rows,groups):
    preds={name:{"M0":np.full(len(rows),np.nan),"M1":np.full(len(rows),np.nan)}
           for name in TARGETS}
    all_i=list(range(len(rows)))
    for group in sorted(groups):
        test_idx=groups[group]
        te_set=set(test_idx)
        train_idx=[i for i in all_i if i not in te_set]
        x0,x1,t0,t1,w,nu,cond=design(rows,train_idx,test_idx)
        sw=np.sqrt(w)
        for name in TARGETS:
            yy=np.array([rows[i][name] for i in train_idx],float)
            for model,x,t in (("M0",x0,t0),("M1",x1,t1)):
                beta=np.linalg.lstsq(sw[:,None]*x,sw*yy,rcond=None)[0]
                preds[name][model][test_idx]=t@beta
    ensure(all(np.isfinite(x).all() for q in preds.values() for x in q.values()),
           "PREDICTION_NONFINITE_HOLD")
    return preds

def summarise(rows,groups,preds):
    ordered=sorted(groups)
    endpoints={}
    for name in TARGETS:
        obs=np.array([r[name] for r in rows],float)
        e0=(obs-preds[name]["M0"])**2
        e1=(obs-preds[name]["M1"])**2
        per=np.array([[e0[groups[s]].mean(),e1[groups[s]].mean()] for s in ordered],float)
        ensure(per[:,0].sum()>0,"ZERO_BASELINE_SCORE_HOLD")
        endpoints[name]={"study_equal_gain":float(1-per[:,1].sum()/per[:,0].sum()),
           "heldout_study_groups_improving":int(np.sum(per[:,1]<per[:,0])),
           "heldout_study_groups_total":len(ordered),
           "model_base_study_equal_SSE":float(per[:,0].sum()),
           "model_plus_FD_study_equal_SSE":float(per[:,1].sum())}
        endpoints[name]["_per_group"]=per
    rng=np.random.default_rng(SEED)
    indices=rng.integers(0,len(ordered),size=(B,len(ordered)))
    boot={}
    for name,data in endpoints.items():
        per=data.pop("_per_group")
        sums=per[indices].sum(axis=1)
        ensure(np.all(sums[:,0]>0),"BOOTSTRAP_ZERO_BASELINE_HOLD")
        gg=1-sums[:,1]/sums[:,0]
        data["study_group_bootstrap_95CI"]=np.quantile(gg,[.025,.975]).tolist()
        boot[name]=gg
    diff=boot["CE"]-boot["SE"]
    result={"outcomes":endpoints,
        "primary_paired_FD_increment_CE_minus_SE":endpoints["CE"]["study_equal_gain"]-endpoints["SE"]["study_equal_gain"],
        "primary_paired_study_bootstrap_95CI":np.quantile(diff,[.025,.975]).tolist(),
        "bootstrap_unit":"original_StudyID_of_fixed_LOSO_error_vectors",
        "bootstrap_resamples":B,"seed":SEED,
        "no_new_causal_intervention_claim":True,
        "no_new_significance_p_values_computed":True}
    return result

def main(out,mode):
    result={"status":"ORIGINAL_SOURCE_PREMODEL_PENDING",
            "source_DOI":"10.6084/m9.figshare.27316062",
            "analysis_pre_outcome_freeze":SOURCE_FROZEN,
            "analysis_role":"RETROSPECTIVE_PUBLISHED_META_DATA_STUDY_HOLDOUT_PREDICTION",
            "author_published_FD_CE_SE_findings_known_before_design":True,
            "no_original_study_plot_or_species_names_exported":True,
            "no_original_biological_rows_exported":True,
            "no_phylogenetic_memory_causal_mediation_claim":True,
            "original_StudyID_not_verified_unique_paper_identity":True,
            "model_fitted":False,"cohorts":{}}
    try:
        for trait in ("leafN","SLA"):
            rows,groups,structure=assemble(trait)
            fold_info=folds_qualified(rows,groups)
            result["cohorts"][trait]={"source":structure,"fold_source_design":fold_info,
                         "source_admission":"SOURCE_AND_ALL_LOSO_TRAIN_FOLDS_PASS"}
            if mode=="fit":
                preds=model_predictions(rows,groups)
                score=summarise(rows,groups,preds)
                result["cohorts"][trait]["fixed_model_comparison"]=score
        result["status"]=("CHEN452_CE_SE_ORIGINAL_STUDY_SOURCE_QUALIFIED"
            if mode=="preflight" else "CHEN452_LEAFN_AND_SLA_FD_STUDY_HOLDOUT_COMPLETED")
        result["model_fitted"]=(mode=="fit")
    except (SourceHold,urllib.error.HTTPError,urllib.error.URLError,
            TimeoutError,OSError,ValueError,np.linalg.LinAlgError) as e:
        result["status"]="SOURCE_OR_FIXED_DESIGN_HOLD_NO_ADMISSIBLE_EFFECT_CLAIM"
        result["hold_type"]=type(e).__name__
        if isinstance(e,SourceHold):result["hold_code"]=str(e)[:100]
        if isinstance(e,urllib.error.HTTPError):result["source_HTTP"]=e.code
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("CHEN452_FIXED_STUDY_HOLDOUT_VERDICT",json.dumps({
        "status":result["status"],"model_fitted":result["model_fitted"],
        "hold_code":result.get("hold_code"),
        "cohort_counts":{k:{"n":v["source"]["paired_complete_case_mixture_rows"],
                             "studies":v["source"]["paired_complete_case_distinct_studies"],
                             "with5":v["source"]["distinct_studies_with_at_least_5_rows"]}
                         for k,v in result["cohorts"].items()},
        "primary_CE_gain":result.get("cohorts",{}).get("leafN",{}).get("fixed_model_comparison",{}).get("outcomes",{}).get("CE",{}).get("study_equal_gain"),
        "primary_SE_gain":result.get("cohorts",{}).get("leafN",{}).get("fixed_model_comparison",{}).get("outcomes",{}).get("SE",{}).get("study_equal_gain")
    },sort_keys=True))

def test():
    assert maybe_num("-99")==-99 and maybe_num("NA") is None
    assert math.log2(4)==2 and math.log1p(0)==0
    assert FILES["leafN"]["fd"]=="RaoQLN" and FILES["SLA"]["fd"]=="RaoQSLA"
    assert B==2000 and SEED==20261120 and TARGETS==["CE","SE","CE_minus_SE"]
    s=[{"rich":4,"age":1,"pd":.25,"cwm":2.,"MAT":16.,"AI":.7}]
    assert len(numeric(s[0]))==6
    print('{"status":"CHEN452_FIXED_DESIGN_SYNTHETIC_PASS","checks":7}')

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--mode",choices=("preflight","fit"),default="preflight")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.self_test:test()
    elif a.out:main(a.out,a.mode)
    else:p.error("Use --self-test or --out")
