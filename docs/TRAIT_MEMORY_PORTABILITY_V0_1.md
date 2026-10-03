# Cross-lineage portability of phylogenetic trait memory

Status: **prospective, pre-outcome**.

The preceding crossed variance-ratio study stopped before real memory-loss effects because the 201-system graph could recover the *direction* of a twofold trait-vs-family variance contrast but not its magnitude at the predeclared precision.

This follow-up does not relax that precision criterion and does not ask which variance component is larger.

## New question

**Can the evolutionary memory of a trait be transported across lineages?**

For a family that is completely held out, can we predict its memory-loss rate for a trait from the same trait measured in other families?

A positive answer would mean that trait identity carries transferable macroevolutionary information even when family-specific evolutionary context is unknown.

## Design

The graph is fixed before real effects:

- 201 family × trait systems;
- 45 families;
- 12 continuous traits;
- every family has at least 2 traits;
- every trait occurs in at least 5 families;
- all systems passed support, semantics, phylogeny, S3/prune-only geometry informativeness.

For every held-out family:

1. estimate each trait's mean memory-loss rho from all other families;
2. predict the held-out family × trait systems using those trait means;
3. compare squared error with a training-set global-mean predictor.

The primary statistic is:

`gain = 1 - SSE_trait / SSE_global`.

The null shuffles rho values among trait labels **within each family**, preserving family-level response distributions and the exact incidence graph while breaking cross-family trait correspondence.

Primary evidence requires positive gain and permutation p<=0.05.

The identical test is mandatory on prune-only rho.

## Before real rho

The exact 201-edge graph must first pass a known-truth calibration:

- signal benchmark: trait variance 0.005, family variance 0.005, residual variance 0.01;
- trait-null benchmark: trait variance 0, family variance 0.01, residual variance 0.01;
- 1,000 datasets per benchmark;
- 199 within-family permutations per dataset;
- require >=80% power under the signal benchmark;
- require <=6% false positives under the trait-null benchmark;
- require >=99% valid datasets.

Only after this gate passes may real memory-loss rho be extracted.

## Hard nonclaims

This study does not estimate whether trait variance exceeds family variance.

It does not revive the failed spatial programme.

It does not use real rho to choose traits or families.

It does not alter the 201-system graph after outcomes are opened.
