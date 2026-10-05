# Novelty boundary — truth accessibility in phylogenetic-signal simulations

## Closest prior work

### Fritz & Purvis (2010)
Fritz, S. A. & Purvis, A. *Selectivity in mammalian extinction risk and threat types: a new measure of phylogenetic signal strength in binary traits.* Conservation Biology 24:1042–1051. doi:10.1111/j.1523-1739.2010.01455.x.

Contribution relevant here:
- established a dedicated phylogenetic-signal statistic for binary traits;
- calibrated binary signal against random and Brownian-threshold expectations;
- showed that sample size and trait prevalence affect binary-trait performance.

Boundary:
- the paper evaluates a binary-specific statistic under specified generative null/reference models;
- it does not decompose whether a fixed requested effect size is structurally realizable, generator-accessible, and recoverable on each realized tree.

### Münkemüller et al. (2012)
Münkemüller, T. et al. *How to measure and test phylogenetic signal.* Methods in Ecology and Evolution 3:743–756. doi:10.1111/j.2041-210X.2012.00196.x.

Contribution relevant here:
- showed by simulation that signal metrics differ in sensitivity to sample size, topology and the assumed evolutionary model;
- emphasized that evolutionary interpretation of a signal statistic is model-dependent.

Boundary:
- the focus is comparative performance of signal indices;
- a generating model is treated as the mechanism that supplies simulated truth, rather than as a separate accessibility gate that can itself fail to assign the requested statistic.

### Borges et al. (2019)
Borges, R. et al. *Measuring phylogenetic signal between categorical traits and phylogenies.* Bioinformatics 35:1862–1869. doi:10.1093/bioinformatics/bty800.

Contribution relevant here:
- developed the categorical δ statistic;
- explicitly noted that binary D relies on a Brownian-threshold construction and that this model may not suit categorical traits without a continuous latent liability;
- evaluated categorical signal across sample size and evolutionary scenarios.

Boundary:
- motivates representation-appropriate categorical methods;
- does not hold one distance-based estimator and target fixed while separating state-space realizability from generator accessibility.

### Yao & Yuan (2025)
Yao, L. & Yuan, Y. *A Unified Method for Detecting Phylogenetic Signals in Continuous, Discrete, and Multiple Trait Combinations.* Ecology and Evolution 15:e71106. doi:10.1002/ece3.71106.

Contribution relevant here:
- developed a unified distance-based M statistic for continuous and discrete traits;
- simulated discrete traits with a Markov model;
- explicitly identified the small number of possible distances for low-state categorical traits, especially binary traits, as a source of lower statistical power.

Boundary:
- therefore this paper must **not** claim novelty for the generic statement that binary/discrete traits can have lower power;
- the new result here is that low recoverability can be localized to the truth-assignment route even when the binary state space demonstrably contains configurations far above the target.

### General simulation-study design

Morris, White & Crowther (2019, *Statistics in Medicine*, DOI 10.1002/sim.8086) formalized the ADEMP framework: aims, data-generating mechanisms, estimands, methods and performance measures. They emphasize that the relevant truth is normally a parameter or quantity implied by the data-generating mechanism; when a target is not a direct DGM parameter, they discuss estimating that truth from a very large simulation.

Williams et al. (2024, *Methods in Ecology and Evolution*, DOI 10.1111/2041-210X.14415) extend simulation-study guidance specifically for ecology and evolution, emphasizing transparent reporting of data-generating mechanisms, implementations, code, Monte Carlo uncertainty and prospective registration.

Boundary:
- this paper must **not** claim to discover the general principle that simulation truth depends on the data-generating mechanism, nor the need to preregister and report simulation designs transparently;
- the contribution is narrower and operational: before power or recovery is interpreted, an explicitly requested target statistic may need to pass separate **realizability** and **generator-accessibility** gates on the realized design.

### DGM-dependent power and nominal-versus-realized effects

Simulation-based power tutorials already emphasize that data-generating-mechanism features can materially alter power even at similar nominal effect sizes (e.g. Rudolph, Goin & Stuart 2020, *American Journal of Epidemiology*). Recent simulation-based power work also distinguishes fixed effect specifications from the effect sizes actually realized in simulated trials.

Boundary:
- this paper must **not** claim that DGM choice affecting power, or nominal and realized effect sizes differing, is newly discovered;
- the new inferential move is to make **generator accessibility to a requested summary target** an explicit pass/fail object between structural feasibility and estimator recovery;
- the paired OU→Mk2 intervention is useful because it changes generator accessibility while holding the realized trees, target statistic and estimator fixed.

### Feasible-correlation checks in synthetic-data generation

Fialkowski & Tiwari (2019, *The R Journal*, DOI 10.32614/RJ-2019-022) developed `SimCorrMix` for generating correlated continuous, binary, ordinal and count variables. The package explicitly calculates feasible correlation boundaries and provides input checks for requested dependence structures.

Boundary:
- this is a clear precedent for **structural feasibility checking**, so the present paper must **not** claim that verifying whether a requested effect can exist is itself a new idea;
- those generators primarily test whether a requested dependence structure is feasible under specified supports and marginals;
- the present contribution is the next separation: a target can be structurally feasible on the realized design and still be **generator-inaccessible** under a particular stochastic evolutionary mechanism, after which downstream recovery remains a third question;
- the 276/276 realizability result plus the OU→Mk2 paired intervention is the evidence that feasibility and generator accessibility are empirically distinct, not merely differently named checks.

### Simulation-based calibration

Simulation-based calibration (SBC) checks whether an inference algorithm is calibrated on data generated from a specified generative model; posterior SBC further asks whether calibration holds in the region relevant to observed data (Säilynoja et al. 2026, *Statistics and Computing*, DOI 10.1007/s11222-026-10825-9).

Boundary:
- SBC tests inferential self-consistency **conditional on a generative model**;
- the present problem occurs one logical step earlier when a user declares a target summary such as rho=0.15: the representation × geometry × generator may fail to assign that target at all, even before estimator calibration is considered.

## What the present study adds

The contribution is not a new phylogenetic-signal statistic. It is a diagnostic framework for known-truth simulation studies.

For a declared target effect, distinguish:

1. **structural realizability** — does the representation × realized tree contain an attainable state configuration at the target?
2. **generator accessibility** — can the chosen stochastic generator place the system near that target while satisfying its validity rules?
3. **estimator recovery** — once the target is successfully assigned, can finite simulation recover it?

The empirical leverage is that these gates separate sharply on the same real geometries:

- 220/220 categorical OU no-bracket systems have a realizable one-transition edge split above rho = 0.15;
- median maximum edge-split rho is 0.773, versus median maximum OU-grid rho 0.0979;
- 195/220 never reach 0.15 anywhere on the finite OU grid;
- 25/220 reach it only after the binary valid-replicate fraction falls below 0.90;
- stronger OU latent memory increases measured rho while simultaneously collapsing polymorphism.

Thus a simulation can be labelled “known truth” even though the requested truth is not accessible to the chosen generator on the realized design.

## Claim boundary

Safe:
- known-truth simulation requires an accessibility audit when representations impose constrained state spaces;
- latent continuous threshold generators can create a truth-accessibility bottleneck for binary distance-based signal;
- generator failure can be mistaken for low estimator power if calibration and recovery are not separated.

Do not claim:
- checking attainable/feasible correlation bounds is newly invented here;
- data-generating mechanisms affecting power is newly discovered here;
- nominal and realized simulated effect sizes are always identical;
- categorical traits are intrinsically less conserved;
- binary traits are intrinsically incapable of rho = 0.15;
- Mk2 is universally the correct evolutionary model;
- two-valued distances causing lower power is newly discovered here.

## Generator substitution result

The pre-frozen Mk2 comparison is now complete. Holding the trees, binary mismatch, Spearman rho and rho = 0.15 target fixed:

- latent-OU threshold no-bracket = **220/276 (79.7%)**;
- symmetric Mk2 no-bracket = **170/276 (61.6%)**;
- **51/220 (23.2%)** original OU no-bracket systems are rescued to Mk2 calibration;
- only **1/56** originally OU-calibrated systems becomes a new Mk2 calibration failure;
- Mk2 S3 PASS = **69/276 (25.0%)**.

The paired 51-versus-1 asymmetry makes generator choice an identified source of accessibility loss. But Mk2 does not remove the problem: 61.6% remain no-bracket.

The novelty therefore should not be phrased as “threshold generators are bad.” The result is that **generator choice is part of truth assignment**, and its effect can be separated empirically from both the representational state space and downstream recovery.

## State-balance mechanism result

For binary mismatch, the distance-rank association has the exact factorization

`rho = Delta_rank * sqrt(p(1-p))`,

where `p` is mismatch-pair prevalence and `Delta_rank` is the standardized separation of phylogenetic-distance ranks between mismatch and match pairs.

Because `sqrt(p(1-p)) <= 0.5`, **Delta_rank >= 0.30 is necessary for rho = 0.15 to be attainable at any state balance**. The implementation reproduces this identity to maximum absolute error **8.88e-16**.

The v0.5 test keeps the same Mk2 states and distance ranks and removes only this exact attenuation term. A live-BIEN provenance drift discovered during the first execution is handled by a frozen, outcome-blind geometry identity gate: four systems are HOLD and remain explicitly in population accounting.

Among **272 exact geometry matches**:
- Mk2-rho reference = **167 no-bracket / 105 calibrated**;
- balance-normalized Delta_rank = **117 no-bracket / 155 calibrated**;
- **50/167 = 29.9%** of matched Mk2-rho no-bracket systems are rescued;
- **0/105** previously calibrated matched systems become new failures.

Accounting for the four HOLD systems without imputation bounds the full-population balance-normalized no-bracket rate at **42.4–43.8%** and the rescue fraction among the original 170 Mk2-rho no-bracket systems at **29.4–31.2%**.

Thus state balance is a second identified mechanism, but it does not exhaust the failure. Under the pre-frozen stop rule, the remaining ~42–44% no-bracket fraction is an unresolved generator–partition–geometry alignment remainder, not a target for further estimator search on these same systems.

## Likely journal positioning

The strongest framing is a general simulation-design principle demonstrated with a comparative-ecology stress test:

> **A declared simulation truth is not automatically an assigned truth. Constrained representations require separate audits of structural realizability, generator accessibility and downstream recovery.**

The closest literature already separates DGM, estimand and performance, already checks feasible correlation ranges for constrained variables, already warns that discrete phylogenetic traits can have lower power, and already validates inference under fixed generative models. The defensible novelty is therefore **not** feasibility checking alone. It is the **sequential assignability audit**, especially the distinction between feasibility and generator-specific accessibility, and its empirical demonstration: the same declared target can be structurally realizable, inaccessible to one generator, partly rescued by a representation-appropriate generator, further attenuated by state balance, and still fail recovery after assignment.

A targeted literature search through 2026 did not identify a prior ecology/evolution or general simulation-methods paper that operationalizes these three gates as the object of a power/recoverability study. That is a novelty boundary, not proof of absence from the entire literature.

The paper should therefore lead with simulation methodology and use phylogenetic memory as the concrete system, rather than lead with a new plant-trait or phylogenetic-signal estimator claim.
