#!/usr/bin/env python3
"""Frozen after source-only PASS: E141 August 2021 secondary SLA candidate FD.

A single retrospective experiment; no causal mediation or multi-site inference.
No original rows/species names/plot IDs or original numeric values are emitted.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import random
import urllib.error
import urllib.request
from pathlib import Path
import numpy as np

SOURCE="https://ndownloader.figshare.com/files/54836267"
SOURCE_MD5="8185b8effca37c8740ad065c53eb75d2"
TRAITS_BASE=("https://raw.githubusercontent.com/kaitkimmel/FDiv/"
 "e61c8814f3fc8e8fa7cac6141ee462c3e8b22554/data/Cleaned/")
PINS={
 ("Camb","Namb"):("cdrnaca_traitsout.csv","295d760e6cde3102a8e5b4ef325f6ea7d0a8372f"),
 ("Cenrich","Namb"):("cdrnace_traitsout.csv","f7fc222803afc40d5759ae5e650f82c9ce36cad9"),
 ("Camb","Nenrich"):("cdrneca_traitsout.csv","f7a0b4cd6e20fe1865d134a96c0a256a330a4918"),
 ("Cenrich","Nenrich"):("cdrnece_traitsout.csv","b94f2822a2ff066ce7933af4e075df3e20d845c2")}
MISSING_NATIVE_SLA={"Bouteloua gracilis","Poa pratensis"}
MISSING_STR={"","NA","NaN","nan","-9999","-9999.0"}
OUT=Path("results/biocon_e141_2021_secondary_sla_fd_B_NDE_composition_holdout_v0_1.json")
SEED=20261124
NBOOT=2000

def get(url,limit=4000000):
    r=urllib.request.Request(url,headers={"User-Agent":"turnover-biocon-e141-retrospective-2021/0.1"})
    with urllib.request.urlopen(r,timeout=40) as resp:
        blob=resp.read(limit+1)
    if len(blob)>limit:raise ValueError("Original archived source too large")
    return blob

def git_blob(blob):
    return hashlib.sha1(b"blob "+str(len(blob)).encode("ascii")+b"\x00"+blob).hexdigest()

def original_native_SLA():
    result={}
    for context,(file,sha) in PINS.items():
        blob=get(TRAITS_BASE+file,40000)
        if git_blob(blob)!=sha:raise ValueError("Author secondary SLA source blob changed")
        reader=csv.DictReader(io.StringIO(blob.decode("utf-8-sig"),newline=""))
        if not {"monospecies","CO2.Treatment","Nitrogen.Treatment","SLA"}.issubset(set(reader.fieldnames or [])):
            raise ValueError("Author treated SLA original schema invalid")
        table={}
        excluded=set()
        for r in reader:
            name=(r.get("monospecies") or "").strip().replace("."," ")
            if name in MISSING_NATIVE_SLA:
                excluded.add(name)
                continue
            if (r.get("CO2.Treatment"),r.get("Nitrogen.Treatment"))!=context:
                raise ValueError("Author treated original condition mismatch")
            if name in table or not name:raise ValueError("SLA source species duplicate/empty")
            sla=float(r["SLA"])
            if sla<=0 or not math.isfinite(sla):
                raise ValueError("Nonpositive originally processed native 14-candidate SLA")
            table[name]=math.log(sla)
        if len(table)!=14 or excluded!=MISSING_NATIVE_SLA:
            raise ValueError("Original author SLA native-source candidate count no longer 14")
        result[context]=table
    return result

def numeric_total(r):
    v=(r.get("AbovegroundTotal Biomass (g/m^2)") or "").strip()
    if v in MISSING_STR:raise ValueError("Earlier original biomass source presence changed")
    x=float(v)
    if not math.isfinite(x) or x<0:
        raise ValueError("Missing or physically negative original biomass for fixed cohort")
    return x

def prepare_rows():
    log_trait=original_native_SLA()
    blob=get(SOURCE)
    if hashlib.md5(blob).hexdigest()!=SOURCE_MD5:
        raise ValueError("Original 2025 Figshare E141 source MD5 mismatch")
    r=csv.DictReader(io.StringIO(blob.decode("utf-8-sig"),newline=""))
    h=list(r.fieldnames or [])
    if len(h)!=70:raise ValueError("Original 70 field source changed")
    cols=[x for x in h if x.endswith(" planted")]
    a=h.index("Monogroup")+1
    b=h.index("AbovegroundTotal Biomass (g/m^2)")
    full=[x.removesuffix(" (g/m^2)") for x in h[a:b]]
    if len(full)!=16 or len(cols)!=16:raise ValueError("Original 16-species source schema failed")
    pred=[x.split()[0][:3].casefold()+"."+x.split()[1][:3].casefold() for x in full]
    if pred!=[x.removesuffix(" planted").casefold() for x in cols]:
        raise ValueError("Original full species name to sown flag mapping changed")
    all_rows=[]
    monos=collections.defaultdict(list)
    used_ring_context=collections.defaultdict(set)
    for row in r:
        if (row.get("year") or "").strip()!="2021":
            continue
        def v(k):return (row.get(k) or "").strip()
        fs=[1 if v(col)=="1" else (0 if v(col)=="" else None) for col in cols]
        if any(x is None for x in fs) or sum(fs)!=int(v("CountOfSpecies")):
            raise ValueError("Original sown source flags failed 2021")
        if v("Experiment")!="M" or v("Season")!="August":
            continue
        ring,plot=v("Ring"),v("Plot")
        c,n=v("CO2 Treatment"),v("Nitrogen Treatment")
        used_ring_context[ring].add(c)
        ctx=(c,n)
        if sum(fs)==1:
            if v("AbovegroundTotal Biomass (g/m^2)") not in MISSING_STR:
                monos[(ctx,fs.index(1))].append(((ring,plot),row))
            continue
        if sum(fs) not in (4,9) or v("Water trt")!="0" or v("Temp trt")!="0":
            continue
        if v("AbovegroundTotal Biomass (g/m^2)") in MISSING_STR:
            continue
        native_vals=[log_trait[ctx][s] for s,f in zip(full,fs) if f and s in log_trait[ctx]]
        if len(native_vals)<2 or len(native_vals)/sum(fs)<0.8:
            continue
        all_rows.append({"id":(ring,plot),"co2":c,"n":n,"flags":tuple(fs),
            "rich":sum(fs),"CWM":sum(native_vals)/len(native_vals),
            "FD":sum(abs(x-y) for x in native_vals for y in native_vals)/(len(native_vals)**2),
            "source_row":row,"context":ctx})
    cnt=collections.Counter(p["rich"] for p in all_rows)
    comps={p["flags"] for p in all_rows}
    rings=sorted({p["id"][0] for p in all_rows})
    if len(all_rows)!=46 or cnt!={4:36,9:10} or len(comps)!=46 or len(rings)!=6:
        raise ValueError("Original frozen 2021 46 plot/36+10/46 composition/6 ring support changed")
    if any(len(used_ring_context[r])!=1 for r in rings):
        raise ValueError("Original ring-level CO2 allocation nonconstant")
    used_idx={i for p in all_rows for i,z in enumerate(p["flags"]) if z}
    used_ctx={(p["context"],i) for p in all_rows for i,z in enumerate(p["flags"]) if z}
    for k in used_ctx:
        if len(monos[k])!=2 or len({ident for ident,_ in monos[k]})!=2:
            raise ValueError("Expected 2 independent same-year August original monos missing")
    # Only now, AFTER numerical source gate checks, open the 46 source B and
    # original exact-context mono response cells. No other numeric responses.
    mono_numeric={}
    for k in used_ctx:
        mono_numeric[k]=[numeric_total(row) for _,row in sorted(monos[k],key=lambda p:p[0])]
    for p in all_rows:
        p["B"]=numeric_total(p.pop("source_row"))
        indices=[i for i,z in enumerate(p["flags"]) if z]
        e=[sum(mono_numeric[(p["context"],i)])/2 for i in indices]
        p["E"]=sum(e)/len(e)
        p["NDE"]=p["B"]-p["E"]
        p["NDE_mono1"]=p["B"]-sum(mono_numeric[(p["context"],i)][0] for i in indices)/len(indices)
        p["NDE_mono2"]=p["B"]-sum(mono_numeric[(p["context"],i)][1] for i in indices)/len(indices)
    return all_rows, rings

def matrix(rows,rings):
    first=rings[0]
    return np.asarray([
        [1.,float(p["rich"]==9),float(p["n"]=="Nenrich")]
        +[float(p["id"][0]==r) for r in rings if r!=first]
        +[p["CWM"],p["FD"]]
        for p in rows],dtype=float)

def crossval(rows,rings,response):
    rawX=matrix(rows,rings)
    y=np.asarray([p[response] for p in rows],dtype=float)
    original_comps=sorted({p["flags"] for p in rows})
    if len(original_comps)!=46 or rawX.shape!=(46,10):
        raise ValueError("Source original 46×10 geometry mismatch")
    pred0=np.full(len(rows),np.nan)
    pred1=np.full(len(rows),np.nan)
    for comp in original_comps:
        train=np.asarray([i for i,p in enumerate(rows) if p["flags"]!=comp])
        test=np.asarray([i for i,p in enumerate(rows) if p["flags"]==comp])
        if not len(test) or len(train)<35:
            raise ValueError("Invalid source original composition holdout")
        trainR=collections.Counter(rows[i]["id"][0] for i in train)
        if len(trainR)!=6:raise ValueError("Heldout fold missing original ring")
        Xtr=rawX[train].copy()
        Xte=rawX[test].copy()
        for col in (8,9):  # CWM and Rao-type FD, training-only standardization
            mu=float(Xtr[:,col].mean())
            sd=float(Xtr[:,col].std())
            if sd<1e-12:raise ValueError("Predictor constant in source fold")
            Xtr[:,col]=(Xtr[:,col]-mu)/sd
            Xte[:,col]=(Xte[:,col]-mu)/sd
        for p,X in ((9,Xtr[:,:-1]),(10,Xtr)):
            if np.linalg.matrix_rank(X)!=p:
                raise ValueError("Original frozen fold rank failure")
        w=np.asarray([1./trainR[rows[i]["id"][0]] for i in train])
        sqw=np.sqrt(w)
        for features,pred in ((9,pred0),(10,pred1)):
            design=Xtr[:,:features]
            coef=np.linalg.lstsq(design*sqw[:,None],y[train]*sqw,rcond=None)[0]
            pred[test]=Xte[:,:features]@coef
    if not all(np.isfinite(z).all() for z in (pred0,pred1)):
        raise ValueError("Source original heldout prediction not finite")
    return y-pred0,y-pred1

def ring_sse(rows,rings,errors0,errors1):
    # One equal-weight vote for each of six source original CO2 whole rings.
    out={}
    for r in rings:
        idx=[i for i,p in enumerate(rows) if p["id"][0]==r]
        if not idx:raise ValueError("Empty original CO2 ring under matched selection")
        a=float(np.mean(np.square(errors0[idx])))
        b=float(np.mean(np.square(errors1[idx])))
        out[r]=(a,b)
    return out

def gain(pairs):
    a=sum(x[0] for x in pairs)
    b=sum(x[1] for x in pairs)
    if not math.isfinite(a) or a<=0 or not math.isfinite(b):
        raise ValueError("Source baseline SSE invalid")
    return 1.-b/a

def quantile(sorted_arr,p):
    idx=(len(sorted_arr)-1)*p
    j=int(idx)
    k=min(j+1,len(sorted_arr)-1)
    return sorted_arr[j]*(1-(idx-j))+sorted_arr[k]*(idx-j)

def bootstrap(rings,ring_co2,rv_B,rv_N):
    rng=random.Random(SEED)
    source_groups={}
    for c in ("Camb","Cenrich"):
        source_groups[c]=sorted([r for r in rings if ring_co2[r]==c])
        if len(source_groups[c])!=3:
            raise ValueError("Not original 3+3 CO2 ring randomization")
    gsB,gsN,delta=[],[],[]
    for _ in range(NBOOT):
        selected=[]
        for c in ("Camb","Cenrich"):
            selected += rng.choices(source_groups[c],k=3)
        gb=gain([rv_B[r] for r in selected])
        gn=gain([rv_N[r] for r in selected])
        gsB.append(gb)
        gsN.append(gn)
        delta.append(gn-gb)
    return {name:{"95CI":[quantile(sorted(vals),0.025),quantile(sorted(vals),0.975)]}
            for name,vals in (("absolute_B",gsB),("signed_NDE",gsN),("NDE_minus_B",delta))}

def run():
    rows,rings=prepare_rows()
    co2={}
    for p in rows:
        r=p["id"][0]
        if r in co2 and co2[r]!=p["co2"]:
            raise ValueError("Original CO2 ring treatment not constant")
        co2[r]=p["co2"]
    eb0,eb1=crossval(rows,rings,"B")
    en0,en1=crossval(rows,rings,"NDE")
    B=ring_sse(rows,rings,eb0,eb1)
    N=ring_sse(rows,rings,en0,en1)
    gB,gN=gain(list(B.values())),gain(list(N.values()))
    mono_robust={}
    for k in ("NDE_mono1","NDE_mono2"):
        x0,x1=crossval(rows,rings,k)
        mono_robust[k]=gain(list(ring_sse(rows,rings,x0,x1).values()))
    uncertainty=bootstrap(rings,co2,B,N)
    return {
     "source_original_biocon_experiment":"BioCON E141 one field programme, 6 CO2 whole rings",
     "source_original_yield":"2021 August aboveground total g/m^2",
     "source_secondary_trait":"Ohlert 2024 author-processed monoculture SLA, 14 native E141-source candidate species, two E120-substituted taxa excluded",
     "source_year_upper_bound_from_PLoS_publication":"2020, NOT independently original EDI row dated",
     "published_original_EDI538_access_hold_unmodified":True,
     "retrospective_not_independent_confirmatory":True,
     "original_main_mixture_plot_units":len(rows),
     "original_sown_composition_folds":len({p["flags"] for p in rows}),
     "source_richness_counts":dict(collections.Counter(p["rich"] for p in rows)),
     "original_co2_whole_rings":len(rings),
     "model_source_baseline":"intercept+richness9+N+ring fixed 5 + 14-source-trait CWM",
     "model_source_plus_FD":"baseline+equal-planted-weight 1D candidate log-SLA Rao-type distance",
     "original_monoculture_E":"mean of 2 separate original 2021 August mono plots in exact CO2/N context, equally sown seed mass",
     "original_mixture_B_and_E_units":"g dry aboveground mass/m2",
     "predicted_heldout_composition_equal_ring_SSE_gains":{
       "absolute_B":gB,"signed_NDE":gN,"NDE_minus_B":gN-gB},
     "ring_stratified_fixed_OOF_error_bootstrap_draws":NBOOT,
     "fixed_OOF_ring_bootstrap_uncertainty_approximation":uncertainty,
     "monoculture_two_original_replicate_reference_sensitivity_NDE_gain":mono_robust,
     "source_ring_level_gains":{
       "B":{"positive_rings":sum(v[1]<v[0] for v in B.values()),"total_rings":6},
       "NDE":{"positive_rings":sum(v[1]<v[0] for v in N.values()),"total_rings":6}},
     "caveats":[
       "Retrospective secondary trait source after primary EDI 403; no original individual trait year verification",
       "One experiment and one year, not generalizing species diversity effects across biomes",
       "Original species composition selection determines FD; cannot identify FD-only causal intervention",
       "Only 6 CO2 rings; fixed-error ring bootstrap does not refit models or propagate all trait/mono uncertainty",
       "NDE is signed B-E, not the positive observed/expected ratio and not CE+SE independently reconstructed",
       "Source plant FD is based on native-candidate 14-species measured subset, not full 16 taxa"
     ],
     "source_original_row_values_or_taxon_labels_published":False,
     "original_numeric_source_rows_redistributed":False,
     "original_models_fitted":True
    }

def selftest():
    assert git_blob(b"abc")=="f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f"
    assert abs(gain([(1,0.5),(3,1.5)])-0.5)<1e-12
    assert len(matrix([{"rich":4,"n":"Namb","id":("1","1"),"CWM":1.0,"FD":0.5}], ["1","2","3","4","5","6"])[0])==10
    assert abs(quantile([0.,10.],0.25)-2.5)<1e-12
    print("SYNTHETIC_FROZEN_SECONDARY_CV_ARITHMETIC_PASS")

def main():
    out={"as_of_jst":"2026-11-24",
         "status":"SOURCE_OR_RANK_HOLD_NOT_A_NEGATIVE_BIOLOGICAL_FINDING",
         "original_EDI_538_HTTP403_HOLD_preserved":True,
         "analysis_type":"single-study retrospective secondary-SLA 2021 only"}
    try:
        out["results"]=run()
        out["status"]="RETROSPECTIVE_SECONDARY_2021_PREDICTION_COMPLETED_NO_CAUSAL_CLAIM"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
            ValueError,KeyError,TypeError,UnicodeError,csv.Error,
            np.linalg.LinAlgError,ZeroDivisionError) as exc:
        out["failure_class"]=type(exc).__name__
        if isinstance(exc,ValueError):
            out["source_stop_reason"]=str(exc)[:170]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if out["status"].startswith("RETROSPECTIVE"):
        # Never log original rows, source taxon values or source species labels
        d=out["results"]
        print(json.dumps({"status":out["status"],"sample_original_physical_plots":d["original_main_mixture_plot_units"],
             "heldout_original_composition_groups":d["original_sown_composition_folds"],
             "point_gains":d["predicted_heldout_composition_equal_ring_SSE_gains"],
             "ring_bootstrap_95CI":d["fixed_OOF_ring_bootstrap_uncertainty_approximation"],
             "mono_reference_sensitivity":d["monoculture_two_original_replicate_reference_sensitivity_NDE_gain"]}))
    else:
        print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--fit",action="store_true")
    args=p.parse_args()
    if args.selftest:selftest()
    elif args.fit:main()
    else:p.error("Choose --selftest or --fit")
