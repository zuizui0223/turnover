# BIODEPTH 8-site matched planted guild replacement: original-source retrospective result v0.1

Checkpoint 2026-11-15 (JST). **Exploratory/post-result extension only**; source comparison was selected after original Jena, Cedar and BIODEPTH guild-count results were already known. The paper BIODEPTH Spehn et al. (2005) already examined legume and functional-guild effects; this cannot be described as a new general ecological discovery.

## Original data and frozen contract

Original public Figshare Supplement 1, Spehn et al. (2005) [DOI 10.6084/m9.figshare.3565170.v1](https://doi.org/10.6084/m9.figshare.3565170.v1), source license CC0:
- `Design.txt`, SHA256 `a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a`; original 480 experimental plots × 8 geographic field sites.
- `Shoots.txt`, SHA256 `cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135`; original 1,440 plot × year records (year 1,2,3).
- Original companion metadata `suppl-1.htm`, SHA256 `20694c14d6b6eccf016294eeae2058479b12c830272a6175a62d32714703c116`.

**Independent original structural primary source gate remains HOLD**: 8 sites/480 plots/3 years were present but only **one of eight sites** had ≥20 plots in one exact planted-species richness treatment with ≥2 distinct functional-guild counts; the prior minimum was six qualifying sites. The current matched guild replacement is a **separately frozen exploratory subpopulation**, defined in `docs/BIODEPTH_TWO_GUILD_MATCHED_LEGUME_VS_FORB_V0_1.md`, not retroactive passage of that gate.

## Sample and estimator

The studied comparison explicitly fixes grasses present, *planned number of functional guilds* = 2, original site, exact *planted species richness*, and original field block. The only variation is whether the other planned guild was **nitrogen-fixing legumes** or **nonlegume forbs**. Actual species mixtures differ between arms, so this does not identify a pure legume addition, an experimental nitrogen-fixation effect, or a guild-intrinsic effect.

Design-only support: 114 candidate source plots, 110 matched eligible plots in 35 site × richness × block strata, across all eight BIODEPTH sites. There were 330 repeated plot × year rows (same plots across 3 source years), of which 327 have valid original biomass, with 3 NA values not recoded as zero. For each matched stratum × year, compute mean `log1p(Shoots.biomass)` for grass+legume minus grass+forb; take equal mean of three years within each stratum, then equal mean of the available original strata per site. **Geographic site** is the unit of cross-site uncertainty; do not treat 327 rows as independent environments. Exactly 105 paired stratum × year contrasts exist, all 35 × 3.

## Eight geographic site-level results

| Original BIODEPTH site | Matched original plots | Planted composition clusters | Matched log difference: grass+legume minus grass+forb |
|---|---:|---:|---:|
| Germany | 18 | 9 | **+0.5520** |
| Greece | 14 | 7 | **−0.8327** |
| Ireland | 16 | 8 | **+0.2020** |
| Portugal | 6 | 3 | **−1.6640** |
| Sheffield | 8 | 4 | **+0.1561** |
| Silwood | 20 | 10 | **+0.1349** |
| Sweden | 8 | 4 | **+2.2231** |
| Switzerland | 20 | 10 | **+0.6003** |

**Equal-site descriptive mean** of the 8 log differences: **+0.17147**, median **+0.17905**, between-site SD **1.12869**, six positive and two negative original site estimates. 10,000 site-resampling bootstrap draws (seed 20261116), 95% percentile CI **−0.54832 to +0.91837**. This CI spans zero, so no robust common positive legume-companion association across sites is established.

A site-specific alternative fixed-stratum + source-year model with sandwich covariance clustered by original planted species composition was estimable in 7 sites. **Portugal has only 3 planted composition clusters and is inferentially HOLD**; its descriptive point remains included in the equal-site mean, preserving the original eight-site support. No site/plot exclusion based on outcome magnitude.

## Post-result influence and year sensitivity

- Leave one geographic site out from equal-site mean: **excluding Sweden produces −0.12162**; **excluding Portugal produces +0.43368**. These are *influence diagnostics*, not a license for selective exclusion.
- Equal-site mean at source year 1: **+0.04618** (five sites positive); year 2: **+0.43042** (six positive); year 3: **+0.03782** (five positive). No robust monotonic or universal year trend is inferred.
- Equal **35-stratum** mean is **+0.37175**, rather than equal-**8-site** +0.17147. The change is a weighting/estimand issue, not another independent dataset or proof of positive effects.
- Of source-matched numeric rows, nine plant-biomass zeros occur at Greece and one at Portugal, with 3 missing response rows (Ireland 2, Portugal 1). These real zeros are retained. A log1p difference is not a direct effect on annual NPP, especially when some original sites harvest standing crop once and others twice per year.

## Verification and scientific boundary

Locally the pinned original Figshare source bytes were re-read independently using **stdlib `csv.DictReader` + manual nested site/stratum/year aggregation**, without importing production helper functions. All 8 site results agree with the principal pandas/statsmodels implementation to numerical precision; 35 matched strata, 110 plots, 327 valid rows, 105 valid comparisons and original bootstrap CI exactly reproduced. Independent output: `matched_legume_forb_robustness_v0_1.json` and `verification_matched_independent_v0_1.json`. Reproduction source and original public CC0 source may be packaged for researcher audit; no raw original data are committed to the GitHub branch.

Source methods report aboveground **standing crop clipped above 5 cm and dried at 80 °C for 24 h**, harvested once in UK, Portugal, Sweden and Greece and twice in Germany, Switzerland and Ireland (UK Site Sheffield and Silwood both once); site/year measurement schedules differ. Avoid reinterpreting the common source `biomass` variable as cross-site homogeneous annual net primary production.

The scope here is more limited than the user’s broader original goal of **functional trait FD, family×trait phylogenetic memory `rho`, and biomass**: these BIODEPTH planted guild indicators are coarse assignment categories, not continuous plant traits or independent `rho`. The original sPlotOpen/GIFT/BIEN 201-system gate and NEON official API authentication gate remain untouched. No global evolutionary-memory-mediated biomass relationship or guild-specific causal mechanism is established.

### Implication for the next independent analysis

The source design suggests a more meaningful conditional question than 'Does more functional diversity always produce more biomass?' — **Under what source/environment and species-pool conditions is a planted guild composition contrast even identifiable, and how stable is its sign across genuinely independent field sites?** For a new claim, source-derived species mixtures and original climate/soil variables must be declared before outcomes, with meaningful replication beyond these eight original European experiments and explicit measurement protocol harmonization.
