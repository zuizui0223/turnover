# BIODEPTH original 2005: exact-treatment grass+legume versus grass+forb matching, eight-site exploratory audit

Date 2026-11-15. **Post-2005-publication and post-Jena/Cedar exploratory diagnostic**, not novel ecological mechanism discovery. Previously frozen source gate requiring ≥6 sites each with 20 replicates within one single species-richness stratum **remains HOLD (only 1/8 qualified)**. This is a separate explicitly described matched-comparison analysis, not retroactive gate PASS.

## Source and audit trail
- Original [Spehn et al. (2005)](https://doi.org/10.1890/03-4101), [BIODEPTH original CC0 supplement v1](https://doi.org/10.6084/m9.figshare.3565170.v1).
- `Design.txt` Figshare file 5640240, SHA256 `a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a`; `Shoots.txt` file 5640249, SHA256 `cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135`; source methods `suppl-1.htm` file 5640234. Original source content and source row identities were directly downloaded and SHA-checked. Raw plot values are *not* committed.
- The original response is **aboveground standing crop** collected above 5 cm, after one/two quadrat samples, with site-specific harvesting once or twice a year. Dried at 80°C; not universally annual net primary production. The three source years are repeated on the same plots, not independent sites. The original consortium has already published ecosystem effects of legumes/diversity.
- Original `Design.txt` has binary guild indicators **Yes/No**, and `Shoots.txt` uses numeric site location 1–8 while original Design names the sites. Global plot-ID mapping was checked exactly. Original table has grasses *absent* for 122/480 plots; a narrative sentence implying obligatory grasses must **not** supersede the original field treatment table.

## Matched source population selected entirely from original sowing design
1. Start with all source plots originally planted with grass present and exactly **two** guilds: **114** plots.
2. Require both original treatments `grass+legume` and `grass+nonlegume forb` represented within the **same original site × planted species richness × field block**. This leaves **35 original treatment strata, 110 original experimental plots**. Four Irish one-sided treatment plots are excluded before biomass outcomes, not by response.
3. Original 110 plots have 330 source plot×year rows; **327** have valid measured aboveground biomass, and yield **105** usable original matched site×richness×block×year contrasts. Do not replace missing with zero.
4. For each matched stratum and each source year, subtract the **mean log1p biomass** of grass+forb plots from grass+legume plots; average over available years for that original stratum, then average the distinct original strata in each site. Treat all **eight sites equally**, regardless of how many plots they contain. A source-site bootstrap of 10,000 resamples (seed 20261116) captures the uncertainty of the 8 geographic units; it does not create independent new regions.
5. Secondary site-specific fixed-stratum `log1p(biomass) ~ C(exact richness × original block) + C(year) + legume_companion` is clustered on planted original species-composition ID, preserving replicates/years. **Portugal has only three distinct original composition clusters; site regression uncertainty is SOURCE HOLD** while its observational stratum contrast is retained.

## Results: source-site contrast not consistently positive

| Source site | Matched original plots | Original composition clusters | Grass+legume minus grass+forb log1p biomass |
|---|---:|---:|---:|
| Germany | 18 | 9 | +0.552 |
| Greece | 14 | 7 | −0.833 |
| Ireland | 16 | 8 | +0.202 |
| Portugal | 6 | 3 | −1.664 |
| Sheffield | 8 | 4 | +0.156 |
| Silwood | 20 | 10 | +0.135 |
| Sweden | 8 | 4 | +2.223 |
| Switzerland | 20 | 10 | +0.600 |

**6/8 positive, 2/8 negative**. Equal eight-site mean **+0.17147**; **10,000-site bootstrap 95% interval −0.54832 to +0.91837**. Median **+0.17905**, across-site SD **1.12869**. The mean is highly site-sensitive: omit Sweden, mean **−0.12162**; omit Portugal, mean **+0.43368**. No source-wide consistently positive benefit of a planted legume guild is established by this comparison. Wide variation does **not** prove biological absence of a legume effect.

Year-specific source-equal site mean differences: **year 1 +0.04618**, **year 2 +0.43042**, **year 3 +0.03782**. These were calculated *after* the main 8-site estimate; their differences are descriptive, not a pre-registered temporal hypothesis or proof of guild interaction with age.

## Independent verification and source-pinned GitHub Actions
- Original entire 480-plot Design and 1440 plot×year Shoots source verified by SHA256.
- Independent implementation using **standard-library csv.DictReader + manually reconstructed original nested strata**, with no production helper imports, reproduced 110 plots / 35 matched strata / 327 valid row records / 105 matched stratum-years and all eight site contrasts to maximum absolute discrepancy **4.44×10⁻¹⁶**.
- Original year/stratum eight-site mean and 10k bootstrap 95% CI reproducibility differences under 2×10⁻¹³.
- GitHub Actions **[run #43696766996](https://github.com/zuizui0223/turnover/actions/runs/43696766996) SUCCESS**, artifact 14155275309 digest **sha256:dd764ea3cc5a680a8319f141cf780815d92d2be3ad185b924c44fb5e78b2c2d9**.
- Reproduction source `scripts/analysis/replay_biodepth_two_guild_matched_v0_1.py`; verified nonraw result `results/biodepth_8site_source_v0_1/legume_forb_matched_replay_ci_v0_1.json`, full supplementary site composition-cluster comparisons `matched_two_guild_legume_vs_forb_v0_1.json`. No source field values committed.
- Older eight-site *guild count* exploratory `n=230` plots original β site-equal mean **+0.03274**, site-bootstrap CI **−0.13146 to +0.17997**, with only 3/8 sites full-rank for all three guild-identity indicators. Numeric source CI replay [Actions #43696573966](https://github.com/zuizui0223/turnover/actions/runs/43696573966). The guild-count source gate is separately HOLD as described above.

## Boundaries and ecological next step
The matched contrast compares two **planted species mixtures with different guild labels**, not identical species with only a nitrogen-fixation gene turned on or off. Within a given site/richness/block, species combinations, initial trait states, species identity, detection and management may vary. **Neither the source-site contrast nor any year coefficient establishes causal nitrogen fixation, resource complementarity, species selection, phylogenetic memory, quantitative multi-axis FD or worldwide biomass relationships.**

Cross-experiment Jena and Cedar are different in species pools, grass subdivision, source response definition and original treatment replication; do NOT meta-pool their guild coefficients. A genuinely general synthesis needs multiple source-independent geographic ecosystems, original treatment quality and source-matched continuous trait measurements, with every site's within-richness and source support demonstrated before biology is opened. PR #45 stays Draft/unmerged, original BIEN 201-system source QUALIFICATION HOLD and NEON AUTH HOLD unchanged.
