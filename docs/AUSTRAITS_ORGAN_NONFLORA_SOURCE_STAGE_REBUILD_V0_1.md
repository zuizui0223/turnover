# AusTraits 283/142 nonflora source and taxon-stage K reproduction

**22 October 2026 — in-progress full original nonflora K regeneration. No biological reanalysis or hypothesis discovery.**

## Why this is separate from the original 760-pair replay
The original same-tip 760-pair K computations have already been fully numerically reproduced, with maximum difference 0.0 ([raw v7 760-run #39713644617](https://github.com/zuizui0223/turnover/actions/runs/39713644617), preserved in the paper repository). The article's *second* result depends on further **source-restricted observations and species eligibility**, so the ordinary 760-pair raw-to-K replay does not establish this part of the manuscript.

The target original comparisons are (1) **283 S3 / 233 native-prune** pairs from the original 760 graph after removing five fixed electronic Floras, (2) **142 S3 / 101 prune** jointly qualified same-remaining-DatasetID pairs, then (3) an original family×named-pair-ID matched three-stage source/tip transition:
- S3 reproductive-higher K signs **110 → 121 → 120** for 142 identical pair identities
- Prune reproductive-higher K signs **82 → 83 → 81** for 101 identical pair identities

The first transition changes available species, tree-tip support/geometry and K normalization **together**. The second transition changes only the surviving source measurements on the *same species and same tree*. This is an observational sensitivity analysis, not a pure causal selection or measurement-error effect.

## What has independently passed
- Original 283/142 K-blind source-only cohort and all 28 original K batch outputs (16 broad, 12 strict) preserved byte-for-byte with SHA256 before original GitHub Actions expiry, [permanent source K archive #39722381639 PASS](https://github.com/zuizui0223/turnover/actions/runs/39722381639). Source records are aggregate-only, never raw species traits.
- [Public AusTraits v7 original source-eligibility rebuild #39723741575 PASS](https://github.com/zuizui0223/turnover/actions/runs/39723741575) downloaded the original versioned public Parquet, checked SHA256 5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99, and regenerated every original post-five-Flora common-species and same-DatasetID source-only eligibility count. The **entire original/nonflora eligibility JSON files were byte-identical** (SHA256 2870909f97d492400d7a3f6978f94689e5a829ed719cd48340d0633c0f9c83d5). This is not new K estimation.

## Re-execution now underway
[Original 28-batch public-v7 broad/strict K matrix #39723170670](https://github.com/zuizui0223/turnover/actions/runs/39723170670) restored all the original K-blind family×pair identities with original batch placement and has begun independent R/C++ and pinned V.PhyloMaker2 S3/prune K calculation. For each pair it tests all four original K values (both organs in two source arms), both log-K contrasts, measurement-source log-K shift, original tree native tip numbers and HOLD/PASS decisions, with rtol 1e-7 and atol 2e-8. The final step requires all **283+142 family×pair outputs**, exact original native-tree pass counts and 142/101 identity-matched stage transitions including the 23/9 S3 and 13/12 prune sign reversals.

**Do not claim all 28 K batches or the three-stage result are newly reproduced until the final GitHub Actions aggregate is marked completed + success.** A separate permanent-archive workflow is staged in the branch but has no completion marker triggered at this stage. On successful completion it will independently reaggregate the original source/measurement stages and 5,000-family bootstrap, compare all published aggregate fields with original archived results, and permanently commit only nonraw K/QA/aggregate files with SHA256.

## Hard inferential boundaries
The observations are retrospective, within the **same** original AusTraits v7 compilation, with originally post-selected organ grouping and removal of five electronic Flora DatasetIDs. A matching DatasetID can contain secondary or derivative sources and does not guarantee independent original specimens. A clean technical recomputation does not establish a universal difference in plant organ constraint, BM evolutionary velocity, OU attraction, natural selection, or independent primary-source validation.

The current manuscript remains coauthor-review-only, Draft PR #38, unmerged and unsubmitted. Journal compliance, original source attribution and authorship/submission authorization remain separate human gates.
