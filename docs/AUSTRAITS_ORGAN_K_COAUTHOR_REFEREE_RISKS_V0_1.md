# Coauthor scientific red-team review — AusTraits organ-K manuscript

## High-priority mathematical dependence audit — correct before treating model transfer as a separate result

**P0: The 42-fold organ-only hard accuracy adds no independent reproductive-K evidence.** Original source-code inspection confirms one signed organ feature and no intercept; within-organ rows always have x=0 and p=0.5, earning exactly half-credit. A family can remove at most 36 named cross-organ comparisons, so every family-held-out fit retains a positive reproductive coefficient. Thus S3 `(313+354/2)/760 = 64.47%`; prune `(314+350/2)/747 = 65.46%`. These are identical to published LOFO hard scores up to rounding. An editor must not count both 77–79% reproductive K wins and 65% model accuracy as two independent lines of ecological confirmation.

**Allowed response:** Reframe organ model Figure 2 and Results 3.2 as **conditional Brier probability scoring**, not another hard-label result. The original pooled-vs-organ Brier gains remain factual and potentially informative for probabilistic performance (not a separate reliability/calibration assessment), but selected grouping, shared sources and family dependencies constrain their inferential interpretation. Scientific evidence is strongest in the matched-tip organ K asymmetry and same-pair-ID source/tip composition sensitivity, with original post-selection disclosures.

[Source-linked count proof and unit tests](https://github.com/zuizui0223/turnover/blob/paper/austraits-organ-ecology-v0-2/docs/AUSTRAITS_LOFO_HARD_ACCURACY_DEPENDENCE_VERDICT_V0_1.md).

---


**19 October 2026 · Reporting-only editorial audit · No new analyses.**  
**Applies to:** `docs/AUSTRAITS_K_ORGAN_ECOLOGY_MANUSCRIPT_V0_2.md` and Supplementary Tables S1–S3, [PR #38](https://github.com/zuizui0223/turnover/pull/38).

## Verdict

**Scientifically defensible as a transparent exploratory comparative study, not as a confirmed macroevolutionary mechanism or universal plant-organ law.** The strongest ecological signal is a consistent *descriptive* reproductive K advantage on same-tip contrasts within AusTraits; the strongest inferential addition is separating what data are available for comparison from which contributing source supplies their values. Neither is an independent biological experiment. The ~65% whole-family model score is useful **only conditional on a functional grouping selected using the same source data**.

The figures and reporting QA are reproducible, but the following issues are either unresolvable without new measurements or must be plainly disclosed before author-level review.

| Priority | Likely referee objection | Verified evidence | Allowed editorial resolution |
| --- | --- | --- | --- |
| **P0** | **Functional module was selected after original K outcomes; “held-out” model is not fully nested.** | The 6+6 organ grouping was selected after the 760-pair K discovery; the 42 model coefficients are estimated with each evaluation family held out **after** the grouping was chosen. | Keep “retrospective within-compilation portability”; do **not** report 64.5–65.5% as unbiased future-lineage prediction or calculate a confirmatory post-selection p-value. |
| **P0** | **K does not estimate evolutionary velocity/selection.** | Same-tip K signs (313/406 S3; 314/397 prune) are a normalized covariance signal, not BM sigma² or OU alpha. | Use “higher estimated phylogenetic K” not “slower evolution”, “stronger constraint” or inferred stabilizing selection. |
| **P0** | **Observed-tree process null answers a different question.** | Previously frozen homogeneous OU plus source-noise reproduced scalar rank portability; post-hoc organ model adequacy uses **410 original unequal-tip** pairs, whereas the biological matched-tip observations use 406/397. | Label OU outcome post-discovery, source-model-specific, not a rejection of all homogeneous processes or matched-tip null. |
| **P1** | **Source agreement changes which taxa survive.** | On 142 fixed S3 pair identities, reproductive K higher shifts **110→121→120**. Tip/support narrowing flips 23 directions; changing source values on identical narrow tips flips 9; prune has 13 vs 12. | Present both trees and original paired denominators; the first transition also changes tree pruning/normalization, so avoid causal “sampling alone” language. |
| **P1** | **Repeating correlated family×trait pairs makes the raw 77–79% appear stronger.** | 406/397 comparisons are repeated pairs nested in only 34 families; pairwise shared-species intersections vary. | Lead with family-equal rates and whole-family resampling alongside pair-weighted descriptions, noting remaining cross-family phylogenetic/source correlation. |
| **P1** | **A common source DatasetID does not prove an independent original measurement.** | 283/233 five-flora-excluded comparisons and 142/101 common-DatasetID comparisons still contain secondary source classes; leaf/leaflet and fruit/diaspore concepts vary. | Explain original publication/specimen-level uncertainty, show named-source exclusions but **do not** call them independent replication. |
| **P1** | **Brier/accuracy and cross-organ frequency use different prediction populations.** | The conditional LOFO model scores **760/747 all pair types** (including within-module ties); the 77–79% statement concerns 406/397 cross-module pairs only. | Keep both distinct denominators and “within-module half-credit ties”; no claim that 65% is a direct test accuracy on the cross-organ-only 406/397. |
| **P1** | **Globality and novelty may be overstated.** | 12 morphometric traits in 42 studied families from AusTraits; Ackerly (2009) already examined seed, leaf and height evolutionary patterns. | Claim the combination of same-tip organ contrast, retrospective family-holdout prediction and stage-matched source/taxon sensitivity, **not** discovery of phylogenetic signal in reproductive organs per se. |
| **P2** | **Raw observation matrix is not bundled for third-party reproduction.** | Original source-native values have provider conditions; artifact PDFs/figure images only reproduce manuscript **aggregates**. | Link code, exact original action runs, figure-input SHA256 and access steps, and preserve source-artifact retention/rights before formal submission. |

## Claim ladder for coauthor sign-off

1. **Directly observed:** Higher reproductive than vegetative K in 313/406 and 314/397 matched-species/phylogeny comparisons in the available AusTraits dataset.
2. **Descriptive generalization within this compilation:** A post-selected organ grouping shows modest conditional family-holdout prediction improvement; unknown-family predictability on genuinely independent new data is **not established**.
3. **Source/tip result:** More restrictive source qualification can make the observed K ranking appear more consistently reproductive-heavy by changing the eligible taxa and tree; changing source values on identical tips has a smaller S3 descriptive impact.
4. **Not established:** A universal reproductive conservation principle, an identified developmental constraint or selection regime, a difference in absolute evolutionary rate, or independent ecological confirmation.

## Editorial acceptance criteria (not submission authorization)

The manuscript is ready for **scientific comments from coauthors** if all listed facts and stop rules remain intact and the final figures and supplementary tables show no clipping, overlaps or omitted denominators. Author order/affiliations, journal choice, data licence/citation obligations, archiving and approval to submit remain **not resolved**. A reviewer-response document should be prepared only after actual coauthor or journal comments; do not fabricate peer-review history.

The original closed BIEN 201-system `rho` programme and the frozen external source-validation gates are not reopened by this memo.
