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

## Why the Mk2 comparison is decisive

The next pre-frozen experiment holds constant:
- the 276 categorical S3 trees;
- binary mismatch;
- Spearman rho;
- rho = 0.15 target;
- calibration grid size/range;
- pilot and evaluation replication;
- validity and recovery criteria.

Only the state generator changes from latent OU + threshold to symmetric Mk2/ER.

A large paired rescue would therefore isolate generator choice as a causal source of the stage-2 accessibility loss. A weak rescue would instead direct attention toward state-balance and estimator constraints.

## Likely journal positioning

The strongest framing is methodological ecology/evolution rather than a new phylogenetic-signal index:

> **A declared simulation truth is not automatically an assigned truth. Constrained trait representations require separate audits of realizability, generator accessibility and estimator recovery.**

That framing is most naturally aimed at methods/comparative-ecology audiences rather than sold as a new biological result about plant traits.
