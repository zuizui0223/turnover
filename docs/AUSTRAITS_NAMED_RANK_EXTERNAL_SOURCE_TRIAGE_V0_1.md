# External validation source triage for 5 named plant trait K predictions

**2026-10-11; metadata-only first gate.** No target K, empirical values, species-level phenotype or source overlap outcomes have been obtained for a new validation source.

Parent frozen discovery protocol: `data/austraits_named_rank_external_validation_protocol_v0_1.json`.
Candidate registry: `data/austraits_named_rank_external_source_candidates_v0_1.json`.
CI metadata feasibility assessment: `scripts/source/audit_external_named_rank_source_candidates_v0_1.py`.

## Why this is necessary

The 249-system AusTraits source-OU discovery shows a concrete **post-outcome signed named-trait rank discrepancy**, despite homogeneous OU plus trait-global source variation reproducing the *magnitude* of rank portability. The original primary finding is **not** evidence of evolutionary-process heterogeneity, and five signed departures are **hypotheses formed after opening the data**. Claiming independent replication requires genuinely new primary observations and a new family×trait graph, not a newer compilation or another analyst fitting the same source.

The external protocol requires **at least 10 families with 20 distinct species per trait**, and **10 families with at least two target traits**, for at least **four of five** preread signed predictions. This implies a necessary minimum of **200 different species per qualifying trait**, but not a sufficient one; they must be distributed across 10 families and support paired data. Species totals for a whole database are not trait/family-specific support.

## Source triage: metadata-only

| Public candidate | Publicly reported scale | Number of frozen five trait concepts potentially covered | First-stage outcome |
|---|---:|---:|---|
| **TRY v7**, released 2026-09-04 | 306,701 plant taxa across database | 5 trait identifiers listed | **HOLD**, not independent validation |
| **MorFunSeed** Brazil, 2026, primary seed morphology | 131 plant species total | Seed width and dry mass potentially available (2) | **HARD structural fail:** fewer than 200 species total |
| **Western Ghats** India, 2025, new leaf measurements | 93 woody species total | Leaf area only (1) | **HARD structural fail:** fewer than 200 species total |

TRY is an integrated database and includes primary and secondary sources. Its 2026 public release date does **not** prove non-overlap with AusTraits primary datasets; TRY states that **version 7 data import was completed on 2025-07-25**, so a newly released interface must not be mistaken for newly collected, independently sampled biological measurements. Trait-registry counts are not proof of ≥20 species in ≥10 families after source-level de-duplication, nor evidence that the five trait concepts have semantically matching measurements.

MorFunSeed and Western Ghats are useful as **supporting measurement sources** for narrower, externally predeclared supplemental questions. Neither can be upgraded to a five-trait independent replication by weakening the previously frozen family thresholds.

## Five TRY trait IDs as *search terms*, not an accepted crosswalk

| AusTraits discovery trait | TRY candidate ID | Provisional concept | Semantic caution |
|---|---:|---|---|
| seed_width | 239 | Seed width | Confirm per seed, not fruit/diaspore or projected width |
| seed_dry_mass | 26 | Seed dry mass | Exclude fruit/dispersal-unit masses and unsupported conversions |
| leaf_area | **3108** | Whole-leaf area, petiole excluded | **HOLD:** simple versus compound leaf/leaflet, petiole inclusion; don't merge generic area ID 1 or 3110–3114 automatically |
| leaf_width | 145 | Leaf width | Lamina width versus leaflet measurements require source-level review |
| petiole_length | 143 | Leaf petiole length | Do not substitute rachis length or another plant organ |

These candidate IDs are grounded in the [TRY Data Explorer](https://www.try-db.org/de/TraitSearch.php). Trait semantics are not yet adjudicated against the pinned [AusTraits Plant Dictionary](https://doi.org/10.1038/s41597-024-03368-z). The dictionary explicitly warns that leaf and leaflet area measurements can be mixed under a general leaf-area concept. As a result, **leaf_area must remain on semantic HOLD** until a documented source-level crosswalk is available.

## Required next *data request* (metadata first, K/value blinded)

Ask for the following **catalogue fields** for those five candidate trait IDs, before requesting phenotype values: source dataset identifier, original primary dataset DOI/citation, observation or measurement identifier availability, source taxon name, standardized family, valid trait ID and full definition, native unit, petiole/leaflet/seed-part protocol, primary versus derivative-source lineage, permission/license and approximate per-family distinct species counts for each trait. Request a contributor-level dataset catalogue first; do **not** treat a dataset-level count as independent observation proof.

Next compare primary DOI and dataset IDs to the original AusTraits v7 underlying source list and their measurement IDs. A source with missing DOI coverage is **unknown independence**, not verified independence. A source that lacks raw identifiable records cannot estimate source noise and cannot be called independent under the frozen protocol. Do not read the biological trait values or calculate target K until the metadata/provenance/taxon-graph gates are documented and qualified.

## Scientific stop rule

The result of this metadata screen is **zero independently qualified validation sources**. This is a data-access/provenance HOLD, not a biological null result. The successful original BM/OU/source-noise and named-trait adequacy results are unchanged. The BIEN 201-system rho empirical study is scientifically closed; its original source observations cannot be mined to convert the exploratory five AusTraits signs into 'prospective' primary hypotheses.

References:

- [TRY v7 home](https://www.try-db.org/) and [TRY data explorer](https://www.try-db.org/de/TraitSearch.php)
- [TRY integrated-source description](https://www.try-db.org/TryWeb/About.php)
- [MorFunSeed, Ecological Research 2026](https://doi.org/10.1111/1440-1703.70086)
- [Western Ghats leaf dataset, Data in Brief 2025](https://doi.org/10.1016/j.dib.2025.112225)
- [AusTraits Plant Dictionary, Scientific Data 2024](https://doi.org/10.1038/s41597-024-03368-z)
