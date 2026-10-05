# Pre-submission enquiry draft — Methods in Ecology and Evolution

## Proposed title

**Known truth is not automatically assignable in simulation-based power studies**

## Article type

Research Article

## Abstract

1. Simulation-based power studies usually treat a requested effect size as an input. That assumption can fail when the effect is a summary of constrained data rather than a freely assignable parameter of the generator. We distinguish three logically ordered events: **structural feasibility**, **generator accessibility**, and **recovery**.

2. We tested these gates across 722 real plant family × trait sampling geometries under a common phylogenetic-memory target (Spearman rho = 0.15), with observed trait values kept hidden. Structural feasibility was screened with a one-sided attainable-state ceiling diagnostic; generator accessibility was challenged by a controlled latent-OU-to-Mk2 substitution; downstream recovery was evaluated only after successful assignment.

3. Among 683 systems with complete calibration diagnostics, generator no-bracket failure differed by 65.0 percentage points between continuous-scalar and nominal-categorical representations (14.7% versus 79.7%), whereas assigned-but-S3-recovery-failed systems occupied nearly identical shares of the full diagnostic populations (13.3% versus 13.8%). All 276 categorical trees contained a realizable one-transition state with rho >= 0.15, excluding a hard one-transition ceiling below the benchmark without claiming exact per-tree attainability within the calibration tolerance. Replacing only the generator with symmetric Mk2 reduced categorical no-bracket frequency to 61.6%, and removing the exact binary state-balance attenuation term reduced it further to 42.4–43.8%. Even after successful Mk2 assignment, 34.9% failed downstream recovery.

4. A failed known-truth simulation can therefore represent different inferential events. Structural feasibility does not guarantee generator accessibility, and generator accessibility does not guarantee recovery. Power studies for constrained representations should establish target assignability before interpreting failure as low statistical power.

## Why we think this fits MEE

The manuscript introduces and tests a methodological distinction that is independent of the focal taxa. Feasibility checks for constrained simulated correlations already exist, and simulation studies already show that DGM choice affects power, so we do not claim either observation as new. Our contribution is to separate **structural feasibility** from **generator-specific accessibility** and from downstream **recovery**; in the empirical stress test, the structural audit is deliberately one-sided and excludes a hard ceiling below the benchmark rather than asserting exact target attainability on every tree. In our benchmark, all categorical trees can express the requested target, yet one generator fails to assign it in most systems; changing only the generator rescues 51 systems while creating one new failure. Conventional power summaries collapse these inferentially different events. The phylogenetic example is a stress test of the method, not the scope of the claim. We therefore view this as a Research Article introducing a tested simulation-design diagnostic rather than a Workflow or a case study.

## Evidence and reproducibility note

All mechanism analyses are outcome-free and prospectively frozen. Observed trait values and observed phylogenetic-memory effects are excluded. The primary mechanism programme was closed under a pre-frozen unconditional stop rule before manuscript preparation. Code, design contracts, provenance records and source-backed figure generation are available in the repository.
