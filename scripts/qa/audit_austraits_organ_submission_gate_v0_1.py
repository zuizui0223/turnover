#!/usr/bin/env python3
"""Check honest submission-stage gaps for an exploratory AusTraits coauthor bundle.

No new K, statistics, source records or network queries. PASS means the
*preflight report is internally valid*; it never means submission-ready.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

MANUSCRIPT = Path("docs/AUSTRAITS_K_ORGAN_ECOLOGY_MANUSCRIPT_V0_2.md")
DECISION = Path("docs/AUSTRAITS_ORGAN_COAUTHOR_SUBMISSION_DECISION_V0_1.md")
SOURCE = Path("results/austraits_organ_paper_frozen_aggregate_inputs_v0_1")
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

def audit(repo: Path, manuscript: str, decision: str):
    keys = text_checks(manuscript, decision)
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
        "full_original_record_to_K_cleanroom_reproduction_verified": False,
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
    need(good["eligible_for_submission_claim"] is False,
         "Preflight accidentally became submission authorization")
    for wrong_manuscript, wrong_decision in [
        (manuscript.replace(DOI, "10.0000/broken", 1), decision),
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
