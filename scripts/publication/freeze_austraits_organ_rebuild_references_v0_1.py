#!/usr/bin/env python3
"""Freeze original aggregate-only core/K/support records; never raw measurements."""
import argparse,csv,hashlib,json,shutil
from pathlib import Path

RUNS={"core_systems.csv":37561341286,"original_K_effects.csv":37725935020,
      "shared_taxon_pair_support.json":38673955087}
SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
BAN={"binomial","species","species_id","species_name","genus","dataset_id",
     "observation_id","raw_value","value","measurement","specimen_id","taxon_id"}

def need(test,message):
    if not test:raise AssertionError(message)

def table(path,require_k):
    with path.open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f)
        need(rd.fieldnames,"CSV header absent")
        cols=set(rd.fieldnames)
        need(not({c.lower() for c in cols}&BAN),"Raw observation columns not allowed")
        rows=list(rd)
    need(len(rows)>=254,"Original source core or K graph has fewer than 254 rows")
    key={(r["family"],r["trait_name"]) for r in rows}
    need(len(key)==len(rows),"Original family/trait systems not unique")
    if require_k:
        need(len(rows)==254 and len({z[0] for z in key})==42
             and len({z[1] for z in key})==13,"Frozen 254-system K graph drift")
    return rows,key,cols

def freeze(core,effects,support,design,out):
    c,cids,ccols=table(core,False)
    k,kids,kcols=table(effects,True)
    need(kids<=cids,"Original K system graph not contained in source core")
    c={ (r["family"],r["trait_name"]):r for r in c }
    need(all(int(c[key]["n_input_species"])>=20 for key in kids),
         "K subset includes unsupported source core")
    need("n_input_species" in ccols,"Original support count missing")
    need({"system_id","S3_K","prune_K"}<=kcols,"Original native K fields missing")
    need(len({r["system_id"] for r in k})==254,"Duplicate system K")
    need(all(int(x["n_input_species"])>=20 for x in c.values()),
         "Original core includes unsupported system")
    need(all(float(x["S3_K"])>0 and float(x["prune_K"])>0 for x in k),"Invalid original K")
    s=json.loads(support.read_text())
    d=json.loads(design.read_text())
    need(d["source"]["source_parquet_sha256"]==SHA,"Source Parquet hash changed")
    need(d["status"]=="POST_EMPIRICAL_K_AND_SOURCE_DIAGNOSTICS_PRE_SHARED_TAXON_OVERLAP_RESULTS_FROZEN",
         "Original design status changed")
    need(s["status"]=="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED",
         "Original support audit status changed")
    need(s["original_graph"]=={"systems":254,"families":42,"traits":13},
         "Original core graph changed")
    need(s["named_graph"]=={"systems":249,"families":42,"traits":12},
         "Named trait subset changed")
    need(s["qualifying_family_trait_pairs"]==760 and len(s["trait_pairs"])==66,
         "760/66 support contract violated")
    need(s["no_species_or_trait_values_persisted"] is True,"Support contains raw data")
    allrows=s["family_trait_pair_support"]
    selected=[x for x in allrows if x["qualifies_20_common_species"]]
    need(len(selected)==760 and all(x["n_common_species_same_genus"]>=20 for x in selected),
         "Matched support qualification changed")
    need(all((x["family"],x["trait_A"]) in kids and (x["family"],x["trait_B"]) in kids
             for x in allrows),"Pair refs absent from original system graph")
    need(all(not any(field in x for field in ("species","genus","binomial",
              "dataset_id","observation_id","raw_value","value")) for x in allrows),
         "Source support includes prohibited measurement field")
    src={"core_systems.csv":core,"original_K_effects.csv":effects,
         "shared_taxon_pair_support.json":support}
    out.mkdir(parents=True,exist_ok=True)
    for name,f in src.items():
        dest=out/name
        if dest.exists():
            need(dest.read_bytes()==f.read_bytes(),"Frozen source bytes changed: "+name)
        else:shutil.copyfile(f,dest)
    hashes={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in src}
    result={
        "status":"PASS_FROZEN_ORIGINAL_AGGREGATE_REBUILD_REFERENCES_V0_1",
        "source_release":"AusTraits v7.0.0",
        "source_parquet_sha256":SHA,
        "original_source_workflow_runs":RUNS,
        "source_byte_sha256":hashes,
        "original_systems":254,"original_families":42,"original_traits":13,
        "full_source_core_systems":len(c),
        "matched_supported_pairs":760,"named_pair_types":66,
        "raw_species_or_measurement_values_included":False,
        "new_K_or_phylogeny_models_fitted":0,
        "independent_primary_source_replication":False,
        "full_raw_to_K_reproduction_already_verified":False,
        "note":"Original aggregate core/K/support snapshots; public Parquet/units and pinned tree are external dependencies."
    }
    manifest=out/"frozen_rebuild_manifest.json"
    txt=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if manifest.exists():
        need(manifest.read_text()==txt,"Original source manifest changed")
    else:manifest.write_text(txt)
    return result

def main():
    p=argparse.ArgumentParser()
    for a in ("core","effects","support","design","out-dir"):
        p.add_argument("--"+a,required=True,type=Path)
    a=p.parse_args()
    r=freeze(a.core,a.effects,a.support,a.design,a.__dict__["out_dir"])
    print(json.dumps({"status":r["status"],"hashes":r["source_byte_sha256"],
                      "pairs":r["matched_supported_pairs"]}))
if __name__=="__main__":main()
