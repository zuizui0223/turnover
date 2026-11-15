# Cedar E120 1998 guild-identity contrasts conditional on original field geometry

Date 2026-11-15. **Retrospective/post-result exploratory stress test only.** The original 1998 Cedar guild identity result was already known before choosing the extra spatial conditioning. Original 3-year teaching source fails the previous source programme's ≥4-year gate. No source change or selection on measured biomass was applied during this stress test.

## Verified original source and treatment population
- ESA TIEE 2004 E120 public `DataBonus-Student.xls` with SHA256 `a86755544d75fabb85f4979303efcada96683ae60c0bc3bdb60c5d4c739d7476`, converted to research-only CSV with SHA256 `c40ee678ca80a6bb73680115205b13eef20a9c5fd502284be38482a332a43db1`.
- Same **94 source-selected plots** with planted richness 2,4,8; 39 originally Woody-positive. Response is `log1p(AbvBio 1998)` from secondary educational table, documented as aboveground biomass g/m²; exact harvest definition and sowing/weed separation from authoritative EDI remains inaccessible (HTTP 403).
- Four herb guild flags `C3,C4,Forb,Legume`, and `FG4=sum(flags)`. Woody is separately controlled, not included in FG4. No causal mechanism or new taxa are inferred.

## Source-only exchangeability support

| Conditioning for changing the guild *vector* while retaining guild *count* | Variable source strata | Plots in variable strata |
|---|---:|---:|
| Cedar: exact planted richness × Woody × FG4 | 9 / 14 | 73 / 94 |
| Cedar: + 4 original grid-row zones | 18 / 39 | 60 / 94 |
| Cedar: + **18 individual field rows** | 15 / 71 | **33 / 94** |
| Jena 2003: planted richness × **original experimental block** × FG4 | 8 / 54 | **16 / 62** (all richness2, 8 distinct two-plot pairs) |

Cedar four field-row zones are analytical spatial strata, whereas Jena's four original blocks are experimental design features, so these are not fully equivalent exchangeability structures. In both designs some source cells have one planted guild vector only.

## After conditioning on geography, the within-Cedar identity heterogeneity persists

For each spatial geometry, fit nested same-source models `log1p(aboveground biomass 1998) ~ C(planted richness) + Woody + C(geography) + FG4` versus replacing `FG4` with `C3+C4+Forb+Legume`. Both models use the same 94 plots.

| Location adjustment | HC3 3-df Wald test of four equal guild coefficients | 9,999 guild-vector permutations conditional on richness, Woody, FG4 and location |
|---|---:|---:|
| Four spatial zones | χ² **30.33**, **p = 1.18 × 10⁻⁶** | **p = 0.0004** |
| Eighteen individual field rows | χ² **23.93**, **p = 2.58 × 10⁻⁵** | **p = 0.0070** |

Group-vector permutations are **conditional reference diagnostics**, not exact causal randomization or proof of guild-specific functional complementarity: they preserve observed design covariates but not planted *species identities*. Four-zone 60 / 94 and 18-fieldrow 33 / 94 are the effective label-variable subsets, not 94 independent observational comparisons.

Source-reproduction code re-estimated source-species exact matrix models from pinned CSV, and an independent `statsmodels.formula.api` reconstruction matched both Wald χ² and p to machine precision. Result: `results/cedar_e120_source_v0_1/1998_guild_identity_geo_conditioned_v0_1.json`.

## Interpretation: difference between two experiments is not a universal law
- Cedar 1998 n94: **group count** FG4 β+0.083, p=.544 (not positive evidence); guild identity heterogeneity significant under 4-zone or row controls.
- Jena 2003 n62: FG count β+0.129, p=.168; four-guild coefficient heterogeneity May p=.309 (strict block×richness p=.641), eight exact design pairs p=.5, May original-block heldout SSE **0.83% worse** with guild identities than count.
- Thus **the measured pattern differs across original experiments**; identity cannot be asserted as generally more important than group count for biomass. The difference may reflect plant taxon compositions, unequal guild definitions, ecological backgrounds, treatment support, response/season definitions, or differences in power. Two datasets are not a meta-analysis and cannot distinguish these explanations.
- Both guild count and guild identity are **coarse categorical features**, not independently measured quantitative trait diversity Rao Q, phylogenetic signal rho, or whole ecosystem biomass/NPP.

The original turnover BIEN 201-system memory mainline, sPlotOpen/GIFT source HOLD and NEON auth gate are unchanged; PR #44 stays exploratory Draft/unmerged.
