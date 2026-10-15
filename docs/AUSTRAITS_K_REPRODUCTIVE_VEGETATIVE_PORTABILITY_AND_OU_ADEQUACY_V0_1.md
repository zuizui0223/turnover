# Reproductive plant morphology is more phylogenetically structured than vegetative morphology within sampled families — but why remains unresolved

**Verified 2026-10-15.** A new **explicitly post-outcome exploratory** analysis of the original AusTraits v7.0.0 Blomberg K programme. This is **NOT** a newly pre-registered process discovery, not external validation, and not direct evidence of natural selection or an intrinsic evolutionary rate.

## Question

If reproductive and vegetative plant traits are measured on **exactly the same species and the same plant phylogeny**, is there a transferable difference in their estimated phylogenetic K? Can the broad organ category predict the **rank ordering of K in a held-out plant family** as well as — or better than — specific trait identities? And can the already-frozen **homogeneous stationary OU + source-associated observational noise** models reproduce the original-tip organ-category pattern?

**Organ classes (defined only after viewing the original trait K and shared-tip results):**

- **Reproductive morphology:** `fruit_height`, `fruit_length`, `fruit_width`, `seed_dry_mass`, `seed_length`, `seed_width`.
- **Vegetative morphology:** `leaf_area`, `leaf_length`, `leaf_mass_per_area`, `leaf_width`, `petiole_length`, `plant_height`.

These are morphometric/functional categories, **not observed reproductive fitness or pollinator selection**. The 12-trait source-calibration cohort excludes `seed_height` by its original K-blind source coverage rule.

## Finding 1 — Matched exact-taxon and exact-tree reproductive K advantage

Frozen exact-source support: 760 source-qualified family×two-trait pairs among 42 families. All original 24 K batches [#38674635870](https://github.com/zuizui0223/turnover/actions/runs/38674635870) were recovered and revalidated. Each within-family comparison used the **same original eligible species and phylogenetic tree for both traits**.

The post-outcome [functional organ module workflow #38685668376](https://github.com/zuizui0223/turnover/actions/runs/38685668376) **succeeded** with 5,000 independent-family cluster bootstrap draws.

| Matched-tip, cross-organ K comparison | S3 | Native prune-only |
|---|---:|---:|
| Families supporting at least one cross-organ pair | 34 | 34 |
| Reproductive–vegetative family×pair comparisons | 406 | 397 |
| **Reproductive K higher** | **313 / 406 (77.09%)** | **314 / 397 (79.09%)** |
| 34-family cluster bootstrap 95% interval, pair-weighted | **66.20–86.01%** | **71.00–86.09%** |
| **Equal-family average reproductive-K advantage** | **74.73%** | **75.84%** |
| Equal-family bootstrap 95% interval | **64.30–84.36%** | **67.42–84.06%** |
| Distinct reproductive×vegetative named-trait pair types | 36 | 36 |
| Equal 36-pair-type descriptive win mean | 81.74% | 81.53% |
| ≥5-family pair types | 29 | 28 |

Among **397 cross-organ pair identities valid on both tree treatments**, **290** show reproductive K higher **on both**, **66** vegetative K higher **on both**, and **41** disagree across trees. Comparisons inside the *same* organ class do not enter these percentages.

### Robustness to one data-rich source and to individual trait selection

| Reproductive K higher, same matched tree | S3 | Prune |
|---|---:|---:|
| **Exclude all pairs involving seed dry mass (Kew SID concern)** | **263/344 (76.45%)** | **268/337 (79.53%)** |
| Exclude all pairs involving leaf area (known leaf vs leaflet/source ambiguity) | 291/380 (76.58%) | 295/374 (78.88%) |
| **Fruit traits only versus vegetative traits** | **149/193 (77.20%)** | **150/189 (79.37%)** |
| **Seed traits only versus vegetative traits** | 164/213 (77.00%) | 164/208 (78.85%) |

Removing **any one** of the 12 named traits leaves at least ~75.6% of surviving cross-organ comparisons oriented reproductive higher on S3 and prune. This argues against a **single source/trait** explaining the entire *descriptive* advantage, but **does not eliminate shared primary-dataset reuse, trait class-level protocol effects, covariation or biological confounders**.

## Finding 2 — Genuine leave-one-plant-family-out predictive transfer *within the same compilation*

For each of 42 folds, **all K outcomes from one entire family were excluded from model fitting**. Training uses the other 41 families and the same matched-tip 12-trait pair comparisons. Prediction asks whether trait A has higher K than trait B in that held-out family. Classification of exactly 50:50 predictions is scored as **half-credit**, not arbitrarily as one label.

Models have frozen, non-tuned predictions: source-blind other-family global empirical lexical sign rate (with Laplace smoothing), a single reproductive-vs-vegetative logistic contrast (ridge C=1, no intercept), twelve named trait Bradley–Terry style scores (ridge C=1, no intercept), and same named-pair Laplace-smoothed rate. **No held-out-family K effect enters any training feature, source calibration or prediction.**

| LOFO metric, all native supported family×pair comparisons | S3 (760 pairs) | Prune (747 pairs) |
|---|---:|---:|
| Pooled other-family baseline accuracy | 52.63% | 53.82% |
| **Single reproductive–vegetative module model accuracy** | **64.47%** | **65.46%** |
| 12 separately estimated trait identity scores accuracy | 64.47% | 66.00% |
| Exact named-pair training frequency model accuracy | 63.75% | 65.66% |
| Pooled baseline Brier loss (**lower is better**) | 0.25062 | 0.25017 |
| **Organ module Brier loss** | **0.21378** | **0.20671** |
| Full 12-named-trait Brier loss | 0.21792 | 0.21156 |
| Exact pair-specific Brier loss | 0.22662 | 0.21879 |
| **Organ module Brier gain versus baseline** | **+0.03685** | **+0.04347** |
| 42-family bootstrap 95% CI for module Brier gain | **+0.00433 to +0.06388** | **+0.01946 to +0.06338** |

The **simple six-versus-six organ class** performs almost as well in held-out families as the fuller individual-trait model; its Brier score is slightly lower on both trees, **but that small difference is not established as a statistically robust head-to-head victory**. Proper scoring remains improved versus the trivial pooled sign prior in family-resampled intervals. The organ classifier's ~65% ALL-pair hard-sign accuracy includes within-organ predictions with no class contrast (p=0.5 and half-credit); its performance on the **cross-organ pairs alone** is summarized by Finding 1.

**Limit:** This is only *family-held-out* cross-validation within AusTraits; original primary data sources can be shared between distinct families and trait definitions, and observations are not a fully external confirmation set. A Bradley–Terry trait-score prediction across *different pair-specific species intersections* does not establish a universal 12-trait hierarchy on one identical global set of species.

## Finding 3 — Original-tip homogeneous OU plus calibrated source heterogeneity does not reproduce the organ advantage under the tested models

A **different** source-null comparison is possible using the pre-existing frozen [249 original family×trait systems / exact tree and source-noise OU simulation #37785257795](https://github.com/zuizui0223/turnover/actions/runs/37785257795). **These simulations use each trait's ORIGINAL separate species/tip support, not the matched 760-pair tip sets above.** We therefore compare each scenario to the **observed original 410 cross-organ family×pair comparisons**, never to the matched-tip percentages.

The [12-condition exploratory posterior predictive model-adequacy workflow #38685916126](https://github.com/zuizui0223/turnover/actions/runs/38685916126) **succeeded**, validating every source simulation system against the original published K on its **rounded K scale** (rather than spuriously comparing rounded K log to pre-rounding original logK).

| Original separate-tip pair-weighted statistic | S3 | Prune |
|---|---:|---:|
| Observed reproductive K higher, 410 cross-organ pairs | **302/410 (73.66%)** | **330/410 (80.49%)** |
| Homogeneous OU + *trait-global* K-blind source heterogeneity: scenario-mean range | **63.21–64.34%** | **65.63–67.67%** |
| Homogeneous OU + *system-local* K-blind source heterogeneity: scenario-mean range | **57.83–58.26%** | **60.67–61.19%** |
| Number of these 12 model×OU-strength×tree tests where observed > model 97.5% null quantile | **6/6 for S3** | **6/6 for prune** |

Original 410-pair **equal-family** observed rates were **75.13% S3 / 80.24% prune**, and also exceeded the null 97.5th quantile under each tested scenario. Monte Carlo one-sided tail values from 256 draws were 0.00389–0.01556, but are **NOT preregistered confirmatory p-values**: the biological class hypothesis was chosen after viewing K outcomes and all 12 cases share the same discovery data and similar null assumptions.

**Important logical distinction:** The earlier **predeclared scalar LOFO rank-gain statistic** was reproduced by homogeneous OU plus trait-level source observation heterogeneity, so `RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES` **still stands**. This new *post-outcome* organ identity statistic is a different model-adequacy target. Matching *how much* trait rank structure exists does not necessarily predict *which functional organ category* has greater K.

The tested source-OU models assume independent latent trait processes, fixed source-dispersion point estimates and simplified observation covariance; their failure to reproduce this post-outcome feature **does not identify true trait-specific OU alpha, adaptive constraint, stabilizing selection or evolutionary rate**.

## Ecological interpretation, alternative mechanisms and next discriminators

The defensible positive, **descriptive and cross-validated** ecological pattern is:

> On identical species and phylogenies, seed and fruit morphological traits more often exhibit stronger phylogenetic signal than leaf and plant-height traits across the sampled plant families. The organ-category contrast transports some sign-prediction information to unseen families within AusTraits, while tested homogeneous evolutionary models with source-associated observation heterogeneity fail to predict its magnitude on original separately sampled tips.

**Biological hypotheses consistent with, but NOT proved by, these observations:** (a) stronger constraints on reproductive morphology, (b) greater functional/environmental lability of leaf/vegetative morphology, (c) differences in phenotypic plasticity and within-species variability, and (d) evolutionary covariance/trait syndrome structure. **Equally necessary observation explanations:** (e) organ-specific dataset composition, (f) trait protocols, derivation/uncertain dry seed-mass conversions, (g) correlation among source records and original taxa, and (h) phylogeny errors and uneven family/trait support.

**Necessary next discriminator:** New primary measurement sources with demonstrably independent original records and standardized organ protocols, plus matched species, family and tree support; jointly model trait covariance and source-level error, rather than regarding current TRY v7 (not source-qualified) as independent confirmation. The earlier original BIEN 201-system rho analysis remains scientifically closed.

## Reproducibility

- [Exploratory post-outcome functional module protocol](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_k_functional_module_portability_v0_1.json)
- [Verified module/LOFO 42-family whole-holdout CI #38685668376](https://github.com/zuizui0223/turnover/actions/runs/38685668376)
- [Verified original-tip OU+source process posterior predictive check #38685916126](https://github.com/zuizui0223/turnover/actions/runs/38685916126)
- [Original 760 matched-tip K #38674635870](https://github.com/zuizui0223/turnover/actions/runs/38674635870)
- No trait values, species names or measurement IDs were stored in the new module results.
