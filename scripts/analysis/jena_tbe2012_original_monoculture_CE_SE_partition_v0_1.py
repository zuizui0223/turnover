#!/usr/bin/env python3
"""2012 Jena TBE original exact same-pool mono expected yield / LH partition pilot.

Strict same-study retrospective CE/SE/NDE, not a scalar FD causal effect or
new independent biological replication. No original species/plot rows exported.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,re,sys,urllib.error
from pathlib import Path
import numpy as np

sys.path.insert(0,"scripts/source")
import audit_jena_tbe_2012_assigned_fd_biomass_v0_1 as src

DOI="10.1594/PANGAEA.876725"
SHA="458f61307df217d285c972f894ca5cf23709c3524dc6e13bb4d9dd3c26c2ab56"
PAT=re.compile(r"^B0B([ABC])[0-9]{3}$")
BOOT=2000
SEED=20261121
CONTRACT="docs/JENA_TBE2012_MONOCULTURE_NDE_CE_SE_MECHANISM_FROZEN_20261121.md"

class Stop(Exception):pass
def required(ok,msg):
    if not ok:raise Stop(msg)

def assemble_source():
    data=src.public_bytes()
    required(hashlib.sha256(data).hexdigest()==SHA,"OFFICIAL_ORIGINAL_SOURCE_SHA_CHANGED")
    headers,rs=src.parse_source(data)
    a=src.inspect(headers,rs)
    required(a["source_unique_plot_IDs"]==138 and a["source_harvest_rows"]==276,
             "ORIGINAL_PANGAEA_SOURCE_DENOMINATOR_CHANGED")
    required(a["status"]=="ORIGINAL_TBE_SOURCE_OR_DESIGN_HOLD"
             and a["source_field_blocks_distinct"]==1,
             "OLD_3_LITERAL_BLOCK_SOURCE_HOLD_NOT_PRESERVED")
    cols={
       "plot":src.find_col(headers,("plot",)),
       "month":src.find_col(headers,("month",)),
       "rich":src.find_col(headers,("spec no","number of species")),
       "pool":src.find_col(headers,("species pool",)),
       "fd":src.find_col(headers,("wfdc","functional diversity")),
       "block":src.find_col(headers,("block",))
    }
    species=[h for h in headers if "biom" in h.lower() and "dw" in h.lower()
             and not any(w in h.lower() for w in ("weed","unid","dead"))]
    required(len(species)==20,"SOURCE_SOWN_BIOMASS_SPECIES_COLUMNS_CHANGED")
    byplot=collections.defaultdict(list)
    for row in rs:
        plot=row[cols["plot"]].strip()
        prefix=PAT.fullmatch(plot)
        required(prefix is not None,"UNMATCHED_ORIGINAL_PLOT_PREFIX")
        month=row[cols["month"]].strip()
        rich=src.parsed_number(row[cols["rich"]],True)
        fd=src.parsed_number(row[cols["fd"]],True)
        pool=row[cols["pool"]].strip()
        required(month in {"May","Aug"} and rich in (1,2,3,4,8) and fd in (0,1,2,3,4),
                 "ORIGINAL_PLANTING_OR_HARVEST_DOMAIN_DRIFT")
        sown=[s for s in species if (row.get(s) or "").strip()]
        required(len(sown)==rich,"SOURCE_ORIGINAL_SOWN_SPECIES_ROSTER_SIZE_DRIFT")
        recorded={}
        for sp in sown:
            n=src.parsed_number(row[sp])
            required(n is not None and n>=0,"SOURCE_MISSING_OR_NEGATIVE_PLANTED_MASS")
            recorded[sp]=n
        byplot[plot].append({"month":month,"pool":pool,"prefix":prefix.group(1),
           "rich":rich,"fd":fd,"literal":row[cols["block"]].strip(),
           "sown":frozenset(sown),"mass":recorded})
    required(len(byplot)==138,"SOURCE_ORIGINAL_PLOT_COUNT_DRIFT")
    combined=[]
    for sourceplot,rowpair in byplot.items():
        required(len(rowpair)==2 and {x["month"] for x in rowpair}=={"May","Aug"},
                 "SOURCE_ORIGINAL_HARVEST_SEASON_PAIRING_HOLD")
        keys={(r["pool"],r["prefix"],r["rich"],r["fd"],r["literal"],r["sown"])
              for r in rowpair}
        required(len(keys)==1,"SOURCE_ORIGINAL_MONTHLY_PLANTED_ROSTER_DRIFT")
        x=rowpair[0]
        mass={s:sum(row["mass"][s] for row in rowpair) for s in x["sown"]}
        combined.append({"pool":x["pool"],"prefix":x["prefix"],
          "rich":x["rich"],"fd":x["fd"],"mass":mass})
    prefix=collections.Counter(x["prefix"] for x in combined)
    required(sorted(prefix.values())==[46,46,46],"PLOT_PREFIX_SOURCE_BALANCE_NOT_3x46")
    mono=collections.defaultdict(list)
    for z in combined:
        if z["rich"]!=1:continue
        required(z["fd"]==0,"MONOCULTURE_SOURCE_FD_VALUE_NOT_ZERO")
        single=list(z["mass"].items())
        required(len(single)==1,"MONOCULTURE_HAS_MULTIPLE_PLANTED_SPECIES")
        sp,val=single[0]
        mono[(z["pool"],sp)].append(val)
    mono_by_pool=collections.Counter(pool for pool,sp in mono)
    required(len(mono)==24 and sorted(mono_by_pool.values())==[8,8,8],
             "ORIGINAL_POOL_SPECIFIC_MONOCULTURE_DESIGN_NOT_24")
    required(all(len(v)==1 and v[0]>0 for v in mono.values()),
             "ORIGINAL_MONO_DUPLICATE_MISSING_OR_ZERO_ANNUAL_YIELD")
    multis=[r for r in combined if r["rich"]>=2]
    required(len(multis)==114,"ORIGINAL_COMPLETE_MIXTURE_COUNT_NOT_114")
    cells=collections.defaultdict(list)
    for r in multis:cells[(r["pool"],r["rich"])].append(r)
    eligiblekeys=[k for k,v in cells.items()
                  if sum(r["fd"]<=2 for r in v)>=4
                  and sum(r["fd"]>=3 for r in v)>=4]
    required(len(eligiblekeys)==6,"ORIGINAL_PRESPECIFIED_6_STRATA_MISSING")
    selected=[r for k in eligiblekeys for r in cells[k]]
    required(len(selected)==84,"ORIGINAL_MATCHED_84_MIXTURES_CHANGED")
    required(len({r["pool"] for r in selected})==3
             and len({r["prefix"] for r in selected})==3,
             "ORIGINAL_FD_ELIGIBLE_POOL_OR_PREFIX_LEVELS_MISSING")
    for z in selected:
        required(all((z["pool"],s) in mono for s in z["mass"]),
                 "ORIGINAL_MONOCULTURE_SAME_POOL_SPECIES_NOT_FOUND")
    sourceinfo={
      "original_source_sha256":SHA,
      "original_2012_plots":138,
      "source_mono_plots":24,"source_unique_mono_pairs_pool_taxon":len(mono),
      "source_mono_pairs_anonymized_by_pool":sorted(mono_by_pool.values()),
      "source_mixtures":114,"original_matched_mixplots":len(selected),
      "source_pools":3,"source_prefix_classes":3,
      "prefix_original_plot_counts":sorted(prefix.values()),
      "original_block_field_distinct_categories":1,
      "original_matched_pool_x_richness_strata":len(eligiblekeys),
      "mono_yield_positive_same_pool_all_matched_source_species":True,
      "no_original_biomass_or_species_values_exported":True}
    return selected,mono,sourceinfo

def partition(selected,mono):
    out=[]
    maxdiff=0
    for r in selected:
        species=list(r["mass"])
        n=len(species)
        M=np.array([mono[(r["pool"],s)][0] for s in species],float)
        Y=np.array([r["mass"][s] for s in species],float)
        required(n==r["rich"] and np.all(M>0) and np.all(Y>=0),
                 "MONO_MIX_EXPECTATION_SOURCE_INVALID")
        dy=Y/M-1/n
        nde=float(Y.sum()-M.sum()/n)
        ce=float(n*dy.mean()*M.mean())
        se=float(n*np.mean((dy-dy.mean())*(M-M.mean())))
        diff=abs(nde-(ce+se))
        required(diff<=1e-8*max(1,abs(nde)),
                 "ORIGINAL_LOREAU_HECTOR_ADDITIVE_IDENTITY_FAIL")
        maxdiff=max(maxdiff,diff)
        out.append({"pool":r["pool"],"rich":r["rich"],"prefix":r["prefix"],
                    "FD_high":int(r["fd"]>=3),"NDE":nde,"CE":ce,"SE":se})
    return out,maxdiff

def design(rows):
    strata=sorted({(r["pool"],r["rich"]) for r in rows})
    prefix=sorted({r["prefix"] for r in rows})
    required(len(strata)==6 and len(prefix)==3,
             "ORIGINAL_SIX_STRATA_THREE_PREFIX_DESIGN_MISSING")
    X=np.zeros((len(rows),1+5+2+1))
    for i,r in enumerate(rows):
        X[i,0]=1
        g=(r["pool"],r["rich"])
        if g!=strata[0]:X[i,strata.index(g)]=1
        if r["prefix"]!=prefix[0]:X[i,len(strata)+prefix.index(r["prefix"])-1]=1
        X[i,-1]=r["FD_high"]
    counts=collections.Counter((r["pool"],r["rich"]) for r in rows)
    w=np.array([1/counts[(r["pool"],r["rich"])] for r in rows],float)
    required(np.linalg.matrix_rank(X)==X.shape[1] and np.linalg.cond(X)<=1e8,
             "ORIGINAL_FD_CONTRAST_DESIGN_NOT_FULL_RANK")
    return X,w

def fit(rows):
    X,w=design(rows)
    wy=np.sqrt(w)
    xp=X*wy[:,None]
    out={}
    for label in ("NDE","CE","SE"):
        y=np.asarray([r[label] for r in rows],float)
        beta=np.linalg.lstsq(xp,y*wy,rcond=None)[0]
        out[label]=float(beta[-1])
    required(abs(out["NDE"]-out["CE"]-out["SE"])<1e-8*max(1,abs(out["NDE"])),
             "MODEL_PARTITION_NOT_ALGEBRAICALLY_COHERENT")
    return out

def bootstrap(rows):
    clusters=collections.defaultdict(list)
    for r in rows:clusters[(r["pool"],r["rich"],r["FD_high"])].append(r)
    required(len(clusters)==12,"ORIGINAL_FIXED_12_SOURCE_TREATMENT_CELLS_CHANGED")
    observed=fit(rows)
    draws={n:[] for n in ("NDE","CE","SE","CE_minus_SE")}
    rng=np.random.default_rng(SEED)
    failed=0
    for b in range(BOOT):
        selected=[]
        for _,cluster in sorted(clusters.items()):
            chosen=rng.integers(0,len(cluster),size=len(cluster))
            selected.extend(cluster[int(i)] for i in chosen)
        try:
            vals=fit(selected)
        except Stop:
            failed+=1;continue
        for label in ("NDE","CE","SE"):draws[label].append(vals[label])
        draws["CE_minus_SE"].append(vals["CE"]-vals["SE"])
    required(len(draws["NDE"])>=0.9*BOOT,"STRATIFIED_BOOTSTRAP_DESIGN_HOLD")
    summary={}
    for label in ("NDE","CE","SE"):
        summary[label]={"assigned_HighFD_minus_LowFD_beta_g_dry_mass_m2":observed[label],
          "paired_plot_strata_bootstrap_95CI":np.quantile(draws[label],[.025,.975]).tolist()}
    summary["CE_minus_SE"]={
        "assigned_HighFD_minus_LowFD_beta_g_dry_mass_m2":observed["CE"]-observed["SE"],
        "paired_plot_strata_bootstrap_95CI":np.quantile(draws["CE_minus_SE"],[.025,.975]).tolist()}
    return {"endpoints":summary,
        "source_partition_consistent_model_NDE_equals_CE_plus_SE":True,
        "n_bootstrap_refits":len(draws["NDE"]),
        "n_bootstrap_failed_refits":failed,
        "n_bootstrap_requested":BOOT,"seed":SEED,
        "bootstrap_source_unit":"original_plot_within_pool_richness_assignedFD",
        "new_p_values":0}

def main(path):
    report={"status":"SOURCE_OR_CE_SE_PARTITION_HOLD",
        "source_doi":DOI,
        "frozen_design_document":CONTRACT,
        "retrospective_after_previous_absolute_biomass_result":True,
        "original_v01_Block_source_gate_HOLD_preserved":True,
        "original_JEXIS_physical_block_source_HOLD_preserved":True,
        "not_pure_randomized_FD_effect":True,
        "not_independent_Wagg_original_biological_replication":True,
        "not_cross_site_or_K_to_FD_mediation":True,
        "no_original_species_plot_or_biomass_rows_exported":True}
    try:
        selected,mono,source=assemble_source()
        report["original_source_support"]=source
        part,err=partition(selected,mono)
        report["original_partition_max_absolute_identity_discrepancy"]=err
        report["response"]=bootstrap(part)
        report["status"]="JENA_TBE_2012_MONO_BASED_CE_SE_NDE_DESCRIPTIVE_PARTITION_COMPLETE"
    except (Stop,ValueError,urllib.error.HTTPError,urllib.error.URLError,
            TimeoutError,np.linalg.LinAlgError,OSError) as exc:
        report["hold_type"]=type(exc).__name__
        if isinstance(exc,Stop):report["hold_code"]=str(exc)[:110]
        if isinstance(exc,urllib.error.HTTPError):report["source_http"]=exc.code
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("JENA_TBE_2012_MONOCULTURE_LOREAU_HECTOR_VERDICT",json.dumps({
        "status":report["status"],
        "source_mono":report.get("original_source_support",{}).get("source_mono_plots"),
        "source_mix":report.get("original_source_support",{}).get("original_matched_mixplots"),
        "partition_diff_max":report.get("original_partition_max_absolute_identity_discrepancy"),
        "NDE_high_minus_low":report.get("response",{}).get("endpoints",{}).get("NDE",{}).get("assigned_HighFD_minus_LowFD_beta_g_dry_mass_m2"),
        "CE_high_minus_low":report.get("response",{}).get("endpoints",{}).get("CE",{}).get("assigned_HighFD_minus_LowFD_beta_g_dry_mass_m2"),
        "SE_high_minus_low":report.get("response",{}).get("endpoints",{}).get("SE",{}).get("assigned_HighFD_minus_LowFD_beta_g_dry_mass_m2"),
        "causal_FD_effect":False},sort_keys=True))

def test():
    M=np.array([10.,20.])
    Y=np.array([6.,8.])
    n=len(M)
    delta=Y/M-1/n
    ce=n*delta.mean()*M.mean()
    se=n*np.mean((delta-delta.mean())*(M-M.mean()))
    nde=Y.sum()-M.sum()/n
    assert abs(nde-ce-se)<1e-12
    assert nde==-1 and abs(ce)<1e-12 and abs(se+1)<1e-12
    assert BOOT==2000 and SEED==20261121
    print('{"status":"JENA_TBE_MONOCULTURE_PARTITION_SYNTHETIC_PASS","checks":4}')

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    x=p.parse_args()
    if x.self_test:test()
    elif x.out:main(x.out)
    else:p.error("Choose --self-test or --out")
