#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from itertools import combinations
import numpy as np,pandas as pd
from scipy.stats import spearmanr

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()

rows=[]
full=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    if x.get("status")!="AUSTRAITS_SPLIT_HALF_SYSTEM_ESTIMATED":raise SystemExit(f"bad result {p}")
    for axis,key in [("S3","S3"),("prune","prune_only")]:
        full.append({"system_id":x["system_id"],"family":x["family"],"trait_name":x["trait_name"],
                     "axis":axis,"full_rho":x[key]["full_rho"],"n_tips":x[key]["n_tips"]})
        for z in x[key]["splits"]:
            rows.append({"system_id":x["system_id"],"family":x["family"],"trait_name":x["trait_name"],
                         "axis":axis,"replicate":int(z["replicate"]),"n_A":int(z["n_A"]),"n_B":int(z["n_B"]),
                         "rho_A":float(z["rho_A"]),"rho_B":float(z["rho_B"])})
spl=pd.DataFrame(rows);ful=pd.DataFrame(full)
if ful.system_id.nunique()!=158:raise SystemExit(f"expected 158 systems, got {ful.system_id.nunique()}")
a.table_out.parent.mkdir(parents=True,exist_ok=True);spl.to_csv(a.table_out,index=False)

def allowed_pairs(df,min_fams):
    counts={}
    for (a1,b1) in combinations(sorted(df.trait_name.unique()),2):
        fa=set(df.loc[df.trait_name==a1,"family"]);fb=set(df.loc[df.trait_name==b1,"family"])
        n=len(fa&fb)
        if n>=min_fams:counts[(a1,b1)]=n
    return counts

def measurement_reversal(axis,min_fams):
    d=spl[spl.axis==axis].copy()
    base=ful[ful.axis==axis]
    allowed=allowed_pairs(base,min_fams)
    repout=[]
    for rep,g in d.groupby("replicate"):
        disc=den=0
        for fam,h in g.groupby("family"):
            m={r.trait_name:r for r in h.itertuples(index=False)}
            for pair in allowed:
                if pair[0] not in m or pair[1] not in m:continue
                ra,rb=m[pair[0]],m[pair[1]]
                da=ra.rho_A-rb.rho_A;db=ra.rho_B-rb.rho_B
                if da==0 or db==0:continue
                den+=1;disc+=int((da>0)!=(db>0))
        repout.append({"replicate":int(rep),"discordant":disc,"comparisons":den,
                       "reversal_probability":disc/den if den else None})
    vals=[z["reversal_probability"] for z in repout if z["reversal_probability"] is not None]
    return {"minimum_trait_pair_family_cooccurrence":min_fams,"n_trait_pairs":len(allowed),
            "replicates":repout,"mean_reversal_probability":float(np.mean(vals)),
            "median_reversal_probability":float(np.median(vals)),
            "range":[float(min(vals)),float(max(vals))]}

def observed_cross_family(axis,min_fams):
    d=ful[ful.axis==axis].copy()
    traits=sorted(d.trait_name.unique());obs=den=maxobs=npairs=0
    details=[]
    for A,B in combinations(traits,2):
        da=d[d.trait_name==A][["family","full_rho"]].rename(columns={"full_rho":"a"})
        db=d[d.trait_name==B][["family","full_rho"]].rename(columns={"full_rho":"b"})
        m=da.merge(db,on="family")
        if len(m)<min_fams:continue
        diff=m.a-m.b;pos=int((diff>0).sum());neg=int((diff<0).sum());n=pos+neg
        if n<2:continue
        o=pos*neg;D=n*(n-1)/2;mx=(n//2)*(n-n//2)
        obs+=o;den+=D;maxobs+=mx;npairs+=1
        details.append({"trait_a":A,"trait_b":B,"n_families":n,"reversal_probability":o/D})
    return {"minimum_trait_pair_family_cooccurrence":min_fams,"n_trait_pairs":npairs,
            "weighted_reversal_probability":obs/den if den else None,
            "fraction_of_pair_specific_maximum":obs/maxobs if maxobs else None}

def system_reliability(axis):
    d=spl[spl.axis==axis]
    out=[]
    for rep,g in d.groupby("replicate"):
        z=spearmanr(g.rho_A,g.rho_B)
        out.append({"replicate":int(rep),"n_systems":len(g),"spearman_rho":float(z.statistic),"p_two_sided":float(z.pvalue)})
    return {"replicates":out,"mean_spearman":float(np.mean([z["spearman_rho"] for z in out]))}

out={"version":"v0.1","status":"AUSTRAITS_SPLIT_HALF_RANK_RELIABILITY_ESTIMATED",
     "post_outcome_exploratory":True,"n_systems":158,"n_families":int(ful.family.nunique()),"n_traits":int(ful.trait_name.nunique()),
     "support_rule":"prune-only native tips >=40; matched positive-numeric log core","axes":{}}
for axis in ["S3","prune"]:
    obs5=observed_cross_family(axis,5);obs10=observed_cross_family(axis,10)
    meas5=measurement_reversal(axis,5);meas10=measurement_reversal(axis,10)
    out["axes"][axis]={
      "system_split_half_reliability":system_reliability(axis),
      "measurement_order_reversal_min5":meas5,
      "measurement_order_reversal_min10":meas10,
      "observed_cross_family_reversal_min5":obs5,
      "observed_cross_family_reversal_min10":obs10,
      "measurement_to_observed_ratio_min5":meas5["mean_reversal_probability"]/obs5["weighted_reversal_probability"] if obs5["weighted_reversal_probability"] else None,
      "measurement_to_observed_ratio_min10":meas10["mean_reversal_probability"]/obs10["weighted_reversal_probability"] if obs10["weighted_reversal_probability"] else None
    }
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
