# Manuscript skeleton v0.3: lineage memory level and trait allocation are separable

## One biological question

**When evolutionary history leaves a phenotypic signature, what is actually conserved across lineages: the average tendency of a trait, the overall memory level of a lineage, or the identity of the traits that carry that memory?**

Previous comparative work already established that phylogenetic signal varies among traits and among clades. The present study asks a different question: which components of that structure are portable.

## Core model

For family (f) and trait (t),

[
ho_{ft} = mu + F_f + T_t + U_{ft}.
]

Interpretation:

- (T_t): weak trait-level prior in average phylogenetic memory.
- (F_f): lineage-wide memory level shared across the traits represented in that family.
- (U_{ft}): lineage-specific allocation of memory among traits, plus finite-sample uncertainty where not explicitly separated.

This decomposition yields three distinct predictions.

1. If trait identity is intrinsically informative, (T_t) should improve held-out-family prediction of absolute rho.
2. If lineages differ repeatably in overall memory level, (F_f) should recur across multiple traits.
3. If trait allocation is conserved, the relative ordering of traits should remain portable across families.

The data support the first two weakly-to-moderately and reject the third.

## Two orthogonal architecture indices

The crossed model naturally defines two different repeatabilities.

[
L = rac{sigma_F^2}{sigma_F^2+sigma_U^2}
]

is **lineage memory-level stability**: whether a family tends to remain globally high or low in phylogenetic memory across traits.

[
A = rac{sigma_T^2}{sigma_T^2+sigma_U^2}
]

is **trait-allocation stability**: whether the relative trait effect survives family-specific deviations.

For Gaussian crossed effects, allocation stability has a direct rank interpretation:

[
P(	ext{trait-pair order reverses between two families})
=
rac{arccos(A)}{pi}.
]

The expected Kendall similarity between two lineage-specific trait rankings is (2arcsin(A)/pi).

Point estimates on the matched/cleaned log scale are:

- BIEN S3: (L=0.184, A=0.140);
- BIEN prune: (L=0.165, A=0.114);
- AusTraits S3: (Lapprox0.300, Aapprox0.069);
- AusTraits prune: (Lapprox0.333, Aapprox0.067).

Thus phylogenetic memory is substantially more repeatable as a **lineage-wide level** than as a **trait allocation**, especially in AusTraits.

## Discovery: BIEN

Fixed cleaned core:

- 201 family x trait systems;
- 45 families;
- 12 continuous traits.

### Trait-average prior

On the all-201 log scale, named trait identity improves held-out-family absolute prediction:

- S3 gain +3.79%, p=0.0005;
- prune gain +4.40%, p=0.0008.

Trait identity therefore contains real but modest average information.

### Lineage-wide memory level

Conditional family repeatability is about 0.18.

Measurement-aware log-S3 heterogeneity is approximately:

- family 16%;
- trait 12%;
- family-by-trait/system 72%.

The family component survives measured geometry, provenance and correlated-trait audits, although its magnitude is imprecise.

### Trait allocation is strongly re-ordered

For well-represented trait pairs:

- log-S3 cross-family order reversal = 45.6%;
- log-prune = 47.8%.

These correspond to 85.4% and 89.5% of the pair-specific finite-sample maximum.

The measurement-aware model independently predicts approximately 45.5% and 46.4% reversal.

Thus the observed re-ordering is not explained by finite-species sampling error in the BIEN discovery.

## Prospective independent-compilation validation: AusTraits

Outcome-blind qualification produced:

- 259 systems;
- 42 families;
- 14 traits;
- provenance label: independent-compilation validation.

Only one of 130 retrievable AusTraits primary DOIs overlaps the BIEN DOI set, but DOI metadata coverage is 67.4%, so the stronger independent-source label is not used.

### Lineage-wide memory level strengthens

Prospective conditional family repeatability:

- S3 = 0.296;
- 95% bootstrap CI = 0.147–0.432;
- prune = 0.391.

The lower S3 interval exceeds the pre-frozen 0.10 practical reference.

Simple species-support/native-tip adjustment does not reduce this result:

- S3 repeatability 0.296 -> 0.299;
- prune 0.391 -> 0.397.

A deeper post-outcome tree-geometry audit adds system-level polytomy burden, patristic-distance CV, maximum distance-tie share, pendant-branch CV, and tip count. This **partly attenuates** the family component but does not remove it:

- S3 repeatability 0.296 -> 0.251; family variance retains 79.1% of its unadjusted value;
- prune repeatability 0.391 -> 0.358; family variance retains 84.7%.

Pairwise-distance CV explains the largest single attenuation. Thus lineage-wide context contains a measurable phylogenetic-geometry component, but most of the family signal remains after those measured tree features are accounted for.

### Weak trait-average information replicates

On the identical 254-system positive-numeric log core:

- S3 absolute trait prediction gain +1.67%, p=0.0027;
- prune gain +1.27%, p=0.0071.

Thus trait identity again gives a small but reproducible average prior.

### A portable trait hierarchy does not replicate

The prospectively frozen source-native rank-portability test fails:

- S3 gain -3.78%;
- prune gain -1.55%.

On the matched log core:

- S3 rank gain approximately -0.2%;
- prune approximately -1.8%.

Therefore a universal conservative-to-labile ordering of traits is not supported.

### Re-ordering is near its attainable maximum

On the matched log core:

- S3 reversal 48.8%, 92.9% of pair-specific maximum;
- prune reversal 48.2%, 91.8% of maximum.

On source-native scale:

- S3 50.5%, 96.2% of maximum;
- prune 50.3%, 95.7% of maximum.

The matched-log crossed model estimates:

- family share 28.5% / 31.8% on S3 / prune;
- trait share 4.9% / 4.7%;
- residual 66.6% / 63.6%.

The trait-contrast correlation across families is only about 0.068, predicting approximately 47.8% pair-order reversal. Again, model-implied and directly observed re-ordering are nearly identical.

## Memory level and memory allocation are separate lineage properties

A lineage's overall family BLUP is almost unrelated to how faithfully its trait ordering follows the global trait prior.

Using matched/cleaned log-S3:

- BIEN: family BLUP versus global-order disagreement rho = -0.112, p=0.462;
- AusTraits: rho = -0.018, p=0.909.

Thus a lineage can retain unusually strong or weak overall phylogenetic memory without becoming more or less faithful to the global trait ordering.

This motivates a two-dimensional view of lineage context:

1. **memory level** — how strongly history structures traits on average;
2. **memory allocation** — which traits carry that history within the lineage.

The two are empirically close to decoupled.

## Global trait means behave as graded priors, not fixed rankings

The failure of overall rank portability does not mean that trait averages are useless.

Using leave-one-family-out trait means, pairwise ordering is calibrated by the magnitude of the predicted trait difference.

BIEN log-S3:
- lowest prior-margin quartile: 47.8% ordering agreement;
- highest quartile: 73.5%;
- +1 SD in absolute prior margin increases agreement by about 7.4 percentage points under a two-way clustered linear-probability model.

AusTraits log-S3:
- lowest quartile: 48.3%;
- highest quartile: 64.0%;
- +1 SD margin increases agreement by about 4.9 percentage points.

AusTraits prune gives a similar positive calibration; BIEN prune is weaker.

Therefore the appropriate interpretation of the global trait effect is probabilistic:

> **Trait identity supplies a graded prior. When two traits have strongly separated global memory means, their ordering is more likely to survive in a new lineage; when the prior separation is small, lineage-specific allocation dominates.**

This resolves the apparent tension between positive absolute portability and failed rank portability.

## Pair-specific portability follows a signal-to-contingency ratio

The two-axis model also predicts when a particular trait pair should retain its global ordering.

For traits (a) and (b) within family (f),

[
D_f=(T_a-T_b)+(U_{fa}-U_{fb}).
]

If lineage-specific deviations are approximately Gaussian with variance (sigma_U^2), the probability that a lineage preserves the sign of the global trait contrast is

[
P(mathrm{global order survives})
=
Phileft(rac{|T_a-T_b|}{sqrt{2sigma_U^2}}ight).
]

Thus portability is not an all-or-none trait property. It is controlled by a **signal-to-contingency ratio**: the global separation between two trait means relative to the scale of lineage-specific deviations.

The observed leave-one-family-out margin calibration follows this prediction qualitatively. Trait pairs with almost no global separation are near chance ordering inside a new family, whereas strongly separated pairs are more likely to retain their order.

## A cross-compilation portability law emerges after normalization

The pair-specific signal-to-contingency rule can be tested across compilations by normalizing each leave-one-family-out global trait contrast by the estimated lineage-specific deviation scale:

[
x=rac{|Delta T|}{sqrt{2sigma_U^2}}.
]

Using measurement-aware (sigma_U^2) for BIEN and the high-support split-half measurement-aware estimate for AusTraits, the S3 family x trait-pair observations from both compilations fall on the same probabilistic calibration.

A pooled probit model with two-way cluster-robust uncertainty gives:

- common slope = 0.764, SE = 0.204, p = 1.8e-4;
- source intercept shift = -0.069, p = 0.665;
- source x slope interaction = 0.029, p = 0.943.

Thus there is no detectable need for a different S3 calibration law in BIEN versus AusTraits.

The idealized Gaussian crossed model predicts slope 1. The empirical slope is smaller, so the simple equation is somewhat overconfident, but the normalized trait contrast remains strongly predictive.

This suggests a more general statement than a fixed trait hierarchy:

> **Whether a trait ordering transports to a new lineage is governed by the size of the global trait contrast relative to lineage-specific contingency.**

The prune-only calibration is less clean, so this cross-compilation law should be presented as S3-primary with mandatory prune sensitivity rather than as tree-treatment invariant.

## Re-ordering is not a simple support or module artifact

AusTraits matched-log S3 reversal remains roughly 47–49% as the minimum species support per system is increased from 20 to 150.

Within functional modules, re-ordering is at least as strong as between modules:

- S3 within-module 50.9% versus between-module 49.1%;
- prune 50.8% versus 50.2%.

BIEN shows the same qualitative pattern.

Thus re-ordering is not produced merely by comparing unrelated functional systems such as leaves versus seeds.

## Shared-species matching rejects a trait-composition explanation

Trait pairs were also recomputed within each family using the **identical shared-species set for both traits**.

Across 33 well-supported trait pairs and 42 families:

- S3 weighted reversal changes only from 48.8% on the restricted original estimates to 47.1% after species matching;
- prune changes from 48.2% to 47.3%;
- paired-species reversal remains about 90% of the pair-specific attainable maximum;
- species matching changes the focal within-family trait order in only 16.7% of S3 cells and 13.9% of prune cells.

The shared-species sets contain a median of 98.5 species (range 21–2202).

Therefore near-half re-ordering is not primarily generated by different species being observed for different traits within the same family.

## Split-half reliability rejects a pure estimator-instability explanation

A high-support AusTraits subset was defined using matched-log systems with at least 40 native prune tips, ensuring at least 20 tips in each split half.

Across 158 systems:

- S3 half-A versus half-B rho reliability is 0.698–0.729 across three deterministic splits; Spearman–Brown full-data reliability is about 0.833.
- prune half reliability is 0.619–0.659; full-data reliability is about 0.783.

For trait pairs represented in at least 10 families:

- S3 measurement-only split-half order reversal = 22.2%, versus 48.8% observed cross-family reversal;
- prune measurement-only reversal = 28.4%, versus 47.7% observed cross-family reversal.

This is conservative against the biological interpretation because each split-half rho uses only half the species and is therefore noisier than the full-data rho used in the cross-family comparison.

Measurement and biological reversal probabilities are not additive, so the difference is not interpreted as an exact biological fraction. The key result is narrower: **finite-species estimator instability is far too small to account for near-half cross-lineage re-ordering.**

## Trait allocation is phylogenetically mosaic

Family patristic distance does not predict how different two families are in trait ordering.

BIEN log:

- S3 rho=0.037, p=0.340;
- prune rho=-0.011, p=0.529.

AusTraits:

- source-native S3 rho=-0.051, p=0.878;
- source-native prune rho=-0.079, p=0.947;
- matched-log S3 rho=-0.071, p=0.858;
- matched-log prune rho=-0.057, p=0.799.

Thus the identity of the traits carrying evolutionary memory is not smoothly inherited along deep family phylogeny. It is mosaic at this scale.

## The exact family effect is not robustly portable across compilations

Across 25 shared families, unadjusted family BLUPs correlate between BIEN and AusTraits:

- log-S3 rho=0.412;
- log-prune rho=0.362.

However, source-specific support/geometry adjustment attenuates these to approximately 0.265 and 0.227 and removes conventional significance.

Therefore claim:

- repeatable family context **within each compilation**;

do not claim:

- robust transport of the exact family score between compilations.

## Mechanism remains open

Current exploratory screens do not provide a robust explanation for lineage-wide memory level.

Not supported on the primary axes:

- family crown age;
- family richness;
- perennial fraction;
- woody fraction.

A BIEN prune-only richness association does not reproduce in BIEN S3 or AusTraits.

Measured family crown age, richness, woodiness and perenniality do not explain the architecture. Pairwise differences in woody/perennial composition also fail to predict how differently two families allocate memory among traits.

Tree geometry explains a minority of the lineage-wide memory-level component, especially through variation in the distribution of pairwise patristic distances, but leaves conditional family repeatability at 0.251 on S3 and 0.358 on prune.

For trait allocation itself, support restriction, functional modules, split-half estimator reliability, shared-species matching and deep-family distance all leave strong re-ordering. The ecological/developmental cause of that allocation remains unidentified.

## Allocation amplitude is repeatable within a trait universe but not portable across universes

A separate post-outcome analysis asks whether some families are generally more prone to large trait-specific deviations.

Traits were divided into balanced disjoint subsets. For each family and subset, allocation amplitude was defined as the RMS of trait-specific deviations after removing both source-wide trait means and the subset-wide family shift.

Across all balanced partitions:

- BIEN log-S3: median half-to-half family amplitude correlation = 0.392; after adjusting each half for observed trait count and species support = 0.260;
- BIEN log-prune: 0.350 -> 0.249;
- AusTraits log-S3: 0.378 -> 0.376;
- AusTraits log-prune: 0.154 -> 0.177.

Thus within a given compilation and trait universe, families that express larger allocation deviations for one group of traits tend to do so for another.

However, the exact family amplitude does not transport between BIEN and AusTraits across the 25 shared families:

- log-S3 rho = 0.028; adjusted rho = 0.018;
- log-prune rho = 0.255; adjusted rho = 0.272; neither is conventionally significant.

Therefore “rewiring propensity” is not a universal scalar property of a family. The more defensible interpretation is **lineage x trait-domain contingency**: a family may show a characteristic allocation amplitude within a given trait universe, but that amplitude need not persist when a substantially different trait set is examined.

## Low-dimensional allocation regimes are not a cross-dataset generality

A ridge-regularized low-rank family-by-trait model was evaluated by repeated held-out-cell cross-validation.

BIEN shows essentially zero predictive gain for ranks 1–4 beyond the additive family+trait model.

AusTraits, in contrast, shows a modest rank-1 gain:

- log-S3 SSE improvement = 3.2%;
- log-prune = 7.7%.

Thus AusTraits contains some recurrent low-dimensional allocation structure, but it does not replicate in BIEN and is not part of the cross-dataset central claim. Its biological interpretation remains a secondary exploratory question.

## What changes relative to previous comparative biology

Existing work established that:

- phylogenetic signal is common;
- traits and trait categories differ on average;
- the same trait can differ in signal among clades.

The closest empirical precedent compares the same traits among a small number of clades, for example the seven leaf traits studied across three major Pelargonium clades.

The present study adds a different inferential level:

- a many-lineage x many-trait crossed design;
- held-out-lineage prediction of absolute trait effects;
- a separate held-out-lineage test of trait rank portability;
- direct cross-lineage pair-order reversal;
- lineage-wide family repeatability;
- independent-compilation validation;
- explicit separation of memory level from memory allocation.

## Central claim

> **Lineages differ repeatably in the overall level of phylogenetic memory, but independently rewire which traits carry that memory.**

More conservative:

> **Traits carry weak global priors in phylogenetic memory, whereas lineage context strongly reconstructs their relative ordering.**

Conceptual:

> **A macroevolutionary average can be reproducible without being a rule that individual lineages obey.**

## Possible titles

- **Lineages rewire the trait allocation of phylogenetic memory**
- **Evolutionary memory has a lineage level but no portable trait hierarchy**
- **Weak trait priors and lineage-specific allocation of phylogenetic memory**
- **Lineages rewrite which traits carry evolutionary history**

Avoid claiming a universal hierarchy, because the prospective AusTraits rank-portability criterion failed.

## Figure logic

1. Conceptual decomposition into trait prior (T_t), lineage memory level (F_f), and trait allocation (U_{ft}).
2. Absolute versus rank portability in BIEN and AusTraits.
3. Pair-order reversal relative to pair-specific maximum.
4. Variance architecture and model-implied reversal.
5. Memory level versus allocation disagreement, showing decoupling.
6. Deep phylogeny and robustness tests.

## Hard boundaries

- The strict prospective portable-hierarchy prediction was not validated.
- Trait identity is not zero.
- Near-maximal rank re-ordering does not imply random trait evolution.
- rho is a phylogenetic-memory statistic, not an evolutionary rate.
- Residual/system variance is not a diagnosed biological interaction.
- The exact family effect is not robustly portable across compilations.
- AusTraits is independent-compilation validation, not fully verified independent-source replication.
