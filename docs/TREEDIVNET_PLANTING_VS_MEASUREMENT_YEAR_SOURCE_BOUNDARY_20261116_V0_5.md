# TreeDivNet source chronology v0.5 — what the 11-site public Table 1 can and cannot resolve

**Source crosswalk completed 2026-11-16**: Jensen et al. 2026 *Functional Ecology* original public [article Table 1](https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2435.70320) and original Figshare DS1/DS2 source-only eligibility counts archived in `results/treedivnet_2026_methods_s1_s2_site_cohort_eligibility_v0_4.json`. Additional original Methods S1–S3 came from the separately uploaded 15-page DOCX, NOT from the published supplementary Table S1 or Table S3 XLSX files. All earlier source-only numerical estimates, historical BIODEPTH analyses and `main` remain unchanged.

## Exact original Table 1 site *planting year* crosswalk

| Original study site | Original published planting year | Original plots with ≥2 source species positive on one identical SLA/LNCM/WD axis and valid DS1 woody |
| --- | ---: | ---: |
| B-Tree | 2013 | 9 |
| BIOTREE Kaltenborn | 2004 | 8 |
| ECOLINK Uppsala | 2014 | 33 |
| FORBIO Gedinne | 2010 | 12 |
| FORBIO Hechtel-Eksel | 2012 | 12 |
| FORBIO Zedelgem | 2009 | 12 |
| IDENT Freiburg | 2013 | 12 |
| IDENT Macomer | 2014 | 12 |
| MataDIV | 2019 | 10 |
| MyDiv | 2015 | 60 |
| ORPHEE | 2008 | 6 |
| **All 11 studies** | **2004–2019** | **186** |
| **Excluding ECOLINK genotype diversity + cumulative coppice** | **2004–2019** | **153 across 10 sites** |
| **Also excluding only-fertilized MataDIV** | **2004–2015** | **143 across 9 sites** |

Original published **planting years vary by 15 calendar years** between BIOTREE Kaltenborn and MataDIV. **No explicit trait and woody biomass source observation year exists in original publicly shared DS1/DS2 or the uploaded 15-page Methods S1–S3 supplement.** The statement `year=2014` for IDENT Macomer means planted in 2014, **not** a 2014 nutrient measurement. Likewise the ECOLINK Figure S2 2022 measured diameter-height relation applies solely to its own caption, not all original sites.

### Methodological implications

- On the surviving 10 sites, each source site has **one** original published establishment year; the two do not vary independently *within* original experiment. **Site fixed effects absorb the between-site establishment-year contrast**. An apparently identifiable pooled/year effect across sites from such data would rely on modelling assumptions about between-site variation, not a site-controlled within-site planting-year test.
- **A true tree age at biomass or leaf trait measurement requires original observation year**. It cannot be inferred by subtracting published planting year from the paper's 2026 publication year; that would create systematic source age error, particularly for ECOLINK cumulative 3-year harvest cycles.
- The source 153 eligible post-ECOLINK plots are distributed across **nine published planting-year groups** (the source block `MyDiv 2015` alone contributes **60/153**, about 39%). This is highly imbalanced between experiments and planting-year groups. That imbalance does **not** establish that site age drives biomass; no ecological response model was fit.
- Original 11-study experiment age/planting calendars from published Table 1 are valuable study metadata for source auditing but cannot resolve whether original SLA/LNCM/WD was measured within two calendar years of the corresponding DS1 woody estimate.
- A prior assistant instruction implied that original **Supplementary Table S1 would necessarily establish those observation years**. That is **not source-verified**: the paper's Supporting Information lists Table S1 as **stand-level characteristics** across the 11 studies. It may contain sampling/measurement years, but the file contents have not been inspected. The exact column list must be checked before promising any temporal source gate pass.

### Current stop condition and next source-specific action

Prior source-only data geometry **PASS**: 328 original DS1×DS2 site/block/plot keys, 186 original positive two-species-trait+DS1 woody plots, **153** if removing incompatible ECOLINK genetic diversity/cumulative harvest response. Original Methods S3 confirms leaf nutrient means for species within plots. The separate Table S1 and Table S3 XLSX files were not present in the conversation upload or discovered as directly accessible original public files outside the publisher, and official Wiley file requests returned 403 from the CI environment. This is **an ACCESS dependency**, not proof those files are absent.

**HOLD** remains for: original **trait sampling year vs woody observation year** per site; complete raw individual sample lineage if needed to infer individual-level local provenance; and original **DS2 species-row woody→DS1 plot woody source scaling**, where previous source-only arithmetic matched 321/328 plots but the remaining 7 disagree. None can be fixed by substituting published Table 1 planting year or manipulating 321/328 arithmetical matches.

A future authenticated/user-supplied original Table S1 could be read with a source-only header/year audit, but must be checked for whether years and source measurement periods are actually reported. A publisher Table S3 could clarify species×site allometry but does not necessarily disclose DS2 row normalization. If neither identifies the needed measured year and response hierarchy, an original author clarification is a valid unresolved source dependency.

No K, rho, source-community FD→biomass association, or new causal or predictive ecology effect was fit in this source chronology crosswalk. Previously closed original BIEN/sPlotOpen and BIODEPTH source quality gates remain closed.
