#!/usr/bin/env python3
"""Original S5/S6 source adapter and fixed DivResource transfer analysis.

Actual source rows stay in ephemeral memory. Aggregate results only.
No observed-abundance-weighted FD predictors; S7 is not used.
"""
from __future__ import annotations
import argparse,collections,hashlib,importlib.util,itertools,json,math
from decimal import Decimal
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
S5_SHA="413fd1b856ce64385ea4935d8de1352e5fb5855d9c009e6a28de6c07dc516a53"
S6_SHA="6305db4081822e2b9105913be9b53526201f245fa40c32295d420198b1ae664b"
SP=("Arr_ela","Cen_jac","Ant_odo","Pla_lan","Dac_glo","Kna_arv","Lol_per","Pru_vul")
# Published field design: each original pool has one short/tall grass/forb.
# Independent confirmation by source monoculture FG/GS and pool labels required.
CLASSES={
 "Arr_ela":(1,1),"Cen_jac":(0,1),"Ant_odo":(1,0),"Pla_lan":(0,0),
 "Dac_glo":(1,1),"Kna_arv":(0,1),"Lol_per":(1,0),"Pru_vul":(0,0)
}
EXPECTED_POOLS={frozenset(SP[:4]),frozenset(SP[4:])}
H5=["Block","Plot","Mix","S","F","SR","Pool","FG","GS",*SP,"BM"]
H6=["Block","Plot","RYT","Dmax","NE","TICE","TDCE","DE"]
OUT=ROOT/"results/divresource_2013_pool_transfer_v0_1.json"

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    if spec is None or spec.loader is None:raise ValueError("required frozen module absent")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def source_records(module,raw,headers,n):
    all_rows=[]
    for t in module.tables(raw):
        if not t or t[0]!=headers:raise ValueError("original supplement table header changed")
        for row in t[1:]:
            if len(row)!=len(headers):raise ValueError("source table body row width changed")
            all_rows.append(dict(zip(headers,row)))
    if len(all_rows)!=n or len({r["Plot"] for r in all_rows})!=n:
        raise ValueError("original physical plot count or unique key changed")
    return all_rows

def decimal(v):
    q=Decimal(v.strip())
    if not q.is_finite():raise ValueError("nonfinite original source field")
    return q

def uncertainty(q):
    return Decimal("0.5")*(Decimal(10)**q.as_tuple().exponent)

def matched(a,b,tol):
    return abs(a-b)<=tol+Decimal("0.00000001")

def source_adapter():
    m=load("scripts/source/divresource_2013_original_schema.py","source_schema")
    a=m.get("s008");b=m.get("s009")
    if hashlib.sha256(a).hexdigest()!=S5_SHA or hashlib.sha256(b).hexdigest()!=S6_SHA:
        raise ValueError("published official DOCX source bytes changed")
    s5=source_records(m,a,H5,96)
    s6=source_records(m,b,H6,64)
    mono={}; mix_mapping={}; reverse={}
    taxon={}
    blocks=collections.defaultdict(set)
    rows=[]; source_mass={}
    all_component_identity=0
    for r in s5:
        if r["S"] not in ("0","1") or r["F"] not in ("0","1") or r["SR"] not in ("1","2","4"):
            raise ValueError("original treatment/richness code not verified")
        pool=r["Pool"]
        if pool not in ("A","B") or r["Block"] not in {f"B{i}" for i in range(1,9)}:
            raise ValueError("original source pool/block labels changed")
        # S5 uses numeric mass for the planted species and NA for absent columns.
        # Require this mask to reproduce the author's independent SR and Mix
        # assignment, all source pair cells, and independent Table 1 FG/GS.
        # Zero is a valid planted observation, never a removal criterion.
        ss=tuple(sorted(s for s in SP if r[s]!="NA"))
        if len(ss)!=int(r["SR"]):raise ValueError("source recorded mass-presence mask differs from sown richness")
        numeric={s:decimal(r[s]) for s in ss}
        total=decimal(r["BM"])
        if total<0 or any(v<0 for v in numeric.values()):
            raise ValueError("negative original physical biomass")
        tol=uncertainty(total)+sum(uncertainty(q) for q in numeric.values())
        if not matched(sum(numeric.values()),total,tol):
            raise ValueError("original species biomass sum not compatible with reported BM rounding")
        all_component_identity+=1
        original_mix_key=(pool,r["Mix"])
        if original_mix_key in mix_mapping and mix_mapping[original_mix_key]!=ss:
            raise ValueError("original Mix identity changes its planted species mask across treatments")
        mix_mapping[original_mix_key]=ss
        rev=(pool,ss)
        if rev in reverse and reverse[rev]!=r["Mix"]:raise ValueError("multiple Mix labels for same source composition")
        reverse[rev]=r["Mix"]
        classes=[CLASSES[s] for s in ss]
        g={q[0] for q in classes};h={q[1] for q in classes}
        # Source author FG G/F, homogeneous multispecies GG/FF, mixed GF;
        # source GS S/T and ST. Accept only original exact category semantics.
        expected_fg=("G" if g=={1} else "F") if len(ss)==1 else ("GG" if g=={1} else ("FF" if g=={0} else "GF"))
        expected_gs="S" if h=={0} else ("T" if h=={1} else "ST")
        if r["FG"]!=expected_fg or r["GS"]!=expected_gs:
            raise ValueError("source author's FG/GS assigned classification differs from published classes")
        if len(ss)==1:
            s=ss[0];new={"pool":pool,"grass":CLASSES[s][0],"tall":CLASSES[s][1]}
            if s in taxon and taxon[s]!=new:raise ValueError("mono taxonomy source not constant")
            taxon[s]=new
        treatment=f"F{'+' if r['F']=='1' else '-'}S{'+' if r['S']=='1' else '-'}"
        blocks[r["Block"]].add(r["S"])
        ctx=(pool,treatment,ss)
        source_mass.setdefault(ctx,[]).append(total)
        rows.append({"plot":r["Plot"],"pool":pool,"treatment":treatment,"species":list(ss),"B":float(total),
                     "block":r["Block"],"original_B_decimal":total})
    if len(taxon)!=8 or len(blocks)!=8 or any(len(v)!=1 for v in blocks.values()):
        raise ValueError("original pool or shade whole-block structure not matched")
    if sum(v=={"1"} for v in blocks.values())!=4:
        raise ValueError("expected original four shaded and four unshaded blocks")
    if {frozenset(s for s in taxon if taxon[s]["pool"]==p) for p in ("A","B")}!=EXPECTED_POOLS:
        raise ValueError("original mono source pool sets disagree with documented field design")
    if len(mix_mapping)!=22 or len(reverse)!=22:
        raise ValueError("original 22 distinct sown pool-composition identifiers not matched")
    keyed6={r["Plot"]:r for r in s6}
    actual_mixture_ids={r["plot"] for r in rows if len(r["species"])>1}
    if set(keyed6)!=actual_mixture_ids:raise ValueError("S5 and S6 do not match exact original 64 mixture keys")
    ne_valid=triplet_valid=0
    for r in rows:
        if len(r["species"])==1:continue
        q=keyed6[r["plot"]]
        if q["Block"]!=r["block"]:raise ValueError("source S5/S6 physical block mismatch")
        s=len(r["species"]);ctx=(r["pool"],r["treatment"])
        orig=[]
        for name in r["species"]:
            vals=source_mass[ctx+((name,),)]
            if len(vals)!=1:raise ValueError("one original treatment matched mono per species required")
            orig.append(vals[0])
        B=r["original_B_decimal"]
        E=sum(orig)/s
        NE=decimal(q["NE"])
        tol=uncertainty(B)+sum(uncertainty(x) for x in orig)/s+uncertainty(NE)
        if not matched(B-E,NE,tol):
            raise ValueError("computed signed B-E not compatible with author S6 NE precision")
        ne_valid+=1
        parts=[decimal(q[k]) for k in ("TICE","TDCE","DE")]
        if not matched(sum(parts),NE,sum(uncertainty(x) for x in parts)+uncertainty(NE)):
            raise ValueError("author S6 tripartite source components do not sum to NE at printed precision")
        triplet_valid+=1
    if ne_valid!=64 or triplet_valid!=64:raise ValueError("64 original source mixture accounting gate incomplete")
    # Output only verified design and numeric aggregate results. No source rows.
    source_summary={"original_S5_sha256":S5_SHA,"original_S6_sha256":S6_SHA,
       "source_S5_physical_plots":96,"source_S6_mixture_records":64,
       "original_species_sum_matches_BM_at_printed_precision":all_component_identity,
       "source_distinct_Mix_within_pool_keys":22,"source_matched_author_NE":ne_valid,
       "source_NE_equals_TICE_plus_TDCE_plus_DE":triplet_valid,
       "original_full_physical_shade_blocks":8,"shaded_blocks":4,
       "source_species_pools_disjoint":True,
       "source_mono_species_treatment_replicates":1}
    core=load("scripts/analysis/divresource_2013_pool_transfer_core.py","frozen_core")
    return source_summary,core.evaluate(rows,taxon)

def main():
    out={"date":"2026-11-26","status":"SOURCE_OR_MODEL_HOLD",
         "field_programme":"DivResource 2013 Bad Lauchstadt",
         "doi":"10.1371/journal.pone.0158110","independent_of_other_meta_analysis_source_ids_verified":False,
         "raw_source_rows_released":False}
    try:
        audit,effect=source_adapter()
        out["source_audit"]=audit;out["results"]=effect
        out["status"]="COMPLETE_EXPLORATORY_TWO_POOL_TRANSFER"
    except Exception as exc:
        # Only validation messages, not row values or raw source observations.
        out["failure_class"]=type(exc).__name__
        out["failure_reason"]=str(exc)[:180] if isinstance(exc,ValueError) else "original source access/parser or numeric gate"
    OUT.parent.mkdir(exist_ok=True,parents=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":main()
