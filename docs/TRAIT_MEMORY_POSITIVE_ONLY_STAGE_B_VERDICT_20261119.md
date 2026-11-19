# Stage B positive-only correction: audited result and submission implications

**Verified computation:** GitHub Actions [run #37443037590](https://github.com/zuizui0223/turnover/actions/runs/37443037590), downstream job `112205536516`, completed **2026-10-06**. The Stage B full 201-system synthesis was printed as structured JSON in the successful job log and has been preserved **verbatim from that log** in [permanent aggregate-only result](../results/trait_memory_positive_only_cleaning_impact_v0_2/result.json) on this branch. Its original Actions ZIP artifact #11402782797 (SHA256 `69a1db6627fb30494dd84ad0ae1228af09419e4f7b1a7e7b16cc9af02ef86fc6`) was generated with 30-day retention; do not assert its continued availability. The printed JSON is a verifiable **aggregate**, not the original 201-row cleaned effects table. Full row-level reproducibility still requires recovering/rebuilding the original pinned source-derived artifacts.

## 1. Primary input decision — cleaning mandatory on validity, not effect direction

Stage A pre-fixed five strictly positive physical traits. Remove raw BIEN values ≤0 **only in these five traits** before computing species medians; no offset, source deletion, cap, selective trait loss, updated phylogenetic placement, or outcome-based filtering.

**Stage B passed its frozen support gate:** **201/201** family×trait systems retained (45 families, 12 continuous traits); 49 affected systems recomputed; 152 unchanged copied exactly. Cleaned log-scale results are available for **all 201** on both S3 and prune. Total original species-tip removals counted across affected systems: S3 **141**, prune **54** (not unique species over all families).

Original-vs-cleaned `rho`: S3 Spearman **0.9910**, Prune **0.9936**; |Δrho|≥0.01 in **17** S3 / **15** prune systems; sign flips **2/3**. The maximum |Δrho| is **0.0850 / 0.1438**. These are observed source-quality corrections, not a selected sensitivity.

## 2. Results on cleaned primary data

| Statistic / model | Cleaned raw S3 | Cleaned raw prune | Cleaned log S3 | Cleaned log prune |
|---|---:|---:|---:|---:|
| Naive crossed family repeatability | 0.1564 | 0.1541 | 0.1489 | 0.1615 |
| Naive crossed trait repeatability | 0.0519 | 0.0279 | 0.0972 | 0.0846 |
| Measurement-aware family share of typical total variance (point) | 16.22% | 14.27% | 12.46% | 11.14% |
| Measurement-aware sampling error share (point) | 23.18% | 24.86% | 23.45% | 25.36% |
| Held-out-family trait BLUP SSE gain | 1.21% | 0.00% | 5.92% | 5.51% |

For the **cleaned raw** correlated-trait zero-family-effect null, p-values are S3 **0.0170** and Prune **0.0130**. The unchanged predeclared null is exceeded, but this does not identify a causal lineage-level mechanism.

### What changes from RC3?

- Earlier uncleaned S3 crossed family repeatability was **0.1504**; after source-validity cleaning, primary cleaned raw is **0.1564**. The family context remains. This is no longer a merely optional robustness sensitivity.
- Earlier raw-scale *BLUP* gains were **0.60% / -0.48%**. Cleaned raw gains are **1.21% / 0.00%** (S3 / prune). **Both are small**, and these are **not** the original unshrunk primary portability test (different predictor/estimand).
- Cleaned logarithmic trait representation yields **5.92% / 5.51%** positive BLUP gains; this differs from raw-scale performance, so **cross-lineage trait information is scale-dependent**, not absent.
- Approx. 23.18% of typical cleaned raw S3 total variation is sampling error. Residual heterogeneity cannot all be labelled evolutionary idiosyncrasy. The pre-frozen two-way cluster bootstrap of 500 fits succeeded but its component-share intervals are broad and overlapping, so no family>trait or system-dominance test is licensed.
- Blomberg K and distance–disparity rho remain distinct estimands. AusTraits `K` rank portability in PR #13 is not a new estimator tested on the BIEN cleaned primary outcomes.

## 3. Revised manuscript-safe claim

> **Plant phylogenetic distance–disparity structure retains a modest repeatable family component after removal of invalid zero/negative trait measurements, while the predictive value of trait identity across unfamiliar families is limited on the raw scale and larger—but still modest—on the logarithmic scale.**

No claim of intrinsically non-portable traits, uniformly weak trait effect, adaptive reallocation, or phylogenetic evolutionary-rate heterogeneity follows from this one statistic. The stronger inference is **scale-qualified generalization**.

## 4. Submission gate and data preservation

**A new manuscript RC is required.** The existing [Evolution RC3 PR #29](https://github.com/zuizui0223/turnover/pull/29) remains explicitly HOLD and should not be submitted. The corrected positive-only dataset is the next primary contract by the already-frozen Stage B rule, irrespective of effect direction. The next RC must replace **all** original effect/scale/claim descriptions together, retain the original extraction as an explicitly labelled invalid-code audit sensitivity, and cross-check its figures/tables to the corrected 201-row effects.

The 201-row cleaned-effects and model intermediate ZIPs were generated in October with 30-day artifact retention and are **not in this repository snapshot**. Saving the exact printed final aggregate JSON prevents losing the numerical verdict but **does not reconstruct the 201-row per-system effects/SE table**. Before final submission, recover or rerun the full pinned upstream pipeline under an approved durable artifact policy, then validate every figure/table, licences and independent-source claims. Do not try to rescue this by using unpinned substitute raw trait files.

**Science stop:** No new predictor, scale chosen for better direction, K metric, source deletion, subgroup search, or revised significance threshold. Both cleaned raw and cleaned log results must be reported.
