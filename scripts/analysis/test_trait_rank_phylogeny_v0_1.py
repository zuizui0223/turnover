#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

AXES={
    "log_S3":"S3_log_rho",
    "log_prune":"prune_log_rho",
    "raw_S3":"S3_raw_rho",
    "raw_prune":"prune_raw_rho",
}

def profile_disagreement(values_a,values_b,min_shared):
    shared=sorted(set(values_a).intersection(values_b))
    if len(shared)<min_shared:
        return None,len(shared),0
    discord=0; denom=0
    for x,y in combinations(shared,2):
        da=values_a[x]-values_a[y]
        db=values_b[x]-values_b[y]
        if da==0 or db==0:
            continue
        denom+=1
        if (da>0)!=(db>0):
            discord+=1
    if denom==0:
        return None,len(shared),0
    return discord/denom,len(shared),denom

def build_profile_pair_table(df,col,min_shared):
    profiles={
        fam: dict(zip(g["trait_name"],g[col].astype(float)))
        for fam,g in df[["family","trait_name",col]].dropna().groupby("family")
    }
    rows=[]
    fams=sorted(profiles)
    for a,b in combinations(fams,2):
        d,nshared,nden=profile_disagreement(profiles[a],profiles[b],min_shared)
        rows.append({
            "profile_family1":a,"profile_family2":b,
            "shared_traits":nshared,"trait_pair_comparisons":nden,
            "rank_disagreement":d
        })
    return profiles,pd.DataFrame(rows)

def stat_for_assignment(distance_df,pair_lookup,assignment):
    xs=[];ys=[]
    for r in distance_df.itertuples(index=False):
        pa=assignment[r.family1]; pb=assignment[r.family2]
        key=tuple(sorted((pa,pb)))
        d=pair_lookup.get(key)
        if d is None or not np.isfinite(d):
            continue
        xs.append(float(r.patristic_distance));ys.append(float(d))
    if len(xs)<3:
        return np.nan,len(xs)
    return float(spearmanr(xs,ys).statistic),len(xs)

def run_axis(df,distance_df,col,min_shared,B,seed):
    profiles,pairs=build_profile_pair_table(df,col,min_shared)
    lookup={}
    for r in pairs.itertuples(index=False):
        if r.rank_disagreement is not None and np.isfinite(r.rank_disagreement):
            lookup[tuple(sorted((r.profile_family1,r.profile_family2)))]=float(r.rank_disagreement)
    tree_fams=sorted(set(distance_df.family1)|set(distance_df.family2))
    profile_fams=sorted(profiles)
    if tree_fams!=profile_fams:
        raise RuntimeError(f"tree/profile family mismatch: tree={len(tree_fams)} profile={len(profile_fams)}")
    ident={f:f for f in tree_fams}
    obs,n_pairs=stat_for_assignment(distance_df,lookup,ident)
    rng=np.random.default_rng(seed)
    null=np.empty(B,float)
    vals=np.asarray(profile_fams,dtype=object)
    for i in range(B):
        shuffled=rng.permutation(vals)
        assignment=dict(zip(tree_fams,shuffled.tolist()))
        null[i]=stat_for_assignment(distance_df,lookup,assignment)[0]
    valid=np.isfinite(null)
    p=float((1+np.sum(null[valid]>=obs))/(1+valid.sum()))
    quart=pd.qcut(distance_df.patristic_distance,4,labels=False,duplicates="drop")
    tmp=distance_df.copy();tmp["quartile"]=quart
    dis=[]
    for r in tmp.itertuples(index=False):
        key=tuple(sorted((r.family1,r.family2)))
        z=lookup.get(key)
        if z is not None and np.isfinite(z):
            dis.append((int(r.quartile),float(r.patristic_distance),float(z)))
    qrows=[]
    if dis:
        qdf=pd.DataFrame(dis,columns=["quartile","distance","disagreement"])
        for q,g in qdf.groupby("quartile"):
            qrows.append({
                "quartile":int(q)+1,
                "n_pairs":int(len(g)),
                "median_distance":float(g.distance.median()),
                "median_rank_disagreement":float(g.disagreement.median()),
                "mean_rank_disagreement":float(g.disagreement.mean())
            })
    return {
        "column":col,
        "minimum_shared_traits":min_shared,
        "n_eligible_family_pairs":int(n_pairs),
        "spearman_distance_vs_rank_disagreement":obs,
        "permutation":{
            "replicates":B,"valid_replicates":int(valid.sum()),"seed":seed,
            "p_one_sided_positive":p,
            "null_median":float(np.nanmedian(null)),
            "null_q025":float(np.nanquantile(null,.025)),
            "null_q975":float(np.nanquantile(null,.975))
        },
        "distance_quartiles":qrows,
        "profile_pair_table":pairs.to_dict(orient="records")
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--effects",type=Path,required=True)
    ap.add_argument("--distances",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--pairs-out",type=Path,required=True)
    ap.add_argument("--permutations",type=int,default=9999)
    ap.add_argument("--seed",type=int,default=20261006)
    a=ap.parse_args()
    df=pd.read_csv(a.effects)
    dist=pd.read_csv(a.distances)
    req={"family","trait_name",*AXES.values()}
    if not req.issubset(df.columns):
        raise RuntimeError(f"effects missing {sorted(req-set(df.columns))}")
    if not {"family1","family2","patristic_distance"}.issubset(dist.columns):
        raise RuntimeError("distance schema mismatch")
    if df.family.nunique()!=45 or len(df)!=201:
        raise RuntimeError("unexpected fixed discovery population")
    out={
        "version":"v0.1",
        "status":"TRAIT_RANK_PHYLOGENY_EXPLORATORY_ESTIMATED",
        "post_outcome_exploratory":True,
        "design":"data/trait_rank_phylogeny_design_v0_1.json",
        "n_systems":int(len(df)),
        "n_families":int(df.family.nunique()),
        "n_traits":int(df.trait_name.nunique()),
        "primary":run_axis(df,dist,AXES["log_S3"],4,a.permutations,a.seed),
        "mandatory_log_prune":run_axis(df,dist,AXES["log_prune"],4,a.permutations,a.seed+1),
        "shared3_sensitivities":{
            "log_S3":run_axis(df,dist,AXES["log_S3"],3,a.permutations,a.seed+2),
            "log_prune":run_axis(df,dist,AXES["log_prune"],3,a.permutations,a.seed+3)
        },
        "raw_descriptive":{
            "S3":run_axis(df,dist,AXES["raw_S3"],4,a.permutations,a.seed+4),
            "prune":run_axis(df,dist,AXES["raw_prune"],4,a.permutations,a.seed+5)
        }
    }
    # avoid duplicating large pair tables in JSON; persist them separately
    pair_rows=[]
    for label,obj in [
        ("log_S3_shared4",out["primary"]),
        ("log_prune_shared4",out["mandatory_log_prune"]),
        ("log_S3_shared3",out["shared3_sensitivities"]["log_S3"]),
        ("log_prune_shared3",out["shared3_sensitivities"]["log_prune"]),
        ("raw_S3_shared4",out["raw_descriptive"]["S3"]),
        ("raw_prune_shared4",out["raw_descriptive"]["prune"]),
    ]:
        for row in obj.pop("profile_pair_table"):
            row={"analysis":label,**row}
            pair_rows.append(row)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.pairs_out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    pd.DataFrame(pair_rows).to_csv(a.pairs_out,index=False)
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
