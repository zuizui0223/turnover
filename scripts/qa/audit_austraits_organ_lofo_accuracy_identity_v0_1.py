#!/usr/bin/env python3
"""Audit that organ-only LOFO HARD ACCURACY adds no independent binary evidence.

Uses only the already-published AusTraits aggregate counts and the frozen
algorithmic scoring semantics; NO trait observations, new K, model fit,
hypothesis search, independent-source lookup or p-value is allowed.

The model is a one-coefficient no-intercept signed organ contrast, fitted
by L2 logistic regression; all within-organ inputs are x=0 -> p=0.5 and
receive 0.5 accuracy credit for a tie. When each family is held out,
the cross-organ training margin is positive. The sign of every fitted
coefficient therefore remains positive, regardless of its magnitude.
Consequently accuracy is EXACTLY (reproductive wins + half same-module
rows)/all eligible rows. Accuracy is not an additional independent
cross-family replication of the post-selected organ phenotype pattern.
Brier probabilities ARE distinct numerical predictions and remain
conditional-on-post-selection probabilistic prediction-score diagnostics.
"""
import argparse
import json
from pathlib import Path

EXPECTED = {
    "S3": {
        "total": 760, "cross": 406, "reproductive_wins": 313,
        "reported_LOFO_accuracy_rounded": .6447,
        "reported_pooled_accuracy_rounded": .5263,
    },
    "prune": {
        "total": 747, "cross": 397, "reproductive_wins": 314,
        "reported_LOFO_accuracy_rounded": .6546,
        "reported_pooled_accuracy_rounded": .5382,
    }
}

def require(test, label):
    if not test:
        raise AssertionError(label)

def audit(registry):
    require(registry.get("role") == "REPORTING_ONLY_NO_NEW_EMPIRICAL_EFFECTS",
            "Not a frozen reporting-only claim registry")
    scope=registry["phenotype_scope"]
    scores=registry["predictive_whole_family_holdout"]
    require(scope["continuous_traits"]==12 and scope["families_in_LOFO"]==42,
            "Unexpected original organ classification/scoring cohort")
    require(
        registry["source_run_ids"]["functional_module_LOFO"]==38686389859,
        "Not the final complete 34-family LOFO result archive"
    )
    axes={}
    for axis, exp in EXPECTED.items():
        cross=scope["cross_organ_"+axis]
        n=scope["matched_all_pairs_"+axis]
        wins=cross["wins"]
        cross_n=cross["pairs"]
        require((n,cross_n,wins)==
            (exp["total"],exp["cross"],exp["reproductive_wins"]),
            "Original cross-organ cohort or source K direction changed: "+axis)
        within=n-cross_n
        losses=cross_n-wins
        margin=wins-losses
        # A family contributes no more than 6 reproductive x 6 vegetative
        # unique named trait-pairs; each family×named-pair appears once.
        max_cross_pairs_one_family=6*6
        lower_train_margin=margin-max_cross_pairs_one_family
        require(lower_train_margin > 0,
                "Positive training logit sign is not guaranteed after family holdout: "+axis)
        # In no-intercept 1-D ridge logistic regression on x in {-1,0,+1},
        # sign(beta) == sign(sum(x_i*(y_i-.5))) if nonzero, regardless of
        # penalty C>0. With the chosen x coding, this is 0.5*(wins-losses).
        # Therefore for EVERY held-out fold the sign is positive.
        tie_credit=within*0.5
        expected_hard=(wins+tie_credit)/n
        observed=scores[axis]["organ_accuracy"]
        require(abs(expected_hard-observed) <= 0.000051,
                "Heldout hard accuracy is not its deterministic organ-count identity: "+axis)
        require(abs(observed-exp["reported_LOFO_accuracy_rounded"])<1e-8,
                "Archived conditional reported accuracy changed")
        require(scores[axis]["pooled_brier"]>scores[axis]["organ_brier"],
                "Separate probability-score improvement changed")
        axes[axis]={
            "n_total_original_named_pair_rows": n,
            "n_cross_organ_rows": cross_n,
            "n_same_organ_rows": within,
            "reproductive_higher_cross_organ_rows": wins,
            "vegetative_higher_cross_organ_rows": losses,
            "cross_organ_reproductive_win_fraction": wins/cross_n,
            "half_credit_same_organ_ties": tie_credit,
            "derived_hard_correct_credit": wins+tie_credit,
            "derived_hard_accuracy": expected_hard,
            "original_reported_conditional_LOFO_accuracy": observed,
            "difference_only_roundoff": expected_hard-observed,
            "max_cross_organ_pairs_per_heldout_family": max_cross_pairs_one_family,
            "training_reproductive_minus_vegetative_margin_lower_bound":
                lower_train_margin,
            "nonredundant_brier_gain_vs_pooled":
                scores[axis]["pooled_brier"]-scores[axis]["organ_brier"]
        }
    return {
        "status": "PASS_HARD_ACCURACY_IS_ALGEBRAIC_REEXPRESSION",
        "source_k_study": "AusTraits v7.0.0 post-discovery organ classification",
        "reference_code": "scripts/analysis/audit_austraits_k_functional_module_lofo_v0_1.py",
        "exact_scoring_semantics": (
            "single signed contrast +/-1 for between-organ and zero for "
            "within-organ, no-intercept L2 logistic with C=1, and half-credit "
            "for p=0.5 hard-label ties"
        ),
        "axes": axes,
        "interpretation": (
            "The 64.5-65.5% within-compilation LOFO HARD accuracy is exactly "
            "the 313/406 and 314/397 already-reported reproductive-win fractions "
            "with half-credit for 354/350 zero-feature same-module rows. "
            "It is not independent corroboration of an organ-specific K effect. "
            "LOFO Brier scores compare conditional probabilistic predictions, without isolating calibration "
            "across withheld families, but the organ module was chosen after "
            "all original family outcomes; model selection remains non-nested."
        ),
        "new_trait_results_computed": 0,
        "independent_biological_replication": False
    }

def self_test(d):
    correct=audit(d)
    require(correct["status"].startswith("PASS_"),"Original paper should pass")
    for axis,field in (
        ("S3","matched_all_pairs_S3"),
        ("prune","matched_all_pairs_prune"),
    ):
        dirty=json.loads(json.dumps(d))
        dirty["phenotype_scope"][field]+=1
        try:
            audit(dirty)
        except AssertionError:
            continue
        raise AssertionError("Fail-closed source-support perturbation was accepted: "+axis)
    dirty=json.loads(json.dumps(d))
    dirty["predictive_whole_family_holdout"]["S3"]["organ_accuracy"]-=.018
    try:audit(dirty)
    except AssertionError:pass
    else:raise AssertionError("Incorrect accuracy was accepted")
    print("SELF_TEST_PASS: original algebra plus 3 corrupted source-count/score states rejected")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--claims",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    d=json.loads(args.claims.read_text(encoding="utf-8"))
    if args.self_test:self_test(d)
    ans=audit(d)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(ans,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print("LOFO_ACCURACY_IDENTITY="+json.dumps({
        "status":ans["status"],
        "S3":ans["axes"]["S3"]["derived_hard_accuracy"],
        "prune":ans["axes"]["prune"]["derived_hard_accuracy"],
        "separate_brier_gain_S3":ans["axes"]["S3"]["nonredundant_brier_gain_vs_pooled"],
        "separate_brier_gain_prune":ans["axes"]["prune"]["nonredundant_brier_gain_vs_pooled"],
    },ensure_ascii=False))

if __name__=="__main__":
    main()
