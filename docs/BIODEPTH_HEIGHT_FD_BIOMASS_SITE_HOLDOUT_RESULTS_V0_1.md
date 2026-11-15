# BIODEPTH 2010 source-verified maximum-height FD predicts biomass across sites? — first locked result v0.1

Checkpoint: 2026-11-15. **Exploratory post-result quantitative height-dispersion benchmark.** The user had already seen Jena, Cedar Creek and BIODEPTH planted functional-group results before this source/trait analysis was developed. Do **not** claim first new biodiversity–ecosystem functioning or worldwide phylogenetic-memory mechanism.

## Source and frozen design chain

1. Same original **eight European BIODEPTH experimental fields**, not a representative global sample or extra studies: original Hector et al. 2010 original site×plot×year Species 5802 records and Community 1440 records. Original 2010 Species→Group→Community is exactly additive on complete data. The alternative Spehn et al. 2005 Shoots edition is NOT numerically interchangeable: 346/1415 comparable plot-years differ by >100g/m²; don't mix 2005 Community outcome with species trait weights or claim a uniform ANPP estimate.
2. GIFT v3.1 original trait `1.6.2 Plant_height_max`, species maximum height in **metres**, maximum over original source reports, with original bibliographic `ref_ID`s. Original reference catalog 949 metadata rows /760 bibliographic IDs; 88/88 original 2010 BIODEPTH height-covered taxa have fully resolved reference IDs and **no explicit original BIODEPTH direct literature citation**. Two of 88 have potentially overlapping other trait-database sources; these are not automatically original experiment duplication. Original height/reference canonical source fingerprint `125ced593d7218369b33fb11b6fae8e296f5d4d7b57700222b0800ed4adef9ee`.
3. Original 103 source named taxa, 93 exact GIFT accepted species matches, 88 positive source-attested GIFT maxheight values, 174 originally sown plots meeting ≥3 planted species with maxheight and ≥80% planted species coverage. **Greece has zero eligible plots**; therefore only 7/8 original sites analyzed. Source original 2010 Community has **521 valid plot×year responses**, one missing 2010 source record for these 174 plots.
4. **Frozen before opening outcome** in `docs/BIODEPTH_SOURCE_2010_HEIGHT_DISPERSION_BIOMASS_TRANSPORT_V0_1.md`: predictors use equal weights for initially **planted** species (not contemporaneous biomass), log maximum height values, CWM = mean(log height), one-axis FD=mean absolute pairwise distance among logged heights. Baseline includes polynomial log2 planted species richness, original three planted guild presence flags, year2/year3. Site is entirely held out; no heldout site intercept, heldout data preprocessing or source outcome-derived feature selection. M1=baseline+CWM; M2=M1+FD. Compare site-heldout SSEs, never data-row random splits. Predeclared primary score is **equal-site mean of `1-SSE(M2,s)/SSE(M1,s)`**, n=7 original heldout fields, 10,000 site bootstraps seed 20261115.

## Locked external-field holdout result

| Original heldout field | Original plots | Plot×year | FD vs CWM model test SSE gain |
|---|---:|---:|---:|
| Germany | 26 | 78 | **+23.68%** |
| Ireland | 32 | 95 | **+2.58%** |
| Portugal | 14 | 42 | **+9.55%** |
| Sheffield | 20 | 60 | **−908.48%** |
| Silwood | 32 | 96 | **+5.54%** |
| Sweden | 22 | 66 | **−6.44%** |
| Switzerland | 28 | 84 | **+11.97%** |

**Five of seven** sites have positive *point* gain, but the **equal-site mean gain is −123.09%**, 10,000 site-bootstrap 95% CI **[−386.11%,+13.09%]**; the fixed positive-support criterion **FAILED**. Pooled across all original repeated plot-year test predictions, source SSE gain is **−43.68%**; average CWM alone versus context baseline site gain is **−2.75%**. These very large negative percentages are **relative error increases**, not negative biomass production or FD effects. Do not turn 5 positive fields into support for a general ecological effect by dropping Sheffield; 7 original fields provide limited high-level replication.

Strong missingness robustness: the original **150/174 plots with 100% GIFT height coverage for all originally planted species** still produce site-equal FD predictive gain **−122.95%** (95% CI [−382.20%,+10.12%]), with Sheffield **−897.28%**. The catastrophic Sheffield failure is not explained solely by partial missing trait values in 80%-covered plots.

[Original source-pinned GitHub Actions #43723058720](https://github.com/zuizui0223/turnover/actions/runs/43723058720) SUCCESS, run artifact #14164924899 SHA256 `824419d297ffd7b01ebb12d936afce57268088af49976a8bd832612f37b15ad9`. Explicit original GIFT-source code and original 2010 biomass bytes are cryptographically pinned; the only 88 raw maximum height values are used in-memory and never committed. Canonical summary `results/biodepth_2010_species_source_v0_1/height_pairwise_dispersion_biomass_site_holdout_v0_1.json`.

## Interpretation and next root-cause check

Current conclusion: **adding planned species maximum-height dissimilarity does not reliably improve predictions across the seven eligible original BIODEPTH fields**, even though five original fields show small/moderate benefits. This is **site transportability failure of a specific retrospective model**, not an empirical rejection of functional complementarity or a test of family-specific evolutionary-memory rho. One field's huge loss can arise from feature range shift, OLS coefficient instability, limited planted species composition support, GIFT species upper-bound measurement aggregation or source-specific outcome/site effects. **No cause yet proven**; do not infer trait context as mechanism from poor prediction alone.

A separately frozen *post-result* source-only model/feature diagnosis is executing at `docs/BIODEPTH_HEIGHT_FD_SHEFFIELD_SITE_OOD_DIAGNOSTIC_V0_1.md`. The diagnosis will compare Sheffield's original planted logheight FD distribution against all other training sites, model condition number, FD coefficient, and number of heldout plots carrying the extra error, while rechecking the original frozen source version. It will NOT exclude original plots or change the negative heldout result.

## Hard boundaries
- GIFT maximum species height is external, literature-aggregated and sometimes from overlapping trait databases; not necessarily measured at these fields or independent of all historical trait sources.
- 521 annual biomass plot-year rows are repeated observations of 174 original plots, not 521 independent experimental sites.
- Original BIODEPTH six-high-support-site within-exact-planted-richness gate remains HOLD at 1/8; the 174-plot GIFT-based cohort does not retroactively satisfy that design criterion.
- Original sPlotOpen×GIFT×BIEN 201 family×trait rho→PD–FD source gate remains HOLD, and NEON public API requires authorization. A community planted-height FD predictive gain is not a test of original phylogenetic signal/lineage context.
