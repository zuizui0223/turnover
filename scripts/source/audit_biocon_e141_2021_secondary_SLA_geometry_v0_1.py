#!/usr/bin/env python3
"""BioCON original 2021 secondary-SLA design matrix geometry before outcomes.

Read original treated author SLA values for 14 source-candidate species; read
only ORIGINAL B presence, never original numeric biomass/mono response values.
Fail close before entering the separately frozen biological effect model.
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

ORIGINAL_CSV="https://ndownloader.figshare.com/files/54836267"
SOURCE_MD5="8185b8effca37c8740ad065c53eb75d2"
ROOT=("https://raw.githubusercontent.com/kaitkimmel/FDiv/"
      "e61c8814f3fc8e8fa7cac6141ee462c3e8b22554/data/Cleaned/")
PINS={
 ("Camb","Namb"):("cdrnaca_traitsout.csv","295d760e6cde3102a8e5b4ef325f6ea7d0a8372f"),
 ("Cenrich","Namb"):("cdrnace_traitsout.csv","f7fc222803afc40d5759ae5e650f82c9ce36cad9"),
 ("Camb","Nenrich"):("cdrneca_traitsout.csv","f7a0b4cd6e20fe1865d134a96c0a256a330a4918"),
 ("Cenrich","Nenrich"):("cdrnece_traitsout.csv","b94f2822a2ff066ce7933af4e075df3e20d845c2")
}
EXCLUDED={"Bouteloua gracilis","Poa pratensis"}
OUT=Path("results/biocon_e141_2021_secondary_sla_source_geometry_20261124_v0_1.json")
MISSING={"","NA","NaN","nan","-9999","-9999.0"}

def get(url,limit=4000000):
    req=urllib.request.Request(url,headers={"User-Agent":"turnover-e141-secondary-SLA-geometry/0.1"})
    with urllib.request.urlopen(req,timeout=40) as res:
        raw=res.read(limit+1)
    if len(raw)>limit:raise ValueError("official source exceeds bytes cap")
    return raw

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\x00"+raw).hexdigest()

def source_traits():
    out={}
    for (c,n),(filename,sha) in PINS.items():
        raw=get(ROOT+filename,40000)
        if git_blob(raw)!=sha:raise ValueError("published author trait CSV blob not original pinned source")
        f=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
        if not {"monospecies","SLA","CO2.Treatment","Nitrogen.Treatment"}.issubset(set(f.fieldnames or [])):
            raise ValueError("source author SLA treated schema changed")
        trait={}
        skipped=set()
        for row in f:
            name=(row.get("monospecies") or "").strip().replace("."," ")
            if name in EXCLUDED:
                skipped.add(name)
                continue # do not inspect any substituted numeric value
            if not name or name in trait:raise ValueError("source direct candidate taxon duplication")
            if row.get("CO2.Treatment")!=c or row.get("Nitrogen.Treatment")!=n:
                raise ValueError("author treated source environment mismatch")
            sla=float(row["SLA"])
            if not math.isfinite(sla) or sla<=0:raise ValueError("nonpositive original 14-candidate SLA")
            trait[name]=math.log(sla)
        if len(trait)!=14 or skipped!=EXCLUDED:
            raise ValueError("native source candidates not exactly 14 without 2 substitutes")
        out[(c,n)]=trait
    return out

def inspect():
    traits=source_traits()
    raw=get(ORIGINAL_CSV)
    if hashlib.md5(raw).hexdigest()!=SOURCE_MD5:
        raise ValueError("original BioCON Figshare byte MD5 mismatch")
    f=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
    h=list(f.fieldnames or [])
    if len(h)!=70:raise ValueError("source original 70 header contract mismatch")
    plant_cols=[z for z in h if z.endswith(" planted")]
    sp_start=h.index("Monogroup")+1
    sp_end=h.index("AbovegroundTotal Biomass (g/m^2)")
    full=[z.removesuffix(" (g/m^2)") for z in h[sp_start:sp_end]]
    if len(full)!=16 or len(plant_cols)!=16:
        raise ValueError("original exact 16 source taxa/flag crosswalk failed")
    predicted=[s.split()[0][:3].casefold()+"."+s.split()[1][:3].casefold() for s in full]
    if predicted!=[z.removesuffix(" planted").casefold() for z in plant_cols]:
        raise ValueError("original crosswalk not unique")
    mono=collections.defaultdict(set)
    mixes=[]
    for row in f:
        if (row.get("year") or "").strip()!="2021":continue
        def v(k):return (row.get(k) or "").strip()
        fl=[1 if v(x)=="1" else (0 if v(x)=="" else None) for x in plant_cols]
        if any(x is None for x in fl) or sum(fl)!=int(v("CountOfSpecies")):
            raise ValueError("original row planted code invalid")
        c,n=v("CO2 Treatment"),v("Nitrogen Treatment")
        context=(v("Season"),c,n)
        physical=(v("Ring"),v("Plot"))
        present=v("AbovegroundTotal Biomass (g/m^2)") not in MISSING
        if v("Experiment")=="M" and sum(fl)==1 and present:
            mono[context+(fl.index(1),)].add(physical)
        if v("Experiment")=="M" and sum(fl) in (4,9) and v("Water trt")=="0" and v("Temp trt")=="0" and present:
            mixes.append((physical,context,tuple(fl)))
    result=[]
    for physical,(season,c,n),fl in mixes:
        if not all(len(mono[(season,c,n,i)])==2 for i,x in enumerate(fl) if x):
            continue
        sl=[traits[(c,n)][s] for s,x in zip(full,fl) if x and s in traits[(c,n)]]
        if len(sl)<2 or len(sl)/sum(fl)<0.8:
            continue
        cwm=sum(sl)/len(sl)
        fd=sum(abs(a-b) for a in sl for b in sl)/(len(sl)**2)
        result.append({"ring":physical[0],"rich":sum(fl),"n":n,
                       "composition":fl,"cwm":cwm,"FD":fd})
    byrich=collections.Counter(x["rich"] for x in result)
    composition_groups={x["composition"] for x in result}
    rings=sorted({x["ring"] for x in result})
    if len(result)!=46 or byrich!={4:36,9:10} or len(composition_groups)!=46 or len(rings)!=6:
        raise ValueError("frozen original 2021 cohort 46/36/10/46 groups/6 rings failed")
    ring_base=rings[0]
    xs=[]
    for x in result:
        xs.append([1.,float(x["rich"]==9),float(x["n"]=="Nenrich")]
                  +[float(x["ring"]==r) for r in rings if r!=ring_base]
                  +[x["cwm"],x["FD"]])
    X=np.asarray(xs,dtype=float)
    n_fail=0
    for group in composition_groups:
        idx=[i for i,p in enumerate(result) if p["composition"]!=group]
        a=X[idx,:-1];b=X[idx,:]
        if (len(idx)<35 or np.linalg.matrix_rank(a)!=a.shape[1]
            or np.linalg.matrix_rank(b)!=b.shape[1]):
            n_fail+=1
    can_pass=n_fail==0 and np.std(X[:,-1])>1e-9 and np.std(X[:,-2])>1e-9
    return {
     "source_author_table_git_blob_shas_verified":True,
     "source_first_trait_numeric_values_used_only_for_geometry":True,
     "source_original_biomass_numeric_values_opened":False,
     "source_original_plant_composition_count":len(result),
     "source_original_plots_by_richness":dict(byrich),
     "whole_CO2_ring_count":len(rings),
     "source_candidate_full_14_direct_code_inferred_SLA_treatment_cells":56,
     "source_distinct_composition_holdout_groups":len(composition_groups),
     "M0_parameter_count":X.shape[1]-1,
     "M1_parameter_count":X.shape[1],
     "source_training_matrix_rank_failures_across_all_46_holdout_compositions":n_fail,
     "CWM_variation_present":bool(np.std(X[:,-2])>1e-9),
     "FD_variation_present":bool(np.std(X[:,-1])>1e-9),
     "design_only_source_geometry_pass":bool(can_pass),
     "original_EDI_538_trait_observation_years_verified":False,
     "new_biomass_FD_effect_models_fit":0
    }

def selftest():
    assert git_blob(b"abc")=="f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f"
    test=np.array([[1.,0.,1.],[1.,1.,0.],[1.,1.,1.]])
    assert np.linalg.matrix_rank(test)==3
    print("SYNTHETIC_SOURCE_PREDICTOR_GEOMETRY_PASS")

def main():
    out={"as_of_jst":"2026-11-24","status":"SOURCE_TRAIT_OR_MODEL_GEOMETRY_HOLD",
         "source_analysis_mode":"post-original-EDI403 secondary-derived retrospective-only",
         "original_biomass_numeric_values_opened":False,
         "biological_effect_models_fitted":0}
    try:
        out["source_geometry"]=inspect()
        out["status"]=("SECONDARY_SLA_FIXED_MODEL_GEOMETRY_PASS_OUTCOME_NOT_YET_OPENED"
                      if out["source_geometry"]["design_only_source_geometry_pass"]
                      else "SOURCE_MODEL_GEOMETRY_RANK_HOLD")
    except (urllib.error.HTTPError,urllib.error.URLError,UnicodeError,
            ValueError,KeyError,TypeError,StopIteration,TimeoutError,csv.Error) as exc:
        out["failure_class"]=type(exc).__name__
        if isinstance(exc,ValueError):out["source_stop_reason"]=str(exc)[:170]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    a=p.parse_args()
    if a.selftest:selftest()
    elif a.source:main()
    else:p.error("choose --selftest or --source")
