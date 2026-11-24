#!/usr/bin/env python3
"""BioCON E141 2021 source component accounting, not a model refit.

Source data: author Figshare 26841637 v3 MD5 verified. Audit original
2021 August fixed 46-mixture cohort and source-matched 128 monocultures.
Do not emit original observation values, plot IDs, species identities,
individual residuals, newly fitted FD coefficients or reconstructed yields.
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

FILE_ID=54836267
FILE_MD5="8185b8effca37c8740ad065c53eb75d2"
ORIGINAL_URL=f"https://ndownloader.figshare.com/files/{FILE_ID}"
README_ID=56055623
README_MD5="9ce824a94a0ad0ab455a9cfcc1589670"
AUTHORED_R_ID=54890864
AUTHORED_R_MD5="3166d7b1f8ee36e974812b3c7ac2cb48"
OUT=Path("results/biocon_e141_original_2021_biomass_components_accounting_v0_1.json")
MISSING={"","NA","NaN","nan","-9999","-9999.0"}
EXCLUDED_SLA={"Bouteloua gracilis","Poa pratensis"}
ABS_TOL_G_M2=0.001
REL_TOL=1.0e-5
ORIGINAL_MIXES=46
ORIGINAL_MONO_PLOTS=128

def get(url:str,limit:int=4_000_000)->bytes:
    r=urllib.request.Request(url,headers={"User-Agent":"turnover-biocon-mass-source-accounting/0.1"})
    with urllib.request.urlopen(r,timeout=40) as resp:
        data=resp.read(limit+1)
    if len(data)>limit:raise ValueError("original source byte limit exceeded")
    return data

def number(raw):
    s=(raw or "").strip()
    if s in MISSING:return None
    try:v=float(s)
    except ValueError:raise ValueError("Unexpected original numeric schema")
    if not math.isfinite(v) or v<0:raise ValueError("Original physical source mass invalid")
    return v

def near(a,b):
    return abs(a-b)<=ABS_TOL_G_M2+REL_TOL*max(1.0,abs(a),abs(b))

def distinct_plant_flags(row,columns):
    values=[]
    for c in columns:
        s=(row.get(c) or "").strip()
        if s=="1":values.append(1)
        elif s=="":values.append(0)
        else:raise ValueError("original sown flags unexpectedly changed")
    return tuple(values)

def group_counts(rows,full,cols):
    mono=collections.defaultdict(set)
    candidate=[]
    contexts=set()
    for row in rows:
        def f(k):return (row.get(k) or "").strip()
        if f("year")!="2021" or f("Season")!="August" or f("Experiment")!="M":
            continue
        flags=distinct_plant_flags(row,cols)
        richness=int(f("CountOfSpecies"))
        if sum(flags)!=richness:raise ValueError("sown flags and richness disagree")
        ctx=(f("CO2 Treatment"),f("Nitrogen Treatment"))
        physical=(f("Ring"),f("Plot"))
        contexts.add(ctx)
        if richness==1 and number(row.get("AbovegroundTotal Biomass (g/m^2)")) is not None:
            mono[(ctx,flags.index(1))].add(physical)
        if richness in (4,9) and f("Water trt")=="0" and f("Temp trt")=="0":
            if number(row.get("AbovegroundTotal Biomass (g/m^2)")) is None:
                continue
            covered=sum(flags[i] for i,s in enumerate(full) if s not in EXCLUDED_SLA)
            if covered<2 or covered/richness<0.80:
                continue
            candidate.append((physical,ctx,flags,row))
    accepted=[]
    for physical,ctx,flags,row in candidate:
        if all(len(mono[(ctx,i)])==2 for i,v in enumerate(flags) if v):
            accepted.append((physical,ctx,flags,row))
    dist_phys={x[0] for x in accepted}
    dist_comp={x[2] for x in accepted}
    dist_rings={x[0][0] for x in accepted}
    richness=collections.Counter(sum(x[2]) for x in accepted)
    if (len(accepted)!=ORIGINAL_MIXES or len(dist_phys)!=ORIGINAL_MIXES
        or len(dist_comp)!=ORIGINAL_MIXES or len(dist_rings)!=6
        or richness!={4:36,9:10}):
        raise ValueError("Original frozen E141 August2021 46 source-mixture cohort mismatch")
    mono_qual={}
    for ctx in contexts:
        for i in range(16):
            n=len(mono[(ctx,i)])
            if n!=2:raise ValueError("Original 64×2 mono source physical match changed")
            mono_qual[(ctx,i)]=mono[(ctx,i)]
    used_mono={p for key in mono_qual for p in mono_qual[key]}
    if len(used_mono)!=ORIGINAL_MONO_PLOTS:
        raise ValueError("Expected 128 physical source monoculture plots")
    monos=[]
    for row in rows:
        def f(k):return (row.get(k) or "").strip()
        if f("year")!="2021" or f("Season")!="August" or f("Experiment")!="M":
            continue
        flags=distinct_plant_flags(row,cols)
        physical=(f("Ring"),f("Plot"))
        if sum(flags)==1 and physical in used_mono:
            monos.append((physical,(f("CO2 Treatment"),f("Nitrogen Treatment")),flags,row))
    if len(monos)!=ORIGINAL_MONO_PLOTS:
        raise ValueError("Original mono source rows physical count failed")
    return accepted,monos

def audit_one(row,flags,source_cols):
    b=number(row.get("AbovegroundTotal Biomass (g/m^2)"))
    t=number(row.get("Total Biomass"))
    litter=number(row.get("Miscellaneous Litter (g/m^2)"))
    values=[number(row.get(c)) for c in source_cols]
    output={
        "all_species_16_numeric_present":all(v is not None for v in values),
        "no_species_numeric_reported":all(v is None for v in values),
        "number_of_planted_species_with_reported_mass":sum(flags[i] and values[i] is not None for i in range(16)),
        "number_of_nonplanted_species_with_nonzero_reported_mass":sum(not flags[i] and values[i] is not None and values[i]>ABS_TOL_G_M2 for i in range(16)),
        "number_of_planted_source_species":sum(flags),
        "source_B_present":b is not None,
        "source_Total_Biomass_present":t is not None,
        "source_Misc_Litter_present":litter is not None,
    }
    if b is not None and t is not None:
        output["B_equals_reported_Total_Biomass"]=near(b,t)
    if b is not None and t is not None and litter is not None:
        output["B_plus_litter_equals_reported_Total"]=near(b+litter,t)
        output["B_equals_reported_Total_plus_litter"]=near(b,t+litter)
    if b is not None and all(v is not None for v in values):
        output["B_equals_all_16_source_species_sum"]=near(b,sum(values))
    if b is not None and all(values[i] is not None for i,f in enumerate(flags) if f):
        planted=sum(values[i] for i in range(16) if flags[i])
        output["B_equals_only_originally_planted_species_sum"]=near(b,planted)
    return output

def summarize(records):
    ct=collections.Counter()
    h=collections.Counter()
    for row,flags in records:
        stats=audit_one(row,flags,source_cols=SOURCE_COLS)
        ct["source_records"]+=1
        for k,v in stats.items():
            if isinstance(v,bool):
                ct[k+"_checked_or_true" if v else k+"_false"]+=1
                if k in ("B_equals_all_16_source_species_sum",
                         "B_equals_only_originally_planted_species_sum",
                         "B_plus_litter_equals_reported_Total",
                         "B_equals_reported_Total_plus_litter",
                         "B_equals_reported_Total_Biomass"):
                    ct[k+"_auditable"]+=1
            elif isinstance(v,int) and k.startswith("number_of_"):
                h[(k,v)]+=1
    return {
      "counts":dict(sorted(ct.items())),
      "source_number_of_reported_species_cells_histograms":{
        k:[{"n":n,"source_plot_records":v} for (key,n),v in sorted(h.items()) if key==k]
        for k in sorted({x[0] for x in h})
      }
    }

def audit():
    raw=get(ORIGINAL_URL)
    if hashlib.md5(raw).hexdigest()!=FILE_MD5:
        raise ValueError("Original author CSV MD5 changed")
    rdr=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
    header=rdr.fieldnames or []
    cols=[c for c in header if c.endswith(" planted")]
    start=header.index("Monogroup")+1
    end=header.index("AbovegroundTotal Biomass (g/m^2)")
    source_cols=header[start:end]
    names=[x.removesuffix(" (g/m^2)") for x in source_cols]
    if len(cols)!=16 or len(source_cols)!=16:
        raise ValueError("Original 16 sown species/source mass header mapping changed")
    pred=[x.split()[0][:3].casefold()+"."+x.split()[1][:3].casefold() for x in names]
    if pred!=[x.removesuffix(" planted").casefold() for x in cols]:
        raise ValueError("Source species abbreviations do not map one-to-one")
    rows=list(rdr)
    accepted,monos=group_counts(rows,names,cols)
    global SOURCE_COLS
    SOURCE_COLS=source_cols
    r4=[(r,fl) for _,_,fl,r in accepted if sum(fl)==4]
    r9=[(r,fl) for _,_,fl,r in accepted if sum(fl)==9]
    source_monos=[(r,fl) for _,_,fl,r in monos]
    readme=get(f"https://ndownloader.figshare.com/files/{README_ID}",30000)
    original_r=get(f"https://ndownloader.figshare.com/files/{AUTHORED_R_ID}",60000)
    if hashlib.md5(readme).hexdigest()!=README_MD5 or hashlib.md5(original_r).hexdigest()!=AUTHORED_R_MD5:
        raise ValueError("Original author source README/R source MD5 changed")
    rt=readme.decode("utf-8-sig",errors="replace")
    code=original_r.decode("utf-8-sig",errors="replace")
    return {
      "source_data":"Huang et al 2025 BioCON E141 author Figshare 26841637.v3",
      "source_file_md5":FILE_MD5,
      "original_author_README_md5":README_MD5,
      "original_author_R_code_md5":AUTHORED_R_MD5,
      "source_original_mass_table_headers":{
        "original_aboveground_total":"AbovegroundTotal Biomass (g/m^2)",
        "alternate_source_total":"Total Biomass",
        "separate_litter":"Miscellaneous Litter (g/m^2)",
        "species_mass_column_count":len(source_cols)
      },
      "author_source_text_mentions":{
        "README_defines_aboveground_total":("AbovegroundTotal Biomass" in rt),
        "README_defines_misc_litter":("Miscellaneous Litter" in rt),
        "README_defines_alternate_total":("Total Biomass" in rt),
        "author_R_uses_aboveground_total":("AbovegroundTotal Biomass" in code or "AbovegroundTotal.Biomass" in code),
        "author_R_uses_alt_total":("Total Biomass" in code or "Total.Biomass" in code),
        "author_R_mentions_species_biomass_estimation":("estimate" in code.lower() or "predict" in code.lower()),
      },
      "cohort_source":"Original 2021 August, main 4/9 species, fixed earlier 46 plots",
      "original_mixture_4species":summarize(r4),
      "original_mixture_9species":summarize(r9),
      "original_mono_128_controls":summarize(source_monos),
      "audit_numeric_identity_abs_tolerance_g_m2":ABS_TOL_G_M2,
      "audit_numeric_identity_relative_tolerance":REL_TOL,
      "source_values_not_emitted":True,
      "original_plot_or_species_labels_not_emitted":True,
      "original_species_biomass_values_used_only_for_source_accounting":True,
      "no_FD_or_NDE_model_reestimated":True,
      "source_litter_not_automatically_classified_as_unsorted":True
    }

def test():
    assert near(10.,10.00001)
    assert not near(10.,11.)
    assert number("NA") is None and number("1.25")==1.25
    assert distinct_plant_flags({"A planted":"1","B planted":""},["A planted","B planted"])==(1,0)
    print("SYNTHETIC_ORIGINAL_BIOMASS_COMPONENT_IDENTITY_QA_PASS")

def main():
    out={"as_of_jst":"2026-11-24",
         "status":"SOURCE_BIOMASS_COMPONENT_ACCOUNTING_HOLD",
         "original_source_numeric_values_redistributed":False,
         "original_FD_NDE_models_refit":False}
    try:
        out["source_aggregate_identity"]=audit()
        out["status"]="ORIGINAL_BIOMASS_COMPONENT_IDENTITIES_AUDITED_NO_REFIT"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,
            UnicodeError,KeyError,TypeError,csv.Error) as exc:
        out["failure_class"]=type(exc).__name__
        if isinstance(exc,ValueError):out["source_error_reason"]=str(exc)[:200]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    a=p.parse_args()
    if a.selftest:test()
    elif a.source:main()
    else:p.error("choose --selftest or --source")
