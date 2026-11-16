# TreeDivNet Jensen et al. 2026 Figshare: independent species-trait × woody-biomass source-first qualification

**Contract frozen 2026-11-16 before looking at the Figshare article's actual files or numerical outcomes.** This is a distinct forest field-experiment source from historical BIODEPTH, not a third first-party attempt to reopen any old prospectively closed global BIEN/sPlotOpen gate.

## Published public source anchor

- Jensen, J. et al. 2026, *Functional Ecology*, DOI [10.1111/1365-2435.70320](https://doi.org/10.1111/1365-2435.70320).
- Authors' original Data Availability Statement explicitly names **Figshare dataset** DOI [10.6084/m9.figshare.31026004](https://doi.org/10.6084/m9.figshare.31026004), which is expected to be Figshare article ID `31026004`.
- Original study includes **11 tree-diversity experiments in Europe and Brazil, 40 tree species/varieties**, distinct young planted stands (5–15 years). Biomass components include **woody dry biomass (Mg ha−1)**, litterfall (Mg ha−1 yr−1), and understory (Mg ha−1). Keep woody mass and annual litterfall separate; carbon accumulation is a different derivation.
- Original researchers measured individual tree × plot traits, SLA, leaf N, wood density, etc. However the published FDis computation relied on **283 site-specific trait records from monocultures and 17 values substituted from external trait literature/databases**. The published community-level trait values/FDis could therefore be derived, not independently measured in each target plot. **Never equate original measured within-plot species trait, monoculture transplant, and compiled external trait values.**
- The authors already reported positive mixing effects on woody/litterfall biomass and SLA/LAI shifts. Any comparison using this same published dataset is a *different estimator/transport diagnostic* only, not an independent replication of their own published positive study result.

## First pass: metadata and licensing, no ecological effects

1. Read **official anonymous public Figshare API** `https://api.figshare.com/v2/articles/31026004`. Confirm exact DOI and public visibility before interpreting files, collect article/version/date/license, all file names, numeric file IDs, byte sizes, checksums and anonymous-access HTTP statuses. Reject unexpected DOI or non-Figshare redirects.
2. For files that look like source tables, read **only bounded source file bytes** when anonymous public download works and exact source advertised file IDs/checksums agree. Original original rows are temporary in the workflow runner, never committed. No ecological effect coefficient, FD, K, phylogenetic distance or source-by-response fit.
3. Structural data contract for a *new* plot-level trial if public files exist:
   - At least one table with **original experiment/site × original plot × original tree species** and primary measured/averaged individual **positive SLA/leaf nutrient/wood density**; distinguish original direct measurements from literature-filled and from published derived FDis.
   - At least one table with **original experiment/site × original plot woody aboveground biomass** (Mg dry mass ha−1, not litterfall or basal area increment), including true observational/measurement-year identity. The same exact `site×plot` must be in both; no string-heuristic or unverified project aliases.
   - Minimum **≥5 separately named tree experiments** with ≥8 source-eligible plots each, **≥80 distinct original plots**, ≥20 unique directly field-measured tree taxa, ≥2 directly measured species present in original community per eligible plot, and exact year matching or known ≤2-year mismatch documented per plot.
   - If biomass represents allometric estimates, report original DBH inputs/formulas and harvest assumptions; do not call annual gain a standing stock. Species-plot mass weighting derived from the same response year is prohibited as FD predictor.
   - A cross-site K test requiring ≥12 families ×20 species (≥240 species) is logically impossible with only 40 study species even if plot source PASSes. Do not claim that matching original data is enough to test original global trait-memory bridge.

## Expected source-only outcomes and stop rules

- `SOURCE_GATE_PASS`: official source files anonymous access + source-native original traits and plot woody biomass support sufficient at frozen thresholds, with original measurement/literature flags.
- `METADATA_PASS_DATA_GRAIN_HOLD`: anonymous article/file listing works but original plot×species direct trait or original woody-biomass rows not distinguishable (e.g. published summary FDis only, R scripts, figures).
- `PUBLIC_DATA_ACCESS_HOLD`: article is public, but required source files are inaccessible/embargoed, or files exceeding fixed download bounds.
- `ARTICLE_NOT_PUBLIC_HOLD`: API fails/DOI mismatches.
- `SCHEMA_OR_JOIN_HOLD`: row data present but exact original experiment/plot/species keys or taxon/literature-source provenance insufficient.
- `SOURCE_COVERAGE_HOLD`: original site, plot, taxon or year support below frozen minima.
- Any result is **source-only**, not biomolecular, FD or biomass effect. If PASS, *first create a separate frozen original model on an independent study PR*, with leave-whole-experiment-out heldouts, then and only then fit ecological response. Do not change source thresholds to rescue.

## Source-first API safety

- Public GET only, no auth. Follow only official Figshare metadata-download endpoints and exact `https://ndownloader.figshare.com/files/<ID>` original file IDs advertised by API. Validate expected file ID and checksum. Limit per-file compressed/read bytes and per-archive member decompressed bytes; no bulk >30 MB data mining or code execution. Never print transient downloads or source rows. If original file format is unsupported, provide full file inventory and HOLD.
- This source is explicitly independent from BIODEPTH but not new independent test of Jensen 2026's own paper. NASA original NACP TERRA-PNW remains `AUTH_HOLD` (Earthdata 403) and Dryad original local-tree trait file download remains `AUTH_HOLD` (401); cannot bypass.
