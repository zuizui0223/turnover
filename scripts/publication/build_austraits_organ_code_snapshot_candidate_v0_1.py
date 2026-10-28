#!/usr/bin/env python3
"""Create an auditable, DOI-READY-ONLY, original AusTraits organ-K code bundle.

NOT a DOI deposit, journal submission, permission claim, original specimens
archive or biological validation. Sources and results are included only from
fixed publication-specific paths. No third-party flattened Parquet or RDS.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

PARQUET_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
V7_ZIP_SHA="2995fb9e5eebf9271f9241b5a6c2e2cbb7b45e8eda5ce4db43c14c68f95e2f3f"
STATUS="PASS_CODE_SNAPSHOT_CANDIDATE_ONLY_NOT_DEPOSITED"
RESULTS=(
 "austraits_organ_paper_frozen_aggregate_inputs_v0_1",
 "austraits_organ_paper_frozen_rebuild_inputs_v0_1",
 "austraits_organ_paper_original_pair_K_v0_1",
 "austraits_organ_paper_original_nonflora_K_references_v0_1",
 "austraits_organ_paper_original_254_single_K_v0_1",
 "austraits_organ_paper_public_v7_full_K_replay_v0_1",
 "austraits_organ_paper_public_v7_nonflora_3stage_replay_v0_1",
 "austraits_organ_paper_public_v7_254_single_K_replay_v0_1",
 "austraits_organ_paper_compact_source_credit_review_v0_1"
)
PUBLISHED_DOCS=(
 "AUSTRAITS_K_ORGAN_ECOLOGY_MANUSCRIPT_V0_2.md",
 "AUSTRAITS_ORGAN_K_SUPPLEMENTARY_TABLES_V0_2.md",
 "AUSTRAITS_ORGAN_COAUTHOR_SUBMISSION_DECISION_V0_1.md",
 "AUSTRAITS_ORGAN_SOURCE_CREDIT_AND_DATA_DEPOSIT_GATE_V0_1.md",
 "AUSTRAITS_ORGAN_PAPER_REPRODUCIBILITY_V0_1.md",
 "AUSTRAITS_ORGAN_PAPER_SUBMISSION_READINESS_V0_2.md",
 "AUSTRAITS_ORIGINAL_254_SINGLE_K_REPRODUCTION_V0_1.md",
 "AUSTRAITS_ORGAN_NONFLORA_SOURCE_STAGE_REBUILD_V0_1.md",
 "AUSTRAITS_ORGAN_ALL_760_RAW_K_REPRODUCTION_V0_1.md"
)

def need(ok,msg):
    if not ok:raise AssertionError(msg)

def fingerprint(data):
    return hashlib.sha256(data).hexdigest()

def source_paths(root):
    # Paper's original code and all its internal source modules, but no raw data
    # folders, transient builds or independent third-party data bundles.
    files=set()
    for folder in ("scripts/analysis","scripts/source","scripts/qa","scripts/publication"):
        base=root/folder
        for f in base.rglob("*"):
            if f.is_file() and f.suffix.lower() in (".py",".r",".cpp",".h",".hpp"):
                files.add(f.relative_to(root))
    for path in (root/"data").glob("austraits*.json"):
        files.add(path.relative_to(root))
    for pattern in ("austraits-organ-*.yml","austraits-k-*.yml",
                    "austraits-blomberg-*.yml","austraits-ou-*.yml"):
        for path in (root/".github/workflows").glob(pattern):
            files.add(path.relative_to(root))
    for name in PUBLISHED_DOCS:
        path=root/"docs"/name
        need(path.is_file(),"Manuscript/source-replay document missing: "+name)
        files.add(path.relative_to(root))
    for directory in RESULTS:
        base=root/"results"/directory
        need(base.is_dir(),"Original K/public-v7 replay archive missing: "+directory)
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in (".json",".csv",".bib",".md"):
                files.add(path.relative_to(root))
    return sorted(files,key=str)

def approved_provenance(root):
    # Verify published original K cases are actually the ones included.
    expected=[
      ("results/austraits_organ_paper_public_v7_full_K_replay_v0_1/reproduction_archive_manifest.json",
       "PASS_PERMANENT_FULL_760_CLEAN_SOURCE_K_REPLAY_ARCHIVE_V0_1"),
      ("results/austraits_organ_paper_public_v7_nonflora_3stage_replay_v0_1/nonflora_replay_archive_manifest.json",
       "PASS_DURABLE_ORIGINAL_283_142_SOURCE_STAGE_RAW_K_REPRODUCTION_ARCHIVE"),
      ("results/austraits_organ_paper_public_v7_254_single_K_replay_v0_1/all_254_single_K_replay_archive_manifest.json",
       "PASS_DURABLE_PUBLIC_V7_ORIGINAL_254_SINGLE_K_NUMERICAL_REPLAY"),
      ("results/austraits_organ_paper_compact_source_credit_review_v0_1/original_source_citation_priority_verdict.json",
       "PASS_COMPACT_DATASET_CITATION_REVIEW_INDEX_WITH_HUMAN_GATES")]
    for path,status in expected:
        o=json.loads((root/path).read_text(encoding="utf-8"))
        need(o["status"]==status,"Evidence not verified before code snapshot: "+path)
    source=json.loads((root/
        "results/austraits_organ_paper_source_citation_inventory_v0_1"
        "/original_K_source_citation_audit_verdict.json").read_text())
    need(source["original_parquet_sha256"]==PARQUET_SHA
         and source["compiled_v7_metadata_zip_sha256"]==V7_ZIP_SHA
         and source["citation_selection_currently_human_approved"] is False,
         "Original public v7/author credit provenance unknown")

def readme(sha,files):
    return """# Original AusTraits organ-K reproducibility code — REVIEW CANDIDATE ONLY

This archive is NOT deposited under a DOI and NOT a journal submission.
The real authors must check source study attribution, source-data licenses,
software ownership/permissions, journal data/metadata/code instructions,
author roles, funding, conflicts, and explicitly approve a versioned deposit.

Repository: https://github.com/zuizui0223/turnover
Paper branch: paper/austraits-organ-ecology-v0-2
Exact source code snapshot commit: """+sha+"""
External publicly available original trait data (not redistributed here):
AusTraits v7.0.0 DOI: https://doi.org/10.5281/zenodo.15718081
Original flattened Parquet SHA256: """+PARQUET_SHA+"""
Original compiled metadata ZIP SHA256: """+V7_ZIP_SHA+"""
Native V.PhyloMaker2 commit: 7af3fb5152f691af2e4ec9d5e2e467d1b50505e9
Original AusTraits source-native unit config commit:
7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c

The original calculations reproducibly matched the original historical results:
(1) 254 single-trait K reference systems across 42 families and 13 traits;
(2) 760 shared-tip pairwise K comparisons (760 S3/747 native prune PASS);
(3) 283 broader/142 strict source-dependent K pairs, with exactly 142/101
S3/native-prune common pair IDs in the three-stage source/taxon audit.

Evidence workflow URLs:
https://github.com/zuizui0223/turnover/actions/runs/40541276639
https://github.com/zuizui0223/turnover/actions/runs/39713644617
https://github.com/zuizui0223/turnover/actions/runs/39723170670
https://github.com/zuizui0223/turnover/actions/runs/40612020973

There are """+str(len(files))+""" repository files plus this README and manifest.
See docs/AUSTRAITS_ORGAN_PAPER_REPRODUCIBILITY_V0_1.md and the original
GitHub Actions workflows for the exact commands. The paper's source-credit
list is machine-generated and NOT author-approved. Blomberg K is NOT an
absolute evolutionary rate, selection regime, nor independent source validation.
The coauthor manuscript is a draft, not submitted or merged.
"""

def build(root,output,manifest,sha):
    need(re.fullmatch(r"[a-f0-9]{40}",sha),"Exact original Git SHA missing")
    approved_provenance(root)
    selected=source_paths(root)
    need(500<=len(selected)<=2000,
         "Unexpected code/data snapshot file set (check source path review)")
    hashes={}
    allowed={".py",".r",".cpp",".h",".hpp",".json",".csv",".bib",".md",".yml"}
    for path in selected:
        need(path.suffix.lower() in allowed,"Unexpected original-record binary: "+str(path))
        b=(root/path).read_bytes()
        hashes[str(path)]=fingerprint(b)
        need(len(b)<=10*1024*1024,"Single unexpectedly large repository file "+str(path))
    docs=readme(sha,selected)
    descriptor={
       "status":STATUS,"repository":"zuizui0223/turnover",
       "paper_branch":"paper/austraits-organ-ecology-v0-2",
       "snapshot_commit_sha":sha,
       "raw_data_release_DOI":"10.5281/zenodo.15718081",
       "original_parquet_sha256":PARQUET_SHA,
       "original_compiled_metadata_zip_sha256":V7_ZIP_SHA,
       "included_versioned_repository_file_sha256":hashes,
       "repository_files_included":len(hashes),
       "no_original_raw_AusTraits_measurements_bundled":True,
       "original_254_760_and_283_142_K_computations_reproduced":True,
       "underlying_source_study_independent_validation":False,
       "contributing_studies_citations_author_approved":False,
       "permanent_code_archive_DOI_issued":False,
       "all_journal_data_metadata_code_gates_met":False,
       "coauthors_approved_submission":False
    }
    outer=json.dumps(descriptor,indent=2,sort_keys=True)+"\n"
    output.parent.mkdir(parents=True,exist_ok=True)
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(outer,encoding="utf-8")
    with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in selected:
            info=zipfile.ZipInfo(str(path),date_time=(2026,10,28,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(root/path).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,
                       compresslevel=9)
        z.writestr("README_REVIEW_CANDIDATE_NOT_DEPOSITED.md",docs)
        z.writestr("SOURCE_CODE_SNAPSHOT_SHA256_MANIFEST.json",outer)
    with zipfile.ZipFile(output) as z:
        for name,hashval in hashes.items():
            need(fingerprint(z.read(name))==hashval,
                 "Original source code/derived K SHA256 changed inside reproducibility ZIP")
        need(len(z.namelist())==len(selected)+2,"Candidate code ZIP incomplete")
    print(json.dumps({"status":STATUS,"files":len(selected),
       "snapshot_commit_sha":sha,"zip_sha256":fingerprint(output.read_bytes()),
       "zip_bytes":output.stat().st_size,"data_code_deposit_approved":False}))
    return descriptor

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=Path("."))
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--commit-sha",required=True)
    a=p.parse_args()
    build(a.repo,a.output,a.manifest,a.commit_sha)
if __name__=="__main__":main()
