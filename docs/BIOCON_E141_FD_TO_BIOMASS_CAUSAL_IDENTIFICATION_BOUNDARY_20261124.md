# BioCON E141: source chronology and FD→biomass causal-identity boundary (2026-11-24)

**Original data provenance audit, not a new biological result.** BioCON E141 is one distinct field experiment relative to the existing Cedar Creek E120 analysis. The Huang et al. (2025) CE/SE/richness findings from this same field experiment have already been published.

## Original sown-design source audit

The original author Figshare v3 CSV is MD5 pinned (8185b8effca37c8740ad065c53eb75d2). Its 70 columns include original physical Ring and Plot, calendar year/season, 16 species-specific planting indicators, 16 species biomass columns and absolute aboveground total. The scripts currently read **only source identifiers and planting indicators**, never numeric responses.

The same 371 physical plots are sampled 24 years (1998–2021), twice annually. Their original source design partitions into 128 main (M) monocultures, 60 main 4-species, 60 main 9-species, 48 main 16-species, 12 main bare, and 63 supplemental (S) 4-species plots. Six CO2 ring-level randomization units are not 371 independent CO2 units. Original planted flag cells are exclusively 1 and blank; interpreting blank as unsown yields exact agreement with original CountOfSpecies for all 17,808 rows (not an independently supplied literal codebook).

## Source identity and how to calculate genuinely comparable signed net diversity effect

Require at least two independent physical original monoculture plots for each of 16 species x four CO2/N settings (=64 cells), not multiple years from one plot as separate monocultures. The source-only monoculture preflight counts this before reading biomass.

For the same actual original year, season, CO2/N and eligible mixture composition, E = sum_i p_i M_i, with **actual source sown proportion p_i** and matching context monoculture biomass M_i. Source planting *presence flags* by themselves **do not prove equal p_i**. E and B must be in the same annual/seasonal units, with water/warming treatments controlled where introduced. Signed NDE = B-E and NDE=CE+SE only if an exact author-compatible Loreau-Hector definition is reconstructed. Signed components may be negative and are not the published relative ratio B/E; neither signed NDE nor CE/SE can be simply logged. Published CE/SE re-computation is not a new independent biological discovery.

## Direct SLA versus source-substituted FD, and temporal leakage

The author's public 2024 original source code [Kimmel/Ohlert original CDRTraitCleaning.R](https://github.com/kaitkimmel/FDiv/blob/e61c8814f3fc8e8fa7cac6141ee462c3e8b22554/R/CDRTraitCleaning.R) groups E141 monoculture trait measurements **by species x CO2 x N and averages across available observation years**. It does not impose a requirement that a trait observation be strictly earlier than a focal target year's biomass. If used to predict biomass in 1998–2021, this whole-period aggregate can contain **measurements obtained after the target year**, so it is not a pre-sowing or time-pure predictor by default.

The original 2024 author code explicitly describes direct E141 source SLA as **56/64 treated species cells**, with two E120/Big Bio SLA substitutes (*Bouteloua gracilis*, *Poa pratensis*). Original seed mass coverage is **44/64**, filled for five species from Big Bio; root C/N coverage **61/64**, with other Anemone treatment contexts copied. Four available processed treatment tables each have 16 species, but **they are filled tables, not proof of 64 independent direct SLA or seed measurements**. Exact source code/derived table blob SHAs are recorded in [source provenance audit](../results/biocon_e141_ohlert2024_source_trait_provenance_20261124_v0_1.json).

Before any FD effect, require original EDI traits with source observation dates, actual same-group trait measured *before the focal response*; direct E141-only species and trait values, with no E120 substitutes; and source plots whose planted species trait coverage exceeds an outcome-blind threshold **at least 80% with at least two truly observed species**. Original all-period mean trait values do not meet historical prediction chronology unless underlying measurement years are certified. Avoid treating Big Bio/E120 data reuse as an independent E141 trait source.

## Decision on future statistical estimand

Only after sown-treatment plot keys, mono baselines, original trait timing and source-eligible mixture counts pass, freeze the exact E141 M-plot response accounting. Evaluate M0 (species richness, planted species CWM, CO2, N, ring, year, management) versus M1 adding directly measured plant FD on source-eligible independent **assigned species composition** holdouts; never put repeated years of one held-out composition in the training fold, or interpret thousands of repeated plot-years as experiment-level generalization. Ring-level uncertainty (only six whole-ring CO2 replicates) and at most one independent field site must be retained.

Continuous FD is derived from chosen species identity and phylogeny; its regression prediction beyond richness cannot alone establish an **FD-only causal intervention**. Nor can 16 species in one site identify family-specific BIEN/AusTraits trait K/rho as a mediator. No new biological outcomes or source response values have been opened in this branch.

**Result status: source key/provenance checks progressing; FD→CE/SE→absolute biomass causal claim HOLD pending original temporal trait measurements and source-matched mono baselines.** Evolution RC4 and the 21-claim registry remain untouched.
