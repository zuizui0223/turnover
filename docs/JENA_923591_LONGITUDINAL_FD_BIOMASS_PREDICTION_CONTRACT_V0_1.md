# Frozen retrospective long-term Jena FD vs biomass transport benchmark v0.1

**Frozen 2026-11-14, before running any 2003–2012 FD-to-biomass model.**

This is a focused follow-up to the May 2003 planned functional group count effect: a temporal *transportability* test within the same experimental site and the original publication's data, **not** cross-site macroecological validation or evidence for BIEN phylogenetic trait-memory causality.

## Verified pre-outcome input sources
- PANGAEA DOI [10.1594/PANGAEA.923591](https://doi.org/10.1594/PANGAEA.923591), PINNED `predictors_raw.zip` SHA 4af2ccca7b85b7a15b47ace87acfe0386feab79da51d3d5f67b3cf6034442e4b, `biomass02_12.zip` SHA aa4e4904c200e4a7d35cfd713a47969b3c08f014bccfe330cefe245ee1e875db, `traits.st.zip` SHA 5ae74c473ff2e36861f137f4fc8a28740725a90dda9e265350fd45bcb38996c5.
- Original [plot information](https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt) SHA 7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70.
- Original 78-plot subset, 1,541 exact plot×year×season matched cells, 2003–2012 (772 spring / 769 summer), four prespecified FD trait columns fully present after original PCA imputation. [Source-only QA](../results/biomass_jena_2003_source_v0_1/longitudinal_fd_biomass_join_qa_v0_1.json).
- Author's original script [main analysis.r](https://github.com/fonsvanderplas/traits-and-ecosystem-properties/blob/master/main%20analysis.r) documents May/Jun → spring and Aug/Sept → summer, species composition-based Rao FD, PCA-imputed static species traits, median aggregation across plant biomass harvest subsamples; original cohorts may be response-selected and must not be treated as unbiased new community sampling.

## Exact temporally held-out target and contrasts

**Single unit**: distinct plot × year × season; subsamples within plot/year/season aggregated to one **median of nonmissing nonnegative source `target.biomass`**. Preserve zeros, exclude -9999/NA, do not claim `target.biomass` g/m² until original source units confirmed. Outcome `y=log1p(median_biomass)`. Never equate with annual NPP.

**Temporal split frozen**: train 2003–2007, test 2008–2012. Repeated records from the *same* 78 plots in train and test are intentional and are **NOT spatial generalization**. All four models use the **same complete-case plot/year/season cells** and the same exact data year split. No test-year biomass used to select features or preprocessing.

**M0 design baseline**: intercept; `log2(NumberSownSpecies)`; `NumberFunctionalGroups`; binary summer indicator; `year-2003`; original block indicators (three columns). These planned treatments come from the 2002 original allocation, not computed from realized biomass.

**M1 continuous FD extension**: M0 + `FD_h1`, `FD_sla`, `FD_leafN`, `FD_SeedsTCW`. All four fixed before viewing target effects; original author-derived Rao FD values are *source-derived* and may carry source-study/imputation leakage. This measures a concurrent trait-FD explanation, **not a future forecast**.

**M2 CWM/identity contrast**: M0 + four `FI_h1`, `FI_sla`, `FI_leafN`, `FI_SeedsTCW` on identical training/test cells.

**M3 combined**: M0 + both groups of four. For M1–M3 each trait predictor z-standardized from training rows only; fail if nonfinite or zero training SD. No feature choice, no tuning after outcomes. Use OLS with all full-rank fixed design matrices. If any model rank deficient, HOLD instead of cherry-picking.

**Primary score**: future 2008–2012 pooled test SSE gain `G_FD=1-SSE(M1)/SSE(M0)`, tested against 0. Report negative as informative. Parallel descriptive `G_FI`, `G_both`; `G_FD` is primary for this retrospective within-site benchmark, not a confirmatory hypothesis since prior analyses examined these outcomes in the same experiment.

**Uncertainty**: paired bootstrap by *plot ID*, 2000 replicates (seed=20261114) of existing holdout predictions, same plot multiplicity across seasons/years, 2.5/97.5 percentile CI for `G_FD`. No treating 1,541 rows as independent. Report season-specific test score as *descriptive* (not separate significance claims). Train/test mean-based R² by year and sample sizes can be reported, but do not present post-hoc selected traits.

**Data-quality conditions:** full source hash match; 78 expected plot IDs; all four FD and FI columns required; ≥50 plots in both train/test; each split ≥300 plot/year/season samples; ≥4 train years and ≥4 test years; identical complete-case population across models; at most one biomass calendar month per season; reference Jena original plot code must match; no missing original block/richness. Otherwise fail closed.

## Interpretation
Van der Plas et al. (2020, *Nature Ecology & Evolution* 4:1602–1611) already report limited cross-year ecosystem property prediction with plant traits, and Hagan et al. (2023, *Nature Ecology & Evolution* 7:332–334) challenge general interpretation of trait predictability. This *new data-path QA + locked low-dimensional benchmark* is an **internal assessment** of the earlier May/Autumn mismatch and temporal portability; do not present Jena trait-FD/biomass association as a new empirical first discovery. If enough future-year FD predictive gain exists, it supports only conditional same-site prediction. The global/NEON multi-site study is unchanged, and authenticated NEON plot-level access still required.
