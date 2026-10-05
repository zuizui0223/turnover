# Pre-submission enquiry draft — Methods in Ecology and Evolution

## Proposed title

**Known truth is not automatically assignable in simulation-based power studies**

## Article type

Research Article

## Abstract

Simulation-based power studies usually treat a requested effect size as an input. That assumption can fail when the effect is a summary of constrained data rather than a freely assignable parameter of the generator. We formalize three logically distinct gates—**structural realizability**, **generator accessibility**, and **recovery**—and test them across 722 real plant family × trait sampling geometries under a common phylogenetic-memory target (Spearman rho = 0.15), with observed trait values kept hidden. Among 683 systems with complete calibration diagnostics, generator no-bracket failure differed by 65.0 percentage points between continuous-scalar and nominal-categorical representations (14.7% versus 79.7%), whereas assigned-but-S3-recovery-failed systems occupied nearly identical shares of the full diagnostic populations (13.3% versus 13.8%). For all 276 categorical trees the target was structurally realizable, showing that the dominant loss preceded recovery without reflecting a hard binary state-space ceiling. Replacing only the generator with symmetric Mk2 reduced categorical no-bracket frequency to 61.6%; removing the exact binary state-balance attenuation term reduced it further to 42.4–43.8%. Even after successful Mk2 assignment, 34.9% failed downstream recovery. A failed known-truth simulation can therefore represent different inferential events, and power studies should establish target assignability before interpreting failure as low statistical power.

## Why we think this fits MEE

The manuscript introduces and tests a methodological distinction that is independent of the focal taxa: a failed known-truth simulation may fail because the target is structurally unrealizable, because an attainable target is inaccessible to the declared generator, or because an assigned target is not recovered. These are different inferential events, but conventional power summaries collapse them. We define prospective diagnostics for each gate and show, by controlled generator substitution and an exact attenuation factorization, that they separate empirically on hundreds of real sampling geometries. The phylogenetic example is a stress test of the method, not the scope of the claim. We therefore view this as a Research Article introducing a general simulation-design diagnostic rather than a Workflow or a case study.

## Evidence and reproducibility note

All mechanism analyses are outcome-free and prospectively frozen. Observed trait values and observed phylogenetic-memory effects are excluded. The primary mechanism programme was closed under a pre-frozen unconditional stop rule before manuscript preparation. Code, design contracts, provenance records and source-backed figure generation are available in the repository.
