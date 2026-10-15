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

## One-sentence manuscript conclusion

**Functional organ category carries limited but measurable cross-family predictive information about phylogenetic trait K, even when species and trees are standardized, while several lineages reverse the trend and tested common evolutionary-plus-observation models fail to predict the specific organ identity ordering.**

The phrase "limited but measurable" is essential: **~65%** out-of-family accuracy is useful but far from deterministic, and these folds share AusTraits primary-source regimes.

## Draft abstract (working, not submission-ready)

Understanding whether the phylogenetic signal of a functional trait generalizes across evolutionary lineages requires separating biological trait identity from the taxonomic and observational context in which signal is estimated. Using a fixed AusTraits plant-morphology dataset, we first reconstructed 760 within-family comparisons of 12 traits on identical species and phylogenies. Across 34 plant families, seed and fruit morphological traits showed higher Blomberg's K than leaf and plant-height traits in 77.1% (S3) and 79.1% (prune-only) of the matched comparisons. This contrast persisted after excluding the Kew-dominated seed dry mass trait. In leave-one-family-out prediction, a single reproductive-versus-vegetative organ contrast predicted the direction of held-out family K differences with 64.5–65.5% accuracy, compared with 52.6–53.8% for a trait-uninformed reference, and performed comparably to a model with separate parameters for all 12 named traits. However, some families displayed the reverse pattern or strong phylogeny-treatment sensitivity. A separately evaluated homogeneous Ornstein–Uhlenbeck process combined with independently source-calibrated observational variation reproduced the overall extent of trait-rank portability but underpredicted the observed reproductive-versus-vegetative ordering on the original species supports. These exploratory findings indicate that the identity of functional organs contains transferable information about phylogenetic signal, but also that taxon sampling, observation provenance and lineage context limit its generalization. Independent primary-measurement replication and covariance-aware evolutionary models are required to identify the underlying biological processes.

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
