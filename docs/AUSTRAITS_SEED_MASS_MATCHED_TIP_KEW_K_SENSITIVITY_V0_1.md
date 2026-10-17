# Source composition versus phylogenetic tip support in seed dry mass K

**Verified 2026-10-15.** Original Kew-source removal source-eligibility cohort fixed **before this matched-tip K result** (but **after** the original AusTraits K and source-OU discovery). This is a post-outcome, exploratory sensitivity, **not independent TRY v7 validation**.

## Reproduction

[Successful exact-tree paired K workflow #38407138733](https://github.com/zuizui0223/turnover/actions/runs/38407138733), artifact `austraits-seed-mass-matched-tip-kew-sensitivity-v0-1`, frozen design `data/austraits_seed_mass_matched_tip_kew_sensitivity_v0_1.json`. Exact AusTraits 7.0.0 parquet SHA256 and V.PhyloMaker2 commit are pinned. All-original-source and non-Kew-only positive source-native median values are evaluated on **identical retained species tips and exactly the same reconstructed tree**, separately on S3 and native prune. Original full-tip K is used only for the separate descriptive support/geometry component.

Original seed dry mass: 15 family systems, 4,242 species×system cells. After excluding `Kew_2019_1`, 2,072 positive-median species×system cells remain and 13 families have ≥20 species; the prune tree for one of those families does not meet 20 supported tips.

## Decomposition

`delta_source = log(K_nonKew_matched_tips) - log(K_all_sources_matched_tips)`

`delta_support_geometry = log(K_all_sources_matched_tips) - log(K_all_sources_original_full_tips)`

`delta_total = delta_source + delta_support_geometry`

| Exploratory component | S3 (13 families) | prune-only (12 families) |
|---|---:|---:|
| Source-only median Δlog(K) | **−0.0024** | **+0.0191** |
| Source-only mean Δlog(K) | +0.0177 | +0.0223 |
| Source-only min to max | −0.1587 to +0.3401 | −0.0642 to +0.1466 |
| Source-only positive/negative family deltas | 6 / 7 | 9 / 2 (one near-zero) |
| **Tip-support/geometry median Δlog(K)** | **+0.1101** | **+0.2397** |
| Tip-support/geometry mean Δlog(K) | +0.2523 | +0.3989 |
| Tip-support/geometry min to max | −0.8311 to +1.5857 | −0.6917 to +2.4503 |
| Total median Δlog(K) | +0.2325 | +0.2148 |

**Interpretation:** In the families where source-only comparisons can be made on exactly matched tips, excluding Kew observations has a small *median* effect on estimated K; **which species remain and the associated phylogenetic support/geometry shift often have a much larger effect**. This does not imply that source composition has no effect in every family: Rhamnaceae S3 +0.3401 and Fabaceae S3 −0.1587; Solanaceae prune +0.1466. Nor does a larger tip-support effect prove an evolutionary process.

The tip-support component is not a pure tree-topology effect: it combines **species inclusion/exclusion, associated branch geometry and phylogenetic K normalization**. No causal decomposition or extrapolation to excluded species is justified. Median components do not necessarily add to median total because they are computed across families.

## Ecological implications and boundaries

1. A strong source-family representation (Kew contributes to 78.88% of original seed-mass species×system cells) does **not** automatically imply a large same-tip K bias. Non-Kew median reconstruction retains 48.84% of the original species×system cells, and matched-tip median source-only Δlog(K) is near zero on S3.
2. But dropping the Kew source changes **which taxa** can be analyzed. The observed support/geometry component is often larger than the same-tip measurement-source component. This is consistent with **phylogenetic sampling and taxonomic coverage** being a major factor in the estimated K magnitude for this trait; it is not evidence of a different OU process.
3. A source-only exclusion is **not** independent biological replication: non-Kew AusTraits sources may share underlying primary observations, and TRY v7 original-record genealogy remains unverified.
4. The previously frozen primary classifier `RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES` is unchanged. The five signed named-rank deviations remain *post-outcome* hypotheses. This 13-family single-trait sensitivity cannot establish their cross-trait ranking portability or test selection.
5. Next biological discriminator: independently source-qualified, matched-tip sampling across **multiple traits**. Before that, do not claim trait-specific evolutionary constraints from a seed-mass-only source sensitivity.

**Status:** source-only sensitivity **reproduced**; independent TRY v7 source validation **HOLD**. Closed BIEN 201-system rho analysis not reopened.
