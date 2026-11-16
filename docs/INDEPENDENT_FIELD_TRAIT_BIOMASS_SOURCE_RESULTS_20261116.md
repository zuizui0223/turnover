# Independent plot traits × woody biomass: source-first results, 2026-11-16

## Decision

**Source retrieval: newly successful for original 2026 TreeDivNet Figshare data.** Original site×block×plot×species trait and original plot standing woody dry mass can be joined on 190 original plots from 11 experiments, spanning 40 original taxa. **No new FD→biomass or phylogenetic-memory (K/rho) response inference is yet authorized:** observation-year proof and physical interpretation of original species biomass scaling are unresolved, source trait XLSX contains aggregate species-per-plot values rather than original raw individual tree/leaf measurements, and the author already published biodiversity/biomass effects on this study. Keep all original BIEN/BIODEPTH/NEON HOLDs unchanged.

## A. Independent source access

| Candidate | Official source | 2026-11-16 original access / decision | Why no biological effect |
| --- | --- | --- | --- |
| NASA ORNL DAAC NACP TERRA-PNW | doi:10.3334/ORNLDAAC/1292, CMR `C2539885886-ORNL_CLOUD` | Metadata 200, six granules, 12 original-link candidates; HEAD **403** for both leaf and aboveground woody C original CSV | **AUTH_HOLD**. Published 1296 individual traits/266 biomass record rows/35 species are not verified joined original plot keys |
| Dryad Massachusetts 2026 local trait + forest allometry | doi:10.5061/dryad.kprr4xh8v, public dataset 106480 v7 | Dataset/version/file listing 200, 11 source files, three required CSVs identified; original `trait_obs.csv` file download **401** | **AUTH_HOLD**. Catalog describes 142 original local tree measurements in max 26 original plots, not all 304 inventory plots |
| TreeDivNet 2026 Jensen et al. | doi:10.6084/m9.figshare.31026004.v1 | **Anonymous original data access PASS**: README.txt, DS1.xlsx, DS2.xlsx, DS3.xlsx, all exact published MD5/byte counts matched | **Source structural PASS; new-effect provenance and year/scale HOLD**. No direct K→FD→mass inference |

No bypass, account credential export, recopy of original data, or outcome model fitted. All downloaded original Excel data remain in ephemeral GitHub runners; only aggregate provenance saved.

## B. Original TreeDivNet data structure (new source audit, not copied abstract)

2026 Jensen et al., *Functional Ecology* DOI `10.1111/1365-2435.70320`, reports 11 tree diversity experiments from Europe/Brazil, 40 species; woody mass is **aboveground woody dry mass Mg ha−1 estimated from original tree DBH/other allometry** rather than a direct destructive harvest or year-rate. The author studies themselves already report mixed-community woody/litterfall biomass and SLA shifts. Do not call a new regression using the same data independent replication of their published findings.

Exact Figshare files from public version 1:
- `README.txt`, 8130 bytes, ID 61014400, MD5 `8fd3551d0a2b69fb9dca54b7cdbca422`;
- `DS1.xlsx`, 103401 bytes, ID 61014562, MD5 `ab691e410093885d08ad8738cbdedf91` — 363 original plot source records;
- `DS2.xlsx`, 92898 bytes, ID 61014565, MD5 `571e0ef965e28b8b31dd27f971efeff6` — 689 original species-per-plot source records;
- `DS3.xlsx`, 51698 bytes, ID 61014568, MD5 `888d7a3d156be451966be3ca34b7892f` — 224 original mixture-plot NDE source records.

Original exact original `site × block × plot` key join:
- DS1 363 distinct plots, DS2 340 distinct plots, DS3 224; **DS1×DS2 exact key overlap 328 original plots** (no duplicate original plots or species-per-plot keys), 11 experiment/site labels.
- **190 original plots** have same plot woody biomass and ≥2 distinct species with at least one finite positive original DS2 trait among SLA, WD, leaf N/P and height increment; **40 taxa, 11 experiments**, all 11 site groups contribute ≥8 such plots. Original DS1 mass present on 363 and joined source DS1+DS2 mass present on all 328.
- At least **165 original plots** / 37 species have ≥2 positive SLA species trait records and plot mass (10 experiment labels, only 8 with ≥8 such plots); **LNCM 170 plots/38 species**; **WD 77 plots/22 species**; height increment 190/40.
- This passes structural **≥80 eligible original plots, ≥5 experiments with ≥8, ≥20 species**. This does **not** prove every source number is an individual raw measurement or paired within a ≤2-year collection window.

Main article **Section 2.3–2.5** says leaf and other traits were collected originally at individual tree × species × plot levels and aggregated for paper analyses; 283 site-specific monoculture/17 external literature+TRY/WD values were substituted **only for published FDis**, while other trait/biomass analyses use measured values. Accordingly DS2 published species-per-plot results can be considered measurement-based aggregate source values, but **not direct individual-tree measurement records**, and lack per-cell original measurement source flags. The published `DS3.fdis` also mixes site monoculture estimates with 17 database-sourced values; do not use it as a wholly field-observed independent FD predictor.

The source DS1 and DS2 files have **no recorded original year/date columns**; year matching ≤2 years by exact plot is not source-verified. Do not assert simultaneous ecological measurement merely from matching an original plot ID, though the paper intentionally analyzes those source values together.

## C. A concrete source data-quality issue uncovered and explained, without new ecology

**Initial predeclared strict additive source check** for DS1 stand woody mass vs sum of all DS2 original species woody mass (tolerance `≤max(0.001 Mg ha−1, 1% of stand mass)`) gave **135 of 328 matches (41.16%)**. Original DS2 species count vs DS1 sown richness matched in **322 of 328 plots (98.17%)**, so gross missing species is not the main overall cause of nonadditivity.

**Separate post-observation source scaling diagnosis**, frozen after the initial sum surprise, compared three accounting identities across the same 328 source matched plots:
- Direct sum DS2: 135/328 = 41.2% matches.
- **Mean of DS2 species woody values `sum(DS2)/n_species`: 323/328 = 98.5%**.
- **Mean of DS2 species woody values scaled by original sown richness: 323/328 = 98.5%**.
- Critically, **all 322/322 plots with DS1 richness exactly equal to the DS2 distinct species count match the mean formula** at the fixed tolerance. Among six plots with conflicting source richness/species count, only one matches; five source exceptions remain.
- The source plot-level `sum(species values)/stand` ratios have median 1.0 for richness 1, 2.0 for richness 2, 3.0 for richness 3, and 4.0 for richness 4. This pattern recurs across all 11 experiments.

**Important scientific meaning:** this is overwhelming evidence that the authors' *recorded species-per-plot woody mass* and *recorded plot woody mass* are related by a species-mean normalization, **not an additive partition at the supplied units**. It does not by itself establish whether DS2 represents species-specific per-unit planted area, extrapolated target biomass, study processing, or an unintended source aggregation: the README labels both as Mg ha−1 but does not define this transformation. We have **not repaired, substituted, reweighted or changed DS1** based on the retrospective diagnosis. The original strict `SOURCE_SPECIES_MASS_INTEGRITY_HOLD` remains as an unmodified historical source gate; the post-observation alternative is `SOURCE_SCALE_PATTERN_FOUND_UNCONFIRMED_PHYSICAL_MEANING`.

**Do not derive independent community FD by using the same-year DS2 species woody mass as weights**; original source data indicate a nontrivial normalization and these values would be part of the biomass response. Use only independently and originally defined pre-outcome/sown species weights if a subsequent test qualifies.

## D. Next scientific step and final source status

The actual product of this work is a **reproducible independent source-data population** with original published taxon/plot-specific trait aggregate, real tree-allometry biomass and original multi-site geometry, plus two explicit blockers:
1. The **original experiment-year measurement chronology** (per site biomass diameter/leaf trait census year or author protocol) is not recorded in Figshare DS1/DS2; must establish that paired measurements represent a valid fixed original time window (original gate ≤2 calendar years).
2. The source-specific DS2 woody mass per-species scaling is empirically the species arithmetic mean; **original author numeric meaning must be documented** before using DS2 woody mass for any species allocation or extrapolation.

Even if independently resolved, this is a study of predictive transfer **within one already published 2026 experimental programme**, not a direct trait-specific phylogenetic K→FD→mass test. With only 40 tree species, the old ≥12 families×20 species (≥240) K design is structurally impossible, and original original 201-system BIEN/sPlotOpen, 6-site strict BIODEPTH, and NEON token source gates stay **HOLD**. A future ecological model must be separately frozen and assessed by **leave-whole-experiment-out**, including site-level uncertainty, without reusing published Figshare FDis to claim independent original trait measurement.

## Provenance and exact GitHub executions

- NASA/Dryad metadata/auth: [Actions #43853096898](https://github.com/zuizui0223/turnover/actions/runs/43853096898) SUCCESS, not source file access.
- Figshare article/file manifest (all anonymous public): [Actions #43854584295](https://github.com/zuizui0223/turnover/actions/runs/43854584295) SUCCESS.
- Original read-only Excel schema with all 4 MD5 checked: [Actions #43855200772](https://github.com/zuizui0223/turnover/actions/runs/43855200772) SUCCESS.
- Exact DS1–DS2 source-plot trait and mass join: [Actions #43856186343](https://github.com/zuizui0223/turnover/actions/runs/43856186343) SUCCESS.
- Original direct species-sum woody mass source QA: [Actions #43857493766](https://github.com/zuizui0223/turnover/actions/runs/43857493766) SUCCESS/strict-source-HOLD.
- Post-discovery source scale diagnosis and species-roster cross-check: [Actions #43858126778](https://github.com/zuizui0223/turnover/actions/runs/43858126778) SUCCESS.
- Permanent original nonraw source summaries: `results/independent_field_trait_biomass_source_gate_20261116.json`, `results/independent_field_trait_biomass_treedivnet_2026_source_join_v0_1.json`, `results/independent_field_trait_biomass_treedivnet_2026_mass_hierarchy_v0_1.json`, `results/independent_field_trait_biomass_treedivnet_2026_mass_scale_v0_1.json`.
- Frozen source-first and source-diagnostic contracts reside under `docs/TREEDIVNET_2026_*.md`; scripts under `scripts/source/audit_treedivnet_*.py` and `scripts/source/diagnose_treedivnet_*.py`.

All source data are only transient on GitHub runner, and results in this PR are aggregate-only. No original biological effect fitted, no merging to `main`, PR remains Draft.
