# Independent original forest trait × biomass source eligibility: Africa and BEF-China

**New programme isolated from completed original BIODEPTH PRs #46–53 and TreeDivNet Jensen 2026 PRs #54–57. Source contract fixed 2026-11-18 before original new candidate files/columns are opened, and before any new FD, phylogenetic K, PD or forest biomass effects.** The new study cannot change historically terminal original BIEN×sPlotOpen, BIODEPTH or NEON source-gate decisions.

## Goal and exact source priority

We need an **independent original species×plot trait source and original per-plot biomass**, including taxonomic identities and a group structure permitting honest out-of-region validation. Original author papers have already studied diversity/biomass: source admission is **not** independent positive confirmation of their ecological claims.

### Candidate A: open Zenodo archived African forest inventory (priority for geography)

**Noulekoun et al. (2023), GEB**, doi [10.1111/geb.13800](https://doi.org/10.1111/geb.13800); public archive [Zenodo #10045492](https://zenodo.org/records/10045492), reproducing archived source doi [10.5061/dryad.dfn2z3582](https://doi.org/10.5061/dryad.dfn2z3582). Paper reports **276 original inventory plots / 7,993 original trees / 207 original species, five countries (Benin, Burkina Faso, Ghana, Togo, Ethiopia), 2014–2020, multiple aridity classes**. Study published original positive richness/structural diversity/CWM drivers; NOT a newly observed ecological effect. Zenodo offers:
- `dataall_Noulekoun_GEB.csv`: reported *plot-level analytical variables* (AGB, species richness, CWM traits, FDis, structural metrics, country/climate/etc.), public originally listed MD5 `60fc555c8e2942af432b09d3aeb84d57`;
- `Description_abbreviations_Noulekoun.xlsx`: source variable metadata, advertised MD5 `6779d4c95a31e254f33e6c2e421d1f38`;
- `R_script_Noulekoun_GEB.r`: original author statistical scripts, advertised MD5 `f3763db40ac72598e1138a0ce48006f4`.
Use **official public Zenodo API** `https://zenodo.org/api/records/10045492`, verify exact record and advertised names/sizes/MD5, and bounded original-file anonymous GET through advertised Zenodo-only `/api/records/.../files/.../content` or `/records/10045492/files/...?... ` URLs. Never alter site/country labels; avoid DOB/coordinate exports.
  
**Prior to effects, source grain must be measured:** row count, unique plot IDs, actual study country/forest type diversity, original biomass field and unit, missingness, whether genuine **species×plot trait observations and species identities** exist (vs *already-derived* CWM/FDis). If **only plot-level CWM/FDis and richness** are published, then **`NO_ORIGINAL_SPECIES_TRAIT_GRAIN_HOLD`** for a new K→FD→mass test regardless of 276 plots. Do not reverse-engineer individual values from community means.

### Candidate B: BEF-China 2025 tree inventory and LiDAR/production

Deng et al. (2025), *PNAS* doi [10.1073/pnas.2506750122](https://doi.org/10.1073/pnas.2506750122), original data declared in article at [Figshare article #29592203](https://doi.org/10.6084/m9.figshare.29592203). Authors report **482 planted plots / 38,088 individual trees, two BEF-China sites, 4-year repeated growth monitoring (2021–2024)**, woody biomass derived from basal diameter, height and a deliberately **constant wood-density parameter 0.52 for all taxa**, so NOT an independent species-WD biomass association. Annual aboveground woody biomass is estimated from those dendrometric inputs, not destructive measured carbon.
  
Fetch official public metadata `https://api.figshare.com/v2/articles/29592203`; verify exact article ID plus root DOI or its numeric `.vN` version and original file manifest, size, checksums and anonymous public availability. Inspect only small tabular files; **no more than 10MB per original file or 30MB across the article**; skip 3D point clouds/large LiDAR binary sources. Classify source fields by original measurement grain:
- `site×plot×year×species/treeID` counts/identifiers, actual species-level directly measured leaf traits (SLA, N, wood density etc.) and study-site provenance (vs modelled CWM, simulated, literature species means).
- `site×plot×year` original measured stock and/or year-to-year change/production, with documented time/mass units.
- Does original source enumerate **both BEF-China sites** (only two original experimental environments), not 482 independent regions. If only plot×year biomass, vegetation and LiDAR, **`DIRECT_FIELD_TRAIT_GRAIN_HOLD`** for K/FD biomass despite excellent original woody source.
- Even if original functional traits exist, only **two** genuinely independent original experimental sites; a ≥5-site out-of-location generality claim is **`INDEPENDENT_SITE_SUPPORT_HOLD`**. Repeated years are not independent ecosystem locations.

## One consistent pre-outcome source gate

To authorize a NEW *independent* species-trait FD/mass association across natural source regions, require **all**:
1. ≥80 unique original source plot IDs, **≥5 independently named geography/forest-study blocks each with ≥8 source-qualified plots**. Countries may reflect climatic variation but **countries alone are not automatically independent field stations**; source forest/study-block identity must be documented, not fabricated.
2. ≥2 *independently source measured* positive trait values for distinct original species within each plot, with **≥80% measured original planted/community species coverage per plot**, and ≥30 unique original measured source taxa. No reuse of derived CWM/FDis as species-level primary observations. If original local measurements are per species across sites but not per-plot, report `SPECIES_SOURCE_NOT_PLOT_LOCAL_HOLD` separately.
3. A plot-level woody aboveground biomass endpoint (standing stock) or actual production/increment endpoint, with **exact original site×plot×year** identity and original units. No combining Mg C ha−1 with Mg dry matter ha−1, basal area increment and annual production into one outcome. No same-year species biomass used to weight or create source predictors.
4. Original measurements/provenance support original trait and biomass year alignment ≤2 calendar years, or report `TEMPORAL_ALIGNMENT_HOLD`. Site-level timing does not prove individual leaf/tree sampling IDs.
5. No original group that source article declares a manipulation of *genetic diversity only* or a cumulative stock/harvest response can be treated as a comparable tree-species-richness/standing-stock sample. The prior TreeDivNet Jensen original 11 sites are not automatically independent of other datasets; do not overlap source plot IDs/experiment names.

**Additional original evolutionary trait memory K gate is independent:** original ≥12 families ×≥20 original independent species per family implies **≥240 source species**, so neither reported Africa (207 total) nor BEF-China (40) can directly meet it, even if every taxon is included. External independently estimated family K could support an explicitly different later study only after strict family identity and traceable source comparability checks; don't silently equate tree PD with trait memory K.

## Output, accuracy and stopping

Produce official DOI/version access records, file inventory and checksums; original row/column/identifier **aggregates only**, no raw copyrighted source data in Git or unexpired links. For every source return `SOURCE_GRAIN_PASS`, `SOURCE_METADATA_ONLY`, `PUBLIC_DATA_ACCESS_HOLD`, `ORIGINAL_SPECIES_TRAIT_GRAIN_HOLD`, `NO_ORIGINAL_PLOT_BIOMASS_FIELD_HOLD`, `INDEPENDENT_SITE_SUPPORT_HOLD`, `SOURCE_UNIT_OR_PROVENANCE_HOLD` or `TECHNICAL_HOLD` with observed counts, not guesses.

**No biological FD–biomass, K, PD, causal or cross-study prediction effects until all gates and a separate new outcome contract pass.** If original data do not qualify, preserve genuine data-quality findings and prefer a truly new source instead of changing thresholds within the same data to obtain a desired sign.
