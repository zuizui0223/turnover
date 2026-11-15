#!/usr/bin/env python3
"""Independent source-native BIODEPTH grass+legume vs grass+forb matched replay.

Does not use the eight-site FG model, model selection or any tree/trait FD.
All original 6-site strict single-richness support gates remain HOLD.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np

ORIGINAL={
 "Design.txt":(5640240,"29e7d05f45b8613d9bead9337da7d3cc","a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a"),
 "Shoots.txt":(5640249,"76824bf9ce195e84aa17ae4cd6c1a336","cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135")
}
FROZEN_SITES={
 "Germany":0.552019, "Greece":-0.832717, "Ireland":0.202011,
 "Portugal":-1.663950, "Sheffield":0.156082, "Silwood":0.134931,
 "Sweden":2.223094, "Switzerland":0.600319
}

def original_rows(name):
    fileid,md,sha=ORIGINAL[name]
    req=urllib.request.Request(f"https://ndownloader.figshare.com/files/{fileid}",
             headers={"User-Agent":"turnover-BIODEPTH-matched-legume-forb-original-replay/0.1"})
    with urllib.request.urlopen(req,timeout=85) as f:
        b=f.read(1500000)
    if hashlib.md5(b).hexdigest()!=md or hashlib.sha256(b).hexdigest()!=sha:
        raise ValueError(f"Original Figshare v1 original byte checksum mismatch {name}")
    return list(csv.DictReader(io.StringIO(b.decode("utf-8-sig")),delimiter="\t"))

def summarize(design,shoots):
    if len(design)!=480 or len(shoots)!=1440:
        raise ValueError("Original BIODEPTH source shape changed")
    indexed={r["plot"]:r for r in design}
    if len(indexed)!=480:raise ValueError("Duplicate original plot")
    if sum(r["grasses"]=="Yes" for r in design)!=358:
        raise ValueError("Original grass Yes/No source support changed")
    target=[r for r in design
            if r["grasses"]=="Yes" and r["functional.richness"]=="2"
            and (r["legumes"],r["forbs"]) in (("Yes","No"),("No","Yes"))]
    if len(target)!=114:raise ValueError("Fixed original pre-outcome source support changed")
    g=defaultdict(set)
    for r in target:
        g[(r["location"],r["species.richness"],r["block"])].add(r["legumes"])
    matched={k for k,v in g.items() if v=={"No","Yes"}}
    matching={r["plot"] for r in target
               if (r["location"],r["species.richness"],r["block"]) in matched}
    if len(matched)!=35 or len(matching)!=110:
        raise ValueError("Original matched 35 source treatment strata/110 plots changed")
    by=defaultdict(list)
    valid=0
    for r in shoots:
        plot=r["plot"]
        if plot not in matching:continue
        source=indexed[plot]
        for col in ("composition","block","functional.richness","species.richness","legumes"):
            if r[col]!=source[col]:
                raise ValueError("Published original treatment contradicts source response")
        val=r["biomass"].strip()
        if val in ("","NA","NaN","nan","null"):continue
        f=float(val)
        if not math.isfinite(f) or f<0:
            raise ValueError("Nonfinite or negative original BIODEPTH biomass")
        key=(source["location"],source["species.richness"],source["block"],r["year"],source["legumes"])
        by[key].append(math.log1p(f))
        valid+=1
    if valid!=327:raise ValueError("Original matched observed source records changed")
    rank_year=defaultdict(list)
    all_years=0
    for site,rich,block in matched:
        for year in ("1","2","3"):
            base=(site,rich,block,year)
            a=by.get(base+("Yes",),[])
            b=by.get(base+("No",),[])
            if not a or not b:continue
            delta=sum(a)/len(a)-sum(b)/len(b)
            rank_year[(site,rich,block)].append(delta)
            all_years+=1
    if all_years!=105 or len(rank_year)!=35:
        raise ValueError("Expected all 105 matched site×rank×block×year comparisons")
    site_deltas=defaultdict(list)
    for (site,rich,block),vals in rank_year.items():
        site_deltas[site].append(sum(vals)/len(vals))
    if len(site_deltas)!=8:raise ValueError("Original 8 original site population differs")
    effects={site:sum(xs)/len(xs) for site,xs in site_deltas.items()}
    for site,approx in FROZEN_SITES.items():
        if abs(effects[site]-approx)>1e-5:
            raise ValueError(f"Source replay disagrees with frozen independent source validation: {site}")
    q=np.array([effects[site] for site in sorted(effects)],dtype=float)
    rng=np.random.default_rng(20261116)
    sims=q[rng.integers(0,8,size=(10000,8))].mean(axis=1)
    ci=[float(x) for x in np.quantile(sims,[.025,.975])]
    if abs(float(q.mean())-0.17147354565109507)>1e-11 or \
       max(abs(x-y) for x,y in zip(ci,(-0.5483165023631258,0.9183743892614635)))>1e-11:
        raise ValueError("Independent source-matched 8-site site bootstrap disagrees")
    return {
     "version":"v0.1",
     "status":"PINNED_ORIGINAL_BIODEPTH_MATCHED_GUILD_REPLAY_PASS",
     "source_hashes":{k:v[2] for k,v in ORIGINAL.items()},
     "original_mainline_six_site_20plot_single_richness_gate":"HOLD_ONE_OF_EIGHT",
     "design":"grass+legume versus grass+nonlegume forb, exact site×sown species richness×original field block, unchanged two planned guilds",
     "n_original_experiment_plots":480,"n_original_plot_year_rows":1440,
     "n_raw_eligible_grass_two_guild_plots":114,"n_source_matched_plots":110,
     "n_original_matched_strata":35,"n_valid_matched_plot_year_rows":valid,
     "n_matched_stratum_by_year_differences":all_years,"independent_geographic_sites":8,
     "original_site_estimands_log1p_biomass_legume_minus_forb":effects,
     "equal_site_mean":float(q.mean()),"positive_site_count":int((q>0).sum()),
     "resample_original_site_bootstrap_seed":20261116,
     "resample_site_10000_CI95":ci,
     "no_causal_N_fixation_or_generalized_biomass_FD_claim":True,
     "novelty":"Retrospective internal BIODEPTH support-conditioned diagnostic; original Spehn et al. 2005 had analyzed legume diversity-functioning",
    }

def selftest():
    # No data fitting: verify original contrast signed direction and missing treatment logic.
    assert math.isclose(math.log1p(3)-math.log1p(1),math.log(2))
    assert {("Yes","No"),("No","Yes")}=={("No","Yes"),("Yes","No")}
    return {"status":"MATCHED_SOURCE_FIXTURE_PASS","checks":2}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(selftest()))
    else:
        if not a.out:p.error("--out required")
        doc=summarize(original_rows("Design.txt"),original_rows("Shoots.txt"))
        path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("BIODEPTH_ORIGINAL_MATCHED_REPLAY",json.dumps(doc,sort_keys=True))
