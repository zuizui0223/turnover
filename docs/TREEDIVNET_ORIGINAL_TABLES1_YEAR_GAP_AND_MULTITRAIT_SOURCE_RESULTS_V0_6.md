# Uploaded original TreeDivNet Table S1: actual inventory years permit two-trait FD *source eligibility*, not new ecology

**Source checked 2026-11-16.** The original `fec70320-sup-0002-tables1.xlsx` was uploaded by the user and directly read with `artifact_tool` (original 16,088 bytes, SHA256 `245fdf2002240b905b032c9f444a9a359991212be93032637c9ed80a27516fee`). The workbook contains source `Table S1` A1:AA13 and original `Caption` stating that **each trait and biomass has its own inventory year**. The uploaded original copyrighted XLSX file is NOT redistributed on GitHub; only source year/site/caption metadata are in `results/treedivnet_uploaded_original_TableS1_inventory_years_source_v0_6.json`, labeled as locally transcribed. The Actions runner independently reproduces source plot/trait counts against the public original **Figshare DS1/DS2 MD5-verified records**, but cannot re-open the upload bytes in GitHub.

## Important correction: original Table S1 supplies actual per-variable inventory years

The earlier v0.5 claim that available source metadata included *only establishment years* is now **superseded**. Actual Table S1 reports a unique woody biomass inventory year at most sites and distinct SLA, LNCM, WD, LPCM and height-increment inventory years.

| Study site | Woody stock inventory | SLA year, difference | LNCM year, difference | WD year, difference | Fixed main 2-year support |
| --- | --- | --- | --- | --- | --- |
| B-Tree | 2021 | 2022, **1** | 2022, **1** | 2021, **0** | SLA, LNCM, WD |
| BIOTREE Kaltenborn | 2019 | 2016, **3** | 2016, **3** | 2021, **2** | WD only |
| **ECOLINK Uppsala** | **2017+2020+2023 cumulative harvests** | 2022, 1 nearest | 2022, 1 nearest | missing | **Not in standing stock/tree species-diversity primary cohort** |
| FORBIO Gedinne | 2021 | 2021, **0** | 2021, **0** | 2021, **0** | SLA, LNCM, WD |
| FORBIO Hechtel-Eksel | 2019 | 2021, **2** | 2021, **2** | 2021, **2** | SLA, LNCM, WD |
| FORBIO Zedelgem | 2018 | 2021, **3** | 2021, **3** | 2021, **3** | **none**, 12 original source plots lost |
| IDENT Freiburg | 2021 | 2021, **0** | 2021, **0** | 2021, **0** | SLA, LNCM, WD |
| IDENT Macomer | 2022 | 2022, **0** | 2020, **2** | 2021, **1** | SLA, LNCM, WD |
| MataDIV (fertilized study context) | 2024 | 2022, **2** | 2022, **2** | not available | SLA, LNCM |
| MyDiv | 2021 | 2021, **0** | 2021, **0** | 2017, **4** | SLA, LNCM |
| ORPHEE | 2021 | not available | 2018, **3** | 2021, **0** | WD only |

- This was measured **per site / variable**, not each original individual tree or leaf and not exact observation day or plot-level tree/sampling provenance.
- The source identifies **FORBIO Hechtel-Eksel establishment as December 2010**, correcting the earlier turnover v0.5 secondary ledger that reported 2012; its biomass inventory year is **2019**, so this establishment discrepancy does NOT change the new time-gap rule. FORBIO Zedelgem establishment spans Dec 2009 + Mar 2010.
- User-uploaded Methods S1–S3 independently establishes ECOLINK is **genetic-diversity manipulation** and its biomass is accumulated coppice harvests, not generic single-time standing biomass. ECOLINK must not be saved by using only the nearest of its three source harvest years.

## Frozen original source eligibility: woody stock vs *same trait's* Table S1 inventory gap ≤2 years

Original exact source joins and 186 preliminary woody+positive measured-trait plots across 11 original experimental sites replayed from public MD5-pinned Figshare DS1/DS2. Excluding ECOLINK gives the previous preliminary 153, excluding MataDIV further gives 143.

| Source population | Original preliminary source plots | Original plots with at least two different trait-positive species for *one* allowed time-matched trait | Original sites with ≥8 qualifying original plots | Distinct represented species | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| All original 11 studies (coverage diagnostic; includes ECOLINK incomparable response) | 186 | **174** | 9 | 38 | Source-only pass |
| **Exclude ECOLINK** | **153** | **141** | **8** | **34** | **SITE_INVENTORY_YEAR_SUPPORT_PASS** |
| Also exclude fertilized MataDIV for sensitivity | 143 | **131** | **7** | **28** | **SITE_INVENTORY_YEAR_SUPPORT_PASS** |

All **12 lost ECOLINK-excluded source plots** came from **FORBIO Zedelgem**, where all three principal trait axes are from 2021 vs original 2018 woody stock (3 years). For the **141-plot** ECOLINK-excluded original source population, available plots with ≥2 positive **same-axis** species at year gap≤2: **SLA 117**, **LNCM 120**, **WD 56**. Each uses original DS1 plot woody, never summed species-row woody.

These are NOT 141 independently matched leaf/woody sample dates. They are site-level inventory-year-aligned original source records and still lack individual sample lineage and original species-row woody/plot normalization (321/328 source arithmetic identity only; seven unresolved discrepancies).

## Multivariate FD: exact same two species must have all axes and match all inventory years

**Separate source-only FD feasibility test frozen before these counts**, requiring the *same original DS2 site×plot×species source row* positive on every selected axis, at least two such species per plot, and independently within-2-year inventoried original source years for every axis.

| Original source cohort | ≥2 species jointly SLA+LNCM | ≥2 species jointly SLA+WD | ≥2 species jointly SLA+LNCM+WD |
| --- | ---: | ---: | ---: |
| All 11 original experiments (includes ECOLINK as source diagnostic only) | 150 | 34 | 34 |
| **Exclude ECOLINK** | **117 plots / 7 sites / 32 taxa** | **34 plots / 4 sites / 15 taxa** | **34 plots / 4 sites / 15 taxa** |
| Exclude ECOLINK + MataDIV | **107 plots / 6 sites / 26 taxa** | 34 | 34 |

The pre-frozen minimum is ≥**80 original plots, ≥5 named study sites each ≥8 source plots, ≥20 species**. **SLA+LNCM meets all source coverage thresholds**: after ECOLINK exclusion **117 plots, 6 sites each ≥8, 32 species**; further excluding MataDIV **107 plots, 5 sites each ≥8, 26 species**. **SLA+WD or three-trait source FD FAIL** (34 plots, only 2 sites each ≥8 and 15 species) and should not be promoted by loosening criteria.

The 117 two-trait eligible source plot counts by study: **B-Tree 9**, **FORBIO Gedinne 12**, **FORBIO Hechtel-Eksel 12**, **IDENT Freiburg 4**, **IDENT Macomer 12**, **MataDIV 10**, **MyDiv 58**. Only 6/7 participating sites have ≥8 eligible plots, and MyDiv is ~49.6% of total 117 source plots. Any future source-site-generalization test needs whole-study-site holdouts and equal-site weighting; do not treat 117 plots as 117 independent forests.

## What the original data now permit — and what is still not permitted

**New source success:** the original supplementary Table S1 genuinely resolves **site-level measurement/inventory year support**, rather than only planting-year metadata. It removes one source uncertainty for 141 original plot eligibility and 117 source two-trait FD feasibility. This supports a narrow original-source **two-trait SLA+leaf-N source FD** research route without source-filling from TRY or prior FDis reference values.

**Unresolved source contracts, not optional for declaring an *independently measured individual trait* result:** user-uploaded Table S1 does not expose original tree/leaf sample IDs; it only reports site-variable inventory years. Uploaded Methods S3 says leaf nutrients were measured and averaged by species and plot but not individual original rows/years. The earlier DS2 species-row woody mass accounting is unresolved: **DS1 = arithmetic mean DS2** in 321/328 original plots, with seven exceptions; the new year table has no explanation. A valid future response would be **one DS1 woody mass per unique site×block×plot**, not summing DS2 species rows. Do not silently assert the DS2 woody species value is a raw biomass contribution or proportional weight.

**No ecological mechanism has been tested here.** The source data reuse the same experimental network already analyzed by Jensen 2026 (original positive mixing effects), not an independent confirmation of its original results. The original dataset has only ~40 tree taxa, far below 12 families ×20 species to infer original family-level evolutionary trait-memory K. We have not estimated FD→woody biomass, PD→biomass, K→FD or causal mediation. Historic original global BIEN/sPlotOpen, original BIODEPTH and NEON authentication gates stay HOLD.

## Reproducibility and provenance

- Original user-uploaded Table S1 original bytes locally hashed and imported with **artifact_tool**, original Excel not committed.
- Immutable locally inspected original inventory-year ledger: `results/treedivnet_uploaded_original_TableS1_inventory_years_source_v0_6.json`.
- Site-time original plot support: `results/treedivnet_original_TableS1_woody_trait_gap2_site_source_v0_6.json`.
- Same-species multiaxis FD source support: `results/treedivnet_original_TableS1_multiaxis_year_supported_plots_v0_6.json`.
- Frozen methodology: `docs/TREEDIVNET_ORIGINAL_TABLES1_INVENTORY_YEAR_GATE_V0_6.md` and `docs/TREEDIVNET_ORIGINAL_TABLE_S1_MULTITRAIT_SOURCE_SUPPORT_V0_6.md`.
- Original Figshare data source replay [GitHub Actions #43881430051](https://github.com/zuizui0223/turnover/actions/runs/43881430051) **SUCCESS**, nonraw artifact #14232222695, digest `sha256:09310d1aa274151ad550faf49f78c4eb969d03d76f09653d2d4c04dfd808a97c`.
- Same-species multi-axis original source rerun [#43882190312](https://github.com/zuizui0223/turnover/actions/runs/43882190312) **SUCCESS**, nonraw artifact #14232412341, digest `sha256:172cfd4c3e7eb2539bc67e297ab3289e5e8332f47050245760bbddd543b726a0`.

This is source-only and part of Draft PR #56 stacked above original source-only PR #55. `main` remains unmodified; no original individual tree/leaf, sampled original plot keys, raw biological values or uploaded original copyrighted XLSX transferred to GitHub.
