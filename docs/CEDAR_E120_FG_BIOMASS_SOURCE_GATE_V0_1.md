# Cedar Creek E120: independent grassland biomass × functional-group transport source gate v0.1

**Frozen:** 2026-11-15. Source-only checkpoint, before examining any E120 treatment–biomass associations. This new experiment was selected *after* seeing Jena outcomes; all subsequent contrasts are exploratory/replication, not previously preregistered multi-site confirmation.

## Why this extension
Original 2003 Jena result for planned FG richness (+0.168, HC3 p=0.044) weakens after exact sown-species richness adjustment (82 plots +0.127, p=0.151; same-richness-supported 62 plots +0.129, p=0.168; strict block×richness +0.119, p=0.293). No direct effect of phylogenetic-memory rho, multi-trait FD, all-biomass yield or biological competition is established. Cedar Creek E120 independently manipulates planted species (1,2,4,8,16) among four guilds, unlike Jena's 1,2,4,8,16,60; useful to test whether the **FG signal depends on the exact richness adjustment**.

## Grounded public source alternatives
1. **Authoritative:** Cedar Creek LTER E120 [description](https://cedarcreek.umn.edu/research/experiments/e120), 168 randomized long-term plots sown 1994; C3 grasses, C4 grasses, legumes and other non-legume forbs. Original aboveground biomass data EDI PASTA [knb-lter-cdr.273](https://pasta.lternet.edu/package/eml/knb-lter-cdr/273/newest). The 2026 LTER catalog describes measurements 1996–2023, while older individual listing says 1996–2021; identify exact revision, table date range and units independently, do not mix rolling counts.
2. **Republished teaching source:** [ESA TIEE Cedar Creek E120](https://www.esa.org/tiee/vol/v2/issues/data_sets/cedar_creek/data.html) provides 168-plot `DataBonus-Student.xls` with functional group presence and biomass, plus `Species_List.xls`; may be altered/abridged for teaching. Must audit fields, years, units, joins to authoritative source before treating as primary measurements.
3. **Secondary independently distributed subset:** [CRAN functClust](https://github.com/cran/functClust) `CedarCreek.2004.2006.dat`, only 91 plots with planted species indicators and 2004–2006 unsorted biomass. Treat as a subset/port rather than independent ecological replication and audit original row identity; never double-count it with E120 official archive.

## Tier 0 (this turn; no outcome)
- Pin source EDI revision, DOI, access license, entity SHA and original names/definitions for actual annual aboveground plant biomass and original treatment/plot composition. Record EDI revision list, metadata SHA, table count, title and exact URLs. Do not print or upload plot-level biomass measurements.
- Probe ESA `DataBonus-Student.xls` and species list: HTTP, content signature (true XLS), row/column counts, column names, year fields, unique plot IDs, richness and group presence fields, source attribution. Do not infer primary-scale biomass units from an unlabeled spreadsheet.
- Probe CRAN data source inventory, but do not use its 91-plot subset as if it represented all 168 plots.
- Source feasibility gate: exactly identified E120 experiment, at least 100 plot IDs matched to original design, ≥4 annual measurements/campaigns under documented definition (or a distinct single-year externally predeclared analysis), at least 60 plots whose **within richness** support admits ≥2 distinct planned functional-group counts, and no observed biomass effect opened.
- Stop HOLD if original species/FG assignments cannot be reconstructed or biomass measurements do not have known physical units/replicate structure. No retroactive relaxation.

## Next prospective biological analysis (only after source gate)
- Compare historical `log1p(y) ~ log2(sown richness) + FG + field-block` against categorical exact richness, with *the same actual source-defined y*, plot-level independent unit and calendar year as a separate block or repeated measure. Restrict further to levels with FG variation and use plot-level clustered uncertainty.
- **Guild identity** is not independent of guild count: `FG = I(C3)+I(C4)+I(legume)+I(forb)`. A four-group indicator model subsumes FG count, so test equal guild coefficients versus unrestricted identities and held-out-block predictive gain, never include FG count plus all four presence indicators in the same model.
- Do not aggregate differences in **annual productivity** and **standing seasonal biomass** as the same effect without a response-specific meta-analysis; one Jena and one Cedar experiment form exploratory two-study comparison, not worldwide generality.
- Exclude outcome-driven trait/plot/season selection. Preserve exact richness categories and definitions. Permutation within block×richness is a conditional exchangeability test, not a pure guild-count causal randomization.

## Claims explicitly prohibited
No cross-study positive result before actual Cedar source qualification and independent computation. The original sPlotOpen×GIFT×BIEN FD programme remains pre-outcome HOLD (87.7% exact species names vs 90% and 10 rather than 12 BIEN matched families). NEON released data require an official user token since June 2026. Current Jena may-only association is *not* conclusive under richness factor adjustment, and its sample selection sensitivity is not global biology.
