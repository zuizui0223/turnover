# Organ-specific phylogenetic K persists under same-source, same-species and same-tree restriction

**Verified 2026-10-15; post-discovery robustness within AusTraits v7.0.0, NOT independent external source replication or a test of natural selection.** The [complete 279-pair workflow #38698215216](https://github.com/zuizui0223/turnover/actions/runs/38698215216) **succeeded in all 18 jobs**, including preparation, 16 source-qualified original phylogenetic K batches and final aggregation. [Source-only qualification #38696272257](https://github.com/zuizui0223/turnover/actions/runs/38696272257) was frozen before the source-restricted K outcomes were opened. Results in CI artifact `austraits-k-279-same-dataset-organ-final-v0-1`. Full reproduction code, synthetic record-join tests and original AusTraits source checks remain in the PR.

## Question, estimands and support

The previous 760 comparisons controlled **identical plant species and identical trees** but allowed reproductive and vegetative trait states to be estimated from **different contributing AusTraits datasets**. This analysis adds an internal observation-source restriction:

1. Start from original positive-median species and the **406** source-eligible cross-organ family×trait pairs, ignoring their observed K outcome.
2. Retain the **279 family×cross-organ pairs in 32 families** where at least 20 original common species have a positive measurement of both traits in **at least one same `dataset_id`**. These source-based eligibility rules are fixed before recalculating K.
3. For each such pair and species, estimate the original all-dataset median for each organ and a separate median based **ONLY on original AusTraits contributing dataset IDs shared by the two organs on that species**. Require source medians to be positive. The same species-tip list and reconstructed native tree are used for all **four** K estimates (two traits × two source arms).
4. Compare `ΔlogK = log(K_reproductive) − log(K_vegetative)`, first under all original source medians, then under shared-source medians, separately for V.PhyloMaker2 S3 and native prune-only. No data-dependent family selection, source substitution, or tree modification is permitted after K outcomes.
5. Resample **whole plant families** (5,000 bootstrap replicates) for uncertainty, not the dependent family×trait pairs themselves. All source eligibility and aggregate family results are retained.

## Full results

| Same-tip comparison on 279 source-prequalified pairs | S3 | Native prune |
|---|---:|---:|
| Source-qualified candidate family×organ pairs | **279** | **279** |
| Native K pairs with ≥20 supported exact tree tips | **279** | **246** |
| Paired native-tree/median HOLD | 0 | 33 |
| Plant families represented | **32** | **32** |
| **All AusTraits contributing datasets: reproductive K higher** | **217/279 = 77.78%** | **179/246 = 72.76%** |
| **Only dataset IDs common to both traits: reproductive K higher** | **209/279 = 74.91%** | **183/246 = 74.39%** |
| Bootstrap 95% CI of pair-weighted common-source rate (family resampling) | **67.08–81.97%** | **67.31–81.14%** |
| **Equal-family mean common-source reproductive win rate** | **72.85%** | **71.20%** |
| 95% family-bootstrap CI of equal-family common-source mean | **61.91–82.65%** | **61.80–80.30%** |
| **Identical-tip source-composition-only K-order sign flips** | **18/279 = 6.45%** | **26/246 = 10.57%** |
| Median source-composition shift in reproductive−vegetative `ΔlogK` | −0.0133 | −0.0117 |
| Mean source-composition shift in reproductive−vegetative `ΔlogK` | −0.0507 | −0.0337 |

**Key inference:** Restricting measurements to common AusTraits contributing dataset IDs has only a small *median* effect on the within-family organ K contrast, and **a reproductive K advantage is preserved on both native tree axes**. This is stronger internal robustness evidence than merely matching species and trees, but it is still **not independent source replication** or identified evolutionary constraint.

The smaller source-composition sign-reversal rates do **not** directly contradict the original 760-pair 19.9% / 18.3% sign reversals: the earlier rates compare separate-original-tip K against common-tip K, whereas this new result compares **two measurement-source arms on exactly identical source-prequalified tips and trees**. They have different estimands and source-selected cohorts.

### Organ-category and source-concern robustness

| Common AusTraits dataset source only | S3 | Prune |
|---|---:|---:|
| Fruit morphology vs vegetative K | **117/159 = 73.58%** | **107/143 = 74.83%** |
| Seed morphology vs vegetative K | **92/120 = 76.67%** | **76/103 = 73.79%** |
| All organ comparisons except seed dry mass | **196/261 = 75.10%** | **172/232 = 74.14%** |

These rates remain above 0.5, although **the underlying metadata source classes and cross-organ trait protocols may share systematic biases**. Excluding `seed_dry_mass` is useful due to its original high representation from the Kew SID derivative compilation, but this does not remove every potential compiled or correlated data source.

## Plant family contexts and counterexamples

| Family | Same-source reproductive K higher S3 | Native prune | Interpretation |
|---|---:|---:|---|
| **Fabaceae** | **18/23** | **18/21** | Within-source positive family contrast remains |
| Poaceae | 11/12 | 10/12 | Mostly reproductive on both |
| **Casuarinaceae** | **0/3** | **1/3** | Opposite/weak reproductive trend, but only 3 source-qualified pairs |
| **Rubiaceae** | **0/6** | **0/6** | Opposite trend persists with common source data |
| Lauraceae | 4/8 | 3/6 | Family and phylogenetic tree treatment sensitive |
| Cyperaceae | 6/8 | 3/3 | Source restriction changes subset/relative weighting |

For the **246 pairs** with valid K on both native trees, the **common-source** organ winner agrees on **221** pairs (172 reproductive higher on both, 49 vegetative higher on both), while **25** differ between tree axes. This retains nonuniversal family structure even under source matching.

The [independent original native-source ontology audit #38698913288](https://github.com/zuizui0223/turnover/actions/runs/38698913288) found `Casuarinaceae` source support largely from compiled taxonomic floras: `ABRS_2023` (34 species from *Flora of Australia*) and `NHNSW_2023` (5 species from a state flora/PlantNet source), with overlapping species. Metadata describe `leaf_length` as "leaf or leaf analogue" and `fruit_length` via named fruit/achene/capsule notes. This is **not a verified homologous lamina/samara definition**, particularly for scale-leaved Casuarinaceae. Source-only K robustness does not resolve underlying botanical measurement ontology or common specimen identity.

## Reviewer-facing limitations

- **Shared AusTraits `dataset_id` is not necessarily shared primary data collection:** both organ measurements can be extracted from an online flora, compiled trait database or different original field sources; even identical `dataset_id+observation_id` is not physical specimen identity without native reference/protocol audits.
- **Post-outcome comparisons:** the organ grouping and lineage exceptions were selected after original AusTraits K and matched-tip K results. This stricter source restriction was designed after that discovery, though the 279 source-eligibility list was frozen before the new source K outcomes. This is *within-discovery robustness*, not prospectively replicated biology.
- **Coverage shifts:** the 279-pair subset is a source-defined subset of 406 cross-organ pairs. Under full-source medians on the new same-source cohort, S3 reproduces **77.8%** positive rate; prune yields **72.8%**, lower than the previously 397-pair prune estimate of 79.1%. It would be invalid to ascribe this difference solely to measurement-source effects; the restricted species/taxon and family pairing composition also changed.
- **Not a mechanistic K null:** the source-OU plus K-blind observational heterogeneity models were fit on original separate-tip 249 K systems, **not** re-generated for each new same-source pair's reduced tree and source-specific record covariance. They cannot serve as direct posterior predictive nulls for the 279 same-source K percentages.
- **Not source or phylogeny independence:** all comparisons still use AusTraits-derived original records and a common family-level tree backbone. Cross-family reused taxonomic flora records and trait-class protocols can induce correlations.
- **No causal selection, developmental constraint or evolutionary-rate interpretation:** the direction of Blomberg's K is a sampling- and variance-conditioned statistic, not an identified OU alpha, rate or fitness effect.

## Scientific outcome and research next step

**Decision:** The positive, exploratory finding that reproductive organ morphology often has stronger phylogenetic K than vegetative morphology is robust to *species*, *tree*, and now *same-contributing-dataset restriction* in the observed original AusTraits cohort. It is **not robustly mechanistically explained** by the tested evolutionary and observational nulls. A truly independent cross-source reproduction is still required and must distinguish flora/secondary species summaries from primary, semantically harmonized organ measurements.

The already locked [new-source organ K replication protocol](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_reproductive_vegetative_k_external_validation_protocol_v0_1.json) remains unchanged: ≥12 independently source-qualified plant families, ≥20 matched species per family×pair, support for both fruit- and seed-versus-vegetative organ contrasts on BOTH native phylogenetic tree axes, audited primary record identities and measurement definitions. No TRY v7 independent record cohort currently passes this gate.

**Reproduce:** [GitHub Actions workflow #38698215216](https://github.com/zuizui0223/turnover/actions/runs/38698215216), frozen [design](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_k_same_dataset_organ_matched_tip_sensitivity_v0_1.json), source and phylogeny [scripts](https://github.com/zuizui0223/turnover/tree/analysis/brownian-process-null-v0-1/scripts/analysis), and final archived `austraits-k-279-same-dataset-organ-final-v0-1` output. Closed original 201-system BIEN rho study is not reopened.
