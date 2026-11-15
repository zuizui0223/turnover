# Jena 2003 within-sown-richness support sensitivity — 2026-11-15

**Status:** completed retrospective post-result exploration. This does not modify the original PANGAEA 2003 coefficients, original Jena biomass endpoint partition, original BIEN/AusTraits phylogenetic memory results, or the sPlotOpen primary PRE-OUTCOME HOLD.

## Core source identity
- Original sown-species aboveground dry biomass: [PANGAEA 846317](https://doi.org/10.1594/PANGAEA.846317), 820 records = 82 original plots × 2 seasons × 5 replicate/mean rows; original content SHA256 `70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079`.
- [Original Jena plot allocation](https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt), SHA256 `7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70`.
- Data plot × richness × planned FG support: 1 species/FG1 n16; 2 species/FG1–2 n16; 4 species/FG1–4 n16; 8 species/FG1–4 n16; 16 species/FG1–4 n14; 60 species/FG4 n4. **Only 62 plots** (2/4/8/16 species) have within-exact-richness FG variation.

## Explicitly retrospective statistical comparison (May log1p sown-species dry mass)
| Treatment effect model | Plots | FG slope | HC3 95% CI | HC3 two-sided p |
|---|---:|---:|---:|---:|
| Original log2 planted species number + block FE | 82 | +0.167891 | [+0.004585,+0.331196] | 0.043905 |
| Exact species richness category + block FE | 82 | +0.127496 | [-0.046508,+0.301500] | 0.150974 |
| Exact species richness category + block FE; only supported 2/4/8/16-species | **62** | **+0.128671** | **[-0.054094,+0.311437]** | **0.167628** |
| Fully within-block×exact-richness 16-stratum FE (post-result conservative diagnostic) | **62** | **+0.119307** | **[-0.102991,+0.341604]** | **0.292841** |

For the primary supported 62-plot categorical-richness model: block-stratified independent-plot bootstrap **4,000/4,000 valid**, seed 20261119, 95% percentile CI **[-0.029345,+0.342164]**. An approximate within-*block×richness* response-permutation test, 9,999 draws, seed 20261120 gives two-sided **p=0.4170**; an independent permutation of FG labels rather than the outcome (4,999 draws, seed 20261121) gives **p=0.4212**. The strict 16-stratum model's same-resampling null p=**0.4633**. These are **exploratory conditional-exchangeability tests**, not causal group-count randomization distinct from species identity.

**Key distinction:** categorical species-richness slopes at n82 and n62 are almost the same. The apparent attenuation relative to the original `log2(richness)` model comes chiefly from permitting a flexible non-linear richness response, **not** solely deleting richness 1 and 60 extremes. Direction remains positive but statistical uncertainty is broad; absence of p<0.05 does not prove a zero FG effect.

## Other outcome sensitivity, same 62 supported plots
- August sown biomass FG β=−0.0162, p_HC3=0.848.
- May combined sown + non-sown plant biomass FG β=+0.1168, p_HC3=0.205.
- August combined aboveground biomass FG β=−0.0269, p_HC3=0.753.
- Raw-scale May sown aboveground mass FG slope +37.08 g/m² per planned group (HC3 95% CI −13.16 to +87.33, p=0.148).
- Leave one supported richness level out: coefficient +0.1432 (omit 2), +0.1701 (omit 4), +0.0330 (omit 8), +0.1546 (omit 16). No p-values support a conclusion that one richness level mediates the effect.

## Verification
Original treatment labels/frozen input SHA256 verified, original 82-plot May FG beta reproduced to <1e-9. **14 Python tests pass.** Independent pandas/statsmodels formula reanalysis for eight endpoint/model comparisons (including a saturated 16-cell model) reproduces estimated coefficients, HC3 p-values and confidence intervals with maximum absolute discrepancy **5.7e−14**. Independent within-stratum FG-label permutations reproduce p≈0.42. All new tests are post-result, no data- or significance-driven redefinition of original cohorts or claimed confirmatory novelty. Source/public original bytes and complete runnable code retained in conversation ZIP `turnover_jena_within_richness_results_20261115.zip`; do not commit source observations to Git.

## Ecological claim boundary
Original May nominal association **does not remain statistically established** when species richness is fitted as a categorical treatment or when contrasts are restricted to genuinely FG-variable richness strata. This supports downgrading any strong independent FG complementarity/biodiversity–biomass effect claim from this particular 2003 cohort. The positive direction alone is not proof of strong complementarity, and neither this source nor the 10-year Jena source establishes phylogenetic trait-memory effects or a global FD–biomass law.

**Publication readiness:** source and calculations reproducible for this narrow robustness check, but Jena alone should not be sold as a novel independent macroecological paper. Preserve one-site, original sowing-treatment, same-study and post-result boundaries.
