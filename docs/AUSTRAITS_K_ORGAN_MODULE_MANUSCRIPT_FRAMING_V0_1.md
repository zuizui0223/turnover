# Manuscript framing — Functional organ context of plant phylogenetic K across lineages

**Draft prepared 2026-10-15; evidence verified on original AusTraits v7.0.0; exploratory biology, not a confirmatory evolutionary-process discovery.**

## Proposed main title

**Reproductive morphology predicts phylogenetic trait signal across plant lineages, but lineage and source context limit portability**

Alternative: **Plant organ identity carries transferable phylogenetic signal beyond taxonomic-sampling differences**

Avoid titles claiming universal reproductive evolutionary stasis, stabilizing selection, distinct evolutionary OU parameters, or that phylogenetic signal itself equals an evolutionary rate.

## One biological question

When plant traits are compared on the **same species and phylogenetic relationships**, does organ function (seed/fruit reproductive morphology versus leaf/plant-height vegetative morphology) tell us something systematic about the relative phylogenetic signal of those traits, and is that information transferable to a family absent from the training data?

This is less trivial than simply asking whether a trait exhibits significant phylogenetic signal. It tests whether a **biologically interpretable class** transfers information to an **unseen lineage** beyond sharing the exact taxon/tree geometry.

## Reproducible empirical answer

The fixed 249-system source-calibratable AusTraits graph contains 12 named traits in 42 families. Original source-native species-state support yielded **760 family×trait pairs** (66 different named pairs) with at least 20 common species; both traits in each comparison were fitted using the **same species and native tree**.

- **Reproductive versus vegetative:** across **34 plant families**, seed/fruit K > leaf/plant-height K in **313/406 (77.1%)** S3 and **314/397 (79.1%)** prune comparisons; family-equal rates **74.7% / 75.8%**, with family-bootstrap CIs **64.3–84.4% / 67.4–84.1%**.
- **Observation-source robustness:** excluding the Kew-dominated `seed_dry_mass` trait still yields **263/344 (76.5%) S3 and 268/337 (79.5%) prune**; fruit traits alone versus vegetative: **149/193 (77.2%) / 150/189 (79.4%)**. This does not prove independent primary measurement sources.
- **Out-of-family transfer:** a one-parameter reproductive/vegetative identity model trained separately on the **other 41 families** correctly predicts the K sign in the withheld family on **64.5% S3 / 65.5% prune** of all 760/747 qualified pair comparisons, versus **52.6% / 53.8%** for a pooled other-family sign prior. Brier probability loss improves from **0.2506→0.2138 / 0.2502→0.2067**, with 42-family-bootstrap Brier-skill intervals above zero in both tree treatments. A 12-named-trait identity model does not materially improve the descriptive heldout prediction (Brier **0.2179 / 0.2116**).
- **Explicit lineage exceptions:** Fabaceae **35/36 and 34/34** reproductive K wins; Casuarinaceae **2/12 and 3/12**; Rubiaceae **1/6 and 2/6**; Lauraceae changes from **1/9 to 6/9** across S3/prune, illustrating nonuniversality, limited independent family support and tree dependence.
- **Process-model adequacy is a separate, post-outcome diagnostic:** on the ORIGINAL (unmatched) 249 source-system geometry, observed reproductive-higher K proportions are **302/410 (73.7%) S3, 330/410 (80.5%) prune**; pre-existing common OU + K-blind source-noise scenario means are roughly **58–64% / 61–68%**, and the observed original-tip proportions exceed 12 correlated scenario×tree 97.5% simulation bounds. **This post-outcome module result does not overturn the pre-frozen scalar source-OU process null**, which accommodates the observed *amount* of trait rank portability, nor can its Monte Carlo tails be used as preregistered discovery p-values.

## Strongest within-source robustness result, completed 2026-10-15

The source-only qualifying stage tested all originally comparable cross-organ trait pairs **without reading their K outcomes** and identified **279 family×pair comparisons spanning 32 plant families** with ≥20 species for which both reproductive and vegetative organ measurements came from an **identical contributing AusTraits DatasetID**. The subsequent [18-job workflow #38698215216](https://github.com/zuizui0223/turnover/actions/runs/38698215216) recomputed the K of each organ twice on **identical species and phylogenetic trees**: first using all original observed AusTraits trait values on those same species, then restricting medians to source DatasetIDs **shared by both organ measurements for each species**.

| Source restriction on identical species and tree | S3 | Prune-only |
|---|---:|---:|
| Source-qualified pairs | 279 | 279 |
| K-supported pairs after phylogeny check | **279** | **246** |
| **Reproductive organ K higher using shared-DatasetID observations only** | **209/279 = 74.91%** | **183/246 = 74.39%** |
| Equivalent K higher using ALL source measurements on these SAME reduced tips | 217/279 = 77.78% | 179/246 = 72.76% |
| Reproductive dominance **equal-family average**, 32 families | **72.85%** | **71.20%** |
| Equal-family 95% whole-family bootstrap | **61.91–82.65%** | **61.80–80.30%** |
| Sign inversion due solely to changing original AusTraits contributing DatasetID source arm (species/tips/tree fixed) | **18/279 = 6.45%** | **26/246 = 10.57%** |

The source-only sensitivity retains reproductive K dominance **even when all seed dry mass comparisons are excluded** (**196/261 S3 / 172/232 prune**) or only fruits are compared with vegetative traits (**117/159 / 107/143**). This is the strongest **internal robustness check** now available, and it is distinctly **not independent external confirmation**.

Family context persists: under source-restricted K, **Casuarinaceae 0/3 S3 and 1/3 prune**, **Rubiaceae 0/6 on both native trees**, while **Fabaceae 18/23 S3 and 18/21 prune** show the opposite positive tendency. The actual original source documentation for Casuarinaceae comes primarily from **online taxonomic floras**, with source metadata for `leaf_length` allowing **"leaf or leaf analogue"** and for `fruit_length` spanning fruit/achene/capsule terminology. A shared DatasetID can therefore still label **floristic aggregate species descriptions**, not identical independently measured specimens or homologous broad leaves. Report the botanical **homology/ontology limitation** as an important unresolved alternative mechanism.

The dedicated [full 279 source-arm verdict](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/docs/AUSTRAITS_K_SAME_DATASET_ORGAN_279_VERDICT_V0_1.md) preserves the design, exact source results, family cluster uncertainty, tree axis holds and limitations. New primary-measurement validation under the previously locked external organ protocol is still absent.

## One-sentence manuscript conclusion

**Functional organ category carries limited but measurable cross-family predictive information about phylogenetic trait K, even when species and trees are standardized, while several lineages reverse the trend and tested common evolutionary-plus-observation models fail to predict the specific organ identity ordering.**

The phrase "limited but measurable" is essential: **~65%** out-of-family accuracy is useful but far from deterministic, and these folds share AusTraits primary-source regimes.

## Draft abstract (working, not submission-ready)

Understanding whether the phylogenetic signal of functional traits generalizes across evolutionary lineages requires separating organ identity from taxonomic and observation-source context. We reconstructed 760 within-family comparisons of 12 AusTraits morphological traits on identical species and phylogenies. Across 34 families, reproductive seed and fruit traits showed higher Blomberg's K than vegetative leaf and height traits in 77.1% (S3) and 79.1% (prune-only) of comparisons. We then used a K-blind source eligibility audit to identify 279 reproductive–vegetative comparisons from 32 families in which the same contributing dataset included measurements of both organs for at least 20 common species. Restricting observations to shared original DatasetIDs while holding species and trees fixed, reproductive K remained higher in 74.9% of S3 and 74.4% of prune comparisons; changing observation sources alone reversed 6.5–10.6% of K orderings. A simple organ-category model trained on all other families predicted a held-out family's K ordering with 64.5–65.5% accuracy versus 52.6–53.8% for a pooled sign baseline. Yet Casuarinaceae and Rubiaceae showed contrasting patterns, and original source records for some families were based on floristic species descriptions with potentially nonhomologous organ definitions. Homogeneous Ornstein–Uhlenbeck models with calibrated observation-source heterogeneity reproduced scalar rank portability but underpredicted the observed reproductive–vegetative K ordering on the original trait-specific tip sets. These explicitly exploratory results suggest that organ identity carries cross-family predictive information about phylogenetic signal beyond simple taxon- and contributing-dataset mismatches, but they do not identify evolutionary constraint or selection. Independent primary measurements with harmonized organ definitions and source-aware evolutionary covariance models are required for causal or mechanistic interpretation.

## Figure storyboard

1. **Matched-species comparisons and inference separation:** 254 original K systems → K-blind 249 source-calibratable systems → 760 source-eligible family×named-pair comparisons on identical taxon/tree supports → matched K sign contrasts. Show original-tip OU model adequacy and held-out-family evaluation as **separate branches**, not one null matched to the wrong geometry.
2. **Reproductive vs vegetative K by family:** 34-family equal-weight forest/dot plot, sample pair counts annotated. Emphasize consistent strong families and exceptions (Casuarinaceae/Rubiaceae) while visually encoding low support and S3/prune differences.
3. **Transfer to a novel family:** LOFO Brier score and half-credit hard sign accuracy: pooled other-family prior; organ class (one coefficient); all named-trait Bradley–Terry (12 score coefficients); exact named-pair Laplace. Add cluster-resampled 42-family CI for differences against the pooled prior.
4. **Posterior-predictive model adequacy:** observed original-tip organ win rate versus homogeneous OU+source models (trait-global versus family×trait-local, c=.25/1/4), separately for S3 and prune. Label as **post-discovery adequacy check on original disparate taxa**.
5. **Source confound context (supplement):** Kew SID contributes to 3,346/4,242 original seed dry mass cells; after excluding Kew, 2,072 original positive-median cells remain, 13/15 families have ≥20; exact same-tip K median changes are small. Avoid treating positive-source exposure as verified TRY measurement duplication.

## What is already known, and the defensible increment

- [Ackerly 2009, PNAS, DOI:10.1073/pnas.0901635106](https://doi.org/10.1073/pnas.0901635106) previously compared seed size, leaf size and height phylogenetic signal and evolutionary rates in multiple clades. Do **not** claim that comparing seed/leaf phylogenetic signal is new.
- [Wang et al. 2023, Frontiers in Plant Science, DOI:10.3389/fpls.2023.1266798](https://doi.org/10.3389/fpls.2023.1266798) showed a substantial contribution of phylogeny to seed-mass variation, with a different variance-partitioning target.
- [Pothasin et al. 2022, Frontiers in Plant Science, DOI:10.3389/fpls.2022.852167](https://doi.org/10.3389/fpls.2022.852167) reported no phylogenetic signal for seed size in a 196-species tropical tree/liana study — consistent with meaningful context dependence.
- The **possible methodological and ecological increment** of the current work is **same-taxon/same-tree cross-organ K contrast + truly whole-family heldout classification + independently frozen source-OU observation-model falsification of a different, named-module feature**, not the bare statement that seed traits can be phylogenetically structured.

## Reviewer-facing hard boundaries and stop rule

**P0: post-outcome module selection.** The six reproductive-versus-six vegetative trait grouping and the module-specific posterior-predictive statistic were formulated after original K and 760 pair outcomes were available. The Brier intervals support *internal resampling performance*, not independent external discovery. The 12 OU exceedances are related post-outcome diagnostics, **not 12 prospective hypothesis tests**.

**P0: true independent replication.** TRY v7 has not provided a qualified, nonoverlapping primary measurement cohort. Newer database labels are not new primary measurements. The [future independent-source module validation protocol](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_reproductive_vegetative_k_external_validation_protocol_v0_1.json) is now fixed before any new data are opened, and is separate from the previously frozen five named-trait replication plan.

**P1: source covariance.** Source-association dispersion is not pure instrument error, and Kew SID itself combines original measurement studies. The tested source-OU model omits realistic cross-trait covariance and correlated source conditions; failure to match the named organ effect does not prove heterogeneous evolutionary OU optima or rates.

**P1: family and phylogeny structure.** A whole-family bootstrap controls repeated within-family comparisons but does not automatically make all plant families independent through deep evolutionary time. The S3 versus native-prune axis and incomplete taxonomy/tip support must be reported.

**P1: estimator discipline.** K is a normalized phylogenetic signal statistic, **not** a direct evolutionary speed, absolute conservatism, selection coefficient or evolutionary half-life. A stronger evolutionary-mechanism paper needs a new source-qualified multivariate comparative model.

**Recommended scientific stop:** Freeze the entire original AusTraits exploratory ecology narrative now. Further use of the same AusTraits trait K outcomes should be only for figure QA, reproducibility, or prespecified stress tests (not unbounded fishing for another favorable biological grouping). The next substantive biological gate is genuinely independent matched-taxon reproductive and vegetative measurement support under the new protocol. **Do not reopen the closed BIEN 201-system rho analysis.**
