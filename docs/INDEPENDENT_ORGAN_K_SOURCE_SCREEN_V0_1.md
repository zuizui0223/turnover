# Independent organ-K validation: source-only candidate gate (2026-10-19)

## Fixed question

Can the exploratory AusTraits finding that reproductive seed/fruit morphology tends to have higher Blomberg K than vegetative morphology be reproduced using **genuinely independent, direct, provenance-qualified** measurements?

The biological prediction and thresholds are **unchanged** from
`data/austraits_reproductive_vegetative_k_external_validation_protocol_v0_1.json`.
All sources here are screened **before** any new organ-K computation. A compilation
is not automatically independent, even when its original papers use a different
language or publication year.

## Candidate triage

| Candidate | Verified source facts | Strict next action / ruling |
| --- | --- | --- |
| FAIRTraits, Garnier et al. 2025 | 240 species, 48 families, ~189,452 original observations and 183 quantitative traits; direct shared-group protocols; GBIF DOI `10.15468/r5kj3q` | **Structural HOLD**: even if every family had one species, at most floor((240−48)/(20−1))=**10** families can have >=20 species, short of the locked minimum of 12. Do not run K. |
| Chinese Seed Trait Database, Wang et al. 2025, Figshare v4 | CC BY 4.0; 3,897 plant species; >110,000 records across 118 trait labels from 694 cited sources, including seed/fruit traits and plant height | **UNKNOWN / metadata-screen-only**. Run CSTD original workbook MD5-pinned trait×family same-species support check. No phenotype magnitudes, phylogenetic K, source semantic PASS, or independence claim. Original cited source lineage, homology, and S3/prune still unverified. |
| ForestGEO network | Publishes standardized leaf lamina and reproductive seed/diaspore measurement protocols, but data access/support vary by plot, with a separate access request portal | **ACCESS / coverage HOLD**. Do not assume all network sites have both traits or that a direct data request is automatically authorized. |
| Hong Kong fruit/seed database, Law et al. 2026 | New direct measurements for 684 species across 128 families, but documented files contain fruit/seed tables and a species list rather than corresponding leaf traits | **Single-arm HOLD** under the locked paired-organ contract; possibly useful only if an independently verified and homologous leaf source is found. |

### CSTD v4 public accession (metadata only)

- DOI: https://doi.org/10.6084/m9.figshare.28152035.v4
- Public API: https://api.figshare.com/v2/articles/28152035/files
- Workbook `CSTD_v1.xlsx`: 10,175,445 bytes; `https://ndownloader.figshare.com/files/53721110`
- MD5: `9d02dfed7de29484d2f5c5137235cabe`
- License: CC BY 4.0. Only structural counts may enter the result artifact.
- Runner: `scripts/source/audit_cstd_organ_metadata_v0_1.py`; fails closed if the original schema, identity or metadata mappings are ambiguous.
- `seed_mass` is **not** automatically treated as `seed_dry_mass`; an unspecified fruit part is likewise not homologous to a defined fruit dimension.

The report's `structural_necessary_gate_possible_unverified` indicates only whether one necessary species/family-support criterion **might** be satisfiable. Even a positive value would remain **HOLD** until original-study source lineage, organ homology, independence from the original AusTraits contributors, rights and two-tree eligibility are demonstrated.

## Sources

- FAIRTraits: https://www.gbif.org/dataset/3772c2f3-28e4-4e25-938a-93635e6642a2
- CSTD article: https://doi.org/10.1111/nph.70296
- ForestGEO protocols: https://forestgeo.si.edu/node/145666
- ForestGEO data access: https://ctfs.si.edu/datarequest/
- Hong Kong primary seed/fruit database: https://doi.org/10.3390/data11010008

## Actual outcome-blind CSTD screen — 2026-10-19

The pinned workbook passed its MD5 identity check and its accepted species/family
metadata were read successfully in [GitHub Actions #39208217308](https://github.com/zuizui0223/turnover/actions/runs/39208217308).
**No numeric trait comparison was performed**.

- 694 distinct source reference labels; 3,232 family×accepted-species metadata
  keys with one of the strictly mapped organ traits.
- At least 20 same-species metadata-presence overlaps in **67 family×trait
  pairs spanning 20 families**.
- Fruit-vs-vegetative support in 16 families and seed-vs-vegetative in 20.
- Four candidate reproductive names: fruit length/width, seed length/width.
- Only **ONE** admissible candidate vegetative name in CSTD:
  `plant_height`. The fixed protocol requires **TWO**.

**Decision for CSTD-alone: STRUCTURAL HOLD (one vegetative trait),
irrespective of the otherwise-promising family counts.** No K computation is
authorized. This is not evidence against the biological organ hypothesis.

The China Plant Trait Database v2 (CPTD v2; accession
https://figshare.com/articles/dataset/The_China_Plant_Trait_Database_Version_2_0/19448219)
was independently screened at schema level in
[GitHub Actions #39208517972](https://github.com/zuizui0223/turnover/actions/runs/39208517972).
The original chemical-traits CSV (2,888 rows) includes `Average LA` and
`LMA` fields that **may** supply two frozen leaf traits, but the separate
morphometric file (2,415 rows) contains categorical leaf size/shape and must
not be substituted for numeric leaf area. Original taxon translations contain
2,949 sample rows. Source DOI/record independence, leaf/leaflet ontology,
field-versus-literature provenance, and CSTD species overlap remain unverified.
The audit code `scripts/source/audit_cstd_cptd_pair_support_v0_1.py` screens
only exact accepted-binomial overlap and measurement *presence*.

### Pinned CPTD v2 public file identities

| File | Figshare file ID | MD5 |
| --- | --- | --- |
| Species translations.csv | 38095881 | `2c1285a6bf78112c855f0ce735685343` |
| Chemical traits.csv | 38095812 | `bf772a9e6a7251f8bed33d06d29f8fed` |
| Morphometric traits.csv | 38095836 | `ca21286257508e05cd2e102cbfbac748` |

## Scientific boundaries

Nothing in this source-only step updates the original AusTraits 77–79% exploratory organ-K finding, the closed BIEN 201-system rho conclusion, or the fixed external success criterion. An inaccessible or unsupported independent source yields **UNTESTED**, not a negative evolutionary conclusion.
