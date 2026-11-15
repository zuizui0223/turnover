# BIODEPTH 2005 vs 2010 harvested biomass hierarchy QA (source-only, 2026-11-15)

Original 2005 Figshare source `Shoots.txt` records 1440 plot×year community biomass values (21 original missing, 1419 numeric). Original 2010 Hector et al. `BiodepthSpeciesBiomass.txt` records 5802 species×plot×year rows, 71 original nonnumeric, and `BiodepthBiomass.txt` has 9816 rows with explicit `level=Species|Group|Community`.

**Confirmed previous source keys:** 480 exact original plot IDs, eight original sites, original 3 years, 1934 sown plot×species pairs, 103 original Linnaean taxa corresponding to 186 site/ecotype codes. The original 2010 dictionaries are internally consistent; seven separate R-repackaging species abbreviations remain unresolved and are not required for this original-source hierarchy comparison.

**Critical blocker:** in the earlier sum-of-2010-species versus 2005-Shoots check, only 243/1415 comparable plots×years matched numerically; 1172 differ (max absolute difference 1170.4). This is SOURCE DEFINITION HOLD, not a tested ecological effect. The discrepancy may be a 2010 processing change, a missing species contribution, or different standing crop / NPP aggregation. Do not infer the cause from the discrepancy alone.

## Locked source audit, no biological FD or guild effect

Original file identities pinned:
- `Shoots.txt` (2005 original Figshare v1) SHA256 `cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135`.
- `BiodepthSpeciesBiomass.txt` (Hector 2010 original) SHA256 `ebe677c639ef4603bc1ed50d49e7440588683e7696be230c0cbfff7d6b22b816`.
- `BiodepthBiomass.txt` (Hector 2010 original hierarchy) SHA256 `9d95e65295bf6014e753f474dffa09036718b6b54ad5e1d4eea41c1dde76f886`.

Treat **plot×year** as original biological unit, and levels as nested/mutually redundant responses, NEVER sum across levels.

For each original plot×year, compare:
1. Species-level 2010 `BiodepthSpeciesBiomass.txt` to Species-level 2010 hierarchy by original species code (both rows and values, missing flags).
2. Sum *complete* nonmissing Species level vs independently reported Group level sum (only complete groups) vs one Community level 2010 response.
3. 2010 Community value vs 2005 Shoots response (year- and site-specific agreement).
4. For each site×year, publish **aggregate only**: number comparable, exact agreement within 1e−5, median and maximum absolute numeric differences, median of ratios for strictly positive pairs; missing/negative counts. No individual plot-level biomass values, correlations with species/FG traits, or ecological regressions.

Rules: no missing→zero substitution; preserve all valid zeros. Group missing sentinel remains missing; if any group/species source not complete, labels may be partial. Verify 2010 source internal values only by original plot/year/species, not numeric `mix` from secondary R package. Stop if any raw hash changed, 2005 1440 IDs differ from 2010 1440, any duplicated Community rows, or mixed-hierarchy values exceed the published 9816 rows. If 2010 internally consistent but cross-edition differs, flag original-version incompatibility; future FD/biomass studies must use **one internally coherent 2010 response** and separately assess its independence from predictors. Do not overrule previous 2005 guild association or frozen original source HOLD.
