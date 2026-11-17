# Original Jena long-term 2003–2012 source-key and grain audit (v0.1)

**Fixed 2026-11-17 after official source Figshare file manifest/anonymous availability verified, but BEFORE opening original 2020 biological data contents or plot/year/species values.** Zero ecological outcome coefficients, K, time-disparity rho, FD, or predictive scores are to be computed in this gate. The original terminal general time-space BIEN/GloBI gates remain closed.

Official original authored paper: van der Plas et al. 2020, `10.1038/s41559-020-01316-9`. The author Figshare dataset DOI `10.6084/m9.figshare.12834350.v1`, exactly public original author article ID 12834350, with 46 original files (all 46 anonymous file HEAD passed), including:
- `biomass02_12.csv` file #24365000, original 2,120,583 bytes, Figshare MD5 `2e350fae58c653c78edc606dad157533`.
- `CoverMain-JenaExp2003-2015all.csv` file #24365003, 198,989 bytes, MD5 `9a1d6c8ea08e089717ae9933a11394ec`.
- `traits.st.csv` file #24365039, 47,135 bytes, MD5 `8045e7ee38f26b212dbe81aed0039765`.
- `functions raw values.csv` file #24365009, 201,652 bytes, MD5 `dc76132cd190a770eb4b0e8dbdd98c6e`.
- `functions4.st.csv` file #24365006, 360,071 bytes, MD5 `0bb0b5b909f21b1c152086351ad7f240`.
- `predictors_raw.csv` file #24365042, 2,334,726 bytes, MD5 `1ad0602600c00a9c2f580c05ebd8084c`.

**The 2022 reply**, Hagan et al., Figshare 19087640.v1, four public files, is a **reanalysis of the same Jena experiment**, not an independent original 2nd observation source. The PANGAEA `10.1594/PANGAEA.923591` repackage (78 plots / 2003–2012 biomass and 41 traits) is the same source, with publication note that final author scientific approval was absent. Do not double count the original source as 2020+2022+PANGAEA.

## Frozen original row/source-only gate

1. Download **exact** six 2020 files only from official `https://ndownloader.figshare.com/files/<file_id>`, cap downloaded bytes by advertised source size, verify exact length and MD5 before processing; original data stay in ephemeral workflow runner, nothing raw committed.
2. Read complete CSV header and source row counts with Python standard csv; record **only original field names, file byte hashes, row counts, column counts, missingness and exact source key coverage summaries**; no biological response numeric values or per-original-plot/trait records copied.
3. Infer only genuine original grain columns supported by explicit file headers; source aliases for plot ID (e.g., `plot`, `plotid`, `plot_id`) and sampling date/year (`year`, `yearid`) must be exact advertised names. Do not interpret 2002–2012 filename string as evidence of all years actually present.
4. Do not mix `biomass02_12.csv` original species/plot standing biomass with `functions raw values.csv` authors' many original ecosystem-function responses before source time/plot grain understood. Exclude transformed `functions4.st.csv` and `predictors_raw.csv` as source-derived predictors until their transformation/origin is documented; do not leak the original outcome into a source CWM predictor.
5. Declare a **future** independent-by-time source population feasible only if original source files allow exact plot/year join of ≥50 independent original Jena plots across ≥6 source years, with original traits for ≥20 named original plant species and either direct original species-specific plot biomass or explicit plant cover/source abundance at same plot×year. This is a **structural gate**, not a new longitudinal R² test; if plot/year/trait source keys lack unambiguous identity, status SOURCE_GRAIN_HOLD (do not use fuzzy keys).
6. Original Jena 2003–2012 78 plots and 41 traits are **from different papers on the SAME original field experiment**; earlier turnover PR #40 already used Jena standing-biomass data. Distinct year/trait source can be a new longitudinal *estimand*, not an independent entire-study replication of PR #40.
7. Original ecological response may be standing mass vs harvested production, plot-year repeated. Any later predictive comparison must freeze real observation year and original process-specific trait pair *before* scoring, and leave whole later years out; plot blocking must account for repeated measures. Do not optimize based on original 2020 within-year 32.6% vs across-year 12.7% or 2022 correspondence argument.

Only original-source access/schema metrics and source-definitional conclusions are permitted in this branch. All original empirical 2020/2022 authors' R² and prior turnover TreeDivNet negative FD transport values remain **previously published findings** and are NOT newly estimated or independent replications.
