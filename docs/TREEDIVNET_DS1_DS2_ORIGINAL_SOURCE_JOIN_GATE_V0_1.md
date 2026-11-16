# TreeDivNet 2026 DS1–DS2 exact original plot/species join: source-only contract

Frozen 2026-11-16 **before numeric original source-row join outcomes**, following public Figshare article and workbook header checks in Draft PR #54.

## Fixed provenance

Official Figshare article 31026004, version 1, DOI `10.6084/m9.figshare.31026004.v1`. Four public source files original MD5:
- README.txt (#61014400, 8,130 bytes, `8fd3551d0a2b69fb9dca54b7cdbca422`)
- DS1.xlsx (#61014562, 103,401 bytes, `ab691e410093885d08ad8738cbdedf91`)
- DS2.xlsx (#61014565, 92,898 bytes, `571e0ef965e28b8b31dd27f971efeff6`)
- DS3.xlsx (#61014568, 51,698 bytes, `888d7a3d156be451966be3ca34b7892f`)

Only DS1/DS2 are directly inspected for this gate, and official README for semantic definitions; DS3 is published net diversity effect (NDE), not an independent raw measured-trait/woody biomass sample. Existing checked workbook headers: DS1 original `site,block,plot,treatment,species_richness,species_composition,biomass_woody`, plus community CWM. DS2 original `site,block,plot,treatment,species_richness,species_composition,species,biomass_woody,SLA,WD,LNCM,LNCA,LPCM,height_increment`, with 363 and 689 nonheader rows respectively (subject to exact source row checks).

## Intended estimand and grain

- **Primary join identity:** original `site × block × plot` after whitespace-only trimming of text and canonical numeric `123.0 → 123` formatting **only** for number-coded IDs. No approximate/fuzzy/spatial matching. Verify `site×plot` alone would not silently collide; add block to avoid conflating plots from different blocks. No code may fabricate or infer omitted year.
- DS1 must have one unique original row per `site×block×plot`. DS2 must have unique original `site×block×plot×species` rows or report original duplication. Check exact `treatment`, `species_richness`, `species_composition` values agree across matched rows/plots before any effect use. Site is the independent experimental cluster, not plot-year or tree individual.
- Count original unique site, block, plot and species identities, matched DS1/DS2 plots, unmatched rows/plots, trait-column nonmissing/positive/invalid rates, and source `biomass_woody` numeric-present/invalid count, **without correlating or regressing any trait and biomass outcomes**, and without exporting any original source rows/species/plot labels.
- Per plot among exactly matched DS2 species rows: count ≥2 positive `SLA`, ≥2 positive `WD` and ≥2 positive `LNCM` species, with each eligible plot having an original DS1 finite nonnegative `biomass_woody`. No mass-dependent outcome selection beyond finite nonnegative value checks. At least 80 plots must satisfy ≥2 species with one **same trait axis**, from ≥5 independently identified sites each with ≥8 plots. At least 20 distinct study taxa must support trait coverage (only aggregate count, no names exported). This is plot-level numerical *support* only; original field measurement provenance is a separate mandatory gate.
- Mandatory **provenance:** Published methods report many species traits were measured in monocultures (site-specific) and some supplemented from external literature/databases. DS2 per `site×plot×species` trait *values are not necessarily measurements from those individual plots*. A plot-local independently measured species trait can only be classified if explicit original `tree/sample ID, measurement date, source type, individual-level provenance` or equivalent original author metadata exists. **No invented per-row 'measured' flag**. If provenance cannot separate field-measured, site-monoculture-transferred, and literature-imputed values, report `TRAIT_PROVENANCE_HOLD` even when plot joins succeed.
- If no original year/measurement date columns exist, report `TEMPORAL_ALIGNMENT_HOLD` separately. The paper might have measured biomass and traits in different years; README prose alone is insufficient to claim ≤2-year original per-plot observation alignment without authoritative site/year metadata.
- Source biomass units: DS1 `biomass_woody` Mg dry mass ha−1 (not annual litterfall, not carbon stock unless conversion documented); DS2 `biomass_woody` may be per-species woody mass, **not** a second independent plot biomass value. Check only presence and optional additivity at exact matched plot, no trait/biomass correlation. Any numerical additivity is a source consistency audit, not proof of ecological positive effect.

## Fixed labels and stopping conditions

- `SOURCE_JOIN_GEOMETRY_PASS`: exact identifiers, original-plot one-to-many join, trait and biomass completeness thresholds above supported.
- `SOURCE_JOIN_GEOMETRY_HOLD`: duplicate/unknown primary keys, no unique join, unsupported plot/site/taxon coverage.
- `TRAIT_PROVENANCE_HOLD`: plot-source join geometry works, but original direct versus monoculture-transferred versus externally imputed trait lineage unresolvable at original-record grain.
- `TEMPORAL_ALIGNMENT_HOLD`: original dates not visible to verify per-plot source measurement timing.
- `SCHEMA_OR_ACCESS_HOLD`: wrong source bytes, source file columns, invalid original workbook parsing, unsafe access.
- The final **direct-original-measurement research admissibility** requires geometry PASS, provenance PASS and temporal alignment PASS. Failure of any means no study claim that independently observed plot-level traits cause or predict woody biomass. A further source provenance authorization and new frozen outcome model are required before any ecological regression even when geometry PASSes.

## Nonclaims and independence

TreeDivNet Jensen 2026 itself has already reported positive forest diversity/carbon findings. Reusing this original study is not an independent confirmation of its published results. Original `SLA`, `WD`, `LNCM` and tree height are not family-specific trait phylogenetic signal K. With ~40 tree taxa, direct 12-family×20-species trait-K analysis is structurally unsupported. No biological effect of diversity, competition, PD, K, FD, carbon, or biomass will be calculated in this gate.

Keep original DS1/DS2 source rows in ephemeral CI runner only. GitHub commits only counts, key-integrity summaries and provenance decisions. Do not loosen source thresholds after seeing the outcome.
