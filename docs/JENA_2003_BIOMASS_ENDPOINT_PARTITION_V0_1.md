# Jena 2003: sown, non-sown and combined biomass — endpoint sensitivity

Checkpoint 2026-11-15. **Post-result exploratory extension**, not a preregistered or independent experiment. Original K/rho, long-term FD/FI and original Jena estimates are not changed.

## Executed question
Does the May association of planned functional-group richness with sown-species aboveground dry mass extend to the combined mass of sown and non-sown plants? Existing sampling-sensitivity results were replayed first; the previous official-mean and ordinary-quadrat coefficients were reproduced with 4000/4000 full-rank draws.

Original source: Buchmann N & Temperton VM (2015), PANGAEA https://doi.org/10.1594/PANGAEA.846317 (CC BY 3.0). Source cache run 43604642543 / artifact 14117253081 was downloaded and its ZIP SHA256 matched 9646b7dade486a2f3cde7a08d89124d03570841096d886834a1a894956a270a2. Original source hashes are retained in the result JSON. No raw observations committed to Git.

## Model and measurement boundaries
- The weed category means plants not sown in that particular plot, not necessarily exotic species.
- Use official FOUR-quadrat means for both sown and non-sown mass. Weed mass is unavailable per quadrat, so it must NOT be added to the ordinary three-quadrat sown mean.
- One mean weed observation is blank: B1A18, May 2003. Blank was not replaced by zero. Use the same **81 complete plots in both seasons and all endpoints**, 162 plot-season observations but only 81 experimental plots.
- Predictors unchanged: intercept, log2(sown species richness), planned functional-group richness, and three original field-block indicators.
- Compare log1p(sown), log1p(non-sown) and log1p(sown + non-sown). Addition precedes transformation.
- Four new exploratory tests are log non-sown and log combined FG slopes in May and August; apply Holm to their HC3 normal-Wald p-values. Raw-mass models and paired log-endpoint contrasts are descriptive sensitivity analyses.
- Bootstrap 4000 paired plot draws stratified by original block, seed 20261118, preserving the same sampled plot multiplicity across both seasons/all endpoints. Intervals are marginal, not simultaneous.

## May results on the SAME 81 plots

| Endpoint | Raw-scale FG slope g/m2 per additional planned group | HC3 95% CI | Log1p FG slope | Nominal HC3 p |
|---|---:|---:|---:|---:|
| Sown plants | +46.8786 | +1.2725 to +92.4847 | +0.167320 | 0.044126 |
| Non-sown plants | -6.0288 | -13.0411 to +0.9835 | -0.220347 | 0.113307 |
| Combined sown + non-sown | +40.8498 | -5.9288 to +87.6284 | +0.148217 | 0.068443 |

Raw additive identity is verified for all coefficients: combined = sown + non-sown (maximum difference 1.78e-13). This is an algebraic decomposition of regression slopes, not a causal mediation estimate.

Holm-adjusted p-values across the four new log endpoint tests: May non-sown **0.339920**, May combined **0.273770**, August non-sown **1.0**, August combined **1.0**. No new test crosses 0.05 after this adjustment.

Uncertainty is method-sensitive. For May log combined mass, the paired percentile bootstrap interval is **[+0.008211,+0.322216]**, while the HC3 interval is **[-0.011216,+0.307650]**. Raw combined mass also has intervals spanning zero (HC3 and bootstrap). Report both; do not select the positive interval as decisive evidence. May raw non-sown mass likewise has a negative bootstrap interval but an HC3 interval including zero.

The direct May log-combined-minus-log-sown FG slope is **-0.019103**, HC3 p **0.051381**, CI **[-0.038321,+0.000115]**. It does not establish an endpoint difference; comparing separate p-values would not establish one either.

## August and earlier weeding sensitivity
August raw combined FG slope **-4.8621 g/m2** (HC3 CI **[-38.5452,+28.8209]**). Log combined slope **-0.015072**, p **0.845782**. This alone does not prove a seasonal interaction.

The existing 82-plot May sampling sensitivity was independently replayed: official slope +0.167891; ordinary quadrats 1–3 slope +0.172590 (HC3 p=0.055877); paired ordinary-minus-official difference +0.004699 (p=0.822862). Similar point estimates do not prove equivalence, but there is no support for assigning the May association specifically to quadrat 4.

## Ecological interpretation
The observed May positive association is clearest for **biomass of the experimentally sown plants**. The combined endpoint remains positive in point estimate, so this is not evidence for a complete replacement of weed biomass with no overall gain. However, an increase in combined biomass and a reduction in non-sown biomass are not robustly established under the new endpoint comparisons. Competition/suppression, compensation and resource complementarity remain hypotheses rather than identified mechanisms.

Combined mass here excludes roots, detached dead material and unidentified material; it is not total ecosystem biomass or annual primary production. Planned functional-group richness is not continuous trait FD, and no phylogenetic-memory or cross-site effect was tested.

## Reproduction and verification
New script: `scripts/analysis/jena_weeding_v0_1/response_partition.py`; new tests: `scripts/analysis/jena_weeding_v0_1/tests/test_partition.py`. Reuses the unchanged helper `weeding_sensitivity.py` (Git blob 682d6ac38f75d49cd751af4ffe23a897cf1b968f).

Existing 13 plus 9 new tests: **22 passed** locally. Independently reconstructed panel with pandas and fitted all 14 models using statsmodels, importing no production helpers: maximum coefficient/SE/p/CI discrepancy **1.56e-13**. Independent weighted-least-squares bootstrap replay matched all 4000 draws' interval summaries to **9.86e-14**. Holm correction reproduced independently. No new GitHub Actions execution is claimed; skip-ci commits avoid re-running unrelated frozen analyses.

Result: `results/biomass_jena_2003_source_v0_1/endpoint_partition_summary_v0_1.json`. Full coefficients, tests, original public source files and independent verifier are included in the conversation's reproducible archive. Existing scientific result files are unchanged; PR #40 remains Draft/unmerged.
