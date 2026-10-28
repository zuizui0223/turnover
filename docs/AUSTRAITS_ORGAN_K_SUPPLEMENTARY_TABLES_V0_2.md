# Supplementary data tables — post-discovery AusTraits organ K paper

**Version v0.2 · 2026-10-20 · Reporting-only, outcome-frozen.**

Tables S1–S3 reproduce `data/austraits_organ_paper_claim_registry_v0_2.json`, keyed to completed original analysis runs. The additional family-composition note reproduces only the permanently archived per-family aggregate (`reproductive_vegetative_lofo.json`) with a source-SHA256 audit; no original trait observations were reopened. They report already-observed retrospective descriptive results. The 34–42 family clusters and repeated family-by-pair rows are not independent evolutionary origins, and S3 and prune share the underlying megaphylogeny.

## Table S1. Source qualification, family support and reproductive-K-higher direction

| Analytical cohort | S3: reproductive higher / evaluable cross-organ pairs | S3 families | Native prune: reproductive higher / evaluable pairs | Prune families | What changes |
|---|---:|---:|---:|---:|---|
| Original common-species original source cohort | 313/406 (77.1%) | 34 | 314/397 (79.1%) | 34 | Same species and tree within each trait pair, post-discovery grouping |
| Fruit-only vs vegetative | 149/193 (77.2%) | Not separately frozen | 150/189 (79.4%) | Not separately frozen | Excludes seed trait comparisons |
| Remove seed dry mass comparison rows | 263/344 (76.5%) | Not separately frozen | 268/337 (79.5%) | Not separately frozen | Excludes seed_dry_mass, an influential source-concentrated trait |
| Exclude five dominant online Floras | 221/283 (78.1%) | 29 | 180/233 (77.3%) | 25 | Original non-flora species/trait source support; other secondary monographs can remain |
| Non-flora + common contributing DatasetID on every retained species | 120/142 (84.5%) | 24 | 81/101 (80.2%) | 18 | Strong source/tip restriction: does NOT demonstrate same original physical specimen |

The complete **all-named-pair** LOFO scoring graph has 760 supported S3 pairs and 747 native-prune pairs in 42 families, including within-organ comparison rows. These should not be confused with the 406/397 cross-organ-only descriptive denominator.

*Statistical interpretation:* Each row is a family×two named traits on an explicitly pair-specific common-species tip set. Different rows can share most tips and original measurements; 5,000 whole-family bootstrap replicates quantify family-cluster uncertainty conditional on the retrospectively selected organ grouping. Higher K does not imply a slower evolutionary rate.

**Frozen per-family composition audit (not another independent test):** Reproductive-higher K was the majority of observed contrasts in **27/34 S3** and **30/34 native-prune** families. Whole-family deletion left the pooled pair-weighted direction at **75.1–79.1% S3** or **77.1–80.8% prune**. **Asteraceae** was near 50% (**16/30 S3; 16/27 prune**); **Casuarinaceae** (**2/12; 3/12**) and **Rubiaceae** (**1/6; 2/6**) favored vegetative K under both tree treatments. Three families (**Elaeocarpaceae, Lauraceae, Phyllanthaceae**) switched majority direction between the *related, nonindependent* phylogenies. These are outcome-selected descriptive family observations, not trait-independent samples, corrected subgroup tests or proven family-specific constraints. Source SHA256 and per-family counts: `docs/AUSTRAITS_ORGAN_FAMILY_HETEROGENEITY_V0_1.md`; reproducible reporting gate: `scripts/qa/audit_austraits_organ_family_heterogeneity_v0_1.py`.

## Table S2. Family-held-out K-ranking prediction within a post-selected functional grouping

| Tree treatment | Pooled prior sign accuracy | Organ-only sign accuracy | Pooled Brier | Organ-only Brier | Named-trait Brier | Organ-only Brier improvement, family-bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---|
| S3 | 52.63% | 64.47% | 0.25062 | 0.21378 | 0.21792 | +0.03684 [+0.00433, +0.06388] |
| Native prune | 53.82% | 65.46% | 0.25017 | 0.20671 | 0.21156 | +0.04346 [+0.01946, +0.06338] |

Predictions leave every evaluated family's own K outcomes out of *coefficient fitting*, but the reproductive–vegetative category was chosen after viewing initial K outcomes in this same 42-family data compilation; consequently, the LOFO model is **non-nested to the original hypothesis selection**. The Brier results estimate **conditional retrospective probabilistic prediction scoring**, not a separate reliability/calibration test, not an independently selected evolutionary hypothesis or unbiased prospective transport to another compilation.

**Critical: the 64.47% and 65.46% organ hard-sign accuracies are algebraically redundant with Table S1's reproductive K wins.** The predictor's one coefficient is positive in every heldout-family training sample: original cross-organ winner minus loser margins of **220 S3** and **231 prune** exceed the maximum number (**36**) of cross-organ named-trait comparisons that a single held-out family can remove. For all same-organ rows, predictor x=0 gives probability 0.5 and hence exactly half-credit accuracy. Thus:

S3 identity: **(313 + 354/2) / 760 = 490/760 = 64.47%**. Native-prune identity: **(314 + 350/2) / 747 = 489/747 = 65.46%**. These denominators correspond to the same original common-tip K winners as Table S1; no second independent accuracy sample exists.

There is **no additional independent biological support** in hard accuracy after the 313/406 and 314/397 post-selected reproductive-higher K counts have been reported. Brier probability-score performance remains numerically distinct from that hard-label algebra because the cross-organ predicted probability *magnitudes* are learned on other families, but the category remains post-selected. Exact counts are checked by `scripts/qa/audit_austraits_organ_lofo_accuracy_identity_v0_1.py` (not an additional empirical K analysis).

## Table S3. Exact same-family×named-pair taxon/measurement transitions

| Tree | Frozen pair IDs (families) | Broad non-flora species/tips | Narrow shared-DatasetID-eligible species/tips; all remaining sources | Same narrow species and tree; common DatasetID values only |
|---|---:|---:|---:|---:|
| S3 | 142 (24) | 110/142 (77.5%) | 121/142 (85.2%) | 120/142 (84.5%) |
| Native prune | 101 (18) | 82/101 (81.2%) | 83/101 (82.2%) | 81/101 (80.2%) |

| Tree | Broad → narrow: vegetative→reproductive / reverse, total flips | Narrow all-sources → narrow common-source: vegetative→reproductive / reverse, total flips | Median absolute change in logK contrast: support / source |
|---|---|---|---|
| S3 | 17/6, 23 | 4/5, 9 | 0.1964 / 0.0758 |
| Native prune | 7/6, 13 | 5/7, 12 | 0.2513 / 0.0948 |

Stage 1→2 changes matched species, phylogenetic tip geometry and K normalization jointly, so it does **not** isolate a causal species-sampling treatment. Stage 2→3 uses the same tips and native phylogeny and alters the median values contributed by surviving source DatasetIDs. The apparent strict-S3 improvement is therefore substantially affected by **which species/tips qualify**; the effect is smaller or different under native prune.

## Original workflow provenance

- Original matched-tip K and LOFO organ comparison: [#38686389859](https://github.com/zuizui0223/turnover/actions/runs/38686389859); original matched-tip K batches [#38674635870](https://github.com/zuizui0223/turnover/actions/runs/38674635870).
- Five-electronic-Flora exclusion: [#38922133371](https://github.com/zuizui0223/turnover/actions/runs/38922133371).
- Common remaining non-flora DatasetID and 142/101 results: [#39006469805](https://github.com/zuizui0223/turnover/actions/runs/39006469805).
- Same-pair-ID staged contrast: [#39202352075](https://github.com/zuizui0223/turnover/actions/runs/39202352075).

**Hard boundary:** The six reproductive/six vegetative grouping, and the source/tip restrictions, were proposed after the initial AusTraits K outcomes. No row here supplies independent primary-source replication, identifies OU attraction or selection, or restores a preregistered discovery claim.
