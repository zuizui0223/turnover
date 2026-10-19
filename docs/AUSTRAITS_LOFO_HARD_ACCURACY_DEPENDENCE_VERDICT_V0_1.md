# Organ-only heldout hard accuracy is an algebraic re-expression of the post-selected organ K contrast

**2026-10-19 · Reporting-only methodological correction to exploratory AusTraits organ paper; no new phenotypic result, K estimate, or new source.**

## Finding: accuracy is not a second independent line of ecological evidence

The 42-fold leave-one-family-out (LOFO) model uses one signed predictor:
`x=+1` for reproductive `trait_A` and vegetative `trait_B`,
`x=-1` in the opposite orientation, and `x=0` when both traits belong
to the same organ category. It fits a penalized logistic coefficient
**without intercept** (`LogisticRegression(C=1,fit_intercept=False)`).
The source `accuracy_credit` assigns **half credit** when the predicted
probability is 0.5.

Every same-module row has `x=0` and thus probability **exactly 0.5**
in every family fold; its accuracy contribution is invariably 0.5.
For a cross-organ pair, when the fitted coefficient is positive,
the predicted higher-K trait is always the **reproductive** one,
irrespective of the fitted coefficient's magnitude.

The sign remains positive in every LOFO training fold **by construction
of the observed cohort**. On S3, the original cross-organ wins minus
losses equal `313 − (406−313) = 220` comparisons. On prune,
`314 − (397−314) = 231`. Any one withheld family supplies **at most
36** distinct cross-organ named trait pairs (6 reproductive × 6
vegetative), so the remaining training comparison margin is **at least
184 S3 or 195 prune**, still strictly positive. For the no-intercept
one-predictor ridge logistic model, the gradient at coefficient zero
has the same sign as that margin, guaranteeing a positive fitted
coefficient, without assuming any additional properties of heldout
families.

Therefore the organ model's hard accuracy over **all** eligible pairs
obeys the exact identity

[
A_{mathrm{organ}}
=rac{W_{mathrm{reproductive}}+	frac12(N_{mathrm{all}}-N_{mathrm{cross}})}{N_{mathrm{all}}}.
]

| Axis | N all family×named-trait comparisons | Cross-organ comparisons | Reproductive K wins | Same-module comparisons (all fixed 0.5 credit) | Algebraic hard accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| S3 | 760 | 406 | 313 | 354 | **(313+177)/760 = 64.473684%** |
| Native prune | 747 | 397 | 314 | 350 | **(314+175)/747 = 65.461847%** |

These are **identical to the published model's 64.47% / 65.46%
hard-sign scores up to rounding**, requiring no new model outputs.

## Consequences for the manuscript's novelty and claim independence

1. The organ-specific `77.1%/79.1%` descriptive sign direction and
   `64.47%/65.46%` all-pair LOFO hard accuracy **are not two independent
   replications of a biological pattern**. They are the same original
   post-discovery organ winners, counted under two denominators with
   fixed half-credit same-organ ties.
2. Whole-family holdout still separates **coefficient fitting** within
   the model, but cannot make the hard-label sign an independent prediction
   here: all folds learn an identical positive sign, an exact result
   given the observed 42-family margins. The organismal category was
   itself selected using original outcomes across those families,
   making the model selection **non-nested/post-selected**.
3. **Brier loss is not algebraically determined by the binary win fraction
   alone:** the magnitude of heldout-family predicted probabilities
   depends on the other families' data. Its improvement from
   `0.25062→0.21378 S3` and `0.25017→0.20671 prune`
   remains a **retrospective, conditional probability-calibration result**.
   It is not source-independent or unbiased prospective evidence.
4. The paper's stronger ecological content is (a) the **reproductive
   versus vegetative K asymmetry** on matched species and trees and
   (b) the **taxon-coverage sensitivity** of that contrast (142 S3
   identity-matched pairs: **110→121→120**, with 23 sign flips from
   taxon/tip selection versus 9 from source-value substitution on fixed tips).
   Its novelty must be argued with these rather than duplicating the
   same direction twice as independent lines of evidence.

## Source and exact QA

- Original archived matched K/LOFO run:
  https://github.com/zuizui0223/turnover/actions/runs/38686389859
- Original algorithm: `scripts/analysis/audit_austraits_k_functional_module_lofo_v0_1.py`.
- Frozen report registry: `data/austraits_organ_paper_claim_registry_v0_2.json`.
- Exact, fail-closed algebra: `scripts/qa/audit_austraits_organ_lofo_accuracy_identity_v0_1.py`.
- Retain the original original-tip source-OU diagnostic separately: no new
  statistical evolutionary process is inferred here.

**No new biological claims from this correction.** The purpose is
to eliminate a potentially misleading duplicate line of evidence
before scientific peer review.
