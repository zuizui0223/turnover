#!/usr/bin/env python3
"""Freeze provenance of complete original broad/strict nonflora K computational replay.

Original K/trait outcomes are not re-fit by this script; complete source-native
batch results and numeric QA are copied by SHA256 only after independent checks.
"""
import argparse,hashlib,json,math,shutil
from pathlib import Path

EXPECTED_RUN=39723170670
SOURCE_REF=Path("results/austraits_organ_paper_original_nonflora_K_references_v0_1/original_nonflora_reference_manifest.json")
ORIGINAL_PARQUET_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
STATUS="PASS_ALL_283_142_NONFLORA_K_AND_THREE_STAGE_TRANSITIONS_REPRODUCED"
ARCHIVE_STATUS="PASS_DURABLE_ORIGINAL_283_142_SOURCE_STAGE_RAW_K_REPRODUCTION_ARCHIVE"

def must(ok,why):
    if not ok:raise AssertionError(why)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def preserve(root,verdict,target,run_id):
    must(run_id==EXPECTED_RUN,"The archived run is not the verified original full nonflora replay")
    m=json.loads(SOURCE_REF.read_text())
    must(m["status"]=="PASS_PERMANENT_AUSTRAITS_ORIGINAL_NONFLORA_SOURCE_K_REFERENCE"
         and m["original_public_v7_sha256"]==ORIGINAL_PARQUET_SHA,
         "Original source K reference manifest changed")
    v=json.loads(verdict.read_text())
    must(v["status"]==STATUS and v["source_release"]=="AusTraits v7.0.0"
         and v["original_public_parquet_sha256"]==ORIGINAL_PARQUET_SHA,
         "Source-restricted exact K reproducibility verdict not qualified")
    expected={"broad":{"n_qualified":283,"axes":{"S3":{"pass":283,"hold":0},
                                                 "prune_only":{"pass":233,"hold":50}}},
              "strict":{"n_qualified":142,"axes":{"S3":{"pass":142,"hold":0},
                                                  "prune_only":{"pass":101,"hold":41}}}}
    for arm,item in expected.items():
        got=v["source_arms"][arm]
        must(got["n_qualified"]==item["n_qualified"],"Full original K population changed")
        for ax,val in item["axes"].items():
            must(all(got["axes"][ax][k]==num for k,num in val.items()),
                 "Original nonflora S3/prune K graph invalid")
    expected_stage={"S3":(142,[110,121,120],[23,9]),
                    "prune_only":(101,[82,83,81],[13,12])}
    for ax,(n,wins,flips) in expected_stage.items():
        z=v["three_stage_identical_pair_contrasts"][ax]
        must(z["same_original_pair_identities"]==n and
             z["reproductive_K_wins"]==wins and
             z["source_tip_then_value_sign_flips"]==flips,
             "Original 3-stage source/taxon observed result did not reproduce")
    discrepancy=float(v["maximum_absolute_source_K_or_logK_discrepancy"])
    must(math.isfinite(discrepancy) and 0<=discrepancy<=2e-8,
         "Unexpected K discrepancy outside audit absolute tolerance")
    must(v["independent_original_measurement_replication"] is False and
         v["new_evolutionary_process_parameter_tests"]==0,
         "This is not independent source biological validation")
    named={f"{arm}_B{k:02d}_{extension}.json"
           for arm,n in (("broad",16),("strict",12))
           for k in range(1,n+1)
           for extension in ("fresh","audit")}
    existing={p.name for p in root.iterdir() if p.is_file()}
    must(existing==named,"Expected exactly 28 K plus 28 audit files")
    target.mkdir(parents=True,exist_ok=True)
    sums={t:{"n":0,"S3":0,"prune_only":0} for t in ("broad","strict")}
    hashes={}
    for file in sorted(named):
        src=root/file; raw=src.read_bytes()
        obj=json.loads(raw)
        arm=file.split("_")[0]
        if file.endswith("_fresh.json"):
            must(obj["no_species_observation_IDs_or_raw_trait_measurements_persisted"] is True,
                 "Source values or specimen IDs were not filtered")
            must(len(obj["pairs"])>0,"Original K batch empty")
            for row in obj["pairs"]:
                must(not any(f in row for f in
                             ("binomial","species","dataset_id","observation_id","raw_value")),
                     "Original measurements leaked into archive")
            sums[arm]["n"]+=len(obj["pairs"])
        else:
            must(obj["status"]=="PASS_ORIGINAL_NONFLORA_SOURCE_K_BATCH_NUMERIC_REGRESSION",
                 "Batch numerical comparison was not passed")
            for ax in ("S3","prune_only"):
                sums[arm][ax]+=obj["axes"][ax]["pass"]
        dest=target/file
        if dest.exists():must(dest.read_bytes()==raw,"Permanent source-K replay file differs")
        else:shutil.copyfile(src,dest)
        hashes[file]=sha(raw)
    must(sums=={"broad":{"n":283,"S3":283,"prune_only":233},
                "strict":{"n":142,"S3":142,"prune_only":101}},
         "28 K batches do not sum to original source-support denominators")
    dest=target/"nonflora_K_three_stage_verdict.json"
    if dest.exists():must(dest.read_bytes()==verdict.read_bytes(),"Final source/tip verdict changed")
    else:shutil.copyfile(verdict,dest)
    hashes[dest.name]=sha(dest.read_bytes())
    report={"status":ARCHIVE_STATUS,"workflow_run_id":run_id,
            "source_verification_run_url":
               "https://github.com/zuizui0223/turnover/actions/runs/39723170670",
            "original_nonflora_reference_manifest_sha256":sha(SOURCE_REF.read_bytes()),
            "original_AusTraits_parquet_sha256":ORIGINAL_PARQUET_SHA,
            "source_arms":v["source_arms"],
            "three_stage_identical_pair_contrasts":v["three_stage_identical_pair_contrasts"],
            "maximum_absolute_numeric_discrepancy":discrepancy,
            "n_original_pair_fits_freshly_computed":425,
            "n_original_real_tree_K_passes":{"S3":425,"prune_only":334},
            "preserved_file_sha256":hashes,"n_preserved_files":len(hashes),
            "underlying_original_study_independence_proven":False,
            "new_K_effects_fitted_by_this_archiver":0,
            "original_species_level_values_committed":False}
    dest=target/"nonflora_replay_archive_manifest.json"
    txt=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if dest.exists():must(dest.read_text()==txt,"Repeat archive lacks byte reproducibility")
    else:dest.write_text(txt)
    return report

def main():
    p=argparse.ArgumentParser()
    for k in ("source-dir","verdict","out-dir"):
        p.add_argument("--"+k,type=Path,required=True)
    p.add_argument("--run-id",type=int,required=True)
    a=p.parse_args()
    r=preserve(a.source_dir,a.verdict,a.out_dir,a.run_id)
    print(json.dumps({"status":r["status"],
                      "files":r["n_preserved_files"],
                      "pairs":r["n_original_pair_fits_freshly_computed"],
                      "maximum_abs":r["maximum_absolute_numeric_discrepancy"]}))
if __name__=="__main__":main()
