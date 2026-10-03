# Manuscript skeleton — Lineage repeatability of phylogenetic trait memory

Status: interpretation language frozen before the aggregate real-data model result is opened.

## Working title

**Plant families carry repeatable evolutionary-memory regimes across traits**

This title may be used only if the frozen 95% bootstrap interval for conditional family repeatability lies entirely above 0.10.

Neutral title if the interval crosses 0.10:

**How repeatable are lineage-level evolutionary-memory regimes across plant traits?**

Weak-repeatability title if the interval lies entirely below 0.10:

**Limited lineage-level repeatability of phylogenetic trait memory across plants**

## Question

After each trait is given its own mean memory-loss rate, does family identity explain a repeatable shift shared across multiple traits?

This is not the closed trait-versus-lineage dominance question. Trait identity is controlled as a fixed nuisance effect rather than estimated as a competing random variance component.

## Response

For each of the fixed 201 family × trait systems:

`memory_loss_rho = Spearman(patristic distance, absolute species-state difference)`

All systems are continuous traits, all unordered species pairs are used, and the exact whole-state permutation-null mean is zero.

## Primary model

`rho ~ 0 + trait_name + (1 | family)`

Primary parameter:

`R_family = variance_family / (variance_family + variance_residual)`

Interpretation is conditional on trait-specific means.

## Frozen decision language

### Repeatable lineage regime

Use only if the 95% bootstrap interval has lower bound > 0.10:

> After controlling trait-specific mean memory loss, family identity accounts for a repeatable component exceeding the predeclared 10% reference across traits.

### Weak lineage repeatability

Use only if the 95% bootstrap interval has upper bound < 0.10:

> Family identity contributes less than the predeclared 10% repeatability reference after trait-specific means are controlled.

### Uncertain relative to the 10% reference

Use only if the interval crosses 0.10:

> Family identity shows an estimated repeatable component, but its uncertainty spans the predeclared 10% reference.

No significance language substitutes for these frozen interval rules.

## Sensitivities

- Same 201 systems with prune-only rho.
- Leave one trait out.
- Leave one family out.

Sensitivities are descriptive and cannot replace the primary full-core classification.

## Hard nonclaims

- Do not state that family effects are larger than trait effects.
- Do not revive the failed variance-ratio question.
- Do not make a spatial-turnover claim.
- Do not rank individual families as a primary result.
- Do not remove systems based on observed rho.
