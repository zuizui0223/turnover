# BIEN–AusTraits synthesis: weak trait priors, repeatable lineage context, strong re-ordering

Status: post-outcome synthesis. This document does not reclassify the prospectively frozen AusTraits tests.

## The strict pre-frozen architecture did not validate

The prospective AusTraits rank-portability criterion required positive predictive gain on both S3 and prune-only trees.

It failed:
- S3 rank gain = -3.78%, p = 0.197;
- prune-only rank gain = -1.55%, p = 0.0503.

Therefore the strong statement that a portable global conservative-to-labile hierarchy coexists with re-ordering is **not validated**.

That failure is informative. It forces a sharper distinction between two kinds of trait-level generality.

## Trait identity predicts average memory, not a stable hierarchy

On the identical positive-numeric log core, named trait identity improves absolute held-out-family prediction in both datasets:

- BIEN: +3.79% (S3) and +4.40% (prune);
- AusTraits: +1.67% (S3) and +1.27% (prune).

All four harmonized blocked-permutation tests are positive and significant.

Thus trait identity is not irrelevant. Traits carry a weak global prior for their **average** phylogenetic-memory strength.

But that prior does not define a reliable ranking inside a lineage.

## Relative trait ordering is extensively reconstructed

For well-represented trait pairs:

- BIEN log S3: reversal probability 45.6%, equal to 85.4% of the maximum possible disagreement for those pair sizes;
- BIEN log prune: 47.8%, 89.5% of maximum;
- AusTraits log S3: 48.8%, 92.9% of maximum;
- AusTraits log prune: 48.2%, 91.8% of maximum.

The source-native AusTraits result is even closer to the finite-pair maximum: 96.2% and 95.7% of the maximum on S3 and prune.

So the reproducible cross-dataset result is not a stable hierarchy. It is **near-maximal lineage-specific re-ordering around weak trait means**.

## The variance architecture explains how both can be true

Write memory for family f and trait t as

rho_ft = mu + F_f + T_t + U_ft.

The trait main effect T_t can improve prediction of absolute rho even if it is small.

Within a family, however, F_f cancels when two traits are compared. The ordering of traits is then controlled by the competition between T_t and the family-specific deviations U_ft.

In BIEN log-S3, the measurement-aware trait-versus-system contrast correlation is about 0.140, implying a Gaussian pair-order reversal probability of 45.5%.

In AusTraits log-S3, the crossed model gives trait variance share 4.9%, family share 28.5%, and residual share 66.6%. The corresponding trait-contrast correlation is only 0.068, implying 47.8% reversal.

The model prediction and the directly observed reversal are nearly identical in both compilations.

## Lineage-wide context itself replicates

Family context is not only present in each source:

- BIEN conditional family repeatability = 0.183;
- AusTraits = 0.296, with 95% CI 0.147–0.432 and prune estimate 0.391.

Across the 25 families shared by the two final cores, log-S3 family BLUPs correlate at Spearman rho = 0.412 (one-sided permutation p = 0.018). Log-prune gives rho = 0.362 (p = 0.037).

This is exploratory cross-source evidence, not a prospectively frozen replication test. It nevertheless suggests that some lineage-wide memory context persists across largely different trait sets and compilations.

## Aggregate trait means can still look reproducible

Only four direct semantic trait anchors are available across final cores, so this is descriptive only. Their log-S3 mean memory ranks agree on 5 of 6 pairwise comparisons (Spearman rho = 0.80).

That is exactly the pattern expected if marginal trait means are real while lineage-specific rankings are unstable.


## Independent deep-phylogeny test

AusTraits independently gives the same mosaic result as BIEN.

Among 41 final-core families with full-backbone family representatives, family patristic distance does not predict disagreement in trait-memory ranking.

Matched log:
- S3: rho = -0.071, p = 0.858 for the preregistered positive direction;
- prune: rho = -0.057, p = 0.799.

Source-native shared-trait thresholds give rho from -0.045 to -0.079, with all one-sided p values >=0.878.

Thus the strong family-level context is not accompanied by a smoothly inherited deep-family hierarchy of which traits are conservative. The allocation of memory among traits is phylogenetically mosaic at this scale.

## Revised central claim

> **Traits carry weak global priors in phylogenetic memory, but lineages strongly reconstruct their relative ordering.**

More conceptual:

> **A macroevolutionary average can be reproducible without constituting a rule that individual lineages obey.**

The important advance is therefore not that phylogenetic signal depends on clade. That is known. The advance is the separation of:
- transferable average trait effects,
- repeatable lineage-wide context, and
- largely non-transferable within-lineage trait hierarchy.

## Boundaries

- Do not claim a universal trait conservatism ranking.
- Do not claim trait identity has zero effect.
- Do not call AusTraits an independent-source replication; provenance supports independent-compilation validation.
- Do not interpret rho as an evolutionary rate.
- Do not identify the family or residual component with a specific causal mechanism.
