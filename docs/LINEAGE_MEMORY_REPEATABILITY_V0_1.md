# Lineage repeatability of phylogenetic trait memory

## Question

After controlling the average memory-loss rate of each trait, do plant families show a repeatable tendency to lose trait similarity unusually fast or unusually slowly across multiple traits?

This is distinct from the closed trait-vs-lineage variance-ratio study. The earlier study asked which variance component is larger and failed its pre-outcome precision gate. This study asks only whether a family-level repeatable component can be estimated with useful precision.

## Fixed analysis set

The analysis set is the already-qualified, outcome-blind 201-system crossed core:

- 45 families
- 12 continuous traits
- family degree at least 2
- trait degree at least 5
- one connected family-trait graph
- all systems passed temporal structural, semantic, phylogeny, and known-truth geometry gates

No system can enter or leave after real memory rho is opened.

## Primary model

`rho ~ 0 + trait_name + (1 | family)`

Trait identity is a fixed nuisance effect. Family is the only random grouping factor.

Primary parameter:

`R_family = variance_family / (variance_family + variance_residual)`

This is conditional lineage repeatability after trait-specific mean memory rates have been removed.

A predeclared 10% conditional-repeatability reference is used only for interpretation, not system selection.

## Pre-outcome model informativeness

Before real rho is opened, the realized 201-edge graph must recover:

- a meaningful benchmark (R_family=0.20), and
- a null benchmark (R_family=0).

The meaningful benchmark must have >=95% successful fits, median absolute ICC error <=0.08, absolute median bias <=0.05, and >=80% of estimates above 0.10.

The null benchmark must have >=95% successful fits, <=10% of estimates above 0.10, and median estimated repeatability <=0.03.

If this fails, the study stops before real memory effects.

## Real-data interpretation

After a model-informativeness PASS, use 2,000 fixed-seed parametric bootstrap replicates.

- 95% CI lower >0.10: repeatable lineage regime.
- 95% CI upper <0.10: weak lineage repeatability.
- Otherwise: uncertain relative to the predeclared 10% reference.

No comparison against trait variance is made.

## Sensitivities

- Same 201 systems, prune-only rho.
- Leave-one-trait-out.
- Leave-one-family-out.

All are descriptive robustness checks and cannot replace the primary full-core result.
