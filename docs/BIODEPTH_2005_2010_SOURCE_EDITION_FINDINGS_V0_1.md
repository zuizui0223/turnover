# BIODEPTH original 2005–2010 biomass hierarchy and edition compatibility — evidence checkpoint

Checkpoint 2026-11-15. Original BIODEPTH source files DOI [Spehn et al. 2005](https://doi.org/10.6084/m9.figshare.3565170.v1) (original CC0 supplement) and [Hector et al. 2010](https://esapubs.org/archive/ecol/E091/155/suppl-1.htm) (original author source) are the **SAME eight field experiments**; no pooling as independent publications or additional experimental studies.

## 1. Source taxon identity (complete for the original 2010 dataset)

Original 2005 design provides 480 globally unique plot IDs, eight sites and 3 original source years. Original 2010 species biomass roster provides 5,802 plant × plot × year entries = 1,934 planned plot×species occurrences ×3 years. Original 2010 names include **103 original Linnaean species names /186 site ecotype codes**. They map fully to the original 2010 species dictionary and the 480 original plotted species assemblages.

The separate `jebyrnes/multifunc` 2015 R repackaging has all 480 plots and 103 planted incidence columns, with correct sums of planted richness (480/480), but **secondary mixture numbers were recoded in seven of eight sites**, and seven **secondary species abbreviations** differ from the original 2010 Linnaean names. Of 5,802 original species-year records, 5,580 have an exact secondary R taxon-column label, while 222 source records correspond to seven unresolved secondary R name abbreviations. **Do not automatically infer seven taxonomic synonyms or merge by secondary composition integer.** Use original 2010 species codes/plot IDs for source-native FD estimation.

Source verification: [Actions #43714413569](https://github.com/zuizui0223/turnover/actions/runs/43714413569), original byte-pinned artifact; result `results/biodepth_2010_species_source_v0_1/full_2005_2010_species_crosswalk_v0_1.json`.

## 2. Internal 2010 original biomass hierarchy is exactly additive

The original 2010 `BiodepthBiomass.txt` has **5,802 Species**, **2,574 Group**, and **1,440 Community** rows. The separate 2010 `BiodepthSpeciesBiomass.txt` agrees with every one of the 5,802 2010 hierarchy Species rows, **including 71 original source nonnumeric/missing species entries**. On complete source records, **1,423/1,423** summed Species plot-years equal original reported Community biomass to float precision; **1,434/1,434** summed Group plot-years equal Community biomass likewise. There are 17 plots×years with one or more missing species values, six group-incomplete plot-years; do not add original hierarchy levels or replace NA with zero.

Source: [2010 original hierarchy verification #43715145821](https://github.com/zuizui0223/turnover/actions/runs/43715145821), pinned `BiodepthBiomass.txt` SHA256 `9d95e65295bf6014e753f474dffa09036718b6b54ad5e1d4eea41c1dde76f886`. Nonraw aggregate result `results/biodepth_2010_species_source_v0_1/biomass_original_hierarchy_qa_summary_v0_1.json`.

## 3. 2005 Shoots and 2010 Community editions are not numerically interchangeable

The 2005 source `Shoots.txt` has 1,440 plot-year responses (1,419 numeric); the 2010 hierarchy `Community` also has 1,440 plots (1,434 numeric). Exactly **1,415** source plot-years have both responses. At strict 1e−5 g/m², **1,172** differ, and **243** agree. The **overall median absolute difference 0.125 g/m² is misleading**, because pooled locations include 162 exactly identical Sheffield plot-years and many other rounded-equal sources. Source-specific disparity is large:
- **346/1,415** source records differ by **>100 g/m²**; **455** by >50, **638** by >10.
- **686/1,415** pairs differ by **>1%** of larger original source value.
- 21 source plot-years have 2005 biomass **positive** but 2010 Community biomass **zero**; no source pair has the reverse zero/nonzero case.
- **Ireland year3:** 65/70 >100 g/m², 68/70 have 2010 at least 1g/m² *lower* than 2005. **Switzerland year1:** 50/64 >100, 55/64 have 2010 at least 1g/m² *higher*. **Sheffield:** 162/162 source observations exactly identical across all three years. This is not a uniform rounding or multiplicative-rescaling effect.
- 95th percentile absolute source difference ≈385 g/m²; maximum ≈1,170.4 g/m².

Source: [Numeric edition/site×year discrepancy QA #43715363831](https://github.com/zuizui0223/turnover/actions/runs/43715363831); summary `results/biodepth_2010_species_source_v0_1/original_2005_2010_numeric_edition_audit_summary_v0_1.json`. Original primary publications refer to aboveground biomass and biomass-production indices, and the 2010 methods describe species-wise aboveground net biomass production. **No source-backed exact explanation for edition-specific site/year numeric discrepancies has yet been identified.** Handling, weed/non-sown components, corrections, clipping and timing are candidate causes, not proven. Do not select or "correct" one response version based on apparent ecological significance.

## 4. Same-cohort observed guild substitution is sensitive to source edition

On **exact same original 110 matched plots /35 source site×planted-richness×block strata /327 plot-year rows** (all source-complete), keep source treatment `grasses=Yes`, `functional.richness=2`, and substitute original planted legume versus nonlegume forb. Site-equal original log1p biomass differences:
- **2005 Shoots:** +0.1714735 (six sites positive, two negative).
- **2010 Community:** +0.2756586 (same six positive, two negative).
- Edition shift +0.104185 (n=8 site-bootstrap 10,000 draws CI95 +0.00304 to +0.23312); **post-result source-edition processing sensitivity**, not biological replication or a new causal finding. Greece -0.833→-0.335, Ireland +0.202→+0.392, Sweden +2.223→+2.144; no source site flips sign.

Source [same fixed cohort CI #43715879761](https://github.com/zuizui0223/turnover/actions/runs/43715879761); result `results/biodepth_2010_species_source_v0_1/original_response_edition_matched_guild_summary_v0_1.json`.

## Scientific decision

For new BIODEPTH species/trait FD exploration, **the coherent response set is original 2010 Species/Group/Community data**, with absent/NA and true zeros treated correctly. Original 2005 Shoots effects remain historical published and exploratory estimates *of that edition* and may not be mixed with 2010 species relative-biomass-derived predictors. The safest new trait-FD predictor candidate is **original planned sown species incidence × independently sourced plant traits**, not an outcome-derived same-year biomass-weighted trait index. This avoids immediate algebraic response leakage. The new **103-taxon GIFT v3.1 height source eligibility** is separately frozen in `docs/BIODEPTH_103TAXA_GIFT_HEIGHT_SOURCE_GATE_V0_1.md` and must pass without retrospective threshold tuning before any numerical FD association is estimated.

**Previously frozen programmes remain unchanged:** original Spehn BIODEPTH ≥6 sites with 20 plots at one exact richness main gate is HOLD (only Ireland qualifies); original sPlotOpen×GIFT×BIEN family×trait memory/FD primary gate HOLD; NEON requires an authorized token for released plot data. One BIODEPTH consortium with eight original sites is not a worldwide sample, and no new mechanistic nitrogen-fixation or multi-axis trait-memory→biomass result is established.
