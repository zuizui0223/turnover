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

## Next decisive generator test

If the full v0.3.1 result confirms the interim pattern, the most direct follow-up is not an estimator search. It is a representation-appropriate generator comparison on the same categorical S3 trees.

### Candidate categorical generator

Use a symmetric two-state continuous-time Markov chain (Mk2/ER):

- root state sampled symmetrically;
- along branch length t, the probability of a state flip is
  `(1 - exp(-2 q t))/2`;
- parameterize q relative to tree height so the calibration grid is dimensionless across trees;
- use the same binary mismatch + Spearman estimator and the same target rho=0.15;
- retain the same validity rule requiring both states to be present and adequate valid-replicate fraction.

### Primary comparison

For the same 276 categorical systems:

`no-bracket rate under latent OU thresholding` versus `no-bracket rate under symmetric Mk2`.

Interpretation:
- Mk2 strongly rescues bracketing -> the dominant stage-2 bottleneck is generator-specific;
- Mk2 does not rescue -> investigate estimator/state-balance constraints next;
- either way, do not call the problem an inherent categorical-trait limitation without this generator check.

## Secondary estimator mechanism

For binary mismatch Y with mismatch-pair prevalence p and rank-distance X,

`corr(X,Y) = [(mean X_mismatch - mean X_match) / SD(X)] * sqrt(p(1-p))`.

Thus binary Spearman contains an explicit state-balance attenuation term. A later balance-normalized rank-separation statistic can isolate this factor without changing the pair-distance ranking. This is a cleaner estimator diagnostic than switching simultaneously from ranks to raw patristic distances.

## Status

Structural realizability and the latent-OU accessibility failure are now closed on the full categorical population. The next gate is the pre-specified generator substitution: keep binary mismatch + Spearman fixed and test whether a symmetric two-state Markov generator can assign rho = 0.15 more reliably. The balance-normalized estimator remains secondary and should not be opened before that generator comparison.
