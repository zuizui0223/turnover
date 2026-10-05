# Manuscript skeleton — The phylogenetic-memory measurement frontier

## Working title

**Known truth is not automatically assignable in simulation-based power studies**

Alternative:

**Equal phylogenetic memory signals are not equally assignable across trait representations**

## Question

If the true distance–dissimilarity association is held constant, which properties of a real comparative sampling design determine whether that signal can actually be recovered?

This is an outcome-free methods study. It uses only known-truth simulations on real family × trait phylogenetic geometries. No observed trait-memory rho enters any result.

**Central claim:** a requested simulation truth must pass a structural-feasibility audit and be generator-accessible before downstream failure can be interpreted as low statistical power (Fig. 1). A journal-neutral abstract is frozen in `docs/PHYLO_MEMORY_ABSTRACT_V0_1.md`.

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

Interpretation: additional sampling and backbone-native coverage help overall, but representation changes the recoverability surface itself (Fig. 1B).

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

## Main result 4 — a hard one-transition ceiling is excluded but the generator remains inaccessible

The v0.3.1 one-sided structural ceiling test asks whether each realized S3 tree has at least one attainable one-transition binary state at or above rho = 0.15.

Every tree edge defines a realizable one-transition binary state: descendant clade versus all remaining tips. Across all 276 categorical systems:

- **276/276** have at least one one-edge split with rho >= 0.15;
- among the **220 OU no-bracket systems, 220/220** still have a realizable one-edge split above the benchmark;
- median maximum one-edge rho among no-bracket systems = **0.773** (IQR 0.742–0.811);
- median maximum OU pilot rho in the same no-bracket systems = **0.0979**;
- median edge-split minus OU-accessible gap = **0.677** (IQR 0.629–0.728).

Thus the categorical calibration failure is **not a hard binary-state-space ceiling**. Even a single-transition state family can express associations far stronger than the declared target on every realized tree. What fails is access to those states under the frozen latent-OU-plus-zero-threshold generator.

The edge-split maximum is deliberately not a global upper bound over arbitrary multi-transition patterns. It is enough for the present inference because it supplies an explicit realizable witness above rho = 0.15 for every system.

## Main result 5 — stronger latent memory trades off against binary validity

The stored OU calibration grids reveal how generator accessibility fails in the 220 categorical no-bracket systems.

- **195/220 (88.6%)** never reach rho = 0.15 even when low-validity grid points are allowed.
- **25/220 (11.4%)** reach rho >= 0.15 only after the predeclared valid-replicate fraction falls below 0.90.
- No categorical no-bracket system reaches the target at an admissible grid point.
- Median maximum unconstrained pilot rho = **0.0979**; median maximum among admissible grid points = **0.0821**.
- Across systems, increasing lambda raises the pilot effect (median within-system Spearman **+0.767**) while sharply reducing the fraction of replicates retaining a defined binary mismatch effect (median **-0.957**).
- Median valid fraction at the largest lambda is **0.20**.
- In the 60 continuous no-bracket systems, the corresponding valid fraction remains **1.00**.

For binary traits, invalid pilot replicates occur when thresholded tip states become monomorphic. The generator therefore faces an accessibility trade-off: strengthening latent phylogenetic memory tends to increase the desired distance structure while simultaneously erasing the binary variation required to measure it (Fig. 2).

## Main result 6 — a representation-appropriate generator partially rescues accessibility

The v0.4.1 generator-substitution test keeps the categorical S3 trees, rho = 0.15 target, and binary mismatch + Spearman estimator unchanged, but replaces latent-OU thresholding with a symmetric two-state Mk2 process.

Across the same 276 categorical systems:

- OU-threshold no-bracket = **220/276 = 79.7%**;
- Mk2 no-bracket = **170/276 = 61.6%**;
- **51/220 = 23.2%** of original OU no-bracket systems become calibratable under Mk2;
- only **1/56** originally OU-calibrated systems becomes Mk2 no-bracket;
- Mk2 S3 PASS = **69/276 = 25.0%**;
- recovery failure after Mk2 calibration = **37/106 = 34.9%**.

The strongly asymmetric paired transition (51 rescues versus one new failure) establishes that the stage-2 bottleneck is materially **generator-specific**. However, generator substitution is not a complete solution: nearly two thirds of systems still fail calibration under Mk2.

For binary mismatch, ordinary Spearman can be written exactly as

`rho = Delta_rank * sqrt(p(1-p))`,

where `p` is mismatch-pair prevalence. This identifies a narrower second mechanism after generator substitution.

## Main result 7 — state balance independently attenuates accessibility

v0.5 keeps the same Mk2 states and patristic-distance ranks and removes only the exact binary state-balance term. The algebraic factorization is numerically exact (maximum absolute identity error **8.88e-16**).

Four systems were placed in an outcome-free geometry HOLD before their v0.5 statistic was computed. Among the **272 exact geometry matches**:

- Mk2-rho reference = **167 no-bracket / 105 calibrated**;
- balance-normalized Delta_rank = **117 no-bracket / 155 calibrated**;
- **50/167 = 29.9%** of matched Mk2-rho no-bracket systems become calibratable;
- **0/105** previously calibrated matched systems become new failures;
- median mismatch-pair prevalence at Delta_rank calibration = **0.4037**;
- median ordinary rho at the same calibration point = **0.1398**;
- median pilot valid fraction = **1.00**.

The four geometry-HOLD systems comprise three original Mk2-rho no-bracket systems and one calibrated system. Without imputing their outcomes, the full-population balance-normalized no-bracket rate is therefore bounded at **42.4–43.8%**, and the rescue fraction among the original 170 Mk2-rho no-bracket systems is bounded at **29.4–31.2%**.

State balance is therefore an additional, separable accessibility mechanism. It is not a complete explanation: a large residual no-bracket fraction remains after both generator substitution and exact balance normalization. Under the pre-frozen stop rule, that remainder is retained rather than optimized away (Fig. 3).

## Mechanistic interpretation

For a continuous trait, pairwise dissimilarities can occupy many ranks. For a nominal binary representation, pairwise dissimilarity is only match versus mismatch, so Spearman correlation is a rank association between phylogenetic separation and a two-level mismatch indicator.

The combined mechanism results separate three distinct questions. Every categorical tree contains a realizable one-transition state at or above the benchmark, excluding a hard ceiling below it; the latent-OU-threshold generator nevertheless often cannot place probability mass in the target region while retaining measurable polymorphism, and calibrated categorical systems still fail finite-sample recovery more often. The relevant object is therefore not “categorical traits are unmeasurable,” but **whether a declared truth is realizable, generator-accessible, and recoverable for the chosen representation on the realized phylogeny**.

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

For nominal categorical traits under binary mismatch + Spearman, simply increasing n is not demonstrated to solve the calibration problem. The edge-split witness shows that the target itself is available in the binary state space; the OU-grid audit shows that a major loss occurs along the chosen generative path. Mk2 substitution materially improves accessibility, and exact balance normalization rescues another ~30% of the remaining matched no-bracket systems. The approximately 42–44% unresolved remainder is retained under the frozen stop rule rather than pursued through additional estimator or parameter search.

## Evidence provenance correction

On 2026-10-04, an audit of the cited GitHub Actions artifacts found that the previously committed v0.2 and v0.2.1 summaries did not match their cited artifact contents. The repository result files and this skeleton were corrected to the artifact-backed values before the v0.3.1 mechanism analysis was opened. The v0.1 measurability artifact matched its committed scientific quantities.

## Publication boundary

The primary mechanism programme is closed under the pre-frozen v0.5.2 stop rule. Primary evidence is fully outcome-free:
- frozen known-truth simulations;
- pre-frozen targets, grids and recovery rules;
- real sampling geometries;
- sequentially frozen mechanism tests;
- no observed trait values;
- no observed memory-loss rho.

No additional generator, estimator, parameter-grid, target or subgroup search on these 276 categorical systems may strengthen the primary claim. The approximately 42–44% unresolved balance-normalized no-bracket remainder is part of the result.

The closed BIEN empirical trait-memory paper is a separate biological paper. This methods paper should not import its biological family-repeatability result as evidence.


## Primary figure architecture

- **Figure 1:** three-gate assignability framework plus the continuous-versus-categorical recovery contrast.
- **Figure 2:** explicit structural witness versus OU accessibility, followed by effect-ceiling versus validity-collapse decomposition.
- **Figure 3:** sequential OU → Mk2 → balance-normalized rescue, paired rescue/new-failure counts, and recovery after assignment.

The frozen source-backed figure plan is `data/phylo_memory_figure_plan_v0_1.json`; captions are in `docs/PHYLO_MEMORY_FIGURE_CAPTIONS_V0_1.md`. Figure preparation adds no new scientific estimand.
