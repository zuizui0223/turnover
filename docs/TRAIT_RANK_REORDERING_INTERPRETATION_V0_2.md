# Trait-rank reordering interpretation v0.2

Status: post-outcome exploratory synthesis using the pre-frozen positive-only cleaning analysis. This supersedes the v0.1 interpretation for manuscript framing. The BIEN rank analysis remains exploratory; the corresponding AusTraits rank-portability test is frozen before any AusTraits memory-loss outcome is opened.

## The result changed after the scale blocker was resolved

The earlier raw-scale result suggested almost no robust trait portability. That is not the full result.

Stage B removed raw values <=0 only in the five physical traits declared positive-only before the cleaned outcomes were opened. All 201 systems retained support, and natural-log effects became available for all 201 systems.

On the cleaned log scale, trait identity contains modest but real transferable information:

- absolute memory-loss BLUP portability gain: +5.9% on S3 and +5.5% on prune-only;
- within-family rank portability gain: +6.8% on S3 (blocked-permutation p=0.0003) and +2.8% on prune-only (p=0.0071).

Therefore the strongest claim is **not** that traits lack intrinsic or transferable phylogenetic memory.

## A real global spectrum exists

Mean within-family trait ranks are highly concordant between the two tree treatments:

- cleaned raw S3 versus prune: Spearman rho = 0.909;
- cleaned log S3 versus prune: rho = 0.916.

The global conservative-to-labile spectrum is therefore not merely noise.

But it is a weak prior, not a fixed hierarchy.

## The same hierarchy is repeatedly reordered inside lineages

For each pair of traits represented in at least 10 families, ask whether two randomly chosen families agree on which trait has the larger memory-loss rho.

On the cleaned log scale, the weighted probability of disagreement is:

- 45.6% under S3;
- 47.8% under prune-only.

Across all trait pairs represented in at least two families, the corresponding values are 44.1% and 46.6%.

Family-by-family ranking similarity is also low. For the 289 family pairs sharing at least three traits, mean rank correlation is 0.174 on log-S3 and 0.084 on log-prune.

So a stable global average spectrum coexists with almost coin-flip local ordering.

## Measurement error does not explain the reversals

The measurement-aware crossed model separates finite-species sampling variance from latent between-system heterogeneity.

Write latent memory loss as

theta_ft = mu + F_f + T_t + U_ft.

For the contrast between two traits inside one family, F cancels. Across two random families, the correlation of the two trait contrasts is

r = sigma_trait^2 / (sigma_trait^2 + sigma_system^2).

Under the Gaussian crossed model,

P(order reverses) = acos(r) / pi.

For the cleaned log analysis:

- S3: r = 0.140 -> expected latent reversal = 45.5%;
- prune-only: r = 0.114 -> expected latent reversal = 46.4%.

These sampling-error-aware values closely match the directly observed reversal frequencies. Thus the near-half reordering is not simply finite-species noise.

For cleaned raw S3, the pre-frozen two-way cluster bootstrap gives median latent reversal 42.3%, with 90.4% of bootstrap replicates above one-third.

## What the literature had established

Blomberg, Garland & Ives (2003) established that phylogenetic signal is widespread and that trait categories differ on average; behavioral traits were more labile on average than several other categories.

Subsequent work has repeatedly shown that signal and evolutionary rates can vary by clade. For example, the same plant trait can show signal in one clade and not another, and LMA conservatism differs between woody and herbaceous lineages. This means that lineage dependence itself is not new.

The missing distinction is between an **aggregate trait spectrum** and a **portable within-lineage hierarchy**.

## What this analysis adds

The BIEN result shows that both statements can be true at once:

1. there is a reproducible global ordering of traits in average phylogenetic memory;
2. that ordering is extensively reconstructed within individual lineages.

The global spectrum is therefore best interpreted as a population-level prior. It should not be read as a fixed biological hierarchy that determines which trait is more conservative inside a new lineage.

This resolves the earlier apparent dichotomy between “trait-intrinsic” and “lineage-context” explanations. The data support both, but at very different strengths.

## Candidate central claim

> A reproducible global spectrum of phylogenetic trait memory coexists with near-half cross-lineage reordering.

A more conceptual version:

> Global evolutionary regularities can be real averages without being conserved rules within lineages.

The strongest manuscript version should remain conditional on prospective replication in AusTraits.

## Nonclaims

- Trait identity is not zero and is not generally non-portable.
- Near-half reversal is not exact randomness.
- Memory-loss rho is not an evolutionary rate.
- The system-specific component does not identify a mechanism.
- BIEN rank reordering is exploratory.
