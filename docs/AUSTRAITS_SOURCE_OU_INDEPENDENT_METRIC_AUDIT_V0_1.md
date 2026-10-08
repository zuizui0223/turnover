# Independent metric audit of the 249-system source-noise OU simulations

**Status:** Independent from the primary aggregation code, using the complete 16 successful source-native batch artifacts of [GitHub Actions #37785257795](https://github.com/zuizui0223/turnover/actions/runs/37785257795). The primary workflow's aggregation/12 REML fits/final interpretation must be checked separately before closing the canonical result.

**Graph:** 249 family×trait systems, 42 families, 12 named traits; `seed_height` removed by the earlier K-blind source-coverage gate on BOTH observed and null. Each scenario uses 256 draws per system and each exact native tree treatment. No parameters were tuned to empirical K; the whole analysis is **post-original-rho/K and post-homogeneous-OU outcomes**.

## Primary held-out-family within-family rank-gain metric

The independently recomputed empirical source-conditioned ranks were **+8.00831% S3** and **+15.57657% prune-only**, agreeing with earlier observation-only matched-graph checks.

| Source model | Dimensionless common OU attraction `c` | S3 null mean | S3 null 97.5% | prune null mean | prune null 97.5% |
|---|---:|---:|---:|---:|---:|
| `trait_global` | 0.25 | +13.17% | +22.74% | +15.45% | +25.97% |
| `trait_global` | 1 | +11.51% | +20.33% | +13.52% | +24.31% |
| `trait_global` | 4 | +7.31% | +16.81% | +8.96% | +18.59% |
| `system_local` | 0.25 | +4.73% | +13.66% | +6.41% | +15.06% |
| `system_local` | 1 | +4.26% | +13.46% | +5.43% | +14.91% |
| `system_local` | 4 | +1.90% | +11.73% | +2.96% | +10.80% |

Of the 12 predeclared model×OU×tree **rank-gain** checks, **3** exceed the null 97.5% quantile (all `system_local` on prune), while **9 do not**. Crucially, all six `trait_global` rank checks accommodate the observed rank gain. Therefore the original pre-outcome decision rule for the primary endpoint resolves to **`RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES`**. This is a **failure to require process heterogeneity**, *not* evidence that the source-noise generating process was the true one.

## Why metric-matching is insufficient: post-outcome named-trait profile check

The primary statistic measures the *degree of portability* without requiring the *identity and order of the traits* to match. We therefore added a separately labelled **exploratory posterior-predictive named-trait profile diagnostic**, after seeing the primary null outcome. It computes average within-family normalized ranks for each trait on the exact same system graph; Spearman correlation compares empirical trait mean ranks to those predicted across the 256 source-noise OU realizations. The null reference compares each synthetic replicate with the prediction averaged from its other 255 replicates.

| Shared OU `c` | S3 empirical-to-`trait_global` expected profile rho | prune rho |
|---:|---:|---:|
| 0.25 | 0.497 | 0.531 |
| 1 | 0.531 | 0.580 |
| 4 | 0.559 | 0.580 |

The model-generated replicate-to-held-out-model-mean rank correlations average **0.84–0.88** for the corresponding conditions. Most empirical profile correlations are below the simulated 2.5th percentile; these *exploratory*, dependent-across-tree comparisons are **not** a preregistered extra discovery test. [Reproduction script](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/scripts/analysis/audit_austraits_k_source_ou_named_rank_alignment_v0_1.py).

For example, under the `trait_global`, `c=1` comparison, the empirical normalized S3 mean ranks for `petiole_length` and `leaf_width` are **0.406 and 0.325** versus model-expected **0.630 and 0.531**. Conversely, `seed_width` and `leaf_area` are **0.591 and 0.700** empirically versus **0.327 and 0.439** expected. This means source variation alone does not predict the *same named-trait hierarchy*, even when it explains overall rank-gain magnitude.

## Secondary descriptive metric check

On the identical 249-system graph, observed LOFO **absolute log(K) gain** is **+4.173% S3** and **+5.917% prune**. Under the `trait_global, c=1` source-noise null, those means become **+14.48% S3** and **+13.23% prune**, much more predictive than actual observations. This mismatch means no claim is permitted that the alternative has explained the *entire K architecture*.

Observed cross-family K pair-order reversal on the fixed 12-trait subgraph is **44.03% S3** and **39.88% prune** (33 comparable trait pairs). The `trait_global, c=1` model yields approximately **43.1% S3** and **42.0% prune**. Again, metric-level agreement must not be mistaken for the particular trait ranking's fit.

## Hard scientific boundaries

- Source variance ratios are differences among records attributed to datasets of the same named species, **not independent instrument-error estimates**. They may contain real environment/population/protocol differences.
- All predeclared source-noise models retain a **single homogeneous latent OU process**; named-trait differences exist in the **observation layer**.
- The strong general statement `K portability requires distinct evolutionary-process parameters` is **not supported by the predefined rank-gain endpoint**; mechanistic alternatives are *not yet identified*.
- The named-trait identity and absolute K prediction checks reveal **model inadequacy** for other features but are exploratory in this analysis. They do **not** demonstrate adaptation, selection, or trait-specific OU parameters.
- No retrospective rewriting of the prospective AusTraits rho ranking failure, BIEN analyses, or fixed source/OU decisions is allowed.

**Provisional quantitative status:** rank and secondary metrics were independently reconstructed from archived complete raw batches. Canonical GitHub aggregation and model-family REML final artifacts remain separate reproducibility gates.
