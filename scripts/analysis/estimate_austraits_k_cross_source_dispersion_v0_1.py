#!/usr/bin/env python3
"""Estimate K-blind observational/source heterogeneity by trait on exact AusTraits K core.

This is NOT a fitted measurement-error model or an OU process-null comparison.
Source-specific medians, rather than repeated individual records, are the
sampling units. No species, datasets or K values are written to the report.
"""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb
import yaml

STATUS="AUSTRAITS_K_CROSS_SOURCE_DISPERSION_ESTIMATED"
DESIGN="POST_COVERAGE_PRE_CROSS_SOURCE_DISPERSION_FROZEN"

def summarize(rows, systems, coverage, design):
    bysys=defaultdict(list)
    for sid,fam,trait,species,median_state,nsrc,source_var in rows:
        bysys[str(sid)].append((str(fam),str(trait),str(species),float(median_state),
                                int(nsrc),float(source_var) if source_var is not None else float("nan")))
    if set(bysys)!=set(systems):
        raise ValueError("source-dispersion graph differs from original exact K systems")
    out=[]
    bytrait=defaultdict(list)
    for sid,sys in sorted(systems.items()):
        rr=bysys[sid]
        if len(rr)!=sys["n_input_species"]:
            raise ValueError(f"source species support changed in {sid}: {len(rr)} != {sys['n_input_species']}")
        if any((r[0],r[1])!=(sys["family"],sys["trait_name"]) for r in rr):
            raise ValueError("source family/trait mismatch")
        if any(not (r[3]>0 and np.isfinite(r[3])) for r in rr):
            raise ValueError("nonpositive species median within original K core")
        if any(r[4]<1 for r in rr):
            raise ValueError("species has positive median but no positive source measurements")
        logmed=np.log(np.asarray([r[3] for r in rr],float))
        between=float(np.var(logmed,ddof=1))
        valid=[r[5] for r in rr if r[4]>=2]
        if not all(np.isfinite(x) and x>=0 for x in valid):
            raise ValueError("invalid cross-source log dispersion")
        within=float(np.median(valid)) if len(valid)>=5 else None
        ratio=(float(within/between)
               if within is not None and np.isfinite(between) and between>0 else None)
        if within is not None and ratio is None:
            raise ValueError("invalid interspecific log trait variance")
        row={"system_id":sid,"family":sys["family"],"trait_name":sys["trait_name"],
             "n_species":len(rr),"n_multi_positive_datasets":len(valid),
             "source_log_variance_median":within,
             "between_species_log_variance":between,
             "relative_source_dispersion":ratio,
             "calibratable":bool(ratio is not None)}
        out.append(row)
        bytrait[sys["trait_name"]].append(row)
    tr_out={}
    eligible_total=0
    for trait in sorted(bytrait):
        rr=bytrait[trait]
        rr_cal=[r for r in rr if r["calibratable"]]
        ratios=np.array([r["relative_source_dispersion"] for r in rr_cal],float)
        n_multi=sum(r["n_multi_positive_datasets"] for r in rr)
        ref=coverage["traits"][trait]
        if n_multi>ref["species_with_two_datasets"]:
            raise ValueError("positive-source replication exceeds unfiltered coverage")
        eligible=bool(ref["qualifies_source_calibration_coverage"] and
            len(rr_cal)>=3 and n_multi>=30)
        if eligible:
            eligible_total+=1
        q=np.quantile(ratios,[0.25,0.5,0.75]) if len(ratios) else None
        tr_out[trait]={
            "systems":len(rr),"family_systems_with_at_least_5_multidataset_species":len(rr_cal),
            "positive_multidataset_species":int(n_multi),
            "source_log_variance_ratio_q25":float(q[0]) if q is not None else None,
            "source_log_variance_ratio_median":float(q[1]) if q is not None else None,
            "source_log_variance_ratio_q75":float(q[2]) if q is not None else None,
            "calibratable_for_followon_process_null":eligible,
            "coverage_gate_qualifies":bool(ref["qualifies_source_calibration_coverage"])
        }
    if len(tr_out)!=13 or len(out)!=254:
        raise ValueError("unexpected trait/system count")
    return {
        "status":STATUS,"version":"v0.1","source_only_design_status":DESIGN,
        "graph":{"systems":254,"families":42,"traits":13},
        "eligible_traits":eligible_total,"traits":tr_out,
        "systems":out,
        "interpretation":"Within-species between-source log dispersion relative to within-system interspecific spread; not independent measurement error.",
        "no_K_response_used":True
    }

def main():
    ap=argparse.ArgumentParser()
    for item in ("parquet","traits-yml","core","observed-K","coverage","design","out"):
        ap.add_argument("--"+item,required=True,type=Path)
    a=ap.parse_args()
    design=json.loads(a.design.read_text())
    if design.get("status")!=DESIGN:
        raise ValueError("dispersion protocol not frozen")
    cov=json.loads(a.coverage.read_text())
    if cov.get("status")!="AUSTRAITS_K_SOURCE_REPLICATE_FEASIBILITY_AUDITED":
        raise ValueError("missing frozen coverage audit")
    k=pd.read_csv(a.__dict__["observed_K"],usecols=["system_id","family","trait_name"])
    core=pd.read_csv(a.core,usecols=["family","trait_name","n_input_species"])
    d=k.merge(core,on=["family","trait_name"],validate="one_to_one")
    if (len(d),d.family.nunique(),d.trait_name.nunique())!=(254,42,13):
        raise ValueError("K cohort changed")
    cfg=yaml.safe_load(a.__dict__["traits_yml"].read_text())["traits"]["elements"]
    systems={}
    cand=[]
    for r in d.itertuples(index=False):
        unit="" if cfg[r.trait_name].get("units") is None else str(cfg[r.trait_name]["units"]).strip()
        if not unit:
            raise ValueError("missing expected unit")
        sid=str(r.system_id)
        systems[sid]={"family":str(r.family),"trait_name":str(r.trait_name),
                      "n_input_species":int(r.n_input_species)}
        cand.append((sid,str(r.family),str(r.trait_name),unit))
    if len(systems)!=254:
        raise ValueError("duplicate original system ids")
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE candidates(system_id VARCHAR,family_name VARCHAR,trait_name VARCHAR,expected_unit VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES(?,?,?,?)",cand)
    query=r"""
    WITH base AS (
      SELECT c.system_id,c.family_name,c.trait_name,
         trim(CAST(a.genus AS VARCHAR)) genus,
         trim(CAST(a.binomial AS VARCHAR)) species,
         trim(CAST(a.dataset_id AS VARCHAR)) dataset_id,
         trim(CAST(a.observation_id AS VARCHAR)) observation_id,
         try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) value_num
      FROM read_parquet(?) a JOIN candidates c
        ON trim(CAST(a.family AS VARCHAR))=c.family_name
       AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
      WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
        AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
        AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
        AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
        AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
        AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
        AND coalesce(trim(CAST(a.unit AS VARCHAR)),'')=c.expected_unit
        AND c.expected_unit<>''
    ), dedup AS (
      SELECT DISTINCT system_id,family_name,trait_name,genus,species,
         dataset_id,observation_id,value_num
      FROM base WHERE value_num IS NOT NULL AND isfinite(value_num)
    ), states AS (
      SELECT system_id,family_name,trait_name,species,
         median(value_num) median_state
      FROM dedup
      GROUP BY system_id,family_name,trait_name,species
      HAVING count(DISTINCT genus)=1
    ), by_dataset AS (
      SELECT system_id,species,dataset_id,median(ln(value_num)) source_log_median
      FROM dedup WHERE value_num>0
      GROUP BY system_id,species,dataset_id
    ), by_species AS (
      SELECT system_id,species,
        count(*) n_positive_sources,
        var_samp(source_log_median) source_log_variance
      FROM by_dataset GROUP BY system_id,species
    )
    SELECT s.system_id,s.family_name,s.trait_name,s.species,
           s.median_state,b.n_positive_sources,b.source_log_variance
    FROM states s LEFT JOIN by_species b
      ON s.system_id=b.system_id AND s.species=b.species
    ORDER BY s.system_id,s.species
    """
    try:
        rows=con.execute(query,[str(a.parquet)]).fetchall()
    finally:
        con.close()
    result=summarize(rows,systems,cov,design)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"eligible_traits":result["eligible_traits"],
                      "n_systems":len(result["systems"])}))
if __name__=="__main__":
    main()
