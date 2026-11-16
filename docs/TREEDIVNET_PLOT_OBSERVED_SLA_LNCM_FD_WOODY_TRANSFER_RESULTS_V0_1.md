# Original TreeDivNet 2026: measured plot-local two-axis FD does NOT add out-of-experiment woody stock prediction (v0.1)

**Original data/model executed 2026-11-17 JST, after freezing new exploratory estimand and 80%-joint species-completeness source gate.** Same Jensen et al. 2026 Figshare 31026004.v1 original dataset. This is **not independent confirmation** of those authors' own positive diversity/mixing findings and **not** a causal mechanism.

## Scientific distinction: source response and predictor were not reconstructed

The authors' original [paper](https://doi.org/10.1111/1365-2435.70320) found positive forest mixture effects on woody biomass and a positive functional dispersion FDis association with woody *net diversity effect* (NDE; original paper β≈0.27, p<.001). Their published FDis source combined **283 original site-monoculture in situ averages + 17 externally sourced species-site trait values** (uploaded original Figure S4 and paper §2.5), not necessarily original measurements of all species in each target mixed plot.

**Here the deliberately different estimand** asks whether *actual measured in-mixture species×plot SLA and mass-based leaf nitrogen LNCM* pairwise Euclidean dispersion helps predict **absolute** plot-level woody standing stock (original DS1, Mg dry mass/ha), held out by entire independent planting experiment, after original planted species richness and same-in-plot trait CWMs are already in baseline. The original published plot-aggregate trait source (original DS2) was used only for original same-species SLA and LNCM; **DS2 species `biomass_woody` never entered either response or predictors**. Thus the historical `mean(DS2 woody)=DS1 woody` 321/328 identity is not used for the new predictor/response join. No original per-individual source reconstruction/causality claim is made; the historic stricter original individual-source and 7-plot DS2 woody normalization gates remain HOLD.

## First: source completeness PASS, independent of biomass effect

Source-only script and source artifact run [#43904442625](https://github.com/zuizui0223/turnover/actions/runs/43904442625) passed original Figshare DS1/DS2 MD5, original uploaded Table S1 source inventory year SHA and original Methods S1/S2 genetic/coppice restrictions. The original 117 source plots across 7 sites after excluding ECOLINK have **100% source planted-species coverage in both original observed SLA and LNCM**, original DS1 richness exactly matches DS2 species-row count in every one. **32 original source taxa**. The fertilized-MataDIV exclusion leaves 107 source plots in 6 sites with same completeness, 26 taxa.

The frozen new model further requires ≥8 original eligible plots per original experimental site (before opening outcomes) and ≥80 total eligible plots / ≥5 independent sites / ≥20 source species. Therefore:

| Original study population | Original source plots | Original study sites | Original full two-axis source taxa | Source check |
| --- | ---: | ---: | ---: | --- |
| Source eligibility after ECOLINK | 117 | 7 | 32 | 100% SLA+LNCM completeness |
| **Primary whole-site predictions** (remove IDENT Freiburg: 4 source plots, below a priori ≥8 source minimum) | **113** | **6** | **29** | PRE-RESPONSE rank and source gate PASS |
| Exclude MataDIV, before site ≥8 source minimum | 107 | 6 | 26 | 100% SLA+LNCM completeness |
| **Sensitivity whole-site predictions**, no MataDIV, also exclude IDENT Freiburg 4 | **103** | **5** | **23** | PRE-RESPONSE rank and source gate PASS |

These populations were fixed by original **source-only** plots/sites/trait coverage. No source site was dropped after viewing prediction errors. Site counts main: B-Tree9, FORBIO Gedinne12, FORBIO Hechtel-Eksel12, IDENT Macomer12, MataDIV10, MyDiv58. MataDIV-excluded drops its original ten plots but reruns all model fits, so the sensitivity is NOT a paired causal effect of fertilization.

## Frozen models and actual prediction results

- Original response `log1p(DS1.biomass_woody [Mg/ha])`, one stand-level source record per plot. Source Table S1 within **≤2 original inventory years** for both original observed species SLA and LNCM (no proxy for exact plot sampling day). ECOLINK genotype/coppice excluded. Original Table S3 documents site-specific allometries, including WD entering five MataDIV original mass equations, but **WD is absent from predictors**.
- Training only: log-transform original SLA and LNCM and standardize each trait **using the original DS2 species×plot measurements from the training 5/4 experimental sites only**. Compute site-heldout equal-species CWM for SLA and LNCM; mean pairwise Euclidean two-trait dispersion `FD_2D` across each original plot's complete, fully observed species set.
- **M1 (baseline):** intercept + log2 original planted species richness + two original CWM traits. **M2:** M1 + one FD_2D. Both fitted by original experiment-balanced WLS: each training study has total weight one, regardless of how many original plots. Leave one entire original site out (no site fixed effects for heldout unseen study).
- At each independent heldout site, `G_s=1−SSE(M2,s)/SSE(M1,s)` on log1p mass; positive means FD improves unseen-site prediction. Primary = **equal-site mean**, source-site 10,000-bootstrap CI, seed 20261117. Source preflight verifies original training M1 rank4/M2 rank5 and nonconstant observed FD before any outcome model score; it PASSED all 6 and all 5 source folds.

| Entire heldout original study site | n original plots | Main: added FD prediction gain | MataDIV-excluded sensitivity |
| --- | ---: | ---: | ---: |
| B-Tree | 9 | −1.24% | −134.16% |
| FORBIO Gedinne | 12 | +4.23% | +3.17% |
| FORBIO Hechtel-Eksel | 12 | −83.78% | −96.85% |
| IDENT Macomer | 12 | −45.46% | −16.66% |
| MataDIV | 10 | −98.06% | *excluded by frozen source context* |
| MyDiv | 58 | +14.88% | −286.47% |
| **Equal-source-site mean** | **113 main / 103 sensitivity** | **−34.91%** | **−106.19%** |

- **Main 6-site source-site bootstrap 95% CI −70.78 to −1.56%; only 2/6 positive sites.** Frozen positive transfer test FAILS.
- **MataDIV-excluded 5-site source-site bootstrap 95% CI −198.08 to −24.77%; only 1/5 positive sites.** Frozen positive transfer test FAILS.
- On the six pre-existing main source fold scores, removing *each one already-scored heldout-site gain* yields an equal-site mean range **−44.86% to −22.28%** (all negative). On the five pre-existing MataDIV-excluded fold scores, omission gives **−133.54% to −61.13%** (all negative). These are **posthoc descriptive influences**, not independently refitted 5/4-site validations or selection criteria. Source-site bootstrapping with only 6 or 5 clusters is fragile and descriptive, NOT a new meta-analysis.

These negative incremental prediction scores are **NOT negative biomass effects of traits or of tree diversity**; negative scores indicate FD worsens predictions after mean traits in this particular out-of-experiment model. Local original trait plasticity could respond to biomass/light, and year/stand-age/method differences are strong alternative explanations for unreliable generalization. No model was changed to rescue a preferred result.

## Ecological interpretation and what this does *not* contradict

1. **Original paper:** site-monoculture/externally completed FDis was associated with woody biomass *NDE* within known original experiments; mixture mass exceeded authors' expected monoculture values. **This new analysis:** plot-*observed* source SLA+leaf-N FD did not improve prediction of *absolute woody standing mass at unseen study sites*. Both can be correct because the original source traits, response target, estimand and validation geometry are different. There is no formal statistical evidence that original paper β and our prediction gains are inconsistent.
2. **No K or phylogenetic signal was paired here.** The tested predictor is *multivariate functional distance between plot-measured leaves*, not taxonomic phylogenetic breadth, original BIEN distance–disparity rho, AusTraits family Blomberg K, trait evolutionary rates or a tested K→FD→mass mechanism.
3. **No causality** from same-time observational plot means, with original stand biomass allometrically estimated using site-specific equations. In particular MataDIV's WD-derived estimated mass and original fertilized-only sample context prevent naïve ecological standardization of source allometries.
4. **Study-site adaptation to unseen experiments remains a challenge**: small original number of independently heldout study sites (6/5), MyDiv contributes 58 plots (~51% main), source richness/trait distributions differ by site. Site-balanced training guards against one large study dominating fit but does not create matching environments or prove intrinsic trait-rank portability across lineages.
5. **Original source historical HỌLD remains:** fully reconstructing per-tree measurements, per-sample origin or `DS2 species woody → DS1 plot woody` factor still needs author-supplied original calculation metadata. This exploratory *plot-level aggregate prediction* deliberately did not invoke those transformations.

**Stop:** Do not continue on this same original Jensen experiment with posthoc FD axes, weights, partial subsets, or tuning to find a positive effect. The next *distinct empirical* K→FD→biomass study requires independent original plant-community plot measurements of actual traits, properly qualified original plot mass and phylogenies across sufficiently many original taxa/families. The original global 201-family BIEN/sPlotOpen, strict original BIODEPTH and NEON auth source HOLD gates remain unchanged.

## Exact reproducibility

- Frozen source plot completeness protocol: `docs/TREEDIVNET_PLOT_LOCAL_TRAIT_COMPLETENESS_SOURCE_GATE_V0_1.md`.
- Frozen **new study prediction** before outcome opening: `docs/TREEDIVNET_OBSERVED_PLOT_TRAIT_FD_WOODY_SITE_TRANSFER_FROZEN_V0_1.md`.
- Historical original source 117/117 complete plotted species: `results/treedivnet_original_plot_local_SLA_LNCM_80pct_source_coverage_v0_1.json`.
- Source-verified original data run **[GitHub Actions #43905844746 SUCCESS](https://github.com/zuizui0223/turnover/actions/runs/43905844746)**, aggregate artifact #14245291977 digest `sha256:d82e78f67292eb3e064b033a2340ecba9c915080a599078e189b20a72cd640c7`.
- Permanent full nonraw study-site scores and CI: `results/treedivnet_plot_local_observed_SLA_LNCM_FD_woody_site_holdout_v0_1.json`. Original source-pinned code: `scripts/analysis/fit_treedivnet_plot_observed_twoaxis_fd_woody_source_site_holdout_v0_1.py`. This is a new Draft PR stacked on source PR #56; `main` unchanged. No original Figshare biological rows or user-uploaded XLSX/DOCX re-uploaded.
