# Independent forest source audit, 2026-11-18: 276 plot rows ≠ five independent country generalization domains; 486 source plots ≠ published 482

**New external-source data-quality results only; no new biomass/FD/K ecological coefficient computed.** The two original primary datasets are independent of the previously closed BIODEPTH field experiments and Jensen 2026 TreeDivNet network. The original direct plant family-specific evolutionary trait memory K→community FD→mass study **remains source-ineligible** for both.

## 1. African original forest source: five-country holdout is structurally nonidentifiable as frozen

**Original**: Noulekoun et al. 2023, *GEB* DOI `10.1111/geb.13800`. Public original [Zenodo #10045492](https://zenodo.org/records/10045492) original archived `dataall_Noulekoun_GEB.csv` MD5 `60fc555c8e2942af432b09d3aeb84d57`, original code & metadata separately MD5 verified. Original file has **276 rows, 276 unique plot IDs, 64 source columns, 5 original country labels**, complete 276 source plot standardized CWM/FDis/standardized AGB/climate/richness fields. The article reports 7,993 trees and 207 species, but **NONE of the original 207 species observations or original species names appears in this public aggregate CSV**. Source response `sd_agb.mg.ha` is **standardized author-derived AGB**, not original unstandardized biomass in Mg/ha. Age is absent for old-growth plots (only 104/276 original `age_years` values are present).

The *original* country labels and growth stage source grouping:

| Original CSV country label | Source forest plots | `old` plots | `young` plots |
| --- | ---: | ---: | ---: |
| `Benin` | **64** | 64 | 0 |
| `Burki Faso` | **8** | 8 | 0 |
| `Ethiopia` | **168** | 64 | **104** |
| `Gha` | **6** | 6 | 0 |
| `Togo` | **30** | 30 | 0 |
| **Total** | **276** | **172** | **104** |

`Burki Faso` and `Gha` are **the exact original CSV labels**, not normalized taxonomic/country aliases. The original article describes Burkina Faso and Ghana as sampling countries, but these raw abbreviations must be preserved unless a source-native validated crosswalk is supplied.

The separate, independent **derived-index** out-of-country predictive proposal had frozen source qualification **≥12 original plots in each of five countries**, ≥200 complete original plots, and **full-rank original baseline predictor design** in *every country-withheld fold*. Prescribed baseline included source `sd_richness`, `sd_cwmwd`, `sd_cwmsla`, `sd_cwmlnc`, `sd_cwmhm`, `sd_prec`, `sd_temp`, `sd_plots` and two-class `growth` plus intercept (10 columns); FDis candidate adds original `sd_fdis` (11 columns). This design and thresholds were frozen before source original country counts/FX scores were opened.

**Structural failure**:
- Two source countries are below the predetermined 12-plot minimum: `Burki Faso` **8**, `Gha` **6**.
- The `young` category exists **only inside Ethiopia** (104/104 young original plots). With Ethiopia held out, every one of the **108 other-country training plots is `old`**, so the developmental-stage class has no training variation. The source baseline design drops to rank **9/10** and FDis candidate design rank **10/11**; source-stage parameter cannot be distinguished from the intercept in that fold. Other four heldout countries have source rank 10/10 and 11/11.
- Ethiopia itself contributes **168/276 = 60.9%** original source plots, so conventional plot-random validation would create strong geography/source-stage leakage, hiding the absence of young forest outside Ethiopia.

**Decision: `AFRICAN_DERIVED_FDIS_AGB_COUNTRY_SOURCE_SUPPORT_HOLD`, before any AGB effect.** Do NOT drop `growth`, remove Ethiopia, merge country labels, lower country minimum, or call the resulting source CV a valid five-domain evolutionary/biomass law. This is an informative **source design confounding result**, not evidence that FDis has positive or negative biological effect. A genuinely new source such as measured young stands in other countries or adequate biomass+traits in `Gha`/`Burki Faso` would be needed for the frozen question.

Original source evidence [GitHub Actions #44302931105 SUCCESS](https://github.com/zuizui0223/turnover/actions/runs/44302931105) of **source audit** (scientific original country-effect model intentionally not executed). Nonraw artifact #14426977039 digest `sha256:20167df986f2ed804586170c1fa4c3709c5f3171fd1f6be03b65d042ca98095b`. Permanent original source counts and per-country fold ranks `results/africa_original_276plots_5country_derived_FDis_AGB_source_gate_v0_1.json`.

## 2. BEF-China original public Figshare source: an exact scientific sample-definition inconsistency

**Original**: Deng et al. 2025, *PNAS* DOI `10.1073/pnas.2506750122`, original [Figshare dataset #29592203.v1](https://doi.org/10.6084/m9.figshare.29592203). The original paper reports **482 experimental plots, 38,088 trees and four annual aboveground woody survey years**, 2021–2024, at *two* BEF-China experimental locations. Its published allometry deliberately uses a **constant 0.52 wood-density factor for all taxa**; no source functional wood-density differentiation can be inferred from the calculated AGB.

An additional direct original-source Python standard-library XLSX reader opened actual original source rows **only ephemerally** on GitHub runner (verified original file MD5s in records below), validated original `Plot×year` unique keys and numerical presence, then emitted nonraw counts:

| Source file | Original published file ID | Exact original MD5 | Original data rows | Original distinct Plot IDs | Duplicate Plot×year keys |
| --- | ---: | --- | ---: | ---: | ---: |
| `DengEtAl_PNAS_H1H2_20250718.xlsx` | 56354972 | `d045623a427b076d529cadb12c025242` | **1,927** | **486** | **0** |
| `DengEtAl_PNAS_H3_20250718.xlsx` | 56354975 | `a39eb71df9bf507892213a1d3891bc23` | **1,251** | **316** | **0** |

Original H1H2 fields are `Plot, year, TREE_R, AGB, Canopy cover, FHD, Db`. H3 fields are `Plot, year, TREE_R, NE, SE, CE, Canopy cover, FHD, Db`, the **already-derived** net diversity/selection/complementarity analysis, not 1,251 independent biomass specimens.

| Source year | H1H2 original Plot×year rows | H3 original Plot×year rows |
| --- | ---: | ---: |
| 2021 | **486** | 314 |
| 2022 | 481 | 315 |
| 2023 | 481 | 315 |
| 2024 | 479 | 307 |

**Original source bookkeeping issue:** the authors report **482** analysed plots, but the original released H1H2 data contain **486 distinct plot IDs**, including **486 original records in 2021 alone**. The extra four identities may reflect source QC exclusions or differences in study/figure subsamples, but **the published data do not identify the reason through these original headers alone**. Do not assert four corrupt plots or delete them posthoc; reconstruction of the authors' actual filtering rules from the original supplied R script and README would be needed before using 482 as a denominator for new analysis. Source year rows are repeated and incomplete; don't divide by four and claim 482 full balanced plots.

**Additional source limitations:** Neither original main H1H2 nor H3 table contains named source tree species or original directly measured SLA/N/WD per plot. `TREE_R` reports original tree-species richness only, not recoverable named taxa. Figshare offers an additional Fig5 source file, README and R code, not an original local species×plot trait dataset in the verified tabular manifest. The authors' reported **38,088 original trees** are not individual input rows in these Excel sources. Therefore original **K→FD→AGB data remain HOLD** and the **two original sites** are far below the five independent experimental location threshold even with four years.

Verified [GitHub Actions #44302830945 SUCCESS](https://github.com/zuizui0223/turnover/actions/runs/44302830945); original public nonraw artifact #14426223817 digest `sha256:1859f7f1b0b1f34c40e504c36530c31ea7af149eebeca4fd7ec7316eab022942`. Permanent file `results/befchina_original_2025_H1H2_H3_plotyear_grain_source_v0_2.json`. No original copyrighted source binary, plot IDs or original AGB tree values committed.

## 3. Integrated biological design interpretation

The two independent source checks give a concrete explanation for why trait names, phylogenetic signal and functional diversity cannot simply be transported across existing public biomass studies:

1. **Source selection and covariate confounding:** Many nominal "independent" plot observations share a country, site, manipulation or forest successional stage. In the African source **all 104 young plots share one country**, making a five-domain stage-controlled prospective transport model statistically unidentified. **This is a *data-design* finding**, not a previously established evolutionary memory ecology mechanism.
2. **Original data granularity:** African published FD/CWM have already collapsed species into plot indices and lost all named source trait lines. BEF-China public source has annual plot AGB/canopy but no named source leaf traits. Neither permits a direct matched family Blomberg K, nor even reconstructs fully observed original species-level FD from public source. No artificial species-trait reconstruction.
3. **Published source denominator:** BEF-China main paper reports 482 plots while raw H1H2 has 486 distinct IDs; original filters need reproduction before new source effect estimates. This is a field inclusion/processing audit, not confirmed biological bias or dataset error.
4. **No direct K→FD→mass test:** reported African total 207 species and BEF-China total 40 species fall short of the frozen original ≥240 independently sampled species across 12 nonoverlapping families, even before taxon-level original identities are unavailable. These sources cannot be declared causal K evidence by looking at published CWM/FD or PD proxies.

**Decision:** preserve these source-only scientific findings in a separate Draft PR from `main`, and **do not run the cancelled five-country FDis biomass effect or a two-site BEF-China macro-generalization after either frozen gate fails**. A new independently source-qualified region/taxon original dataset (or genuinely new source data for undercovered young forests outside Ethiopia and detailed tree traits) is required for the original hypothesis. Historic BIODEPTH/TreeDivNet/sPlotOpen/NEON source HOLD remains unchanged; no new ecological effect coefficients, p-values, variable selection or source subgroup rescue were computed.
