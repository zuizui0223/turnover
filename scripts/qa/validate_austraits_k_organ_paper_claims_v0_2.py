#!/usr/bin/env python3
"""Check a frozen AusTraits organ-K manuscript claim register.

This is a REPORTING audit only. It uses no raw traits, no rerun of models,
no outcome-dependent search, no threshold changes, and no new p values.
It checks consistency and derived *transition counts* from immutable summaries.
"""
import argparse
import json
import re
from pathlib import Path
from audit_austraits_organ_lofo_accuracy_identity_v0_1 import audit as audit_lofo_accuracy_identity

REQUIRED_CAVEATS = (
    "post-discovery", "same species", "family",
    "not an independent", "taxon", "original unequal-tip", "ou",
    "not", "source", "reproductive", "vegetative"
)
REQUIRED_LINKS = (
    "https://github.com/zuizui0223/turnover/pull/33",
    "https://doi.org/10.1073/pnas.0901635106",
    "https://doi.org/10.5281/zenodo.15718081",
    "https://doi.org/10.1038/s41597-021-01006-6",
    "https://doi.org/10.1111/j.0014-3820.2003.tb00285.x",
    "https://doi.org/10.1016/j.pld.2022.05.005",
    "https://doi.org/10.1111/j.2041-210X.2011.00169.x"
)

def require(cond, name):
    if not cond:
        raise AssertionError(name)

def flow(before, after, flips, n):
    """Net sign flows determined by win counts and total flip count."""
    require(all(isinstance(v, int) for v in (before, after, flips, n)),
            "integer counts required")
    require(0 <= before <= n and 0 <= after <= n and flips <= n and flips >= 0,
            "invalid wins, flips or sample size")
    delta = after - before
    require((flips + delta) % 2 == 0, "inconsistent flip-count parity")
    neg_to_pos = (flips + delta) // 2
    pos_to_neg = (flips - delta) // 2
    require(0 <= neg_to_pos <= n - before and 0 <= pos_to_neg <= before,
            "sign-flip directions impossible")
    require(neg_to_pos + pos_to_neg == flips, "flip arithmetic invalid")
    require(before + neg_to_pos - pos_to_neg == after,
            "net signs invalid")
    return {"vegetative_to_reproductive": neg_to_pos,
            "reproductive_to_vegetative": pos_to_neg,
            "total_reversals": flips}

def check_claims(d, manuscript=None):
    require(d["source_run_ids"]["functional_module_LOFO"] == 38686389859,
            "main paper source run not final 34-family LOFO")
    identity=audit_lofo_accuracy_identity(d)
    require(identity["status"] == "PASS_HARD_ACCURACY_IS_ALGEBRAIC_REEXPRESSION",
            "independent biology inferred from redundant LOFO accuracy")
    require(d["role"] == "REPORTING_ONLY_NO_NEW_EMPIRICAL_EFFECTS",
            "outcome firewall removed")
    n=d["phenotype_scope"]
    require(n["continuous_traits"] == 12 and
            n["matched_all_pairs_S3"] == 760 and
            n["matched_all_pairs_prune"] == 747 and
            n["families_in_LOFO"] == 42, "original matched graph mismatch")
    for tree in ("S3","prune"):
        g=n["cross_organ_"+tree]
        require(g["pairs"] <= n["matched_all_pairs_"+tree] and
                0 < g["wins"] <= g["pairs"] and g["families"]==34,
                "mismatched organ direction denominator: "+tree)
        sub=n["seed_dry_mass_excluded"][tree]
        fruit=n["fruit_vs_vegetative"][tree]
        require(0 < sub["wins"] <= sub["pairs"] <= g["pairs"],"seed-mass sensitivity invalid")
        require(0 < fruit["wins"] <= fruit["pairs"] <= g["pairs"],"fruit-only sensitivity invalid")
        pred=d["predictive_whole_family_holdout"][tree]
        require(pred["organ_accuracy"] > pred["pooled_accuracy"],
                "pooled prediction skill statement invalid")
        brier_gain=pred["pooled_brier"] - pred["organ_brier"]
        lo,hi=pred["organ_brier_gain_ci"]
        require(lo > 0 and lo < brier_gain < hi, "Brier gain must be positive with valid CI")
        require(abs(brier_gain-(0.03684 if tree=="S3" else 0.04346))<0.0002,
                "Brier magnitude not pinned")
        strict=d["strict_joint_source"][tree]
        broad=d["full_source_exclusion"][tree]
        require(strict["pairs"] <= broad["pairs"] and strict["families"] <= broad["families"],
                "wrong nested source support")
        require(strict["pairs"] == (142 if tree=="S3" else 101), "strict denominator drift")
        require(strict["wins"] == (120 if tree=="S3" else 81), "strict K sign drift")
        require(strict["family_equal_CI"][0] < strict["family_equal"] < strict["family_equal_CI"][1],
                "family-bootstrap interval inconsistent")
    transitions={}
    expected={
        "S3":[(17,6),(4,5)],
        "prune":[(7,6),(5,7)]
    }
    for tree in ("S3","prune"):
        item=d["same_pair_ID_three_stage"][tree]
        require(len(item["wins"])==3 and len(item["flip_count"])==2,
                "three-stage analysis malformed")
        require(item["wins"][-1] == d["strict_joint_source"][tree]["wins"],
                "stage 3 and strict cohort disagree")
        require(item["N"]==d["strict_joint_source"][tree]["pairs"],
                "stage 3 and strict denominator disagree")
        transitions[tree]=[]
        for i in (0,1):
            calc=flow(item["wins"][i],item["wins"][i+1],
                      item["flip_count"][i],item["N"])
            require((calc["vegetative_to_reproductive"],
                     calc["reproductive_to_vegetative"])==expected[tree][i],
                    "unexpected sign flow")
            transitions[tree].append(calc)
    orig=d["original_unequal_tip_source_OU_postdiscovery"]
    require(all(orig[k]["N"]==410 for k in ("S3","prune")),
            "original-tip OU denominator must not be matched-tip N")
    require(d["predeclared_scalar_source_OU_judgement"]==
        "RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES",
            "premature post-selected OU reversal")
    require(len(d["hard_boundaries"])>=7, "nonclaim framework missing")
    if manuscript is not None:
        m=manuscript.casefold()
        for phrase in REQUIRED_CAVEATS:
            require(phrase in m,"required limitation absent: "+phrase)
        for u in REQUIRED_LINKS:
            require(u in manuscript,"provenance link absent: "+u)
        require("110/142" in manuscript and
                "120/142" in manuscript and "81/101" in manuscript,
                "three-stage reporting omitted")
        require("17" in manuscript and "6" in manuscript and
                "4" in manuscript and "5" in manuscript,
                "S3 directional transitions missing")
        require("newly discovered subgroup" in manuscript,
                "freeze/stop disclosure absent")
        require("version v7.0.0" in m and
                "earlier database" in m and
                "original source-unit" in m,
                "versioned AusTraits data/old-descriptor distinction not documented")
        require("non-nested hypothesis selection" in m,
                "post-selected organ definition / non-nested fold caveat absent")
        require("hypothesis-selection leakage" in m,
                "LOFO selection-leakage caveat absent")
        require("not two independent" in m,
                "non-independent binary accuracy and K win evidence not acknowledged")
        require("64.47%" in manuscript and "65.46%" in manuscript,
                "LOFO original accuracy is not fully reported")
        require("half-credit" in m and "algebraically" in m,
                "identity derivation absent from biology manuscript")
    return {
        "status":"PASS_REPORTING_ONLY",
        "matched_cross_organ_S3_percent":round(100*n["cross_organ_S3"]["wins"]/
                                                n["cross_organ_S3"]["pairs"],3),
        "matched_cross_organ_prune_percent":round(100*n["cross_organ_prune"]["wins"]/
                                                   n["cross_organ_prune"]["pairs"],3),
        "claim_transition_flows":transitions,
        "LOFO_hard_accuracy_independent_K_evidence":False,
        "LOFO_identity_S3":identity["axes"]["S3"]["derived_hard_accuracy"],
        "LOFO_identity_prune":identity["axes"]["prune"]["derived_hard_accuracy"],
        "external_primary_validation":"NOT_QUALIFIED",
        "new_biological_effects":0
    }

def check_supplement_tables(d, tables):
    """Guard supplement counts and their denominators against a different source run."""
    src=d["source_run_ids"]
    require(src["functional_module_LOFO"] == 38686389859,
            "supplement no longer uses the final matched 34-family LOFO run")
    must_have=(
        "Table S1.", "Table S2.", "Table S3.",
        "non-nested", "does **not** isolate", "42 families",
        "not independent evolutionary origins"
    )
    lower=tables.casefold()
    for label in must_have:
        require(label.casefold() in lower,
                "missing supplement evidence/limitation: "+label)
    require("algebraically redundant" in lower and
            "(313 + 354/2) / 760" in tables and
            "(314 + 350/2) / 747" in tables,
            "redundant heldout hard accuracy not documented in supplement")
    p=d["phenotype_scope"]
    for tree in ("S3","prune"):
        fam=p["cross_organ_"+tree]
        source=d["full_source_exclusion"][tree]
        strict=d["strict_joint_source"][tree]
        fruit=p["fruit_vs_vegetative"][tree]
        seed_ex=p["seed_dry_mass_excluded"][tree]
        for z in (fam,source,strict,fruit,seed_ex):
            value=f'{z["wins"]}/{z["pairs"]} ({100*z["wins"]/z["pairs"]:.1f}%)'
            require(value in tables, "supplement missing source-linked pair direction: "+value)
        score=d["predictive_whole_family_holdout"][tree]
        require(f'{score["pooled_brier"]:.5f}' in tables,
                "supplement pooled Brier not matched")
        require(f'{score["organ_brier"]:.5f}' in tables,
                "supplement organ Brier not matched")
        n=d["same_pair_ID_three_stage"][tree]
        for positive in n["wins"]:
            require(f'{positive}/{n["N"]}' in tables,
                    "supplement stage numerator/denominator mismatch")
    return True


def self_test(d):
    check_claims(d)
    for invalid in (
        lambda x: x["same_pair_ID_three_stage"]["S3"]["flip_count"].__setitem__(0,22),
        lambda x: x["strict_joint_source"]["S3"].__setitem__("wins",133),
        lambda x: x.__setitem__("role","FRESH_EMPIRICAL_HYPOTHESIS_MINING"),
        lambda x: x["predictive_whole_family_holdout"]["S3"].__setitem__("organ_brier",0.42)
    ):
        mutated=json.loads(json.dumps(d))
        invalid(mutated)
        try:
            check_claims(mutated)
        except AssertionError:
            continue
        raise AssertionError("Fail-closed QA did not reject invalid claims")
    print("SELF_TEST=PASS: original + 4 deliberately corrupted reporting states rejected")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--claims",required=True,type=Path)
    parser.add_argument("--manuscript",type=Path)
    parser.add_argument("--supplementary",type=Path)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    d=json.loads(args.claims.read_text(encoding="utf-8"))
    if args.self_test:
        self_test(d)
    text=args.manuscript.read_text(encoding="utf-8") if args.manuscript else None
    verdict=check_claims(d,text)
    if args.supplementary:
        check_supplement_tables(d,args.supplementary.read_text(encoding="utf-8"))
        verdict["supplementary_tables_qa"]="PASS_COUNT_AND_INFERENCE_SCOPE"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(verdict,ensure_ascii=False))

if __name__ == "__main__":
    main()
