# BIODEPTH: original native-tip source eligibility selects an unusual community design, not a demonstrably harmful tree placement

**Source-run 2026-11-16; retrospective plot-resampling diagnostics.** Contract `docs/BIODEPTH_NATIVE_PLOT_SELECTION_NULL_FROZEN_V0_1.md` was committed before THESE 499+499 randomized-subset outcomes, but the historical biomass effect and the native-102 source plot population were known. This is not a prospectively independent study, an ecological randomization of plant communities, or a demonstration of a causal diversity effect.

## Upstream original-data and scientific boundaries

The original 150 GIFT-height × GBOTB-S3 source-qualified planted plots come from seven original Hector2010 BIODEPTH field sites with **449 numeric Community plot-year standing-biomass responses**, 84 jointly matched species across 17 families. Native-backbone support qualifies a fixed **102 of those original planted plots**, 305 numeric source Community plot-year responses. Prior parent Draft PR #52 original entire-site holdout refits were replayed to exact site SSE: full 150 sample PD increment **−1.451%**; same 102 native-qualified plots with *full-S3 trait/PD features* **−4.008%**. The two source response editions of BIODEPTH (Spehn 2005 Shoots and Hector 2010 Community) were not mixed; only original 2005 *planting design* used for covariates. No new family-specific Blomberg K or BIEN memory-rho data entered this analysis.

## Mandatory pre-outcome source-only eligibility: 150 versus native-selected 102

| Observed planted source community feature | Native-qualified 102 plots | Excluded 48 plots |
| --- | ---: | ---: |
| Mean planted species richness | **8.31** | 6.42 |
| Proportion with >8 planted species | **25.5%** (26/102) | 12.5% (6/48) |
| Mean log-height CWM | +0.0233 | +0.0067 |
| Mean pairwise absolute log-height difference | **0.3465** | 0.3056 |
| Mean pairwise S3 patristic distance | **193.46** | 156.48 |
| Plots with all three planned grass/forb/legume guilds | **60/102** | 22/48 |

These measures are descriptive **original source eligibility/composition diagnostics**, not source-plot estimates of a biomass treatment response. The native 102 set differs from the omitted 48 in planted richness, planted group makeup, height dispersion and original phylogenetic breadth. Source selection is not random and cannot be assigned a causal effect from those means.

## Primary: 499 random source plot subsets matching the exact seven original field quotas

Randomly select 102 original plot IDs, drawing within each original field exactly the observed native-qualified counts (Germany14, Ireland26, Portugal8, Sheffield18, Silwood14, Sweden14, Switzerland8). For every draw, retain original biomass rows by whole plot/year, and refit the **same** seven held-out-original-field full-S3 M2 (quadratic richness + original three planned guild indicators + year + mean log height + height FD) versus M3 (+phylogenetic MPD) model. Fixed seed **20261116**, 499 draws, require >=475 valid. Original source responses and species heights were never permuted.

- **482/499 eligible fitted draws**; 17 fail `RANK_DEFICIENT_TRAINING_MODEL_2` and were retained as failures, **not re-drawn**.
- Median PD incremental heldout SSE prediction gain across valid random subsets: **−1.486%**.
- Random reference 2.5–97.5%: **−3.933% to +1.317%**; only 74/482 random samples had point-positive gains.
- The *observed native-support selected 102 original plots* yielded **−4.008%**, which is **−2.523 percentage points below** this valid-draw median.
- **11 of 482** valid random subsets had gain as low or lower; add-one descriptive lower-tail reference **(1+11)/(482+1)=0.02484**.

Thus, **given original site counts alone**, the observed native-eligible subset is on the low tail of the distribution of possible 102-plot samples. This is a descriptive source-selection benchmark and **NOT** a causal randomization p-value for biological selection or a predeclared biomass general effect.

## Secondary: exact site × original sown richness × planned guild-vector source matching

The stricter source-only eligibility requires ≥10 freely substitutable native-selected plot IDs in ≥3 sites. It PASSED with **24 movable selected original plots across 8 partially replaceable strata in 5 sites**, among 47 exact source strata. Other original plots are necessarily fixed by their site/richness/guild design. Deterministically draw **499** source strata-matched alternative 102-plot combinations, seed **20261117**, and fit the same held-out-field models without changing original species attributes or Community outcomes.

- **499/499 valid refits**, 0 rank failures. Every draw has 305 numeric plot-year responses.
- Conditional null median PD incremental field-heldout SSE gain **−5.519%**.
- Conditional reference 2.5–97.5% **−9.591% to −2.943%**. All 499 matched alternative samples yielded a *negative* gain.
- The observed native-selected 102-plot gain **−4.008%** is **+1.510 percentage points above** the exact-richness/guild-matched median.
- **426/499** matched resamples had gains at or below observed; add-one lower-tail reference `427/500 = 0.854`. The original subset is **not unusually negative** once exact planted richness and planned guild composition are also fixed.

**Scientific diagnosis:** The apparent native-source-selection outlier **disappears when the original planted richness and functional-group-vector support is held constant**. This makes original study design/population support a credible explanation for the shift between the 150-plot and 102-plot predictive results. More generally, including richness and guild flags as model covariates does not automatically make predictions transportable to a different mixture of richness/guild strata. However, the alternative conditional draws have only 24 movable selections, the two resampling references are different conditional populations, and original sampling was not randomized. Therefore do **not** interpret the difference between null medians as an identified mediated effect or causal partition.

## Outcome and no-go decision

The project has repeatedly failed to establish a transferable independent positive phylogenetic breadth or one-axis height-diversity increment for original BIODEPTH standing biomass under the prespecified seven-field holdout tests. This new null test identifies a concrete *sampling-design sensitivity* instead of rescuing a biomass effect.

A direct same-plant-family trait-specific K→FD→biomass effect cannot be established from the local source 84 taxa across 17 families under the original ≥20 species × ≥12 independent families structural standard (at least 240 species would be needed for 12 non-overlapping families). Externally estimated independently sourced family K would have to pass a new explicitly separated provenance/portability gate, and that is not attempted here. The previously closed original 201-system BIEN/sPlotOpen, exact-richness >=6 BIODEPTH-site, and NEON auth gates remain HOLD.

**Decision:** Close this retrospective BIODEPTH selection diagnosis after archival verification. Do **not** start another outcome-driven threshold search or claim plant evolutionary memory causes biomass differences from these data.

## Permanent provenance

- Verified original-data GitHub Actions: https://github.com/zuizui0223/turnover/actions/runs/43831214966 (**SUCCESS**).
- Full nonraw aggregate artifact #14209062451 digest `sha256:b0e9830971a2ed2b910d0bdfa0d310824c9bcc8e400bca881d964f94eee5149a`.
- Frozen source/label controls: `docs/BIODEPTH_NATIVE_PLOT_SELECTION_NULL_FROZEN_V0_1.md`.
- Source-pinned original data and null Python: `scripts/analysis/audit_biodepth_native_selection_site_quota_v0_1.py`.
- Persistent output/summary: `results/biodepth_2010_species_source_v0_1/native102_selection_benchmark_source_verified_v0_1.json`.
- Single original experiment programme; source plot/year rows, GIFT numerical source traits, individual named sample identities and original S3 distance matrices are not committed to Git. All branch changes remain in a Draft PR stacked above #52; `main` unchanged.
