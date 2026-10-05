# Pre-submission enquiry draft — Methods in Ecology and Evolution

## Proposed title

**Known truth is not automatically assignable in simulation-based power studies**

## Article type

Research Article

## Abstract

Simulation-based power studies usually treat a requested effect size as an input. That assumption can fail when the effect is a summary of constrained data rather than a freely assignable parameter of the generator. We formalize three logically distinct gates—**structural realizability**, **generator accessibility**, and **recovery**—and test them in 722 real plant family × trait sampling geometries under a common phylogenetic-memory target (Spearman rho = 0.15), with observed trait values kept hidden. Known-truth recovery was 56.2% for continuous-scalar systems but 2.15% for nominal-categorical systems. Among 276 categorical systems, the target was structurally realizable in every tree, yet latent-OU thresholding failed to bracket it in 79.7%. Replacing only the generator with symmetric Mk2 reduced no-bracket frequency to 61.6%; removing the exact binary state-balance attenuation term reduced the full-population frequency further to 42.4–43.8%. Even after successful Mk2 assignment, 34.9% of calibrated systems failed downstream recovery. Thus a failed known-truth simulation can reflect absence of an attainable target, failure of the generator to assign an attainable target, or failure to recover an assigned target. Power studies for constrained representations should distinguish these events before interpreting failure as low statistical power.

## Why we think this fits MEE

The manuscript introduces and tests a methodological distinction that is independent of the focal taxa: a failed known-truth simulation may fail because the target is structurally unrealizable, because an attainable target is inaccessible to the declared generator, or because an assigned target is not recovered. These are different inferential events, but conventional power summaries collapse them. We define prospective diagnostics for each gate and show, by controlled generator substitution and an exact attenuation factorization, that they separate empirically on hundreds of real sampling geometries. The phylogenetic example is a stress test of the method, not the scope of the claim. We therefore view this as a Research Article introducing a general simulation-design diagnostic rather than a Workflow or a case study.

## Evidence and reproducibility note

All mechanism analyses are outcome-free and prospectively frozen. Observed trait values and observed phylogenetic-memory effects are excluded. The primary mechanism programme was closed under a pre-frozen unconditional stop rule before manuscript preparation. Code, design contracts, provenance records and source-backed figure generation are available in the repository.
