# Jena 2003 group diversity–harvested biomass: independent sentinel effect contract v0.1

Frozen on 2026-11-14 **before reading any biomass values into the regression**.
Upstream independently verified:
- Original PANGAEA 10.1594/PANGAEA.846317 (SHA256 `70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079`) contains 82 plots, 820 rows, four subsamples plus one mean per plot × 2 harvests, 60 species-specific dry-weight columns, no community biomass failure sentinel.
- Original [Jena plot information](https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt) (SHA256 `7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70`) uniquely covers all 82 plots, 4 blocks, 6 sown richness levels, 4 original functional-group richness levels, and a 60-taxon group allocation with **100%** agreement against structural source sowing masks. Verified [Actions #43576253012](https://github.com/zuizui0223/turnover/actions/runs/43576253012).
- This is a **separate single-site measured-biomass sentinel**, NOT reopening the held original global sPlotOpen/GIFT/BIEN >=90% exact name and >=12-family programme. No quantitative Rao's Q, phylogenetic MPD, evolutionary `rho` or causal group complementarity coefficient can be inferred from this design.

## Exact primary analysis

**Unit:** one Jena experimental plot; 82 unique plot IDs, not individual quadrat rows.

**Outcome:** `Y_p=log1p(Sown plant biom dw [g/m**2])` from the original source row with `Repl=="mean"` and `Date/time start` in **May 2003**. May was frozen as primary before numerical outcomes opened. No pooling the same plot's August, no summing standing biomass to annual NPP. Refuse to fit if any plot is unavailable, source hash changes, any negative/missing biomasses appear, or any duplicate plot-month mean exists.

**Predictors from source-independent original sowing metadata:** `x_p=log2(NumberSownSpecies)`, `FG_p=NumberFunctionalGroups` (integer 1–4), and block `B1` through `B4`. These are **planned experimental assignments**, not realized 2003 biomass-derived weights. Four original group classes are grasses, small herbs, tall herbs, legumes.

**Models (same 82 May plots):**
- Baseline M0: `Y ~ 1 + log2(sown_richness) + block` (three fixed block indicators).
- Primary M1: `Y ~ 1 + log2(sown_richness) + FG_richness + block`.
- `beta_FG` of M1 is the primary descriptive effect per added sowing functional group at the same planned sown richness/block.
- Two-sided HC3 plot-robust coefficient p and 95% Wald CI; additionally **2000** plot-level block-stratified nonparametric bootstrap M1 coefficient draws (same number of plots per block, with replacement, seed **20261114**); percentage 2.5/97.5 CI. No p-hacking; positive support defined ahead of time as `beta_FG>0`, bootstrap 95% lower bound >0, and HC3 p<0.05. If any condition fails, no positive support claim.

**Independent predictive test:** leave-one-*block*-out (4 groups), M0cv `Y ~ 1+log2(sown_richness)`; M1cv `Y ~ 1+log2(sown_richness)+FG_richness`. Block indicators are omitted in both because the held block has no estimated fixed effect. Pool 82 test predictions once, return `gain=1-SSE_M1cv/SSE_M0cv`. Positive gain is separate from coefficient evidence, and negative/zero results must be retained.

**Pre-registered secondary diagnostics (not separate confirmatory discoveries):**
- Same M1 formula on **August 2003** (same 82 plots), report sign and coefficient; do not double sample size.
- Remove all 4 60-species whole-pool plots and refit M1 to identify high-richness leverage, not select hypothesis.
- Add `PresenceLegumes` to M1 as an explicit *alternative group-identity* explanation: whether an FG-richness association persists when the legume group is present is descriptive only, NOT a randomized independent legume experiment. Do not add all four group-presence indicators because their sum identically equals FG richness.
- If design full rank/expected n insufficient, stop as pre-outcome HOLD; if an effect is null/negative, report it.

## Interpretation and attribution
The response is directly dried harvested **standing aboveground biomass** per m² at one season, **not annual NPP**, belowground carbon, whole-plant biomass or organ-specific allocation. A positive FG effect conditional on sown richness would be a **within-Jena experimental pattern**; do not claim evolved trait-memory explains it, or that the coefficient transfers to other biomes, islands or plant families. Follow PANGAEA CC BY 3.0 source attribution and Jena data-use citation guidance.

The valid empirical result must preserve both a favourable and an unfavourable answer. The original global PD–FD primary programme remains completely unchanged.
