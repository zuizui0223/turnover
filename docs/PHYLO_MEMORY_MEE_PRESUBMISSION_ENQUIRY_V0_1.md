# Pre-submission enquiry draft — Methods in Ecology and Evolution

## Proposed title

**Known truth is not automatically assignable in phylogenetic-memory simulations**

## Article type

Research Article

## Abstract

Simulation-based power analyses usually treat the requested “true” effect as given. That assumption can fail when the outcome representation is constrained. We tested a common phylogenetic-memory target (Spearman rho = 0.15) across 722 real plant family × trait sampling geometries while keeping observed trait values hidden. Recovery was 56.2% for continuous-scalar systems but 2.15% for nominal-categorical systems. We then separated three logically distinct gates: structural realizability, generator accessibility, and downstream recovery. Among 276 categorical systems, latent-OU thresholding failed to bracket the target in 79.7%. Yet every categorical tree, including all 220 OU no-bracket systems, contained an explicit realizable one-transition binary state above the target, rejecting a hard state-space ceiling. Replacing only the generator with symmetric Mk2 reduced no-bracket frequency to 61.6%. Removing the exact binary state-balance attenuation term while retaining the same Mk2 states reduced the full-population no-bracket frequency further to 42.4–43.8%. Even after successful Mk2 assignment, 34.9% of calibrated systems failed the frozen recovery gate. Thus a declared known truth is not automatically an assignable truth. Power studies for constrained representations should audit target realizability and generator accessibility before interpreting failure as low statistical power.

## Why we think this fits MEE

The manuscript addresses a methodological problem that is independent of the focal taxa: simulation-based power studies can conflate failure to assign a requested target with failure of an estimator to recover it. We introduce a sequential audit separating structural realizability, generator accessibility and downstream recovery, and demonstrate that these gates give sharply different answers on hundreds of real comparative sampling geometries. The plant phylogenies are used as a stress-test benchmark rather than as the biological subject of the paper. We believe the framework is broadly relevant whenever a simulation target is a constrained data summary rather than a freely assignable parameter of the data-generating model.

## Evidence and reproducibility note

All mechanism analyses are outcome-free and prospectively frozen. Observed trait values and observed phylogenetic-memory effects are excluded. The primary mechanism programme was closed under a pre-frozen unconditional stop rule before manuscript preparation. Code, design contracts, provenance records and source-backed figure generation are available in the repository.
