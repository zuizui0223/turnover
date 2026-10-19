# Independent-organ-K candidate: NHM botanical descriptions and herbarium images

**Stage:** source-only, no phenotype-value extraction, no Blomberg K or evolutionary inference.

## Why this source merits a preflight

The [Natural History Museum plant-traits public repository](https://github.com/NaturalHistoryMuseum/plant-traits) provides two complementary modalities:
- Morphometric leaves extracted by LeafMachine2 from 14,533 herbarium-sheet images (`output/raw/cv-traits/all_leaf_measurements.csv`).
- Numeric and categorical traits extracted from botanical descriptions for 59,369 angiosperm species, 888,328 stated traits (`output/raw/ocr-traits/combined.csv`) originating in BHL, EFlora and Ecoflora.

The README explicitly states CC BY 4.0. We pin source commit `4843c22bb2fc91018d9828dcddebf067c83b1097` so that changing upstream rows cannot affect the pre-outcome cohort.

Unlike the previously screened CPTD-v2 leaf records, the OCR database contains tens of thousands of **leaf-length and leaf-width description-derived labels** plus over 13,000 **seed-length descriptions**. This is potentially useful to test the *coverage* of a botanical description × independently compiled seed/fruit database matrix. However:
- Source trait definitions are **descriptive species ranges** and may not be homologous with observed individual means in AusTraits.
- NLP extraction is *not itself* a new, independent primary measurement. Reusing Flora of Australia/other historical floras or OCR output does not establish independent original observations.
- CV leaf detection may treat leaflets as whole leaves; taxon identity and original specimen metadata must be checked.
- The fixed pre-existing external protocol requires 12 independently measured families, >=20 matched species per pair, >=6 fruit and >=6 seed families, at least two original vegetative and two reproductive trait names on both S3/prune trees. The frozen requirements cannot be weakened just because this source is large.

## Initial gate

The pinned GitHub Actions preflight (`.github/workflows/nhm-macro-organ-source-v0-1.yml`) fetches three upstream CSV files and reports file SHA256, exact source columns, row counts and first three taxonomy/source-only metadata rows:
- `output/raw/cv-traits/all_leaf_measurements.csv`
- `output/raw/ocr-traits/combined.csv`
- `input/wfo-angiosperms.csv`

No values are opened to test the biological contrast. The next allowed step is determining the exact taxonomic and measurement-source identities and then counting *presence-only* family×reproductive×vegetative matches. The CSTD×CPTD v2 source screening in [PR #35](https://github.com/zuizui0223/turnover/pull/35) remains source-only HOLD, especially after the worst-source-label ablation reduced 17 leaf-pairs to 0 pairs with >=20 species.

**Potential outcome:** even if a large coverage set qualifies structurally, independent *primary* source evidence remains **HOLD** until original references, overlap with AusTraits source lineage, trait homology and two-tree matched-tip data are verified. Data mining by changing source inclusion after seeing K is prohibited.

## Completed source-support outcomes — 2026-10-19

All findings below are **source/taxon/trait PRESENCE only**, never the observed
phylogenetic signal of a measured organ. The exact NHM upstream Git commit and
CSTD v4 workbook checksum are pinned.

### NHM-only seed vs leaf / height

[Successful source-only CI #39215100055](https://github.com/zuizui0223/turnover/actions/runs/39215100055):

| Original botanical source stream | Eligible 20+ species family×seed×vegetative pairs | Distinct families |
| --- | ---: | ---: |
| All source descriptions combined | **264** | **72** |
| Biodiversity Heritage Library | 48 | 19 |
| Flora of China | 179 | 54 |
| Flora of North America | 90 | 26 |
| Flora of Pakistan | 34 | 12 |
| Ecoflora | 8 | 4 |
| NHM independent herbarium leaf images vs NHM seed descriptions | 6 | 1 |

NHM's numerical organ columns have **seed length/width** and vegetative
leaf length/width and plant height; they do **not** include a directly
corresponding numeric fruit-length/width field. The frozen seed+fruit external
replication cannot be completed with NHM-only. Source-type subsamples can
share original descriptions and are **not independent biological replicates**.

### Original CSTD fruits/seeds × NHM leaf/height

[Full CSTD×NHM source-presence CI #39216636641](https://github.com/zuizui0223/turnover/actions/runs/39216636641)
and [flora-source ablation CI #39216867540](https://github.com/zuizui0223/turnover/actions/runs/39216867540):

- CSTD original 110,451 records; 2,555 unique binomials retain
  the specified seed/fruit trait and **exact WFO family agreement**.
  This is an outcome-blind support screen, **not** a validated phylogeny.
- NHM combined × CSTD: **206** eligible family×trait-pair presences in
  **26 families**; **19** families have fruit comparisons and **25**
  have seed comparisons. Numeric family/source coverage requirements are
  potentially satisfiable; primary-source and tree support are not.
- NHM *Flora of China alone* × CSTD: **195** pairs in **25**
  families, illustrating strong geographical/bibliographical concentration.
- NHM **herbarium-image** leaf measurements × CSTD: **0**
  pairs in **0** families with 20+ same accepted species.
- On unions of the distinct original flora streams: **206 pairs,
  26 families**. Remove **Flora of China** and this falls to
  **47 pairs in 7 families**, below the frozen 12-family minimum.
  Removing BHL alone gives 203/26; removing Flora of North America
  gives 206/26. These are support counts, not K outcome changes.

The strongest apparent CSTD×NHM comparative capacity is thus contingent
on the **same Flora of China description stream** and Chinese secondary
literature selection. No evidence establishes that the underlying raw
measurements of either database are independent of AusTraits, or that
`leaf` always denotes a homologous single lamina rather than a leaflet.
The exact matched S3 and native-prune phylogenies also have not passed
the external support qualification.

**Explicit conclusion:** both major NHM screens and CSTD×NHM remain
`HOLD_PRE_OUTCOME_PRIMARY_PROVENANCE` for the frozen prospective
*independent primary measurement* replication.

### Publication and execution boundary

These screens identify that **apparent global taxonomic coverage is not
synonymous with globally independent original measurements**. That is
a source-architecture warning, not a biological claim about evolutionary
constraint, selection, stability, OU alpha, or a difference in Blomberg's K.

- Do **not** count secondary botanical source streams as independent
  source-level biological replication.
- Do **not** compute an external confirmatory K under the original frozen
  protocol with this source set.
- Do **not** lower 12 family / 20 same-species / six fruit + six seed /
  two organ-trait names / S3+prune criteria to rescue it.
- A new *exploratory secondary-description* study, if ever pursued,
  must be declared **separate from this prospective independent-data
  validation** and model source identity; it cannot retroactively
  confirm the original AusTraits discovery.
- The next materially useful route is a genuinely **independent directly
  measured source** with family×trait support and original study lineage
  available *before* inspecting its phenotypic values, or documenting
  an explicit no-source HOLD rather than further outcome-driven mining.
