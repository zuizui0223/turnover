# TreeDivNet Jensen 2026: supplementary methods and original README crosswalk

**Source-only preflight fixed 2026-11-16** before opening any supplementary data or a new original-response model. Based on the prior exact original DS1×DS2 328-plot join, 186 plots with ≥2 same-trait species plus valid DS1 woody biomass, and the established 321/328 numerical mean identity between DS2 species-row woody values and DS1 plot-level woody values. This is not a new positive diversity–biomass result, K or FD analysis.

## Target sources and safe exact-match rule

- **Original Figshare public README.txt**, immutable file ID 61014400, 8130 bytes and verified MD5 `8fd3551d0a2b69fb9dca54b7cdbca422`. Read source definitions, study-year/measurement-year statements, data tables DS1/DS2 and normalization/area/biomass semantics, not original study outcome associations. This file is already public and source-verified in PR #54.
- Original publisher Jensen et al. 2026, DOI `10.1111/1365-2435.70320`, Wiley **Supporting Information**:
  - `fec70320-sup-0001-FigureS1-S12-TableS5-S6.docx` (Methods S1–S3, especially Methods S2 allometry and S3 leaf sampling);
  - `fec70320-sup-0002-TableS1.xlsx` (11 study-site characteristics / potentially sampling timing);
  - `fec70320-sup-0004-TableS3.xlsx` (study-specific tree allometric equations).
- Candidate URLs under official Wiley / British Ecological Society Wiley hostname are **access hypotheses**, not confirmed original file links. Probe with bounded GET only. Accept file bytes as source only after HTTP 200, canonical HTTPS Wiley hostname, PK-ZIP magic and ZIP validation; otherwise report exact `PUBLISHER_SUPPLEMENT_ACCESS_HOLD` and do not invent publisher file contents. Never circumvent paywalls or access authentication.
- Source docs are public, but original individual tree/source plot rows must not be committed.

## Fixed source decision questions

1. **Chronology:** do original sources give **per-site biomass tree-diameter measurement year** and **per-site SLA/LNCM/WD trait sampling year**? Extract year tokens only for precisely labelled `biomass` vs `trait` site/source columns and explicitly documented Methods S2/S3. A generic experiment establishment year or article publication date is not a measured date. Admit each of 11 sites only with independently checked original same-site source years separated ≤2 calendar years; no post-result relaxing.
2. **Original allometric response scaling:** does README/Methods S2 directly explain why 321/328 original source plots satisfy `DS1.biomass_woody = mean(DS2 species-row biomass_woody)`, while `sum` matches only 135/328? Need an explicit source formula or original spreadsheet processing/response definition, not infer a species-share rule from observed numerical equality.
3. **Individual trait provenance:** do original Methods S3 or Table S2 trace DS2 `site×plot×species` SLA/N/WD values to within-plot measured leaves / wood, versus site monoculture and external FDis reference values? Preserve distinction from *paper's published §2.5 statement* that 283 original site-monoculture and 17 external substitutions were used **only for FDis**, while other analysis used measured traits. This supports study methods, but is not automatically a per-DS2-row measurement audit.

## Outcomes and safe stopping

- `TIMING_SOURCE_PASS` only if 11-sites year/measurement-source crosswalk is clearly supported for an identifiable eligible multi-site sample and exact plot-season identity is not misrepresented.
- `BIOMASS_CONVENTION_SOURCE_PASS` only when explicit study formula/definition explains DS2 species rows relative to DS1 stand response; otherwise `BIOMASS_SCALING_HOLD`, regardless of numerical 321/328 identity.
- `ROW_PROVENANCE_SOURCE_PASS` only if original individual IDs or source lineage is available; otherwise retain `INDIVIDUAL_SOURCE_PROVENANCE_HOLD`.
- A successful Wiley file download may support a *separate* new future outcome-frozen original 186-plot experiment-holdout analysis; it does not itself establish new ecological associations or identify causal traits.
- If publisher access fails, preserve original data geometry PASS but source-year/scale HOLD; no new K→FD→woody biomass inference. The global original 201-family BIEN/sPlotOpen and earlier BIODEPTH exact-richness site gates remain HOLD.
