# TreeDivNet 2026: original Methods S1–S3 recovered from user-uploaded 15-page publisher supplement

**Source checked 2026-11-16.** Original file `fec70320-sup-0001-figures1-s12-tables5-s6.docx`, **1,170,063 bytes**, SHA256 `6e422d5bbe685e00b045634137c150e8a6824e8dd4c6f88da43beae2f2ee9ddd`. Opened and inspected with python-docx; original 15 pages, 12 embedded figures and the paper's Tables S5/S6. Source article Jensen et al. 2026 `10.1111/1365-2435.70320`. The actual binary came from the user's attached file, **not from the earlier HTTP 403 Wiley downloads** and is **not redistributed or uploaded** to this repository. Extracted *source statements* are recorded as short summaries and controlled flags in `results/treedivnet_2026_user_supplied_methods_s1_s3_source_audit_v0_4.json`.

## What the original supplementary Methods actually establish

| Original section | Location | New source-supported fact | Consequence |
| --- | --- | --- | --- |
| Methods S1 | p.15 | **ECOLINK Uppsala** manipulates genotype/variety diversity, **not tree species diversity**. | Do not classify ECOLINK as a replicated manipulated tree-species-diversity response. |
| Methods S1 | p.15 | Study excluded fertilization/irrigation manipulation at most sites; **MataDIV Brazil included exclusively fertilized plots**. | Fertilized environment is the sampled design, not an unfertilized reference. |
| Methods S2 | p.15 | **ECOLINK** willow coppice harvested in **3-year cycles**, and reported accumulated woody mass combines harvest-year biomasses; allometry separately fitted per harvest except first harvest weighed manually. | ECOLINK original mass is **cumulative harvest biomass**, unlike an ordinary single standing-stock estimate. Do not pool without explicitly modelling response semantics and time. |
| Methods S2 | p.15 | At **ORPHEE**, some Quercus root-collar diameters derived from DBH or height when DBH missing. | DBH-derived allometric response partly predicted rather than direct tree-diameter measured; record method heterogeneity. |
| Methods S2 | p.15 | At **IDENT Freiburg**, Rubus and non-target woody seedlings were removed; non-woody understory retained. | Site-specific weeding/vegetation filter; cannot attribute all differences to original woody species richness alone. |
| Methods S3 | p.15 | **IDENT Macomer and IDENT Freiburg** sampled leaves from tree crown top; others from across the crown; leaf chemistry differs among sites. | A cross-experiment leaf trait comparison requires method/site adjustment. |
| Methods S3 | p.15 | Nutrient concentration values are averaged at original **species × plot**, then within plots. Author defines `LNCA=LNCM×(1/SLA)`. | Supports the *published site×plot species mean protocol*; does **not** provide individual leaf IDs or original sampling dates. |
| Figure S2 | p.3 | ECOLINK diameter–height calibration shown for **2022**. | Does **not** identify original tree biomass and original SLA/LNCM/WD observation year at 11 sites. |
| Figure S4 | p.5 | Published FDis source used **283 site-monoculture in situ averages + 17 external database/literature values**. | Already-published FDis has distinct provenance from directly recorded plot×species traits; no inferential portability without a new study. |

**Importantly, this recovered source is not Supplementary Tables S1, S2 or S3.** It contains Figs S1–S12, Tables S5–S6, and Methods S1–S3. The original **Table S1 (site/year info)** and **Table S3 (per-species/site allometries)** are separate files. The original binary resolves the historical *publisher access limitation for Methods*, but **not** all original methodological evidence requirements.

## Existing published authors' statistical effects, not new results

Original Table S5 (p.14) compares observed versus expected mixture biomass components:

| Author test | Original chi-squared | Original p |
| --- | ---: | ---: |
| Woody biomass | **18.441** | **<0.001** |
| Litterfall biomass | **29.562** | **<0.001** |
| Understory biomass | 1.051 | 0.305 |

These ANOVAs show a statistical difference between expected and observed mixtures for wood and litterfall but **do not independently identify the sign from a chi-squared value**, and this existing Jensen publication is **not a novel independent reanalysis**.

Original Table S6 (p.14) shows that *unweighted* SLA (`χ²=23.119, p<0.001`), LAI (`χ²=12.168, p<0.001`), and LNCA (`χ²=32.186, p<0.001`) were statistically different expected-versus-observed, while basal-area-weighted LNCA still differs (`χ²=7.481, p=.006`). Basal-area-weighted SLA (`χ²=.982, p=.322`) and wood density (weighted `χ²=.005, p=.945`) did not. **Weighting choice is substantively important**, but these are **original authors' tests, not new effects computed in turnover**.

Figure S11 (p.12) is the authors' **six-experiment** SEM (Fisher C=6.58, p=.584), which is **not** 11 separate experiment holdout replications and is **not** a family-specific Blomberg K→FD→biomass model.

## Now-qualified and still-blocked original research steps

**Confirmed:** Source joining remains 328 exact original DS1×DS2 plots across 11 experiments; original +woody trait subset is 186 source plots across 10 eligible experimental sites (the prior original-gate result). The original supplemental Methods S3 does **upgrade the methods evidence** for leaf nutrients being measured and averaged for each plot×species, as described by original authors.

**Not confirmed:** No individual leaf/tree sample IDs, no per-site trait-and-biomass original measured year table, and no explicit `DS1.biomass_woody ← DS2.biomass_woody` normalization factor. Prior original 321/328 arithmetic mean identities and seven discrepancies remain unmodified. ECOLINK's accumulating coppice years require a **source design restriction** in any common single-standing-stock woody mass study; genotype manipulation also defeats naive tree-species richness experiment contrasts.

**New source-only cohort test** (frozen before site counts): `docs/TREEDIVNET_UPLOADED_METHODS_SITE_ELIGIBILITY_GATE_20261116_V0_4.md`. Computes the original 186-source-plot population and the exact ECOLINK exclusion and MataDIV sensitivity, without any biological effects or new coefficients. Even a structural PASS does not bypass original `TEMPORAL_ALIGNMENT_HOLD`, `INDIVIDUAL_SOURCE_LINEAGE_HOLD` or `WOODY_SOURCE_NORMALIZATION_HOLD`.

Original signed Figshare public files remain original SHA/MD5 pinned; this user-uploaded DOCX was inspected locally and its SHA256 recorded. No document binary, figures, copied tables or raw biological observations committed. The earlier biological source gates in BIODEPTH, global BIEN and NEON remain HOLD, and PR #55 is Draft/unmerged.
