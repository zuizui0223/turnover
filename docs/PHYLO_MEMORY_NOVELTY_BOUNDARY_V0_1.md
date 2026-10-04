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

Morris, White & Crowther (2019, *Statistics in Medicine*, DOI 10.1002/sim.8086) formalized the ADEMP framework: aims, data-generating mechanisms, estimands, methods and performance measures. They emphasize that the relevant truth is normally a parameter or quantity implied by the data-generating mechanism, and warn that data-generation tricks can yield data different from what was intended.

Boundary:
- this paper must **not** claim to discover the general principle that simulation truth depends on the data-generating mechanism;
- the contribution is to make that issue operational for constrained comparative representations by separating an explicitly requested effect into structural realizability, generator accessibility and recovery on real phylogenetic geometries.

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

## State-balance mechanism

For binary mismatch, the distance-rank association has the exact factorization

`rho = Delta_rank * sqrt(p(1-p))`,

where `p` is mismatch-pair prevalence and `Delta_rank` is the standardized separation of phylogenetic-distance ranks between mismatch and match pairs.

Because `sqrt(p(1-p)) <= 0.5`, **Delta_rank >= 0.30 is necessary for rho = 0.15 to be attainable at any state balance**.

The active v0.5 test therefore keeps the same Mk2 states and distance ranks and removes only this exact attenuation term. Systems that reach Delta_rank = 0.30 but failed rho = 0.15 isolate state balance as the lost information; systems that still fail 0.30 reveal a deeper alignment limitation between Mk2-generated binary partitions and phylogenetic-distance ranks.

A live-BIEN provenance drift discovered during the first v0.5 execution is handled by a frozen, outcome-blind geometry identity gate: unmatched systems are recorded as HOLD and remain explicitly in population accounting rather than being silently redefined.

## Likely journal positioning

The strongest framing is methodological ecology/evolution rather than a new phylogenetic-signal index:

> **A declared simulation truth is not automatically an assigned truth. Constrained trait representations require separate audits of realizability, generator accessibility and estimator recovery.**

That framing is most naturally aimed at methods/comparative-ecology audiences rather than sold as a new biological result about plant traits.
