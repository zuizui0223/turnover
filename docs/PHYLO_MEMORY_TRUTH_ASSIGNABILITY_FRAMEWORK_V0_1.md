# Truth assignability framework for phylogenetic-memory simulations

## Why the current result needs a three-stage decomposition

A known-truth recovery study can fail for at least three logically distinct reasons.

1. **Structural feasibility** — does the representation × realized tree state space contain any configuration whose target statistic reaches the declared truth?
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

> **A hard one-transition ceiling below the benchmark is excluded, but the chosen generator cannot reliably assign the benchmark before binary variation collapses.**

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

1. **One-sided structural ceiling:** a hard one-transition ceiling below rho=0.15 is excluded for every categorical tree; this does not prove exact per-tree target attainability within tolerance.
2. **Generator accessibility:** strongly limiting and generator-dependent; Mk2 materially improves but does not solve it.
3. **Estimator/recovery:** still limiting after successful assignment; categorical recovery failure remains substantial even under Mk2.

## v0.5 state-balance attenuation result

For binary mismatch Y and patristic-distance rank X,

`rho = Delta_rank * sqrt(p(1-p))`

where `p` is the fraction of unordered tip pairs that mismatch and

`Delta_rank = (mean rank_mismatch - mean rank_match) / SD(rank)`.

The identity is numerically exact in the frozen implementation (maximum absolute error **8.88e-16**). v0.5 keeps the **same Mk2 states and the same patristic-distance ranks** and removes only this algebraic state-balance term.

Four systems encountered outcome-free geometry drift during exact reconstruction and were held before their v0.5 outcome was computed. Among the remaining **272 exact geometry matches**:

- Mk2-rho reference: **167 no-bracket / 105 calibrated**;
- balance-normalized Delta_rank: **117 no-bracket / 155 calibrated**;
- **50/167 = 29.9%** of matched Mk2-rho no-bracket systems are rescued;
- **0/105** matched Mk2-rho calibrated systems become new failures;
- median mismatch-pair fraction at Delta_rank calibration = **0.4037**;
- median ordinary rho at that calibration point = **0.1398**;
- median pilot valid fraction = **1.00**.

The four geometry-HOLD systems include three original Mk2-rho no-bracket systems and one calibrated system. Therefore, without imputing their missing outcomes, the full 276-system balance-normalized no-bracket rate is bounded at **42.4–43.8%**, and the rescue fraction among the original 170 Mk2-rho no-bracket systems is bounded at **29.4–31.2%**. This third stage calibrates Delta_rank = 0.30 rather than rho = 0.15; it is a mechanism diagnostic that removes the exact balance multiplier, not a third estimate of the identical rho-target estimand.

The balance-normalized diagnostic therefore identifies state balance as a substantial additional attenuation mechanism, but it does **not** explain all of the calibration bottleneck. A large remainder persists even after replacing the generator and removing the exact balance attenuation term. Under the pre-frozen stop rule, that remainder is retained rather than pursued by further estimator or parameter search on the same systems.

## Why this matters beyond this study

Simulation-based power and recoverability studies usually treat “known truth” as an input. The present results show that this assumption can fail at three different levels:

1. the state space may not contain the requested truth;
2. the chosen generator may not reach it with adequate validity;
3. the estimator may attenuate or fail to recover it after assignment.

A fair cross-representation comparison must therefore demonstrate **truth assignability before power**. Otherwise generator or representation constraints can be misread as low statistical power or weak biological signal.

## Status

The primary mechanism programme is **closed** under the pre-frozen v0.5.2 stop rule.

The sequential result is now complete:

1. **A hard one-transition structural ceiling is not limiting** at rho=0.15: every categorical tree has an explicit one-transition witness at or above target, without establishing exact per-tree attainability.
2. **Generator accessibility is strongly limiting and generator-dependent**: OU thresholding fails far more often than Mk2.
3. **State-balance attenuation is an additional, separable limitation**: removing only the exact balance term rescues about 30% of the remaining Mk2 no-bracket systems.
4. **Recovery remains distinct from assignment**: even under Mk2, 34.9% of calibrated systems fail the frozen recovery gate.
5. **An unresolved remainder remains**: approximately 42–44% of the categorical population is still no-bracket after the frozen generator and balance diagnostics.

No further generator, estimator, grid, target, or subgroup search on these 276 systems is allowed as primary evidence. The unresolved remainder is part of the result. No observed trait values or observed phylogenetic-memory effects enter any mechanism analysis.
