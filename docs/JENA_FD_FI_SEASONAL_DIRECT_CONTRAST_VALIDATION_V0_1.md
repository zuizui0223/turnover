# Jena direct-contrast validation v0.1

Date: 2026-11-14. Retrospective validation of already-opened results, not a new preregistered discovery. Original results, four traits, model forms and temporal split stay unchanged.

## Goal
Determine whether the earlier descriptions 'functional composition is more useful than FD' and 'spring-only effect' are statistically supported by DIRECT contrasts, not by comparing separate p-values or point estimates.

## Reproduction
Retrieve exact public PANGAEA 923591 predictors and biomass ZIPs and original sowing metadata using recorded SHA256. Independently reconstruct the 78-plot / 1,541-cell panel (774 training 2003–07; 767 test 2008–12). Require all four archived SSEs and gains to agree to numerical tolerance before calculating contrasts. Retrieve exact PANGAEA 846317 2003 data for 82 paired plot means (May/August).

## Fixed contrasts
1. Existing holdout predictions: paired plot-ID bootstrap, 2,000 draws, seed 20261114. For each SAME resample compute FD, FI and combined gains vs M0; FI-minus-FD gain in percentage points; and conditional FD gain beyond FI. Preserve all test-year/season rows for a sampled plot together. Report percentile intervals, labelled conditional on the fitted training models.
2. Sensitivity: bootstrap plot IDs within original field blocks, refit all four unchanged models on sampled early-year observations and evaluate on corresponding late-year observations, 2,000 draws, seed 20261115. Use the same sampled multiplicities in training and test because the panel contains the same plots. This measures sampling uncertainty in this repeated-plot temporal task, not unseen-site generalization.
3. Seasonal effect: regress paired difference log1p(August dry mass)-log1p(May dry mass) on intercept + log2(sown richness) + planned FG richness + original block. The FG coefficient is exactly August-minus-May conditional FG slopes. Report HC3 interval/p and block-stratified plot bootstrap interval (2,000 draws, seed 20261116). Do not infer season contrast from one p below .05 and another above .05.

## Interpretation
No trait search, threshold relaxation, new holdout split, changed predictor weights or imputation. A CI containing zero means no clear superiority or season difference under the checked model, not equivalence or zero ecological effect. Scores are log-scale out-of-year SSE; same plots and same experiment; source-derived imputed traits and concurrent vegetation cover remain limitations. NEON access remains a separate external prerequisite and no credentials will be inspected or exported.

## Execution and verification
Run local source-hash checks and unit tests for direct gain algebra, identity contrasts, paired resampling and train-only scaling. Independently reproduce archived effects. Save executable analysis, tests, aggregate outputs and source manifest. Do not redistribute original measurements or modify main. This validation does not justify causal effects of phylogenetic memory on FD or biomass.
