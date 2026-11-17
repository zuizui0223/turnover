# Jena original 2020 author code: exact canonical plotcode, species and year source join (v0.2)

**Frozen 2026-11-17 after primary six public Figshare CSV *schema and source-only row cardinality* (NOT new ecological responses) were opened; before any new raw cross-file key overlap, biomass numeric outcomes, time-heldout FD predictor scores or K.** Jena original dataset uses the same grassland experiment as previously available turnover Jena-guild work, but is ecologically separate from TreeDivNet forest data. No claim of independent second study from the 2022 rebuttal or PANGAEA copy.

## Critical original authors' R code (public source of truth)

Original public authors' `fonsvanderplas/traits-and-ecosystem-properties`, script `main analysis.r`:
- Original biomass file `biomass02_12.csv` has **plotcode** (complete experimental plot code), separately `block` and numeric **plot** reused inside blocks, `subsample`, `year`, `month`, `target.biomass` and 60 species dry biomasses. Its **24 distinct values in numeric plot column are NOT 24 experimental plots**. Never join that `plot` integer alone with other files.
- Original species cover `CoverMain-JenaExp2003-2015all.csv` has `Plot` (author code copies to `plotcode`), `Year`, `Month` and 60 species columns.
- Original `functions raw values.csv` and `functions4.st.csv` have `plot,year` at **78 complete main Jena plots**, 2002–2012, including original `target_biomass_average`. The original script renames derived `plotcode` to `plot` only *after* exact original source preparation. Therefore canonical identity to verify **source-only**, not guess: biomass `plotcode` ↔ cover `Plot` ↔ functions `plot`, with original year and season carried appropriately.
- Original author `traits.st.csv` has 59 original species rows, species key `sp`, 44 further source columns (some may be traits, metadata); 2020 original derived predictor `predictors_raw.csv` has 1,619 original `plot×year×season` rows, 42 FD and 42 functional identity FI columns. Do not treat one transformed FI/FD column as an independent raw measurement.

## Author-coded transformation issues for NEW prospective time-transport, not criticism of original inference

The original authors' `main analysis.r`:
1. Replaces original cover `-9999`, `NULL` with 0, converts source ordinal cover **1→0.5 and 2→3** (author scale), converts May to spring and Aug/Sept to summer. These are **original analysis conventions**; a future source-reproduction must document them, not silently change or undo.
2. Aggregates the original multi-`subsample` `target.biomass` using a within-original-plot/year/season **median**; source file original dry mass is g m−2, not TreeDivNet Mg ha−1. Original 2004 summer may have all-zero target biomass from source limitations; do **not** treat zeros as valid ecological production or casually censor them without explicit source semantic verification.
3. The displayed main script uses `community3 <- community2[community2$target.biomass>0,]` before constructing a composition table merged with cover. **This response-dependent row selection is acceptable as a documented original authors' analytic population but would be *leakage for a newly claimed heldout-future-year test* if applied using heldout response values.** For a new predictive study, reconstruct independent composition from original cover and species traits using training-only source selection rules and never use heldout mass to select predictor availability.
4. Uses `imputePCA` on the full 59-species trait matrix, then Rao's quadratic entropy (Rao Q) as trait FD and weighted CWMs/FI, not generic two-axis Euclidean FD. PCA source imputation is performed on trait matrix, not directly on biomass response; whether it's external to time split depends on source sampling/trait dates and original fit protocol.
5. Removes original source trait columns described as **circular** (`predictors_raw <- predictors_raw[,-c(4,6,48,50)]`). A new study cannot blindly treat the precomputed 84-column FI/FD table as leakage-free. Enforce one fixed, biologically motivated target and one independent source/fold-safe predictor definition before opening new result.

## Prespecified source-only canonical key audit

- Download original MD5 files exactly from published author Figshare 12834350; use only canonical **`biomass.plotcode` ↔ `cover.Plot` ↔ `functions.plot`** and original `year`. Do not use `biomass.plot` as a standalone join. Report set intersections and key duplicates only; never emit original plot codes, species code labels or biological values.
- Qualify ≥60 unique main original Jena plotcode matches and ≥7 source calendar years (2003–2012) for raw functions and original biomass; ≥20 original trait species matched to cover columns using **only published author exact abbreviation normalization** (`Ach_mil` vs `Ach.mil`; do not fuzzy-match arbitrary names).
- Before any biomass predictions, count exact original shared **plot×year**, season code and source-year response numeric-present keys. Exclude 2002 establishment year as potential primary validation but **retain in source audit**; 2004 source handling must be documented, not selected by outcome.
- Avoid asserting 82 cover plots vs 78 main function plots are all the same experimental population; original cover and biomass may include 6 non-main reference/free-succession plots.
- Declare `KEY_GEOMETRY_PASS` only for original exact source codes, and label source 2020 author-derived predictors `NOT_OUT_OF_YEAR_FOLD_SAFE_WITHOUT_RECOMPUTATION` if source row filtering uses target biomass. This is a source-method decision, not a numerical ecological effect.

No new model, coefficient, r², predictive gain, trait K or FD relationship estimated in this gate. Historic 201-family terminal HOLD and previous tree trial statuses stay unchanged.
