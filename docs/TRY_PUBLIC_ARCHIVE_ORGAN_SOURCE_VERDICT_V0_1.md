# TRY File Archive v0.1 — public metadata-first organ validation triage

**Date:** 2026-10-19. **Branch:** `source/try-public-primary-catalog-v0-1`.
**Current gate:** `HOLD_PRE_OUTCOME_ORIGINAL_PRIMARY_SOURCE`.
This is a source-qualification study, **not** an evolutionary-trait effect analysis.

## Fixed biological question and untouched rules

Can the reproductive-vs-vegetative Blomberg K tendency discovered
*post-outcome within AusTraits* be replicated in **independent directly
measured plant trait observations**, on identical matched tips and both
V.PhyloMaker2 S3 and native-prune trees, with >=12 independently supported
families, >=20 distinct overlapping species per organ pair, >=6 fruit and
>=6 seed families, and >=2 trait labels per organ module?

The locked contract is `data/austraits_reproductive_vegetative_k_external_validation_protocol_v0_1.json`
on the base branch `analysis/brownian-process-null-v0-1`. No
new biological effect is opened unless all locked source and geometry
eligibility requirements pass. The original BIEN 201-system study stays closed.

## Public archive catalogue: all 122 metadata entries

Official public listing:
https://www.try-db.org/TryWeb/Data.php

The source-only scanner
`scripts/source/audit_try_public_archive_organ_metadata_v0_1.py`
parses the **advertised Field list**, not the downloadable phenotype files,
of all 122 TRY File Archive entries visible on 2026-10-19. Eligibility for
manual adjudication requires **both** an explicit leaf-size/mass column and
an explicit seed/fruit/nutlet/propagule size/mass column.

| TRY File Archive ID | Public title | What the metadata establishes | Independent cross-family validation status |
| --- | --- | --- | --- |
| **10** | Community species composition, above ground biomass nutrient contents | Leaf mass/SLA and seed mass, but they are community-weighted mean records for **692 vegetation plots**, not matched original species-level measurements | **HOLD** — wrong grain |
| **17** | 15 traits of 34 herbaceous species in Sherbrooke | Leaf area/SLA and seed mass/sphericity, approx. **34 species** in mesocosms | **STRUCTURAL HOLD** — 34 < 12×20 minimum distinct species, before any actual family counting |
| **113** | Leaf, stem and fruit traits of `Scleria` species | **1,254 herbarium specimens from 209 species**, originally measured plant height, leaf blade length/width and nutlet length/width; nutlet weight from 141 species | **STRUCTURAL HOLD** — one genus/one family, Cyperaceae; usable only as a separately declared within-lineage primary-data candidate |

**Result:** exactly **3 of 122 public archive datasets** explicitly advertise
both requested organ sizes under this text-field screening. **None** is a
self-standing >=12-family prospective independent primary test.

This is **not** a claim that TRY v7 itself lacks relevant source-native
measurements. The TRY main database is far larger and contains raw source
dataset identities unavailable from this sparse public file archive.
Pooling files or accessing TRY v7 requires separate origin/rights/duplicate
record adjudication; the archive metadata cannot establish cross-dataset
source independence or common phylogenetic trees.

## Direct-measurement Scleria: version and rights risk

Official related records:

- TRY public metadata File Archive #113:
  https://www.try-db.org/TryWeb/Data.php
- Zenodo v1 `10.5281/zenodo.10533114`:
  https://zenodo.org/records/10533114 — metadata displays a public file
  `Scleria_Data.xlsx` and a 136-species `scleria_tree.txt`.
- **Latest Zenodo v2** `10.5281/zenodo.12755860`:
  https://zenodo.org/records/12755860 — **Restricted files**;
  access is NOT established merely because v1 was listed publicly.

Reported original measurements are a promising **single-family direct-source
pilot**. However, 209 species with some specimen measurements, 141 species
with nutlet weights and 136 phylogenetic species are **different support
populations**. Before using v1 even for a separately registered pilot,
verify explicit rights and source version policy, actual original specimen
IDs, original measured **not flora-infilled** species, and exact measured
trait × tree-tip overlap. Do not silently substitute v1 data for restricted
v2, or count floristic additions as primary specimens.

The published leaf trait may describe blade morphology, while `Scleria`
nutlet dimensions are fruits rather than ordinary multi-seeded fleshy fruit
morphology. Trait homology versus AusTraits seed/fruit definitions needs
documented adjudication.

## What this screen allows and forbids

**Allowed:** Count public source-title/field-list metadata; prepare an
authorized TRY v7 *metadata-only* request; design an independent **one-clade
exploratory** pilot with its own pre-outcome contract; count original
Scleria specimen × leaf × nutlet × 136-tip overlap only if provider access
rights permit.

**Not allowed:** Declare one Cyperaceae family a successful 12-family
validation; calculate new confirmatory K on source-ineligible records;
impute missing phylogenetic tips and call them direct; download registered
TRY trait archives or latest restricted Zenodo v2 through another source;
revise original family/trait thresholds post hoc.

**Most useful next actionable dependency:** Authorized record-level
original-measurement identifiers and rights for TRY v7 or a genuinely
independent multisource direct-measurement matrix. The prepared
TRY v7 metadata request documented in Issue #34 can be sent by an
authorized researcher; it has not yet been submitted.

## Sources

- TRY main database: https://www.try-db.org/
- TRY public File Archive: https://www.try-db.org/TryWeb/Data.php
- Scleria original data and tree, Zenodo v1:
  https://zenodo.org/records/10533114
- Scleria latest restricted Zenodo v2:
  https://zenodo.org/records/12755860
- Earlier CSTD+NHM source-only controls:
  https://github.com/zuizui0223/turnover/pull/35 and
  https://github.com/zuizui0223/turnover/pull/36
