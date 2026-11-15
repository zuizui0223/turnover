# Jena 2003 planned guild identity vs guild count: bounded post-result extension v0.1

Frozen analytical choices **2026-11-15**, after the original May and Cedar Creek E120 outcomes were known but before running this particular Jena guild-identity model. Therefore **all results are exploratory/post-selection**; this is not a new independent confirmatory study. This is an internal test of whether Cedar Creek's 1998 guild identity association generalizes even qualitatively to original Jena treatments.

## Original source identity
- Original PANGAEA [846317](https://doi.org/10.1594/PANGAEA.846317) 2003 plot-level aboveground dry mass; exact source SHA256 `70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079`. Response: source `Repl=mean` **May 2003 sown plant biomass**, `log1p(g/m²)`; August is a prespecified repeated-campaign sensitivity, not independent experiment.
- [Original 82-plot Jena sowing design](https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt) SHA256 `7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70`.
- Preserved original 62-plot support population with sown richness in **{2,4,8,16}**, whose richness strata each contain at least two planned FG-count levels. No exclusion depends on outcome.
- Original groups `PresenceGrasses`, `PresenceSmallHerbs`, `PresenceTallHerbs`, `PresenceLegumes`, each 0/1. `FG4 = sum(groups)`. Within same richness & block & FG4, there are precisely **8 exchangeable two-plot guild-assignment pairs (16 plots)**, **all** in 2-species treatments, while no same-stratum swaps exist for richness 4/8/16. This is the principal design-based evidence bottleneck.

## Primary exploratory contrast
- **Equal-coefficient/count model** `Y ~ C(exact_sown_richness) + C(original_block) + FG4` on same **62 May** means.
- **Guild-identity model** `Y ~ C(exact_sown_richness) + C(original_block) + I(Grasses)+I(SmallHerbs)+I(TallHerbs)+I(Legumes)`. The number is exactly the sum of the identities; **never** enter `FG4` plus all four indicators.
- HC3 robust Wald 3-df test of `beta_G=beta_S=beta_T=beta_L` (not 4 individual tests). Report adjusted beta and 95% CI for each group **descriptively**, and lag of legumes versus the mean of the three other group coefficients as a prespecified shared category with Cedar Creek. Since original sown species differ, individual coefficients do **not** isolate biological guild mechanisms.
- Treatment-space saturation sensitivity: replace additive `C(richness)+C(block)` with a distinct intercept for **each block×richness** 16 cells, then compare count versus 4 indicators with 3-df HC3 test. All design columns must be full-rank.
- Same 62 plots in August (sown mass) and within-plot `log1p(Aug)-log1p(May)` as descriptive season-change models; do not infer a seasonal guild interaction by comparing separate nominal p values.

## Design-based and predictive stress tests
- Fixed-label *conditional reference test* enumerates **all 2^8 = 256 swaps** of four-guild identity vectors within the **8 two-plot pairs** that match exact richness, original block and original FG count. The statistic is training-sample SSE improvement of identity-model over count-model with same response and key. This is **not** an exact causal test across the 62 study plots or a proof that guild types are exchangeable because species identities differ and only the 2-species strata are permuted. For each swap the count design is unchanged. Report `p = #{D_perm>=D_observed}/256` and fraction of plot assignments that could actually vary.
- Primary external-block stress test: leave one of the **four original Jena experimental blocks** out, predict its 62-pool plots from the other 3. No block fixed effects in training models (held block has no estimated level). Include exact richness dummies. Compare `SSE(identity)` versus `SSE(count)` and `SSE(baseline exact richness)`, report the relative prediction error reductions. Do not treat four blocks as large-area spatial replication.
- Bootstrap 2000 times whole original plot IDs, stratified by original blocks, **refitting both count and identity models** for each sample and calculating in-sample guild contrast and heldout same-block SSE only if all models full rank. Bootstrap is explicitly retrospective and within one experimental site. Report invalid-rank replicates and CIs or HOLD when validity below 95%. No post-outcome feature choices.

## Claims that remain prohibited
- Jena 2003 May guild *count* loses nominal significance under exact-richness controls (82 plots p=0.151; 62 plots p=0.168; strict block×richness p=0.293). That is unaffected.
- Cedar Creek E120 1998 independent guild-count beta +0.083 p=0.544 and robust guild-identity heterogeneity p=7.63e-7 already documented; its guild types **C3/C4 grasses, nonlegume forbs, legumes** are not identical to Jena's **grasses, small/tall herbs, legumes**. Only legumes are a directly named comparable guild; even this does not mean same species.
- The sole common E120/Jena analytic dimension is **coarse guild composition versus guild count**, not standardized functional traits, functional diversity Rao Q, phylogenetic memory rho, plant biomass production globally, or causal nitrogen fixation.
- Neither the 201-system BIEN pre-outcome HOLD nor the NEON 2026 authenticated source hold is changed.
