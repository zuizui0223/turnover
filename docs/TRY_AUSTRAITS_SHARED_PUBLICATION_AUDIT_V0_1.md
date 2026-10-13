# TRY / AusTraits historical source-lineage linkage catches a DOI-index false negative

**2026-10-11, metadata-only.** This is a publication/citation screen on a *historical TRY public Data Explorer v6 dataset index*, **not** TRY v7 primary measurement confirmation, independent validation, or evidence of the five post-outcome K-rank sign predictions.

## New positive common-study candidate

| Field | AusTraits pinned original core | TRY historical public index |
|---|---|---|
| Source identifier | `Tng_2013` | DatasetID **625** |
| Human-readable name | Source metadata file `data/Tng_2013/metadata.yml` | **Tng et al 2013 Traits** |
| Author/year | Tng, 2013 | Tng et al., 2013 |
| Publication DOI | **10.1371/journal.pone.0084378** | **No DOI hyperlink displayed in the public directory row** |
| Biological source publication | Tng, Jordan & Bowman (2013), PLOS ONE | TRY Kattge et al. (2020) supplementary dataset inventory identifies dataset 625 as Tng et al. (2013) |
| Overlap evidence | **Same cited author/year and plausibly same original publication**, independently identifiable by the PLOS DOI | **NOT proof of same measurement records or retention in TRY v7** |

The PLOS study ([Tng et al. 2013](https://doi.org/10.1371/journal.pone.0084378)) measured functional traits (including **leaf area**) on **128 woody species** in Australia. It can therefore be relevant to the frozen five-trait discovery, but 128 species would be below the new-source validation protocol's **200 distinct species per trait necessary support bound** if treated alone. This point is not a per-trait support count in either compilation.

The historically archived [TRY Kattge et al. (2020) dataset inventory](https://www.esf.edu/srm/yanai/documents/Kattge_et_al-2020-Global_Change_Biology.pdf) explicitly lists DatasetID 625 as “Tng et al. 2013 Traits” and cites “Tng et al. (2013)”. The current [public TRY Explorer directory](https://www.try-db.org/de/Datasets.php) shows ID 625 and its title; the separate TRY website's main page describes v7, but the Explorer says v6.0.

## What changes relative to the earlier zero matches?

Earlier [metadata audit #38107630927](https://github.com/zuizui0223/turnover/actions/runs/38107630927) found:

- 888 TRY historical public dataset IDs, but just **99 with hyperlink-parsable DOIs**;
- 190 contributing source IDs in the pinned AusTraits 254-system K source graph, **128 with primary DOIs**;
- **zero direct linked DOI matches** between these *two incomplete subsets*.

The `Tng_2013` / TRY 625 shared-study candidate **explains how a true cited-study overlap can be invisible to direct DOI-link intersection**: the AusTraits side exposes the PLOS DOI, but the TRY public dataset-list row does not carry a DOI hyperlink. This does **not** prove identical original data, although it invalidates any inference that “zero observed DOI matches” means “no common primary publications.”

A new source-only author/year audit `scripts/source/audit_try_austraits_shared_publication_v0_1.py` detects matching exact surname and year, reports weaker surname-only leads separately, and **does not** count a publication citation as an independently observed measurement. The match rules are archived in `data/try_austraits_public_author_year_overlap_contract_v0_1.json`; [GitHub reproducibility workflow](https://github.com/zuizui0223/turnover/actions/runs/38108651376). The previously frozen five signed K-rank predictions and external validation thresholds are unchanged.

## Quantitative recheck from archived public source indices

A second, locally executed author-token/ID-year scan of the exact publicly archived **888 TRY historical directory rows** against the pinned **190 AusTraits source rows** finds:

| Matching rule | Pairs | Interpretation |
|---|---:|---|
| Exact source-name surname **plus exact four-digit publication year** in the TRY title | **1** | Tng_2013 → TRY DatasetID 625; plausible same original study |
| Exact surname, but no matching title year | **18** | Citation/source tracing leads only, **not** evidence of identical publications or measurements |

The second class includes multiple `Wright` surname matches and the `Fonseca` source name; those leads can reflect common researchers rather than a particular source publication. Three-letter surnames are eligible for the strict rule when their **year also matches**; this was explicitly corrected to admit `Tng` (three letters), without touching any biological source eligibility rule.

This result is based only on prior **public source metadata ZIP archives**, not a new TRY v7 data release, and it does **not** change the original DOI-link intersection result of zero. GitHub Actions [#38108762861](https://github.com/zuizui0223/turnover/actions/runs/38108762861) provides the automated reproduction of this source-only matcher; the local archived result does not imply that the remote workflow has completed.

## Source-native exposure of the original phylogenetic K cohort (2026-10-13)

After the matched historical TRY/AusTraits study-citation audit **passed** in [workflow #38403020753](https://github.com/zuizui0223/turnover/actions/runs/38403020753) (**1 strong author–year publication lead, 18 weak author-only pairs**), the exact original species-median support for all **254 family×trait K systems, 42 families, 13 traits** was independently reconstructed without selecting or exporting K effect values. The [frozen-source exposure workflow #38403894412](https://github.com/zuizui0223/turnover/actions/runs/38403894412) **passed** with each of the original system-species counts reproduced.

| Trait within original K graph | Species×system cells carrying a positive record from `Tng_2013` | Total species×system cells for trait | Exposed families |
|---|---:|---:|---:|
| `leaf_area` | **34** | 1,712 | 4 |
| `leaf_mass_per_area` | 29 | 1,081 | 4 |
| `plant_height` | 69 | 13,053 | 16 |
| All other 10 traits (including `seed_width`, `seed_dry_mass`, `leaf_width`, `petiole_length`) | **0** | — | 0 |
| **All 254 systems together** | **132** | **66,330** | — |

These are **source-exposed species×system cells**, not unique species across traits, independent measurements or verified TRY–AusTraits duplicated records. The separate count of positive Tng original observation keys was also 132. **Only one of the five discovery-generated signed target traits, `leaf_area`, has any direct source exposure to this one historically shared-publication lead**; it comprises 34/1,712 ≈ **1.99%** of that trait’s species-system support.

The 18 **weak author-only** bibliographic matches were kept separate: altogether 4,111 species×system cells had at least one record from the corresponding AusTraits source IDs; a strong author-year result was never imputed for these weak author matches. In particular, the much larger weak-source seed-dry-mass count requires a dedicated **named-source database lineage** audit rather than being called 4,111 confirmed shared measurements.

All of the above were computed entirely inside the already seen original AusTraits discovery data to assess *possible provenance exposure*. They do not constitute new independent TRY v7 K evidence, and do not change the original OU/source null, named-trait sign discovery or external validation threshold. The historical public TRY Explorer is still version 6, not the requested version 7 primary record genealogy.

## Why this matters scientifically

The original main result remains that a homogeneous stationary OU model with externally calibrated source-associated variation **can reproduce the scalar strength of cross-family Blomberg K trait-rank portability**, whereas the same models **do not reproduce the realized 12 named-trait rank profile**. The latter is *post-outcome discovery*, not verified differential selection.

An “independent external test” that inadvertently reuses a published primary dataset can misleadingly reproduce the same trait-rank difference or source bias. Thus source identity must be audited at publication **and measurement-record** levels, not merely by DOI hyperlinks, broad trait names or database version numbers.

**Current decision:** TRY v7 remains **HOLD: no provenance-independent source with qualified 5-trait/family/tip support identified**. A registered TRY metadata-only v7 export with current DatasetIDs, original primary citations/DOIs, source record lineage, measurement IDs and families is still required. The permitted draft request is `docs/TRY7_INDEPENDENT_SOURCE_METADATA_REQUEST_V0_1.md`; **not sent**.
