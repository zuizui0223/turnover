#!/usr/bin/env python3
"""Source-pinned independent original BIODEPTH 8-site exploratory numeric replay.

Original 6-site >=20 plots within ONE richness-level qualification stays HOLD.
Plot x year source response is reused only in separate post-source exploratory study.
"""
from __future__ import annotations
import csv,hashlib,io,json,urllib.request
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import t as student_t

PIN={
"Design.txt":(5640240,"a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a"),
"Shoots.txt":(5640249,"cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135"),
}
EXPECT={
"Germany":(0.31662116166641585,0.04888953814837336),
"Greece":(0.07713899188166996,0.5283558615786296),
"Ireland":(-0.10303510734224747,0.052057827691545155),
"Portugal":(-0.3115363901664102,0.5092536786372474),
"Sheffield":(0.21756249720194504,0.08623647992239573),
"Silwood":(0.108038283369883,0.05707767865877654),
"Sweden":(-0.2756259141971289,0.5476414982896809),
"Switzerland":(0.23273014407973913,0.07858574246884922),
}

def get_sources():
    payload={}
    for name,(fid,sha) in PIN.items():
        url=f"https://ndownloader.figshare.com/files/{fid}"
        req=urllib.request.Request(url,headers={"User-Agent":"turnover-original-BIODEPTH-8site-replay/0.1"})
        with urllib.request.urlopen(req,timeout=70) as res:raw=res.read(1000000)
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("Original Figshare v1 source checksum mismatch")
        payload[name]=pd.read_csv(io.BytesIO(raw),sep="\t")
        print("ORIGINAL_BIODEPTH_SOURCE_PIN_PASS",name,len(raw),sha)
    return payload

def independent_replay():
    source=get_sources()
    d,s=source["Design.txt"],source["Shoots.txt"]
    if len(d)!=480 or len(s)!=1440 or d["plot"].nunique()!=480 or s["plot"].nunique()!=480:
        raise ValueError("Original 480x3 BIODEPTH cohort changed")
    if any(set(d[c].unique())!={"Yes","No"} for c in ("grasses","legumes","forbs")):
        raise ValueError("Original Yes/No guild indicators changed")
    for c in ("grasses","legumes","forbs"):d[c]=(d[c]=="Yes").astype(int)
    if not (d[["grasses","legumes","forbs"]].sum(axis=1)==d["functional.richness"]).all() or int(d.grasses.sum())!=358:
        raise ValueError("Original source guild assignment/grass frequency changed")
    m=s.merge(d,on="plot",how="left",validate="many_to_one",suffixes=("_s","_d"),indicator=True)
    if not m._merge.eq("both").all():raise ValueError("Original source plot mismatch")
    for c in ("species.richness","functional.richness","block","composition"):
        if not m[c+"_s"].eq(m[c+"_d"]).all():raise ValueError("Original treatment key mismatch "+c)
    if not m.legumes_s.eq(m.legumes_d.map({0:"No",1:"Yes"})).all():
        raise ValueError("Original legume condition mismatch")
    cross=m.groupby("location_s").location_d.nunique()
    if len(cross)!=8 or not cross.eq(1).all() or m.groupby("location_d").location_s.nunique().max()!=1:
        raise ValueError("Numeric/text site code crosswalk is ambiguous")
    if m.biomass.notna().sum()!=1419 or m.biomass.eq(0).sum()!=34 or (m.biomass.dropna()<0).any():
        raise ValueError("Original measured response quality changed")
    chosen=[]
    support_meta={}
    for site,g in d.groupby("location",sort=True):
        variants=[]
        nmax=0
        for rich,pop in g.groupby("species.richness"):
            if pop["functional.richness"].nunique()>1:
                variants.extend(pop["plot"].to_list())
                nmax=max(nmax,len(pop))
                chosen.extend(pop["plot"].to_list())
        support_meta[site]={"n_plots":len(variants),"max_single_richness_count":nmax,
                             "strict_ge20_site_pass":nmax>=20}
    if len(chosen)!=230 or len(set(chosen))!=230 or sum(x["strict_ge20_site_pass"] for x in support_meta.values())!=1:
        raise ValueError("Original strict source 1/8 eligibility and 230 cohort changed")
    pop=m[m["plot"].isin(chosen)&m.biomass.notna()].copy()
    pop=pop.assign(site=pop.location_d,richness=pop["species.richness_d"].astype(int),
           fg=pop["functional.richness_d"].astype(int),composition=pop["composition_d"].astype(int),
           block=pop["block_d"].astype(int),grasses=pop.grasses.astype(int),
           legumes=pop.legumes_d.astype(int),forbs=pop.forbs.astype(int))
    pop["log_biomass"]=np.log1p(pop.biomass)
    if len(pop)!=681:raise ValueError("Original 681 eligible source year cells changed")
    effects=[];identity_count=0
    for site,g in pop.groupby("site",sort=True):
        if g["year"].nunique()!=3:raise ValueError("source years missing for "+site)
        block=" + C(block)" if g["block"].nunique()>1 else ""
        count_formula="log_biomass ~ C(richness)+C(year)"+block+" + fg"
        model=smf.ols(count_formula,data=g).fit(cov_type="cluster",
               cov_kwds={"groups":g.composition,"use_correction":True})
        if np.linalg.matrix_rank(model.model.exog)!=model.model.exog.shape[1]:
            raise ValueError("Rank-deficient original source count model: "+site)
        beta=float(model.params["fg"]);se=float(model.bse["fg"])
        eb,es=EXPECT[site]
        if abs(beta-eb)>1e-9 or abs(se-es)>1e-9:
            raise ValueError(f"Effect replay disagreement {site}: {beta} vs {eb}; SE {se} vs {es}")
        clusters=g.composition.nunique();df=clusters-1
        conf=float(student_t.ppf(.975,df))*se
        guild_formula="log_biomass ~ C(richness)+C(year)"+block+" + grasses+legumes+forbs"
        gm=smf.ols(guild_formula,data=g).fit(cov_type="cluster",
                 cov_kwds={"groups":g.composition,"use_correction":True})
        full_rank=np.linalg.matrix_rank(gm.model.exog)==gm.model.exog.shape[1]
        guild_p=float(gm.wald_test("grasses=forbs,legumes=forbs",scalar=True).pvalue) if full_rank else None
        identity_count+=int(full_rank)
        cv={}
        for model_name,term in (("richness_only",""),("plus_count"," + fg"),("plus_identity"," + grasses+legumes+forbs")):
            training=g[g.year.isin((1,2))];testing=g[g.year==3]
            form="log_biomass ~ C(richness)+year"+block+term
            fit=smf.ols(form,data=training).fit()
            if np.linalg.matrix_rank(fit.model.exog)!=fit.model.exog.shape[1]:
                cv[model_name]={"status":"SOURCE_TRAINING_RANK_HOLD"}
                continue
            ytest=testing.log_biomass.to_numpy()
            pred=np.asarray(fit.predict(testing),dtype=float)
            cv[model_name]={"status":"ESTIMABLE","SSE":float(np.sum((ytest-pred)**2))}
        baseline=cv["richness_only"].get("SSE")
        for k in ("plus_count","plus_identity"):
            if baseline and cv[k]["status"]=="ESTIMABLE":
                cv[k]["gain_over_richness_only_SSE"]=1-cv[k]["SSE"]/baseline
        effects.append({"site":site,"n_plots":support_meta[site]["n_plots"],
              "n_source_plot_year_cells":len(g),"n_composition_clusters":clusters,
              "count_beta":beta,"count_cluster_SE":se,"count_cluster_t_CI95":[beta-conf,beta+conf],
              "count_cluster_t_p":float(2*student_t.sf(abs(beta/se),df)),
              "guild_identity_full_rank":full_rank,"guild_equality_wald_p":guild_p,
              "year_1_2_fit_to_year3_same_plots":cv})
    if identity_count!=3:
        raise ValueError("Original source 3/8 full-rank guild identity site support changed")
    coeff=np.array([x["count_beta"] for x in effects])
    rng=np.random.default_rng(20261115)
    sims=coeff[rng.integers(0,len(coeff),size=(10000,len(coeff)))].mean(axis=1)
    mean=float(coeff.mean());interval=[float(v) for v in np.quantile(sims,[.025,.975])]
    if abs(mean-0.0327367083117333)>1e-10 or max(abs(interval[i]-[-0.1314615382085546,0.17997176966827177][i]) for i in (0,1))>1e-10:
        raise ValueError("Independent eight-site meta bootstrap failed to reproduce earlier source")
    return {
      "version":"v0.1","status":"SOURCE_PINNED_EIGHT_SITE_EXPLORATORY_REPLAY_PASS",
      "source_DOI":"10.6084/m9.figshare.3565170.v1",
      "original_primary_source_gate":"HOLD_ONE_OF_EIGHT_SITES_MEET_EXACT_RICHNESS_20PLOTS",
      "original_design_plots":480,"original_yearly_records":1440,
      "exploratory_source_support_plots":230,"exploratory_valid_plot_year_rows":681,
      "site_effects":effects,"guild_identity_full_rank_sites":identity_count,
      "site_equal_mean_beta":mean,"site_equal_mean_bootstrap_ci95":interval,
      "site_sd_beta":float(coeff.std(ddof=1)),
      "positive_site_slopes":int((coeff>0).sum()),
      "original_study_already_reports_diversity_biomass_effects":True,
      "not_confirmatory_or_causal":True,
    }
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=independent_replay()
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("BIODEPTH_ORIGINAL_NUMERIC_REPLAY",json.dumps({k:v for k,v in result.items() if k!="site_effects"},sort_keys=True))
    for x in result["site_effects"]:
        print("BIODEPTH_SOURCE_SITE_REPLAY",json.dumps({k:v for k,v in x.items() if k!="year_1_2_fit_to_year3_same_plots"},sort_keys=True))
