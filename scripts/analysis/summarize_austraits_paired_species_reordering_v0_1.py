#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from itertools import combinations
from pathlib import Path
import numpy as np,pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--original-effects",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()
orig=pd.read_csv(a.original_effects)
orig=orig[orig.log_domain_pass==True].copy()
lookup={(r.family,r.trait_name):r for r in orig.itertuples(index=False)}

rows=[]
holds={}
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text());st=x.get("status")
    holds[st]=holds.get(st,0)+1
    if st!="PAIRED_SPECIES_RHO_ESTIMATED":continue
    ka=(x["family"],x["trait_a"]);kb=(x["family"],x["trait_b"])
    if ka not in lookup or kb not in lookup:raise SystemExit("paired cell absent from frozen effects")
    A=lookup[ka];B=lookup[kb]
    rows.append({
      "family":x["family"],"trait_a":x["trait_a"],"trait_b":x["trait_b"],
      "n_shared_species":x["n_shared_species"],"n_S3":x["n_S3"],"n_prune":x["n_prune"],
      "paired_S3_a":x["S3_rho_a"],"paired_S3_b":x["S3_rho_b"],
      "paired_prune_a":x["prune_rho_a"],"paired_prune_b":x["prune_rho_b"],
      "original_S3_a":float(A.S3_log_rho),"original_S3_b":float(B.S3_log_rho),
      "original_prune_a":float(A.prune_log_rho),"original_prune_b":float(B.prune_log_rho)
    })
d=pd.DataFrame(rows)
if d.empty:raise SystemExit("no paired-species cells passed")

def summarize(axis,minf):
    pa=f"paired_{axis}_a";pb=f"paired_{axis}_b";oa=f"original_{axis}_a";ob=f"original_{axis}_b"
    traitpairs=[]
    obs_pair=obs_orig=den=maxobs=cell_change=cell_den=0
    for (A,B),g in d.groupby(["trait_a","trait_b"]):
        dp=g[pa]-g[pb];do=g[oa]-g[ob]
        valid=(dp!=0)&(do!=0)
        cell_change+=int((np.sign(dp[valid])!=np.sign(do[valid])).sum());cell_den+=int(valid.sum())
        gp=g[dp!=0];n=len(gp)
        if n<minf:continue
        pos=int(((gp[pa]-gp[pb])>0).sum());neg=int(((gp[pa]-gp[pb])<0).sum())
        op=int(((gp[oa]-gp[ob])>0).sum());on=int(((gp[oa]-gp[ob])<0).sum())
        nn=pos+neg
        if nn<2:continue
        D=nn*(nn-1)/2;mx=(nn//2)*(nn-nn//2)
        obs_pair+=pos*neg;obs_orig+=op*on;den+=D;maxobs+=mx
        traitpairs.append({"trait_a":A,"trait_b":B,"n_families":nn,
                           "paired_reversal":pos*neg/D,"original_restricted_reversal":op*on/D})
    return {
      "minimum_eligible_families":minf,"n_trait_pairs":len(traitpairs),
      "paired_species_weighted_reversal":obs_pair/den if den else None,
      "original_restricted_weighted_reversal":obs_orig/den if den else None,
      "paired_fraction_pair_specific_maximum":obs_pair/maxobs if maxobs else None,
      "order_change_after_species_matching":cell_change/cell_den if cell_den else None,
      "n_order_cells_compared":cell_den,
      "trait_pairs":traitpairs
    }

out={
 "version":"v0.1","status":"AUSTRAITS_PAIRED_SPECIES_REORDERING_ESTIMATED",
 "post_outcome_exploratory":True,
 "input_status_counts":holds,
 "n_supported_family_trait_pair_cells":int(len(d)),
 "n_families":int(d.family.nunique()),
 "n_trait_pairs":int(d[["trait_a","trait_b"]].drop_duplicates().shape[0]),
 "shared_species":{"median":float(d.n_shared_species.median()),"min":int(d.n_shared_species.min()),"max":int(d.n_shared_species.max())},
 "S3":{"min5":summarize("S3",5),"min10":summarize("S3",10)},
 "prune":{"min5":summarize("prune",5),"min10":summarize("prune",10)}
}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in out.items() if k not in ["S3","prune"]},indent=2))
print(json.dumps({"S3_min10":out["S3"]["min10"],"prune_min10":out["prune"]["min10"]},indent=2))
