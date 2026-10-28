#!/usr/bin/env python3
"""Pin three already-published AusTraits paper aggregate results in git.

These are immutable, already-opened descriptive output summaries, NOT new
measurement records, species matrices, K fits or external data. Every byte is
checked against original Actions artifacts' SHA256 before publication. The
underlying AusTraits v7.0.0 data and rights remain at original provider DOI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
from pathlib import Path

FROZEN = {
 "reproductive_vegetative_lofo.json": {
    "sha256":"7648ff07a734b96686629d9d158c215670bccbcdec7c6cf385aae9a11a76cfa1",
    "run_id":38686389859,"artifact":"austraits-k-reproductive-vegetative-lofo-v0-1",
    "status":"AUSTRAITS_K_REPRODUCTIVE_VEGETATIVE_LOFO_EXPLORATORY_V0_1",
 },
 "nonflora_283_to_142_source_support_transition.json": {
    "sha256":"5cba03348e4c2342db2e1df202c6036b6b265a829ac43e816388f9f84cc79397",
    "run_id":39202352075,"artifact":"austraits-k-283-to-142-cohort-transition-v0-1",
    "status":"AUSTRAITS_K_NONFLORA_COHORT_TRANSITION_EXPLORATORY_VERIFIED",
 },
 "joint_nonflora_shared_source_K.json": {
    "sha256":"fc9bc62297a16db916f21704203ab1859f65dce33303a8199cb49a6596819dbb",
    "run_id":39006469805,"artifact":"austraits-k-joint-nonflora-shared-dataset-142-final-v0-1",
    "status":"AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_SENSITIVITY_AGGREGATED_V0_1",
 },
}

def check(condition,description):
    if not condition: raise RuntimeError(description)

def audit_archive(root,output=None):
    hashes={}
    results={}
    for name,descriptor in FROZEN.items():
        path=root/name
        check(path.is_file(),"Frozen archive missing: "+name)
        b=path.read_bytes()
        check(len(b)>1000 and len(b)<800000,
              "Original aggregate source file unexpected size: "+name)
        digest=hashlib.sha256(b).hexdigest()
        check(digest==descriptor["sha256"],
              "Original trusted SHA256 mismatch: "+name)
        data=json.loads(b)
        check(data.get("status")==descriptor["status"],"Original archive status drift: "+name)
        # Reject exact raw-taxon/observation keys, not explanatory metadata
        # such as 'pair_level_K_decisions_no_species_names'.
        check(all(('"' + key + '":') not in b.decode("utf-8").lower()
                  for key in ("species_name","observation_id","binomial","trait_value","raw_value")),
              "Potential original specimen-level identifiers require manual authorization")
        hashes[name]=digest
        results[name]=data
    a=results["reproductive_vegetative_lofo.json"]
    check(a.get("no_raw_trait_values_species_ids_exported") is True,
          "Original module archive does not affirm no raw trait values/species")
    check(a.get("independent_TRY_v7_validation") is False,
          "Unexpected false claim of source independence")
    for axis,n,k,win in (("S3",406,760,313),("prune_only",397,747,314)):
        d=a["reproductive_vegetative_matched_tip"][axis]
        check(d["n_supported_family_pair_observations"]==n and
              d["n_reproductive_K_higher"]==win and
              a["source_data_provenance"]["source_eligible_family_pair_comparisons"]==760,
              "Original matched K counts changed")
        p=a["left_one_whole_family_out_prediction"][axis]["all_source_eligible_pairs"]["scores"]
        check(p["reproductive_vegetative"]["heldout_family_pair_rows"]==k,
              "Original LOFO denominator changed")
    b=results["nonflora_283_to_142_source_support_transition.json"]
    check(b.get("not_new_evolutionary_process_hypothesis_or_independent_external_validation") is True,
          "Original transition source independent-validation caveat disappeared")
    c=results["joint_nonflora_shared_source_K.json"]
    check(c.get("not_external_TRY_v7_independent_source_validation") is True,
          "Original strict source archive falsely claimed independent validation")
    for axis,n,w in (("S3",142,120),("prune_only",101,81)):
        check(b["axes"][axis]["n_pair_identities"]==n,
              "Staged original pair identities changed")
        check(b["axes"][axis]["stage_rates"]["same_dataset_eligible_tips_identical_dataset_medians"]
              ["n_reproductive_K_higher"]==w,"Staged original wins drift")
        check(c["axes"][axis]["n_valid_real_tree_K_pairs"]==n,
              "Strict original K native-support drift")
    manifest={
      "status":"PASS_IMMUTABLE_AGGREGATE_PAPER_INPUTS",
      "created_by":"scripts/publication/freeze_austraits_organ_aggregate_archives_v0_1.py",
      "published_in":"zuizui0223/turnover paper/austraits-organ-ecology-v0-2",
      "original_source_workflow_runs":{name:descr["run_id"] for name,descr in FROZEN.items()},
      "original_GitHub_artifact_names":{name:descr["artifact"] for name,descr in FROZEN.items()},
      "file_sha256":hashes,
      "no_new_biological_effects":True,
      "raw_measurements_included":False,
      "original_hypothesis_post_discovery":True,
      "independent_primary_data_replication":False,
      "raw_release":"AusTraits v7.0.0, Zenodo DOI 10.5281/zenodo.15718081, CC BY with source attribution",
      "note":"Versioned aggregate-only outputs, for durable figure regeneration after GitHub Actions artifact expiry. Biological/OU/trait results unmodified."
    }
    if output:
        output.mkdir(parents=True,exist_ok=True)
        for name in FROZEN:
            src=root/name
            target=output/name
            if src.resolve()!=target.resolve():
                shutil.copyfile(src,target)
        (output/"frozen_input_manifest.json").write_text(
            json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return manifest

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--inputs",required=True,type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    print(json.dumps(audit_archive(args.inputs,args.output),indent=2))

if __name__=="__main__":main()
