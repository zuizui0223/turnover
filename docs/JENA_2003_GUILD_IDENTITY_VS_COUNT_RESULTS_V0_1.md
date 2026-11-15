# Jena 2003 guild composition versus guild number: source-verified post-result comparison

Date 2026-11-15. **This is a retrospective exploratory stress test selected after Cedar Creek E120's guild-identity signal was known.** It cannot be used as a new prospectively chosen replication study.

## Original source and source design
- Original Jena 2003 directly harvested **sown plant** standing aboveground dry biomass, May/August, PANGAEA [846317](https://doi.org/10.1594/PANGAEA.846317), SHA256 `70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079`. Original [sowing table](https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt), SHA256 `7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70`.
- Same **62 plots** with exact planted richness 2/4/8/16 where ≥2 guild counts are present within each richness. Four original Jena groups: grasses, small herbs, tall herbs, legumes.
- Source metadata alone show that only **8 two-plot pairs** (all from the 2-species group) have differing group identities conditional on **exact richness × original field block × number of planted guilds**. Other 46/62 have no such swap within their source stratum.
- Before this exploratory outcome opening the specific source subgroup and tests were documented in `docs/JENA_2003_GUILD_IDENTITY_VS_COUNT_PREOUTCOME_ANALYSIS_V0_1.md` (despite the filename, no claim of preregistration: earlier Jena and Cedar outcome results were already opened).

## Same May 62-plot cohort: group count versus four separate guild indicators

| Adjustment/model | Experimental unit | Main number |
|---|---|---|
| `log1p(May biomass) ~ C(sown richness)+C(block)+FG4` | 62 plots | FG β **+0.12867**, HC3 p **0.16763** |
| `~ C(sown richness)+C(block)+Grasses+SmallHerbs+TallHerbs+Legumes` | 62 plots | Guild-equal-coefficients HC3 Wald (3 df) **χ²=3.5904, p=0.30923** |
| 16-cell `C(sown richness)×C(block)` nuisance + individual guilds | 62 plots | Guild-equal-coefficients HC3 p **0.64068** |
| All (2^8=256) possible guild-pair swaps conditional on exact richness, block and FG count | Only 16 plots are label-exchangeable | SSE-improvement upper-tail p **0.50000** |
| Leave one original Jena block out (4 folds), count versus 4 guild identities | 62 predictions once each | Guild identity model has **−0.8269%** additional SSE gain (SSE 55.592 vs count 55.136) |
| 2,000 block-stratified plot bootstrap *retraining* draws (all full rank) | Same original four test blocks | Guild vs count predictive gain 95% interval **−59.42% to +8.76%** |

**Do not conflate** the 62-plot regression Wald test with the 16-plot limited design-based randomization support. This enumeration is NOT a proof of exact random assignment of guild identities across the full experiment, because actual sown species composition differs.

Jena May legume-identity coefficient minus average of other three group coefficients **−0.0420**, HC3 95% CI **−0.6670 to +0.5829**, p **0.895**; bootstrap 95% CI **−0.7102 to +0.4188**. This does not identify or rule out a legume ecological mechanism.

## Repeated-campaign and source scope
- August guild-equal-coefficients HC3 p **0.2240**, strict 16-cell block×richness p **0.4365**, and 8-pair conditioned label swap p **0.1094** (exploratory).
- Direct paired August−May log-biomass regression guild-equal-coefficients Wald p **0.5185**. Separate seasonal p values cannot establish a significant seasonal interaction.
- May out-of-block CV using identities degrades prediction slightly, but uncertainty is substantial because one block dominates squared errors and only four independent field blocks exist. The effect is not proven absent or equivalent.

## Comparison with independently sourced Cedar Creek E120 1998
- Cedar E120 (ESA TIEE 2004 secondary original treatment data) n=94 richness 2/4/8, Woody sowing adjusted: four group **count** β +0.0830, HC3 p **0.5444**, whereas four original guild coefficients differ (HC3 Wald p **7.63×10⁻⁷**, fieldrow-adjusted p **2.58×10⁻⁵**, conditional guild-vector shuffle p **0.0003**). Its holdout-field-zone point prediction advantage remains uncertain under retraining.
- **Cedar groups:** C3 grass, C4 grass, nonlegume forbs, legumes (Woody separately). **Jena groups:** grasses, *small* herbs, *tall* herbs, legumes. The named 'legumes' concept overlaps, **but their species sets, initial richness, biomass response, field geography and detection geometry do not match**.
- Thus the positive guild-identity signal in one experiment **was not reproduced in Jena's available design**, while the simple count's clear positive influence is unsupported in either within-richness analysis. This variation might be due to community composition, contrast distribution, source-specific treatments or low Jena power; two experiments cannot distinguish these explanations.
- Do not pool the source-specific log coefficients in a quantitative two-study meta-analysis without response standardization, cohort/unit reconciliation and identical design support.

## Reproduction and nonclaims
Local independently source-parsed `pandas/statsmodels.formula.api` analysis reproduced the original 62-plot FG count β, all May/Aug guild Wald p, 16-cell strict p, 256-pair conditional reference p and leave-block-out SSE to numerical precision. The separate source-reader implementation passed **8** local tests, with **2,000/2,000** block-stratified bootstrap retrains full-rank. A self-contained source files + code + tests + JSON archive is attached to the conversation; verified nonraw result is in `results/biomass_jena_2003_source_v0_1/guild_identity_vs_count_v0_1.json`.

No causal nitrogen fixation, generalized FD–biomass, phenotype-evolutionary-memory rho or global family×trait association was estimated. Frozen original BIEN 201-system and sPlotOpen×GIFT primary source-design HOLD and NEON authenticated-release gate remain unchanged. PR #40 stays Draft and unmerged.
