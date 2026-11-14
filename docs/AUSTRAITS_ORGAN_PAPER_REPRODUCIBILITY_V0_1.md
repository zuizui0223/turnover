# AusTraits organ-K paper — durable reproducibility and source citation (v0.1)

**Updated: 2026-10-28.** Scope: original AusTraits v7.0.0 `turnover` paper PR #38; descriptive, **post-discovery** source/organ-K results only. This file is not a new dataset, biological fit, source-trait search, or independent replication.

## Original 254 single-trait phytools K clean-source replication (28 October 2026)

[Full unchanged original R phytools K workflow #40541276639 PASS](https://github.com/zuizui0223/turnover/actions/runs/40541276639) reconstructed **all 254 single-trait K reference systems in 42 families and 13 traits** from the SHA256-pinned public AusTraits v7.0.0 source in **16/16 original batches** on both native S3 and prune phylogenies. All original per-system native-tree tip counts, K and log K values agreed with the SHA256-frozen historical R outputs: **maximum absolute discrepancy 0.0**, assessed at the original four-decimal saved precision.

[Permanent 254-system replay archive #40610003843 PASS](https://github.com/zuizui0223/turnover/actions/runs/40610003843) independently rechecked and committed all **254 new K JSONs, 16 batch QA outputs, final numeric verdict and SHA256 manifest** to the [original public-v7 254 single-K directory](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_public_v7_254_single_K_replay_v0_1). The actual realized S3/prune native K tip counts were verified; source eligibility and V.PhyloMaker crosswalk counts can differ from final tree tip counts and were not falsely equated.

**Full evidence boundary:** The original 254 single-trait K, 760 native matched-tip K, and 283 broader/142 strict nonflora source K with original 142/101 stage results and family bootstrap are now reproducible on the **same original public AusTraits v7 source**. These computations are not independent primary-study ecological replication, prospective organ-group selection or causal selection/evolutionary-rate evidence. Contributing-study attribution, complete journal data/metadata/code requirements, author declarations and explicit permission to submit remain unresolved.

## Exact primary dataset version and method citations

**Actually analyzed dataset:** Falster, D., Gallagher, R., Wenk, E., & Sauquet, H. (2025), *AusTraits: a curated plant trait database for the Australian flora* (version **v7.0.0**), Zenodo **https://doi.org/10.5281/zenodo.15718081** (published June 2025). The original database descriptor, Falster et al. (2021), *Scientific Data* 8:254, **https://doi.org/10.1038/s41597-021-01006-6**, describes an **older v3.0.2 era**, so both original-paper and **v7.0.0 version-specific** citations should be included.

The release is **CC BY**; re-use requires attribution, and the original contributing studies should be cited where applicable. The full 2025 v7.0.0 source-native measurement matrix is **not** mirrored into this research paper PR; it remains available from the DOI source. This omission does not imply that the published v7 release is closed or legally unusable.

Published methodology:

- Blomberg, Garland & Ives (2003), original phylogenetic-signal measure K, `Evolution` 57:717–745, DOI **10.1111/j.0014-3820.2003.tb00285.x**.
- Jin & Qian (2022), `V.PhyloMaker2`, `Plant Diversity` 44:335–339, DOI **10.1016/j.pld.2022.05.005**.
- Revell (2012), `phytools` K parity implementation, `Methods in Ecology and Evolution` 3:217–223, DOI **10.1111/j.2041-210X.2011.00169.x**.

The source-native continuous positive-median log transform and the original GBOTB S3/prune tree construction are documented within the original paper Methods and code. None of the K estimands or branch lengths were revised for this citation/readiness step.

## Archival risk fixed

The original three figure-input aggregate JSON files came from GitHub Actions and **could expire**. A new archive-only workflow [CI #39402465299](https://github.com/zuizui0223/turnover/actions/runs/39402465299) passed and committed **only the three original already-opened aggregate outputs**, plus their SHA256 manifest, to:

[**Persistent original aggregate sources**](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_frozen_aggregate_inputs_v0_1)

| File | Original source run | Exact original bytes SHA256 |
| --- | ---: | --- |
| `reproductive_vegetative_lofo.json` | 38686389859 | `7648ff07a734b96686629d9d158c215670bccbcdec7c6cf385aae9a11a76cfa1` |
| `nonflora_283_to_142_source_support_transition.json` | 39202352075 | `5cba03348e4c2342db2e1df202c6036b6b265a829ac43e816388f9f84cc79397` |
| `joint_nonflora_shared_source_K.json` | 39006469805 | `fc9bc62297a16db916f21704203ab1859f65dce33303a8199cb49a6596819dbb` |

These **aggregate** data contain family-level and original family×named-trait-pair K summaries, not new trait measurements or raw species-by-specimen records. Frozen statuses, exact file checksums, non-independence flags and original pair/tip counts are checked by `scripts/publication/freeze_austraits_organ_aggregate_archives_v0_1.py`. The original external primary-source validation of the organ K hierarchy **remains untested**.

## Full original 283/142 nonflora source-stage K reproduction (23 October 2026)

[All 28 native-tree source-stage R/C++ K batches #39723170670 PASS](https://github.com/zuizui0223/turnover/actions/runs/39723170670) recovered the original **283 S3/233 prune broader nonflora** and **142 S3/101 prune strict shared-DatasetID** comparison outcomes directly from the public AusTraits v7.0.0 Parquet using the original exact source units and native tree builder. All original K values and source-specific log-K contrasts matched the frozen historical K outputs, with **maximum absolute numerical difference 0.0**. The original identity-matched **S3 110→121→120 (142)** and **prune 82→83→81 (101)** reproductive-higher source/taxon-stage directions were recovered, with 23/9 and 13/12 sign flips over the respective stages.

[Permanent 60-file SHA256 source-stage archive #39877245159 PASS](https://github.com/zuizui0223/turnover/actions/runs/39877245159) independently regenerated every original pairwise source-K and original **5,000-family bootstrap** summary before committing fresh K results, QA reports, aggregate results and manifest under [nonflora K replay source archive](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_public_v7_nonflora_3stage_replay_v0_1). [Complete K-blind source eligibility from public v7 #39723741575 PASS](https://github.com/zuizui0223/turnover/actions/runs/39723741575) was byte-identical to the original source-support report (SHA256 `2870909f97d492400d7a3f6978f94689e5a829ed719cd48340d0633c0f9c83d5`).

This is **numerical reproducibility on the same original AusTraits data**, not independent primary-study evidence, causal ecology, selection/OU-rate inference or a prospective biological hypothesis. Stage 1→2 changes species/tips/tree normalization together; Stage 2→3 changes the observation-source values on strictly identical tips. The separate original 254 single-trait K reference fits were not rerun in these paired pipelines.

## Full original 760-pair matched-tip K numerical reproduction (22 October 2026)

**COMPLETE TECHNICAL REPRODUCTION ON THE SAME ORIGINAL PUBLIC DATA.** [Full 760-pair raw-source K CI #39713644617](https://github.com/zuizui0223/turnover/actions/runs/39713644617) completed **PASS** in all 26 jobs (24 raw-source R/C++ K batches, source-only workload preparation and independent final aggregation). From the pinned public AusTraits v7.0.0 Parquet with exact SHA256, all 760 original matched-tip comparisons were newly computed on the original S3/prune trees and checked against the original K estimates; the **maximum absolute K or log-K numerical discrepancy was 0.0**. The complete population and directional counts were unchanged: **S3 760 PASS, 406 cross-organ comparisons, 313 reproductive-higher; native prune 747 PASS and 13 HOLD, 397 cross-organ comparisons, 314 reproductive-higher**. No new biological result, model selection or independent data source was introduced.

The original 24 historical K files and *newly* generated 24 complete R K outputs, 24 per-batch numerical integrity audits, final result and SHA256 manifest have been preserved permanently on this paper branch at [public v7 full K replay archive](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_public_v7_full_K_replay_v0_1), validated by [long-term archive CI #39721134903 PASS](https://github.com/zuizui0223/turnover/actions/runs/39721134903). The final verdict is \`PASS_ALL_760_RAW_SOURCE_K_RECOMPUTED_AND_MATCHED\`, and the permanent manifest is \`reproduction_archive_manifest.json\`. No raw species/observation-level measurements were committed.

**Boundary:** This full replay used the historical 254 original single-trait K system values as *reference contrast inputs*; it freshly reconstructed the 760 **matched-tip** K pairs, not the 254 separate original single-trait K fits or the strict 142/101 non-flora source-subset K analyses. Repeating computations on original AusTraits does not provide primary original-study disjoint replication or test evolutionary rates, selection, constraints, causal ecological mechanisms or generality across independent plant data. Formal journal data/metadata availability and contributor attribution remain author-review gates.

The following section records the earlier, superseded **two-pair preliminary technical smoke**.

## Public raw-data source-selection and native K technical reproduction (2026-10-21; preliminary)

**A second, more complete tier of reproducibility is now supported.** We preserved the original source-only 259-system core (254 K-system subset), 254 original K estimates and all 770 candidate / 760 supported pair identities under [permanent source/K reference files](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_frozen_rebuild_inputs_v0_1). The original complete **24 real-tree paired K batch outputs** (760 S3 and 747 native-prune valid comparisons) have also been permanently recorded under [original per-pair K outputs](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_original_pair_K_v0_1). All original aggregate input files have SHA256 manifests; none includes raw species/observation trait values. [Source-core preservation #39448885872](https://github.com/zuizui0223/turnover/actions/runs/39448885872) and [original R K archival #39450135788](https://github.com/zuizui0223/turnover/actions/runs/39450135788) both passed.

[Fresh source-to-K CI #39451543289](https://github.com/zuizui0223/turnover/actions/runs/39451543289) then downloaded the original **public** AusTraits v7 flattened Parquet, verified source SHA256 **5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99**, and rebuilt the **entire source-only 770/760 pair-eligibility graph** with every pair/source count agreeing with the archived original. The unchanged R/C++ and pinned V.PhyloMaker2 scripts also recomputed *two previously source-qualified cross-organ exemplar pairs* on both S3 and native-prune trees: Casuarinaceae fruit length/leaf length (47 shared species, 47/40 tree tips) and Asteraceae fruit width/leaf length (177 shared species, 177/81 tips). All four recomputed K and log-contrast outputs were **numerically identical to the frozen original R pair-batch references (maximum absolute difference 0.0)**.

**Historical stage boundary (21 October only):** At this earlier stage, the test reconstructed two K comparisons but had **not yet** re-executed all 760 original pair estimates. The later **22 October full replay is confirmed above**. Neither stage is independent original-study replication, external biological validation, rate/selection/OU inference or prospective organ-grouping evidence. The reviewed ecological effects 313/406 and 314/397 remain unchanged. The exact source selection, commands, tests and remaining reproducibility limitations are recorded in [raw-K technical documentation](https://github.com/zuizui0223/turnover/blob/paper/austraits-organ-ecology-v0-2/docs/AUSTRAITS_ORGAN_RAW_K_REBUILD_VERIFICATION_V0_1.md).

## Offline relative-to-repository figure reconstruction

Run from the `paper/austraits-organ-ecology-v0-2` checkout:

```bash
python -m pip install numpy matplotlib

python scripts/publication/freeze_austraits_organ_aggregate_archives_v0_1.py \
  --inputs results/austraits_organ_paper_frozen_aggregate_inputs_v0_1

python scripts/analysis/render_austraits_organ_k_paper_figures_v0_2.py \
  --module results/austraits_organ_paper_frozen_aggregate_inputs_v0_1/reproductive_vegetative_lofo.json \
  --transition results/austraits_organ_paper_frozen_aggregate_inputs_v0_1/nonflora_283_to_142_source_support_transition.json \
  --joint results/austraits_organ_paper_frozen_aggregate_inputs_v0_1/joint_nonflora_shared_source_K.json \
  --claims data/austraits_organ_paper_claim_registry_v0_2.json \
  --out-dir build/figures
```

This reconstructs the **two main figures plus the supplementary probability-scoring figure** and its `figure_manifest.json`, without network access to the historical Actions artifacts. [Figure regeneration verification](https://github.com/zuizui0223/turnover/actions/runs/39402642194) passed after switching to committed source snapshots.

The parallel Word/PDF coauthor-review workflow `.github/workflows/austraits-organ-coauthor-review-bundle-v0-1.yml` also regenerates the same original figures and both reporting-only QA results **from this branch**; it no longer downloads short-lived historical source artifacts. It still installs open-source document-conversion utilities to render DOCX/PDF and does not refit K.

## Inference and preservation

- **Descriptive matched-tip direction:** 313/406 S3 and 314/397 prune reproductive K wins in 34 AusTraits families, selected *after* observing original K.
- **Taxon/source sensitivity on identical original family×named-pair identities:** 110→121→120 S3 and 82→83→81 native prune reproductive K wins; stage 1→2 changes species and native tree geometry jointly, stage 2→3 changes source values on fixed tips.
- **Nominal 64.47%/65.46% LOFO hard accuracy:** algebraic restatement of the above original organ K sign counts plus half-credit ties, **not an independent second discovery**. LOFO Brier is a post-selected conditional probabilistic score.
- **Unverified:** primary-original-study-independent replication, causal evolutionary-selection/constraint mechanisms, full family phylogenetic independence, global plant-taxon generality.

**Author-facing status:** Aggregate figure and table reproducibility is durable in the PR; a journal submission still requires the actual coauthors' approvals, data-version/original-source credit checks, target-journal formatting and explicit author consent. Do not merge or submit automatically.
