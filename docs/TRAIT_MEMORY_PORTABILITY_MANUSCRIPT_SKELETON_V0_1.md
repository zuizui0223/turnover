# Manuscript skeleton — Cross-lineage portability of phylogenetic trait memory

Status: **pre-outcome narrative freeze**.

No real portability result was known when this skeleton was frozen.

## Working title

**Do plant traits carry transferable phylogenetic memory across lineages?**

Alternative neutral title:

**Cross-lineage prediction of phylogenetic trait memory in vascular plants**

Do not change the title to assert portability unless the frozen S3 + prune-only criterion passes.

## Gap

Phylogenetic signal is commonly estimated within a clade or for a trait across a broad tree, but this leaves a practical macroevolutionary question unresolved:

**If the evolutionary memory of a trait is learned in some lineages, does that information transfer to another lineage?**

A portable trait signature would mean that trait identity itself contains predictive information about how quickly similarity decays with phylogenetic separation, even when the target family is entirely excluded from training.

A failure of portability would mean that trait-memory estimates cannot safely be transferred among families without lineage-specific information.

## Data unit

The graph is fixed before real effects:

- 201 family × trait systems;
- 45 plant families;
- 12 continuous traits;
- every family represented by at least 2 traits;
- every trait represented by at least 5 families;
- all systems passed support, semantic, phylogeny, and S3 + prune-only known-truth geometry gates.

This graph comes from outcome-blind qualification. It is not selected by observed memory-loss rho.

## Memory response

For each admitted family × trait system:

- species state = median valid BIEN value;
- dissimilarity = absolute difference;
- separation = all unordered patristic distances;
- memory-loss effect = Spearman(separation, dissimilarity).

The exact complete whole-state permutation-null mean is zero, so this rho is already the null-centered memory-loss effect.

Larger positive rho means similarity is lost more rapidly with phylogenetic separation.

## Portability test

Leave one family out completely.

For every system in the held-out family:

- trait predictor = mean rho for the same trait among all training families;
- baseline predictor = mean rho across all training systems.

Pool errors over all 201 held-out systems:

`portability_gain = 1 - SSE_trait / SSE_global`.

Positive gain means trait identity improves out-of-family prediction.

## Null

Within each family independently, permute the rho values among that family's fixed trait labels.

This preserves:

- the exact family × trait incidence graph;
- the number of traits in every family;
- the number of families per trait;
- each family's rho distribution.

It destroys only cross-family trait correspondence.

Use 999 frozen permutations, seed 20261003.

Primary S3 evidence requires:

- gain > 0;
- one-sided blocked-permutation p <= 0.05.

The identical criterion is mandatory for prune-only rho. A portability claim requires both axes to pass.

## Pre-outcome model informativeness

The exact graph was calibrated before real rho:

Signal benchmark:
- trait variance 0.005;
- family variance 0.005;
- residual variance 0.01.

Trait-null benchmark:
- trait variance 0;
- family variance 0.01;
- residual variance 0.01.

With 1,000 datasets per benchmark and 199 blocked permutations per dataset, the graph had to achieve:

- >=99% valid datasets;
- >=80% signal power;
- <=6% null false positives;
- positive median signal gain.

Only after this gate passes may real rho be opened.

## Results template

### Qualification

Report the previously frozen 201-system graph and the model-informativeness result.

### S3 portability

Report:
- gain;
- null median and 95% permutation interval;
- blocked permutation p.

### Prune-only portability

Report the same quantities on the identical systems.

### Prediction audit

Report observed rho versus held-out trait prediction descriptively. Do not remove outliers or high-residual systems.

### Trait summaries

Trait-wise mean rho may be reported descriptively after the global portability test. Do not rank traits as a new primary result.

## Discussion template

If robust PASS:
1. Trait identity contains macroevolutionary information transferable among families.
2. Portability is predictive, not a claim that trait effects dominate lineage effects.
3. Discuss what biological constraints could create recurring memory depth for the same trait across independent clades.
4. Explain why family-blocked validation is stronger than fitting a trait effect on the same observations used to estimate it.

If HOLD:
1. Trait identity does not provide robust out-of-family prediction under the frozen criterion.
2. This does not imply zero phylogenetic memory; it means that memory is not portable across families at this resolution.
3. Lineage context, measurement heterogeneity, or trait-specific evolutionary regimes may prevent transfer.

## Hard nonclaims

- Do not state that trait variance exceeds family variance.
- Do not revive the failed spatial-turnover programme.
- Do not alter the 201-system graph after rho is opened.
- Do not remove families or traits based on prediction residuals.
- Do not change the permutation scheme, alpha, or prune-only requirement after results are seen.
