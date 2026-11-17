# Jena 2020 original h1/leafN: signed trait-scale correction completed, fixed future-year source gate still HOLD

**Result closed 2026-11-17.** No new annual biomass prediction, trait-FD coefficient, effect size, bootstrap interval, phylogenetic K or evolutionary memory rho was ever estimated in either attempt. We retain both original source gates, because the first was semantically incorrect for the original already-standardized data and the second was separately frozen before ANY outcome estimate.

## 2020 original source provenance and exact source geometry

The van der Plas et al. 2020 original author [Figshare 12834350](https://doi.org/10.6084/m9.figshare.12834350.v1) provides all six original CSVs with verified original MD5. Exact cross-file plotcode/years/species identity was established **before** any target-model attempt: **78/78 original Jena main plots**, **851/851 original plot×year** intersection of biomass, vegetation cover and raw functions, original `traits.st.csv` **59/59 source trait-species abbreviations** matching cover and biomass. Original `functions raw values.csv target_biomass_average` 847/851 source records numeric-present (2002–2012). There are 82 cover plots because it includes plots not in the main 78-function study; raw biomass `plot` number alone has 24 values reused within blocks, so `plotcode` is essential. The 2022 Hagan reanalysis is the SAME Jena original experiment, not an independent ecological replication; earlier turnover Jena guild analyses overlap it.

Original authors' [public R analysis](https://github.com/fonsvanderplas/traits-and-ecosystem-properties/blob/master/main%20analysis.r) reads `traits.st.csv`, uses regularized PCA imputation of missing species traits, original code-based cover ordinal corrections, Rao Q FD and cover-weighted community means (FI). Some original derived community rows are conditioned on positive `target.biomass`; those original-author precomputed predictors are **not automatically fold-safe for a new 2010–2012 heldout-year analysis**. We did not re-use them.

## Critical source correction: the original trait table is already standardized

The originally frozen v0.1 trial incorrectly required **positive** physical h1 height and leafN nitrogen concentrations and attempted `log(trait)`. This produced **only five positive-positive taxa** and **three** eligible original cover plot-years (all 2010–2012; none in 2003–2009). The workflow correctly stopped at SOURCE_SUPPORT_HOLD **before running any response model**, but the initial technical CI field assertion needed repair. The fixed original v0.1 CI now marks this as source HOLD **SUCCESS**; its eligibility and science criteria remain unchanged and unmerged.

Independent source-only original `traits.st.csv` diagnosis (MD5 `8045e7ee38f26b212dbe81aed0039765`, 59 original taxa) shows:

| Original trait | Source finite values | Original negative values | Missing | Observed finite-value mean | Source sample SD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `h1` height source column | **57** | **37** | **2** | approximately 0 | **1.0000** |
| `leafN` leaf nitrogen column | **59** | **33** | 0 | approximately 0 | **1.0000** |
| Species with BOTH original source values finite | **57** | — | — | — | — |
| Species with BOTH source values strictly positive | **5** | — | — | — | — |

The exact zero means and sample SD=1 to rounding are direct numeric evidence of **species-level standardization** in the original file. Negative numerical values do **not** mean negative cm of height or leaf N concentration. This is not a raw physical-unit table. Source original per-species physical units or exact precursor transform were not reconstructed from these data. The authors' R code directly computes FD on this trait matrix (after imputation) **without logging these already-standardized values**. A silent switch from positive/log to signed standardized in the same v0.1 protocol would have been incorrect; so a **distinct** corrected v0.2 design was committed **before any new outcome** in `docs/JENA_STANDARDIZED_SIGNED_H1_LEAFN_ORIGINAL_TIME_TRANSPORT_DESIGN_V0_2.md`, preserving the original target, trait pair, original cover ≥80% source threshold and all predeclared plot/year/species minima.

## New signed-source v0.2 trial: source sample geometry still FAILS the frozen gate

The corrected v0.2 no-imputation test uses all 57 original finite signed h1+leafN source taxa without log, contemporaneous original Jena cover, original authors' cover ordinal correction (1→0.5, 2→3), original plot-year cover weights, 2003–2009 source training years and fixed 2010/2011/2012 original heldout calendar years. Source eligibility still requires at least two matched positive-cover species, ≥80% cover mass represented, ≥20 original trait species, **≥60 unique original training plots**, ≥6 original train years and **≥60 original plots in every heldout calendar year**.

| Source-only quantity after correct original scale | Actual verified original source | Frozen eligibility threshold |
| --- | ---: | ---: |
| Distinct original signed h1+leafN reference species in source-feasible plot-years | **57** | ≥20, PASS |
| Original 2003–2009 source training years with numeric target *presence* | **7** | ≥6, PASS |
| Unique original training plots with eligible cover/traits | **55** | **≥60, HOLD** |
| Original 2010 source plot-years with eligible cover/traits | **47** | **≥60, HOLD** |
| Original 2011 eligible source plots | **48** | **≥60, HOLD** |
| Original 2012 eligible source plots | **51** | **≥60, HOLD** |
| Total original 2003–2012 source plot-years with full source covariates | **489** | original 773 within chronological window |
| Original plot-years failing ≥80% original source trait-cover weight | **137** | source-only QA |
| Original plot-years with <2 joint complete trait species | **147** | source-only QA |

**Status SOURCE_SUPPORT_HOLD, NOT an ecological nonpositive finding.** Zero model coefficients, no source-year out-of-sample SSE gain, no community FD-to-biomass association estimated. Original 78 main experimental plots still exist, but a substantial fraction are single-species stands or have insufficient *usable source trait* cover to compute pairwise FD, and the matched source populations do not meet the originally specified ≥60 plot/year threshold. We did not change `h1+leafN`, source transformations, seasons, years, cover minimum or plot support thresholds after seeing this result.

Note that the 137 and 147 plot-year support counts refer to mutually categorized source cases (the source workflow checks <80% cover before <2 species), not two independent biological causes. Do not assume all 147 are monoculture plots without a separate source audit of original sown diversity.

## Scientific decision

- **Confirmed methodological point:** phylogenetic breadth, source trait dispersion, original plot-in-situ trait plasticity, and reference trait-based FD are different biological quantities, and trait compilation can have missingness/standardization that must be audited before interpreting a "failed ecological signal."
- **Cannot support:** a positive/negative Jena FD→biomass transfer result under the fixed v0.2 no-imputation source thresholds, because no such effect was fitted.
- **Old strict general tests remain closed:** global BIEN time-space, GloBI interaction, original BIODEPTH 6-site and NEON source-auth; no family Blomberg K/rho measured for these 59 original source species.
- **Do not run another adjusted h1+leafN Jena model** by lowering ≥60 plot/year to 47 or by replacing negative signed source traits with arbitrary positive offsets after source results. A new biological question requires independently preregistered data and preferably another original site/dataset, not recursive source-gate relaxation.
- Original published 2020 results of 41 trait/FI/FD analyses (authors' imputed matrix) and 2022 reply (same original study) should remain original authors' already published findings, distinct from this source-only failure.

## Exact reproducibility

- Historical canonical 78 plot/851 plot-year/59 source taxon source: `results/jena_2020_original_source_78plots_851plotyears_59traitspecies_v0_2.json` (parent Draft #58), original successful source run [#44004892797](https://github.com/zuizui0223/turnover/actions/runs/44004892797).
- Original v0.1 **source HOLD** archive `results/jena_original_h1_leafN_raw_source_HOLD_preoutcome_v0_1.json`, [corrected technical CI #44005557495 SUCCESS](https://github.com/zuizui0223/turnover/actions/runs/44005557495), artifact #14295060234.
- Source-only signed transform audit [#44006083178 SUCCESS](https://github.com/zuizui0223/turnover/actions/runs/44006083178), `results/jena_original_h1_leafN_signed_source_scale_v0_2.json`; artifact #14293638794 digest `sha256:f690544337f9564c4d069a28b43f780b7425d9e013894296c5c33bbc69b10ea5`.
- v0.2 source gate trial [#44006596166 SUCCESS](https://github.com/zuizui0223/turnover/actions/runs/44006596166) (source scientific status HOLD, no effect), archive `results/jena_original_signed_h1_leafN_time_transport_SOURCE_HOLD_v0_2.json`, artifact #14294044423 digest `sha256:00321094d5e1ddbf04486125540520645e368283cb0ef75ea952898160aa8b1e`.
- Source files `scripts/source/audit_jena_h1_leafN_signed_scale_semantics_v0_2.py`, `scripts/analysis/test_jena_signed_h1_leafN_raoq_outofyear_v0_2.py`. All original public data downloaded and MD5-pinned inside ephemeral GitHub Actions only; source tables, traits, biomass values and plot IDs never committed. Draft stacked above Draft #59, main untouched.
