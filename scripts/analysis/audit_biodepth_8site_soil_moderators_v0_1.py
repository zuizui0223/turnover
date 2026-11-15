#!/usr/bin/env python3
"""BIODEPTH Table S1 soil N/pH context vs already seen 8 site guild contrasts.

This is post-result exploratory correlation, not prospective site moderation,
not an N-fixation or causal experiment. All eight field sites are retained.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.request
from itertools import permutations
from pathlib import Path
import numpy as np
from bs4 import BeautifulSoup
from scipy.stats import pearsonr,spearmanr,theilslopes

SITE_NAMES={"Germany":"Bayreuth","Greece":"Mytilini","Ireland":"Riverstick",
            "Portugal":"Lezirias","Sheffield":"Sheffield","Silwood":"Silwood",
            "Sweden":"Umeå","Switzerland":"Lupsingen"}
SOURCE_SHA="20694c14d6b6eccf016294eeae2058479b12c830272a6175a62d32714703c116"

def source_soil_table():
    req=urllib.request.Request("https://ndownloader.figshare.com/files/5640234",
       headers={"User-Agent":"turnover-biodepth-source-soil-context-v0.1"})
    with urllib.request.urlopen(req,timeout=90) as r:raw=r.read(1000000)
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError("Original supplementary Table S1 source changed")
    soup=BeautifulSoup(raw.decode("utf-8","replace"),"html.parser")
    tables=soup.find_all("table")
    if len(tables)<2:raise ValueError("Cannot identify original BIODEPTH 2005 Table S1")
    rows=[[x.get_text(" ",strip=True) for x in tr.find_all(["th","td"])]
          for tr in tables[1].find_all("tr")]
    if len(rows)!=9 or len(rows[0])!=11:raise ValueError("Original 8-site table geometry changed")
    names={r[1]:r for r in rows[1:]}
    if set(names)!=set(SITE_NAMES.values()):raise ValueError("Original 8 field sites differ")
    return {s:{"soil_pH":float(names[n][5]),
               "soil_total_N_percent":float(names[n][7]),
               "latitude_deg_N":float(names[n][2]),
               "original_location_name":n}
            for s,n in SITE_NAMES.items()}

def exact_p(x,y):
    # 8! label arrangements, fixed original eight-site x values.
    x=np.asarray(x,float);y=np.asarray(y,float)
    xc=x-x.mean();yc=y-y.mean()
    obs=abs(float(xc@yc))
    ext=sum(abs(float(xc@yc[list(perm)]))>=obs-1e-12
            for perm in permutations(range(8)))
    return ext/40320

def test_one(label,field,soil,eff):
    sites=sorted(SITE_NAMES)
    x=np.array([soil[s][field] for s in sites],float)
    y=np.array([eff[s]["matched_stratum_equal_weight_mean_log_difference"] for s in sites],float)
    p=pearsonr(x,y);sp=spearmanr(x,y)
    loocv=[float(pearsonr(x[np.arange(8)!=i],y[np.arange(8)!=i]).statistic)
           for i in range(8)]
    ts=theilslopes(y,x)
    return {"axis":label,"n_original_sites":8,"Pearson_r":float(p.statistic),
            "Pearson_p_normal_theory":float(p.pvalue),
            "Pearson_exact_permutation_40320_p":exact_p(x,y),
            "Spearman_rho":float(sp.statistic),"Spearman_p":float(sp.pvalue),
            "TheilSen_slope":float(ts.slope),
            "TheilSen_95CI":[float(ts.low_slope),float(ts.high_slope)],
            "Pearson_leave_one_site_out_minmax":[min(loocv),max(loocv)]}

def main(matched):
    soil=source_soil_table()
    original=json.loads(Path(matched).read_text(encoding="utf-8"))
    effects={x["site"]:x for x in original["site_results"]}
    if set(effects)!=set(SITE_NAMES) or original["source_selected_population"]["matched_original_plots"]!=110:
        raise ValueError("Original matched treatment outcome sources no longer agree")
    if abs(np.mean([x["matched_stratum_equal_weight_mean_log_difference"] for x in effects.values()])
           -0.17147354565109507)>1e-10:
        raise ValueError("Historical published BIODEPTH eight-site contrast changed")
    out={k:test_one(k,field,soil,effects) for k,field in [
        ("soil_total_N_percent","soil_total_N_percent"),
        ("soil_pH","soil_pH"),
        ("latitude_posthoc_only","latitude_deg_N")]}
    # Two planned-after-outcome soil axes; latitude not included in this family.
    ss=["soil_total_N_percent","soil_pH"]
    order=sorted(ss,key=lambda k:out[k]["Pearson_exact_permutation_40320_p"])
    rolling=0.
    for i,k in enumerate(order):
        rolling=max(rolling,min(1.,(2-i)*out[k]["Pearson_exact_permutation_40320_p"]))
        out[k]["Holm_two_soil_axes_exploratory_p"]=rolling
    return {"version":"v0.1","status":"BIODEPTH_POSTRESULT_EIGHT_SITE_SOIL_CONTEXT_AUDIT_VERIFIED",
        "source_metadata":"Spehn et al. 2005 original Figshare sup-1.htm Table S1",
        "source_sha256":SOURCE_SHA,"n_original_sites":8,
        "site_data":[{"site":s,**soil[s],
                     "observed_prior_guild_contrast":effects[s]["matched_stratum_equal_weight_mean_log_difference"],
                     "original_matched_plot_count":effects[s]["n_matched_original_plots"]}
                     for s in sorted(SITE_NAMES)],
        "tests":out,
        "hard_nonclaims":[
          "The same eight site treatment effects were already observed before moderator selection",
          "Soil pH and total N are eight original site-level summaries, not plot-matched lab measures",
          "Latitude is posthoc geography and proxy for weather, species pool and site history",
          "The original sites used different soil sampling depths and harvest schedules",
          "No causal nitrogen fixation, trait FD or family phylogenetic memory rho tested",
          "Original ≥6 sites with 20 same-richness plots gate remains HOLD"]}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--matched",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    results=main(a.matched)
    f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n")
    print("BIODEPTH_EIGHT_SITE_SOIL_CONTEXT",json.dumps(
        {k:v for k,v in results.items() if k!="site_data"},sort_keys=True))
