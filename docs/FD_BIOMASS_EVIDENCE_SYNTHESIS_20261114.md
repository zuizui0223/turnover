# Current evidence: functional group richness, trait FD and harvested biomass

Checkpoint: 2026-11-14, updated after direct-contrast validation. All original BIEN rho, AusTraits organ-K and archived Jena model outputs remain unchanged. This synthesis corrects interpretation, not the original estimands.

## Current conclusion
A positive association between planned functional-group richness and May 2003 biomass is retained. However, neither a genuine May–August difference in that association nor superiority of functional composition over FD has been established by direct contrasts. The small FD point prediction gain is not an equivalence test or evidence that FD has no ecological effect.

## 1. Original 2003 directly harvested biomass: what remains positive
Source: Buchmann & Temperton (2015), PANGAEA 10.1594/PANGAEA.846317. Eighty-two original plot means per May/August campaign; original sowing metadata independently matched.

- May log1p(sown aboveground dry biomass g/m²), adjusted for log2(sown richness) and block: planned functional-group-richness beta **+0.16789**, HC3 two-sided p **0.0439**, block-stratified plot bootstrap CI95 **+0.0219 to +0.3521**.
- August with the same covariates: beta **+0.00168**, p **0.9829**.
- Removing four 60-species plots preserves the May direction. Adding legume presence increases uncertainty; it does not demonstrate mediation by legumes.
- These are separate conditional estimates. A significant May coefficient and nonsignificant August coefficient do not themselves establish seasonal modification.

Original result: [group_biomass_effect_v0_1.json](../results/biomass_jena_2003_source_v0_1/group_biomass_effect_v0_1.json).

## 2. New direct season contrast: season difference is unresolved
Using the **same 82 paired plot means**, regress log1p(August biomass) minus log1p(May biomass) on intercept, log2(sown richness), planned FG richness and original block. This directly estimates the difference between the two original conditional slopes, allowing all nuisance slopes to differ between seasons.

- August-minus-May FG slope: **−0.16621**.
- HC3 SE **0.09744**, two-sided p **0.08806**, CI95 **−0.35720 to +0.02478**.
- Two thousand block-stratified paired-plot bootstrap draws: CI95 **−0.36704 to +0.00949**.

Both intervals span zero. Replace earlier language such as **“spring-only effect”, “the effect disappears in summer”, or established seasonal dependence** with: **“May supports a positive conditional association; August does not individually establish it, but their difference is not clearly distinguished from zero.”** The direction suggests possible attenuation but does not establish it. The original official means include subsample 4, which the source identifies as more carefully weeded; that original estimand is retained, not silently altered.

## 3. Longitudinal FD versus functional composition: direct uncertainty
Source: van der Plas et al. (2024), PANGAEA 10.1594/PANGAEA.923591. The source was used in prior published analyses; this is not independent biological discovery.

Seventy-eight plots, 1,541 plot×year×season cells. Train 2003–2007 (774 cells), evaluate 2008–2012 (767 cells); the same 78 plots appear in both. Four unchanged traits: height, SLA, leaf nitrogen and seed weight. Original imputed, concurrent-cover-based Rao FD and FI/CWM predictors. Baseline is original sown richness, planned functional-group richness, season, linear year and block. Outcome is log1p of median processed source target.biomass; physical units in the longitudinal processed file remain unaudited.

Independent reconstruction reproduced all four archived SSEs and the earlier conditional FD bootstrap interval to numerical tolerance. The earlier fixed-model paired uncertainty audit is also reproduced, not treated as a new finding.

### Refit sensitivity: same sampled plot multiplicities in training and test
Two thousand within-block plot resamples, refitting each unchanged full-rank OLS model on the sampled early-year records and evaluating corresponding later-year records. All draws valid. The following are exploratory marginal percentile intervals, conditional on the observed years and this one site; not simultaneous guarantees or uncertainty across independent sites/years.

| Contrast | Point estimate | Refit 95% interval |
|---|---:|---:|
| FD vs baseline: SSE reduction | +0.46% | −2.61% to +3.75% |
| FI/CWM vs baseline: SSE reduction | +2.98% | −1.33% to +9.57% |
| FD + FI vs baseline: SSE reduction | +2.86% | −2.97% to +10.69% |
| FI minus FD, common baseline | +2.51 percentage points | −2.33 to +8.87 percentage points |
| Add FD after FI: SSE reduction vs FI | −0.12% | −3.05% to +2.87% |

All span zero. FI has a larger point gain but is **not demonstrably superior to FD** here. The four-trait FD gain is small at the point estimate, but the confidence intervals do not prove zero effect or practical equivalence. Neither branch supports “composition matters but diversity does not.”

The previously archived fixed-fitted-model intervals remain valid for their narrower conditional target: FI gain −2.94% to +8.34%; FI-minus-FD −3.72 to +8.20 percentage points. Refit intervals need not be uniformly wider because this sensitivity also stratifies on original block and preserves training/test plot dependence.

## Evidence, execution and reproducibility
- [Direct validation plan](JENA_FD_FI_SEASONAL_DIRECT_CONTRAST_VALIDATION_V0_1.md).
- [New complete direct-contrast result](../results/biomass_jena_2003_source_v0_1/direct_contrast_validation_v0_1.json).
- [Earlier fixed-model uncertainty](../results/biomass_jena_2003_source_v0_1/fd_fi_paired_uncertainty_v1.json).
- [Analysis code](../scripts/analysis/validate_jena_direct_contrasts_v0_1.py) and [8 unit tests](../scripts/qa/test_jena_direct_contrasts_v0_1.py).
- Verified Actions [43600592223](https://github.com/zuizui0223/turnover/actions/runs/43600592223); artifact 14116213160; downloaded ZIP SHA256 d69c1ba5acf9d73dbfc16e29e0c78634d8f3a1970a289fc861bafed93007de70 matched the Actions digest.

## Scope and remaining boundaries
The positive May association is **planned functional-group count**, not continuous FD, a hypervolume effect or an effect of evolutionary trait memory. The long-term comparison is concurrent explanation transported across dates within the same plots, not an ex-ante forecast or spatial validation. Traits were imputed in the original source. All direct contrasts are post-outcome validation, not fresh preregistered confirmation.

The original global BIEN/sPlotOpen source programme and NEON authentication boundary are not changed by this validation. NEON exact plot/day co-location remains unverified; no token was accessed or exported here. The minimal manual credential workflow is in separate PR #42 and must be on the default branch before UI dispatch; this validation does not merge it or change credentials.
