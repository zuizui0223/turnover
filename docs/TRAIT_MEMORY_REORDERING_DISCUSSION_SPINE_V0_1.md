# Discussion spine: when does a global trait hierarchy survive lineage context?

Status: conceptual synthesis of the completed BIEN discovery. Strong cross-dataset generalization remains conditional on the prospectively opened AusTraits validation.

## 1. Start from the apparent contradiction

Two statements are simultaneously true in BIEN:

1. trait identity contains reproducible information about the phylogenetic-memory gradient;
2. the relative order of the same traits changes extensively among plant families.

This is not a contradiction if a global trait hierarchy is treated as a **probabilistic prior** rather than a deterministic lineage-level rule.

## 2. Separate three components

For trait t in lineage f, write the latent memory-gradient descriptor as

theta_ft = mu + F_f + T_t + U_ft.

- T_t: global trait prior.
- F_f: lineage-wide displacement shared across traits.
- U_ft: lineage-specific trait deviation that reorders traits within a lineage.

Taking the difference between traits a and b inside a lineage removes F_f:

theta_fa - theta_fb = Delta_ab + (U_fa-U_fb),

where Delta_ab = T_a-T_b.

Thus family-wide memory strength and within-family trait ordering are biologically/statistically distinct properties.

## 3. Portability has a quantitative condition

If U is approximated as Gaussian with variance sigma_U^2, the trait-pair contrast has variance 2 sigma_U^2.

For a global trait gap |Delta|, define

H = |Delta| / sigma_U,

a descriptive hierarchy-separation-to-context ratio.

The probability that two independent lineages disagree about pair order is

P(disagreement) = 2 p (1-p),

where

p = Phi(H / sqrt(2)).

This gives useful portability landmarks:

- H = 0 -> disagreement 0.50;
- H ≈ 0.84 -> disagreement 0.40;
- H ≈ 1.13 -> disagreement 1/3;
- H ≈ 1.49 -> disagreement 0.25;
- H ≈ 2.29 -> disagreement 0.10;
- H ≈ 2.76 -> disagreement 0.05.

A global hierarchy becomes a reliable lineage-level rule only when between-trait separation is large relative to lineage-specific trait deviations.

## 4. BIEN occupies the soft-prior regime

On cleaned log effects, the largest adjusted global trait gap among well-represented pairs is only:

- 1.07 sigma_U on S3;
- 1.09 sigma_U on prune-only.

So even the most widely separated observed pairs do not reach the H≈1.49 threshold needed for <25% cross-lineage disagreement.

Consistently:

- all well-represented pairs: reversal 45.6% / 47.8%;
- top quartile by global separation: 33.9% / 38.7%.

The global spectrum is informative, but no observed well-represented pair lies in a strongly lineage-invariant regime.

## 5. The variance model predicts the observed ordering behavior

The same crossed variance model predicts several otherwise separate-looking results.

### Pair reversal

Using system heterogeneity only:
- predicted weighted reversal 43.7% S3 versus 45.6% observed;
- 44.9% prune versus 47.8% observed.

Adding system-specific sampling SE:
- 45.2% S3;
- 46.2% prune.

Finite-species estimation error therefore adds only a few percentage points; latent lineage-specific heterogeneity explains most of the observed re-ordering.

### Family-to-family rank similarity

From

r = sigma_trait^2 / (sigma_trait^2 + sigma_system^2),

the Gaussian-copula expected Spearman correlation between lineage trait profiles is:

- 0.134 S3;
- 0.109 prune.

Observed mean family-pair rank correlations (shared traits >=3) are:

- 0.174 S3;
- 0.084 prune.

Thus variance decomposition, pair reversal, and full-ranking similarity are mutually consistent consequences of the same architecture.

## 6. The lineage-specific component is mosaic, not a deep clade regime

Trait-rank disagreement does not increase detectably with family patristic distance:

- log S3: rho = 0.037, p = 0.340;
- log prune: rho = -0.011, p = 0.529.

The earlier family-wide context score is likewise unrelated to deep family distance.

So both lineage-wide shifts and lineage-specific re-ordering lack detectable smooth inheritance at the family-phylogeny scale. “Lineage context” here is not simply a deeper taxonomic regime.

## 7. Nor is re-ordering just cross-module comparison

Among well-represented trait pairs, reversal is at least as high within functional modules as between modules.

This weakens a simple explanation in which the result arises because functionally unrelated trait domains are being compared.

## 8. What prior literature already established

Do not claim novelty for:
- widespread phylogenetic signal;
- average differences among trait categories;
- clade-dependent signal;
- local phylogenetic-signal heterogeneity;
- same-trait differences among a few clades.

Blomberg et al. (2003), Jones et al. (2013), Keck et al. (2016), Ackerly (2009), and related work already establish those points.


## 8.5. Analogy to global plant trait spectra

Plant functional ecology already distinguishes global trait spectra from local departures. The global spectrum of plant form and function captures strong aggregate coordination, while leaf-economics relationships are known to be very general but not universal across sites, biomes and functional groups.

The present result concerns a different object—the relative ordering of phylogenetic-memory gradients rather than trait-value correlations—but the inferential lesson is similar: a global regularity can be biologically useful without being a hard rule inside every context.

This analogy should be used to explain the concept, not as the novelty claim. The distinctive contribution remains direct quantification of held-out-lineage hierarchy portability and pair-order reversal.

## 9. What this paper adds

The contribution is the **portability level of inference**:

- a crossed many-lineage x repeated-trait design;
- held-out-lineage prediction of relative trait-memory ordering;
- explicit pair-order reversal probability;
- a measurement-error-aware link between variance architecture and ranking stability;
- a pre-frozen validation in an independently compiled trait database.

The conceptual advance is to distinguish:

> a reproducible marginal hierarchy

from

> a conserved conditional hierarchy within lineages.

## 10. Candidate endpoint

Technical:

> Global differences among traits define a weak but reproducible prior for phylogenetic-memory gradients, while lineage-specific trait deviations are large enough to reconstruct relative trait ordering across families.

Conceptual, conditional on AusTraits validation:

> A global evolutionary hierarchy becomes a lineage-level rule only when trait separation exceeds lineage-specific context variation; in plant trait-memory gradients, it usually does not.

Hard boundary: rho is the pre-frozen distance-based phylogenetic-memory descriptor, not a universal phylogenetic-signal or evolutionary-rate parameter.
