# Matched-species feasibility for all 12 AusTraits functional trait K comparisons

**Audited 2026-10-15; K-blind species-support result, not a new K ranking outcome.** On the [successful fixed-source pre-K audit #38673955087](https://github.com/zuizui0223/turnover/actions/runs/38673955087), the original **254 family×trait K systems / 42 plant families / 13 named traits** were exactly recovered from the pinned AusTraits v7.0.0 source. The source-calibratable 12 traits excluding `seed_height` produce the original fixed **249 family×trait systems**. Species are original positive source-native unit medians with unambiguous genus, and a pair is eligible at **>=20 shared species of identical binomial and genus**, regardless of the observed K values.

## Support result

| K-blind metric | Original-source result |
|---|---:|
| Same-family, different-trait available comparisons | **770** |
| Pair comparisons with >=20 identical species | **760 (98.7%)** |
| Unique trait-pair types | **66 of 66** with >=1 eligible family |
| Trait pairs with >=5 eligible families | **54 of 66** |
| Median shared species per eligible family×pair | **105** (range 20–2,202) |
| Median overlap as fraction of the **smaller** trait species set | **95.4%** |
| Distinct genus-name conflicts for the same original binomial | **0** |

The median 95.4% denominator is `n_shared / min(n_original_A,n_original_B)`. It does **not** mean the larger trait cohort has 95.4% common support, nor does it ensure identical tip sets before the matched-pair reconstruction.

## Examples with independent family replication

| Pair from K-blind source intersection | Eligible independent families |
|---|---:|
| leaf length vs leaf width | **37** |
| leaf length vs plant height | 34 |
| leaf width vs plant height | 32 |
| leaf width vs seed width | **16** |
| leaf width vs seed dry mass | **15** |
| petiole length vs seed width | **11** |
| petiole length vs seed dry mass | 8 |
| seed dry mass vs seed width | 8 |
| leaf area vs leaf width | **6** |
| leaf area vs seed dry mass | 6 |
| leaf area vs seed width | 5 |
| leaf area vs petiole length | **4** (insufficient for a >=5-family generalization) |

All ten combinations among the five discovery-selected named traits have at least one eligible family, but only nine have >=5. The five signed named-trait deviations were selected **after** the original AusTraits K outcomes and do not constitute independent replication.

## Scientific importance and restrictions

**Why this matters:** If two traits share most of the species in a family, large pairwise K differences cannot simply be attributed to the two traits having totally nonoverlapping taxon sets. But the K comparison remains vulnerable to unequal numbers of tips, unequal exact branch geometry when using the *original* separately sampled trees, trait source calibration differences, taxonomic missingness and phylogenetic covariance. High species overlap alone does **not** show that the original rank survives an identical-tree comparison.

We therefore separately froze a new **post-original-K exploratory** comparison:

1. Intersect the original eligible species for every one of the **760** pairwise comparisons independently of K.
2. Compute both Blomberg K responses on **exactly the same shared tips and S3/prune-only tree** using the phytools-parity-validated linear-time covariance K implementation.
3. Compare matched-tip signed `logK_A − logK_B` against the original K difference, and report loss/gain of pair ordering across the same family. All 66 pair types and all 760 eligible family comparisons remain in the denominator.
4. Report family support and within-pair matched K signs descriptively without significance hunting, adaptation claims or presenting pair-specific taxa as a globally common 12-trait species set.

The full method contract is `data/austraits_k_shared_taxa_cross_trait_design_v0_1.json`, the exact-source support code is `scripts/analysis/audit_austraits_k_shared_taxon_pair_support_v0_1.py`, and the scientific paired-K calculation is in `scripts/analysis/run_austraits_k_shared_taxon_pairs_batch_v0_1.py`, `scripts/analysis/fit_austraits_k_shared_taxon_pairs_v0_1.R`, with quality-controlled aggregation in `scripts/analysis/aggregate_austraits_k_shared_taxon_pair_results_v0_1.py`.

**Hard distinction:** This is **within original AusTraits**, not a source-independent test. Species overlap and matched trees do not, by themselves, disentangle evolutionary constraints from measurement processes or shared environmental conditions. The original five signed rank discrepancies remain exploratory and TRY v7 independent source qualification remains HOLD.
