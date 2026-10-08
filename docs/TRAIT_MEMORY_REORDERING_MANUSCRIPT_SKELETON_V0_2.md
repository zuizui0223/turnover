# Manuscript skeleton v0.2: weak trait priors, repeatable lineage context, strong re-ordering

## One biological question

**Do traits carry a stable hierarchy of phylogenetic conservatism across lineages, or do lineages reconstruct that hierarchy around only weak trait-level priors?**

This is not a paper about whether phylogenetic signal exists, nor about whether signal can vary among clades. Both are established.

The paper asks which part of phylogenetic-memory structure is actually portable:
- the average effect of trait identity,
- a lineage-wide context shared across traits,
- or the relative ranking of traits within a lineage.

## Core decomposition

For family f and trait t,

rho_ft = mu + F_f + T_t + U_ft.

- T_t: a trait-level prior in average phylogenetic memory.
- F_f: a lineage-wide shift shared across represented traits.
- U_ft: lineage-specific trait deviation, plus finite-sample estimation noise where not separated.

Absolute held-out-family prediction can benefit from T_t.

Within-family trait ordering removes F_f. It is stable only if trait contrasts dominate lineage-specific deviations.

This makes absolute portability and rank portability distinct biological questions.

## Discovery: BIEN

Fixed cleaned core:
- 201 family x trait systems;
- 45 families;
- 12 continuous traits.

On the all-201 log scale:

### Weak trait prior

Harmonized held-out-family absolute trait prediction:
- S3 gain +3.79%, p=0.0005;
- prune gain +4.40%, p=0.0008.

Thus named traits carry real but modest average information.

### Lineage context

Conditional family repeatability is about 0.18.

Measurement-aware log-S3 heterogeneity:
- family 16.3%;
- trait 11.7%;
- system 72.0%.

### Strong re-ordering

Well-represented trait pairs reverse order across two families with probability:
- 45.6% S3;
- 47.8% prune.

Relative to the finite-pair maximum possible for the observed pair sizes, this is:
- 85.4% of maximum S3;
- 89.5% of maximum prune.

The measurement-aware crossed model independently predicts:
- 45.5% reversal S3;
- 46.4% prune.

Observed and latent-model reversal therefore agree closely.

BIEN alone showed some weak rank portability on log scale, so it could not establish whether that relative hierarchy would generalize.

## Prospective independent-compilation validation: AusTraits

The outcome-blind qualification produced:
- 259 systems;
- 42 families;
- 14 traits;
- provenance label: independent-compilation validation.

Only 1 of 130 AusTraits primary DOIs with retrievable metadata overlaps a BIEN DOI, but DOI coverage is 67.4%, so the stronger independent-source label is not used.

### Family context replicates and strengthens

Prospective conditional family repeatability:
- S3 = 0.296;
- 95% bootstrap CI 0.147–0.432;
- prune = 0.391.

The lower CI exceeds the pre-frozen 0.10 practical reference.

### Trait identity still carries average information

On the identical 254-system positive-numeric log core:
- S3 absolute trait prediction gain +1.67%, p=0.0027;
- prune gain +1.27%, p=0.0071.

So the trait prior replicates.

### But the trait hierarchy does not

Prospective source-native within-family rank portability:
- S3 gain -3.78%, axis FAIL;
- prune gain -1.55%, axis FAIL.

On the matched log core:
- S3 rank gain -0.20%;
- prune rank gain -1.76%.

Thus the strong portable-hierarchy prediction is not validated.

### Re-ordering is nearly maximal

On the matched log core:
- reversal 48.8% S3, 92.9% of finite-pair maximum;
- reversal 48.2% prune, 91.8% of maximum.

On source-native scale:
- 50.5% S3, 96.2% of maximum;
- 50.3% prune, 95.7% of maximum.

The crossed variance model gives matched-log:
- family share 28.5% S3 / 31.8% prune;
- trait share 4.9% / 4.7%;
- residual 66.6% / 63.6%.

Trait-contrast correlation across families is only 0.068–0.069, predicting 47.8% reversal on both tree treatments.

Again the model prediction closely matches direct pair-order reversal.

## The cross-dataset result

The strict pre-frozen claim that a **portable global trait hierarchy** coexists with re-ordering is not validated.

What does replicate is stronger in a different way:

1. **Trait identity has a small but transferable effect on average memory.**
2. **Lineage-wide context repeats across traits, and is stronger than the trait main effect in point estimates.**
3. **The relative ordering of traits is extensively reconstructed inside lineages.**
4. **Directly observed re-ordering matches what the trait-versus-lineage-specific variance architecture predicts.**

The same named trait can therefore have a real global prior without carrying a stable position in a universal conservative-to-labile hierarchy.

## Additional cross-source evidence

Across the 25 families shared by the final BIEN and AusTraits cores, unadjusted log-S3 family BLUPs correlate at rho=0.412 (one-sided permutation p=0.018); log-prune gives rho=0.362 (p=0.037).

This exact-family correspondence is **not robust** to source-specific coverage adjustment: it attenuates to rho=0.265 (p=0.098) on S3 and 0.227 (p=0.141) on prune. Therefore the manuscript should claim repeatable lineage context within each source, not robust transport of the exact family effect across sources.

Four semantic trait anchors are available across final cores. Their log-S3 mean memory ordering agrees for 5 of 6 pairwise comparisons (Spearman rho=0.80). This is descriptive only.

## Deep phylogeny

In BIEN, family-to-family trait-ranking disagreement is not detectably related to deep family patristic distance:
- log-S3 rho=0.037, p=0.340;
- log-prune rho=-0.011, p=0.529.

The lineage-specific ranking is therefore mosaic rather than a smoothly inherited family-level hierarchy in the discovery data.

AusTraits gives the same null result independently. Among 41 families with valid full-backbone representatives:

- source-native S3 shared>=4: rho=-0.051, p=0.878;
- source-native prune shared>=4: rho=-0.079, p=0.947;
- matched-log S3: rho=-0.071, p=0.858;
- matched-log prune: rho=-0.057, p=0.799.

Thus the re-ordering is phylogenetically mosaic in both compilations rather than a smooth deep-family inheritance pattern.

## Robustness of re-ordering

The matched-log AusTraits result survives progressively stricter species-support thresholds. S3 reversal remains roughly 47-49% from >=20 through >=150 species per system; prune remains similarly high over thresholds with enough well-represented pairs.

Functional modules do not explain the effect. In AusTraits matched-log S3, within-module reversal is 50.9% and between-module reversal 49.1%; prune gives 50.8% and 50.2%, respectively. BIEN shows the same qualitative pattern.

The family-wide context is also stable to measured tree/data geometry in AusTraits: S3 repeatability 0.296 becomes 0.299 after species-count/prune-fraction adjustment, and prune 0.391 becomes 0.397 after native-species-count adjustment.

## Mechanism remains open

Exploratory screens do not identify family crown age, family richness, perennial fraction, or woody fraction as a robust explanation of the lineage-wide context. A BIEN prune-only richness association does not reproduce on BIEN S3 or in AusTraits.

The paper should therefore stop at the architectural result: lineage context is repeatable, but the ecological/evolutionary driver remains unidentified.

## What changes relative to previous comparative biology

Previous work established:
- phylogenetic signal is widespread;
- trait categories differ on average;
- the same trait can show different signal or evolutionary dynamics in different clades.

Those facts do not distinguish a marginal trait effect from a lineage-level rule.

This study directly separates:
- **trait-average portability** from
- **within-lineage rank portability**.

The key result is that the former can be real while the latter disappears.

Thus a statement such as “trait X is generally more phylogenetically conserved than trait Y” can be informative as a population-level prior while being a poor prediction for a particular lineage.

## Central claim

> **Traits carry weak global priors in phylogenetic memory, but lineages strongly reconstruct their relative ordering.**

Conceptual version:

> **A reproducible macroevolutionary average need not be a rule that individual lineages obey.**

## Possible title language

- **Lineages rewrite the hierarchy of phylogenetic trait memory**
- **Global trait priors conceal lineage-specific re-ordering of evolutionary memory**
- **Weak trait priors and strong lineage contingency in phylogenetic memory**

Avoid “universal hierarchy” in the title because the prospective rank-portability test failed.

## Figure logic

1. **Conceptual decomposition** — trait prior T, lineage shift F, lineage-specific deviation U.
2. **Absolute versus rank portability** — BIEN and AusTraits side by side.
3. **Re-ordering effect size** — observed pair-order reversal and fraction of pair-specific maximum.
4. **Variance architecture** — family / trait / residual or system components and model-implied reversal.
5. **Lineage context** — within-source repeatability plus exploratory cross-source family BLUP correspondence.
6. **Deep phylogeny** — family distance versus rank disagreement.

## Hard boundaries

- The strict prospective portable-hierarchy architecture was not validated.
- Trait identity is not zero.
- Re-ordering does not imply random evolution.
- rho is not an evolutionary rate.
- The residual/system component is not a diagnosed mechanism.
- AusTraits is independent-compilation validation, not fully verified independent-source replication.
