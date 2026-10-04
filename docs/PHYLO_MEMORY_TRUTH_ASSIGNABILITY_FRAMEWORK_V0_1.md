# Truth assignability framework for phylogenetic-memory simulations

## Why the current result needs a three-stage decomposition

A known-truth recovery study can fail for at least three logically distinct reasons.

1. **Structural realizability** — does the representation × realized tree state space contain any configuration whose target statistic reaches the declared truth?
2. **Generator accessibility** — can the chosen stochastic generator reach and bracket that target with adequate validity over its frozen parameter family?
3. **Estimator recovery** — after a target has actually been assigned, can finite simulation/evaluation recover it under the frozen error criteria?

Calling all three failures “low power” conflates different problems.

## Artifact-backed stage decomposition already available

For the 683 novel systems in the cited v0.2 artifact:

| Representation | n | Generator no-bracket | Calibrated | Recovery fail given calibrated | S3 pass |
|---|---:|---:|---:|---:|---:|
| continuous scalar | 407 | 60 (14.7%) | 347 | 54/347 (15.6%) | 293 (72.0%) |
| nominal categorical | 276 | 220 (79.7%) | 56 | 38/56 (67.9%) | 18 (6.52%) |

Thus categorical systems lose information at both stages 2 and 3, but stage 2 is the larger bottleneck.

## v0.3.1 structural-realizability result

For every categorical S3 tree, every edge defines a realizable one-transition binary configuration: descendant clade = state 1, all remaining tips = state 0. The exact binary-mismatch Spearman rho was computed for every such edge.

Across all **276 categorical systems**, every system has at least one one-edge split above rho = 0.15. Among the **220 original OU no-bracket systems**:

- edge-split ceiling below 0.15: **0/220**;
- edge-split ceiling at or above 0.15: **220/220**;
- median maximum one-edge rho = **0.7733** (IQR 0.7422–0.8114);
- median maximum OU-grid rho = **0.09785**;
- median edge-minus-OU accessibility gap = **0.67665**.

The simplest structural-ceiling explanation is therefore rejected. A binary tip-state configuration capable of expressing the benchmark exists on every realized tree, even within a biologically interpretable one-transition family.

## v0.3.1 generator-accessibility trade-off

The stored calibration grids then locate the failure inside the latent-OU-plus-zero-threshold generator.

Among the 220 categorical no-bracket systems:

- **195 (88.6%)** never reach rho = 0.15 anywhere on the finite OU grid, even when the valid-fraction rule is ignored;
- **25 (11.4%)** reach rho >= 0.15 only at grid points with valid fraction < 0.90;
- **0/220** reach the target at an admissible grid point;
- median maximum unconstrained rho = **0.09785**;
- median maximum admissible rho = **0.08205**;
- median within-system Spearman(log lambda, pilot rho) = **+0.767**;
- median within-system Spearman(log lambda, valid fraction) = **-0.957**;
- median valid fraction at the largest lambda = **0.20**.

For binary thresholded states, invalid replicates are monomorphic. Increasing latent phylogenetic memory therefore tends to strengthen the desired pairwise structure while destroying the polymorphism needed to define the statistic. The corresponding valid fraction is 1.00 throughout the 60 continuous no-bracket systems.

The resulting mechanism is:

> **The truth is structurally realizable, but the chosen generator cannot reliably assign it before binary variation collapses.**

This is a property of the **generator × representation × realized tree** combination, not evidence that categorical biological traits are intrinsically weakly conserved.

## Why this matters beyond this study

Simulation-based power and recoverability studies usually treat “known truth” as an input. But for constrained or discrete outcome spaces, a requested truth can fail to be assignable by the chosen generative family.

A fair cross-representation comparison therefore needs to establish, in order:

1. target realizability;
2. target accessibility under the representation-appropriate generator;
3. recovery conditional on successful assignment.

Otherwise generator failure can be misread as weak statistical power or weak information in the data.

## v0.4.1 representation-appropriate generator substitution

The next test held the realized trees, benchmark and binary mismatch + Spearman estimator fixed, but replaced latent-OU thresholding with a symmetric two-state Mk2/ER process.

Across the same 276 categorical systems:

- OU-threshold no-bracket: **220/276 = 79.7%**;
- Mk2 no-bracket: **170/276 = 61.6%**;
- original OU no-bracket systems rescued to Mk2 calibration: **51/220 = 23.2%**;
- original OU-calibrated systems newly lost under Mk2: **1/56**;
- Mk2 calibrated systems: **106/276**;
- Mk2 S3 PASS: **69/276 = 25.0%**;
- recovery failure given Mk2 calibration: **37/106 = 34.9%**.

The paired asymmetry (51 rescues versus one new calibration failure) shows that truth accessibility is materially generator-dependent. But Mk2 does not erase the bottleneck: **61.6%** still fail calibration, so the mechanism is not reducible to one badly chosen generator.

The current decomposition is therefore:

1. **Structural realizability:** not limiting at rho=0.15 for these categorical trees; every tree has an explicit one-transition witness above the target.
2. **Generator accessibility:** strongly limiting and generator-dependent; Mk2 materially improves but does not solve it.
3. **Estimator/recovery:** still limiting after successful assignment; categorical recovery failure remains substantial even under Mk2.

## v0.5 state-balance attenuation test

For binary mismatch Y and patristic-distance rank X,

`rho = Delta_rank * sqrt(p(1-p))`

where `p` is the fraction of unordered tip pairs that mismatch and

`Delta_rank = (mean rank_mismatch - mean rank_match) / SD(rank)`.

Thus ordinary binary Spearman contains an exact mismatch-prevalence attenuation term. The next frozen test keeps the **same Mk2 states and the same patristic-distance ranks**, removes only this algebraic factor, and asks whether the remaining 170 Mk2 no-bracket systems become calibratable.

The target is frozen at **Delta_rank = 0.30**, because rho = 0.15 at maximally balanced mismatch prevalence p = 0.5 corresponds exactly to 0.15 / sqrt(0.25) = 0.30. The original rho tolerance 0.01 maps to a Delta_rank tolerance of 0.02 on the same scale.

This is deliberately narrower than the earlier unexecuted alternative-estimator proposal, which changed both rank geometry and balance sensitivity at once.

## Why this matters beyond this study

Simulation-based power and recoverability studies usually treat “known truth” as an input. The present results show that this assumption can fail at three different levels:

1. the state space may not contain the requested truth;
2. the chosen generator may not reach it with adequate validity;
3. the estimator may attenuate or fail to recover it after assignment.

A fair cross-representation comparison must therefore demonstrate **truth assignability before power**. Otherwise generator or representation constraints can be misread as low statistical power or weak biological signal.

## Status

Structural realizability is closed. Latent-OU accessibility failure is closed. The representation-appropriate Mk2 substitution is closed and shows a substantial but incomplete rescue. The active gate is now the pre-frozen **state-balance attenuation** test on the same Mk2 states. No observed trait values or observed phylogenetic-memory effects enter any of these mechanism analyses.
