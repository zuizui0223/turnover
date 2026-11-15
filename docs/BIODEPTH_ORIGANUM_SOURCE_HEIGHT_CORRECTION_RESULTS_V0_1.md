# BIODEPTH: A single anomalous plant-height record reversed a retrospective 7-site heldout FD prediction result

Checkpoint: 2026-11-15. **Completed, source-fingerprinted, post-result botanical quality-control sensitivity**. No changes to the original frozen analysis. Do not describe the corrected model as a new prospectively confirmed ecological finding, and do not claim height difference itself causes plant biomass differences.

## Data identity and original frozen analysis
Original BIODEPTH 2010 Hector plot×year Community aboveground biomass, 174 original sown-species height-eligible plots across seven BIODEPTH European fields (Greece has 0 eligible under the original ≥3 species and ≥80% height coverage rule), **521 numeric plot-year original Community responses**. Height values are GIFT v3.1 original species `Plant_height_max`, metres, source-level maxima (not measured in the field). Original reference provenance all 88 height-covered species resolved, no explicit original BIODEPTH bibliography overlap. The 2005 Spehn Shoots data are NOT numerically identical in many site-years to 2010 Hector Community, so only internally coherent original 2010 Community edition was analyzed.

Original frozen model before biomass outcomes opened was `M0 = log1p(original 2010 Community biomass) ~ log2(original planted richness)+square+3 original planned guild identities+year`; M1 adds the equal-sown-species mean log maximum height; **M2** adds mean absolute pairwise difference of equal-sown-species log maximum heights. Every original European field held out once. Each training fit uses only the other source sites, with train-only trait means and SDs. Primary score = site-equal mean `1−SSE(M2)/SSE(M1)` from original heldout field response. Bootstrap original geographic sites 10,000 times (seed 20261115). All original source byte SHA256 and GIFT original 88-species trait/references fingerprint retained.

## Original GIFT extreme, independently verified original raw source
**Origanum vulgare** GIFT original work_ID31210 had maximum species height **13 metres**, aggregated n=14 and coeff_var 2.102. GIFT `traits_raw` source `ref_ID=263` (Schönfelder & Schönfelder, 1997 flora) contains **13** m, versus 0.5–0.7m from other original GIFT raw references (IDs 10224, 10247, 10302, 10315, 10320). The 1997 book itself was **not** read; no assertion it printed 13m. Independent botanical height ranges: [Kew POWO](https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:453395-1/general-information) 20–90cm, [RHS](https://www.rhs.org.uk/plants/11923/origanum-vulgare/details) typically 20–80cm/max 0.5–1m, [Pladias](https://pladias.cz/en/taxon/data/Origanum%20vulgare) .25–.7m. The GIFT maximum aggregation promotes the outlying record to the species trait. Original GIFT source audit [Actions #43724523438](https://github.com/zuizui0223/turnover/actions/runs/43724523438) SUCCESS and source result `results/biodepth_2010_species_source_v0_1/gift_origanum_maxheight_anomaly_source_summary_v0_1.json`.

## Matched sample botanical-source sensitivity (post-outcome, values frozen before new fit)
The sample was **identical**: 174 original plots and 521 original measured response records, same seven heldout-site folds, same original M0/M1/M2 formulas, same 10k site bootstrap and original GIFT reference source fingerprint `125ced593d7218369b33fb11b6fae8e296f5d4d7b57700222b0800ed4adef9ee`. **One parameter was changed:** the original GIFT Origanum 13m replaced with botanical range values Kew .9m (primary sensitivity), Pladias .7m and RHS 1.0m (secondary sensitivity). Original remains in historical result.

| Source height for oregano | Original heldout sites with FD improvement | Mean of seven heldout site SSE gains: M2 over M1 | Site-bootstrap 95% interval | Sheffield heldout SSE gain | Pooled source response SSE gain, descriptive |
|---|---:|---:|---:|---:|---:|
| **Original GIFT 13m** | 5 / 7 | **−123.09%** | **[−386.11%,+13.09%]** | **−908.48%** | −43.68% |
| **Pladias 0.70m** | 4 / 7 | **+3.89%** | **[−11.09%,+18.24%]** | **−29.04%** | +14.09% |
| **Kew 0.90m** | 4 / 7 | **+3.83%** | **[−10.92%,+18.29%]** | **−27.05%** | +14.26% |
| **RHS 1.00m** | 4 / 7 | **+3.79%** | **[−11.02%,+18.29%]** | **−26.85%** | +14.29% |

**Original-site holdout effect with unchanged GIFT 13m versus Kew 0.9m:**

| Heldout source site | Original GIFT source 13m | Kew botanical 0.90m |
|---|---:|---:|
| Germany | +23.68% | +18.56% |
| Ireland | +2.58% | +17.13% |
| Portugal | +9.55% | +30.37% |
| Sheffield | **−908.48%** | **−27.05%** |
| Silwood | +5.54% | −11.73% |
| Sweden | −6.44% | +15.04% |
| Switzerland | +11.97% | −15.50% |

**Source-only predictor shift diagnosed:** Original GIFT Sheffield 10/20 eligible plots planted oregano, 6 of 20 original planted log-height MPD values exceeded training-site maximum and 10 were >3 training-site SD (max z=10.71); original M2 partial VIF≈1.34, making severe collinearity unlikely as the *main* explanation. With the Kew 0.9m correction, **0 of 20** Sheffield plots lie outside six-site training source MPD range, **0** exceed 3 SD, max |z|≈1.91. No plots were removed from analysis, no model tuned on Sheffield response.

The highly nonportable *original result* is strongly **source-anomaly sensitive**: original huge Sheffield prediction loss largely arose from one implausible library species height promoted by maximum aggregation. The corrected M2 site-average is slightly positive but has a 95% interval covering 0 and only 4/7 sites improving. Therefore **a broadly generalizable positive height-FD→biomass predictive benefit is not established** after correction, and a strongly negative ecological FD effect is likewise not established by the original bad source. This is an important **data quality / measurement portability finding**, not evidence that biodiversity only matters in some habitats or that the one-axis dispersion is a complete functional diversity measure.

[Original/sensitivity GitHub Actions #43724949088](https://github.com/zuizui0223/turnover/actions/runs/43724949088) SUCCESS; artifact #14165668294 SHA256 `25944ace5357b5579c598a90f16f25d971d5d8b1e3456056c598576f04916d65`, full source-signed per-site models/feature diagnostics. Archived review summary `results/biodepth_2010_species_source_v0_1/origanum_botanical_height_source_correction_summary_v0_1.json`, source and model `scripts/analysis/fit_biodepth_2010_origanum_height_botanical_correction_v0_1.py`, frozen contract `docs/BIODEPTH_ORIGANUM_SOURCE_HEIGHT_REPAIR_SENSITIVITY_V0_1.md`. Original unmodified model remains `results/biodepth_2010_species_source_v0_1/height_pairwise_dispersion_biomass_site_holdout_v0_1.json`.

## Implication for turnOver mainline and future independent trait hypotheses
- Source bibliography traceability and 80% site-community trait coverage are **necessary but not sufficient**. One record with very high species height CV and physically implausible maximum changes the sign of out-of-community predictive gain. Any macroecological functional-trait analysis based on maxima requires original raw source value plausibility, reference dispersion, and *source-heldout predictive shift* QA **prior to response opening**. Extending the same correction downstream to GIFT/TRY/BIEN source intersections would require a new prospective scope, not a post-hoc rescue.
- All current associations use **planted** species heights at source species-level and original harvested Community biomasses. No observed competition mechanism, no plant actual height, no quantitative trait phylogenetic K/rho, and no family×trait memory mediation tested.
- The original BIODEPTH strict ≥6 sites with 20 within-one-exact-sown-richness eligible plots main source gate stays **HOLD** (only one field passes); the global sPlotOpen×GIFT×BIEN 201 systems source gate remains **HOLD** (87.7% accepted taxon name matching; 10 vs 12 original BIEN height families), NEON released data require official API token and plot-level joins.
