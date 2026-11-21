# Jena TBE 2012 original monoculture-based Loreau–Hector partition: separate retrospective mechanistic test
**Frozen 2026-11-21 BEFORE computing original source mixture NDE / complementarity / selection endpoints.** Earlier [descriptive 84-plot high-FD vs total biomass PR #73](https://github.com/zuizui0223/turnover/pull/73) already found log1p contrast +6.22% CI [−15.72,+32.83], spanning zero; because this direction was visible, the current mechanistic extension is **explicitly outcome-aware exploratory**, not independent prospective validation. The motivation—mechanistic CE versus SE partition—was set earlier by the user and published Wagg 2017 study, not chosen from favorable per-pool FD models.

## PANGAEA original source and exact same-population eligibility
Wagg et al 2017 original [PANGAEA 10.1594/PANGAEA.876725](https://doi.org/10.1594/PANGAEA.876725), SHA256 **458f61307df217d285c972f894ca5cf23709c3524dc6e13bb4d9dd3c26c2ab56**, CC BY 3.0: 138 original planted plots × original 2012 May/Aug harvests, up to 20 sown-species annual harvest masses; source includes both planted **24 monoculture plots across three different pools** and 114 planted multi-species plots. The original designed richness and species roster are recovered from original blanks (unsown) versus numeric zero (sown but zero biomass), original missing sentinel -9999 is NEVER zero. The original *Block* value is one constant site code; 3 physically randomized blocks cannot be certified because original JEXIS source download #739 timed out. Exactly balanced source Plot A/B/C classes are descriptive spatial-prefix proxies, not proven treatment randomization.

Source-only gate before opening CE/SE effects:
1. Exact original source SHA, 138 plots, two 2012 harvest months (May/Aug) per plot, within-plot planting metadata identical, 20 source species columns. No observed source missing species harvest rows, no unverified plot/species join.
2. Exactly **24 original monoculture Plot IDs**, 8 per source pool, and one original same-pool, same-2012-year monoculture per each planted mixture species. If a species×pool has zero or missing annual monoculture dry-mass yield, or if source has duplicate monoculture rows at this grain, **SOURCE_MONOCULTURE_EXPECTATION_HOLD**, not pseudo-count or borrowing from other pools/years. A species appearing in two pools must use its **own pool-specific** original monoculture.
3. Original prespecified **84 plots in 6 pool×planted-richness eligible strata** with ≥4 high wFDc 3/4 and ≥4 low wFDc 1/2 per stratum, no new plot exclusion after outcome. Exactly both May/Aug measurements for every target and every same-pool mono. No mixing original 2002 Jena Main records or NDE computed from external database.
4. Original sown species were initially in equal proportions (author Ebeling 2014/Wagg 2017 design). For planted mixture with original source richness **R** and original same-pool species monoculture annual yields **M_i**, source annual species yield **Y_i**:
   - `expected_monoculture_yield = Σ_i (M_i/R)`
   - `observed_mixture_yield = Σ_i Y_i`
   - `NDE = Σ_i Y_i − Σ_i M_i/R` (original g dry mass/m², signed)
   - `ΔRY_i = Y_i/M_i − 1/R`
   - **Loreau–Hector CE** = `R × mean(ΔRY_i) × mean(M_i)`
   - **Loreau–Hector SE** = `R × cov_population(ΔRY_i,M_i)` (divide covariance by R, not R−1)
   - Identity: **CE+SE=NDE** within abs tolerance **1e−8×max(1,|NDE|)** per source plot, else fail before effect estimates. Negative NDE, CE and SE remain unchanged signed original g/m². Do NOT logarithmize, offset, or discard negative components.
5. Original baseline treatment wFDc≤2 vs high≥3 must be source-design-only; no source-mono expected yields used to choose plot subset or species. Original author Wagg already reported trait differences in complementarity and competitive disparity, so no "discovery of the link" claims.

## Fixed descriptive mechanism comparison (only after source qualification)
Exactly **same 84 mixture plots, same 6 pool×sown-richness strata and 3 source Plot-prefix proxies** used in PR #73. Exposures fixed high/low assigned FD, not realized FD after growth.

- For y in (**NDE, CE, SE**) in this order, WLS on raw signed original g dry mass/m²:
  `y = intercept + C(source pool×sown richness) + C(source Plot A/B/C prefix) + beta_y * HighFD`, with equal total weight per original pool×richness stratum, no interactions, same plots.
- Main mechanistic diagnostic: `beta_CE − beta_SE`, and verify `beta_NDE≈beta_CE+beta_SE` under identical full-rank design. Do not choose the component with positive point estimates for a new primary hypothesis.
- 2,000 plot-stratified paired bootstrap resamples (seed 20261121), draw **identical plots for all three response partitions**, stratified by original pool×richness×high/low source treatment. Refit the same WLS per resample; require ≥90% full-rank refits. Report **all** three βs and CIs and the paired CE-SE contrast CI even if negative or spanning zero. No new p-values or arbitrary one-sided posthoc significance.
- Optional raw original total biomass high-low coefficient from PR #73 is a distinct response; no direct equality with NDE needed because the expected single-species biomass can vary across FD treatment groups due to species identities.

**No randomization/causal mediation claim.** Original species combinations were selected to span dissimilarity. HighFD is confounded with which species were planted; even within richness/pool with source Plot prefix adjustment, this is a treatment **recipe association**, not a pure causal effect of scalar FD. Original mono baseline might have only one mono plot/species×pool, so CI from plot-only resamples does not propagate independent uncertainty in monoculture yield or spatial-pool design. Original TBE is one site, not three independent field studies, and this is not a cross-site or phylogenetic memory linkage. Negative/uncertain results retained without further trait/season/pool searches.

## Provenance and strict output firewall
Release to GitHub only: original metadata/hashes, source counts, aggregate CE/SE/NDE WLS coefficients, 2,000 stratified plot bootstrap uncertainty and limitations. NEVER upload original species/plot IDs, original planted mixture species yields or single-species mono yields. Preserve all original PANGAEA author credit and CC BY. No redefinition of CE/SE after effects opened and no independent confirmation of Wagg's 2017 published mechanism.
