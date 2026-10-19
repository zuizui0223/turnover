# Same-source support feasibility for reproductive/vegetative plant K comparison

**2026-10-15. Source metadata and record availability ONLY; biological K outcomes were neither used nor recomputed.**

[Successful exact source audit #38696272257](https://github.com/zuizui0223/turnover/actions/runs/38696272257) took all **760 frozen K-blind original family×trait pairs** (249 original source-calibratable trait systems, 42 plant families, 12 named traits). It rebuilt the identical original source-native positive species medians and verified every original species-system count in AusTraits v7.0.0 (source data SHA256 `5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99`). It then joined the positive source observations for the two traits **on exact species/genus AND the same AusTraits dataset_id**, separately testing whether the original observation_id was also identical.

## New K-blind shared-original-source eligibility results

| Matched-species family×trait category | Original eligible pairs | Pairs with >=20 species measured by a common dataset_id | Independent families with >=1 eligible common-source pair | Pairs also meeting >=20 species with identical dataset_id+observation_id |
|---|---:|---:|---:|---:|
| **All 12 named-trait pairs** | **760** | **561** | **42** | **556** |
| **Reproductive vs vegetative** | **406** | **279** | **32** | **277** |
| Fruit vs vegetative | 193 | 159 | 30 | 158 |
| Seed vs vegetative | 213 | 120 | 23 | 119 |
| Within the same organ class | 354 | 282 | 42 | 279 |

Among **76,214** original shared species×pair cells for cross-organ comparisons, **47,266** have positive observations from at least one shared source DatasetID, and **46,685** have positive observations from exactly matching dataset_id+observation_id source keys. Species×pair cells are **not unique species across multiple traits**, families or comparisons.

The fixed initial feasibility gate (>=10 independent families, >=5 families in each fruit- and seed-versus-vegetative component, >=20 same-source species per family×pair) **PASSES**, so a purely source-aware K sensitivity is now computationally identifiable. It is still *within original AusTraits*, not external primary-measurement validation.

### Lineage exceptions and trait pairs that need special caution

- **Fabaceae:** 23/36 cross-organ family×pair comparisons meet common DatasetID source eligibility, providing a broad but source-dependent family study.
- **Rubiaceae:** 6/6 qualify. Its reversal of the pooled reproductive-K advantage thus can be rechecked with source control.
- **Casuarinaceae:** only **3/12** qualify. The previously observed vegetative-K advantage in this family must **not** be treated as source-control robust without re-estimation; many of its original cross-organ pairs have no sufficient common DatasetID measurement.
- **Lauraceae:** 8/9 qualify, but its S3/prune organ contrast was tree-sensitive.
- Nine of the original 36 organ-crossing named-trait pair types have **zero** families with >=20 source-shared species. These are **structural missingness, not evidence that organ traits have equal K**. Examples: leaf area versus seed length/seed width and petiole length versus seed dry mass.

### Crucial interpretation

A common `dataset_id` means both traits occur within the same AusTraits contributing *dataset archive*. It **does not establish** that they were measured by the same investigator, in the same field season, on the same specimen, with identical methods or from independent primary source records. A dataset may itself be a derivative compilation. Same `dataset_id + observation_id` is a stronger data-key crosswalk but may still represent group-level/species-level rather than true individual observations, depending on native source semantics. **Neither condition upgrades TRY v7 to independent validation.**

The test asks first whether source-record intersection exists, **before examining the K values of this stricter cohort**. The next permitted exploratory sensitivity will re-estimate both traits on exactly identical shared-source species/tips/tree, using strictly their shared-dataset observations for each trait, and compare with the original all-source medians on the *same retained tips*. This separates measurement source composition from geometry-induced changes but cannot identify evolutionary OU parameters.

## Reproducibility and scientific stop

- [Pre-support frozen source rule](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_k_cross_trait_shared_dataset_support_v0_1.json)
- [K-blind native-source extraction/eligibility code](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/scripts/source/audit_austraits_k_cross_trait_shared_dataset_support_v0_1.py)
- [CI with synthetic source joins, strict original graph reconstruction, and full source support JSON](https://github.com/zuizui0223/turnover/actions/runs/38696272257)
- Original [matched-tip 760 K analysis](https://github.com/zuizui0223/turnover/actions/runs/38674635870) is unchanged.
- The cross-trait organ K effect is a **post-discovery** biological grouping, and further source restriction is a **post-discovery robustness check**, not a second independent empirical confirmation.
- No species names, source measurement IDs or raw trait values appear in public output; original closed BIEN 201-system rho research remains unopened.
