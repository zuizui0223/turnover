#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math,random
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--family-reps",type=Path,required=True)
ap.add_argument("--family-distances",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--scores-out",type=Path,required=True)
a=ap.parse_args()

with a.effects.open(newline="") as fh: rows=list(csv.DictReader(fh))
with a.family_reps.open(newline="") as fh: reps={r["family"]:r for r in csv.DictReader(fh) if r["representative_node"]}
with a.family_distances.open(newline="") as fh: pairs=list(csv.DictReader(fh))

def rho(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    rx=rankdata(x,method="average"); ry=rankdata(y,method="average")
    return float(np.corrcoef(rx,ry)[0,1])

def scores_for(axis,kind="median",omit_trait=None):
    use=[r for r in rows if r["trait_name"]!=omit_trait and r["family"] in reps]
    bytrait={}
    for r in use: bytrait.setdefault(r["trait_name"],[]).append(r)
    centered={}
    for t,rr in bytrait.items():
        vals=[float(r[axis]) for r in rr]
        for i,r in enumerate(rr):
            others=vals[:i]+vals[i+1:]
            if others:
                centered[(r["family"],t)]=float(r[axis])-sum(others)/len(others)
    byfam={}
    for (f,t),v in centered.items(): byfam.setdefault(f,[]).append(v)
    out={}
    for f,v in byfam.items():
        if len(v)>=2:
            out[f]=float(np.median(v) if kind=="median" else np.mean(v))
    return out

def pair_stat(scores):
    d=[]; delta=[]
    for p in pairs:
        f1,f2=p["family1"],p["family2"]
        if f1 in scores and f2 in scores:
            d.append(float(p["patristic_distance"]))
            delta.append(abs(scores[f1]-scores[f2]))
    return rho(d,delta),len(d)

def perm_test(scores,seed=20261004,P=9999):
    obs,n=pair_stat(scores)
    fam=sorted(scores); vals=[scores[f] for f in fam]
    rng=random.Random(seed)
    null=[]
    for _ in range(P):
        z=vals[:]; rng.shuffle(z)
        null.append(pair_stat(dict(zip(fam,z)))[0])
    p=(1+sum(abs(v)>=abs(obs) for v in null))/(P+1)
    return obs,p,n,float(np.quantile(null,.025)),float(np.quantile(null,.975))

s3=scores_for("S3_rho","median")
pr=scores_for("prune_only_rho","median")
mean_s3=scores_for("S3_rho","mean")
s3res=perm_test(s3); prres=perm_test(pr); meanres=perm_test(mean_s3)

traits=sorted({r["trait_name"] for r in rows})
loo=[]
for t in traits:
    sc=scores_for("S3_rho","median",t)
    if len(sc)>=30:
        rr,_=pair_stat(sc)
        loo.append(rr)

a.scores_out.parent.mkdir(parents=True,exist_ok=True)
with a.scores_out.open("w",newline="") as fh:
    w=csv.writer(fh);w.writerow(["family","S3_context_score","prune_context_score","n_traits"])
    for f in sorted(set(s3)&set(pr)):
        n=sum(1 for r in rows if r["family"]==f)
        w.writerow([f,s3[f],pr[f],n])

out={
 "version":"v0.1","status":"FAMILY_CONTEXT_PHYLOGENY_EXPLORATORY_ESTIMATED",
 "post_outcome_exploratory":True,
 "n_families_S3":len(s3),"n_families_prune":len(pr),
 "S3":{"spearman":s3res[0],"permutation_p_two_sided":s3res[1],"n_family_pairs":s3res[2],"null_q025":s3res[3],"null_q975":s3res[4]},
 "prune_only":{"spearman":prres[0],"permutation_p_two_sided":prres[1],"n_family_pairs":prres[2]},
 "mean_score_robustness":{"spearman":meanres[0],"permutation_p_two_sided":meanres[1]},
 "leave_one_trait_out_S3":{"n":len(loo),"min":min(loo) if loo else None,"max":max(loo) if loo else None},
 "interpretation_role":"Post-outcome complementary only; cannot alter prospective portability/repeatability conclusions."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
