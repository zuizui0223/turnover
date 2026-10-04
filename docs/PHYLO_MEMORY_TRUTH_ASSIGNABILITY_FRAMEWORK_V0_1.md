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

## v0.3.1 structural-realizability test

For every categorical S3 tree, every edge defines a realizable one-transition binary configuration: descendant clade = state 1, all remaining tips = state 0. The exact binary-mismatch Spearman rho is computed for every such edge.

This is not a global upper bound over arbitrary multi-transition patterns. It is deliberately a simple biologically interpretable attainable family.

### Interim exact diagnostic

As of the first seven completed v0.3.1 batches:
- 63 categorical systems have exact edge-split results;
- 50 of these are v0.2 S3 no-bracket systems;
- all 63 have maximum one-edge rho >=0.658;
- all 50 no-bracket systems have maximum one-edge rho >=0.709;
- median maximum one-edge rho among those 50 no-bracket systems = 0.785;
- therefore 50/50 no-bracket systems in this interim subset structurally admit a simple binary configuration far above the rho=0.15 target.

These are interim diagnostics only. The primary v0.3.1 result remains the full 276-system aggregate.

## What this would mean if the full result holds

A strong separation between structural realizability and generator accessibility would reject the simplest “binary representation imposes a hard rho<0.15 ceiling” explanation.

The more precise mechanism would be:

> The binary state space on the realized phylogenies can express strong distance structure, but the frozen latent-OU-plus-zero-threshold generator often does not make the rho=0.15 region accessible with adequate validity.

That is a property of the **generator × representation × tree** combination, not of categorical biological traits themselves.

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

This framework is sequential and mechanism-seeking. The Mk2 and balance-normalized follow-ups are not yet evidential results. The full v0.3.1 aggregate remains the next gate.
