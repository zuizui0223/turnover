# Plant organ K hierarchy survives the joint removal of dominant electronic floras and same-source observation matching

**Verified 2026-10-19 from COMPLETE successful primary CI #39006469805 (142 pairs) and the subsequent family-matched decomposition #39202352075.** This is the deliberately **final post-original-K observational/source robustness exercise within AusTraits**, not an independent primary-measurement replication, a prospective organ hypothesis, or an evolutionary process/selection test.

## Biological question

Do seed and fruit dimensions tend to exhibit greater Blomberg K than leaf, petiole and height dimensions when **both organs are assessed on exactly identical taxa/phylogenetic trees and their species measurements come from identical remaining AusTraits contributing datasets after discarding five dominant online flora archives**?

The five exclusions are `ABRS_2023`, `NHNSW_2023`, `RBGV_2023`, `NTH_2023` and `SAH_2023`; this follows original record-level documentation showing that these archives represent substantial online floristic descriptions, not independent new physical measurements. The original source-only eligibility gate identified 142 family×pair systems among 24 families with ≥20 matched original positive species under the additional common-remaining-DatasetID requirement. The earlier 283 family×pair systems (29 families) required only non-flora positive values from *potentially different remaining datasets*.

The source eligibility was frozen before either new source K result **within that stage**, but the organ grouping and five-flora restriction were conceived after seeing earlier AusTraits K results. Neither is a preregistered biological discovery.

## Actual 142-pair joint source restriction result

[GitHub Actions #39006469805](https://github.com/zuizui0223/turnover/actions/runs/39006469805) completed successfully, including 12 reproducible source-balanced K batches, a native small/large-tree smoke check and final source-source K aggregation. For each original K-blind-supported pair, both organ values are compared on **the same species and reconstructed native tree** in two observational arms:

- **Non-flora all sources:** Median of numeric trait values from *every* remaining source DatasetID, restricted to the common-source-qualified species cohort.
- **Non-flora shared source:** Median of numeric trait values from *only original non-flora DatasetID(s) that have positive observations of **both** organs for the same species*.

Both arms have **identical taxa, native phylogenetic tree and normalized K estimand**, so their within-pair contrast difference is observational-source composition rather than differential tree pruning.

| Joint source-qualified paired comparison | V.PhyloMaker2 S3 | Native GBOTB prune-only |
|---|---:|---:|
| K-blind qualified family×organ pairs | **142** | **142** |
| Native-tree K-pass pairs (≥20 tips) | **142** | **101** |
| Family clusters with K-pass comparisons | **24** | **18** |
| Tree support holds, not biological negatives | 0 | 41 |
| **Reproductive K higher — all remaining non-flora sources** | **121/142 = 85.21%** | **83/101 = 82.18%** |
| **Reproductive K higher — identical remaining source DatasetID(s)** | **120/142 = 84.51%** | **81/101 = 80.20%** |
| **Equal-family reproductive-K-higher rate — shared DatasetID arm** | **82.19%** | **69.89%** |
| Equal-family 95% bootstrap interval, 5,000 whole-family draws | **71.15–91.39%** | **53.06–85.00%** |
| Shared-DatasetID arm, 95% family-bootstrap CI pair weighted | **75.83–92.42%** | **72.40–89.11%** |
| Measurement-source substitution **alone** reverses K ordering | **9/142 = 6.34%** | **12/101 = 11.88%** |

The prune family-equal interval is relatively broad; **source-qualified family coverage has fallen from 29 (broad S3) to 24 (strict S3), and to 18 under native prune**. Do not interpret 142 or 101 dependent family×trait comparisons as independent evolutionary replications.

### Organ-subtype and named-trait checks (exploratory)

| Strict common non-flora DatasetID arm | S3 | prune |
|---|---:|---:|
| Fruits vs vegetative | **34/43 = 79.07%** | **23/28 = 82.14%** |
| Seeds vs vegetative | **86/99 = 86.87%** | **58/73 = 79.45%** |
| All organ comparisons EXCEPT Kew-sensitive `seed_dry_mass` | **107/124 = 86.29%** | **70/87 = 80.46%** |

The entire contrast cannot be attributed to seed dry mass or one Kew SID record source in these supported pairs. However, **these descriptive subtype differences are not matched taxonomic or independent-source experiments**: different seed/fruit pair types, their flora-excluded taxa and the families in which they are measurable have different support and study origins.

For strict common remaining DatasetID matches, Fabaceae yielded **9/15 S3 and 8/11 prune** reproductive-higher comparisons; Poaceae **10/12 on both**; Rubiaceae **4/4 S3 but 0/1 prune**. Neither source-screening nor the two native tree treatments establish a universal exception in Rubiaceae or Casuarinaceae. The latter is **absent from the strict 142-pair qualified graph** and thus no strict common-nonflora-source claim for that family can be made.

## Three-stage original family×trait-ID-matched decomposition: why the strict K direction may look stronger

A critical interpretation problem is that the **142** strict source-qualified family×pair IDs are a **subset of the earlier 283** source-eligible pairs, and strict source matching also removes many species/tips *within those same pair IDs*. Comparing crude 283-vs-142 rates confounds pair selection, sampling geometry and measurement sources.

A separate, fully validated [audit #39202352075](https://github.com/zuizui0223/turnover/actions/runs/39202352075) matches each strict 142 pair identity directly to its original broad non-flora K result, then compares three already frozen **log(K reproductive)−log(K vegetative)** estimands, without recomputing K or selecting pairs by outcome:

| Same selected family×trait pair identities | S3, 142 pair IDs/24 families | prune, 101 pair IDs/18 families |
|---|---:|---:|
| **1. Broad non-flora positive shared species/tips**, all non-flora source medians | **110/142 (77.46%)** | **82/101 (81.19%)** |
| **2. Restrict to species also supported in a common remaining DatasetID**, but keep all non-flora medians on those identical narrowed tips | **121/142 (85.21%)** | **83/101 (82.18%)** |
| **3. Same narrow species/tips/tree**, use only median values from the common DatasetID(s) | **120/142 (84.51%)** | **81/101 (80.20%)** |

**Changes attributable to source/tip geometry must be described separately:**

| Within the same fixed family×trait IDs | S3 | prune |
|---|---:|---:|
| Stage 1→2: changed **species/tip support and geometry**, K ranking flips | **23/142 (16.20%)** | **13/101 (12.87%)** |
| Stage 1→2: median absolute change in organ Δlog(K) | **0.1964** | **0.2513** |
| Stage 2→3: identical species/phylogeny, changed **observation-source medians**, K ranking flips | **9/142 (6.34%)** | **12/101 (11.88%)** |
| Stage 2→3: median absolute change in organ Δlog(K) | **0.0758** | **0.0948** |
| Stage 1→3: combined sampling and source shift, flips | **26/142 (18.31%)** | **15/101 (14.85%)** |

For S3, the same **selected 142 original family×trait pair identities** shift from 77.5% to 85.2% reproductive-high **primarily when the taxa qualifying the common source are chosen**; further restricting the measured values to the exact same source changes this to 84.5%. The native prune axis is more subdued (81.2%→82.2%→80.2%). The family-equal Stage 1→2 change is **+11.3 percentage points in S3 (95% 5,000-family bootstrap +0.5 to +22.7 pp)**, but only **+1.2 pp in prune (−4.5 to +7.2 pp)**. The Stage 2→3 family-equal rate change is **−1.1 pp S3 (−6.7 to +3.3 pp)** and **−1.5 pp prune (−7.2 to +3.8 pp)**.

The summary rates refer to **the same pair identities within an axis**, not exactly the same taxon set across *stages 1 and 2*, and the stage 1→2 shift includes species exclusions, tree geometry and K standardization. **It is not a causal estimate of sampling error or an ecological response to source changes.** The whole-family bootstrap intervals quantify retrospective descriptive sensitivity, not prospective confirmation.

### How to interpret the biology

The **robust biological pattern within the available original AusTraits data** is that fruit and seed morphology often exhibit greater *estimated phylogenetic signal K* than vegetative morphology, even after major species-composition, native-tree and source-ID restrictions. It survives at 75–85% in multiple source-qualified designs and is not wholly driven by the five electronic Floras or the `seed_dry_mass` trait.

The **equally important qualification** is that which families, named pairs and exact species qualify strongly alters the magnitude of the apparent advantage. Strict source agreement **cannot be credited for creating an 85% evolutionary signal law**; that rate partly reflects taxon/tip selection. A common remaining DatasetID may itself be a taxonomic monograph or floristic compilation, not new individually sampled primary trait measurements, and leaf/fruit/seed definitions may differ by family. Source heterogeneity and hidden original-data reuse remain potential explanations, and the original homogeneous source-OU model did **not** isolate an evolutionary alpha, sigma2, constraint or selection process.

The model previously frozen as `RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES` on the original scalar LOFO statistic remains unchanged. A later **post-outcome** organ module posterior-predictive discrepancy on original unequal-tip systems is a *different inferential question*; it does not upgrade this retrospective source robustness to process falsification.

## Hard stop and evidence needed for a new ecological discovery

The original [new-independent-source reproductive versus vegetative K replication protocol](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_reproductive_vegetative_k_external_validation_protocol_v0_1.json) remains fixed: ≥12 independent provenance-qualified families with ≥20 exact shared species per organ comparison, both native tree treatments, both seed and fruit and vegetative support, verified original measurement lineage/organ definitions and no reused AusTraits underlying data. **No current TRY v7 source has met this gate.**

**Stop further post-outcome “favorable source-subset” searches on original AusTraits.** The next work is paper figure QA, manuscript completion and a genuinely external primary-measurement cohort. Do not reopen the scientifically closed BIEN 201-system rho data.

## Reproduction

- [Original 283 five-electronic-flora exclusion study](https://github.com/zuizui0223/turnover/actions/runs/38922133371)
- [Final 142 common non-flora DatasetID K study](https://github.com/zuizui0223/turnover/actions/runs/39006469805)
- [Verified 24/18-family three-stage sampling-vs-measurement decomposition](https://github.com/zuizui0223/turnover/actions/runs/39202352075)
- [Freeze file for the post-outcome decomposition](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_k_nonflora_cohort_transition_v0_1.json)
- [Three-stage reanalysis code and fail-closed tests](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/scripts/analysis/audit_austraits_k_nonflora_cohort_transition_v0_1.py)
- No new raw trait values, individual species names or observation IDs were exposed in this reconciliation.
