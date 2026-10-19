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

REQUIRED_CAVEATS = (
    "post-discovery", "same species", "family",
    "not an independent", "taxon", "original unequal-tip", "ou",
    "not", "source", "reproductive", "vegetative"
)
REQUIRED_LINKS = (
    "https://github.com/zuizui0223/turnover/pull/33",
    "https://doi.org/10.1073/pnas.0901635106"
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
        require("non-nested hypothesis selection" in m,
                "post-selected organ definition / non-nested fold caveat absent")
        require("hypothesis-selection leakage" in m,
                "LOFO selection-leakage caveat absent")
    return {
        "status":"PASS_REPORTING_ONLY",
        "matched_cross_organ_S3_percent":round(100*n["cross_organ_S3"]["wins"]/
                                                n["cross_organ_S3"]["pairs"],3),
        "matched_cross_organ_prune_percent":round(100*n["cross_organ_prune"]["wins"]/
                                                   n["cross_organ_prune"]["pairs"],3),
        "claim_transition_flows":transitions,
        "external_primary_validation":"NOT_QUALIFIED",
        "new_biological_effects":0
    }

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
    parser.add_argument("--output",type=Path)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    d=json.loads(args.claims.read_text(encoding="utf-8"))
    if args.self_test:
        self_test(d)
    text=args.manuscript.read_text(encoding="utf-8") if args.manuscript else None
    verdict=check_claims(d,text)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(verdict,ensure_ascii=False))

if __name__ == "__main__":
    main()
