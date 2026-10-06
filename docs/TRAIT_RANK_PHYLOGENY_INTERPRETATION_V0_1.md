# Trait-rank deep-phylogeny interpretation v0.1

## Question

If lineage-specific trait-memory rankings are inherited at deep phylogenetic scale, closely related plant families should show more similar conservative-to-labile trait rankings than distant families.

The analysis compares complete observed family rank profiles on the fixed 45-family backbone. For each family pair sharing enough traits, rank disagreement is the fraction of shared trait pairs whose order reverses between the two families. Family profiles are permuted as intact units across the fixed family phylogeny, preserving the sparse trait-coverage pattern.

## Result

On the cleaned log scale there is essentially no deep-family organization.

- S3, >=4 shared traits: rho = 0.0374, one-sided permutation p = 0.3404, 147 family pairs.
- Prune-only, >=4 shared traits: rho = -0.0113, p = 0.5285, 147 pairs.
- Relaxing only the descriptive shared-trait threshold to >=3 gives rho = 0.0791 (p = 0.1395) on S3 and rho = 0.0481 (p = 0.2495) on prune-only across 289 family pairs.

The raw-scale descriptive sensitivity is also weak: S3 rho = -0.0231; prune-only rho = 0.1047, with the latter only a weak, non-primary tendency (p = 0.0808).

## Biological interpretation

The re-ordering result is therefore not well described as a small number of deep clades carrying different but internally stable trait hierarchies.

Instead:

> **trait-memory rankings appear to be reconstructed in a phylogenetically mosaic way at the family scale.**

This matters because it narrows the biological picture. There are now three distinct levels:

1. a reproducible global trait spectrum;
2. a modest repeatable family-wide shift in mean memory;
3. extensive trait-specific re-ordering within families that is not detectably inherited along deeper family phylogeny.

The third level is what prevents the global spectrum from becoming a reliable lineage-level hierarchy.

## Relation to the main claim

This result strengthens the interpretation of near-half cross-lineage pair-order reversal. The reversals are not simply explained by deeper family divergence: closely related families are not consistently more alike in their rank profiles.

The appropriate wording is **mosaic lineage-specific reconstruction**, not a smoothly inherited deep-clade regime.

## Boundaries

- This does not prove ecological context is the cause.
- It does not prove family rank profiles are random.
- It does not turn phylogenetic-memory rho into an evolutionary-rate parameter.
- It remains post-outcome exploratory and cannot replace the prospective AusTraits replication.
