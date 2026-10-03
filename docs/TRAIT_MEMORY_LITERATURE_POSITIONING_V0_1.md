# Literature positioning — trait identity versus lineage identity

Status: pre-outcome positioning note. This document does not use any real family x trait memory-loss effect from the present study.

## What the literature already establishes

Phylogenetic signal is known to vary strongly among traits, datasets, clades and ecological contexts.

- Münkemüller et al. (2012, Methods in Ecology and Evolution, DOI 10.1111/j.2041-210X.2012.00196.x) review the major phylogenetic-signal statistics and emphasize that the level of phylogenetic dependence can vary strongly among phylogenies and clades.
- Kamilar & Cooper (2013, Philosophical Transactions B, primate behaviour/ecology/life history) show extensive heterogeneity in phylogenetic signal among 31 traits.
- Prinzing et al. (2021, New Phytologist, DOI 10.1111/nph.17705) quantify 10 plant traits in 6,704 communities across 38 habitat types and show that local phylogenetic signal can vary about 50-fold among habitat types. Thus even the same trait does not carry a fixed phylogenetic signal across ecological subsets.
- Sanchez-Martinez et al. (2024, Methods in Ecology and Evolution, DOI 10.1111/2041-210X.14304) partition trait variance-covariance into phylogenetic, environmental and residual components using multivariate phylogenetic mixed models.
- Sanchez-Martinez et al. (2025, Functional Ecology, DOI 10.1111/1365-2435.14700) quantify phylogenetic conservatism in leaf, wood and demographic traits in Amazon tree taxa and decompose phylogenetic versus non-phylogenetic variance/covariance.
- Ackerly et al. / later leaf-economics work has also localized conservative and diversifying nodes within particular traits, showing that conservatism is heterogeneous along the tree rather than globally uniform.

## Gap

These literatures answer related but different questions:

1. **Trait comparison:** Which traits show stronger phylogenetic signal?
2. **Clade/local context comparison:** Where in the tree or in which ecological subset is phylogenetic signal stronger?
3. **Variance-covariance partition:** How much trait variance/covariance is phylogenetic or environmental?

The present follow-up asks a crossed question that these analyses do not directly resolve:

> When the same trait is independently represented in many plant families, and each family contributes multiple traits, is heterogeneity in the phylogenetic memory gradient organized more strongly by trait identity or by lineage identity?

This requires repeated observations on both axes. A trait-only comparison confounds trait identity with the particular clades in which the trait was measured; a clade-only comparison confounds lineage with which traits happen to be available.

## Distinctive design

The present design treats each admitted **family x trait** system as one response unit and decomposes its phylogenetic memory gradient using crossed random effects:

`rho ~ 1 + (1 | family) + (1 | trait_name)`

The primary object is therefore not “is there phylogenetic signal?” but the **variance architecture of phylogenetic memory across a crossed trait-by-lineage matrix**.

The design is further unusual in that family x trait systems are admitted only if the realized phylogenetic geometry can recover a fixed known-truth benchmark on both S3 and backbone-native prune-only trees before the observed memory effect is opened.

## Terminology

The response is a Spearman association between patristic separation and trait-state dissimilarity. It is described as **phylogenetic memory-loss strength** or the **phylogenetic memory gradient**, not as a decay rate or timescale.

## Current novelty assessment

The literature search performed before opening real effects found strong precedent for:
- trait-specific phylogenetic signal,
- clade/local heterogeneity of phylogenetic signal,
- multivariate phylogenetic variance-covariance decomposition.

It did **not** identify a vascular-plant analysis that uses a broad repeated family x trait matrix and directly estimates crossed between-family versus between-trait variance in a common phylogenetic-memory response. This should be treated as a working novelty claim to be rechecked during manuscript literature review, not as a claim that no precedent exists.
