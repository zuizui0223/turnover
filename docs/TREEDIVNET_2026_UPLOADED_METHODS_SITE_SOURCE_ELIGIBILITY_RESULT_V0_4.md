# TreeDivNet 2026 uploaded Methods S1–S3: site-resolved source eligibility

**Verified 2026-11-16**: original Figshare DS1/DS2 source (MD5-pinned 363/689 original rows), the user-supplied 15-page publisher original Methods S1/S2/S3 document (SHA256 `6e422d5bbe685e00b045634137c150e8a6824e8dd4c6f88da43beae2f2ee9ddd`), and a frozen **source-only** original-site cohort qualification script. No original raw biological row, figure, source DOCX binary, sample ID, or plot biomass value is committed; no new trait–biomass, phylogenetic PD, K or causal coefficient is calculated.

## Source-only original trait and woody support by experimental design

Preliminary original source eligibility means an original DS1 `site×block×plot` matched to original DS2 `site×block×plot×species`, with finite nonnegative original **DS1 woody biomass** and **≥2 different DS2 source species positive on one identical SLA, LNCM or WD axis**. This is not an assertion of aligned field sampling years or independently identified individual tree sample records.

| Source-qualified study population | Eligible original plots | Named original study sites | Sites with ≥8 eligible original plots | Distinct original source species carrying positive trait |
| --- | ---: | ---: | ---: | ---: |
| All original 11 studies | **186** | **11** | 10 | **38** |
| **Exclude ECOLINK Uppsala** (Methods S1 genetic-variety manipulation; Methods S2 cumulative three-year coppice harvest woody response) | **153** | **10** | **9** | **34** |
| Also exclude **MataDIV** as a deliberately separate *fertilization/design sensitivity* (Methods S1, only fertilized source stands) | **143** | **9** | **8** | **28** |

The original **328** exact DS1×DS2 matched plots are unchanged before the source-design restrictions. Site ECOLINK Uppsala contributes **33** of the original 186 eligible source plots. MataDIV contributes **10** additional original eligible plots. Original source site labels match `ECOLINK_Uppsala` and `MataDIV` unambiguously.

Within the ECOLINK-excluded numerical cohort, SLA original ≥2-species source support is **132 plots** (original 165), LNCM **137** (original 170), WD remains **77** (original 77). The ECOLINK source-specific difference is consistent with genotype-focused willow plots supplying some SLA/N observations but no additional ≥2-distinct-species wood-density case for the earlier same-axis cohort rule; this is source coverage, **not** an ecological inference.

With MataDIV also excluded, SLA support is **122 plots**, LNCM **127 plots**, WD **77 plots**.

### Per-site eligible source plot counts (before vs after the fixed source-design screen)

| Named original experiment | ≥2 same-axis source species + DS1 woody plots | Source-design label from uploaded Methods |
| --- | ---: | --- |
| B-Tree | 9 | Other original source study |
| BIOTREE_Kaltenborn | 8 | Other original source study |
| **ECOLINK_Uppsala** | **33** | **GENOTYPE manipulation + cumulative 3-year-cycle coppice harvesting** |
| FORBIO_Gedinne | 12 | Other original source study |
| FORBIO_Hechtel-Eksel | 12 | Other original source study |
| FORBIO_Zedelgem | 12 | Other original source study |
| IDENT_Freiburg | 12 | Periodic woody non-target removal (Methods S2) |
| IDENT_Macomer | 12 | Distinct upper-crown leaf sampling (Methods S3) |
| **MataDIV** | **10** | All source stands included were fertilized (Methods S1) |
| MyDiv | 60 | Other original source study |
| ORPHEE | 6 | Some Quercus root-collar diameters inferred where originally missing (Methods S2) |

The sites listed as "other original source study" are **not** presumed methodologically identical or year-aligned; the uploaded Methods only identified the particular differences written above. In particular, 60 of the 153 source eligible post-ECOLINK plots are from MyDiv, so site holdout and site-equal inference must not treat all source plots as geographically independent replicates.

## Fixed numerical source-design thresholds still pass

The prior original source-only data gate requires ≥80 original plots with ≥2 same-axis positive source species and independent original DS1 woody response, ≥5 original study sites each with ≥8 eligible plots, and ≥20 original source trait species.

- Excluding ECOLINK: **153 eligible plots, 9 sites with ≥8, 34 source taxa → numeric coverage PASS.**
- Excluding ECOLINK + MataDIV: **143 eligible plots, 8 sites with ≥8, 28 source taxa → numeric coverage PASS.**
- **None** of these counts authorize a new woody biomass regression, causal biodiversity effect, or plot-specific original measured trait–biomass temporal match. The frozen source chronology and provenance checks still do not pass.

If a future independent taxonomic diversity and standing woody stock test is qualified by original measurement dates and source accounting, **ECOLINK cannot be included as a tree-species richness manipulation** or as a single-year standing woody-stock response. MataDIV could be retained as a **fertilized forestry context** but not represented as an unfertilized control; the 143-plot restricted cohort is a prespecified source-only sensitivity.

## Remaining requirements before opening new ecological results

1. The actual original **Supplementary Table S1** source field observations (trait and tree-biomass measurement years / study-site timing). Figure S2's ECOLINK 2022 diameter–height plot is **not a study-wide observation date**.
2. The actual original **Supplementary Table S3** species×site allometric formulae and, if needed, the authors' data-processing explanation for why **321/328** source plots satisfy `DS1 woody = mean(DS2 species woody)` while seven do not. Do not derive a causal biological species mass contribution from that mathematical identity.
3. Individual tree/leaf sample IDs only if an **individual-row provenance claim** is required. Uploaded Methods S3 *already supports* per-plot species nutrient averaging as the original study protocol, but does not supply individual identifiers.
4. A separate study design that does not take TreeDivNet Jensen 2026's own statistically significant published mixture–wood/litterfall and SLA/LNCA differences as an **independent new positive replication**.

A source-only positive qualification is not a 12-family×20-species plant evolutionary K test: 34 original species after ECOLINK exclusion are far below the ≥240 required for 12 disjoint family-by-trait systems with ≥20 species each.

## Reproducible original-source proof

- Frozen before source cohorts opened: `docs/TREEDIVNET_UPLOADED_METHODS_SITE_ELIGIBILITY_GATE_20261116_V0_4.md`.
- Source-pinned original Figshare script: `scripts/source/audit_treedivnet_s1_s2_site_eligibility_v0_4.py`.
- **Original DS1/DS2 source replay [GitHub Actions #43875714360](https://github.com/zuizui0223/turnover/actions/runs/43875714360) SUCCESS.** Source cohort artifact #14229702034, digest `sha256:2b0771a9b9222f8f7973802cb9830c278cbc9012ce310f826384fe6df5f5c869`.
- Permanent machine-readable exact source counts: `results/treedivnet_2026_methods_s1_s2_site_cohort_eligibility_v0_4.json`; upload-source bibliographic evidence `results/treedivnet_2026_user_supplied_methods_s1_s3_source_audit_v0_4.json`.
- No old source results overwritten, none of the historical strict BIEN/sPlotOpen, BIODEPTH or NEON source HOLD restrictions removed, and `main` unchanged. PR #55 remains unmerged Draft.
