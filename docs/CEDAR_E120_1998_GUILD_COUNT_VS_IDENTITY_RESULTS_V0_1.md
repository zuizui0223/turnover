# Cedar Creek E120: planted guild count versus guild identity and harvested aboveground biomass

Date: 2026-11-15. **Post-Jena source selection; exploratory independent experiment reanalysis, not a globally representative meta-analysis.** Source-only gate is documented in `results/cedar_e120_source_v0_1/teaching_workbook_source_gate_v0_1.json`. Original EDI PASTA package API returned HTTP 403; source actually analyzed is the ESA Teaching Issues and Experiments in Ecology *2004 student Bonus Data*, not a newly obtained authoritative EDI long-term table.

## Original source and population
- [Cedar Creek E120 original experiment](https://cedarcreek.umn.edu/research/experiments/e120) independently planted in 1994. ESA [teaching XLS data](https://www.esa.org/tiee/vol/v2/issues/data_sets/cedar_creek/data.html): 168 unique plots; three measured years (1996–1998); plant aboveground biomass `AbvBio`, described as g/m². Original byte SHA256 `a86755544d75fabb85f4979303efcada96683ae60c0bc3bdb60c5d4c739d7476`; exact CSV SHA256 `c40ee678ca80a6bb73680115205b13eef20a9c5fd502284be38482a332a43db1`.
- 77/168 have original Woody guild treatment. Only 91 plots are Woody-negative; the 55 Woody-negative plots with 2/4/8 species fall short of the earlier source gate. The original **≥4-year** primary source requirement remains **HOLD**. A **separate 1998 single-year exploratory model** was written after discovering source design and *before fitting the Cedar biomass associations*. It used all 94 2/4/8-species plots, including 39 Woody-positive treated plots.
- `FG4 = I(C3 grasses)+I(C4 grasses)+I(non-legume forbs)+I(legumes)`; `Woody` included separately as an original sowing treatment covariate. This guild grouping is **different from Jena** (grasses, small herbs, tall herbs, legumes).

## Results: richness- and Woody-adjusted count has no clear positive association
- Original 1998 model: `log1p(AbvBio1998 g/m²) ~ C(NumSp) + Woody + FG4`, **n=94**.
- FG4 coefficient **+0.083014**, HC3 95% CI **−0.185418 to +0.351446**, two-sided HC3 **p=0.544428**.
- Fixed 9,999 permutations within original **NumSp×Woody** conditions: **p=0.4475**. Four thousand plot bootstrap draws stratified by four spatial grid zones: coefficient percentile CI **[−0.177033,+0.331019]**.
- Add original 18×19 field grid row controls: FG4 coefficient **+0.109808**, p **0.517740**. Restrict to 55 Woody-negative plots: β **+0.161634**, p **0.365127** (underpowered, does not replace original population).
- 1996 FG4 slope +0.3422 (HC3 p=0.0598); 1997 +0.2219 (p=0.2170); 1998 +0.0830 (p=0.5444). Three years are repeated treatments on **the same** plots and not independent replications.

## Results: *which guilds* were planted matters more than the count within Cedar
- Unrestricted 1998 four-guild-presence model: `log1p(AbvBio1998) ~ C(NumSp) + Woody + C3 + C4 + Forb + Legume`. This **subsumes** the equal-guild-coefficients count model exactly because `FG4=C3+C4+Forb+Legume`. Never enter all five predictors simultaneously; the design is rank deficient.
- The three-constraint robust HC3 Wald test of **equal coefficients across the four guilds**: chi-square **31.22**, p **7.63×10⁻⁷**. After field-row adjustment p **2.58×10⁻⁵**.
- An explicitly *post-result exploratory* conditional source-label test shuffled complete four-guild identity vectors **within fixed NumSp, Woody and FG4 treatment strata** (9,999 permutations): p **0.0003**. It supports an association with sown guild **identity** beyond simply the number planted, **not an exact causal guild-specific mechanism** because assigned plant species differ too.
- Individual coefficient point estimates (not causal organism effects): C3 grass −0.349; C4 grass −0.044; non-legume forbs −0.083; legumes +0.566 on the log1p scale. Relative importance cannot be assigned to nitrogen fixation without direct process evidence. The nonwoody 55-subset equality test was also positive (exploratory HC3 Wald p=3.15×10⁻⁵).
- In-sample identity model R² = **0.336** versus simple FG4 model R² = **0.112**; the unrestrained model has three extra parameters and in-sample fit is not itself evidence of transferability.

## Spatially held-out prediction
- Leave one of four **fixed E120 field row zones** out, predict its plots once (n=94) from the other 3:
  - `C(NumSp)+Woody` baseline SSE **37.119**.
  - Add FG4 count SSE **37.166**, gain **−0.13%** (slight degradation).
  - Add four named guild presences SSE **32.433**, point gain **+12.62%**.
- **But** 2,000 **retraining** bootstrap draws of plots stratified within the same four zones yield guild model predictive gain 95% interval **−20.87% to +32.14%**, FG count **−11.43% to +6.38%**, guild minus FG **−16.70 to +33.79 percentage points**. Do not claim established novel-location forecasting superiority. These are zones **within one site**, not two ecoregions.

## Interpretation and cross-experiment boundary
Jena 2003 exact-richness 62-plot FG4 beta **+0.129**, p **0.168**; strict block×richness beta **+0.119**, p **0.293**. Cedar 1998 **+0.083**, p **0.544**, controlling Woody. The two sources thus offer **no clear independent evidence for a universal positive linear effect of coarse FG count**. Cedar provides a separate strong *within-experiment* association with guild identities; Jena's four groups differ fundamentally, and only two independent experiments are represented. Do **not** pool effect coefficients as a meta estimate, or claim community trait hypervolume, evolutionary phylogenetic memory, annual NPP, selection vs complementarity mechanisms.

For new biological significance, follow independent spatially replicated experimentally collected biomass/guild/trait data and preserve source-specific seasonal and treatment units. The original globally qualified 201-system BIEN phenotype-memory and sPlotOpen×GIFT PD–FD sources remain **PRE-OUTCOME HOLD**, and NEON is authenticated-source HOLD.

## Execution, code and provenance
- Frozen source design `docs/CEDAR_E120_FG_BIOMASS_SOURCE_GATE_V0_1.md`; separate single-year contract `docs/CEDAR_E120_1998_GUILD_RICHNESS_EXPLORATORY_EFFECT_V0_1.md`.
- Independently calculated from the byte-verified public source with Python/numpy/statsmodels and independent pandas/patsy reproduction: original 6 source/matrix tests pass; independent 1998 original beta and equal-guild HC3 Wald p match; conditional guild assignment shuffle p=.0003; 2000 refitted CV resamples full-rank.
- Aggregated result: `results/cedar_e120_source_v0_1/1998_guild_identity_vs_count_effect_v0_1.json`.
- Reproduction scripts and tests are packaged in the conversation as a self-contained source-fetching, SHA-verified archive without redistributed original XLS. GitHub Actions additionally pins and checks the original ESA source before numerical comparisons. No raw plot observations committed to Git.
