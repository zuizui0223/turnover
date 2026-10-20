# AusTraits organ-K paper — durable reproducibility and source citation (v0.1)

**Updated: 2026-10-20.** Scope: original AusTraits v7.0.0 `turnover` paper PR #38; descriptive, **post-discovery** source/organ-K results only. This file is not a new dataset, biological fit, source-trait search, or independent replication.

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
