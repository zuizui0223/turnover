# Independent measured-biomass sentinel — Jena 2003 — pre-outcome source gate v0.1
Frozen: 2026-11-14, prior to opening the proposed Jena raw data values for statistical inference.

## Relationship to previous analyses
- This is an **independent, separately scoped** observational/experimental *feasibility and eventual benchmark*; **not** rescue of the closed sPlotOpen × GIFT × BIEN 201-system >=90% exact-match and >=12-family gates.
- The original primary question (predicting PD-to-FD transport with family×trait memory) remains HOLD in PR #39. Do not interpret within-Jena group-biomass effects as across-family memory, community phylogenetic diversity, or globally transferable ecology.
- No modification to original BIEN/AusTraits effect or publication branches.

## Registered sources and objective
1. **Primary measured biomass source:** Buchmann & Temperton (2015), *Aboveground community and species-specific plant biomass from the Jena Experiment (Main Experiment, year 2003)*, DOI https://doi.org/10.1594/PANGAEA.846317 . 82 experimental plots (20 m × 20 m), sown pool of 60 species from four predefined functional groups (grasses, legumes, tall herbs, small herbs), direct 70°C oven-dried harvests twice in 2003, four 0.2 × 0.5 m quadrats per plot per harvest. Reported biomass g/m², not volume or allometric proxy.
2. **Composition / assignment:** original 2002 experimental plot allocation and 60-species functional-group identity from the associated PANGAEA Plot Information and Treatment Description, not derived from 2003 observed species biomass. The source explicitly distinguishes empty cells for species *not sown* from numeric -9999 for failed measurements. Do not treat missing observations as zero.
3. **Optional later trait values:** separately sampled species traits with original field-study DOI, matching definitions, units and original-study/source independence. No use of 2015 plant traits as if measured in 2003 without explicit temporal-transfer restriction.
4. **Potential independent second cohort:** NSF NEON herbaceous clip harvest DP1.10023.001 direct dry mass by functional group + DP1.10058.001 plant species cover in matching plot/subplot/time. NEON product description alone does **not** demonstrate physical coregistration or independent biomass at species level. Audit separately; never use inferred tree AGB from DP1.10098.001 as directly harvested biomass.

## Tier 0: source integrity (current task, *no outcome*)
- Download official PANGAEA 846317 tab-separated text using content negotiation; do not use an HTML or login page as data. Pin SHA256, exact row/column counts, metadata footer, original column labels, date field identities, number of distinct plot IDs, biomass response column and species-specific measured columns. Retain only summary metadata and SHA256, not the full table.
- Verify that at least 70/82 experimental plot IDs are present with at least one valid measurement, both May and August seasons are represented by source rows (not inferred from metadata alone), and the community dry-mass response is a numeric nonnegative g/m² value with -9999 treated as missing. If not, stop as SOURCE_HOLD.
- Distinguish plot, harvest/campaign, subsample and replicate. Do **not** count 4 quadrats × 2 harvests as 8 independent plots. Do not sum 2003 season standing biomass indiscriminately as annual NPP.
- This original Jena direct-biomass proof-of-availability does not by itself qualify trait diversity computation or any predictive model.

## Tier 1: functional-diversity data preflight (no outcome opening)
- From original frozen sowing schedule map exactly 60 species to four functional groups, and plots to sown richness and functional-group richness. Require ≥95% unambiguous crosswalk for 60 sown taxa, ≥70 plots, at least three richness levels, at least two functional-group richness levels, and no treatment alias violations. Thresholds are source feasibility, not p-value gates.
- Verify independent trait values (height, SLA, or leaf area) only when full source references, units and source-overlap matrix exist. Group richness is a coarse *categorical functional-diversity proxy*, not continuous Rao's Q/FDis and not the predeclared sPlotOpen PD–FD estimand.
- No use of realized species-specific biomass to create the predictor community weights for a regression with total biomass response: would embed the outcome in the predictor.

## Tier 2: analysis only if Tier 0 and Tier 1 pass
- Primary, separately scoped sentinel: independent plot-level May 2003 biomass (g/m²) ~ log(sown richness) + planned functional-group richness + original field block; use randomized assignment where verified. Additional August as repeated-measure sensitivity with random plot intercept; family/plot is the unit of replication, not individual species or quadrat. Report adjusted group richness estimate and plot-blocked bootstrap/CI.
- Out-of-plot validation compares species-richness-only vs richness-plus-functional-group-model; group richness model is tested on held-out plot IDs. Do not claim mechanistic causality solely from an association or fold-split. Prespecified null is 0 incremental predictive gain; negative or null counts as legitimate completed result.
- Secondary (only if directly measured independently and enough species): effect of taxon-only vs true quantitative trait FD. Do not introduce new predictors post-outcome to find a positive result.
- No multiregion/macroevolutionary generality: a single Jena field experiment is an *experimental sentinel*, not a global macroecology validation.

## Mandatory result boundaries
- Evidence of **actual harvested dry mass availability** is a meaningful positive source gate; not automatically a positive ecological FD/biomass relationship.
- sPlotOpen main HOLD, BIEN rho, AusTraits reproductive/vegetative K, and memory portability conclusions remain untouched.
- Treat source eligibility failures as HOLD without changing frozen thresholds; require a new, explicitly prospectively scoped source programme for any different population.
