# Manuscript skeleton: global trait-memory spectrum versus lineage re-ranking

## One question

**Is the global conservative-to-labile ordering of traits a portable evolutionary hierarchy, or only a population-level average over lineage-specific rankings?**

The paper does not ask whether phylogenetic signal exists, whether exact signal magnitudes are identical among clades, or whether lineage context matters in some generic sense.

## Competing predictions

### Portable hierarchy

Trait biology imposes a reproducible relative ordering. Absolute memory strength may shift among lineages, but traits that are relatively conservative in one lineage tend to remain relatively conservative elsewhere.

Predictions:
- positive out-of-family trait-rank portability;
- high rank correlation among families;
- low cross-family pair-order reversal;
- trait component large relative to family-by-trait/system heterogeneity.

### Reordered hierarchy

Trait identity supplies only a weak global prior. Lineage-specific evolutionary histories change the relative ordering of traits.

Predictions:
- aggregate trait means may still form a reproducible spectrum;
- out-of-family rank prediction is weak;
- family-specific rankings correlate weakly;
- the same trait pair frequently reverses order among families;
- residual system heterogeneity remains large after sampling error is separated.

## Discovery design

BIEN 4.2.8; fixed 201 family x trait systems; 45 plant families; 12 continuous traits.

Memory-loss effect is Spearman correlation between all unordered patristic distances and absolute trait-state dissimilarities. Larger positive rho means faster decay of trait similarity with phylogenetic separation.

Positive-only cleaning was frozen independently of downstream effects. All 201 systems retained support and both raw and natural-log analyses are available.

The BIEN rank analysis is exploratory. AusTraits replication is prospectively frozen before any AusTraits memory-loss outcome is opened.

## Main discovery results

### 1. A global trait spectrum is real

On the cleaned log scale, mean trait ranks are highly concordant between S3 and prune-only trees (Spearman rho = 0.916).

Trait identity improves held-out-family rank prediction:
- S3 gain = +6.8%, blocked-permutation p = 0.0003;
- prune-only gain = +2.8%, p = 0.0071.

Absolute-rho BLUP portability is also positive on log scale:
- S3 = +5.9%;
- prune-only = +5.5%.

Therefore trait identity contains real transferable information.

### 2. The global spectrum is nevertheless a weak rule inside a lineage

For 16 trait pairs represented together in at least 10 families, two randomly chosen families disagree about which trait has larger memory-loss rho with probability:
- 45.6% on log-S3;
- 47.8% on log-prune.

For all 56 trait pairs represented in at least two families:
- 44.1% on log-S3;
- 46.6% on log-prune.

Among 289 family pairs sharing at least three traits, mean family-to-family rank correlation is only:
- 0.174 on log-S3;
- 0.084 on log-prune.

### 2b. The global hierarchy has coarse, not fine, resolution

The global spectrum is not equally unreliable at all separations.

Using trait pairs represented together in at least five families on the cleaned log scale, pair-order reversal declines as the two traits become farther apart on the global mean-rank spectrum:

- S3: Spearman(global rank gap, reversal) = -0.554;
- prune-only: -0.622.

For traits separated by <=0.20 in global normalized rank, cross-family reversal is essentially coin-flip:
- S3: 50.5%;
- prune-only: 52.3%.

For traits separated by >0.30:
- S3: 24.6%;
- prune-only: 31.5%.

Thus the aggregate spectrum contains useful information about widely separated endpoints but provides little reliable fine ordering among nearby traits. The biological result is a **coarse global prior with lineage-specific fine structure**, not the absence of a global spectrum.

### 2c. What survives is a sparse partial order, not a total ranking

Among the 16 trait pairs observed together in at least 10 families, require a stringent portable-order rule: the same direction on both S3 and prune-only and at least 75% of families agreeing on that direction on both axes.

Only **2/16 pairs (12.5%)** pass:

- SLA (leaf area per leaf dry mass) is more conservative than seed mass: 85.7% agreement on S3 and 81.0% on prune-only.
- DBH is more conservative than stem wood density: 76.9% agreement on both axes.

Thus the cross-lineage signal is better represented as a sparse **partial order** than as a portable total ranking of traits. Even the two robust inequalities are not universal: their family-to-family reversal probabilities remain 25.7–38.5% depending on pair and tree treatment.

### 3. Sampling error does not explain the re-ranking

Measurement-aware log-S3 variance components:
- family share of latent heterogeneity = 16.3%;
- trait share = 11.7%;
- system-specific share = 72.0%.

Log-prune:
- family = 14.9%;
- trait = 9.7%;
- system-specific = 75.4%.

For a two-trait within-family contrast, the family main effect cancels. Under the crossed Gaussian model, cross-family contrast correlation is

r = sigma_trait^2 / (sigma_trait^2 + sigma_system^2),

and pair-order reversal probability is

P(reversal) = acos(r) / pi.

This gives:
- log-S3 latent reversal = 45.5%;
- log-prune latent reversal = 46.4%.

The close match between directly observed reversal and measurement-error-aware latent reversal makes finite-species noise an implausible explanation for the near-half reordering.

### 4. Known measured artifacts do not supply a simple explanation

The pre-frozen species-coverage/tree-geometry adjustment and the post-outcome source/citation-composition sensitivities leave the qualitative re-ranking result intact.

The recurring family-wide component is not detectably organized along deeper family phylogenetic distance.

## What changes relative to previous literature

Blomberg et al. (2003) showed widespread phylogenetic signal and average differences among trait categories. That establishes a global tendency.

Ackerly (2009) showed that the same plant traits can evolve at very different rates in different clades. Gilbert & Webb (2015) emphasized that phylogenetic signal depends critically on clade/time depth.

A particularly close empirical precedent is Jones et al. (2013, American Journal of Botany, doi:10.3732/ajb.1200526): seven leaf traits were compared among three major Pelargonium clades, and both individual-trait phylogenetic signal and trait integration differed among clades. This establishes that the same functional traits can occupy different evolutionary contexts.

Graham et al. (2018, Global Ecology and Biogeography, doi:10.1111/geb.12686) formalized **phylogenetic scale dependence**: an evolutionary attribute may change unpredictably across clade extent, so inference at one phylogenetic scale need not extrapolate to another. Thus scale dependence itself is not the novelty here.

Those studies establish clade-specificity and the general danger of cross-scale extrapolation. They do not directly estimate whether the **relative ordering of trait conservatism itself** is portable to an unseen lineage, how much predictive information the global ordering retains, or how often the same trait pair reverses order across many independent lineages. The present contribution is therefore quantitative cross-level portability, not discovery of context dependence.

The present analysis separates these two levels directly:

**marginal/global trait ordering versus conditional/within-lineage ordering.**

The result is not that global regularities are false. It is that a real global regularity can be a weak population-level prior while lineage-specific rank-changing interactions dominate individual evolutionary systems.

## Central claim

> **A reproducible global spectrum of phylogenetic trait memory coexists with near-half cross-lineage reordering.**

Conceptual form:

> **Global evolutionary regularities can be real averages without being conserved rules within lineages.**

## Why this is not the trivial statement that context matters

A generic context-dependence claim predicts only heterogeneity.

Here, the stronger empirical conjunction is observed:
1. the aggregate trait spectrum is reproducible;
2. it has statistically detectable out-of-lineage predictive information;
3. nevertheless, relative trait ordering reverses between lineages almost half the time;
4. measurement-error correction yields essentially the same reversal magnitude.

The surprise is the coexistence of a stable global spectrum and unstable lineage-level hierarchy.

## Replication requirement

The strong manuscript wording is conditional on the prospectively frozen AusTraits test.

The existing exact AusTraits crosswalk already leaves 1,725 eligible systems, 65 families and 212 traits before downstream informativeness filtering. Outcome-blind degree pruning leaves a large connected graph, so prospective replication is feasible.

A matched positive-numeric raw-versus-log rank sensitivity has been frozen separately before AusTraits memory outcomes.

## Figure logic

1. **Global spectrum:** trait mean rank with S3/prune agreement.
2. **Local scrambling:** family x trait rank heatmap with traits ordered by the global spectrum.
3. **Reversal:** distribution of cross-family pair-order reversal probabilities; mark 0.5 chance.
4. **Architecture:** measurement-aware family / trait / system / sampling decomposition and model-implied reversal.
5. **Replication:** identical pre-frozen rank statistic in AusTraits.

## Hard boundaries

- Memory-loss rho is a phylogenetic-memory statistic, not an evolutionary rate.
- Trait identity is not zero or non-portable.
- Near-half reordering is not exact randomness.
- System-specific heterogeneity is not a mechanistically identified interaction.
- BIEN rank analyses are exploratory.
- A strong general claim requires prospective AusTraits replication.
