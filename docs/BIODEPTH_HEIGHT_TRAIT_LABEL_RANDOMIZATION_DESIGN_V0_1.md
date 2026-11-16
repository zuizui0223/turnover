# BIODEPTH 2010: which species carry height diversity? Fixed guild-conditioned label-null design

**Freeze:** 2026-11-16, after all original FD/biomass results and after the botanical source repair in PR #46, but **before opening any height-species label randomization outcome**. This is a *post-result exploratory source-aware diagnostic*, **not** a prospectively validated ecological finding or evidence of causation.

## Narrow scientific question

Given the same originally planted plots, the same site/year biomass data, the same actual planted species incidences and exactly the same number/distribution of GIFT maximum-height values **within each original planned functional guild**, does the real species-to-height mapping yield more transferable incremental biomass prediction by one-axis height FD (beyond richness, guild flags, calendar year and mean height) than alternative mappings?

This tests the **predictive value of actual within-guild species-to-height alignment**, not K, rho, plant phylogenetic memory, competition, trait evolution, realized standing biomass, or an intervention on species membership.

## Fixed source / population boundaries

- Base branch: `analysis/turnover-memory-fd-biomass-bridge-20261116` (PR #47), which inherits the original PR #46 branch. Never alter those original source results.
- Original Hector et al. 2010 Species and Community, SpeciesCodes, original Spehn et al. 2005 Design and original GIFT v3.1 height bibliographies. Use the *same exact SHA256 bytes and GIFT fingerprints* required by `fit_biodepth_2010_origanum_height_botanical_correction_v0_1.py`. Never mix Community2010 with Shoots2005.
- Frozen analysis population: 174 originally sown plots (min 3 GIFT height species; min 80% sown height coverage) from 7 sites; 521 original 2010 Community plot-year responses; 88 source-traceable height species. Greece remains outside original height sample.
- Correct the SINGLE original out-of-range *Origanum vulgare* 13m source-aggregated maximum to independent Kew 0.9m for the **observed** mapping and *all permutations*. This correction was selected after observing the earlier Sheffield failure: any permutation outcome remains retrospective/exploratory.
- Original source-sown species occurrences, site labels, source year and total plot biomass **never permuted**. Never use current-year species biomass as a trait weight.
- Derive a species' guild **only from source planting records**, not from its trait or biomass: for every original species, intersect the sets of original treatment guild flags (grass / legume / other forb) across all original plots containing it. Use only uniquely inferred guilds; all ambiguous/contradictory guild species retain fixed heights and must be reported. A conflicting source does not get silently guessed from taxonomy.

## Pre-response/permutation informativeness gate (locked before new outcome)

- At least **45** original GIFT height species must be uniquely classified into those three guilds;
- each of the three inferred guild pools must contain **≥5** GIFT height species;
- at least **80** of the 174 source-eligible original planted plots must contain **≥2** guild-classifiable height species (so permutation actually changes the plotted trait geometry);
- the exact original cohort and published Kew observed heldout 7-site effect must replay, or **STOP** with reason.

If any structural gate fails, report **HOLD** rather than unrestricted height shuffling or a new post-outcome subgroup. This is not a renewal of older original strict ≥6-site/20-plot guild experiment source gate.

## Single predeclared primary calculation

- Original baseline M0 = quadratic log2 planted richness + three source guild indicators + year.
- M1 = M0 + train-only standardized equal-planted-species **mean log maximum height**.
- M2 = M1 + train-only standardized **mean pairwise absolute difference in log maximum height** among height-covered planted species, from `fit_biodepth_2010_sown_height_fd_biomass_v0_1.py`.
- Same 7 whole-site holdout folds, 174 source plots, 521 complete source responses and unchanged OLS model fitting for every mapping. No loss of original species height completeness; no feature or covariate tuning.
- At each held-out site `s`: `G_s = 1 - SSE(M2,s)/SSE(M1,s)`; primary aggregate `T = mean_s G_s` (each independent site once, not each plot-year).
- **Primary null:** 999 independent guild-stratified permutations of the 88 original source-qualified species-to-Kew-adjusted log height values (only those with uniquely supported guilds), with fixed seed **20261116**. Assign one permuted value per species globally across *all* sites and plots; maintain the original planted community matrix, source guild labels, source biomass responses, source height missingness, and the within-guild marginal distribution of the trait. Ambiguous guild species remain unchanged.
- Each permuted M1 and M2 are **both refitted** in all training sites; no held-out result drives the randomized mapping. Compare `T_obs` to the 999 null `T_perm` using `p_upper=(1+number(T_perm>=T_obs))/1000`; report 2.5%, 50% and 97.5% null quantiles, observed-minus-null-median, and descriptive all-seven site score distributions.
- **Decision (only a conditional label-null finding):** `T_obs > null Q97.5` AND permutation `p_upper≤0.025`. This does NOT replace the previously frozen primary positive-site-count and site-bootstrap CI source gates, both of which fail on corrected GIFT data. Even when this new null passes, it supports only relative *species-to-height predictive alignment beyond those same-guild shuffles*, not general ecological positive FD/biomass effect.
- No second null, no response permutations, no other trait axis, no species/plot/site trimming, no selection of groups by positive result, no new post-hoc threshold; a species-label null is **not** a general test of a causal species–trait–environment response.

## Expected artifacts and reproducibility

- One Python script with a synthetic seed/guild-fixture, using already source-audited geometry/biomass OLS functions. It first verifies source structural/group eligibility and complete original Kew score reproduction *before* computing any null scores.
- One GitHub Actions workflow fetching original, SHA-pinned data directly into temporary private runner storage. GIFT live API contents must exactly reproduce the already recorded 88-trait values/provenance fingerprint, or fail closed. No copyrighted raw biomass/trait table committed to GitHub.
- Archive one machine-readable **aggregate only** JSON: primary null reference, source gate counts, 7 observed site gains, site score distribution diagnostics, source hashes, software version and hard nonclaims.

## Interpretation and literature warning

BIODEPTH's original functional-group planting design is unbalanced (richness and guild support nonorthogonal); **species composition and heights are not randomized independently**. Guild-conditioned shuffling addresses part of that imbalance, but site history, treatment mixtures, biomass edition, trait measurement sources and geographic species-pool structure remain potential alternative explanations. Existing two-axis CWM / species trait association literature warns that a species-label permutation alone does not establish a causal trait–environment relationship. Keep the original corrected 4/7 positive sites and CI spanning zero as the main boundary. Source: https://doi.org/10.1111/2041-210X.13119 and https://doi.org/10.1890/09-1162.1 .

**Original programme hold boundaries remain:** strict BIODEPTH six sites >20 exact-richness plots = 1/8 eligible (HOLD); global sPlotOpen×GIFT×BIEN 201-system K/rho→FD/mass (HOLD); NEON source token (HOLD). This new retrospective test does not unlock those studies.
