#!/usr/bin/env python3
"""Frozen 2-pool functional-contrast transfer engine; no source ingestion guesses.

Only a separately source-qualified normalized S5 table can be used.
No original individual observations are printed or committed.
"""
from __future__ import annotations
import argparse, collections, itertools, json, math
from pathlib import Path
import numpy as np

TREATMENTS=("F-S-","F-S+","F+S-","F+S+")
# Normalize original author Table 1 design ONLY after independent source check.
# Every pool must have one species in each of four guild x stature classes.
REQUIRED_CLASSES={(0,0),(0,1),(1,0),(1,1)}

def qualify(rows, taxon):
    """taxon: {source species label: {'pool': original pool, 'grass':0/1,'tall':0/1}}.
    rows: exactly source 96 physical plots, annual live sown-species biomass B.
    Each record has unique plot, pool, treatment, planted species and B.
    Input adapter must independently qualify exact author identifiers, units, and source.
    """
    pools=sorted({x["pool"] for x in taxon.values()})
    if len(taxon)!=8 or len(pools)!=2:raise ValueError("expected two disjoint original four-species pools")
    bypool={p:{s for s,v in taxon.items() if v["pool"]==p} for p in pools}
    for p,ss in bypool.items():
        classes={(taxon[s]["grass"],taxon[s]["tall"]) for s in ss}
        if len(ss)!=4 or classes!=REQUIRED_CLASSES:raise ValueError("unqualified original species-pool classes")
    if len(rows)!=96 or len({x["plot"] for x in rows})!=96:
        raise ValueError("exact 96 physical source plots required")
    cells=collections.defaultdict(list)
    for x in rows:
        p=x["pool"];t=x["treatment"];ss=tuple(sorted(x["species"]))
        b=float(x["B"])
        if p not in pools or t not in TREATMENTS or len(ss) not in (1,2,4) or len(set(ss))!=len(ss):
            raise ValueError("invalid original source pool/treatment/species combination")
        if not set(ss).issubset(bypool[p]) or not math.isfinite(b) or b<0:
            raise ValueError("invalid source planted taxa or physical biomass")
        cells[(p,t,ss)].append(b)
    out=[]
    for p in pools:
        for t in TREATMENTS:
            species=sorted(bypool[p])
            for s in species:
                if len(cells[(p,t,(s,))])!=1:raise ValueError("one original mono per species/treatment required")
            if len(cells[(p,t,tuple(species))])!=2:
                raise ValueError("exact two originally designed four-species mixtures per context required")
            for a,b in itertools.combinations(species,2):
                key=(p,t,(a,b))
                if len(cells[key])!=1:raise ValueError("expected exactly one original pair per resource context")
                gm=(taxon[a]["grass"]+taxon[b]["grass"])/2
                hm=(taxon[a]["tall"]+taxon[b]["tall"])/2
                d=(abs(taxon[a]["grass"]-taxon[b]["grass"])+abs(taxon[a]["tall"]-taxon[b]["tall"]))/2
                if abs(d-(4*gm*(1-gm)+4*hm*(1-hm))/2)>1e-12:
                    raise ValueError("source binary contrast arithmetic failed")
                B=cells[key][0]
                E=(cells[(p,t,(a,))][0]+cells[(p,t,(b,))][0])/2
                out.append({"pool":p,"X":[1.,*(float(t==u) for u in TREATMENTS[1:]),gm,hm,d],
                            "B":B,"NDE":B-E})
    if len(out)!=48:raise ValueError("fixed 48-pair cohort failed")
    return out,pools

def evaluate(rows,taxon):
    rr,pools=qualify(rows,taxon)
    X=np.asarray([r["X"] for r in rr],dtype=float)
    g={}
    for endpoint in ("B","NDE"):
        y=np.asarray([r[endpoint] for r in rr],dtype=float)
        fold=[]
        for train_pool in pools:
            train=np.asarray([r["pool"]==train_pool for r in rr]);test=~train
            if train.sum()!=24 or test.sum()!=24:
                raise ValueError("not the frozen balanced original two-pool comparison")
            sse=[]
            for k in (6,7):
                a=X[train,:k]
                if np.linalg.matrix_rank(a)!=k:raise ValueError("fixed model rank HOLD")
                coef=np.linalg.lstsq(a,y[train],rcond=None)[0]
                error=y[test]-X[test,:k]@coef
                sse.append(float(np.sum(error**2)))
            if sse[0]<=1e-12:raise ValueError("baseline SSE zero/invalid; effect HOLD")
            fold.append({"train_pool":str(train_pool),"test_pool":str(next(p for p in pools if p!=train_pool)),
                         "n":24,"SSE_baseline":sse[0],"SSE_plus_D":sse[1],"gain":1-sse[1]/sse[0]})
        g[endpoint]={"both_directions":fold,
                     "pool_equal_gain":1-sum(x["SSE_plus_D"] for x in fold)/sum(x["SSE_baseline"] for x in fold)}
    return {"original_field_programmes":1,"disjoint_species_pools":2,"mixture_plots":48,
            "same_source_rows_and_folds":True,
            "endpoint_results":g,"NDE_minus_B_gain":g["NDE"]["pool_equal_gain"]-g["B"]["pool_equal_gain"],
            "population_CI_reported":False,"causal_FD_only_estimated":False,
            "mono_uncertainty":"one physical source monoculture per species x resource treatment, not resampled",
            "D_interpretation":"fixed nonlinear contrast of planted binary trait means, not independent FD intervention"}

def selftest():
    tx={}
    rows=[]
    for p in (1,2):
        ss=[]
        for i,(g,h) in enumerate(sorted(REQUIRED_CLASSES)):
            s=f"fake{p}_{i}"
            tx[s]={"pool":p,"grass":g,"tall":h}
            ss.append(s)
        for j,t in enumerate(TREATMENTS):
            for n in (1,2,4):
                for combo in itertools.combinations(ss,n):
                    for rep in range(2 if n==4 else 1):
                        means=[50+10*tx[s]["grass"]+8*tx[s]["tall"]+j*2 for s in combo]
                        b=float(sum(means)/n)
                        if n==2:
                            d=(abs(tx[combo[0]]["grass"]-tx[combo[1]]["grass"])+abs(tx[combo[0]]["tall"]-tx[combo[1]]["tall"]))/2
                            b+=12*d
                        rows.append({"plot":f"SYNTHETIC_{len(rows)}","pool":p,"treatment":t,"species":list(combo),"B":b})
    result=evaluate(rows,tx)
    for k in ("B","NDE"):
        assert abs(result["endpoint_results"][k]["pool_equal_gain"]-1)<1e-10
    assert abs(result["NDE_minus_B_gain"])<1e-10
    assert len(rows)==96
    try:qualify(rows[:-1],tx)
    except ValueError:pass
    else:raise AssertionError("missing original physical plot guard failed")
    print("SYNTHETIC_ONLY: exact 96 source design, 48 paired rows, 24 per holdout, known D signal, missing-row guard PASS")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--qualified-json",type=Path)
    a=p.parse_args()
    if a.selftest:selftest()
    elif a.qualified_json:
        j=json.loads(a.qualified_json.read_text(encoding="utf-8"))
        # No original file schema is guessed; only separately verified source adapter input.
        assert j["source_adapter_verified"] is True
        assert j["source_doi"]=="10.1371/journal.pone.0158110.s008"
        assert j["source_sha256"] and len(j["source_sha256"])==64
        print(json.dumps(evaluate(j["rows"],j["taxon"]),ensure_ascii=False))
    else:p.error("use --selftest or separately source-qualified input")
