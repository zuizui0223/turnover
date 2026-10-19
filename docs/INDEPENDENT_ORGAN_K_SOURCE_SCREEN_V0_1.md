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

## Paired-source accepted-taxon screen completed — 2026-10-19

[GitHub Actions #39208958392](https://github.com/zuizui0223/turnover/actions/runs/39208958392)
completed the pinned **CSTD × CPTD v2 metadata-only join** (without comparing
trait magnitudes). Only exact lower-case genus+species binomials were matched;
CSTD accepted names conflicting across families were omitted, no automated
synonym/fuzzy matches were permitted. A presence record is a necessary
support indicator, not a verified biological measurement.

| Necessary-support result | Count |
| --- | ---: |
| CSTD accepted binomials with approved mapped labels | 3,140 |
| CPTD accepted binomials with mapped sample metadata | 1,284 |
| Exact accepted binomials shared by both | **523** |
| CSTD reproductive plus CPTD leaf metadata present | **512** species |
| CSTD+CPTD >=20-species family×organ pairs including CSTD plant height | **84** in **20** families |
| Pairs with CPTD leaf traits and >=20 accepted common species | **17 pairs in only 3 families** |
| Families with any fruit vs vegetative candidate | 16 |
| Families with any seed vs vegetative candidate | 20 |
| Candidate vegetative names | `plant_height`, `leaf_area` candidate, `leaf_mass_per_area` candidate |

Under the strict counts-only necessary support screen, the combination
**may** meet the numerical 12-family / 6-seed / 6-fruit / 2-vegetative-label
requirements. The crucial limit is that **only three families provide the
new CPTD leaf comparisons at >=20 species**; most of the 20-family support
still comes solely from original CSTD plant-height comparisons.

**Final status remains HOLD**, not an independent replicate: published
CSTD is compiled from 694 underlying source references, CPTD contains
a mixture of direct field and literature samples, same-binomial matching
does not establish observation independence, leaf/leaflet morphology is
not yet harmonized, and the predeclared two-tree matched-tip crosswalk
has not been qualified. The biologically measured K direction has not
been opened. No change to frozen sample gates or original effect claims.

## Exact source-lineage audit completed — 2026-10-19

The successful [original-reference integrity workflow #39211759747](https://github.com/zuizui0223/turnover/actions/runs/39211759747)
joined every selected CSTD trait record's raw `Reference` ID against the
published two-column `Reference` worksheet (`ID`, `Name`), not DOI guesses.
There are **694 catalogued bibliographic IDs**; the selected organ-trait
records use **580 source IDs, all 580 resolved; 0 unresolved IDs**.

**CSTD-only source-linked support:** On the EXACT original
`Species_accepted` text strings, with genus/family conflicts excluded in a
separate sensitivity but no artificial merging of infra-specific or
authorship-bearing names, **61** reproductive-versus-plant-height family×pair
comparisons in **20 families** retain at least 20 same-species records where
both traits cite an identical, registered original reference ID. This is
shared *citation* support, NOT paired measurements of a single specimen;
the contributing original publication may be a taxonomic compilation or
nonstandard measurement. It is NOT a full six-versus-six organ validation.

**CSTD × CPTD leaf support:** 17 >=20-binomial cross-organ comparisons remain
within **only three families**, although CSTD height broadens the combined
numerical support to 20 families:

| Family | Species supporting at least one 20+ leaf-versus-seed/fruit comparison | Distinct CSTD cited references | Distinct CPTD site-source labels | Largest single CPTD label covers this share |
| --- | ---: | ---: | ---: | ---: |
| Amaranthaceae | 22 | 10 | 4 | 90.9% |
| Fabaceae | 39 | 34 | 5 | 84.6% |
| Rosaceae | 36 | 16 | 5 | 58.3% |

The original CPTD `Sites information.csv` is fixed by Figshare ID 38095863
and MD5 `76debd1ec32b850efa2c593ee5b94ee4`. It reports exactly 140
sites and 7 distinct source labels, dominated by Wang et al. (2018; 104
sites) and Xu et al. (2021a/b; 18 sites). Source labels are *not*
independent original specimen identifiers. All matched leaf species above
carry at least one site-source label.

The [original CSTD shape and protocol probe #39210980120](https://github.com/zuizui0223/turnover/actions/runs/39210980120)
resolved verbatim dictionary definitions: fruit/seed length are the
longest dimension, width is the maximum perpendicular dimension, and
plant height is above-ground height. The CPTD paper describes
`Average LA` as scanned leaf area and `LMA` as inverse SLA. Exact organ
homology relative to AusTraits, genotype/individual correspondence, and
AusTraits-original-primary-source nonoverlap remain UNKNOWN.

**Method QA lesson:** a first draft erroneously used genus+species
normalization to reconstruct **CSTD-within-database** source-supported
pairs, which can join separate original taxon text rows carrying
complementary traits and artificially increase support. The corrected
workflow reproduces CSTD-only pairs by immutable verbatim species labels
and uses normalized binomials only for the separately labelled
cross-database candidate search. Neither failure was reported as a
biological result.

**Decision remains HOLD_PRE_OUTCOME.** Removing plant height leaves
only **three** families with 20+ seed/fruit-versus-leaf comparisons,
insufficient for family-general evidence on the broad vegetative organ
module, even though the weaker frozen numerical two-vegetative-name
condition can be satisfied when height is included. This is a limitation
of *data coverage*, not rejection of the proposed evolutionary pattern.

## Scientific boundaries

Nothing in this source-only step updates the original AusTraits 77–79% exploratory organ-K finding, the closed BIEN 201-system rho conclusion, or the fixed external success criterion. An inaccessible or unsupported independent source yields **UNTESTED**, not a negative evolutionary conclusion.
