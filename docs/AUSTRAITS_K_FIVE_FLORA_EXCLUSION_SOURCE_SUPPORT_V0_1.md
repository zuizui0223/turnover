# After five electronic floras are removed, a cross-organ K comparison remains possible

**Original source-only 760 trait-pair support audit completed 2026-10-16.** [GitHub Actions #38920414545](https://github.com/zuizui0223/turnover/actions/runs/38920414545) successfully reconstructed **all 254 original AusTraits v7 source-native family×trait eligible species cohorts** and frozen **760 family×two-trait K-blind support pairs**, without opening K effect values. The original morphometric reproductive versus vegetative contrast and its K results were already known before this source exclusion; the new work is **post-discovery sensitivity**, not external validation.

## The five preselected electronic-flora source datasets

The exclusion list was fixed before inspecting the no-flora species support:

- `ABRS_2023`: *Flora of Australia*;
- `NHNSW_2023`: New South Wales PlantNet;
- `RBGV_2023`: VicFlora;
- `NTH_2023`: Northern Territory electronic flora;
- `SAH_2023`: South Australian electronic flora.

Together those five contributing data archives provided **49,746/65,043 = 76.48%** of the 279 previously source-matched original reproductive-versus-vegetative K species×pair×source links. Different source IDs can contribute to the **same pair×species**, so 76.48% is NOT a percentage of distinct specimen measurements. Nor are these five necessarily the only secondary data sources remaining after the exclusion.

The pinned native `method_context_properties` record-level audit [#38705851279](https://github.com/zuizui0223/turnover/actions/runs/38705851279) found **zero numeric K-eligible records explicitly flagged `inferred_from_genus/family/taxonomy`** among 120,853 positive records from these source datasets, while a separate positive control confirmed that thousands of OTHER categorical trait records in those same archives DO carry higher-taxon inference labels. This does NOT establish that the 120,853 numeric records were measured on independent physical specimens: they were scored from textual species descriptions.

## Original matched-species support, before any new K output

All support counts use the *original* source-native units and taxonomic eligibilities (finite measurements, distinct record values, median>0 and unambiguous genus), include **only species originally eligible for the 254 K family×trait systems**, and require two traits in the same family to have exactly matching species and genus.

| Quantity | Original source data | After excluding five electronic flora datasets |
|---|---:|---:|
| Original 254 system×species support cells | 66,330 | **38,875** |
| All 760 possible within-family two-trait source contrasts, >=20 common species | 760 | **527** across 37 families |
| **Reproductive-versus-vegetative organ contrasts, >=20 common species** | 406 across 34 families | **283 across 29 families** |
| **Within those, >=20 species with one identical nonflora original DatasetID covering both traits** | — | **142 across 24 families** |
| Fruit-versus-vegetative contrasts | 193 | **106** with >=20 nonflora species (23 families) |
| Seed-versus-vegetative contrasts | 213 | **177** with >=20 nonflora species (26 families) |
| Within-organ contrasts | 354 | **244** with >=20 nonflora species |

In the 406 cross-organ source-eligible pair population, removing all five floras reduces unique pair×species support cells from **76,214 to 34,152**; of those, **14,731** cells include positive numeric measurements of both organs in at least one common remaining DatasetID. These counts are **not unique biological species across the whole study**, because a species occurs repeatedly in different family×trait pairs.

The frozen descriptive support gates were >=10 plant families with a 20-species cross-organ pair, >=5 families with fruit versus vegetative and >=5 with seed versus vegetative, and >=2 distinct named reproductive/vegetative trait types each. The observed 29-family (23 fruit / 26 seed) K-blind support **PASSES**.

## Biological meaning and next test

A former objection was that a positive source-matched organ K contrast could simply reproduce an online Flora's systematic summary of both leaves and fruits for all species. The 283-pair source population provides a way to test **whether the K contrast survives after removing those dominant electronic flora datasets**, still controlling the exact matched species and their native phylogenetic tree. A [small/large original real-tree K smoke test](https://github.com/zuizui0223/turnover/actions/runs/38921266122) passed for Casuarinaceae (31 species, leaf length vs seed dry mass) and Fabaceae (1,174 species, leaf length vs seed length), showing that **Casuarinaceae can reverse its K organ ordering by source choice ALONE** when the same species and tree are fixed. These two illustrative cases are NOT a prevalence estimate.

The full [283-pair real-tree K study](https://github.com/zuizui0223/turnover/actions/runs/38922133371) uses a fixed K-blind, source-only support cohort, 16 source-count-balanced batches and 5,000 whole-family bootstrap replicates. Source-only comparison is `logK_repro(no-flora)−logK_veg(no-flora)` versus `logK_repro(all sources, same tips)−logK_veg(all sources, same tips)`, separately in original V.PhyloMaker2 S3 and original GBOTB native prune-only trees.

**Strict inference limits:** Both contrast arms remain the *same original AusTraits discovery data*; the nonflora archives can contain secondary monographs, inferred morphology and study reuse. These diagnostics do not determine independent evolution, OU alpha, selection, developmental constraint or homologous organ comparability. The original source-OU scalar rank portability decision, previous post-outcome source module model-adequacy discrepancy, closed BIEN 201-system results, and original TRY v7 external independent-source validation HOLD are unchanged.
