# TreeDivNet 2026 original DS1 × DS2: verified 328 plot joins, source woody response grain and trait provenance

**Checkpoint 2026-11-16, after three independent exact-source GitHub Actions source-only audits (Draft PR #55).** This is an *original-source data-quality finding*, not new inference that species functional diversity raises biomass. Historic BIODEPTH, BIEN, and NEON original study gates are unchanged.

## Immutable original sources, published data meaning

Original Figshare [10.6084/m9.figshare.31026004.v1](https://doi.org/10.6084/m9.figshare.31026004) (Jensen et al. 2026, [10.1111/1365-2435.70320](https://doi.org/10.1111/1365-2435.70320)), official MD5-pinned README.txt, DS1.xlsx and DS2.xlsx:
- DS1 original **363** nonheader source rows: `site, block, plot, treatment, species_richness, species_composition, biomass_woody` and plot CWM fields.
- DS2 original **689** nonheader source rows: same original site/block/plot/treatment/composition keys with `species, biomass_woody, SLA, WD, LNCM, LNCA, LPCM`.
- DS3 original 224 records include published NDE/FDis (derived already; no new original field-trait measurements). Not used in this source-gate join.
- Aboveground woody **standing** biomass is original allometric dry mass (Mg ha−1), **not** litterfall flux, uniform NPP, or total vegetation+soil carbon.

## Source-original exact join, without statistical outcome use

| Source check | Verified from immutable original files |
| --- | ---: |
| DS1 unique original `site×block×plot` keys | **363**; 0 duplicate/missing |
| DS2 unique original `site×block×plot` keys | **340**; 0 duplicate site×block×plot×species, 0 missing |
| Original DS1/DS2 joined plots | **328**, across 11 study sites |
| DS1 plots with no matching DS2 species values | 35 |
| DS2 plot identities with no DS1 response row | 12 |
| Exact original treatment, species richness, species-composition labels | **328/328** agree |
| DS1 reported richness equals distinct DS2 species-row count | **322/328** |
| Joined plots with valid nonnegative DS1 woody biomass | **328** |
| Joined plots with ≥2 species positive on at least one identical leaf/wood trait axis, plus numeric woody biomass | **186**, in ten sites with ≥8 eligible plots |
| Distinct source species observed with positive trait values among the 186 plots | **38** |
| Matched plots with ≥2 positive SLA species | 165 |
| Matched plots with ≥2 positive LNCM species | 170 |
| Matched plots with ≥2 positive WD species | 77 |

The source data-quality geometry gate **PASSES**, but this does not imply independent taxonomic breadth for original global lineage K. Counts are not 186 independent sites or a separate replication of the published authors' biomass result.

## Crucial response-grain identity: never sum species-row `biomass_woody`

The exact original source row check finds:
- **328** original joined plots with valid DS1 and corresponding DS2 woody values, on **665** matched DS2 species rows.
- DS2 species row woody equals the DS1 stand woody on **only 135 of 665 rows** (mostly monocultures). Hence the DS2 woody column is *not* simply a copy of the stand response on every species row.
- For **321/328 plots (97.87%)**, however, the **arithmetic mean** of DS2 woody values equals the DS1 woody stand response, numerical tolerance 1e−8. For only **135/328** does the **sum** of species-row values equal the stand response.
- **Seven** original joined plots do not satisfy the exact mean identity; **six of those seven** also disagree between DS1 recorded richness and the number of DS2 rows. Two residual cases are within 1% of the identity. No original plot IDs, source woody values, or species rows are committed.
- Thus, a naive `sum(DS2.biomass_woody)` would often inflate the plot response by **the number of species rows**, producing an algebraic richness-associated bias without any genuine ecological mechanism. This last bias statement is a *mathematical risk*, not a newly estimated richness–biomass regression.

The exact meaning of the species-row normalized woody mass scale is **not established solely by published DS1/DS2 headers**: it could reflect area/density scaling or a study data transformation. Do **not** use a species-row total/mean to replace source response by convenience or claim a source data error without the original author-specific scaling definition. A correct original biomass analysis must use **one DS1 response per site×block×plot**, never repeated as an independent outcome for each species, and must audit the seven source discrepancies before asserting exact species-plot hierarchy.

## Trait measurement provenance: distinguish DS2 from derived FDis

The original 2026 paper's §2.3 describes field-measured SLA, leaf nutrients, wood density and height at species-per-plot level, aggregated for the original analyses. §2.5 explicitly restricts **site-monoculture trait substitution (283 site-specific values) and 17 literature/TRY or global-WD substituted values to the calculation of *FDis***; the paper says the other functional trait and biomass analyses used measured values. Thus, it would be incorrect to claim *every DS2 species–plot trait value was imputed* merely because paper FDis used external reference values.

**Yet** the distributed DS2 workbook contains no original tree ID, leaf sample ID, measurement provenance flags, or original sampling year/date, and DS1 has no response measurement year/date. Hence:
- Author-study-method **support for species×plot directly measured aggregate trait values: present**.
- **Individual record-level measurement identity (and any site exceptions): not traceable in DS2**.
- **Within-plot original trait vs biomass measurement time alignment (e.g., ≤2 years): NOT independently verified**.
- Published diversity–FDis–biomass coefficients are the *authors' analysis*, not independent confirmation; new study would need truly different model estimands and strong source/temporal controls.

Source trait fields are often absent as **nonnumeric text codes** rather than biologically meaningful zero; source-only positive numeric rows: SLA 573/689, LNCM 594/689, LNCA 572/689, LPCM 511/689, WD 303/689. These are trait-record completeness counts, not trait effects. Never substitute 0 for missing trait measurements.

## Scientific decision

**Status: SOURCE JOIN GEOMETRY PASS; AUTHOR-METHOD SPECIES-PLOT TRAITS SUPPORTED; INDIVIDUAL PROVENANCE AND YEAR MATCH HOLD.**

The original source has adequate geometry for a *potential* study of whether the source's observed trait composition and species mixing predict original woody standing biomass across study experiments, but the same authors already published positive mixing–woody-mass and FDis effects. No genuinely independent trait–biomass effect was estimated in this audit, and with only 40 original species it is impossible to estimate a 12-family×20-species trait-specific K study from these trees alone.

Do **not** relax prior source/year standards after seeing data. The next scientific action is to inspect original site-specific measurement chronology (authors' Methods S2/S3 and Table S1) and provenance for plot measurements, and separately verify the original biomass scaling hierarchy. Only after authorization/source PASS could one freeze a **novel** leave-whole-experiment-out species-trait/stand biomass analysis using the 186 potential plots, with original site/block grouping and prespecified trait axis.

Do not infer ecological positive association from source data success. Previous BIODEPTH repeated-cohort results are closed; no new biological regression, extra BD source subgroup tuning or global K claim.

## Exact reproducible evidence

- Original DS1–DS2 source plot join [GitHub Actions #43862053465](https://github.com/zuizui0223/turnover/actions/runs/43862053465) SUCCESS, aggregate artifact #14223078390, digest `sha256:4f065e370b308e1f7d323f7a08566512a1de446eb03e4d5222234b7bf19a883a`.
- Original trait missingness and woody aggregation QA [#43862840694](https://github.com/zuizui0223/turnover/actions/runs/43862840694) SUCCESS; artifact #14223472403, digest `sha256:bd75ad1cbcd2c01cb5dc4a80f084d808b09d96159b32b8964b149907072fa7ac`.
- Independent source original row identity audit [#43863638593](https://github.com/zuizui0223/turnover/actions/runs/43863638593) SUCCESS; artifact #14224687418, digest `sha256:346379a71c2c8c1c4ac2148f0c8614f293b9182697a9e333b1be37f8ca25c8a3`.
- Original nonraw machine-checkable combined outputs `results/treedivnet_2026_original_DS1_DS2_plot_source_gate_v0_2.json`, scripts in `scripts/source/` and source-first frozen contract `docs/TREEDIVNET_DS1_DS2_ORIGINAL_SOURCE_JOIN_GATE_V0_1.md`.

All changes are stacked as Draft PR #55 on the original-data source-only Draft PR #54; `main` and historical ecological outcomes unchanged.
