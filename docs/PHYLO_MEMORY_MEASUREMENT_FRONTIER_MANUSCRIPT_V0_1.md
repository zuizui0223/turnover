# Manuscript skeleton — The phylogenetic-memory measurement frontier

## Working title

**Trait representation creates a measurement frontier for phylogenetic memory**

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

Interpretation: additional sampling and backbone-native coverage help overall, but representation changes the recoverability surface itself.

## Main result 2 — categorical failure is concentrated at calibration

The v0.2 mechanism decomposition separates two stages:

1. **Calibration accessibility:** can the frozen generator + realized tree + estimator bracket rho=0.15 anywhere on the frozen lambda grid?
2. **Recovery noise:** if calibration succeeds, does the evaluation sample recover the benchmark accurately enough?

Novel systems with full calibration diagnostics: 683.

### Continuous scalar
- n = 407
- no bracket: 60/407 = 14.7%
- calibrated: 347
- S3 PASS: 293/407 = 72.0%
- recovery failure after successful calibration: 54/347 = 15.6%
- median maximum pilot rho among no-bracket systems = 0.106

### Nominal categorical
- n = 276
- no bracket: 220/276 = 79.7%
- calibrated: 56
- S3 PASS: 18/276 = 6.52%
- recovery failure after successful calibration: 38/56 = 67.9%
- median maximum pilot rho among no-bracket systems = 0.0979

Thus categorical systems are penalized at both stages, but the largest loss occurs before evaluation: four-fifths of categorical systems fail to bracket the common benchmark under the frozen generator–tree–estimator combination.

Adjusted no-bracket model:
`NO_BRACKET ~ semantic_class + z_log(n_species) + z_prune_fraction`

- categorical OR ≈ 18.4
- +1 SD log species OR ≈ 1.36
- +1 SD prune fraction OR ≈ 1.01
- pseudo-R² ≈ 0.339

Crucially, **no-bracket is not identical to a hard mathematical ceiling**. Among categorical no-bracket systems, 88.6% have maximum grid median <0.15, but 11.4% reach or exceed 0.15 somewhere on the grid without satisfying the frozen bracketing rule. The next mechanism test therefore distinguishes representational/tree attainability from generator accessibility.

## Main result 3 — the bottleneck is broad but heterogeneous

Seven categorical traits occur in the 683-system v0.2 population.

Trait-level no-bracket rates:
- range = 50.0–86.9%
- median = 60.0%
- 3/7 traits are >=80%
- 0/7 are 100%

The strongest trait-level bottlenecks are:
- whole plant woodiness: 86.9%
- whole plant vegetative phenology: 84.2%
- whole plant growth form: 80.3%

Across 100 families represented by at least two categorical systems:
- median family no-bracket rate = 100%
- IQR = 66.7–100%

Therefore the representation penalty is widespread across families but not uniform across traits. This is more consistent with a **representation × realized geometry measurement frontier** than with a single universal categorical ceiling.

## Mechanistic test — frozen before opening results

The original v0.3 proposal used an unconstrained upper bound that labels arbitrary pairwise distances as match/mismatch. Before any v0.3 result was computed, that construction was recognized as non-realizable for binary tip states: with distinct pair-distance ranks its optimum approaches sqrt(3/4) ≈ 0.866 and is therefore non-discriminating for a rho=0.15 benchmark.

v0.3.1 replaces it with a realizable one-transition state family:

- every edge of the realized S3 tree defines a descendant-clade-versus-rest binary split;
- every such split is an attainable tip-state pattern under a single state transition;
- exact Spearman/point-biserial rho is computed for every edge split;
- the maximum edge-split rho is compared with the frozen OU-threshold generator maximum.

This separates two mechanisms among categorical no-bracket systems:

1. **single-transition structural limitation:** even the best one-edge split has rho < 0.15;
2. **generator accessibility limitation:** a one-edge split can reach rho >= 0.15, but the frozen OU-threshold process does not bracket it.

The edge-split maximum is intentionally not claimed to be a global upper bound over arbitrary multi-transition binary patterns.

## Mechanistic interpretation

For a continuous trait, pairwise dissimilarities can occupy many ranks. For a nominal binary representation, pairwise dissimilarity is only match versus mismatch, so Spearman correlation is a rank association between phylogenetic separation and a two-level mismatch indicator.

The empirical result already shows that equal target signal is not equally recoverable across representations. The corrected breadth analysis adds an important qualification: categorical measurement failure is not uniform. The relevant object is therefore not “categorical traits are unmeasurable,” but **whether a particular representation can express and recover the target association on a particular realized phylogeny and sampling design**.

## What the paper does NOT say

It does not say:
- categorical biological traits are less conserved;
- continuous traits evolve more phylogenetically;
- failed systems have weak real signal;
- every categorical system has a hard rho ceiling below 0.15;
- rho=0.15 is a universal biological threshold.

It says:
- under the same known true benchmark and the same estimator family, representation and sampling geometry strongly determine measurability;
- categorical systems are much more likely to fail both calibration and recovery;
- the size of that penalty varies across real trait × family geometries;
- absence or heterogeneity of measured phylogenetic memory cannot be interpreted safely without a system-specific recoverability check.

## Practical implication

Comparative analyses should perform **system-specific known-truth recoverability checks before interpreting weak or heterogeneous phylogenetic memory**.

For continuous traits, increasing phylogenetic sampling can materially move systems across the measurement frontier.

For nominal categorical traits under binary mismatch + Spearman, simply increasing n is not demonstrated to solve the calibration problem in the v0.2 decomposition. The next question is whether the lost accessibility is imposed by realizable binary/tree geometry or by the particular generator/estimator route used to represent the same underlying memory.

## Evidence provenance correction

On 2026-10-04, an audit of the cited GitHub Actions artifacts found that the previously committed v0.2 and v0.2.1 summaries did not match their cited artifact contents. The repository result files and this skeleton were corrected to the artifact-backed values before the v0.3.1 mechanism analysis was opened. The v0.1 measurability artifact matched its committed scientific quantities.

## Publication boundary

Primary evidence is fully outcome-free:
- frozen known-truth simulations;
- pre-frozen predictors;
- real sampling geometries;
- no observed trait values;
- no observed memory-loss rho.

The closed BIEN empirical trait-memory paper is a separate biological paper. This methods paper should not import its biological family-repeatability result as evidence.
