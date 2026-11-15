# BIODEPTH 2005 vs 2010 response numerical discrepancy profile — source-only v0.1

Checkpoint 2026-11-15, after original hierarchy audit was read; this is a **source-quality follow-up**, not a preregistered biological analysis.

## Verified prior finding
- Original 2010 hierarchy data are additively exact in all complete source plot-years: sum Species→Community 1423/1423; sum Group→Community 1434/1434. The separate 2010 species source and mixed hierarchy Species rows agree 5802/5802 including original missing flags.
- Original 2010 Community vs original 2005 `Shoots.txt` shares 1440 plot×year keys and has 1415 paired numeric comparisons. Only 243 pairs agree at absolute tolerance 1e−5, but median |difference| **0.125 g/m²**, median positive response ratio very close to 1 (2010/2005 = 0.9999926), and maximum difference 1170.4.
- Therefore the 1172/1415 `1e−5` mismatch count alone **does not prove different biomass endpoints**; rounding and site-specific treatment errors are both possible.

## Next source-only questions (do not open ecological effects)
- Original PANGAEA/Figshare 2005 `Shoots.txt` SHA256 `cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135`.
- Original Hector et al. 2010 `BiodepthBiomass.txt` hierarchy with `level == Community` SHA256 `9d95e65295bf6014e753f474dffa09036718b6b54ad5e1d4eea41c1dde76f886`. Previous original-author hierarchy verified 1440/1440 plot×year keys.
- Compare **only the 1415 complete source plot×year pairs**. Do not replace missing with zero, do not add separate Species/Group/Community hierarchy rows.
- Audit absolute deviation histogram thresholds <= 1e−5, .01, .05, .1, .25, .5, 1, 2, 5, 10, 50, 100, 500, 1000 (g/m²); relative deviation to `max(abs(original2005), abs(original2010))` <= 0.01%,0.1%,1%,5%,10%,100%; separately count one-version-zero/other-version-nonzero. Publish median, p90,p95,p99 of |difference| by original study site and year; aggregate only, never expose plot-level response values.
- Investigate whether errors concentrate in a few original sites/years, source validity zeros, or unusually large >100 g/m² discrepancies. Preserve source values unmodified; numerical incompatibility threshold must be defined by scientific response usage, not chosen to maximize model replication.
- Do not yet calculate FD, species traits or phylogenetic relationships. Even when most discrepancies are rounding scale, the raw 2005 and 2010 response tables must not be silently mixed without source-identity and outlier policy.

Completion criteria: original source SHA verified, all 1440 plot-year keys uniquely matched, 1415 numeric pairs verified, histogram bins sum consistently to 1415 and site/year tallies agree. Return SOURCE_AUDIT_COMPLETED_WITH_DISCREPANCIES or SOURCE_VALUES_NEAR_IDENTICAL_EXCEPT_OUTLIERS, not a universal ecological inference.
