# PD–FD and biomass extension | source-first design v0.1
Date: 2026-11-14. **New prospective extension; no new biological outcome estimated.**
Base: turnover organ-K exploratory branch. Does not modify the frozen BIEN 201-system memory study or the retrospective organ-K paper.

## Current verified evidence
- BIEN temporal memory: 201 family×trait systems, 45 families, 12 traits; measured-error-aware family point share ~0.151; trait BLUP out-of-family gain ~+0.006 S3 / -0.0048 prune. This is **not** a proven family-driven FD or biomass effect.
- AusTraits original organ-K (post-discovery): reproductive K > vegetative K in 313/406 S3, 314/397 prune pair comparisons. The same-source 142/101 cohort has 23/13 taxon-selection sign flips. Under equal TOTAL-n random pruning S3 upper-tail 0.0310; after conditioning on per-genus survivor counts S3 upper-tail 0.6047 (prune 0.6822). **Genus composition matters for the original observed K rank, but neither FD nor biomass was measured.**
- Public GIFT 3.1 exact species names: 12,384/13,436 (92.2%) linked for the 760 common-tip pair source population; woodiness available for 10,639. The source joins are NOT independent trait measurements nor biomass.
Sources: docs/AUSTRAITS_TAXON_K_REVERSES_BIOMASS_GIFT_TRY_V0_1.md, results/austraits_organ_paper_gift_original_K_linkage_v0_1/gift_exact_name_growthform_linkage_verdict.json, submission/trait-memory-evolution-rc1/docs/TRAIT_MEMORY_CONTEXT_SYNTHESIS_V0_2.md.

## Single primary new question
**Does a phylogenetic-memory gradient estimated independently for a family×trait system improve the out-of-community prediction of trait FD from phylogenetic MPD, relative to species richness/coverage/environment controls?**

**Unit:** unique sPlotOpen plot × family × named quantitative trait. No extrapolation of a within-family memory estimate to cross-family pairs. Require ≥3 species of that family with an independently sourced, quality-qualified value, abundance coverage ≥0.80, effective abundance n ≥2.5, shared valid phylogenetic tips, and 20 independent eligible plots per family. Pool only family×trait combinations for which a prequalified memory estimate is available; deduplicate sPlotOpen's overlapping three replicates by PlotObservationID. Record all excluded plot-family-trait cells.

**Estimands:** within-family, within-plot abundance-weighted Rao's Q on standardized trait differences (FD) and abundance-weighted mean pairwise patristic distance (MPD, not Faith PD), measured on *identical tips*. Both are non-negative pairwise dissimilarities; scale trait differences within family from independent training population rather than using test assemblages. Compare nested, out-of-group predictive models on held-out plot sources/geographic blocks; assess incremental out-of-sample R² or log score after richness, coverage, plot area and biomes. Cross-fit the memory score to avoid using test assemblage species/traits in the predictor's derivation.

**Primary contrast:** does including the pre-estimated family×trait rho × plot MPD interaction improve out-of-source FD prediction over MPD alone? Compare a conditional trait-label-only predictor and a global rho predictor. Because rho itself correlates phylogenetic and trait distances, **within-sample MPD–Rao association is not an independent ecological mechanism**; only held-out generalization with independent trait measurements is usable as evidence.

## Source-first gate (do NOT open FD outcomes before the gate)
1. Pin exact versions, URLs, hashes, license/citation and keys: sPlotOpen DOI 10.25829/idiv.3474-40-3292; source species composition DT and header (not CWM_CWV as primary FD); trait species values with original study identifiers; phylogeny backbone/tip status; BIEN memory 201 effects from audited frozen artifact.
2. Normalize exact binomials and taxonomic family independently. Report taxonomic species match rate, each trait's raw/observed coverage and overlap with prequalified 201 family×trait systems. Check sPlotOpen PlotObservationID uniqueness, plot size, vegetation layer, dataset, biome, coordinates, date and sampling filters. No invented spatial replication. Primary eligibility is **at least 12 independent families, at least 500 plot×family×trait cells, and at least five contributing source datasets**. Thresholds are a prospective feasibility gate, NOT a significance finding.
3. Traits must be measured (or explicitly marked imputed) and source-provenance audited. sPlotOpen's published CWM/CWV is based on gap-filled TRY, which can reuse phylogenetic information and shared primary studies. Do **not** use the published CWM/CWV as a confirmatory independent FD outcome or treat the same AusTraits/TRY measurement under GIFT as replication.
4. Build family-specific phylogenies and a native-tip sensitivity. No missing-taxon optimistic imputation. Missing trait/phylo coverage and differential representation by growth form/woody status must be audited before fitting.
5. If insufficient eligible source support, stop as **PRE-OUTCOME HOLD**, without lowering thresholds or interpreting the absence of FD outcomes as biology.

## Biomass second-stage (separate response, not a claim today)
Only after the primary source gate: independently measured plot-level aboveground dry biomass (Mg/ha), or annual aboveground biomass increment with known sampling interval. BEF-China public stand *volume* or volume increment is a valuable pilot but must be explicitly labeled m³/ha or m³/ha/year, **not biomass**. Analyze log biomass (or volume separately) ~ FD + CWM + richness + MPD + environmental/stand age/site terms + predeclared interactions; cluster by experiment/site and use held-out plots/species mixtures. Source-/study-overlap controls and provenance audit precede causal interpretation.

## Existing data availability
- AusTraits K and GIFT taxonomic/trait coverage: verified and archived in this repository.
- sPlotOpen: publicly described as 95,104 plots, 42,677 plant species with DT composition + header + CWM/CWV. Verified source: https://www.idiv.de/research/projects/splot/splotopen-splot/ . GitHub mirror https://github.com/ezequielscott/sPlotOpen stores its 149,887,161-byte DT and 24,975,505-byte header as Git LFS pointers; pointer metadata is **not** analyzable plot observations. In this execution environment the original downloadable rows were not obtained.
- Biomass: no verified independent whole-plant dry biomass linked to these plot-family data yet. https://data.botanik.uni-halle.de/bef-china/datasets/640 offers stand volume data, not biomass.

## Next allowed operations
Execute the source-geometry preflight in `scripts/analysis/pd_fd_source_gate_v0_1.py` on source-native data after provenance-preserving normalization; make a one-page coverage report. Only a PASS authorizes real FD calculation and time/space/family transport testing. Keep the present frozen papers unchanged.

## Verified source audit checkpoint — 14 November 2026

- Original official iDiv ZIP `3474?version=5047`: HTTP 500 twice from Actions; the failure was transport, not an ecological gate. No attempt to silently call that file verified.
- Alternative version explicitly pinned: public Git LFS mirror `ezequielscott/sPlotOpen` commit `1bfcad669ae1a7e6f0a419159dd3051e83bdd26b` (manifest dataset version 5806). The mirror is **not** asserted identical to the failed official v5047 archive.
- Successful source-only [GitHub Actions #43571467971](https://github.com/zuizui0223/turnover/actions/runs/43571467971): original sPlotOpen composition has **1,943,306 rows** and **95,104 unique plot IDs**. The header and gap-filled CWM/CWV each contain **95,104 rows**. Composition fields: `PlotObservationID, Species, Original_species, Original_abundance, Abundance_scale, Relative_cover`. Header provides `Dataset, Biome, Releve_area, Latitude, Longitude, is_forest, PlotObservationID`, enabling appropriate quality controls.
- SHA256 of **temporary three-file mirror packaging**, not the official ZIP: `f593719ea187a660fdc1d2c41e5516445cb8581655d84f4b1b2c028eeb4778a6`. Inspect exact member metadata in `results/pd_fd_source_gate_v0_1/splotopen_mirror_schema_probe.json`. No underlying raw public rows committed.
- **This is an actual source-table availability PASS, not a functional-diversity or biomass finding.** The plot×family×trait eligibility gate still requires an accepted-name/family crosswalk, original trait-source audit and valid native phylogenetic tips.
