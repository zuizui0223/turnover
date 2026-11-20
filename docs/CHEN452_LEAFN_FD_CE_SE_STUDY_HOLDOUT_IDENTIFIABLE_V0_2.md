# Chen452 v0.2 structural identifiability amendment (before CE/SE predictive results)

**FROZEN 2026-11-20 after a predictor-only source check, and before opening ANY new held-out CE/SE prediction.** This is a separately identifiable estimator in the same branch, not a retroactive PASS or silent substitution of the original v0.1 model. The original [v0.1](CHEN452_LEAFN_FD_CE_SE_STUDY_HOLDOUT_FROZEN_V0_1.md) remains `SOURCE_TRAINING_FOLD_RANK_HOLD`, no outcomes fitted.

## Empirical source design diagnosis (response/associations unopened)

[Source rank-only Actions #44760950900](https://github.com/zuizui0223/turnover/actions/runs/44760950900) confirmed both original author data, original unmodified source IDs and original `CE+SE=DY` identity:
- Leaf N: 1,709 complete-case mixtures in **116 original StudyID groups**; **116/116** source-held-out folds have original v0.1 M1 rank exactly **one fewer** than the number of columns. Redundancy is always a **PlantType dummy**.
- SLA: 2,031 complete-case mixtures in **127 original StudyID groups**; **127/127** held-out source design matrices deficient by exactly one column, again a PlantType dummy.
- 116/127 are ***original StudyID levels***, not 116/127 independently published DOIs; multiple study labels can share literature origin. No original study names, original response magnitudes, source traits or FD/CE associations were exported from the rank-only CI.
- All original source prespecified **>=300 plots, >=30 original StudyID groups and >=30 groups with >=5 qualifying plots** were checked BEFORE this rank issue was seen. No admission threshold changed.

The original M0 entered both `Eco1` and `PlantType`. The categorical dummy for PlantType is a linear combination of the Eco1 columns in all original eligible training samples (full rank loss 1). Its separate coefficient is **not identifiable**, nor can it establish an independent causal plant-type effect. Eliminating that redundant categorical term is an **outcome-blind design choice**, not selection of favorable predictors or response directions.

## New v0.2 fixed estimator

**Keep exactly the v0.1 complete-case cohort, endpoints, outcome definitions, FD, folds, weights, scaling, bootstrap and all numeric stop gates.** No new source row is admitted, no criterion relaxed. Source `PlantType` must still be **present/nonmissing** for exactly the same complete-case support, but it is excluded from M0/M1 model columns because it duplicates the finer Eco1 information.

v0.2 base model M0 = intercept + `log2(SR)` + `log1p(StandAge_year)` + source-original `PD` + original planted-trait `CWM` + `MAT` + `AI` + `FD_WithNFix` + ecosystem **Eco1** categorical only. M1=M0+the single predeclared planted-species `RaoQLN` leaf-N FD axis. SLA sensitivity separately substitutes original `RaoQSLA` and `CWMSLA`. Original `RaoQ*_harvest` and `CWM*_harvest` are excluded to prevent post-treatment leakage. Original `FD_biomass` and modified SE are excluded from predictor set (mathematical response coupling and different original estimator).

Continue **unpenalized weighted least squares**, one original study equals one total training weight, full-rank and condition number <=1e8 required for *every* training fold, original StudyID held out in entirety, training-only numeric scaling, same plots/studies/folds for CE and SE, and original fixed uncertainty: 2,000 study-bootstrap draws of held-out squared errors (seed 20261120). Main predictive contrast is still `gain_CE−gain_SE`, with CE, SE, CE−SE reported even when negative or uncertain.

Report v0.1 HOLD and v0.2 estimates separately; do not infer a random intervention on FD, a test of phylogenetic K→FD causal mediation, or a new independent biological replication of the Nature 2025 paper. Original article chose an outcome-residual threshold to discard 82 rows, so that selection uncertainty remains even if the new study-heldout gain is positive.

**STOP:** If any v0.2 study-fold remains rank deficient or source support fails, record SOURCE/DESIGN HOLD and do not select an alternative predictor removal, transform, regularization strength or endpoint after opening prediction results.
