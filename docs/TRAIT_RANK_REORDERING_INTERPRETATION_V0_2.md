# Trait-rank reordering interpretation v0.2

Status: post-outcome exploratory synthesis using the pre-frozen positive-only cleaning analysis. This supersedes the v0.1 interpretation for manuscript framing. The BIEN rank analysis remains exploratory; the corresponding AusTraits rank-portability test is frozen before any AusTraits memory-loss outcome is opened.


## Terminology boundary

The response is a distance-based phylogenetic-memory gradient,

`rho = Spearman(patristic distance, pairwise trait dissimilarity)`.

It is not Blomberg's K, Pagel's lambda, a general estimator of phylogenetic signal, or an evolutionary-rate parameter. The safest wording for the reordered quantity is therefore **relative trait-memory gradient ordering**.

“Conservative-to-labile spectrum” may be used only as intuitive shorthand and should not imply that a larger or smaller rho is universally equivalent to more or less evolutionary conservatism under other comparative-method estimators.

All portability and reversal claims in this manuscript concern this pre-frozen distance-based descriptor.

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



## Re-ordering is strongest for globally close traits

A natural alternative explanation for near-half pair reversal is that the global spectrum contains many nearly tied trait pairs.

That explanation is partly correct and is biologically informative rather than fatal.

Among the 16 trait pairs represented together in at least 10 families, larger global mean separation tends to predict lower cross-family reversal. On cleaned log effects:

- S3: Spearman(global absolute mean difference, reversal) = -0.35;
- prune-only: rho = -0.52.

The association is imprecise on S3 and nominally detectable on prune-only, so the exact slope is exploratory.

But the effect-size pattern is clear. For the half of pairs with the largest global separation, weighted reversal remains 42.0% on S3 and 44.9% on prune-only. For the top quartile of global separation, reversal is still 33.9% and 38.7%, respectively.

Thus the global spectrum is **not meaningless**: large global differences are more stable. The better interpretation is a probabilistic prior whose reliability increases with global separation, not a fixed hierarchy. Even strongly separated traits can exchange relative memory-gradient order in roughly one-third of lineage comparisons.


## A quantitative soft-prior model

The “global spectrum as a probabilistic prior” interpretation follows directly from the crossed architecture.

For two traits (a) and (b) in family (f),

[
\theta_{fa}-\theta_{fb}=\Delta_{ab}+(U_{fa}-U_{fb}).
]

The family-wide context term cancels. If the system-specific deviations (U) are approximated as independent Gaussian terms with variance (sigma_U^2), the two-trait contrast has variance (2sigma_U^2).

For a global trait difference (Delta), the probability that a family preserves the global order is

[
p=\Phi\left(\frac{\Delta}{\sqrt{2\sigma_U^2}}\right),
]

and two independent families disagree about the pair order with probability

[
P(\mathrm{reversal})=2p(1-p).
]

Using the cleaned-log system heterogeneity from the measurement-aware model and additive family-adjusted trait means, this simple model predicts weighted reversal of 43.7% on S3 versus 45.6% observed, and 44.9% on prune-only versus 47.8% observed.

Across the 16 well-represented trait pairs, predicted versus observed pair reversal has Spearman rho = 0.61 (p = 0.013) on S3 and rho = 0.43 (p = 0.097) on prune-only.

This makes the soft-prior interpretation quantitative: the reliability of a global pair ordering is controlled by the **signal-to-context ratio (|\Delta|/\sigma_U)**. Trait identity supplies a real prior, but lineage-specific deviations can overwhelm it when the global difference is not large.

This Gaussian calculation is a statistical synthesis, not an identified evolutionary mechanism.

## The re-ranking is not a smooth deep-phylogenetic hierarchy

A separate post-outcome exploratory test asks whether closely related plant families retain more similar trait-memory rankings.

Using full-GBOTB family-crown patristic distances and family pairs sharing at least four traits:

- cleaned log S3: Spearman(distance, rank disagreement) = 0.037, family-profile permutation p = 0.340;
- cleaned log prune-only: rho = -0.011, p = 0.529.

Relaxing the shared-trait requirement to at least three traits increases the eligible set from 147 to 289 family pairs but still gives only rho = 0.079 (p = 0.140) on S3 and rho = 0.048 (p = 0.250) on prune-only.

Distance-quartile summaries likewise show no monotonic increase in ranking disagreement.

Thus lineage-specific re-ranking is not detectably organized as a smooth inherited hierarchy over deep family phylogeny. Together with the earlier null association between family-wide context scores and family distance, this supports a **phylogenetically mosaic** lineage context rather than a single deep clade-level regime.

## Functional modules do not explain the re-ranking

The trait modules were annotated before the original BIEN memory outcomes. Among well-represented trait pairs (co-occurring in at least 10 families), cleaned-log rank reversal is not reduced within functional modules:

- S3: within-module 48.4% versus between-module 45.0%;
- prune-only: within-module 49.1% versus between-module 47.5%.

Only four well-represented pairs are within-module, so this is descriptive rather than a powered module test. Still, the pattern argues against a simple explanation in which re-ranking occurs only because unrelated functional domains are compared.

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
