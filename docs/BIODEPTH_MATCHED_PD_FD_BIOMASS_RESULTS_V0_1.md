# BIODEPTH: matched phylogenetic breadth provides no robust incremental out-of-site biomass or height-FD prediction

**Executed 2026-11-16.** New source-pinned analysis **frozen before these PD-model outcomes** in `docs/BIODEPTH_MATCHED_PD_FD_BIOMASS_SITE_HOLDOUT_DESIGN_V0_1.md`, but scientifically *post-result exploratory* because the historical height-FD and biomass models, their GIFT-source correction, and 999 guild-label null were already seen. Do not describe the result as an independent prospectively confirmatory test.

## Original source and sample eligibility passed before Community response

- Prior GBOTB S3 tree source-only gate (Draft PR #49) **PASS**: 98/103 original BIODEPTH plant taxa, 80 direct tips + 18 grafted, 18 families, 206/480 planted plots with ≥3 S3-covered original species, across 8 sites.
- Prior GIFT×GBOTB joint source-only gate (Draft PR #50) **PASS**: 84 of 88 historical height-covered species on original tree (78 native), across 17 families and **150** of the historical **174** original height-eligible plots, **7** geographically independent original BIODEPTH fields. Site populations **Germany 26; Ireland 26; Portugal 8; Sheffield 20; Silwood 24; Sweden 18; Switzerland 28**. Thus the previous source-model +3.83% gain on 174 plots is *not matched* to this new 150-plot cohort and must not be directly compared as a PD increment.
- Original plotted 2010 Hector **Community** standing aboveground biomass source: **449 numeric original plot×year responses** from the 150 source-qualified planted plots, one source missing value; three source years, same original plot/year labels. All 2010 original source species/codes/biomass and original 2005 **planting design** SHA256 verified. Original 2005 Shoots biomass is NOT used; no species current-year mass predictor weights.
- GIFT original plant maximal-height reference/source fingerprint reverified; historical `Origanum vulgare` 13m source anomaly uniformly replaced by **Kew .9m**, already known from the previous retrospective source audit.
- S3 dated patristic distance on 84 GIFT height-bearing plant taxa, equally weighted from same original planted species as equal-sown height mean and FD. This is phylogenetic **breadth**, not AusTraits Blomberg's K or BIEN time-loss rho.

## Fixed primary: does phylogenetic breadth improve out-of-original-field biomass prediction beyond FD?

M2 has quadratic log2 planted richness, original planted grass/forb/legume treatment, original year, train-normalized original planted log max-height **CWM** and mean absolute pairwise log-height **FD**. M3 adds **one train-normalized same-species S3 mean patristic distance**. Both refitted within seven leave-whole-original-site-out folds. Primary equals 7-site equal average `1−SSE(M3)/SSE(M2)`; 10,000 site-bootstrap draws, seed 20261116. No heldout site or plot was removed after opening effects.

| Heldout original source field | Gain of adding S3 PD beyond FD/CWM |
| --- | ---: |
| Germany | −16.226% |
| Ireland | +1.811% |
| Portugal | +1.714% |
| Sheffield | +0.872% |
| Silwood | +7.556% |
| Sweden | −0.007% |
| Switzerland | −5.878% |
| **Seven independent site-equal mean** | **−1.451%** |

- **95% site bootstrap CI −7.291% to +3.151%**, 4/7 site point estimates >0.
- **Frozen primary positive-site-transfer condition FAILED** (mean not positive, lower CI not positive, only 4 positive sites).
- Deleting each already-computed source-site score from the seven-site average, **without refitting model coefficients**, spans **−2.952% to +1.011%**; only omission of Germany turns the average positive. This is a *posthoc influence diagnostic*, not a new leave-out external validation or permission to drop Germany.

**Interpretation:** In these seven original study environments, S3 phylogenetic breadth is not a robust general added predictive feature for measured biomass beyond planted community composition, mean height and height dispersion. This is **not** evidence of zero causal ecological PD effects or an universal negative PD–mass relationship.

## Fixed secondary: does phylogenetic breadth predict planted height-FD itself out of site?

Same **150 unique original planted plots**, no repeated years; source FD outcome is one-axis mean absolute pairwise **log-height** difference among identical source taxa. Baseline planned richness + original guild flags + train-normalized mean log height; candidate adds train-normalized S3 patristic mean.

| Heldout original source field | Gain of PD for heldout planted height-FD |
| --- | ---: |
| Germany | +5.021% |
| Ireland | −36.800% |
| Portugal | −6.207% |
| Sheffield | +5.365% |
| Silwood | +7.198% |
| Sweden | +10.043% |
| Switzerland | +5.031% |
| **Seven independent site-equal mean** | **−1.478%** |

- Site bootstrap 95% interval **−13.884% to +7.031%**, 5/7 site estimates positive, but frozen positive transport condition still FAILED due negative mean and interval crossing zero.
- Removing only Ireland's **already fitted site score** yields +4.409% among remaining six. No claim of new independent success follows; this exposes that the negative aggregate is sensitive to a single site.

This association tests *how far a phylogeny-proxy of differences between species can generalize*, not whether trait dissimilarity itself has a phylogenetic signal K across families.

## Mandatory native-backbone-only sensitivity

At the same fixed ≥3 taxa and 80% planted-source coverage, restrict traits to **78 exact backbone-native source species**, resulting in a *separate* **102 original plots** / **305 numeric plot-year responses** across seven original source sites (14 Germany, 26 Ireland, 8 Portugal, 18 Sheffield, 14 Silwood, 14 Sweden, 8 Switzerland). This population independently passes the previously frozen ≥100 plots / ≥5 field-sites with ≥8 plots criterion.

- Mean out-of-site incremental S3 PD biomass prediction **−3.500%**.
- 95% source-site bootstrap CI **−6.191% to −1.074%**; 2/7 source site gains positive.
- Removing each already fitted site score yields a six-site mean in **−4.175% to −2.612%**. The negative mean is not caused by one single site in this *restricted cohort*.
- **Critical:** This is **a different source-selected plant/plot cohort**, so the change from −1.451% to −3.500% is not the isolated causal effect of excluding S3-grafted tips. Differences in sample composition, taxon coverage and model retraining could explain it. Not a biological PD negative mechanism.

## Integrated scientific boundary

Three distinct source-verified empirical findings now coexist:
1. Same-tree/source lineage- or organ-level memory K/rho components are measurable, including family-context repeatability and exploratory reproductive > vegetative K.
2. In BIODEPTH, external source maximum-height measurement quality alone reverses an extreme one-axis FD transfer failure; the repaired 174-plot FD positive gain +3.83% is unsupported by its original uncertainty.
3. The new 150-plot matched phylogenetic-breadth arm now **also fails to establish a general transferable increment**, both for direct FD prediction and for biomass given CWM/FD. **No matched family-specific K→FD→mass association was ever estimated**, so never state evolutionary memory drives biomass.

The strongest defensible general framing is that **lineage information, trait dissimilarity, source composition and biomass prediction are not interchangeable summaries**. Which species enter a community, how their traits are measured, and what outcome is predicted govern how useful a phylogenetic proxy is. Proving a mechanism would require independent original species trait measurements, matched phylogeny and field responses at many independent communities/sites, with counterfactual treatment or external validation beyond retrospective model choice.

**Status:** New observational outcome executed with original source and fixed design, independently reproducible as a pipeline, nonraw archived. No claim of general PD positive/negative ecological effect. Original strict six-site BIODEPTH, global BIEN/sPlotOpen 201 family×trait and NEON token source gates remain HOLD. `main` unchanged; Draft PR only.

## Exact evidence

- [Original source-only 103 taxon phylogeny audit](https://github.com/zuizui0223/turnover/actions/runs/43818684314) SUCCESS.
- [Original GIFT 84-taxonomy / 150 plot source-only join](https://github.com/zuizui0223/turnover/actions/runs/43819650055) SUCCESS.
- [**Actual original Community source PD/FD/biomass effect**](https://github.com/zuizui0223/turnover/actions/runs/43821005183) SUCCESS. Original aggregate artifact #14204598003 digest `sha256:43fec0dfe9b2e8d915b2f5529db0406812db688ba7babdc1119a35a015b2aec6`.
- Source-run stdout aggregate and descriptive site influence permanently saved at `results/biodepth_2010_species_source_v0_1/matched_pd_fd_biomass_source_verified_result_v0_1.json`, source-pinned script `scripts/analysis/fit_biodepth_matched_pd_fd_biomass_transport_v0_1.py`, and workflow `.github/workflows/biodepth-matched-pd-fd-biomass-transport-v0-1.yml`. Original copyrighted field rows and downloaded GIFT traits never committed.
