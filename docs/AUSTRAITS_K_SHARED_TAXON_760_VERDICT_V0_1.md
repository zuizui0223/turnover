# Same-tip cross-trait K ranking: mostly retained, not invariant

**2026-10-15 — full exploratory within-AusTraits result, all 26 GitHub jobs successful.** [Source-blind support audit #38673955087](https://github.com/zuizui0223/turnover/actions/runs/38673955087) locked 760 eligible family×trait pairs before the matched-tree K outcomes. [Complete matched-tip workflow #38674635870](https://github.com/zuizui0223/turnover/actions/runs/38674635870) succeeded and archived `austraits-k-matched-taxon-760-final-v0-1`.

## Primary descriptive result

| Tree | K-supported family×trait pairs | Same sign as original different-tip comparison | Reversed sign | Median absolute matched-tip logK contrast | Median absolute change in contrast due to common-tip restriction |
|---|---:|---:|---:|---:|---:|
| S3 | **760** | **609 (80.13%)** | **151 (19.87%)** | **0.5385** | **0.2905** |
| prune-only | **747** | **610 (81.66%)** | **137 (18.34%)** | **0.5886** | **0.2887** |

The prune tree has 13 additional family×pair holds from fewer than 20 matched native tips; they are **not** sign-stable or sign-reversed outcomes. Both traits in each valid pair were estimated on **exactly identical species tips and tree**, using the pinned native V.PhyloMaker2 and parity-checked Blomberg K implementation. Original K comparisons had different species/tip sets. The difference between old and matched contrast combines species inclusion, tree geometry and normalization; it is not a causal partition.

**Interpretation:** The broad cross-trait K ordering is neither wholly a sampling artifact nor invariant to taxonomic support. About one-fifth of originally observed pair signs reverse after identical-tip standardization. The 760 family×pair rows are highly dependent (42 families, 66 pair types), so 80% must not be treated as 760 independent evolutionary replications, or a formal significance estimate. The pairwise shared-tip cohorts differ across pairs; this is **not** a single transitive 12-trait global ranking.

## Five discovery-selected trait hypotheses: 10 matched-tip pairs

The table reports descriptive **median** within-family `logK_A − logK_B`, with alphabetical trait order. The signs are not a direct test of the source-OU residual rank deviations, which were estimated relative to a calibrated null, not simply between raw trait K.

| Trait A – trait B | S3 n / median ΔlogK | prune n / median ΔlogK |
|---|---:|---:|
| leaf_area – leaf_width | 6 / +0.401 | 6 / +0.012 |
| leaf_area – petiole_length | 4 / −0.869 | 4 / −0.651 |
| leaf_area – seed_dry_mass | 6 / −0.447 | 5 / −0.345 |
| leaf_area – seed_width | 5 / −0.527 | 5 / −0.921 |
| leaf_width – petiole_length | 17 / −0.152 | 17 / −0.190 |
| leaf_width – seed_dry_mass | 15 / −0.927 | 15 / −1.216 |
| leaf_width – seed_width | 16 / −0.309 | 16 / −0.330 |
| petiole_length – seed_dry_mass | 8 / −0.759 | 7 / −0.491 |
| petiole_length – seed_width | 11 / −0.693 | 10 / −0.620 |
| seed_dry_mass – seed_width | 8 / +0.110 | 8 / +0.108 |

For leaf width vs seed width, **13/16 S3** and **15/16 prune** families have seed width higher K on matched tips, whereas leaf area vs leaf width is more axis-sensitive (**4/6 S3** and **3/6 prune** families with leaf area higher K). Leaf area vs petiole length has only **4 families**, below the frozen five-family descriptive-generalization threshold.

The five named signed departures were chosen *after* inspecting the original AusTraits K/source-OU outcomes. They cannot be declared independent confirmation of differential evolutionary constraint. Notably, even with the same tips, source-specific measurement regimes, trait definitions, functional covariance and phylogenetic model adequacy are unresolved.

## Conclusions and next discriminator

The defensible result is **partial portability of the observed trait K ordering under taxonomic and tree standardization**, not a universal property of named traits. The previous frozen homogeneous-OU plus source-variation classifier `RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES` remains unchanged, as does the post-outcome 12-dimensional named-rank model-adequacy discrepancy.

To test a **universal named-trait hierarchy**, use a common multi-trait taxon cohort or a source-conditioned predictive model that explicitly handles pairwise different cohorts; do not concatenate the 66 pairwise rankings as one global ranking. To identify process-level differences, genuinely independent primary observations with trait definition and source lineage controls remain required; TRY v7 is not qualified. Closed BIEN 201-system rho results are not reopened.
