#!/usr/bin/env python3
"""Exploratory, paired-tip K after excluding five major electronic floras.

The biological organ grouping was discovered after the original AusTraits K.
The exact candidate list is frozen by a separate K-BLIND 760-family-pair
source-native species feasibility audit (283 qualified cross-organ pairs).

Two arms on EXACTLY the same remaining positive source-native species and
phylogeny: all contributing original sources versus all EXCEPT the five
fixed online floras. Source data are ephemeral and not uploaded as artifacts.
"""
from __future__ import annotations
import argparse,csv,json,subprocess,tempfile,math
from collections import defaultdict
from pathlib import Path
import duckdb,yaml

BATCH_STATUS="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_PAIR_BATCH_COMPLETE"
SUPPORT_STATUS="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_SOURCE_SUPPORT_AUDITED"
ORIGINAL_STATUS="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"
EXCLUDED=["ABRS_2023","NHNSW_2023","RBGV_2023","NTH_2023","SAH_2023"]


def cohort(source,original,design):
    if (design.get("status")!=
        "POST_279_K_AND_FLORA_LINEAGE_OUTCOMES_PRE_FLORA_EXCLUSION_SUPPORT_COUNTS_FROZEN"):
        raise ValueError("original five-flora source support protocol not frozen")
    if design["fixed_excluded_contributing_AusTraits_dataset_ids"]!=EXCLUDED:
        raise ValueError("electronic flora exclusion source cohort altered")
    if (source.get("status")!=SUPPORT_STATUS or
        source.get("original_pairs")!=760 or
        source.get("original_cross_organ_pairs")!=406 or
        not source.get("source_only_exclusion_supported_for_descriptive_reestimation")):
        raise ValueError("original K-blind no-flora source support not qualified")
    if original.get("status")!=ORIGINAL_STATUS or original.get("qualifying_family_trait_pairs")!=760:
        raise ValueError("original 760 K-blind same-tip reference not valid")
    original_idx={(r["family"],r["trait_A"],r["trait_B"]):r
      for r in original["family_trait_pair_support"] if r["qualifies_20_common_species"]}
    if len(original_idx)!=760:raise ValueError("original K-blind source pair identities lost")
    selected=[]
    for r in source["cross_organ_nonflora_supported_family_trait_pairs"]:
        if not r["cross_organ"] or not r["qualifies_20_no_flora_median_species"]:
            raise ValueError("non-K-blind selected cross-organ family pair")
        key=(r["family"],r["trait_A"],r["trait_B"])
        orig=original_idx.get(key)
        if orig is None or (orig["system_A"],orig["system_B"])!=(r["system_A"],r["system_B"]):
            raise ValueError("original source system identity changed")
        if orig["n_common_species_same_genus"]!=r["n_original_shared_positive_species"]:
            raise ValueError("original K-blind original common species support changed")
        selected.append({**r,
            "n_original_A":orig["n_original_A"],
            "n_original_B":orig["n_original_B"]})
    if (len(selected),len({r["family"] for r in selected}))!=(283,29):
        raise ValueError("original post-exclusion 283 pair 29-family K-blind cohort changed")
    if len({(r["family"],r["trait_A"],r["trait_B"]) for r in selected})!=283:
        raise ValueError("duplicated original fixed excluded-flora pair")
    return sorted(selected,key=lambda r:(r["family"],r["trait_A"],r["trait_B"]))


def validate_batch(batch,source,original,design):
    eligible={(r["family"],r["trait_A"],r["trait_B"]):r for r in cohort(source,original,design)}
    if not batch:raise ValueError("empty source-only K batch")
    seen=set()
    for r in batch:
        key=(r["family"],r["trait_A"],r["trait_B"])
        if key in seen or key not in eligible or r!=eligible[key]:
            raise ValueError("duplicate, outcome-adjusted or unidentified nonflora K pair")
        seen.add(key)
    return True


def reconstruct_native_states(parquet,trait_yaml,batch):
    cfg=yaml.safe_load(Path(trait_yaml).read_text())["traits"]["elements"]
    systems={}
    for z in batch:
        for side in ("A","B"):
            sid=z["system_"+side]
            meta={"family":z["family"],"trait":z["trait_"+side],
                  "n_orig":int(z["n_original_"+side])}
            if sid in systems and systems[sid]!=meta:
                raise ValueError("original original-tip trait support changes between pairs")
            systems[sid]=meta
    cand=[]
    for sid,s in systems.items():
        unit=cfg[s["trait"]].get("units")
        if not unit or not str(unit).strip():raise ValueError("missing exact native source trait unit")
        cand.append((sid,s["family"],s["trait"],str(unit).strip()))
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE candidate (sid VARCHAR,family VARCHAR,trait VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO candidate VALUES(?,?,?,?)",cand)
    con.execute("CREATE TEMP TABLE pairs(family VARCHAR,trait_A VARCHAR,trait_B VARCHAR,system_A VARCHAR,system_B VARCHAR)")
    con.executemany("INSERT INTO pairs VALUES(?,?,?,?,?)",[
      (r["family"],r["trait_A"],r["trait_B"],r["system_A"],r["system_B"]) for r in batch])
    con.execute("CREATE TEMP TABLE excluded(dataset_id VARCHAR)")
    con.executemany("INSERT INTO excluded VALUES(?)",[(x,) for x in EXCLUDED])
    try:
        con.execute(r"""
        CREATE TEMP TABLE dedup AS
        WITH base AS (
          SELECT c.sid,c.family,c.trait,
            trim(CAST(v.genus AS VARCHAR)) genus,
            trim(CAST(v.binomial AS VARCHAR)) species,
            trim(CAST(v.dataset_id AS VARCHAR)) dataset_id,
            trim(CAST(v.observation_id AS VARCHAR)) observation_id,
            try_cast(trim(CAST(v.value AS VARCHAR)) AS DOUBLE) val,
            c.unit expected_unit,
            coalesce(trim(CAST(v.unit AS VARCHAR)),'') source_unit
          FROM read_parquet(?) v
          JOIN candidate c ON trim(CAST(v.family AS VARCHAR))=c.family
             AND trim(CAST(v.trait_name AS VARCHAR))=c.trait
          WHERE lower(trim(CAST(v.taxon_rank AS VARCHAR)))='species'
             AND v.genus IS NOT NULL AND trim(CAST(v.genus AS VARCHAR))<>''
             AND v.binomial IS NOT NULL AND trim(CAST(v.binomial AS VARCHAR))<>''
             AND v.dataset_id IS NOT NULL AND trim(CAST(v.dataset_id AS VARCHAR))<>''
             AND v.observation_id IS NOT NULL AND trim(CAST(v.observation_id AS VARCHAR))<>''
             AND v.value IS NOT NULL AND trim(CAST(v.value AS VARCHAR))<>''
        )
        SELECT DISTINCT sid,family,trait,genus,species,dataset_id,observation_id,val
        FROM base
        WHERE val IS NOT NULL AND isfinite(val)
          AND expected_unit<>'' AND source_unit=expected_unit
        """,[str(parquet)])
        con.execute("""
        CREATE TEMP TABLE original AS
        SELECT sid,family,trait,species,min(genus) genus,median(val) AS full_state
        FROM dedup GROUP BY sid,family,trait,species
        HAVING count(DISTINCT genus)=1 AND median(val)>0
        """)
        original_counts=dict(con.execute("SELECT sid,count(*) FROM original GROUP BY sid").fetchall())
        if original_counts!={sid:int(s["n_orig"]) for sid,s in systems.items()}:
            raise ValueError("not original K native unit positive species per system")
        con.execute("""
        CREATE TEMP TABLE retained_nonflora AS
        WITH retained AS (
          SELECT d.sid,d.family,d.trait,d.species,
               min(d.genus) AS genus,median(d.val) AS nonflora_state
          FROM dedup d
          LEFT JOIN excluded f ON d.dataset_id=f.dataset_id
          WHERE f.dataset_id IS NULL
          GROUP BY d.sid,d.family,d.trait,d.species
          HAVING count(DISTINCT d.genus)=1 AND median(d.val)>0
        )
        SELECT n.sid,n.family,n.trait,n.species,n.genus,n.nonflora_state
        FROM retained n
        JOIN original o ON o.sid=n.sid AND o.species=n.species AND o.genus=n.genus
        """)
        result=con.execute("""
          SELECT p.family,p.trait_A,p.trait_B,p.system_A,p.system_B,
                 nA.species,nA.genus,
                 fA.full_state,fB.full_state,nA.nonflora_state,nB.nonflora_state
          FROM pairs p
          JOIN retained_nonflora nA ON nA.sid=p.system_A
          JOIN retained_nonflora nB ON nB.sid=p.system_B
             AND nA.species=nB.species AND nA.genus=nB.genus
          JOIN original fA ON fA.sid=p.system_A AND fA.species=nA.species AND fA.genus=nA.genus
          JOIN original fB ON fB.sid=p.system_B AND fB.species=nA.species AND fB.genus=nA.genus
          ORDER BY p.family,p.trait_A,p.trait_B,nA.species
        """).fetchall()
        return result
    finally:con.close()


def write_ephemeral(rows,batch,tmp):
    by=defaultdict(list)
    for fam,a,b,sa,sb,species,genus,fullA,fullB,nonA,nonB in rows:
        by[(fam,a,b)].append((sa,sb,species,genus,fullA,fullB,nonA,nonB))
    manifest=[]
    for i,z in enumerate(batch,1):
        key=(z["family"],z["trait_A"],z["trait_B"])
        rr=by.get(key,[])
        n=int(z["n_nonflora_positive_median_shared_species"])
        if n<20 or len(rr)!=n:
            raise ValueError("K source data did not reproduce frozen nonflora species count")
        if any((r[0],r[1])!=(z["system_A"],z["system_B"]) for r in rr):
            raise ValueError("pair system IDs corrupted")
        if any(not all(math.isfinite(float(q)) and q>0 for q in r[4:]) for r in rr):
            raise ValueError("non-positive source-native median after five-flora removal")
        file=Path(tmp)/f"Q{i:03d}.csv"
        with file.open("w",newline="",encoding="utf-8") as h:
            w=csv.writer(h)
            w.writerow(("family","genus","species","all_A","all_B","source_A","source_B"))
            w.writerows((z["family"],genus,sp,fullA,fullB,nonA,nonB)
                    for sa,sb,sp,genus,fullA,fullB,nonA,nonB in rr)
        manifest.append({
           "pair_id":f"Q{i:03d}","family":z["family"],
           "trait_A":z["trait_A"],"trait_B":z["trait_B"],
           "system_A":z["system_A"],"system_B":z["system_B"],
           "n_initial_nonflora_positive_median_species":n,
           "n_nonflora_positive_species":n,
           "n_lost_after_source_median":0,
           "status":"READY",
           "state_table":str(file)})
    return manifest


def validate_result(result,manifest):
    if result.get("status")!=BATCH_STATUS or len(result.get("pairs",[]))!=len(manifest):
        raise ValueError("nonflora native K batch incomplete")
    if not result.get("NOT_independent_primary_measurement_validation"):
        raise ValueError("false non-flora independent primary measurements asserted")
    original={i["pair_id"]:i for i in manifest}
    if len(original)!=len(manifest):raise ValueError("pair IDs are not unique")
    seen=set()
    for x in result["pairs"]:
        pid=x["pair_id"];z=original.get(pid)
        if z is None or pid in seen:raise ValueError("nonflora original source identity failed")
        seen.add(pid)
        for field in ("family","trait_A","trait_B","system_A","system_B"):
            if x.get(field)!=z[field]:raise ValueError("source K original pair trait identity changed")
        if x.get("n_nonflora_positive_species")!=z["n_nonflora_positive_species"]:
            raise ValueError("nonflora K original eligible species count changed")
        for axis in ("S3","prune_only"):
            q=x["axes"][axis]
            if q["status"]!="PASS":
                if not q["status"].startswith("HOLD_"):raise ValueError("invalid native phylogeny HOLD")
                continue
            if q["n_tips"]<20 or q["n_tips"]>z["n_nonflora_positive_species"]:
                raise ValueError("nonflora K phylogeny tip support changed")
            for field in ("K_full_A","K_full_B","K_source_A","K_source_B"):
                if not math.isfinite(float(q[field])) or float(q[field])<=0:
                    raise ValueError("non-positive/native K response")
            if not math.isclose(math.log(q["K_full_A"]/q["K_full_B"]),
                                 q["delta_full"],abs_tol=2e-9):
                raise ValueError("original all-source same-tip K contrast arithmetic changed")
            if not math.isclose(math.log(q["K_source_A"]/q["K_source_B"]),
                                q["delta_source"],abs_tol=2e-9):
                raise ValueError("nonflora same-tip K contrast arithmetic changed")
            if not math.isclose(q["delta_source"]-q["delta_full"],
                                q["delta_source_measurements"],abs_tol=2e-9):
                raise ValueError("nonflora original paired source-only K effect changed")
    return True


def main():
    p=argparse.ArgumentParser()
    for v in ("batch-json","nonflora-support","original-pair-support",
              "parquet","traits-yml","design","r-script","out"):
        p.add_argument("--"+v,required=True,type=Path)
    a=p.parse_args()
    source=json.loads(a.__dict__["nonflora_support"].read_text())
    original=json.loads(a.__dict__["original_pair_support"].read_text())
    design=json.loads(a.design.read_text())
    batch=json.loads(a.__dict__["batch_json"].read_text())
    validate_batch(batch,source,original,design)
    rows=reconstruct_native_states(a.parquet,a.__dict__["traits_yml"],batch)
    with tempfile.TemporaryDirectory(prefix="K_5_floras_removed_") as td:
        manifest=write_ephemeral(rows,batch,td)
        fm=Path(td)/"manifest.json";fm.write_text(json.dumps(manifest))
        resultfile=Path(td)/"result.json"
        subprocess.run(["Rscript",str(a.__dict__["r_script"]),
                         "--manifest",str(fm),"--out",str(resultfile)],check=True)
        result=json.loads(resultfile.read_text())
        validate_result(result,manifest)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":BATCH_STATUS,
         "n_pairs":len(result["pairs"]),
         "S3_valid":sum(r["axes"]["S3"]["status"]=="PASS" for r in result["pairs"]),
         "prune_valid":sum(r["axes"]["prune_only"]["status"]=="PASS" for r in result["pairs"])}))

if __name__=="__main__":main()
