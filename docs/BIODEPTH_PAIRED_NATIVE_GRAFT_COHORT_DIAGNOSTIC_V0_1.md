# BIODEPTH phylogenetic breadth — paired site/plot decomposition of the native-tip sensitivity

**Design frozen 2026-11-16 *after* prior PD/biomass outcomes were known but *before new same-102-plot outcomes*.** All results are retrospective diagnostics, not confirmatory new ecology or proof that grafted taxa cause prediction change.

## Question and known measurements

The source-verified seven-site BIODEPTH analysis (Draft PR #51) used 84 height+S3 phylogeny species on 150 original planted plots / 449 original Community plot-years. Added plant phylogenetic mean pairwise patristic distance beyond planted richness, guilds, year, mean log maximum height and log-height FD changed heldout original-field prediction by **−1.451%** (site bootstrap 95% −7.291% to +3.151%). The mandatory direct-backbone-native subset used 78 species and 102 plots / 305 original Community plot-years, with **−3.500%** (CI −6.191% to −1.074%). This is **not yet a controlled comparison** because both taxa and plots change.

The new study will *fix the exact 102 original plots, the 305 original Community plot-year outcomes and the same seven heldout fields* before comparing source-taxon definitions and observed-height covariates.

## Source / original-response firewall

- Inherit all original SHA256 validations and GIFT bibliography fingerprint from PR #51. Use only original Hector 2010 Community (never 2005 Shoots), original 2005 planted design, original GIFT `Plant_height_max` (with previously documented single Kew 0.9m `Origanum vulgare` sensitivity), and GBOTB S3 pinned tree `jinyizju/V.PhyloMaker2@7af3fb5152f691af2e4ec9d5e2e467d1b50505e9`.
- Rebuild the source-only 84-species/150-plot set and the original native-only **78-species/102-plot** nested set exactly as in the unchanged PR #51 script. The native-only site counts must be `Germany14, Ireland26, Portugal8, Sheffield18, Silwood14, Sweden14, Switzerland8`; numeric 2010 Community responses exactly **305**, distributed across all seven field sites, on the same original plot IDs/years for all comparisons. No post-outcome site or plot selection.
- Recompute the *previously published* 150-plot full S3 gain and 102-plot native-only gain to **≤1e-10 absolute** difference per site against the parent saved aggregate before opening the new previously uncomputed full-S3-on-102 gain. This compares unchanged parent model code to source-pinned original outputs; fail closed on mismatch.
- All predictors are source-only **planned** species membership, equal species weights (not contemporaneous biomass-weighted traits). GIFT max height is not actual stand height.

## Single paired diagnostic of where the shift arises

For all comparisons use seven original field-heldout folds, the identical original OLS M2 vs M3 formulas, training-only feature standardization, and the same original `Y=log1p(Hector2010 Community aboveground biomass g/m²)`; site-score `G_s=1−SSE(M3,s)/SSE(M2,s)`. Do NOT reweight seven independent sites by plot-year count.

Three *separately labelled* descriptive estimands:

**A. Same feature definition, smaller fixed source-eligible cohort (composition/precision of sample effect).**

- `G_150_full` — archived and reconstructed original 150-plot, 84-species S3 predictor population.
- `G_102_full` — *new:* exactly original 102 native-support-qualified plots **but** compute CWM, FD and PD on **all** S3-resolved original species present in those same plots, retaining the same species-height and S3 tree rules as the 150-population.
- Compare `G_102_full − G_150_full` with explicit note that training cohort size/mixtures change. This is a *sample-composition influence diagnostic*, not a randomized effect.

**B. Same plot IDs/years, different planted trait/tip coverage.**

- `G_102_native` — archived and reconstructed original 102-plot prediction using native-tip-only planted species for **all three** CWM, FD and PD predictors.
- Compare `G_102_native − G_102_full`. Same 102 plots and 305 responses, but **all three trait/phylogeny features change**, so this is **not** isolated causal effect of S3 grafting or tree distances.

**C. Same plots *and the same full-S3 CWM and FD baseline*, change PD feature alone.**

- In the same 102 source plots, keep original full-S3 CWM/FD and all M2 baseline predictors FIXED, but compute M3 with either **full-S3 species-pool PD** or **native-only-species-pool PD**. Both M3 fit training sites anew.
- Assert every heldout M2 SSE is identical to floating precision ≤1e-10. The difference in site-equal heldout gains tests a narrower change in **which species contribute to the phylogenetic breadth predictor**, not an alternative dated phylogenetic backbone. The S3 distances between shared native tips remain the same.
- Do not assert these differences identify selection, phylogenetic memory K/rho, or biological grafting effects.

Summarize seven site-level gains and equal-site means; use **10,000** paired source-site resamples (seed 20261116) for descriptive percentile intervals for all paired differences. Do not treat the resulting intervals as independent replication or infer a new prospectively supported positive effect. No additional subgroup searches, model tuning, ranking or changing the site numerator.

Optionally calculate the FD prediction effect (PD→planted-height FD) **on the same 102 original plots** using both full-S3 and native-only trait definitions; label it secondary descriptive and never use this result to choose the biomass model.

## Interpretation / stop rules

If the newly computed `G_102_full` is negative, a source-population-associated prediction penalty is already present before native-only feature restrictions. If it is positive, a part of the original native-only negative might arise from changing the observed species/trait/PD feature scope. Both are interpretations **conditional on** having fixed 102 plots; they are not caused treatment effects.

No new independent source study is created by reusing the same original BIODEPTH experiment. All original global BIEN×sPlotOpen 201-system, high-density BIODEPTH 6-site, and NEON AUTH gates remain HOLD.

Persist machine-readable aggregate-only source results and keep PR Draft/unmerged; never commit original biomass rows, species-level GIFT values or temporary S3 distance matrices.
