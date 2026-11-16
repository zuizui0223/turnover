# TreeDivNet 2026 original species×plot woody biomass source hierarchy QA

**Frozen 2026-11-16 BEFORE observing any DS1 vs DS2 biomass numeric reconciliation results.** The original Figshare 2026 source is publicly reachable and its structural plot matching already examined, but no FD/K/PD ecological response association has been opened on this branch.

## Why this source-only audit matters

The original Figshare file `DS1.xlsx` contains stand woody biomass in **Mg dry mass/ha** at site×block×plot. The original `DS2.xlsx` contains *species-per-plot woody biomass* in the same units and locally collected species-per-plot trait summaries. Data are from Jensen et al. (2026), article 31026004, version 1, not historical BIODEPTH.

A correct trait×community analysis must know whether DS2 contains the **full sown species roster and all stand woody biomass** or only selected measured taxa. Mismatches imply unsampled species, season/source processing, imputation or other design support; do **not** silently carry full-stand biomass as if all source species' traits were measured. This is source data-quality evidence, not a new biomass ecology effect.

## Original source IDs and key units

- Original SHA/MD5-pinned three workbooks and README from `10.6084/m9.figshare.31026004.v1` with file IDs **61014562** (DS1), **61014565** (DS2), **61014568** (DS3) and supplied MD5 listed in source audit. Original file rows **363, 689, 224** respectively (one header each).
- Unique site×block×plot keys; DS2 additionally species; exact site/block/plot normalization only (no fuzzy joins or site abbreviations invented). Existing source audit has 328 DS1×DS2 joined source plots, 340 unique DS2 and 363 DS1 plot keys, with 0 original duplicate sample keys.
- For each original DS1×DS2 joined plot with finite nonnegative `biomass_woody`, verify that **all DS2 original species-per-plot** rows have finite nonnegative woody biomass and compare original `DS1.biomass_woody` against sum over original DS2 species `biomass_woody`.
- Define plot mass reconciliation PASS if `abs(DS1−sum(DS2)) <= max(0.001 Mg/ha, 0.01*abs(DS1))`; otherwise mismatch. Handle original 0 explicitly (never substitute zero for missing).
- Independently check **exact number of distinct original DS2 species** against original DS1 `species_richness` within the same plot; count trait-observed species gaps by SLA, LNCM and WD without assuming missing values are zero.
- Predeclared positive source-data integrity coverage: ≥300 source join plots with both original biomass endpoints numeric and all species source responses present; ≥90% of those plots reconcile woody mass within this 1%/0.001 rule; ≥90% of joined plots have DS2 species count equal original DS1 sown richness. If a rule fails, `SOURCE_SPECIES_MASS_INTEGRITY_HOLD`; **no new FD or biomass models**.
- Report site-stratified aggregate counts of source-reconciled plots and species-ratio matches. Do **not** emit individual original plot keys, species names, measurements, stand carbon, biomass values, or fit any biological effect.

## Remaining hard gates even if mass hierarchy PASSes

- Original source Figshare DS2 has plot×species aggregated traits, not primary **individual-tree measurement rows**.
- Main paper Section 2.5 reports published FDis monoculture-derived 283 and literature/TRY-filled 17, but explicitly says source substitutions confined to FDis, with other trait-mass associations measured. Do not use published FDis as original independent FD without provenance filtering.
- Neither DS1 nor DS2 contains explicit observation year. Need author study sampling protocol to distinguish contemporaneous or lagged measurements; source key alone does not establish year ≤2.
- TreeDivNet 40 species cannot satisfy original ≥12 independent families ×20 species trait-specific K gate. Field trait/biomass relation is independent only of BIODEPTH, not a new replication of Jensen's own published positive mixing result.
- NASA Earthdata and Dryad original source access still `AUTH_HOLD`; historical BIODEPTH/BIEN/NEON original source decisions unchanged.

All source-run code/aggregate summary stays in Draft PR #54; no modification to `main`. This check belongs to source fidelity, not a post-outcome rescue of a desired ecological effect.
