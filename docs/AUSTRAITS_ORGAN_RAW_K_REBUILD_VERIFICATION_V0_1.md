# AusTraits v7 raw-source to Blomberg K: permanent source references and clean-run audit

**2026-10-21 | Technical reproducibility evidence | Not a new ecological effect.**

## Scope, immutable original inputs
- Public original AusTraits v7.0.0, Falster et al. (2025), https://doi.org/10.5281/zenodo.15718081
- Actual original analysis Parquet is the versioned public release file at https://github.com/traitecoevo/austraits.build/releases/download/v7.0.0/austraits-7.0.0-flattened.parquet, with source SHA256 5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99.
- Original source-native units are loaded at build commit 7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c; V.PhyloMaker2 is fixed at 7af3fb5152f691af2e4ec9d5e2e467d1b50505e9.
- The permanent repository directory results/austraits_organ_paper_frozen_rebuild_inputs_v0_1 contains the original *259-row full core* (including the original *254 K-eligible* family–trait systems), original 254-system K reference and all original 770 potential/760 qualified family-by-pair **source-only** support identities, with SHA256 of every file.
- The permanent directory results/austraits_organ_paper_original_pair_K_v0_1 contains all 24 originally computed matched-tip K batches, spanning 760 S3 and 747 prune tree successes, including 406/397 reproductive–vegetative comparisons. These are derived K outputs only; species-specific states and specimen observations are not redistributed.

The two archival GitHub Actions have PASSED: [core and source cohort #39448885872](https://github.com/zuizui0223/turnover/actions/runs/39448885872), [historical original 24 K batches #39450135788](https://github.com/zuizui0223/turnover/actions/runs/39450135788). This removes the previous 30-day expiration of the exact paper-reconstruction reference inputs.

## Fresh public-source numerical regression (confirmed)

From a new Ubuntu/R runtime, the existing source-normalization code downloads and SHA-verifies the public v7 Parquet; applies the original species-rank, exact-unit, observation identity, deduplication and per-species-positive-median rules; constructs the original same-species S3 and prune trees; and computes K using the original R and C++ kernels. This was verified in [#39450562893 (PASS)](https://github.com/zuizui0223/turnover/actions/runs/39450562893).

| Previously source-qualified example | Original common species | S3 native tips | Prune native tips | Difference from original K and log-K references |
| --- | ---: | ---: | ---: | --- |
| Casuarinaceae: fruit length / leaf length | 47 | 47 | 40 | exactly 0.0 on both axes |
| Asteraceae: fruit width / leaf length | 177 | 177 | 81 | exactly 0.0 on both axes |

These are **two technical regression cases selected among the original comparisons**, not external biological confirmation of reproductive conservation, not the entire original study, and not 760 fresh K estimates. Both tree axes use the original pinned biological source and tree builder, not new taxa or a new OU model.

## Rebuild workflow

Run the source-linked GitHub Actions workflow:
.github/workflows/austraits-organ-public-raw-k-smoke-v0-1.yml

It uses:
- scripts/analysis/audit_austraits_k_shared_taxon_pair_support_v0_1.py to independently rederive all original family-by-pair source-only common-species support from the exact public Parquet;
- scripts/qa/audit_austraits_organ_public_source_support_regression_v0_1.py to compare all candidate-pair species counts and source qualification against the preserved original graph;
- scripts/analysis/run_austraits_k_shared_taxon_pairs_batch_v0_1.py, scripts/analysis/fit_austraits_k_shared_taxon_pairs_v0_1.R and scripts/analysis/austraits_ou_k_kernel_v0_1.cpp to run actual original real-tree K for two prior source-qualified comparisons;
- scripts/qa/audit_austraits_organ_raw_k_smoke_v0_1.py to check original source SHA256, source-tip agreement and exact historical per-pair K parity.

The experiment uploads only technical JSON results; original raw species observations remain transient runner-local inputs.

## Still to be done, without overclaiming
1. Execute a *full fresh raw-to-K run* for all 760 original source-qualified comparisons and independently compare each estimated K against the permanently stored 24 original batches. The archive makes this possible without historical artifact downloads but does not itself perform 760 fresh R fits.
2. Verify all original contributing-study citation and data/metadata/source-unit obligations for any chosen journal. Public source access and two exact numeric regression cases do not certify full repository-to-submission compliance.
3. Obtain real coauthor review, factual author declarations and explicit approval before a journal submission.

The empirical paper remains an exploratory post-discovery **within-AusTraits** result. No independent source reproduction, developmental constraint, evolutionary-rate inference, selection regime, preregistration or prospective subgroup test has been established.
