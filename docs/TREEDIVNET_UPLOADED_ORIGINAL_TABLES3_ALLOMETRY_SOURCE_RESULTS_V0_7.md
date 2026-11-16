# Uploaded original Table S3 — TreeDivNet allometric biomass response audit (2026-11-17 JST)

**Uploaded source inspected:** `fec70320-sup-0004-tables3.xlsx`, original **21,729 bytes**, SHA256 `c6458fa8f381090a77e529530d5cdb55d44ff3f1fc6e652f61ab2cb29b75d15b`. Directly imported with `artifact_tool` from the user-provided file in the current conversation. Original sheet `Table S3` used A1:M92, including 77 genuine original site×species×inventory-year **allometric formula or actual-harvest-weight entries**, 12 trailing glossary/reference lines, and a separate caption. The original XLSX binary is **not uploaded to GitHub**. The exact extracted aggregate provenance was saved in `results/treedivnet_uploaded_original_TableS3_allometry_source_audit_v0_7.json`. This source does NOT include original individual-tree diameter or plot rows.

## Direct-source facts, no ecological outcome fitting

| Source dimension | Original uploaded Table S3 | Interpretation |
| --- | ---: | --- |
| Sites with original allometries/weights | **11/11** | Every original study site has a source woody-response estimation description |
| Real allometric + actual-weighed rows | **77** | **NOT 77 independent species or 77 independent plots** |
| Unique site×species keys | **63** | Willow varieties repeat harvest years, and some species have two biomass components |
| Unique site×species×inventory-year keys | **71** | Six IDENT Freiburg species have two equations (stem vs branch) each |
| DBH-based model rows | 20 | Diameter at breast height; site/response-specific model |
| RCD-based model rows | 42 | Root-collar diameter, measured at 5, 10 or 20 cm for different sites |
| BA-only model rows | 6 | Basal-area source model; site-specific original coefficients |
| BA + tree height H + wood density WD model rows | **5** | MataDIV mass incorporates WD as an **input**, see below |
| Actual directly weighed harvest rows | 4 | ECOLINK original 2017 coppice first harvest |
| `ln(Y)` regressions | 25 | Published correction factors matter |
| Direct `Y=` equations | 48 | Other source biomass component models |
| Original proxy allometric equations | **7** | Generic or other species equation substituted, not identical taxon fit |
| Correction factor `CF` given numerically | 19 | Relevant for corrected retransformation of log-biomass |
| One CF given only symbolically | **1** | MataDIV palm `exp(RSE2 / 2)`, numerical RSE unavailable in Table S3 |

Original equation output forms also differ: **58 rows marked total aboveground woody biomass, 7 stem+branch, 6 stem, 6 branch**. For six species at **IDENT Freiburg**, there are explicitly separate stem and branch log-equations: use both parts in source-level tree woody reconstruction, rather than treating 12 equations as 12 independent observations. Source output type `stem+branch` must not be confused with an unqualified whole-tree carbon value.

For 35 source equations with an explicit numerical calibration diameter range, none of the *reported site-mean* diameters fell outside that stated numeric range. This is only a mean-value geometry check, **not** proof that every individual original tree was within the equation's calibrated diameter range; individual DBH/RCD values are absent.

## IMPORTANT NEW MODEL-OUTCOME DEPENDENCE: measured WD is a direct woody biomass allometry input at MataDIV

Of **six original MataDIV tree taxa**, **five** use the same published original allometric formula containing `ln(WD)`, with WD noted `from site measurements` in Table S3. The original published coefficients include a direct WD term of **1.022** alongside `ln(BA)` and `ln(H)`:

`ln(Y) = 6.039 + 0.945 ln(BA) + 0.961 ln(H) + 1.022 ln(WD)`

The sixth taxon is a palm and uses a separate DBH model, labelled a **generic palm proxy** with symbolic correction factor `exp(RSE2 / 2)`; that source sheet does not contain a numeric RSE term.

**Inference consequence:** At MataDIV, the *response* `biomass_woody` is at least partly **mathematically constructed from wood density**. A naive regression of source woody biomass on species/community WD (or WD-containing FD) is **not an independent ecological test of WD influencing actual productivity**; some association can arise from the source allometry itself. This does **not** establish direct mathematical circularity for the separate SLA+LNCM two-trait features. However the outcome still uses a trait-derived input and shares an observational method with site-specific WD measurements, which should be documented if MataDIV is retained for SLA/LNCM.

The previously frozen **MataDIV-EXCLUDED** original source time-qualified two-trait SLA+LNCM cohort still has **107 unique original plots, ≥8 plots in five original experimental sites, and 26 original trait-bearing species**, satisfying source-only numeric support. That is a **source-derived sensitivity cohort**, not permission to report a positive or negative biomass relation. Main source timing cohort is 117 original SLA+LNCM plots (site-matched inventory years and two complete original species rows) after ECOLINK exclusion, with 10 MataDIV source plots.

## Other necessary allometry cautions

- Seven explicit **proxy equations** across FORBIO Gedinne (larch), FORBIO Hechtel-Eksel (generic conifer), MataDIV (palm), MyDiv (generic broadleaf / related linden), and ORPHEE (two generic broadleaf `Quercus`) introduce taxon/source model heterogeneity. Do not claim complete independent directly calibrated allometry for all 63 site×species pairs.
- At ORPHEE, three Quercus entries note **DBH converted to RCD**. The row-level input diameter conversion rule is not shown; do not invent it.
- B-Tree has two source expressions with apparently ambiguous exponential grouping (written as an `e^` term followed by `×DBH`). They should be transcribed as original source expressions and **not** numerically evaluated as a single specific mathematical parsing without original authors' clarification.
- `CF` correction factors are numeric for 19 log-model rows, mostly `n.a.` elsewhere; the source palm's `exp(RSE2 /2)` lacks a reported numeric `RSE`. Reconstructing each individual woody mass from Table S3 alone would silently require assumptions about missing residual-error terms, predictor units, tree diameters, and plot area.

## Original year check against uploaded Table S1: exact **11/11 study sites**

Table S3 original inventory years agree **exactly with uploaded Table S1 woody-biomass inventory years** for all eleven sites:
- BIOTREE Kaltenborn 2019; B-Tree 2021; FORBIO Gedinne 2021; Hechtel-Eksel 2019; Zedelgem 2018;
- IDENT Freiburg 2021; IDENT Macomer 2022; MataDIV 2024; MyDiv 2021; ORPHEE 2021;
- ECOLINK Uppsala has **2017 (actual weighed first harvest), 2020 and 2023 (separate allometric estimates)**.

This is strong **source provenance consistency for woody inventory years**, but is not an exact original leaf-sampling-date match or an ecological response test. The earlier 117 SLA+LNCM source plot cohort relied on a site-level ±2-year inventory-year rule; original individual sample IDs remain undisclosed.

## Does Table S3 resolve 321/328 DS1-DS2 woody aggregation?

**NO.** It specifies tree/species allometric **formulae** and response components but does **not** provide original per-individual DBH/RCD/BA/H measurements, tree counts, plot area/ha scaling, DS2 species-column transformation or a reproducible table of original site×block×plot×species mass contributions. Therefore it cannot establish why in the separately archived original source data, `DS1 plot biomass_woody = mean(DS2 woody species rows)` on **321/328** plots, but not the other 7. Earlier original Table S3 access was HTTP403, now the *file access* is resolved by the user upload; **formula-based DS2→DS1 provenance remains HOLD**.

For any future ecological outcome modelling, use **one unique original DS1 stand woody response per original site×block×plot**, never multiply it by number of source species rows or sum DS2 woody without verified original data-processing semantics. A research claim of *independently measured local tree biomass* is stronger than the original source permits: response is partly **allometrically modelled** and site equations differ.

## Current research decision

- Source-only **data-geometry PASS**: original DS1/DS2 328 exact joined plots; after original ECOLINK genetic/coppice design exclusion and measured-year gate, 141 have a supported single-axis trait/woody time interval; **117** original plots have **two same-species complete SLA + LNCM records** within ±2 original study inventory years; excluding MataDIV still gives **107**.
- **Source allometry metadata/year PASS**: all 11 site/year pairs, species-specific (or explicitly proxied) equation inputs, separate source body components, WD input documented.
- **Independent biological WD predictor vs MataDIV estimated woody stock: DIRECT MATHEMATICAL INPUT RISK**. Do not treat this association as independent biology.
- **Still HOLD**: exact source original `DS2 woody ↔ DS1 stand woody` aggregation in 7 source plots; original individual diameter, tree sample identity, response/leaf exact day and whether pooled numerical source-date windows identify identical ecological growing seasons.
- This Table S3 supplementary access does **not by itself authorize a new FD/biomass regression** under the earlier stricter individual-measurement/provenance gate. However the separate two-trait source-only design is now better qualified if the remaining response normalization/source ID interpretation is independently addressed.
- No family-specific trait evolutionary-memory K (historical BIEN/AusTraits) is measured on these trees, and no new original functional diversity or phylogenetic breadth effect was estimated. Existing historical original global BIEN/sPlotOpen, BIODEPTH and NEON source gates stay HOLD.

## Audit sources and reproducibility

- Source original Table S3 locally inspected with `artifact_tool` from the exact uploaded XLSX and original byte SHA256. **GitHub CI cannot re-open the attachment binary** unless a new original copy is supplied independently (not done here); its metadata integrity tests compare the derived source ledger against the independently source-verified Table S1 chronology and the prior original Figshare source joins.
- Derived machine-readable source audit: `results/treedivnet_uploaded_original_TableS3_allometry_source_audit_v0_7.json`.
- Prior time- and trait-qualified source results: `results/treedivnet_original_TableS1_woody_trait_gap2_site_source_v0_6.json` and `results/treedivnet_original_TableS1_multiaxis_year_supported_plots_v0_6.json`.
- Original uploaded publication Methods S1/S2/S3: `results/treedivnet_2026_user_supplied_methods_s1_s3_source_audit_v0_4.json`; original source-only Figshare plot join: `results/treedivnet_2026_original_DS1_DS2_plot_source_gate_v0_2.json`.
- Draft PR #56 stacked above source PR #55, no original copyrighted XLSX, original numerical species/allometry raw table or file binary committed; `main` unchanged.
