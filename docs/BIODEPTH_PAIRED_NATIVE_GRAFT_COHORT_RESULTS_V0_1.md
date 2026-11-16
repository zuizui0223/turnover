# BIODEPTH PD biomass prediction — paired-102 source plot decomposition

**Completed 2026-11-16.** Original immutable source-data and seven-source-field models replayed with GitHub Actions **SUCCESS**. Frozen diagnostic specification at `docs/BIODEPTH_PAIRED_NATIVE_GRAFT_COHORT_DIAGNOSTIC_V0_1.md` was committed *before opening the new full-S3-on-102 outcomes* but after all preceding 150-vs-native-102 results had been seen: this is **retrospective sensitivity analysis**, not new independent confirmatory ecology.

## The original source-reconciliation tests all passed

The original 103 species/480 plots Hector2010 Species+Codes; original 2005 planted design; original Hector2010 Community aboveground standing biomass; GIFT bibliographic max-height source; and pinned V.PhyloMaker2 GBOTB S3 tree were fetched/rechecked with their existing frozen SHA/source fingerprints. All 7 existing site-level predictive SSE values for both **150 full-S3 plots / 449 numeric plot-year responses** and **102 native-only plots / 305 numeric plot-year responses** were reproduced to **≤1e−10**, without changing source quality, originally planted species membership, user-selected outcome, model covariates or original source field identities.

The 102 original source plots remain identical under the new comparisons. Their original field sizes are: Germany 14, Ireland 26, Portugal 8, Sheffield 18, Silwood 14, Sweden 14, Switzerland 8. In **34/102 plots**, all-S3 versus backbone-native species coverage changes planted-species CWM, height FD and phylogenetic PD; in the remaining 68, those predictors are unchanged.

## Three fixed decompositions

All reported values are **equal-seven-site mean gains in out-of-source-field biomass SSE** when adding exactly one phylogenetic MPD predictor to the existing planned richness, planting guild, source year, mean log height and log-height FD model. Positive predicts biomass better out of field; negative predicts worse. Original 2010 standing biomass is not uniform annual NPP.

| Predictor and cohort | PD incremental out-of-field gain | Bootstrap original-site 95% interval | Original fields with gain>0 |
|---|---:|---:|---:|
| Original 150 planted plots, S3 all-covered taxa | **−1.451%** | [−7.291%,+3.151%] | 4/7 |
| **Same source feature definition, only 102 fixed original plots**, full S3 height/PD | **−4.008%** | [−7.668%,−1.026%] | 3/7 |
| **Exact same 102 original plots and Community plot-year responses**, native-backbone-only height/PD | **−3.500%** | [−6.191%,−1.074%] | 2/7 |
| Same 102 plots with the identical **full-S3 CWM and FD baseline**, PD based only on native taxa | **−3.515%** | [−6.878%,−0.595%] | 3/7 |

### A. Original study cohort restriction (full S3 preserved)

`102_full − 150_full = **−2.557 percentage points**`, 10,000 paired-field bootstrap 95% interval **[−6.972,+1.918]**. This *sample-mix/estimation-support sensitivity* changes observed original field plots, source response rows, and model training, **not** the method used for S3 phylogenetic breadth/height FD. It is not a significant site-paired contrast by this descriptive uncertainty interval; no randomized restriction experiment was done.

### B. Same 102 plot IDs/305 responses; all-S3 vs backbone-native source species

`102_native − 102_full = **+0.508 percentage points**`, site-paired CI **[−0.264,+1.747]**. The native-only point estimate is therefore **slightly less negative** after holding source plots/responses identical. Since CWM, FD and PD all change together for the 34 affected plots, this B contrast cannot isolate phylogenetic distance itself.

### C. Same 102 plot IDs, same CWM/FD baseline, change PD source species alone

With all **M2 source-site SSE values identical to ≤1e−10**, original full-S3 PD gives −4.008%, native-only species-pool PD gives **−3.515%**. The source PD-only feature-coverage difference is `nativePD − allPD = **+0.494 percentage points**`, paired CI **[−0.162,+1.219]**. Six of seven source sites have a positive *difference* in PD-score gain, but the interval spans zero. This is not an alternative species phylogeny: both are measured on the same dated GBOTB-S3 tree, with different source species included in the plot-level PD averaging.

**Key diagnosis:** The earlier superficial comparison between −1.451% (150 plots) and −3.500% (102 plots) does *not* show that S3-inserted species or the S3 placement method damaged prediction. When the 102-plot sample itself is fixed, excluding inserted species only slightly improves the point prediction score. The large negative shift arises on restricting the analysis to a different, smaller source-defined plot population, **but whether this is due to species composition, site mixture, sample size/precision, or other changes cannot be causally determined from the retrospective contrast**.

## What is and is not new ecology

- All three predictions remain negative on this specific original group of field experiments and fail the prior frozen positive transfer criterion. The new full-S3-on-102 negative mean also has a site-bootstrap interval entirely below zero. It is observational out-of-field prediction, not a negative biological effect of phylogenetic diversity on plant productivity.
- The original data still show **strong source selection and trait-value sensitivity**: the GIFT *Origanum vulgare* 13m outlier and botanical corrected single-height FD model (174 original source plots) had very different source-site heldout predictions. The 150 and 102 plot sets are not a worldwide representative sample.
- **Nothing here tests family/organ-specific Blomberg's K or BIEN distance–disparity rho against community FD, biomass or population productivity.** Tree-wide original species patristic breadth is not the same estimand as lineage-specific evolutionary trait-memory strength.
- The source inclusion of 34 affected plots and explanatory values is a useful diagnostic for future *sampling-process* research, not a new stable mechanism inferred for ecological selection or interspecific competition. Later new hypothesis testing would require genuinely independent plots/sites or prospective experimental variation.
- Do not resample/retune site selection to rescue a positive FD/biomass predictive result. All original strict BIODEPTH six high-density site support, BIEN×sPlotOpen 201-system macro K→FD→mass, and NEON API auth source gates remain **HOLD**.

## Provenance

- Frozen new 102-paired design: `docs/BIODEPTH_PAIRED_NATIVE_GRAFT_COHORT_DIAGNOSTIC_V0_1.md`
- Source-verified original-data run: https://github.com/zuizui0223/turnover/actions/runs/43828231403 (**SUCCESS**), full aggregate-only artifact #14207851720, digest `sha256:28de2f2550066b67a371525b78a82a9ef21ef6da1bc04191839dde9e873935b4`.
- Permanent nonraw exact source-run result with all seven original field SSE values and paired diagnostics: `results/biodepth_2010_species_source_v0_1/paired_native_full_s3_same102_verified_v0_1.json`. Program `scripts/analysis/audit_biodepth_native_vs_s3_fixed_cohort_v0_1.py`.
- Earlier original PD results (same-source baseline) remain unmodified in `results/biodepth_2010_species_source_v0_1/matched_pd_fd_biomass_source_verified_result_v0_1.json`. PR is Draft and stacked atop original PR #51; `main` unmodified.
