# Current evidence: functional group richness, trait FD and harvested biomass

Checkpoint: 2026-11-14. Separate Jena single-site analyses; no edits to frozen BIEN rho or AusTraits organ-K claims.

## Pooled conclusion is not 'FD increases biomass universally'

### 2003 original directly harvested biomass (PANGAEA 846317)
- 82 original plot means per May/August campaign, verified 2003 source and original sowing group metadata.
- May `log1p(sown aboveground dry biomass g/m²) ~ log2(sown richness)+planned functional-group richness+block`: group-richness β = **+0.16789**, HC3 two-sided p=**0.0439**, block-stratified plot bootstrap CI95 **+0.0219 to +0.3521**.
- The same model in August β **+0.00168**, p=**0.9829**.
- May one-block-held-out SSE predictive gain from FG richness = **+0.7856%**. Adding legume-presence covariate increases FG β uncertainty, HC3 p=**0.221**. These are within-site patterns; multiple tests and limited 4 blocks constrain interpretation.
- Frozen result [JSON](../results/biomass_jena_2003_source_v0_1/group_biomass_effect_v0_1.json), verified [Actions #43576548290](https://github.com/zuizui0223/turnover/actions/runs/43576548290).

### 2003–2012 quantitative trait FD and biomass, temporal heldout (PANGAEA 923591)
- Source: 78 original experimental plots × 10 years × spring/summer, **1,541** distinct plot-year-season joins. 4 prespecified original-author-imputed continuous trait FD axes (plant height, SLA, leaf nitrogen, seed weight) present in all paired source records, original published biomass median across harvest subsamples.
- Temporal generalization 2003–2007 `n=774` training cells; 2008–2012 `n=767` out-of-year test cells; **78 plot IDs occur in both** (no across-site independence). Frozen baseline planned sowing richness, FG richness, season, year and block. All FD/FI variants evaluated on *identical* cells, training-only z-scores.
- Out-of-year SSE gains relative to baseline: **FD alone +0.4627%**, **FI/CWM +2.9765%**, **FD + FI +2.8631%**.
- Two thousand resamples of heldout plot IDs gave FD-only gain 95% interval **−1.581% to +2.178%**; not convincingly positive. Spring FD-only gain **+1.024%** versus summer **−0.168%**; *descriptive*, no prespecified seasonal significance claim. FI/CWM improvement likewise descriptive without an interval; do not claim FI statistically exceeds FD.
- Predicted annual biomass uses *concurrent source-derived cover-based FD* and PCA-imputed trait values, NOT a future forecast before community surveys. Biomass is on the published processed `target.biomass` scale, with physical units unverified; it must not be described as g/m² in this panel without a unit audit.
- See [frozen model](../docs/JENA_923591_LONGITUDINAL_FD_BIOMASS_PREDICTION_CONTRACT_V0_1.md), [source QA](../results/biomass_jena_2003_source_v0_1/longitudinal_fd_biomass_join_qa_v0_1.json), [effect JSON](../results/biomass_jena_2003_source_v0_1/longitudinal_fd_biomass_time_transport_v0_1.json), [Actions #43579207987](https://github.com/zuizui0223/turnover/actions/runs/43579207987).

## Interpretation and separation
1. In the original randomized Jena experiment, a **spring-only** positive planned functional-group-richness coefficient did not transfer to August, and predictive leverage was minimal.
2. Across years in the same Jena plots, four source-derived continuous FD axes **did not meaningfully improve** temporal predictive accuracy over original treatments and seasonal/year context. Four corresponding CWM/FI axes gave slightly larger descriptive gain without inferential confirmation.
3. These results suggest **functional composition and ecological/seasonal context** deserve direct testing, not that FD has no ecosystem effects. The numerical and biological unit is a single European grassland experiment with long-term repeated observations. Author analyses of these data and the 2023 Matters Arising must be cited as prior work:
   - van der Plas et al. 2020, https://doi.org/10.1038/s41559-020-01316-9
   - Hagan et al. 2023, https://doi.org/10.1038/s41559-022-01920-x
4. Original global within-family BIEN 201-system source/qualification is **PRE_OUTCOME HOLD** at 87.7% exact sPlotOpen GIFT match and 10 rather than 12 BIEN height families; neither Jena results nor NEON can retroactively rescue it.
5. NEON independent multi-site herbaceous harvested mass × species cover is promising on metadata (**47 sites, 20 domains, 424 common site-months**) but original release file API requires user `X-API-TOKEN` **since June 2026**. Eight unauthenticated source file list requests failed 403. A manual-only token-protected source manifest QA exists in PR #41 but exact plot/day matching has not occurred.

### What can legitimately be claimed now
**Quantitative positive**: May 2003 Jena planned functional-group richness and dry biomass within plot/season, conditional on richness/block. **Quantitative near-null**: new four-trait FD provides almost no extra long-term out-of-year predictive accuracy in the same Jena experimental plots. Neither constitutes evidence that phylogenetic trait memory causes plot FD or biomass variation across plant families.

### Remaining critical operation
User-only: obtain an account-issued NEON token and store it as a **GitHub repository Actions secret** called `NEON_API_TOKEN` (never in git files, chat or issue). Then manually run `neon-authorized-source-manifest-v0-1.yml` from PR #41. Only after authentication passes can actual plot IDs and sampling dates be audited and any multi-site FD–biomass test proceed. No automated task is currently monitoring this input.
