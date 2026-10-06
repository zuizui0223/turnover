# Trait-rank reordering interpretation v0.1

Status: post-outcome exploratory synthesis of the completed BIEN discovery dataset. This document does not reclassify the prospective BIEN results. The corresponding AusTraits rank-portability test was frozen before any AusTraits memory-loss outcome was opened.

## The sharper biological question

The weak question is whether the exact magnitude of phylogenetic signal is identical across lineages. There is little biological reason to expect that.

The stronger question is whether traits occupy a reproducible relative position on a conservative-to-labile spectrum. If trait biology imposes portable constraints, a trait that is relatively conservative in one lineage should tend to remain relatively conservative in another, even if absolute signal strength changes.

## Discovery result

The 201-system BIEN core contains 45 plant families and 12 traits.

A global-looking trait spectrum is visible. Mean within-family trait ranks are highly similar between the S3 and prune-only tree treatments (Spearman rho = 0.874).

But that aggregate spectrum is a poor rule for a new lineage.

- S3 leave-one-family-out rank gain = +0.0366; blocked permutation p = 0.0036.
- The S3 gain remains positive after every single-trait omission (0.0086 to 0.0654) and every single-family omission (0.0189 to 0.0618).
- Prune-only rank gain = -0.0418; p = 0.226.
- Every prune-only leave-one-trait and leave-one-family sensitivity remains negative.

For the 16 trait pairs represented together in at least 10 families, the median majority ordering is only 63.6% under S3 and 57.5% under prune-only. Only 18.8% of S3 pairs and 6.3% of prune-only pairs retain the same majority order in at least 75% of families.

Across family pairs sharing at least three traits, the mean correlation of trait rankings is only 0.070 under S3 and 0.021 under prune-only.

## Measurement-aware reordering

The measurement-aware model separates sampling variance from latent between-system heterogeneity.

Write latent memory loss as

theta_ft = mu + F_f + T_t + U_ft,

where F is the family component, T the trait component, and U the system-specific component remaining after family and trait main effects.

For the relative ordering of two traits within the same family, F cancels. For two families, the correlation of the two trait contrasts is therefore

r = sigma_trait^2 / (sigma_trait^2 + sigma_system^2).

Under the Gaussian crossed model, the probability that the order of those two traits reverses between two randomly chosen families is

P(reversal) = acos(r) / pi.

Using the measurement-aware S3 point estimates gives r = 0.0939 and P(reversal) = 0.470. Thus the latent relative order of two random traits is predicted to reverse across two random families almost half the time even after sampling error is separated.

The two-way cluster bootstrap gives a median reversal probability of 0.426 (95% interval 0.210 to 0.500); 89.8% of bootstrap replicates imply reversal probability above one third.

The prune-only point estimate is even closer to chance ordering: r = 0.0355 and P(reversal) = 0.489.

This model-based result is the cleanest bridge between the variance decomposition and the biological claim of lineage-specific re-ranking.

## What is known already

Blomberg, Garland & Ives (2003, Evolution, doi:10.1111/j.0014-3820.2003.tb00285.x) established that phylogenetic signal is widespread and that trait categories differ on average, with behavioral traits showing lower signal than several other categories.

Revell, Harmon & Collar (2008, Systematic Biology, doi:10.1080/10635150802302427) showed why phylogenetic signal should not be read directly as evolutionary rate or process.

Ackerly (2009, PNAS, doi:10.1073/pnas.0901635106) showed that the evolutionary rates of the same plant traits can differ by orders of magnitude among clades.

Gilbert & Webb (2015, Annual Review of Phytopathology, doi:10.1146/annurev-phyto-102313-045959) explicitly noted that inference is limited by the paucity of studies comparing the same trait across different clades, and highlighted cases in which the same plant trait shows signal in one clade but not another.

Therefore neither lineage dependence nor heterogeneous signal is itself the novelty.

## What this analysis adds

The new distinction is between an aggregate trait spectrum and a portable lineage-level rule.

A stable average ordering can exist across the full dataset while carrying little information about the ordering inside a new lineage. The global spectrum is therefore not necessarily a conserved biological hierarchy; it can be an emergent average over repeated lineage-specific re-ranking.

This is stronger than saying that context matters, and more defensible than saying that traits possess no intrinsic evolutionary memory.

## Candidate central claim

> A global trait-conservatism spectrum can emerge even when lineages repeatedly reorder it.

Equivalent technical wording:

> Traits show weak average differences in phylogenetic memory, but their relative conservative-to-labile ordering has little robust portability across plant families.

The strongest version should remain conditional on replication in the pre-frozen AusTraits analysis.

## Nonclaims

- Do not claim that trait identity has zero effect.
- Do not claim that S3 rank portability is robust to tree treatment.
- Do not interpret memory-loss rho as an evolutionary rate.
- Do not identify the system-specific component with a particular evolutionary mechanism.
- Do not present the BIEN rank analysis as prospective.
