# BioCON E141 2021: is candidate SLA-FD redundant with richness, CWM and ring?

2026-11-24. **Retrospective source-predictor-only** audit, independently performed **after** learning that PR #77's original August2021 heldout gains were B −3.89% and signed plot-total NDE −9.09%. No original numeric biomass, signed NDE or CE/SE values were opened in this new diagnostic, no biological model or outcome fitted, and no source cohort, original target, predictor, threshold or fold changed.

## Original source, exact support and design

Rebuilt the same original author Figshare v3 MD5-pinned 46 sown composition plots (36 richness4; 10 richness9), original 14 E141 native-source-candidate treated log-SLA values with the two documented E120/Big Bio-substituted taxa excluded, and same M0/M1 columns and original 6 CO2 rings. Source ring plot counts were **4, 7, 8, 9, 9, 9**, not balanced, and original ring assignments are randomization units only for CO2.

| Predictor-only diagnostic | Observed |
|---|---:|
| Original FD variance explained by richness, N, ring FEs, CWM (ring equal weighting) | **24.21%** |
| Remaining FD source variance | **75.79%** |
| Source FD variance inflation factor (VIF) | **1.32** |
| Source training matrix M0 weighted condition (46 holdout folds, median/max) | **7.97 / 8.16** |
| Source training matrix M1 (+FD) weighted condition (46 folds, median/max) | **8.03 / 8.31** |
| Median / max increase in source heldout predictor leverage from adding FD | **1.08× / 2.16×** |
| Original heldout folds with extra FD leverage above 1.5× / 2× | **4/46 / 1/46** |

FD has measurable candidate dissimilarity variation within original planted richness4 (10th/median/90th percentiles **0.130/0.272/0.306**) and richness9 (**0.207/0.301/0.325**). This is the original one-axis log-SLA Rao-like equal-species source index, not a full community multidimensional FD.

## Inference from this diagnostics

**A simple "FD was almost the same predictor as species richness or average SLA" explanation for the PR #77 failed predictive increment is not supported.** VIF 1.32 and full-fold condition numbers near 8 indicate that the numeric original FD predictor retained substantial conditional variation in the fixed 46-plot source cohort. Increasing the model by one parameter did raise out-of-composition predictive leverage, but only 1 of 46 original folds had a more-than-twofold relative increase.

This does NOT establish FD's biological irrelevance; non-significant and negative heldout SSE gains could reflect restricted study size, residual selection/environment noise, cohort restriction and incomplete trait dimensions, even when FD's linear predictor is not redundant. A within-one-study 46-plot analysis cannot identify a universal negative causal FD effect, and the direct original EDI 538 SLA measurement-year access remains **HTTP 403 HOLD**.

**Boundaries kept:** Parent original PR #77 B/NDE gains and CIs remain unchanged, prior strict 24-year EDI trait-year source gate and the original 21-claim registry unchanged, 2024 source Big Bio taxon exclusions unchanged. No new ecological p-values, alternative FD metrics, predictor shopping or independent experiment counts were introduced.

Run: [source-only actual original-data CI #45331157499](https://github.com/zuizui0223/turnover/actions/runs/45331157499). Results: [original nonraw geometry JSON](../results/biocon_e141_2021_secondary_SLA_predictor_identifiability_v0_1.json).
