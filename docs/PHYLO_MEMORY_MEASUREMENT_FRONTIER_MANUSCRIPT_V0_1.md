# Manuscript skeleton — The phylogenetic-memory measurement frontier

## Working title

**Trait representation sets a measurement frontier for phylogenetic memory**

Alternative:

**Equal phylogenetic memory signals are not equally measurable across trait representations**

## Question

If the true distance–dissimilarity association is held constant, which properties of a real comparative sampling design determine whether that signal can actually be recovered?

This is an outcome-free methods study. It uses only known-truth simulations on real family × trait phylogenetic geometries. No observed trait-memory rho enters any result.

## Data geometry

722 prequalified BIEN family × trait geometries:
- 120 plant families
- 25 traits
- S3 and prune-only tree treatments
- 443 continuous-scalar systems
- 279 nominal-categorical systems

Every system is challenged with the same benchmark Spearman rho = 0.15 and the same frozen recovery criteria.

## Main result 1 — recoverability is representation-dependent

Overall: 255/722 = 35.3% recover the common benchmark.

Continuous scalar:
- 249/443 = 56.2%

Nominal categorical:
- 6/279 = 2.15%

Pre-frozen logistic model:
`PASS ~ semantic_class * z_log(n_species) + z_prune_fraction`

Key effects:
- categorical coefficient = -4.74
- family/trait cluster-bootstrap 95% interval = [-26.58, -3.61]
- OR at mean sampling ≈ 0.0087
- +1 SD log species count OR ≈ 5.79
- +1 SD native prune-tip fraction OR ≈ 1.75
- categorical × log species coefficient = -1.45

Pseudo-R² ≈ 0.386.

Interpretation: more species and more backbone-native tips improve measurement, but representation changes the measurement frontier itself.

## Main result 2 — categorical failure begins at calibration

The v0.2 mechanism decomposition separates two stages:

1. **Calibration ceiling:** can the frozen generator + realized tree + estimator attain rho=0.15 anywhere on the frozen lambda grid?
2. **Recovery noise:** if calibration succeeds, does the evaluation sample recover the benchmark accurately enough?

Novel systems with full calibration diagnostics: 683.

### Continuous scalar
- no bracket: 83/418 = 19.9%
- calibrated: 335
- S3 PASS: 249/418 = 59.6%
- recovery failure after calibration: 86/335 = 25.7%
- median maximum pilot rho among no-bracket systems = 0.124

### Nominal categorical
- no bracket: 251/265 = 94.7%
- calibrated: only 14
- S3 PASS: 6/265 = 2.26%
- recovery failure after calibration: 8/14 = 57.1%
- median maximum pilot rho among no-bracket systems = 0.071

Thus both stages hurt categorical systems, but the dominant bottleneck occurs **before evaluation noise**: most binary/tree geometries cannot bracket the common benchmark under the frozen generator-estimator combination.

Adjusted no-bracket model:
`NO_BRACKET ~ semantic_class + z_log(n_species) + z_prune_fraction`

- categorical OR ≈ 186
- +1 SD log species OR ≈ 0.24
- +1 SD prune fraction OR ≈ 0.70
- pseudo-R² ≈ 0.491

## Main result 3 — the ceiling is broad, not one bad trait

Across the 9 categorical traits:
- 8/9 have no-bracket rates >=80%
- 4/9 are 100%
- median trait no-bracket rate = 96.8%
- minimum = 71.4%

Across 83 families represented by at least two categorical systems:
- median family no-bracket rate = 100%
- IQR = 100–100%

Therefore the bottleneck is not attributable to a single categorical trait or a handful of unusual clades.

## Mechanistic interpretation

For a continuous trait, pairwise dissimilarities can occupy many ranks.

For a nominal binary representation, pairwise dissimilarity is only match versus mismatch. Spearman correlation then reduces to a rank correlation between phylogenetic separation and a two-level mismatch indicator. The attainable association is consequently constrained by the realized tree geometry, state balance, and which tip bipartitions the generator can produce.

The observed calibration ceiling is consistent with this rank-information constraint. A future formal ceiling derivation can sharpen this mechanism, but the empirical known-truth result does not depend on that derivation.

## What the paper does NOT say

It does not say:
- categorical biological traits are less conserved;
- continuous traits evolve more phylogenetically;
- failed systems have weak real signal;
- rho=0.15 is a universal biological threshold.

It says:
- under the same known true benchmark and the same estimator family, representation and sampling geometry determine whether a phylogenetic-memory signal is measurable;
- treating continuous and nominal categorical traits as equally powered in comparative distance–dissimilarity analyses can be badly misleading.

## Practical implication

Comparative analyses should perform **system-specific known-truth recoverability checks before interpreting absence or heterogeneity of phylogenetic memory**.

For continuous traits, increasing phylogenetic sampling can materially move systems across the measurement frontier.

For nominal categorical traits under binary mismatch + Spearman, increasing n alone often does not solve the problem because the primary ceiling is representational/geometric rather than merely sampling variance.

## Publication boundary

Primary evidence is fully outcome-free:
- frozen known-truth simulations;
- pre-frozen predictors;
- real sampling geometries;
- no observed trait values;
- no observed memory-loss rho.

The closed BIEN empirical trait-memory paper is a separate biological paper. This methods paper should not import its biological family-repeatability result as evidence.
