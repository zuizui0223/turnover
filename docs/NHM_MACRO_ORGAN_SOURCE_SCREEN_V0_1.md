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
