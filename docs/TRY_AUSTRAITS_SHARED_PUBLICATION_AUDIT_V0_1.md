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

## Why this matters scientifically

The original main result remains that a homogeneous stationary OU model with externally calibrated source-associated variation **can reproduce the scalar strength of cross-family Blomberg K trait-rank portability**, whereas the same models **do not reproduce the realized 12 named-trait rank profile**. The latter is *post-outcome discovery*, not verified differential selection.

An “independent external test” that inadvertently reuses a published primary dataset can misleadingly reproduce the same trait-rank difference or source bias. Thus source identity must be audited at publication **and measurement-record** levels, not merely by DOI hyperlinks, broad trait names or database version numbers.

**Current decision:** TRY v7 remains **HOLD: no provenance-independent source with qualified 5-trait/family/tip support identified**. A registered TRY metadata-only v7 export with current DatasetIDs, original primary citations/DOIs, source record lineage, measurement IDs and families is still required. The permitted draft request is `docs/TRY7_INDEPENDENT_SOURCE_METADATA_REQUEST_V0_1.md`; **not sent**.
