# BIODEPTH original planted traits × GBOTB S3: matched source-only coverage

2026-11-16: **frozen before matching outcomes**, after upstream 103-taxon tree source gate SUCCESS (98/103 mapped, 80 native, 18 bound, 18 families, 206 planted plots with ≥3 tree taxa). Earlier GIFT-height/biomass findings were already known, so the future association study is post-result exploratory.

## Allowed original sources

- The same original Hector 2010 5,802 species×plot×year rows and 186 ecotype codes, exact SHA256 checked.
- GIFT v3.1 `Plant_height_max` original 88 height-bearing source-qualified taxa, the identical original API reference content fingerprint and species-trait tuple fingerprint as archived in the prior BIODEPTH source study. The source-only join may access height values **only** to derive original source coverage and predictor rank/determinism, NOT biomass.
- The prior original `GBOTB.extended.TPL` tree from V.PhyloMaker2 commit `7af3fb5152f691af2e4ec9d5e2e467d1b50505e9`, S3, unique exact original genus→family, no synonym rescue.
- Original planted roster (not realized same-year harvested species) for exactly the original previously qualified **174 height-bearing plots** from **seven original source sites**. The old original Kew botanical replacement of `Origanum vulgare` GIFT 13m by 0.9m will be applied in any subsequent numerical FD model and never changed during the current source-only support analysis.

## Fixed matched source-only qualification

1. ≥65 of 88 original height-bearing species are present on the source-pinned S3 tree; ≥40 of these are native direct GBOTB tips; at least eight different botanical families have at least one height-bearing S3 species.
2. ≥120 of the **historical source-qualified 174** plots have ≥3 jointly GIFT-height + S3-resolved species, representing ≥80% of their original *sown* taxa. At least five original study sites must each contribute ≥8 matched original plots.
3. At least 10 different source-derived original-plot mean pairwise phylogenetic distance (MPD_PD) values across matched plots (rounded to 1e-8), to avoid a constant predictor. Distances are extracted from the dated S3 tree with `ape::cophenetic.phylo`, not hand-assigned taxonomy ranks. Verify symmetric, finite and nonnegative pairwise distances and zero diagonal.
4. No biomass, original Community/Shoots endpoint, site-year response, site-holdout prediction score, original FD×biomass effect or direct K/rho is opened in this gate. Report PASS/HOLD without threshold changes and archive only nonraw aggregate source summary; S3 status label/distance CSVs are temporary runner inputs, never committed.

The previous full 174-plot FD result is not directly comparable to a possible smaller jointly eligible plot cohort. If PASS, **first freeze a new same-plot baseline and PD increment models and their held-out-site scoring**, then open original 2010 Community response only on the fixed matched cohort. If HOLD, do not fit the new biological effect.

## Biological estimands deliberately separated

- `MPD_PD`: mean pairwise patristic distance among planted, jointly GIFT-height and S3-covered species (each species receives equal planned weight); this is community phylogenetic *breadth*, not a family trait-specific Blomberg K.
- `FD_height`: mean pairwise absolute distance in *log* source plant maximal height, computed on the exact same plant tips when a study is later authorized; not multivariate FD and not actual plot-height.
- `CWM_height`: equal-planted-species mean log plant max height (not same-year mass weighted).
- `mass`: original Hector 2010 Community aboveground standing biomass log1p (not NPP), future endpoint only. Never use same-year species mass in predictors.

**Hard boundary:** The global original BIEN/sPlotOpen/GIFT 201-system source gate, original BIODEPTH 6-site exact-richness gate, and NEON authenticated dataset all remain HOLD. This new gate cannot reverse those decisions.
