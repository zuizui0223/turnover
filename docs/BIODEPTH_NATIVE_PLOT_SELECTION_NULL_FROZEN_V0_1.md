# BIODEPTH: is the native-tip-eligible 102-plot subset unusual among the original 150 planted plots?

**Analysis contract frozen 2026-11-16 before any NEW plot-selection null draws or scores.**
This is explicitly **retrospective and exploratory**, because the seven-site biomass model and the previous exact 102-plot subset outcome have already been opened in PR #51 and #52. This study characterizes a sample-selection failure mode, not a new test of phylogenetic trait conservation, causal plant productivity or a universally positive/negative phylogenetic diversity effect.

## Preexisting sources and controlling results

- Same original Hector et al. 2010 Species, SpeciesCodes and Community 2010 biomass (with original SHA256 checks); original Spehn et al. 2005 **planting design only**, not the different Shoots biomass edition.
- Same GIFT 3.1 88 original height species and source bibliography fingerprint; source-reference `Origanum vulgare` maximum-height sensitivity set to already fixed external Kew 0.90m.
- Same V.PhyloMaker2 commit `7af3fb5152f691af2e4ec9d5e2e467d1b50505e9`, GBOTB S3; source-only exact-genera family mapping.
- Original **150** GIFT×S3 plant plots, 84 eligible species, seven source sites, **449** source Community plot-year responses. The original direct-backbone-eligible **102 plot IDs** and **305** responses are a subset. Fix 102 source field plot quotas: Germany14, Ireland26, Portugal8, Sheffield18, Silwood14, Sweden14, Switzerland8. Do not select plots from biomass effects.
- Source effect pipeline in `scripts/analysis/fit_biodepth_matched_pd_fd_biomass_transport_v0_1.py`. Predictor `PD` is mean pairwise S3 patristic distance using **full S3 taxon coverage**; `CWM` and `FD` also use full S3 and log maximum height. Model M2 contains quadratic planted richness, original grass/forb/legume flags, original year, source-height CWM and FD. M3 = M2 + PD. Train-only scaling; fit OLS independently on six fields, predict one entirely withheld field. Site-equal mean `G=mean_s(1-SSE(M3,s)/SSE(M2,s))`. Each source plot is kept with all valid repeated 2010 years.
- Historical `G_150=-0.014511753119435358` and `G_102_fullS3=-0.04008463029040919` must reproduce the original seven individual source-field SSEs to **1e-10 absolute tolerance** before new null scores are reported. Fixed 102 native-only `-0.035001507155048316` is historical and unchanged.

## The fixed primary benchmark (site-stratified source subset null)

**Scientific question:** Is the native-tip-eligible original **102 plot sampling decision** unusually associated with a more negative out-of-original-field *prediction gain* compared to random plots drawn from the original same 150 eligible source plots while **preserving the exact original number of plots from every site**?

- Original population is the 150 previously matched GIFT×GBOTB plots and **only** these plots, not all 480 BIODEPTH fields.
- Fix the original seven source-field site quotas (14/26,26/26,8/8,18/20,14/24,14/18,8/28). Draw **499** independently seeded random 102-plot subsets without replacement **within each site** using numpy `default_rng(20261116)`.
- Every selected plot contributes all original valid 2010 Community years. Never draw individual plot-years or alter original responses. For each resample, compute the same full-S3 CWM, FD and PD using **all S3-resolved species present in that sampled original plot**, and refit both historical M2/M3 for all seven whole-site folds. No model selection or post-outcome seed tuning.
- Compare the existing source-determined 102 native-support plot subset's *full-S3* `G=-4.008463029040919%` against the 499 random site-quota matched `G` values. Descriptive lower-tail reference `p_low=(1+#{G_random<=G_observed})/500`, and null median/2.5/97.5% percentile; **this is not a causal randomization test**, as native eligibility was never randomly assigned.
- The original 150 full-S3 estimate is **not** another sample draw; report only as historical reference, not a null-distributed observation.
- If any draw has insufficient original-source fold rank, mark the draw invalid in the machine-readable output and do not retry it. Require >=475 of 499 valid seeded draws; else verdict `MODEL_INFORMATIVENESS_HOLD`, do not infer a tail probability. If full model rank is uncertain, report that fact as a model geometry limitation.

## One predeclared secondary matching benchmark

Repeat 499 draws with a second deterministic seed `20261117`, stratifying original plots not just by **original site**, but by **exact planted species richness** and the **three original planned guild flags** (grass, forbs, legumes). Preserve exactly the number of native-support-qualified plots in each source `site × exact richness × planned guild-vector` stratum. No new field exclusion or loosened matching.

Before opening any response effects, check source-only **whether the design is informative**:
- at least **10** original native-eligible selections belong to partially selected strata (`0<k<n`) that offer an alternative plot ID; and
- these alternative stratum choices occur in **at least 3 field sites**.

If not, report `SECONDARY_DESIGN_SUPPORT_HOLD` and preserve null settings without relaxing exact matching. If the model rank fails in >24 of 499 fixed draws, report `MODEL_INFORMATIVENESS_HOLD`. Use exactly the same descriptive null scores, seed and tail formula as primary.

This secondary can show whether sampling contrast persists *after exact richness and planned guild composition are controlled*. If too few within-stratum alternatives exist, no inference follows from its prospective structural HOLD.

## Mandatory outcome-blind source-composition diagnostics

Before reading new random-subset biomass results, save nonraw original source eligibility summaries for the original fixed native 102 vs the 48 omitted source-eligible plots: per-site plots, plotted planted richness distribution, original plotted guild vectors, and original GIFT×S3 source-only plot CWM/FD/PD summary (group mean/median only). Report the number of movable native plots and sites in the secondary exact-stratum benchmark. Do not retain original copyrighted raw source data, source trait measurements, species-level rows or original plot-identifiable records in Git.

## Claim boundaries and next decision

- **Source selection is not assigned at random**, so a surprising native subset gain relative to random subsets would only show *selective sampling geometry*, not a biologically selected community mechanism. Weak/typical results would indicate that ordinary 102-plot reductions can produce a similar prediction shift under the same site quotas; not proof of zero selection.
- Causal decomposition into **trait effects** versus **phylogenetic memory** is not feasible with the 84 species/17-family plot support, and no family-specific K is estimated here.
- Do not choose a favorable richness subset or a new K source after seeing these outcomes. If result fails, report it and stop the retrospective BIODEPTH data mining. Existing BIODEPTH six-high-density-site, BIEN×sPlotOpen family-K→FD and NEON authorization gates remain HOLD.
- No source baseline manuscript/main branch mutations; create an independent Draft PR stacked on PR #52 with archived aggregate-only results and source provenance.
