#!/usr/bin/env python3
"""Source-pinned, exploratory BIODEPTH S3 phylogenetic breadth → FD/biomass.

Analysis design frozen in docs/BIODEPTH_MATCHED_PD_FD_BIOMASS_SITE_HOLDOUT_DESIGN_V0_1.md
before this new matched phylogenetic predictor-response was opened.
No BIEN family-specific rho/Blomberg K; no causal inference.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
import numpy as np

from audit_biodepth_103_taxa_gift_height_v0_1 import source,geometry
from audit_biodepth_gift_height_references_v0_1 import run as provenance
from fit_biodepth_2010_sown_height_fd_biomass_v0_1 import (
    composition,baseline,fit_predict
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
from audit_biodepth_gift_gbotb_joint_support_v0_1 import read_tree
from test_biodepth_height_label_guild_null_v0_1 import published_design

SEED=20261116
REPS=10000
ORIGANUM="origanum vulgare"
ORIGINAL_SITES={"Germany":26,"Ireland":26,"Portugal":8,"Sheffield":20,"Silwood":24,"Sweden":18,"Switzerland":28}


def qualify_original_plots(roster:dict,height:dict,status:dict,dist:dict,plan:dict,only_native=False):
    keep=set(dist)
    if only_native:
        keep &= {sp for sp,rec in status.items() if rec["status"]=="prune"}
    plot_data={}
    original_height_plots=set()
    for (site,plot),sown in sorted(roster.items()):
        included=set(sown)&set(height)
        if len(included)<3 or len(included)/len(sown)<.8:continue
        original_height_plots.add((site,plot))
        both=sorted(included&keep)
        if len(both)<3 or len(both)/len(sown)<.8:continue
        planrow=plan[plot]
        if planrow["location"]!=site or int(planrow["species.richness"])!=len(sown):
            raise ValueError("SOURCE_HOLD: original planted Design changed")
        h=np.log(np.array([height[s] for s in both],dtype=float))
        if not np.isfinite(h).all():raise ValueError("SOURCE_HOLD: invalid log height")
        n=len(both)
        meanpair_height=float(np.abs(h[:,None]-h[None,:]).sum()/(n*(n-1)))
        phylo_pairs=np.asarray([dist[a][b] for i,a in enumerate(both) for b in both[i+1:]],dtype=float)
        pd=float(phylo_pairs.mean())
        if not np.isfinite(pd) or pd<=0:
            raise ValueError("SOURCE_HOLD: invalid tree MPD for original planting")
        plot_data[(site,plot)]={
            "site":site,"plot":plot,"richness":len(sown),
            "grass":int(planrow["grasses"]=="Yes"),
            "forbs":int(planrow["forbs"]=="Yes"),
            "legumes":int(planrow["legumes"]=="Yes"),
            "source_sown_species":len(sown),"source_joint_species":n,
            "cwm":float(h.mean()),"mpd":meanpair_height,"pd":pd,
        }
    return plot_data,original_height_plots


def source_checks(args):
    previous=json.loads(Path(args.provenance).read_text(encoding="utf8"))
    tree_prior=json.loads(Path(args.phylogeny_gate).read_text(encoding="utf8"))
    joint_prior=json.loads(Path(args.joint_gate).read_text(encoding="utf8"))
    if (previous["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS" or
        tree_prior["status"]!="BIODEPTH_GBOTB_S3_SOURCE_COVERAGE_PASS" or
        joint_prior["status"]!="BIODEPTH_GBOTB_GIFT_JOINT_SUPPORT_PASS" or
        joint_prior["joint_original_plots_min3_and_80pct"]!=150 or
        joint_prior["joint_height_phylogeny_species"]!=84 or
        joint_prior["joint_height_phylogeny_native_taxa"]!=78):
        raise ValueError("SOURCE_HOLD: previously frozen 88/98/84 source qualifications missing")
    srows=source(args.species,"species")
    crows=source(args.codes,"codes")
    named,roster,source_meta=geometry(srows,crows)
    current,height0=provenance(srows,crows,return_values=True)
    if (current["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS" or
        current["GIFT_original_target_species_height_and_reference_fingerprint_sha256"]!=
        previous["GIFT_original_target_species_height_and_reference_fingerprint_sha256"] or
        current["GIFT_bibliography_content_sha256"]!=previous["GIFT_bibliography_content_sha256"]):
        raise ValueError("SOURCE_HOLD: original GIFT source/provenance fingerprint drift")
    if len(height0)!=88 or height0.get(ORIGANUM)!=13:
        raise ValueError("SOURCE_HOLD: historical raw GIFT Origanum value/source changed")
    height=dict(height0)
    height[ORIGANUM]=.9
    plan=published_design(args.design)
    status,D=read_tree(Path(args.tree_crosswalk),Path(args.tree_distances))
    if len(status)!=98 or len(D)!=98 or len(set(height)&set(D))!=84:
        raise ValueError("SOURCE_HOLD: source-matched 84 taxa cannot be reproduced")
    plots,orig_plots=qualify_original_plots(roster,height,status,D,plan)
    group=dict(Counter(site for site,plot in plots))
    if (len(orig_plots)!=174 or len(plots)!=150 or
        group!=ORIGINAL_SITES or
        len({status[s]["family"] for s in set(height)&set(D)})!=17):
        raise ValueError("SOURCE_HOLD: original 150/174 plot/taxon cohort differs from source-only gate")
    native_plots,_=qualify_original_plots(roster,height,status,D,plan,only_native=True)
    native_counts=dict(Counter(site for site,plot in native_plots))
    # Check all M3 source-only training designs BEFORE reading biomass.
    for held in sorted(group):
        fake=[{**p,"year":year,"response":0.}
              for p in plots.values() for year in (1,2,3) if p["site"]!=held]
        x,_,_=baseline(fake,include_mean=True,include_disp=True)
        pds=np.asarray([r["pd"] for r in fake],float)
        if not np.isfinite(pds).all() or np.std(pds)<1e-9:
            raise ValueError("SOURCE_HOLD: no training phylogenetic distance variation")
        design=np.column_stack([x,(pds-pds.mean())/pds.std(ddof=0)])
        if np.linalg.matrix_rank(design)!=design.shape[1]:
            raise ValueError("SOURCE_HOLD: PD addition rank deficient in pre-response site fold "+held)
    print("PRE_BIOMASS_MATCHED_SOURCE_GATE_PASS",json.dumps({
        "original_source_sites":group,"original_plots":len(plots),"original_height_plots":len(orig_plots),
        "native_only_plots":len(native_plots),"native_only_sites":native_counts,
        "joint_height_tree_taxa":84},sort_keys=True),flush=True)
    return srows,crows,plots,native_plots,height,current


def score_sites(cells:list,sites:list,method="mass"):
    scores=[]
    for held in sites:
        train=[r for r in cells if r["site"]!=held]
        test=[r for r in cells if r["site"]==held]
        if not train or not test:raise ValueError("MODEL_HOLD: empty source site")
        if method=="mass":
            # Parent source-native M2 exactly determines 8 historical context +
            # training-only mean and FD coefficients.
            p0=fit_predict(train,test,2)
            xx,mu,sd=baseline(train,include_mean=True,include_disp=True)
            xt,_,_=baseline(test,include_mean=True,include_disp=True,mu=mu,sd=sd)
            pdtrain=np.asarray([r["pd"] for r in train],float)
            pdtest=np.asarray([r["pd"] for r in test],float)
            scale=pdtrain.std(ddof=0)
            if scale<=1e-9:raise ValueError("MODEL_HOLD: zero training PD scale")
            x3=np.column_stack([xx,(pdtrain-pdtrain.mean())/scale])
            xt3=np.column_stack([xt,(pdtest-pdtrain.mean())/scale])
            if np.linalg.matrix_rank(x3)!=x3.shape[1]:
                raise ValueError("MODEL_HOLD: full design not estimable in "+held)
            y=np.asarray([r["response"] for r in test],float)
            p1=xt3 @ np.linalg.lstsq(x3,np.asarray([r["response"] for r in train],float),rcond=None)[0]
        elif method=="fd":
            def fmatrix(rows,mean=None,scale=None,with_pd=False):
                z=np.log2([r["richness"] for r in rows])
                base=np.column_stack([np.ones(len(rows)),z,z*z,
                    [r["grass"] for r in rows],[r["forbs"] for r in rows],
                    [r["legumes"] for r in rows]])
                values=np.array([[r["cwm"],r["pd"]] for r in rows],float)
                if mean is None:
                    mean=values.mean(axis=0);scale=values.std(axis=0,ddof=0)
                if np.any(scale<=1e-9):raise ValueError("MODEL_HOLD: FD feature source standardization zero")
                values=(values-mean)/scale
                cols=np.column_stack([base,values]) if with_pd else np.column_stack([base,values[:,0]])
                return cols,mean,scale
            xb,mu,sd=fmatrix(train)
            xtb,_,_=fmatrix(test,mu,sd)
            xf,_,_=fmatrix(train,mu,sd,with_pd=True)
            xtf,_,_=fmatrix(test,mu,sd,with_pd=True)
            if np.linalg.matrix_rank(xb)!=xb.shape[1] or np.linalg.matrix_rank(xf)!=xf.shape[1]:
                raise ValueError("MODEL_HOLD: PD→FD planted community source rank deficiency")
            y0=np.array([r["mpd"] for r in train],float)
            y=np.array([r["mpd"] for r in test],float)
            p0=xtb@np.linalg.lstsq(xb,y0,rcond=None)[0]
            p1=xtf@np.linalg.lstsq(xf,y0,rcond=None)[0]
        else:raise ValueError("Unknown estimand")
        s0=float(np.sum((y-p0)**2))
        s1=float(np.sum((y-p1)**2))
        if s0<=0 or not np.isfinite(s0+s1):raise ValueError("MODEL_HOLD: nonfinite/degenerate heldout SSE")
        scores.append({"site":held,"n_units":len(test),
             "baseline_sse":s0,"with_pd_sse":s1,"pd_incremental_SSE_gain":1-s1/s0})
    return scores


def bootstrap_verdict(scores:list):
    v=np.asarray([r["pd_incremental_SSE_gain"] for r in scores],float)
    rng=np.random.default_rng(SEED)
    boot=v[rng.integers(0,len(v),size=(REPS,len(v)))].mean(axis=1)
    ci=np.quantile(boot,[.025,.975])
    return {"site_equal_mean_gain":float(v.mean()),
       "site_bootstrap_ci95":[float(ci[0]),float(ci[1])],
       "n_sites_positive":int((v>0).sum()),
       "n_independent_source_sites":len(v),
       "positive_source_transport_supported":bool(v.mean()>0 and ci[0]>0 and int((v>0).sum())>=5),
       "site_equal_SSE_improvement_pct":float(100*v.mean()),
       "site_records":scores,"bootstrap_seed":SEED,"bootstrap_site_draws":REPS}


def main(args):
    srows,crows,plots,nativeplots,height,qa=source_checks(args)
    # Community source opened only after outcome-blind 150-plot and M3 rank checks.
    sourceplots,allcells,missing,sitepop=composition(srows,crows,args.design,args.community,height,qa)
    if len(sourceplots)!=174 or len(allcells)!=521 or missing!=1:
        raise ValueError("SOURCE_HOLD: original 2010 Community 174/521 original control not reproduced")
    cells=[]
    for r in allcells:
        key=(r["site"],r["plot"])
        if key in plots:
            p=plots[key]
            cells.append({**r,**p})
    sites=sorted(ORIGINAL_SITES)
    if (len(cells)<440 or len(cells)>450 or
        dict(Counter(x["site"] for x in cells)).keys()!=ORIGINAL_SITES.keys() or
        len({(x["site"],x["plot"]) for x in cells})!=150):
        raise ValueError("SOURCE_HOLD: 150 original cohort did not carry >=440/450 valid Community plot-years")
    primary=bootstrap_verdict(score_sites(cells,sites,method="mass"))
    structure=bootstrap_verdict(score_sites(list(plots.values()),sites,method="fd"))
    nativecounts=Counter(s for s,p in nativeplots)
    sufficiently_native=(len(nativeplots)>=100 and sum(x>=8 for x in nativecounts.values())>=5)
    native={"n_plots":len(nativeplots),"n_sites_at_least8":sum(x>=8 for x in nativecounts.values()),
            "source_original_sites":dict(sorted(nativecounts.items()))}
    if sufficiently_native:
        ncells=[{**r,**nativeplots[(r["site"],r["plot"])]} for r in allcells
                if (r["site"],r["plot"]) in nativeplots]
        nsites=sorted({r["site"] for r in ncells})
        native.update({"status":"ESTIMATED_SEPARATE_NATIVE_ONLY_COHORT",
                       "source_plot_years":len(ncells),
                       "prediction":bootstrap_verdict(score_sites(ncells,nsites,method="mass"))})
    else:
        native["status"]="NATIVE_ONLY_UNDERPOWERED_HOLD"
    return {
      "status":"POSTRESULT_BIODEPTH_MATCHED_PD_FD_BIOMASS_ESTIMATED",
      "version":"v0.1",
      "interpretation":"new phylogenetic source breadth is not trait-specific memory K or causal mediation",
      "source_gates":"source-only 98/103 S3 phylogeny PASS and 84-taxon / 150-plot GIFT join PASS",
      "original_GIFT_species_fingerprint":qa["GIFT_original_target_species_height_and_reference_fingerprint_sha256"],
      "source_original_matched_plots":len(plots),
      "source_original_matched_site_counts":ORIGINAL_SITES,
      "source_matched_plot_year_numeric_responses":len(cells),
      "source_Community2010_response_only":True,
      "response":"log1p original Hector 2010 Community standing aboveground biomass g/m2",
      "source_species_weights":"equal original sown species across the same S3+GIFT joint-covered taxa",
      "PD":"mean pairwise patristic distance on original S3 dated phylogeny among same species as height FD",
      "primary_biomass_incremental_PD_over_FD_and_CWM":primary,
      "secondary_planted_height_FD_predictable_by_PD":structure,
      "mandatory_native_only_sensitivity":native,
      "no_original_BIEN_trait_memory_rho_or_AusTraits_K_tested":True,
      "post_result_exploratory":True,
      "nonclaims":["No proof of trait-specific Blomberg K, evolutionary memory, evolutionary selection or causal FD mediation",
                   "Original GIFT plant height source max is not realized local height and excludes original Greece",
                   "Original 150-plot matched cohort is distinct from historical 174-plot original corrected FD study",
                   "Only seven original source study sites; tree phylogeny is not independent biodiversity intervention",
                   "Previous global sPlotOpen×BIEN, strict original BIODEPTH six-site, NEON access gates remain HOLD"],
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for k in ("species","codes","design","community","provenance","phylogeny-gate","joint-gate","tree-crosswalk","tree-distances","out"):
        ap.add_argument("--"+k)
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:
        vals=np.array([.2,.4,.6])
        assert math.isclose(np.abs(vals[:,None]-vals[None,:]).sum()/(3*2),.26666666666666666)
        assert ORIGINAL_SITES["Portugal"]==8 and sum(ORIGINAL_SITES.values())==150
        assert REPS==10000
        print("MATCHED_PD_FD_BIOMASS_FIXTURE_PASS")
    else:
        required=("species","codes","design","community","provenance","phylogeny-gate","joint-gate","tree-crosswalk","tree-distances","out")
        if not all(getattr(args,k.replace("-","_")) for k in required):ap.error("Missing source-locked input path")
        r=main(args)
        path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print("BIODEPTH_MATCHED_PD_FD_BIOMASS_RESULT",json.dumps({
         k:v for k,v in r.items() if k not in ("nonclaims",)},sort_keys=True),flush=True)
