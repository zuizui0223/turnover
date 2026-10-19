# A named data-source collision dominates AusTraits seed dry mass K support

**2026-10-13 — source-provenance audit completed, not independent replication, no phylogenetic K outcomes reopened.**

### Verified source identities

- **AusTraits v7.0.0, exact commit `7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c`**: [`data/Kew_2019_1/metadata.yml`](https://github.com/traitecoevo/austraits.build/blob/7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c/data/Kew_2019_1/metadata.yml) identifies its source as **"Seed Information Database (SID) and Seed Bank Database"**, curated by Royal Botanic Gardens, Kew. The native data source belongs to a **derivative compilation** and tracks an underlying `original_dataset_id` assembled from source `refshort`; hence `Kew_2019_1` is emphatically **not** a single independent field study or a uniform error process. The reported trait is `seed_dry_mass`; its source methods often infer likely dry mass from associated remarks and include multiple original source references.
- **TRY's historical public Data Explorer** (its own stated version 6.0, not current TRY v7): DatasetID **21**, *KEW Seed Information Database (SID)*, and DatasetID **565**, *Seed Information Database, Royal Botanic Gardens, Kew*. The shared *named database lineage* is plain in the public source labels, but it is not an identified matching measurement record, and retention/permissions for these records in TRY **v7 are unknown**.
- The [source identity/source support protocol](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/try_austraits_kew_sid_lineage_exposure_v0_1.json) was frozen before the exact SID source-exposure count was generated. A separate [GitHub Action #38404694553](https://github.com/zuizui0223/turnover/actions/runs/38404694553) **passed**, validating original source metadata and both historical TRY IDs.

### Exact original K cohort exposure

All 254 original family×trait systems, 42 plant families and 13 traits were preserved, with the original source-native species medians and positive numeric source record eligibility. No original K effect values were used and no species names/measurement values or observation IDs were emitted.

| Discovery trait | Total species×system cells | Cells with ≥1 positive Kew_2019_1 observation | Exposed family×trait systems |
|---|---:|---:|---:|
| **seed_dry_mass** | **4,242** | **3,346 (78.88%)** | **15 of 15** |
| seed_width | 2,511 | 0 | 0 |
| leaf_area | 1,712 | 0 | 0 |
| leaf_width | 11,878 | 0 | 0 |
| petiole_length | 2,529 | 0 | 0 |
| Remaining 8 traits | — | 0 | 0 |
| **All 254 systems** | **66,330** | **3,346** | — |

There were **5,914 distinct positive Kew source `dataset_id + observation_id` keys** in the same K systems. Distinct keys within the compiled AusTraits archive **do not** establish independent original field observations or equivalence to any TRY record ID.

This *one candidate source family* is concentrated in **seed dry mass**, one of the five observed-to-source-OU signed ranking departures previously discovered. For comparison, the separate historical TRY/AusTraits **Tng et al. (2013)** possible common-original-*publication* lead affected **34 of 1,712 leaf-area species×system cells** (1.99% leaf-area support, four families) but no other of the five signed traits; see [Tng source exposure audit #38403894412](https://github.com/zuizui0223/turnover/actions/runs/38403894412).

### Why this matters for the ecology inference

**A trait may appear to possess a reproducible high or low phylogenetic K ranking partly because its observation layer has a distinctive source composition.** The large SID fraction establishes an unusually strong **source-family composition confound** for seed dry mass but **does not demonstrate it caused the observed K rank**. Correlated source protocols, measurement assumptions, missingness, original nested citations and the underlying taxonomic/phylogenetic distribution remain unresolved.

The SID-exposed 3,346 species×system cells can overlap with non-Kew source observations for the *same species*; **do not** subtract 3,346 from 4,242 and call 896 the independent K-cohort species count. Correct non-Kew species support requires independently recomputing all original source medians from non-Kew records while preserving the original fixed source-native tree/tip support and reporting exclusion-driven loss as a *post-discovery sensitivity*, not as a new predeclared primary result.

### Necessary next tests and hard boundaries

1. **Pre-K, source-only eligibility sensitivity:** on the already fixed 254-system K graph, count species support after removing only `Kew_2019_1` source observations; preserve original frozen units/species rules; separately report lost systems and families with ≥20 remaining species for `seed_dry_mass`. No K inference in this test.
2. **External TRY v7 source genealogy:** acquire a TRY-authorized metadata-only crosswalk from historical ID 21/565 to any current v7 DatasetID, with underlying primary reference/DOI, source observation-ID lineage and source-per-trait×family species counts. Do not equate historical and current IDs.
3. **Trait-definition firewall:** source-native Kew mass data may be derived from `thousandseedweight` and methods can mark **assumed dry mass**; a new independent validation must distinguish single mature seed mass, fruit/dispersal-unit mass, verified dry mass and imputed protocols.
4. **No score inflation:** the original OU+source rank portability result and its *post-outcome exploratory* named-trait ranking discrepancy are unchanged; this new metadata result does not prove evolution differs among traits or make TRY v7 independent.

**Current state:** genuine independently qualified source for the five frozen named-trait predictions = **0**. No restricted TRY data have been opened and no original BIEN 201-system rho analysis was reopened.
