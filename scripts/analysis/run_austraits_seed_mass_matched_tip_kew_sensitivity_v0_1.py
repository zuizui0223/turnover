#!/usr/bin/env python3
"""Build exact original AusTraits seed-mass shared-tip states, excluding Kew
observations only in the sensitivity arm, and run matched-tree R K contrasts.

A post-discovery source robustness check, NOT independent TRY replication or
a new prospective hypothesis. Species/raw values stay runner-local, never in
the uploaded JSON artifact.
"""
from __future__ import annotations
import argparse,csv,json,subprocess,tempfile
from pathlib import Path
from collections import defaultdict
import pandas as pd
import duckdb,yaml

STATUS="AUSTRAITS_SEED_MASS_MATCHED_TIP_KEW_SENSITIVITY_REESTIMATED"
DESIGN="POST_ORIGINAL_K_AND_SOURCE_SUPPORT_PRE_MATCHED_TIP_K_SENSITIVITY_OUTCOME_FROZEN"

def read_support(path):
    obj=json.loads(Path(path).read_text())
    if (obj.get("status")!="AUSTRAITS_SEED_MASS_NO_KEW_SOURCE_SUPPORT_AUDITED"
        or obj.get("original_graph")!={"systems":254,"families":42,"traits":13}
        or obj.get("original_seed_mass_families")!=15
        or obj.get("families_with_at_least_20_remaining_seed_mass_species")!=13):
        raise ValueError("original no-Kew supported family cohort not fixed")
    return {x["family"]:x for x in obj["family_support"]}

def prepare(effects,core,units,design,support):
    if design.get("status")!=DESIGN:raise ValueError("matched tip K sensitivity not frozen")
    K=pd.read_csv(effects)
    core=pd.read_csv(core,usecols=["family","trait_name","n_input_species"])
    if (len(K),K.family.nunique(),K.trait_name.nunique())!=(254,42,13):
        raise ValueError("changed original K graph")
    kd=K[K.trait_name=="seed_dry_mass"]
    if (len(kd),kd.family.nunique())!=(15,15):
        raise ValueError("original seed mass K graph changed")
    joined=kd.merge(core,on=["family","trait_name"],validate="one_to_one")
    if len(joined)!=15 or set(joined.family)!=set(support):
        raise ValueError("original and no-Kew family supports disagree")
    cfg=yaml.safe_load(Path(units).read_text())["traits"]["elements"]
    unit=cfg["seed_dry_mass"].get("units")
    if not unit or not str(unit).strip():raise ValueError("native seed dry mass unit missing")
    rows=[]
    expected={}
    for z in joined.itertuples(index=False):
        fam=str(z.family);sid=str(z.system_id)
        if int(z.n_input_species)!=support[fam]["n_original_species"]:
            raise ValueError("changed family-specific original seed support")
        expected[sid]={"family":fam,"n_original":int(z.n_input_species),
                       "n_retained":support[fam]["n_non_kew_positive_median_species"],
                       "support_eligible":support[fam]["meets_20_species_descriptive_gate"],
                       "original_S3_K":float(z.S3_K),
                       "original_prune_K":float(z.prune_K)}
        rows.append((sid,fam,"seed_dry_mass",str(unit).strip()))
    return rows,expected

def recover_states(parquet,candidates):
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE candidates (system_id VARCHAR,family VARCHAR,trait VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES (?,?,?,?)",candidates)
    sql=r"""
    WITH base AS (
       SELECT c.system_id,c.family,
          trim(CAST(a.genus AS VARCHAR)) genus,
          trim(CAST(a.binomial AS VARCHAR)) species,
          trim(CAST(a.dataset_id AS VARCHAR)) dataset_id,
          trim(CAST(a.observation_id AS VARCHAR)) observation_id,
          try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) value_num,
          c.unit expected_unit,
          coalesce(trim(CAST(a.unit AS VARCHAR)),'') source_unit
       FROM read_parquet(?) a JOIN candidates c
         ON trim(CAST(a.family AS VARCHAR))=c.family
        AND trim(CAST(a.trait_name AS VARCHAR))=c.trait
       WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
         AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
         AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
         AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
         AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
         AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
    ), dedup AS (
       SELECT DISTINCT system_id,family,genus,species,dataset_id,observation_id,value_num
       FROM base
       WHERE value_num IS NOT NULL AND isfinite(value_num)
         AND expected_unit<>'' AND source_unit=expected_unit
    ), full_states AS (
       SELECT system_id,family,species,min(genus) genus,
          median(value_num) original_state
       FROM dedup GROUP BY system_id,family,species
       HAVING count(DISTINCT genus)=1 AND median(value_num)>0
    ), no_kew_states AS (
       SELECT system_id,family,species,min(genus) genus,
          median(value_num) nonkew_state
       FROM dedup WHERE dataset_id<>'Kew_2019_1'
       GROUP BY system_id,family,species
       HAVING count(DISTINCT genus)=1 AND median(value_num)>0
    )
    SELECT f.system_id,f.family,f.genus,f.species,
       f.original_state,n.nonkew_state
    FROM full_states f LEFT JOIN no_kew_states n
      ON f.system_id=n.system_id AND f.species=n.species
    ORDER BY f.system_id,f.species
    """
    try:rows=con.execute(sql,[str(parquet)]).fetchall()
    finally:con.close()
    return rows

def validate_states_and_write(rows,expected,local_dir):
    groups=defaultdict(list)
    for sid,fam,genus,species,old,new in rows:
        groups[str(sid)].append((str(fam),str(genus),str(species),
                                 float(old),None if new is None else float(new)))
    if set(groups)!=set(expected):raise ValueError("not all original 15 systems represented")
    inputs=[]
    for sid,meta in sorted(expected.items()):
        observed=groups[sid]
        if len(observed)!=meta["n_original"]:
            raise ValueError(f"original seed species count changed in {sid}")
        retained=[a for a in observed if a[4] is not None]
        if len(retained)!=meta["n_retained"]:
            raise ValueError(f"original no-Kew retained support changed in {sid}")
        if bool(len(retained)>=20)!=bool(meta["support_eligible"]):
            raise ValueError("unexpected 20-species gate status")
        if not meta["support_eligible"]:
            continue
        path=Path(local_dir)/f"{sid}.csv"
        with path.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=["family","genus","species","original_state","nonkew_state"])
            w.writeheader()
            for fam,genus,species,old,new in retained:
                if fam!=meta["family"] or not (old>0 and new>0):
                    raise ValueError("source trait identity or positivity changed")
                w.writerow({"family":fam,"genus":genus,"species":species,
                            "original_state":old,"nonkew_state":new})
        inputs.append((sid,meta,path))
    if len(inputs)!=13:raise ValueError("expected exactly 13 pre-K selected families")
    return inputs

def aggregate(responses,expected):
    if len(responses)!=13:raise ValueError("incomplete no-Kew sensitivity")
    seen=set()
    byaxis={"S3":[],"prune_only":[]}
    for z in responses:
        if z.get("status")!="AUSTRAITS_SEED_MASS_MATCHED_TIP_K_PAIR_CALCULATED":
            raise ValueError("wrong matched-tree source K result")
        sid=z["system_id"]
        if sid in seen or sid not in expected:raise ValueError("duplicate/unknown matched K system")
        seen.add(sid)
        if z["family"]!=expected[sid]["family"] or z["n_retained_source_species"]!=expected[sid]["n_retained"]:
            raise ValueError("K source family/count changed")
        for axis in byaxis:
            d=z["axes"][axis]
            if d["status"]=="PASS":
                if d["n_tips"]<20:raise ValueError("under-supported K axis accepted")
                byaxis[axis].append({"system_id":sid,"family":z["family"],
                    "n_tips":d["n_tips"],
                    "delta_source_logK":d["delta_source_logK"],
                    "delta_support_geometry_logK":d["delta_support_geometry_logK"],
                    "delta_total_logK":d["delta_total_logK"],
                    "K_full_sources_matched_tips":d["K_full_sources_matched_tips"],
                    "K_nonkew_matched_tips":d["K_nonkew_matched_tips"]})
            elif not d["status"].startswith("HOLD_"):
                raise ValueError("unrecognized matched K axis verdict")
    import numpy as np
    summary={}
    for axis,rr in byaxis.items():
        vals=np.asarray([x["delta_source_logK"] for x in rr],float)
        summary[axis]={
          "n_paired_supported_families":len(rr),
          "n_axis_holds":13-len(rr),
          "source_delta_logK_median":float(np.median(vals)) if len(vals) else None,
          "source_delta_logK_mean":float(np.mean(vals)) if len(vals) else None,
          "source_delta_logK_min":float(np.min(vals)) if len(vals) else None,
          "source_delta_logK_max":float(np.max(vals)) if len(vals) else None,
          "n_source_delta_positive":int((vals>0).sum()),
          "n_source_delta_negative":int((vals<0).sum()),
          "families":rr
        }
    return {
      "version":"v0.1","status":STATUS,
      "source_only_support_families_before_K":13,
      "study_trait":"seed_dry_mass",
      "axes":summary,
      "not_independent_validation":True,
      "not_preoriginal_K_registered":True,
      "selection_parameters_or_process_null_changed":False,
      "trait_values_or_species_ids_persisted":False,
      "scientific_boundary":"Matched-tip source-composition sensitivity on original AusTraits data only; neither independence from historical TRY measurements nor trait-specific selection follows."
    }

def main():
    p=argparse.ArgumentParser()
    for flag in ("parquet","core","observed-K","traits-yml","support","design",
                 "r-script","out"):
        p.add_argument("--"+flag,required=True,type=Path)
    a=p.parse_args()
    design=json.loads(a.design.read_text())
    support=read_support(a.support)
    candidates,expected=prepare(a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],design,support)
    states=recover_states(a.parquet,candidates)
    with tempfile.TemporaryDirectory(prefix="aust_kew_same_tips_") as td:
        inputs=validate_states_and_write(states,expected,td)
        completed=[]
        for sid,meta,f in inputs:
            dest=Path(td)/f"{sid}.json"
            subprocess.run([
              "Rscript",str(a.__dict__["r_script"]),
              "--states",str(f),"--system-id",sid,"--family",meta["family"],
              "--original-K-S3",str(meta["original_S3_K"]),
              "--original-K-prune",str(meta["original_prune_K"]),
              "--out",str(dest)
            ],check=True)
            completed.append(json.loads(dest.read_text()))
    result=aggregate(completed,expected)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,
       "S3":{k:v for k,v in result["axes"]["S3"].items() if k!="families"},
       "prune":{k:v for k,v in result["axes"]["prune_only"].items() if k!="families"}},sort_keys=True))
if __name__=="__main__":main()
