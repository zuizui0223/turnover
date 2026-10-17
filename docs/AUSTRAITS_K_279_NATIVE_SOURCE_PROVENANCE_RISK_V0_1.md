# Provenance stress test: 279 source-matched organ K comparisons are dominated by floristic descriptions

**2026-10-15, verified after the original organ K results; source-only documentation and input provenance, not a new K comparison.** [Native source concentration audit #38703414522](https://github.com/zuizui0223/turnover/actions/runs/38703414522) **succeeded** after reconstructing exactly the original **279 common-DatasetID reproductive–vegetative family×trait-pair eligibility cohorts** on pinned AusTraits v7.0.0. No K effects, original species names, observations, or phenotype measurements were exported by this audit.

## Provenance concentration — original input contributions, not independent primary replications

| Source audit quantity | Verified result |
|---|---:|
| Original K-blind qualified family×organ pairs | **279** |
| Distinct family×pair×species cells with both traits at ≥1 common DatasetID | **46,684** |
| Public AusTraits contributing dataset IDs in these paired observations | **49** |
| Pair×species cells with **multiple** shared original DatasetIDs | **13,943 (29.87%)** |
| DatasetID-to-pair×species support **links**, counting overlaps | **65,043** |
| Links attributable to **five explicitly named electronic floras or native PlantNet profiles** | **49,746 / 65,043 (76.48%)** |

**Two different denominators:** 46,684 counts each family×pair×species support cell **once**; 65,043 counts contributions by potentially multiple shared source IDs, so a cell with two floristic sources appears twice. **76.48% is a share of dataset-link incidences, not an estimate that 76.48% of individually sampled plant observations originated from floras**.

The five original source datasets with unambiguous online-flora or species-profile metadata are:

| Pinned source DatasetID | Public source description | Positive source links (may overlap) |
|---|---|---:|
| `ABRS_2023` | *Flora of Australia*, Australian Biological Resources Study | **24,273** |
| `NHNSW_2023` | PlantNet / Australian state flora profiles | **9,460** |
| `RBGV_2023` | VicFlora, *Flora of Victoria* | **7,136** |
| `NTH_2023` | Northern Territory online flora | **4,624** |
| `SAH_2023` | South Australian eFlora | **4,253** |
| **Five-flora subtotal** | | **49,746** |

`ABRS_2023` alone appears in **24,273 / 46,684 (51.99%)** of the unique pair×species support cells. This means its source contribution is very common, **not** that the same measured specimen appears in 51.99% of the input. Other data-rich sources include `Kooyman_2011` (4,688 links, reports leaf/seed size compiled from floras and other published sources), `Maslin_2012` (2,602, interactive Acacia taxonomic treatment), `Cooper_2013` (1,893, transcription of Australian rainforest fruits), and `Crisp_2017` (1,216, Daviesia monograph). **Study author names, field/herbarium basis fields, and source citation types cannot alone certify independently collected observations.**

The machine-generated provisional text categorization is intentionally **not used to select K outcomes or infer independence**. The five explicit flora sources above are identified from public native source titles and descriptions, irrespective of whether a broader heuristic tags other studies.

## Critical potential mechanism of artificially high phylogenetic K

The pinned native [`ABRS_2023` AusTraits extraction script](https://github.com/traitecoevo/austraits.build/blob/7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c/data/ABRS_2023/metadata.yml) defines a **trait scoring method** with categories:

- scored directly from a species text description;
- inferred from species-level description;
- **inferred from genus-level description**;
- **inferred from family-level description**;
- inferred from taxonomy or a different trait.

The native metadata for [`NHNSW_2023`](https://github.com/traitecoevo/austraits.build/blob/7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c/data/NHNSW_2023/metadata.yml) and [`RBGV_2023`](https://github.com/traitecoevo/austraits.build/blob/7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c/data/RBGV_2023/metadata.yml) expose related method-context categories. If **genus- or family-derived numeric trait estimates were actually included** in species-level phylogenetic K calculations, closely related species could inherit artificially similar values, inflating Blomberg K and the apparent organ-class evolutionary hierarchy. However, **the presence of these extraction-method categories in the native metadata does NOT establish how many of the 46,684 actual K-support cells carry those flags**; the incidence must be audited directly from source-native observation contexts, not assumed.

A separate [schema audit #38704189501](https://github.com/zuizui0223/turnover/actions/runs/38704189501) confirmed that the pinned 68-column AusTraits flattened parquet includes **`method_context_id` and `method_context_properties`**. These offer a possible path to a record-level method audit; the column name alone does not establish the values, coverage or sensitivity of the actual K-cohort measurements to genus/family inference. The next high-priority diagnostic is **K-blind counts of original positive organ measurements explicitly flagged as scored-from-text versus inferred-from-genus/family/taxonomy, followed by a matched-tip quality-controlled sensitivity only if the flags are recoverable and sufficiently populated**.

## Interpretation and paper status

The independently [verified 279 same-DatasetID paired K result](https://github.com/zuizui0223/turnover/actions/runs/38698215216) still shows **reproductive morphology higher K in 209/279 (74.9%) S3 and 183/246 (74.4%) native prune** paired source-restricted comparisons. That is credible *within-database* descriptive robustness to distinct source IDs and species/tree mismatch. It is **NOT** independent physical measurements, standardized organ ontologies, or evidence that the difference arises from phylogenetic evolutionary rate, constraint or selection. The extreme concentration of source links in online floras raises a meaningful possible **taxonomic-description and secondary-imputation confound** that a reviewer would expect resolved before treating this as biological evolutionary process discovery.

No new outcome-based source exclusions, model tuning or reopening of original homogeneous OU source-noise, 760 K geometry or scientifically closed BIEN 201-system rho results occurred. The [prospective new-data organ K replication plan](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_reproductive_vegetative_k_external_validation_protocol_v0_1.json) remains fixed; independent TRY v7 primary-measurement qualification is still HOLD.
