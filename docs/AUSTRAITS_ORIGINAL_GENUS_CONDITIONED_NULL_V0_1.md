# Genus-count-conditioned original source-selected K rank reversal test

**2026-11-14 — source-fixed, non-independent, post-K-discovery sensitivity. The new genus-conditioned 12-batch results require complete CI and independent verification before being interpreted.**

## Existing original-data finding

- [All-original 142/101 equal-n unstratified pruning #43564505854 PASS](https://github.com/zuizui0223/turnover/actions/runs/43564505854), [permanent SHA256 archive #43565522112 PASS](https://github.com/zuizui0223/turnover/actions/runs/43565522112): actual strict-source surviving tip identities led to 23/142 S3 organ K sign reversals vs 14.8203 mean in 128 same-n family-wide random draws (one-sided Monte Carlo tail 0.0310), while native prune was 13/101 vs 11.2344 (tail 0.3566). K-null draws with an undefined constant organ trait were rejected as a **whole-family draw**, never counted as a zero flip.
- [Whole-family deletion and retained PD audit #43565935858 PASS](https://github.com/zuizui0223/turnover/actions/runs/43565935858) shows the S3 conditional result is sensitive to particular contributing families (Fabaceae removal tail 0.1163). Source survivor native PD can be unexpectedly small even for K comparisons without a rank inversion.
- [Independent strict rebuilt-tree versus fixed broad-tree induced K parity audit #43566078839 PASS](https://github.com/zuizui0223/turnover/actions/runs/43566078839) finds **all 142/101 original pairwise signs agree** and actual strict survivor versus originally reconstructed strict source K log-delta differs by ≤4.02e−9 (S3) / 5.0e−16 (prune). Therefore the original stage1→2 comparison in these cases is not an artifact of a different K direction assigned by phylogeny construction. Taxon identity, retained source trait states and the induced original covariance/normalization remain linked.
- The 142/101 source-selected original reproductive/vegetative grouping remains post-discovery; source and family pairs overlap and the two native phylogenies are NOT independent biological validations.

## Additional question: which GENERA survive, or which species within each genus?

The unstratified matched-n randomization makes all original broad-tree species in a family exchangeable. It therefore does not by itself distinguish selection of a **nonrandom set of genera** from selection of unusual **species within retained genera**.

The new [genus-count-conditioned original source K randomization CI #43566577755](https://github.com/zuizui0223/turnover/actions/runs/43566577755) uses the SAME original AusTraits v7.0.0 SHA256-pinned nonflora median values, same original broad S3/native prune trees and **exact fixed original 142/101 family×trait pair IDs** as the prior null, but for every original trait pair and original native tree treatment it fixes the **observed number of stricter-source surviving tips in each original taxonomic genus**. Each of 128 within-genus draws replaces the actual surviving species identities by random available broad-tree species within the SAME genus, respecting exact retained genus quota and total n. Every genus selection uses a **shared seeded family-wide species-rank** to retain overlapping trait-pair dependence within a family. A missing genus count or original baseline K mismatch is a hard error. Undefined random K with zero trait variance must be rejected as a WHOLE-family rank draw.

The intended comparison is (a) actual K sign flips, (b) unrestricted same-n across-genus random flip distribution, and (c) genus-count-conditioned within-genus random flip distribution. This is a **conditional descriptive decomposition**, not a causal manipulation of the real phylogeny, nor a new ecological/evolutionary confirmation.

**Interpretation rule pre-specified for this audit:**
- If the observed actual flip rate is unusual relative to unrestricted same-n random loss, but ordinary relative to genus-count-matched loss, **which genera survive is a plausible major contributor** to original K sensitivity; does NOT demonstrate specific ecology or selection.
- If still unusual relative to genus-count-matched loss, **within-genus identity or additional source/trait value differences remain plausible**, with missingness and K margin confounding.
- If no genus contains alternative available broad-tree species under observed strict quota, that pair is deterministic under genus-conditioned draws; report this structural limit rather than inventing variation.
- The original S3/prune results may differ in either null. No multiplicity/post-selection corrected p-value, biological independent replication or biomass allocation claim follows from any null outcome.

## Data management and next evidence

The original source Parquet checksum is 5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99. All raw species/genus names, states, source datasets and observation IDs remain inside ephemeral GitHub Actions jobs and are **never** committed by either null; all persistent files are derived K summaries and SHA256 audits. A permanent archive workflow is *staged but will not be triggered before the entire 12-batch/full-142/101 genus conditional run passes*.

The original [GIFT 3.1 accepted-name overlap #43562257361 PASS](https://github.com/zuizui0223/turnover/actions/runs/43562257361) gives growth-form/woodiness for many matched species, but woodiness, stature and single-seed mass are NOT directly measured whole-plant biomass or reproductive allocation; GIFT/TRY primary original study overlap remains a non-independence concern. A genus-based result may prioritize later GIFT life-form and source-study attribution rather than serve as a substitute for them.

**Paper status:** This optional sensitivity belongs in exploratory supplemental research pending authors' scientific review. Do not reclassify the post-selected organ hypothesis as preregistered, change the frozen core K counts or claim a journal submission. PR #38 remains Draft, unmerged and unsubmitted.
