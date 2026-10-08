# AusTraits shared-OU phylogenetic K null: frozen three-scenario verdict (v0.1)

**Scientific status:** `K_STRUCTURE_BEYOND_ALL_THREE_EQUAL_OU_SCENARIOS` under the *pre-outcome specified quantile decision rule*.

**Audited completed reproducibility:** [archived-results recovery workflow #37779668889](https://github.com/zuizui0223/turnover/actions/runs/37779668889) (all eight jobs success; `austraits-shared-ou-process-null-recovered-final-v0-1` is the interpretation artifact). This recovery reused the unchanged 16 successful OU simulation outputs of [original run #37754329843](https://github.com/zuizui0223/turnover/actions/runs/37754329843). Original run failed only at archive K-versus-log(K) precision validation, before metric aggregation. The correction checks log of the exact archived K scalar used in simulation and independently enforces the recorded four-decimal K/logK serialization bounds. It **does not alter the simulated trees, tips, OU draws, K engine, measured observed log(K), or preread decision**. [Synthetic pipeline preflight #37779752387](https://github.com/zuizui0223/turnover/actions/runs/37779752387) passed after the companion test-fixture correction.

## Question

Do observed Blomberg K trait ranking and conditional family repeatability persist beyond independently drawn, *identically parameterized* stationary Ornstein–Uhlenbeck evolutionary traits, on the exact same empirical phylogenies and tip sets?

The design was frozen *after the Brownian results and before observing any OU outputs*, in `data/austraits_k_equal_ou_alternative_null_v0_1.json`. The archived K population is unchanged: 254 family×trait systems, 42 families, 13 traits, on both source-native S3 and prune-only tree treatments. For each of the three globally homogeneous OU scenarios `c = alpha × T_ref ∈ {0.25, 1, 4}`, 256 independent draws per system and axis were generated with stationary roots, common optimum and common diffusion coefficient. `T_ref = 47.5820775` uses the 508 reconstructed system trees and was frozen without access to OU outcomes.

## Frozen quantitative result

The table uses the **observed** quantities and each matching OU null distribution's 97.5% quantile. Positive held-out-family rank gain means informative cross-family trait ranks. Family ICC comes from `log(K) ~ 0 + trait + (1|family)` REML on the same 254-cell graph.

| Shared OU c | S3 observed rank gain | S3 null 97.5% | prune observed rank gain | prune null 97.5% | S3 observed family ICC | S3 null 97.5% | prune observed ICC | prune null 97.5% |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | +8.0818% | +0.3986% | +15.3072% | +0.6882% | 0.5306 | 0.1309 | 0.5881 | 0.1147 |
| 1 | +8.0818% | +0.4735% | +15.3072% | −0.5523% | 0.5306 | 0.2273 | 0.5881 | 0.2199 |
| 4 | +8.0818% | +0.5206% | +15.3072% | +0.8254% | 0.5306 | **0.5253** | 0.5881 | 0.4901 |

- All 12 pre-specified metric-by-tree-by-scenario quantile checks pass (rank gain and family ICC, both trees, three OU strengths).
- Rank-gain one-sided Monte Carlo p = **1/257 ≈ 0.00389** for every scenario and tree treatment.
- Family-ICC Monte Carlo p = **1/257** in five cells and **0.0272 for c=4, S3**. The latter still exceeds the **sample 97.5% quantile** under the explicit pre-frozen threshold rule, but that narrow margin is **not** equivalent to a conventional p < 0.025 claim.
- The c=4 S3 family-ICC excess is only **0.0053** (0.5306 observed versus 0.5253 null quantile). With 256 null draws, its classification has appreciable Monte Carlo quantile uncertainty and must be labelled borderline.
- The original observed cross-family trait-pair reversal is approximately 44.03% S3 / 39.88% prune-only, versus ~50% under trait exchangeability. **Reversal by itself is not evidence of adaptation.**

## Interpretation and limitations

**Supported:** The empirically observed allocation of standardized phylogenetic signal among named plant traits, and family-associated mean differences, are not reproduced by the specified set of independent homogeneous BM and three stationary homogeneous-OU alternatives on the same empirical tree/tip graph. The provisional independent post-repair audit agreed with the archived GitHub output, and the final predeclared three-scenario classification is now reproduced in CI.

**Not supported:** A universal, estimator-invariant trait 'memory strength'; direct estimation of evolutionary rates from K or Spearman distance–disparity rho; natural selection, adaptive trait reallocation, historical genetic reactivation, or necessity of family-specific evolutionary-process parameters. These are stronger hypotheses than an equal-process null exceedance.

**Live alternative explanations:** Correlations among measured traits; trait-specific or source-specific observation error; source aggregation and taxon sampling biases; phylogenetic tree uncertainty; homogeneous OU strengths outside the pre-frozen three-point grid; other shared evolutionary processes. The c=4 S3 boundary particularly calls for a Monte Carlo precision sensitivity, labelled post-outcome rather than misrepresented as preregistered inference.

**Next mechanistic discriminator, rather than unbounded observed-K model fishing:** obtain externally calibrated per-trait/species/source measurement reliabilities, define a matched-tree observation-error null *before simulated outcomes*, and compare its held-out-family K ranking plus family-ICC reproduction to the homogeneous OU result. In parallel, test trait covariance using shared-taxon multivariate process simulations. Do not tune null parameters to observed K and then present the same-data fit as an external falsification.

## Publication boundary

The discovery claim is **statistic-dependent**: AusTraits' Spearman distance–disparity rho does not replicate prospective trait-rank portability while Blomberg K has positive portability. AusTraits is independent compilation with incomplete primary DOI ascertainment, not established wholly independent primary-source replication. This OU exercise is post-rho-outcome and exploratory; it must not upgrade the prospectively failed rho hierarchy hypothesis.
