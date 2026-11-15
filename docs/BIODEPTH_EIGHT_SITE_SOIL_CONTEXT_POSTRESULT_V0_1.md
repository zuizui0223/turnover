# BIODEPTH 8-site planted legume vs forb contrast: original soil context

Checkpoint 2026-11-15. This is explicitly **post-response exploratory**, not an independent experiment or a new prespecified ecological finding. The dependent site contrast is the previously estimated source-native difference between grass+legume vs grass+forb at fixed site×original planted richness×field block and two total planned guilds, 110 original plots/8 sites, source DOI 10.6084/m9.figshare.3565170.v1.

## New external-to-outcome source within original BIODEPTH records

The original 2005 `suppl-1.htm` [Table S1](https://doi.org/10.6084/m9.figshare.3565170.v1) contains separately measured *site-level* soil total N %, soil pH, soluble P, latitude and altitude for eight original experimental fields. Original byte SHA256 `20694c14d6b6eccf016294eeae2058479b12c830272a6175a62d32714703c116`.

Site identity crosswalk:
Germany=Bayreuth, Greece=Mytilini, Ireland=Riverstick, Portugal=Lezirias, Sheffield=Sheffield, Silwood=Silwood, Sweden=Umeå, Switzerland=Lupsingen.

Use the **eight site-level means** of the previously frozen guild contrast; do not treat 327 plot×year observations as 327 environmental replicates. Only two soil hypotheses are named a priori to this new analysis (but **after** observing site differences): soil total N % and soil pH, with exact 8! permutations and two-test Holm sensitivity. Geographic latitude is separately **post-hoc hypothesis-generating**, not part of the two-soil family.

## Source-verified descriptive results (n=8 sites)

| Moderator | Pearson r | Exact 40320 arrangement p | Spearman ρ, p |
|---|---:|---:|---:|
| Soil total N % | +0.2113 | 0.61793 | +0.2619, p=0.5309 |
| Soil pH | −0.0218 | 0.95883 | +0.1317, p=0.7558 |
| **Latitude (exploratory after seeing site differences)** | **+0.9217** | **0.00558** | **+0.5952, p=0.1195** |

Both soil tests have Holm adjusted permutation p=1.000; with only n=8, **failure to identify a correlation is not evidence of no N/pH mechanism**.

Latitude's Pearson r remains 0.835–0.953 on leaving each single site out, and plot-count-weighted Pearson is ≈+0.872. However, rank correlation is much weaker and not significant, and the Theil–Sen robust slope 95% interval is **−0.0753 to +0.1748 log-biomass units per latitude degree** (includes zero). Pearson normal-theory p=0.00113 differs from the exact 8! permutation p=0.00558: both are *post hoc*, not confirmatory. Do not select latitude based on how extreme its p-value appears; soil P, C, site climate, original species pool and sampling schedules also covary with geography.

## Why this does not identify an ecological mechanism

- Each geographic site contributes one known previously observed guild-composition effect. The eight experiments are **not a random sample of global latitudes or biomes**.
- Soil sampling depth/soil chemistry methods differ among original study sites; Table S1 values are site/block summaries, not independently plot-matched accessible N forms, and total soil N does not measure active plant N fixation.
- Sweden and Portugal have very small original guild-matched species-composition sample sizes. Extremely different guild contrasts could reflect species identity, phenology, actual realized biomass, site harvest protocols and/or measurement noise.
- Latitude proxies climate, seasonal growing length, local plant species pools and experimental history. Its association is observational with strong confounding and chosen after seeing outcomes.
- Original 2010 species-level biomass and taxonomic source, *same 480 BIODEPTH plots*, is now available and provides a path to test relative species-identity effects. It does not create a second independent BIODEPTH study.
- The original strict BIODEPTH ≥6 site/≥20 plots within ONE fixed richness gate, sPlotOpen×GIFT×BIEN original rho-to-FD gate and NEON credential gate all remain HOLD.

## Reproducibility

Original 2005 `suppl-1.htm` and previous matching result were read from the already preserved official raw SHA+analyzed ZIPs. The reproducible post-result soil script `soil_vs_guild_site_v0_1.py` enumerates all 8!=40320 site-label permutations per environmental axis, computes Pearson/Spearman/Kendall, Theil–Sen and leave-one-site-out robustness, and saves an 8-site table. An independent GitHub Actions source-based run is configured in `.github/workflows/biodepth-eight-site-soil-original-v0-1.yml`. Do not claim it passed until its published run completes successfully.
