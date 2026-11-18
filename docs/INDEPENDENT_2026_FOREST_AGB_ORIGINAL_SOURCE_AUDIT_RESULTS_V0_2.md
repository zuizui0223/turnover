# Independent 2026 forest AGB × trait original source audit: 200 plot records, **no reconstructable K→FD→AGB**

2026-11-18, separate new source pilot based on original `main`, not a continuation of the exploratory 2026 BIODEPTH (Draft #46–53) or TreeDivNet (Draft #54–57) reanalyses. **Original independent Zenodo DOI:** [10.5281/zenodo.19609795](https://doi.org/10.5281/zenodo.19609795), Ali 2026 *Plant-trait syndromes and environmental filtering drive biomass ecology in resource-limited forest ecosystems*. Original published site+species functional composition work differs in provenance from original BIEN 201-system memory. No source study scientific effect reproduced or estimated.

## Exact original data files verified

Official API `https://zenodo.org/api/records/19609795` returned public official record ID/DOI and two original files:
- `Forest_AGB_Data. Final.csv` original **67,552 bytes**, exact MD5 `c3ffed15932611dca604dcd9e67d9bb8`.
- `README Dataset Description.txt` original **1,686 bytes**, exact MD5 `6f0e782ec7968d35f5ee5f5539124b24`.
- Both were downloaded independently in a GitHub Actions runner with original size + MD5 checks and **never committed** as raw/source files. Their original source-level column and row counts are independently testable.

### Source geometry

| Original field/source check | Result | Meaning |
| --- | ---: | --- |
| Source numeric/identifier records | **200 rows × 28 columns** | Actual file rows, not inferred from abstract |
| Original source plot identifier | `Plot code` | v0.1 simple parser missed this exact header; v0.2 fixed parser, no source change |
| Original source site identifier | `Site` | **3 source site categories**, with **40, 70, 90** uniquely identified plot rows respectively |
| Duplicate `Site×Plot code` combinations | **0** | **200 distinct source original plot keys** |
| Published dataset has original `AGB` field | **200 finite numeric, zero NA** | Numeric present, but physical interpretation fails below |
| Original species×plot names / native measured trait rows | **none** | Cannot reconstruct species assembly, patristic phylogeny or original trait-specific K from this CSV |
| Community trait fields | `FDis,FDiv,FEve,FRic,FDomin,CWM_LDMC,CWM_SLA,CWM_Hmax,CWM_DBHmax,CWM_Crownmax` | **Precomputed** functional diversity/mean traits, no original source species rows |

### **Critical contradictory source-scale interpretation**

The *actual original README* describes `AGB` as **aboveground biomass (Mg ha−1)**. However actual original CSV values are:
- **157/200 (78.5%) AGB negative**; 43 positive, 0 zeros, no missing. Original study-wide aggregate AGB ranges **−0.538 to +1.977** (mean −0.1255, population SD 0.6046). These cannot be untransformed physical dry biomass in Mg ha−1.
- `Latitude` mean essentially zero and population SD **0.99750**, with 81 negative values; `Longitude` similarly essentially zero and SD **0.99750**, with 80 negative. This is strong evidence that the original released numeric table contains **transformed/centred/scaled variables**, not a raw geographic-coordinate or physical-field-biomass record. Yet no original inverse transformations can be reconstructed safely from these aggregates.
- A line-by-line original README audit found **no explicit standardization/inverse-transform recipe**. Initial v0.2 technical parser mistakenly matched the substring `unit` within `community` and incorrectly flagged a “standardization term”; this was **corrected** to exact word-boundary matching and **source revalidated**. The definitive original README explicitly claims Mg ha−1, but no credible original AGB physical units follow from negative source entries.

This is a **source labeling/units inconsistency** requiring original author or processing-code clarification. It is not evidence that forest standing biomass can be negative, nor proof of exactly which standardization method was applied. Likewise, `Latitude` and `Longitude` should never be mapped as original geographic coordinates without the authors' projection/normalization/source lon-lat lookup.

## Verdict by intended scientific claim

- **Original public file access, DOI and checksum provenance:** PASS.
- **Original plot key geometry:** PASS, 200 unique plots /3 labelled site categories. Note source site categories are not automatically independent forest study programmes.
- **Original physical aboveground biomass variable:** **SOURCE SCALE HOLD**, because original README claims Mg ha−1 and 157 negative observations are physically impossible as untransformed mass. No inverse parameters.
- **Direct original species×plot trait matrix:** **PLOT_SUMMARY_ONLY HOLD**, with only original already-computed FDis and CWM fields. Consequently direct original tree trait Blomberg K, trait-specific phylogenetic memory and K→FD→biomass source bridging are **NOT QUALIFIED**. No calculated coefficients are published from this source audit.
- **Current research status:** `PLOT_SUMMARY_ONLY_HOLD` for the intended independent K→FD→AGB programme. A separate source-precomputed FD vs transformed source AGB statistical analysis would be a **different retrospective estimand**, reuse authors' own published effect, and still lacks physical AGB scaling; it is not pursued or reported to rescue any positive outcome.

## Independent candidate contrast

The other currently verified independent public original source, [Bauer et al. 2026 Zenodo 19710211](https://doi.org/10.5281/zenodo.19710211) / [GitHub `markus1bauer/2025_greeen_prairie@v0.2.0`](https://github.com/markus1bauer/2025_greeen_prairie/tree/v0.2.0), **does** provide raw species cover and source measured SLA/height (the original `data_processed_traits_measured.csv` has only **three named species**), but its original processed sites/species metadata publishes **coverage, richness, soil moisture, management** rather than original independently measured aboveground plot biomass. **Original cover is not biomass**, so this candidate is `SOURCE_BIOMASS_MISSING_HOLD` for the same question. This exclusion was verified from original pinned repository tag/tree and field dictionary, not by interpreting vegetation cover as biomass.

The newly catalogued 2026 Boettiger et al. [Dryad `10.5061/dryad.mpg4f4rh5`](https://doi.org/10.5061/dryad.mpg4f4rh5) has independently documented original species traits and plot-year species cover and the authors analyse temporal biomass stability in **a single regional grassland experiment** (36 source species), but the exact original *raw measured plot×year biomass* access/join is not verified here. Do **not** claim its previously published derived FD indices or biomass stability effects as raw physically measured source masses. It cannot support 12 disjoint families×20 species global K in its present single original experiment.

## What now makes a novel, decisive original next step?

A genuinely independent original study with **source measured species×plot traits**, original **species membership** and **source plot dry matter biomass with physical units** across sites and independently qualified dated phylogeny is needed. **A sample containing only 36–40 species cannot internally estimate the originally frozen 12-family×20-species K architecture.** Avoid repeating more ad hoc FE regression subgroups on the same published site data. If a single independent source lacks sufficient families, an explicitly separate study would need a **predeclared multi-study aggregation** with exact taxon, site, trait-origin, biomass grain, year, and family-K portability contracts.

## Reproducibility

- v0.1 original source API + MD5 schema audit **[Actions #44224176076 SUCCESS](https://github.com/zuizui0223/turnover/actions/runs/44224176076)**; artifact #14392461102, digest `sha256:8d7acda7606fc8abd7f02468807c8d9ebbc72cada9d704969c53232723399ef5`.
- v0.2 corrected exact `Plot code`, original AGB/README sign+units **[Actions #44225131413 SUCCESS](https://github.com/zuizui0223/turnover/actions/runs/44225131413)**; artifact #14391858950, digest `sha256:68b9b4343a5540d9e9a6ccda2aaa29a80a71c9ddd061cc306b1d52ccd2d996f2`.
- Permanent nonraw source provenance + statistics: `results/independent_zenodo_19609795_original_AGB_trait_source_audit_v0_2.json`, source scripts `scripts/source/audit_zenodo_independent_forest_agb_trait_grain_v0_1.py` and `scripts/source/audit_zenodo_independent_forest_agb_plot_scale_v0_2.py`.
- Pre-result fixed source plan `docs/INDEPENDENT_K_FD_AGB_NEW_SOURCE_PILOT_20261118.md` and source follow-up contract `docs/INDEPENDENT_FOREST_ZENODO_AGB_SCALE_AND_PLOT_GRAIN_FOLLOWUP_20261118.md`.
- Original general BIEN×sPlotOpen, old BIODEPTH, NEON authorization, and the already closed original TreeDivNet PR #57 FD transport estimand remain untouched. Only independent Draft branch, unmerged.
