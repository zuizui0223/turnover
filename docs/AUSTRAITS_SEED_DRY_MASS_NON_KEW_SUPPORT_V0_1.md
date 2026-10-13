# Seed dry mass support after excluding the Kew SID source family

**2026-10-13 — source-only exploratory eligibility sensitivity, not an independent dataset validation and not a reestimated Blomberg K result.**

The prior [original cohort provenance exposure audit](https://github.com/zuizui0223/turnover/actions/runs/38404694553) found that original AusTraits `Kew_2019_1` supplies at least one positive seed-dry-mass observation for **3,346 of the 4,242 species×system cells (78.88%)**, in **all 15** `seed_dry_mass` family systems. Its source-native metadata explicitly identifies an aggregated **Royal Botanic Gardens Kew Seed Information Database (SID) and Seed Bank Database**, with nested original dataset identifiers. Historical public TRY DatasetIDs 21 and 565 have the same named database family; **this is not a verified duplicate measurement or TRY v7 membership**.

In an independently [frozen source-only support protocol](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_seed_mass_without_kew_source_support_contract_v0_1.json), we recomputed positive source-native species medians with the sole dataset `Kew_2019_1` excluded, then *intersected* surviving non-Kew species with the exact original AusTraits K-support species. All other 12 original trait supports were required to stay unchanged; no original K effect magnitudes were read, recalculated or reported.

[Successful GitHub Action #38405502183](https://github.com/zuizui0223/turnover/actions/runs/38405502183), source artifact `austraits-seed-mass-non-kew-support-v0-1`.

## Complete original versus no-Kew native species support

<| Original original-K seed-dry-mass systems: 15 families, 4,242 species×system cells.
<| After source exclusion: **2,072 / 4,242 (48.84%) retained**, **2,170 (51.16%) lost**.
<| **13 of 15 families** still have at least 20 positive species medians without `Kew_2019_1`.

| Family | Original species | Non-Kew supported species | Retained |
|---|---:|---:|---:|
| Asteraceae | 653 | 332 | 50.8% |
| Casuarinaceae | 61 | 29 | 47.5% |
| Cyperaceae | 300 | 155 | 51.7% |
| Elaeocarpaceae | 34 | 13 | 38.2% |
| Fabaceae | 1,252 | 464 | 37.1% |
| Goodeniaceae | 138 | 71 | 51.4% |
| Haemodoraceae | 38 | 12 | 31.6% |
| Lamiaceae | 147 | 73 | 49.7% |
| Moraceae | 37 | 22 | 59.5% |
| Orchidaceae | 152 | 142 | 93.4% |
| Poaceae | 502 | 316 | 62.9% |
| Proteaceae | 541 | 314 | 58.0% |
| Rhamnaceae | 109 | 37 | 33.9% |
| Rutaceae | 178 | 65 | 36.5% |
| Solanaceae | 100 | 27 | 27.0% |

The only two original families below the **descriptive** 20-species support threshold after Kew exclusion are Elaeocarpaceae (13) and Haemodoraceae (12). No family/trait was removed from the original fitted K outcomes by this audit.

## Two distinct denominators must never be conflated

- **Kew exposed:** 3,346/4,242 **78.88%** of the original eligible seed-mass species×system cells have a positive Kew source record.
- **Lost after excluding Kew:** 2,170/4,242 **51.16%** are no longer eligible after recomputing the species median without Kew.
- The **1,176-cell difference** consists of original Kew-exposed species×system cells which also have valid positive non-Kew source medians. They are **not certified independent primary measurements**: another compilation may have reused the same original field measurements.
- A `dataset_id` is a database/source identifier, not a guarantee of independent measurement, particularly when AusTraits `Kew_2019_1` is itself assembled from many original references and provenance protocols.

This post-discovery result allows a **clearly exploratory matched-tip sensitivity** to ask whether seed-mass phylogenetic K remains similar when only non-Kew measurements determine the same reduced-tree tip values, but it cannot by itself infer how K changes. A correct matched-tip design must calculate the full-source median **on exactly the retained non-Kew species/tips**, then recalculate the non-Kew median on those same species/tips; contrasting the original full-tree K to non-Kew reduced-tree K would confound source composition with phylogenetic pruning and species number.

## Nonclaims and stop rule

The study's frozen equal-OU/source null result (`RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES`) remains unchanged. The five signed named-trait rank discrepancies were selected after observing the original AusTraits effects and are not prospective confirmations. This source-only exclusion check does not identify evolutionary process differences, selection, original measurement error, or independent TRY v7 records.

The closed 201-system BIEN rho study was not reopened. The [external TRY source genealogy issue #34](https://github.com/zuizui0223/turnover/issues/34) remains open until authorized current TRY v7 record-lineage/trait-family support is available.
