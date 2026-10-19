# Trait-specific source dispersion and an OU observation-heterogeneity stress test

**Date:** 2026-10-08

## Empirical source-only evidence (completed)

Frozen before looking at the dispersion outputs:
`data/austraits_k_cross_source_dispersion_design_v0_1.json`

Reproduced on the original 254 family×trait systems/42 plant families/13 traits from AusTraits v7.0.0. The [source-dispersion GitHub Action](https://github.com/zuizui0223/turnover/actions/runs/37784017236) passed and persisted the full 254-system and 13-trait aggregated estimates, without species/raw-observation IDs or any empirical K values.

For a species with >=2 positive-source datasets, compute the sample variance of *dataset-specific median log-trait values*. For each family×trait system with >=5 such species, take their median source variance, and divide by the variance of the original log-species medians across all species in that family×trait system. Then summarize system-relative ratios across families by their median (family-unweighted).

| Trait | Median source variance / interspecific variance | Calibrated family systems |
|---|---:|---:|
| fruit_height | 0.0040 | 4 |
| fruit_length | 0.0023 | 29 |
| fruit_width | 0.0060 | 16 |
| leaf_area | 0.0835 | 6 |
| leaf_length | 0.0398 | 40 |
| leaf_mass_per_area | **0.2461** | 5 |
| leaf_width | 0.0230 | 38 |
| petiole_length | 0.0074 | 18 |
| plant_height | 0.0786 | 35 |
| seed_dry_mass | 0.0181 | 15 |
| seed_height | 0.0870 | **2 — not qualified** |
| seed_length | 0.0070 | 21 |
| seed_width | 0.0733 | 17 |

**12 of 13 traits passed the previously frozen cross-dataset coverage gate and the positive-source dispersion calibration.** Seed height does not have sufficient family spread. The future model therefore compares **249 original systems / 42 families / 12 traits** on both sides; no observed K-driven exclusions are allowed. 244 of these 249 systems have >=5 multi-dataset species for local ratio estimation. The other 5 receive the same K-blind trait-global median imputation only in the `system_local` model.

## Matched-graph observed target (computed before opening OU+source outcomes)

Recomputing the exact original LOFO within-family K rank gain on the observation-error-eligible 12-trait subset gives **+8.0083% S3 / +15.5766% prune-only**, versus **+8.0818% / +15.3072%** on the original 13-trait graph. There are 249 systems from the same 42 families, and every family retains >=2 traits. The source-coverage gate therefore did **not** erase the observed rank-prediction phenomenon. These are observed-only results, **not** a source-noise process-null verdict.

## Post-dispersion K-blind influence audit

The original observed K and the source-calibrated OU process model remain unchanged. A separate **post-dispersion** audit removes each contributing family in turn from the source-error median (without refitting K, reselecting models, or retuning noise):

| Trait | Full median source/among-species variance | Range of leave-one-family-out median | Calibrated families |
|---|---:|---:|---:|
| leaf_mass_per_area | 0.24611 | 0.19840–0.27114 | 5 |
| leaf_area | 0.08354 | 0.06141–0.10568 | 6 |
| leaf_length | 0.03982 | 0.03972–0.03992 | 40 |
| plant_height | 0.07862 | 0.07813–0.08034 | 35 |
| fruit_length | 0.00225 | 0.00211–0.00228 | 29 |
| fruit_height | 0.00397 | **0–0.00795** | 4 |

Of **246** systems with a calibrated within-species cross-dataset variance ratio on the original 254-system graph, **29 (11.79%)** have a **median source variance of zero**. This includes 2/4 fruit-height systems, 6/29 fruit-length systems, and 5/18 petiole-length systems. Such exact zeros do **not** establish no measurement error: reporting precision, truly repeated equal values, shared underlying primary observations across source compilations or genuine low variability are alternatives. The source-only archive does not distinguish these explanations.

Among the originally calibrated systems, a small number have ratios greater than one (e.g., seed_width/Casuarinaceae 2.3723; leaf_length/Casuarinaceae 2.0841; leaf_area/Orchidaceae 1.4697). As pre-frozen, these are not capped or deleted based on their magnitudes.

The median ratios are **point-input error envelopes**, not posterior distributions or precise known variance parameters. The leave-one-family-out audit quantifies family-support sensitivity but is *not* new calibration of the frozen primary OU+source scenarios. Do not rerun the primary comparison under selectively chosen extremes and represent it as preregistered confirmation.

[Reproducible influence audit](https://github.com/zuizui0223/turnover/actions/runs/37786690562), based only on frozen source-dispersion output.

## What this does **not** establish

This is not a measured independent *instrument error variance*. Same-species data from different AusTraits datasets may cover different populations, years, environments and protocols. Dataset replication is not guaranteed independent biological replication; source compilation can duplicate underlying field measurements. The ratio may therefore contain real intraspecific biology or systematic source artifacts.

The large contrast between leaf-mass-per-area and fruit-length source dispersion is a plausible *alternative data-generating channel* for trait-level K portability, not evidence yet that the observed phylogenetic ordering was caused by source error.

## Pre-frozen process-null design

The source-plus-OU forward model was independently frozen **before opening the magnitude output** at `data/austraits_k_source_dispersion_ou_null_design_v0_1.json` (after previous rho/K and pure OU outcomes):

- Exact frozen source-native S3/prune species trees and source-native K estimator.
- Stationary, *identically parameterized OU* latent traits at the original three `c = alpha T_ref = 0.25, 1, 4` values.
- Additional independent Gaussian tip dispersion with `SD = sqrt(eta × realized latent tip variance)`, where each `eta` comes from the above K-blind source audit.
- `trait_global`: same named-trait eta for all families, so stable observed trait noise alone might create portable trait K ranking.
- `system_local`: family×trait source eta when supported, otherwise pre-frozen trait-median fallback.
- For each exact tree axis, model and alpha, 256 independent draws per family×trait system (3 alphas × 2 noise models × 2 tree axes).
- Primary outcome is leave-one-family-out *within-family* trait rank gain, recomputed on the **same 249-system observed graph**. Conditional family ICC is a distinct secondary outcome, not an additional free path to claiming primary success.
- The most conservative interpretation applies: if **any** predeclared scenario on **either** tree can accommodate the observed rank gain, reject the strong conclusion that such portability is beyond these particular homogeneous OU + source-dispersion envelopes.
- Post-outcome exploration cannot be redescribed as prospective discovery.

The new [real-tree smoke-test Action](https://github.com/zuizui0223/turnover/actions/runs/37785073697) and [249-system production Action](https://github.com/zuizui0223/turnover/actions/runs/37785257795) were submitted. The simulation code, data-source lock, source ratio lock, exact K identification and decision rule are versioned. **No inference about whether this alternative succeeds can be made until its jobs complete and final artifacts are validated.**

## What the fixed source-noise model predicts mathematically

The specified model is `Y_tip = X_tip + sqrt(eta * s_X^2) * epsilon_tip`, with `epsilon_tip iid N(0,1)` and `s_X^2` the realized across-tip sample variance of latent OU states. Conditional on those latent tips,

`E[s_Y^2 | X] = (1+eta) s_X^2`.

Consequently, the noise component's share of **expected total sample variance** is `eta/(1+eta)`: approximately 19.7% for the globally calibrated leaf-mass-per-area eta of 0.2461, 7.7% for leaf area eta 0.0835, 3.8% for leaf length eta 0.0398, and 0.22% for fruit length eta 0.00225. These are **model-implied fractions, not measured independent error fractions**.

The key distinction is that Blomberg K is sensitive to the **phylogenetic distribution** of that extra variance, not just its magnitude. On a star phylogeny with equal terminal branch lengths, `C = t I`, the GLS mean is the arithmetic mean and the K normalization simplifies to exactly `K=1` for every nonconstant tip-value vector. In that limiting geometry, independent tip noise alone cannot generate portable K rankings. A source-noise explanation for the empirical K architecture therefore necessarily acts through the combination of source error and **nonstar empirical tree covariance**.

This is a pre-outcome theoretical check, **not evidence** that the real 249-system OU+source simulations meet the frozen primary rank-gain criterion.

## Scientific interpretation boundary

This tests *independent source-associated tip dispersion*. It does not test correlated traits, systematic dataset-level biases shared across species, or lab-verified repeatability error. Those remain distinct and untested. Even a successful null reproduction would provide compatibility with the modeled source channel, not demonstrate that source error caused the observed K pattern.
