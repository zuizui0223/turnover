# Named-trait K ranking is not reproduced by the tested OU + source-variation models

**2026-10-10; post-outcome, exploratory model-adequacy result.** This is deliberately NOT a new preregistered primary result, process-history identification, or evidence of selection.

## Frozen original question and its final answer

The [complete 249-system original source-OU workflow](https://github.com/zuizui0223/turnover/actions/runs/37785257795) and [independent parity-checked recovery](https://github.com/zuizui0223/turnover/actions/runs/37793799844) both finished successfully. On the identical 249 family×trait systems, 42 families, 12 source-eligible traits, the **pre-source-simulation frozen** primary LOFO rank-gain test classifies `RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES`. This means the observed *strength of named-trait rank portability* does not require trait-specific latent OU-process parameters: homogeneous stationary OU plus trait-specific, K-blind externally source-calibrated **observational heterogeneity** can reproduce that scalar statistic. It does NOT mean the model is generally adequate.

The observed K conditional-family ICC on this subgraph is **0.5286 S3 / 0.5879 prune**. In the `trait_global, c=4` model the family ICC null 97.5th quantiles are **0.5636 / 0.6220**, also accommodating the observed ICC on both tree axes. Family×trait-specific source variability (`system_local`) often falls short of the observed ICC. Note the `c=4,system_local,prune` sample 97.5th quantile is 0.5839 (observed 0.5879), but the simulation one-sided tail p is 0.0272—not a conventional p<0.025 result. All source-OU tests are **post original rho/K and homogeneous OU discovery**.

## Why a second, nonprimary test is necessary

The original LOFO rank-prediction gain `G` is invariant under every **globally consistent relabeling of the 12 named traits**. It measures the *amount* of repeatable K ranking, not the *identity* of traits with strong or weak K. This cannot be solved by merely increasing simulation replicates of `G`.

After observing the source-OU primary outcome, we added an explicitly **exploratory** global model-adequacy statistic on the **12-dimensional named profile**:

`D = sum_t [ mean_rank_empirical(t) - mean_rank_null(t) ]²`.

For each simulation replicate, its null distance is computed against the expected named profile of the **other 255 replicates**, guarding against optimistic self-fitting. No K outcomes are used to change the OU alpha values, the two source noise assignments, the 249-system graph, or the source-error calibrations.

## Reproduced quantitative results

[Exploratory GitHub reproduction and artifact #38058633092](https://github.com/zuizui0223/turnover/actions/runs/38058633092) **success**, independently corroborating the earlier [Spearman named-profile check #37793020928](https://github.com/zuizui0223/turnover/actions/runs/37793020928).

| Noise model | Shared OU `c` | S3 observed D / null mean (q97.5) | prune observed D / null mean (q97.5) |
|---|---:|---|---|
| named trait global | 0.25 | 0.307 / 0.062 (0.122) | 0.318 / 0.062 (0.138) |
| named trait global | 1 | **0.268 / 0.064 (0.153)** | **0.298 / 0.060 (0.119)** |
| named trait global | 4 | 0.209 / 0.060 (0.123) | 0.226 / 0.060 (0.125) |
| family×trait local | 0.25 | 0.281 / 0.061 (0.123) | 0.307 / 0.063 (0.139) |
| family×trait local | 1 | 0.254 / 0.066 (0.149) | 0.279 / 0.063 (0.136) |
| family×trait local | 4 | 0.211 / 0.061 (0.148) | 0.224 / 0.065 (0.144) |

In all 12 cells the empirical named-rank distance is above that scenario's 97.5th simulated quantile. One-sided empirical Monte Carlo p = **1/257≈0.00389** in ten cells and **2/257≈0.00778** in two cells (c=4 S3 under each noise assignment). This is a **post-outcome model-adequacy diagnosis**, not 12 independent discoveries. All scenarios share the same observed data, related trees and source calibrations, and the model family is not exhaustive. No multiplicity-corrected novel process conclusion is claimed.

## Which named traits drive the discrepancy?

Across **all 12 simulation×axis conditions**, the observed minus model-expected average within-family rank has the same direction for:

- **Higher observed K rank:** `seed_width` (differences +0.21 to +0.36), `leaf_area` (+0.08 to +0.30), `seed_dry_mass` (+0.13 to +0.18).
- **Lower observed K rank:** `leaf_width` (−0.18 to −0.24), `petiole_length` (−0.15 to −0.22).

The largest robust discrepancy is frequently `seed_width` versus `leaf_width`. *However*, direct matched-family pair comparisons have only 16 shared families: `seed_width > leaf_width` occurs in **10/16 S3** and **15/16 prune**, so the particular pair should not be portrayed as invariant across tree construction methods. Profile summaries use different family supports among traits; shared-species and out-of-source tests are still needed. The named-trait contrast is **a hypothesis from observed outcomes**, not prospective confirmation of differential constraint, canalization, or adaptation.

## Ecological interpretation and next necessary test

The tested model can create **repeatability without the correct identity** by combining a common latent evolutionary process with trait-dependent source variability and tree geometry. Thus the scientifically useful new question is:

> Why do the actual plant traits occupying relatively higher and lower phylogenetic K ranks differ systematically from the ranks expected under the explicitly modeled source-variation process?

Candidate causes include real differences in evolutionary constraint or optimum shifts, covariance among morphometric traits, correlated habitat effects, intraspecific plasticity, source-level measurement regimes, and differences among biological modules (e.g. reproductive versus vegetative traits). **None is identified by this analysis.**

The next clean discriminator is prospective-on-new-data and named-trait aware: select a separately sourced BIEN or comparable compilation with original/source-native taxon and phylogeny support, freeze a prevalidation map of shared trait definitions and signed contrasts from this AusTraits discovery, then compute the signed named-profile predictive loss on a truly held-out compilation. If the exact same signed departures replicate after source/geometry adjustment, process-level hypotheses become more credible; if not, source structure remains a sufficient alternative. Avoid reusing AusTraits source measurements or changing the contrast after looking at the new outcome.

## Reproducibility and limits

- Frozen original source-noise decision: `data/austraits_k_source_dispersion_ou_null_design_v0_1.json`.
- [Named-rank distance audit code](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/scripts/analysis/audit_austraits_source_ou_named_rank_distance_v0_1.py); [CI result](https://github.com/zuizui0223/turnover/actions/runs/38058633092).
- Rho (distance–disparity coupling) and K are **different estimands**, neither is directly an evolutionary rate.
- Same-species across-dataset dispersion includes real biological/environmental differences and shared records; it is not known pure measurement error.
- K and source calibration are conditional on original trees/tip support, rather than accounting for tree uncertainty, all missingness, or all multivariate evolutionary covariance.
- This result **does not validate the original prospectively failed rho-ranking hypothesis**, nor establish selection, trait-specific OU parameters, or mechanistic causation.
