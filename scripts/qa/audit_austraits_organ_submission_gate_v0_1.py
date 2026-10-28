#!/usr/bin/env python3
"""Check honest submission-stage gaps for an exploratory AusTraits coauthor bundle.

No new K, statistics, source records or network queries. PASS means the
*preflight report is internally valid*; it never means submission-ready.
"""
from __future__ import annotations

import argparse
import csv
import copy
import hashlib
import json
import re
from pathlib import Path

MANUSCRIPT = Path("docs/AUSTRAITS_K_ORGAN_ECOLOGY_MANUSCRIPT_V0_2.md")
DECISION = Path("docs/AUSTRAITS_ORGAN_COAUTHOR_SUBMISSION_DECISION_V0_1.md")
SOURCE = Path("results/austraits_organ_paper_frozen_aggregate_inputs_v0_1")
REPLAY = Path("results/austraits_organ_paper_public_v7_full_K_replay_v0_1")
REQUIRED_CODE = (
    "scripts/analysis/fit_austraits_k_shared_taxon_pairs_v0_1.R",
    "scripts/analysis/run_austraits_k_shared_taxon_pairs_batch_v0_1.py",
    "scripts/analysis/render_austraits_organ_k_paper_figures_v0_2.py",
    "scripts/qa/audit_austraits_organ_lofo_accuracy_identity_v0_1.py",
)
REQUIRED_ORIGINAL_RUNS = (38686389859, 39202352075, 39006469805)
DOI = "10.5281/zenodo.15718081"

def need(condition, description):
    if not condition:
        raise AssertionError(description)

def text_checks(manuscript: str, decision: str):
    need(DOI in manuscript and "v7.0.0" in manuscript,
         "Manuscript lost exact source-release citation")
    need("313/406" in manuscript and "314/397" in manuscript,
         "Manuscript lost primary matched-tip observations")
    need("110/142" in manuscript and "120/142" in manuscript and
         "81/101" in manuscript, "Manuscript lost source/taxon stage results")
    need("post-discovery" in manuscript.casefold() and
         "non-nested hypothesis selection" in manuscript.casefold(),
         "Post-selection caveats missing")
    need("283 broader nonflora and 142 strict" in manuscript and
         "283/142 nonflora source-stage K" in decision and
         "same AusTraits" in decision,
         "Complete original nonflora source-stage K numerical evidence or inference limits missing")
    need("760 original matched-tip K comparisons" in manuscript and
         "760-pair K rerun" in decision and "same AusTraits" in decision,
         "Complete paired K technical reproduction and original-source limitations missing")
    need("original 254 single-trait K" in manuscript and
         "254 original single-trait K" in decision and
         "same original AusTraits" in manuscript,
         "Full historical single-system 254 K evidence or original-data limit missing")
    need("23,122 (73.6%)" in manuscript and
         "44 DatasetIDs" in manuscript and "190 DatasetIDs" in manuscript and
         "51 distinct citation keys" in manuscript and
         "190 DatasetID" in decision and "original contributing-study" in decision.lower(),
         "Original source concentration/citation gaps or original-study limits missing")
    need("Data Accessibility Statement" in manuscript,
         "Candidate venue requires Data Accessibility Statement wording")
    need("not" in manuscript.casefold() and
         "full species-by-measurement matrix" in manuscript,
         "Analytic data availability caveat missing")
    match = re.search(r"^\*\*Keywords:\*\*\s*(.*?)\s*$", manuscript, re.MULTILINE)
    need(match is not None, "No explicit keyword line")
    keywords = [s.strip() for s in match.group(1).rstrip(".").split(";")]
    need(4 <= len(keywords) <= 6 and
         all(2 <= len(x) <= 60 for x in keywords) and
         len({x.casefold() for x in keywords}) == len(keywords),
         "Keyword count, uniqueness or length outside 4-6 candidate-venue requirement")
    need("COAUTHOR REVIEW ONLY" in decision and
         "NOT SUBMISSION AUTHORIZATION" in decision and
         "still OPEN" in decision and
         "data, metadata and code at submission" in decision,
         "Decision memo overstates submission readiness or loses data gate")
    need("https://onlinelibrary.wiley.com/page/journal/20457758/homepage/forauthors.html" in decision,
         "Official candidate journal source missing")
    return keywords

def validate_full_replay(repo: Path):
    """Verify durable clean-source K replay without authorizing journal submission."""
    home = repo / REPLAY
    m = json.loads((home / "reproduction_archive_manifest.json").read_text(encoding="utf-8"))
    need(m["status"] == "PASS_PERMANENT_FULL_760_CLEAN_SOURCE_K_REPLAY_ARCHIVE_V0_1",
         "Full native K reproducibility archive invalid")
    need(m["original_actions_run_id"] == 39713644617
         and m["n_recomputed_original_pairs"] == 760,
         "Full original comparison population missing")
    expected = {"S3": {"pass": 760, "hold": 0, "cross": 406, "wins": 313},
                "prune_only": {"pass": 747, "hold": 13, "cross": 397, "wins": 314}}
    need(m["native_axes"] == expected, "Full source-to-K original denominator mismatch")
    need(m["max_absolute_numeric_K_or_logK_difference"] == 0.0,
         "Historical K numerical discrepancy is not the verified exact zero")
    need(m["complete_clean_source_K_replay"] is True
         and m["independent_biological_source_validation"] is False
         and m["raw_species_measurements_committed"] is False,
         "Archive confuses computational reproduction with biological replication")
    hashes = m["permanent_file_sha256"]
    names = {f"B{b:02d}_{kind}.json"
             for b in range(1, 25) for kind in ("fresh", "audit")}
    names.add("all_760_native_K_regression.json")
    need(set(hashes) == names and len(hashes) == m["files_permanently_preserved"] == 49,
         "Full run is missing original 24 K/24 QA/1 aggregate files")
    for name, expected_sha in hashes.items():
        need((home / name).is_file(), "Reproduced K file absent: " + name)
        need(hashlib.sha256((home / name).read_bytes()).hexdigest() == expected_sha,
             "Full public-source K replay was silently changed: " + name)
    result = json.loads((home / "all_760_native_K_regression.json").read_text())
    need(result["status"] == "PASS_ALL_760_RAW_SOURCE_K_RECOMPUTED_AND_MATCHED"
         and result["axes"] == expected
         and result["original_source_qualified_pairs"] == 760
         and result["max_absolute_numeric_K_or_logK_difference"] == 0.0
         and result["independent_original_measurement_replication"] is False,
         "Final clean-source K evidence changed")
    return m

def validate_nonflora_full_replay(repo: Path):
    """Confirm exact full 283/142 source K and original bootstrap SHA256 evidence."""
    base = repo / Path("results/austraits_organ_paper_public_v7_nonflora_3stage_replay_v0_1")
    prior = repo / Path("results/austraits_organ_paper_original_nonflora_K_references_v0_1")
    m = json.loads((base / "nonflora_replay_archive_manifest.json").read_text())
    need(m["status"] == "PASS_DURABLE_ORIGINAL_283_142_SOURCE_STAGE_RAW_K_REPRODUCTION_ARCHIVE"
         and m["workflow_run_id"] == 39723170670
         and m["n_original_pair_fits_freshly_computed"] == 425
         and m["n_original_real_tree_K_passes"] == {"S3": 425, "prune_only": 334}
         and m["maximum_absolute_numeric_discrepancy"] == 0.0,
         "Historical 283/142 original nonflora source-stage K replay not verified")
    need(m["original_nonflora_reference_manifest_sha256"] ==
         hashlib.sha256((prior / "original_nonflora_reference_manifest.json").read_bytes()).hexdigest(),
         "Original source-restricted K reference archive is not byte-exact")
    sources = json.loads((prior / "public_raw_nonflora_support_reproduction_v0_1.json").read_text())
    need(sources["status"] == "PASS_PUBLIC_AUSTRAITS_V7_REBUILT_NONFLORA_283_142_K_BLIND_SUPPORT"
         and sources["original_source_only_support_sha256"] ==
         sources["reconstructed_source_only_support_sha256"]
         and sources["same_nonflora_DatasetID_supported_comparisons"] == 142,
         "Original K-blind source/taxon eligibility not reproduced from public v7")
    stages = {"S3": (142, [110, 121, 120], [23, 9]),
              "prune_only": (101, [82, 83, 81], [13, 12])}
    for axis, (n, wins, flips) in stages.items():
        v = m["three_stage_identical_pair_contrasts"][axis]
        need(v["same_original_pair_identities"] == n
             and v["reproductive_K_wins"] == wins
             and v["source_tip_then_value_sign_flips"] == flips,
             "Original same-identity three-stage K rank changes were altered")
    expected = {f"{arm}_B{i:02d}_{suffix}.json"
                for arm, n in (("broad", 16), ("strict", 12))
                for i in range(1, n+1)
                for suffix in ("fresh", "audit")}
    expected.update(("nonflora_K_three_stage_verdict.json",
                     "broad_283_aggregate.json", "strict_142_aggregate.json",
                     "recomputed_3stage_transition.json"))
    hashes = m["preserved_file_sha256"]
    need(set(hashes) == expected and len(hashes) == m["n_preserved_files"] == 60,
         "Complete source-stage 28 K, 28 audits, 3 aggregates and verdict missing")
    for filename, digest in hashes.items():
        file = base / filename
        need(file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest() == digest,
             "Permanent clean-source nonflora K result SHA256 mismatch: " + filename)
    final = json.loads((base / "nonflora_K_three_stage_verdict.json").read_text())
    need(final["status"] == "PASS_ALL_283_142_NONFLORA_K_AND_THREE_STAGE_TRANSITIONS_REPRODUCED"
         and final["maximum_absolute_source_K_or_logK_discrepancy"] == 0.0
         and final["independent_original_measurement_replication"] is False
         and final["new_evolutionary_process_parameter_tests"] == 0,
         "Original nonflora source-stage numeric replay or noncausal scope changed")
    need(m["underlying_original_study_independence_proven"] is False
         and m["original_species_level_values_committed"] is False,
         "Misrepresented original study independence or raw-source redistribution")
    return m


def validate_original_254_single_K_replay(repo: Path):
    """SHA256-check clean-runtime original 254 phytools K, not independent biology."""
    root = repo / Path("results/austraits_organ_paper_public_v7_254_single_K_replay_v0_1")
    original = repo / Path("results/austraits_organ_paper_original_254_single_K_v0_1")
    m = json.loads((root / "all_254_single_K_replay_archive_manifest.json").read_text())
    original_bytes = (original / "original_single_K_archive_manifest.json").read_bytes()
    need(m["status"] == "PASS_DURABLE_PUBLIC_V7_ORIGINAL_254_SINGLE_K_NUMERICAL_REPLAY"
         and m["original_full_clean_source_R_K_workflow_run_id"] == 40541276639
         and m["original_K_systems_recomputed"] == 254
         and m["original_families"] == 42 and m["original_traits"] == 13
         and m["original_historical_single_K_manifest_sha256"] ==
             hashlib.sha256(original_bytes).hexdigest()
         and m["reported_max_abs_numeric_K_or_logK_discrepancy"] == 0.0
         and m["all_original_S3_prune_native_tips_reproduced"] is True
         and m["independent_source_R_K_execution_complete"] is True,
         "Original 254 single-trait K clean-source numerical verification absent")
    need(m["source_species_measurement_rows_persisted"] is False
         and m["independent_primary_measurement_validation"] is False
         and m["new_biological_hypothesis_tests"] == 0
         and m["explicit_author_submitting_approved"] is False,
         "Source-K computation was mislabelled as independent biological confirmation")
    prior = json.loads(original_bytes)
    names = set(prior["historical_k_source_file_sha256"])
    need(len(names) == 254, "Original per-system K source reference incomplete")
    names.update(f"K{i:02d}_audit.json" for i in range(1,17))
    names.add("all_254_original_single_trait_K_verdict.json")
    hashes = m["all_K_and_QA_file_sha256"]
    need(set(hashes) == names and m["n_source_K_replay_files"] == len(names) == 271,
         "254 new K outputs, 16 QA and final R K verdict not all preserved")
    for name, expected in hashes.items():
        path = root / name
        need(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected,
             "Historical 254 phytools K recomputation file SHA256 mismatch: " + name)
    result = json.loads((root / "all_254_original_single_trait_K_verdict.json").read_text())
    need(result["status"] == "PASS_PUBLIC_V7_ALL_254_ORIGINAL_PHYTOOLS_SINGLE_K_REBUILT"
         and result["original_single_trait_system_count"] == 254
         and result["original_families"] == 42 and result["original_named_traits"] == 13
         and result["all_16_original_K_batches_recomputed_and_numerically_checked"] is True
         and result["all_original_native_S3_prune_tip_counts_reproduced"] is True
         and result["max_absolute_numeric_K_or_logK_discrepancy"] == 0.0
         and result["independent_biological_original_study_replication"] is False,
         "Final original single-trait 254 phytools K numerical result drift")
    return m


def validate_original_source_credit_audit(repo: Path):
    """Verify real original-v7 DatasetID and BibTeX coverage without author approval."""
    original = repo / Path("results/austraits_organ_paper_source_citation_inventory_v0_1")
    compact = repo / Path("results/austraits_organ_paper_compact_source_credit_review_v0_1")
    a = json.loads((original / "original_K_source_citation_audit_verdict.json").read_text())
    need(a["status"] ==
         "PASS_PUBLIC_V7_ORIGINAL_K_CONTRIBUTING_SOURCE_INVENTORY_WITH_HUMAN_ATTRIBUTION_GAPS"
         and a["original_fixed_qualified_systems"] == 254
         and a["original_matched_pair_identities"] == 760
         and a["original_strict_source_pair_identities"] == 142
         and a["no_raw_species_names_observation_ids_trait_values_exported"] is True
         and a["no_new_K_or_biological_models_fitted"] is True
         and a["citation_selection_currently_human_approved"] is False,
         "Original v7 source attribution cohort or scientific caveat changed")
    by_tier = a["exposure_by_original_K_analysis_tier"]
    need(by_tier["original_254_systems"]["n_distinct_datasets"] == 190
         and by_tier["original_760_matched_pairs"]["n_distinct_datasets"] == 190
         and by_tier["strict_142_same_DatasetID"]["n_distinct_datasets"] == 44
         and by_tier["strict_142_same_DatasetID"][
             "n_original_deduplicated_measurement_rows_in_qualified_states"] == 31401,
         "Original source DatasetID/row exposure no longer matches published audit")
    for name, expected_sha in a["aggregate_inventory_files_sha256"].items():
        p = original / name
        need(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == expected_sha,
             "Original v7 source citation/record exposure was changed: " + name)
    c = json.loads((compact / "original_source_citation_priority_verdict.json").read_text())
    need(c["status"] == "PASS_COMPACT_DATASET_CITATION_REVIEW_INDEX_WITH_HUMAN_GATES"
         and c["original_source_audit_sha256"] ==
             hashlib.sha256((original / "original_K_source_citation_audit_verdict.json").read_bytes()).hexdigest()
         and c["all_original_K_dataset_ids"] == 190
         and c["source_DatasetIDs_in_strict_142_K"] == 44
         and c["n_compact_dataset_credit_review_rows"] == 190
         and c["original_citation_roles_review_rows"] == 299
         and c["source_reference_BibTeX"]["n_source_bibtex_entries_exported"] == 247
         and len(c["source_reference_BibTeX"]["unresolved_source_bibtex_keys"]) == 51
         and c["missing_primary_citation_datasets"] == 0,
         "Original public-v7 source bibliography review changed")
    need(c["citation_selection_author_confirmed"] is False
         and c["journal_citable_code_DOI_created"] is False
         and c["journal_full_data_metadata_requirements_verified"] is False
         and c["no_original_source_species_or_observation_ids_or_values_released"] is True
         and c["no_new_evolutionary_process_or_K_fits"] is True,
         "Original source citation review is not human approval or journal readiness")
    for name, expected_sha in c["files_sha256"].items():
        p = compact / name
        need(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == expected_sha,
             "Source-credit BibTeX/index SHA256 changed: " + name)
    with (compact / "dataset_priority_and_credit_gaps.csv").open(
            newline="",encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    p0=[r for r in rows if r["review_priority"] == "P0_STRICT_142"]
    need(len(rows) == 190 and len(p0) == 44,
         "Manuscript strict source credit priority does not match original 142 cohort")
    top=sorted(p0,key=lambda r:-int(r["n_source_rows_strict_142"]))[:5]
    need([r["dataset_id"] for r in top] == [
         "Kooyman_2011", "Maslin_2012", "Cooper_2013",
         "GrassBase_2014", "Everingham_2020"]
         and sum(int(r["n_source_rows_strict_142"]) for r in top) == 23122,
         "Original public-v7 five-source concentration changed")
    flags={}
    for label in ("UNRESOLVED_BIBTEX_REFERENCE",
                  "SECONDARY_OR_ORIGINAL_DATASET_CREDIT_NEEDED",
                  "MULTIPLE_SOURCE_IDS"):
        flags[label] = sum(label in r["source_attribution_review_flags"] for r in p0)
    need(flags == {"UNRESOLVED_BIBTEX_REFERENCE":11,
                   "SECONDARY_OR_ORIGINAL_DATASET_CREDIT_NEEDED":8,
                   "MULTIPLE_SOURCE_IDS":4},
         "Original strict 44 source-credit outstanding review cases changed")
    return {"dataset_ids_in_original_760":190,
            "dataset_ids_in_strict_142":44,
            "strict_original_source_rows":31401,
            "top_five_source_rows":23122,
            "unresolved_original_BibTeX_keys":51,
            "strict_dataset_flags":flags,
            "human_approved_bibliography":False,
            "journal_citable_code_DOI_created":False}


def audit(repo: Path, manuscript: str, decision: str):
    keys = text_checks(manuscript, decision)
    full_replay = validate_full_replay(repo)
    nonflora_replay = validate_nonflora_full_replay(repo)
    singles = validate_original_254_single_K_replay(repo)
    source_credit = validate_original_source_credit_audit(repo)
    source_dir = repo / SOURCE
    manifest_path = source_dir / "frozen_input_manifest.json"
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = m["file_sha256"]
    need(len(files) == 3, "Original source file set changed")
    for name, expected in files.items():
        need(re.fullmatch(r"[a-f0-9]{64}", expected) is not None, "Invalid hash")
        path = source_dir / name
        need(path.is_file(), "Frozen source file is missing: " + name)
        need(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
             "Frozen source file was modified: " + name)
    runs = set(m.get("original_source_workflow_runs", {}).values())
    need(runs == set(REQUIRED_ORIGINAL_RUNS),
         "Source run IDs changed")
    for item in REQUIRED_CODE:
        need((repo / item).is_file(), "Primary reproducibility script missing: " + item)
    return {
        "status": "PASS_EDITORIAL_PREFLIGHT_WITH_HUMAN_SUBMISSION_BLOCKERS",
        "eligible_for_submission_claim": False,
        "candidate_journal_not_author_approved": "Ecology and Evolution",
        "source": "AusTraits v7.0.0 / DOI " + DOI,
        "journal_requirements_page": "https://onlinelibrary.wiley.com/page/journal/20457758/homepage/forauthors.html",
        "keyword_count": len(keys),
        "keywords": keys,
        "permanent_aggregate_file_sha256_validated": len(files),
        "original_source_runs_validated": sorted(runs),
        "checked_original_code_file_count": len(REQUIRED_CODE),
        "aggregate_figures_reproducible": True,
        "full_original_record_to_K_cleanroom_reproduction_verified": True,
        "all_three_original_K_computational_pipelines_cleanruntime_reproduced": True,
        "all_760_original_matched_tip_K_computations_cleanroom_reproduced": True,
        "full_760_original_matched_tip_K_max_absolute_discrepancy": full_replay["max_absolute_numeric_K_or_logK_difference"],
        "original_nonflora_283_142_source_K_cleanroom_reproduced": True,
        "original_nonflora_K_max_absolute_numeric_discrepancy": nonflora_replay["maximum_absolute_numeric_discrepancy"],
        "original_254_single_trait_K_reference_independently_recomputed": True,
        "original_254_single_trait_K_max_absolute_numeric_difference": singles["reported_max_abs_numeric_K_or_logK_discrepancy"],
        "original_v7_contributing_source_attribution_inventory_verified": True,
        "original_dataset_ids_in_matched_K": source_credit["dataset_ids_in_original_760"],
        "original_dataset_ids_in_strict_142": source_credit["dataset_ids_in_strict_142"],
        "unresolved_original_BibTeX_citation_keys": source_credit["unresolved_original_BibTeX_keys"],
        "author_approved_original_source_bibliography": False,
        "permanent_citable_analysis_code_DOI_created": False,
        "independent_primary_study_biological_replication": False,
        "journal_complete_data_metadata_code_access_verified": False,
        "approved_authors_correspondence": False,
        "approved_competing_interests_funding_contributions": False,
        "journal_venue_confirmed_by_authors": False,
        "explicit_author_submission_authorization": False,
        "new_biological_estimates": 0,
        "unresolved_human_gates": [
            "scientific coauthor sign-off",
            "full analytic data and metadata plus code for referee review",
            "original contributing-source citation rights and credit",
            "complete authorship, contributions, funding and conflict statements",
            "selected target journal and possible APC funding",
            "explicit permission to submit"
        ]
    }

def self_test(repo, manuscript, decision):
    good = audit(repo, manuscript, decision)
    need(good["full_original_record_to_K_cleanroom_reproduction_verified"] is True
         and good["all_three_original_K_computational_pipelines_cleanruntime_reproduced"] is True
         and good["original_254_single_trait_K_reference_independently_recomputed"] is True
         and good["independent_primary_study_biological_replication"] is False,
         "Technical original K reproducibility confused with independent ecological evidence")
    need(good["original_v7_contributing_source_attribution_inventory_verified"] is True
         and good["author_approved_original_source_bibliography"] is False
         and good["permanent_citable_analysis_code_DOI_created"] is False,
         "Original-data citation audit incorrectly claims author approval or a code DOI")
    need(good["eligible_for_submission_claim"] is False,
         "Preflight accidentally became submission authorization")
    for wrong_manuscript, wrong_decision in [
        (manuscript.replace(DOI, "10.0000/broken"), decision),
        (manuscript.replace("**Keywords:**", "**Tags:**", 1), decision),
        (manuscript, decision.replace("NOT SUBMISSION AUTHORIZATION", "SUBMISSION APPROVED", 1)),
    ]:
        try:
            text_checks(wrong_manuscript, wrong_decision)
        except AssertionError:
            continue
        raise AssertionError("Preflight did not reject mutated claim/approval")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, default=Path("."))
    p.add_argument("--manuscript", type=Path, default=MANUSCRIPT)
    p.add_argument("--decision", type=Path, default=DECISION)
    p.add_argument("--output", type=Path)
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    manuscript = (a.repo / a.manuscript).read_text(encoding="utf-8")
    decision = (a.repo / a.decision).read_text(encoding="utf-8")
    if a.self_test:
        self_test(a.repo, manuscript, decision)
    result = audit(a.repo, manuscript, decision)
    rendered = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "eligible_for_submission_claim": result["eligible_for_submission_claim"],
        "keyword_count": result["keyword_count"],
        "unresolved_human_gate_count": len(result["unresolved_human_gates"])
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
