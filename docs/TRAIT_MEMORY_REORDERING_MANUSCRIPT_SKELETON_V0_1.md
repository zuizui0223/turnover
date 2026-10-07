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

## Why a stable global spectrum and unstable lineage rankings can coexist

The apparent paradox follows directly from the crossed architecture. Write latent memory for trait t in family f as

```
theta_ft = mu + F_f + T_t + U_ft
```

For two traits A and B inside one family,

```
D_f(A,B) = theta_fA - theta_fB
         = (T_A - T_B) + (U_fA - U_fB).
```

The family-wide shift F_f cancels. Across many families, the lineage-specific U terms average toward zero, so the global trait contrast T_A-T_B can be estimated and a stable aggregate spectrum can emerge.

But prediction inside one new family is governed by the same global contrast plus a new lineage-specific deviation. When system-specific heterogeneity is much larger than trait variance, the global ordering is a weak prior even if it is estimated precisely in aggregate.

If T and U are treated as independent Gaussian random effects, the correlation of the same two-trait contrast in two randomly drawn families is

```
r = sigma_trait^2 / (sigma_trait^2 + sigma_system^2),
```

and the population-average probability that the sign of the contrast reverses is

```
P(reversal) = acos(r) / pi.
```

For the cleaned log BIEN model, r is 0.140 under S3 and 0.114 under prune-only, implying reversal probabilities of 45.5% and 46.4%. These closely match the directly observed pairwise reversal frequencies.

This supplies a mechanistic-statistical explanation for the headline result without assigning a biological cause to U: **aggregation recovers a real trait main effect, while large lineage-specific deviations destroy its status as a deterministic local hierarchy.**


## Deep phylogeny does not organize the re-ranking

If family-specific trait rankings were inherited as deeper clade-level regimes, more distantly related families should disagree more strongly in their trait ordering.

They do not.

Using intact family rank profiles and a family-label permutation on the fixed GBOTB backbone:

- cleaned log S3, >=4 shared traits: distance-disagreement rho = 0.037, p = 0.340;
- cleaned log prune-only: rho = -0.011, p = 0.529;
- the >=3-shared-traits sensitivity remains weak on both axes.

Thus the lineage-specific hierarchy is not detectably a smooth deep-phylogenetic property. It is better described as **phylogenetically mosaic reconstruction at the family scale**.

This creates a three-level architecture:

1. **global trait prior** — traits differ on average;
2. **family-wide context** — families show modest repeatable shifts across traits;
3. **family-specific re-ranking** — individual trait positions are extensively rearranged, with little deep-family continuity.

## Re-ranking is not restricted to comparisons among unlike functional modules

Using the biological trait modules annotated before the original BIEN memory effects were opened, well-represented within-module trait pairs show nearly the same cross-family reversal as between-module pairs.

On the cleaned log scale:

- within-module weighted reversal = 48.4% (S3) and 49.1% (prune-only);
- between-module weighted reversal = 45.0% and 47.5%.

This is descriptive because only four well-represented within-module pairs are available, but it argues against a simple explanation in which re-ranking occurs only because unrelated functions are being compared.


## Three-level architecture

The cleaned BIEN result is best described as three distinct components rather than a binary trait-versus-lineage contrast.

1. **Global trait prior**
   - Traits differ reproducibly in average phylogenetic memory.
   - On the cleaned log scale, trait identity has modest held-out-family predictive information.

2. **Lineage-wide shift**
   - Families differ in overall memory strength across represented traits.
   - This family-wide component survives the correlated-trait/shared-design null and measured geometry/provenance adjustments.
   - It is not detectably organized along deeper family phylogeny.

3. **Lineage-specific re-ranking**
   - Within a family, individual traits deviate strongly enough from the global spectrum that pairwise trait order reverses between families roughly 45-48% of the time.
   - The same reversal magnitude is recovered after finite-species sampling error is separated.
   - Re-ranking is not reduced within functional modules and is not detectably organized by deep family phylogenetic distance.

The family-wide shift and the magnitude of rank re-ordering are also largely orthogonal. On cleaned log effects, the absolute family-wide shift is essentially unrelated to global-ranking disagreement (Spearman approximately -0.11 on S3 and -0.04 on prune-only).

Thus "lineage context" is not one axis. A lineage can shift all traits together and can separately reassemble their relative ordering.

## Stronger conceptual synthesis

The result is not that global trait regularities are false. It is that **marginal regularity and conditional organization are different biological objects**.

A trait spectrum estimated across many lineages is a real population-level prior. But the hierarchy realized inside a particular lineage is reconstructed strongly enough that close relatives do not inherit detectably more similar rankings.

Candidate conceptual statement:

> Global evolutionary regularities can be reproducible marginal averages while lineage-level trait hierarchies remain phylogenetically mosaic.

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

Outcome-blind AusTraits qualification is now complete:

- final core: 259 systems / 42 families / 14 traits;
- all 259 systems are numeric continuous traits;
- graph-specific model-informativeness: PASS;
- provenance label: independent-compilation validation;
- matched positive raw/log core: 254 systems / 42 families / 13 traits.

Real AusTraits memory effects were authorized only after these gates completed. The prospective result must be interpreted under the already frozen family-repeatability, rank-portability, pair-reversal, and raw/log rules.

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
