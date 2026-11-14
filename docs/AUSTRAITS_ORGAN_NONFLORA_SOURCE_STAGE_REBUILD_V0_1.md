# AusTraits 283/142 nonflora source and taxon-stage K reproduction

**23 October 2026 — complete original public-v7 nonflora K and three-stage numerical reproduction; still no independent biological test.**

## Why this is separate from the original 760-pair replay
The original same-tip 760-pair K computations have already been fully numerically reproduced, with maximum difference 0.0 ([raw v7 760-run #39713644617](https://github.com/zuizui0223/turnover/actions/runs/39713644617), preserved in the paper repository). The article's *second* result depends on further **source-restricted observations and species eligibility**, so the ordinary 760-pair raw-to-K replay does not establish this part of the manuscript.

The target original comparisons are (1) **283 S3 / 233 native-prune** pairs from the original 760 graph after removing five fixed electronic Floras, (2) **142 S3 / 101 prune** jointly qualified same-remaining-DatasetID pairs, then (3) an original family×named-pair-ID matched three-stage source/tip transition:
- S3 reproductive-higher K signs **110 → 121 → 120** for 142 identical pair identities
- Prune reproductive-higher K signs **82 → 83 → 81** for 101 identical pair identities

The first transition changes available species, tree-tip support/geometry and K normalization **together**. The second transition changes only the surviving source measurements on the *same species and same tree*. This is an observational sensitivity analysis, not a pure causal selection or measurement-error effect.

## Complete nonflora paired K, stage transitions and 5,000-family bootstrap PASSED

[All 28 originally fixed K batch reruns plus independent final aggregation #39723170670 PASS](https://github.com/zuizui0223/turnover/actions/runs/39723170670) numerically re-estimated all 283 broad / 142 strict original nonflora paired-trait systems, with **283/233 S3/prune** and **142/101 S3/prune** K successes. Original K and log-K pair values reproduced with **maximum absolute discrepancy 0.0**, and identical original 142/101 pair-ID transitions **110→121→120 S3**, **82→83→81 prune** and sign reversals **23/9, 13/12** remained exact.

[Permanent archival and 5,000-family-bootstrap source result reaggregation #39877245159 PASS](https://github.com/zuizui0223/turnover/actions/runs/39877245159) independently rechecked every original K/source transition and bootstrap statistic and committed **60 SHA256-authenticated K/QA/aggregate files** under [original public-v7 nonflora source-stage complete replay](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_public_v7_nonflora_3stage_replay_v0_1). No species or observation-level raw measurements were published; technical reproduction remains within the historical original AusTraits compilation, and Stage 1→2 cannot be attributed purely to species selection.

## What has independently passed
- Original 283/142 K-blind source-only cohort and all 28 original K batch outputs (16 broad, 12 strict) preserved byte-for-byte with SHA256 before original GitHub Actions expiry, [permanent source K archive #39722381639 PASS](https://github.com/zuizui0223/turnover/actions/runs/39722381639). Source records are aggregate-only, never raw species traits.
- [Public AusTraits v7 original source-eligibility rebuild #39723741575 PASS](https://github.com/zuizui0223/turnover/actions/runs/39723741575) downloaded the original versioned public Parquet, checked SHA256 5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99, and regenerated every original post-five-Flora common-species and same-DatasetID source-only eligibility count. The **entire original/nonflora eligibility JSON files were byte-identical** (SHA256 2870909f97d492400d7a3f6978f94689e5a829ed719cd48340d0633c0f9c83d5). This is not new K estimation.

## Historical 22 October execution status, superseded by complete PASS above
[Original 28-batch public-v7 broad/strict K matrix #39723170670](https://github.com/zuizui0223/turnover/actions/runs/39723170670) restored all the original K-blind family×pair identities with original batch placement and has begun independent R/C++ and pinned V.PhyloMaker2 S3/prune K calculation. For each pair it tests all four original K values (both organs in two source arms), both log-K contrasts, measurement-source log-K shift, original tree native tip numbers and HOLD/PASS decisions, with rtol 1e-7 and atol 2e-8. The final step requires all **283+142 family×pair outputs**, exact original native-tree pass counts and 142/101 identity-matched stage transitions including the 23/9 S3 and 13/12 prune sign reversals.

**This was the historical precompletion rule on 22 October.** The full 28-batch original K/three-stage final aggregate and the independent 5,000-family-bootstrap permanent archive have now both passed, as verified above.

## Hard inferential boundaries
The observations are retrospective, within the **same** original AusTraits v7 compilation, with originally post-selected organ grouping and removal of five electronic Flora DatasetIDs. A matching DatasetID can contain secondary or derivative sources and does not guarantee independent original specimens. A clean technical recomputation does not establish a universal difference in plant organ constraint, BM evolutionary velocity, OU attraction, natural selection, or independent primary-source validation.

The current manuscript remains coauthor-review-only, Draft PR #38, unmerged and unsubmitted. Journal compliance, original source attribution and authorship/submission authorization remain separate human gates.
