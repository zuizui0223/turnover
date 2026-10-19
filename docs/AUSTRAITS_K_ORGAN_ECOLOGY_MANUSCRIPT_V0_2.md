# Organ function predicts phylogenetic signal across plant families, but taxon ascertainment governs its apparent strength

**Manuscript draft v0.2 — 19 October 2026**  
**Status:** Reporting-only synthesis of completed AusTraits analyses. The functional-organ grouping was selected *after* initial K outcomes; this is an exploratory comparative paper, **not an independent confirmatory experiment**. The results below are not a new analysis of the locked 201-system BIEN `rho` study.

## Abstract

Phylogenetic signal is frequently compared among plant functional traits, yet it remains unclear how much of a trait's apparent evolutionary conservatism can be predicted from the functional organ it describes, and how much depends on the taxa and measurements available for comparison. We examined twelve continuous reproductive (fruit and seed) and vegetative (leaf, petiole, and height) traits from the AusTraits compilation, using matched sets of species and phylogenetic trees within plant families. In a post-discovery functional-organ comparison, reproductive traits had greater Blomberg's K than vegetative traits in 313 of 406 (77.1%) comparisons across 34 families on one phylogenetic treatment and 314 of 397 (79.1%) on a native-tip sensitivity tree. An organ-only predictor trained on other families improved whole-family-held-out sign prediction to 64.5–65.5%, from pooled baselines of 52.6–53.8%. The broad reproductive advantage persisted after excluding five dominant electronic floras (78.1% and 77.3%) and under a more restrictive shared-source subset (84.5% and 80.2%). However, a fixed-identity decomposition revealed a large influence of which species remained measurable: the apparent reproductive advantage among 142 identical family-by-trait-pair comparisons rose from 110 to 121 pairs when taxon support was restricted, but was 120 when only shared-source measurements were used on those same tips. These results identify an ecologically interpretable, partly transferable hierarchy of *estimated* phylogenetic signal, alongside substantial lineage and observation-source contingency. They do not establish differential evolutionary rates, selection, developmental constraints, or independent-source generality.

## 1. Introduction

Understanding why closely related plant species resemble one another is a central goal of comparative evolutionary ecology. The strength of resemblance depends on evolutionary processes, the phylogenetic tree, the species sampled and the trait measurements used. A statement that one trait has “more phylogenetic signal” than another is therefore incomplete without defining a common comparison population. Blomberg's K is a covariance-based measure normalized relative to a Brownian-motion reference; it should not be interpreted as the rate of evolution, an Ornstein–Uhlenbeck attraction parameter, or direct evidence for functional constraint.

Functional organs provide one candidate level of biological prediction. Reproductive diaspores and fruits participate in dispersal and regeneration, whereas leaves, petioles and whole-plant height participate in resource acquisition and growth. Reproductive and vegetative morphologies may differ in how developmental architecture, allocation and ecology jointly shape covariation across descendants. Yet these plausible mechanisms alone do not predict the direction of K differences without comparative evidence, because both modules contain heterogeneous traits and may be measured in dissimilar taxonomic contexts. Prior studies have compared seed, leaf and height evolutionary attributes (e.g., Ackerly 2009), so a simple observation of trait-specific or organ-specific signal would not be a novel claim by itself.

A stronger, testable question is whether a coarse **organ-function category** can predict the *relative K ranking* of traits within a plant family that was withheld from model training. The comparison must hold the species and tree fixed within each organ pair, and assess whether the resulting predictive regularity survives plausible data-source perturbations. Even if it does, a predictive hierarchy need not imply that reproductive traits evolve more slowly: the same apparent signal can change when the population of sampled species or source measurements changes.

We address three distinct questions using an existing compilation: (1) Is there a descriptive reproductive–vegetative K tendency on common tips? (2) Does knowledge of the organ category predict a withheld family beyond a pooled sign prior? (3) How does the observed tendency respond to changing available taxa versus changing contributing source measurements? A process-model diagnostic provides a bounded additional interpretation. The organ-category hypothesis and some follow-up source controls were formulated **after** viewing original AusTraits K results; accordingly, all biological conclusions are explicitly exploratory. True external confirmation is reserved for an independently collected, prospectively qualified source, which has not yet been obtained.

## 2. Materials and methods

### 2.1 Trait classes and comparison unit

We used AusTraits v7.0.0 family-by-trait systems from the previously qualified K graph. The twelve source-calibratable traits were grouped into six reproductive dimensions (`fruit_height`, `fruit_length`, `fruit_width`, `seed_dry_mass`, `seed_length`, `seed_width`) and six vegetative traits (`leaf_area`, `leaf_length`, `leaf_mass_per_area`, `leaf_width`, `petiole_length`, `plant_height`). This grouping was defined **after initial empirical K rankings were inspected** and is not misrepresented as prospectively selected.

For a family-by-named-trait-pair with at least 20 common species, both trait values were evaluated on exactly the **same species** and reconstructed native phylogeny, with identical retained tips for the two organs. This comparison controls differential tip sampling *within that pair*, but not differences among pairs in the families or species they represent. The full source-qualified matched-tip comparison included 760 family-by-pair observations on the V.PhyloMaker2 S3 tree and 747 on the native-tip prune tree, spanning 42 families. The focal reproductive-versus-vegetative portion included 406 S3 comparisons across 34 families and 397 prune comparisons across the same number of families. Repeated trait pairs within one family are dependent observations, not separate evolutionary origins.

The primary descriptive response for each reproductive–vegetative pair was the sign of `K_reproductive – K_vegetative`. Absolute K magnitudes and relative rankings are not equated with selection coefficients or evolutionary rate.

### 2.2 Predicting a previously unseen plant family

For each held-out family, the prediction model learned only from family-by-trait-pair signs in **other families in the same AusTraits compilation**. The organ-only classifier used a single signed reproductive-versus-vegetative contrast, with no intercept and the previously fixed ridge penalty; pooled sign, separately estimated twelve named-trait scores, and same-named-pair priors provided comparison predictors. Scoring includes all 760/747 supported pair comparisons; within-organ comparisons have an organ contrast of zero and are scored as ties rather than artificially assigned to the reproductive class.

We report hard-sign accuracy and the Brier probability loss; family-cluster bootstrap intervals characterize the improvement relative to the pooled sign prior. Leaving a family out does **not** leave out original publications or shared source measurement protocols, so this is cross-family prediction **within one compilation**, not truly independent original-source replication.

### 2.3 Separating source and taxon-ascertainment sensitivity

Three completed, outcome-labelled exploratory robustness analyses addressed different levels of sample construction:

1. After excluding five large electronic flora contributors, we compared traits on common species/trees with medians from the remaining original AusTraits contributing datasets.
2. We selected pairs with at least 20 species for which both organs had source records from an identical remaining non-flora AusTraits DatasetID. This source identity is not proof of the same directly measured physical specimen.
3. On the **same 142 S3 (101 prune) selected family-by-trait-pair identities**, we compared (A) original broader non-flora species/tip supports and all remaining measurements, (B) the more restrictive common-DatasetID species/tip supports but all remaining measurements, and (C) those exact narrower species/tips/trees using only the shared-source measurements.

A versus B changes the sampled species, the reconstructed native tree geometry and K normalization together. B versus C holds taxa/tree fixed and changes only the contributing values. Descriptive sign-transition counts were reconstructed algebraically from already archived totals and flip counts, not from additional trait outcome searches. For family-level uncertainty, the source analyses used 5,000 whole-family bootstrap draws rather than treating overlapping pair rows as independent.

### 2.4 Evolutionary-process model adequacy is a separate estimand

A previously fitted homogeneous OU model with source-calibrated observational heterogeneity reproduced the *predeclared scalar magnitude of rank portability*, so the original null classification remains `RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES`. A later, **post-discovery** posterior-predictive check asked whether tested members of that model family reproduce the *particular reproductive-versus-vegetative direction*. It was evaluated only on the **original, nonmatched family-by-trait systems** (410 cross-organ comparisons) to match the geometry of the original simulations. It is **not a calibrated null for the 406/397 matched-tip organ comparisons**, nor a preregistered p-value for a hypothesis selected from those outcomes.

## 3. Results

### 3.1 A consistent but not universal organ-level K pattern

Reproductive morphology showed greater K in **313/406 (77.09%) S3** and **314/397 (79.09%) prune** common-tip cross-organ comparisons among 34 families. Family-equal mean reproductive-higher proportions were **74.7% S3** (95% whole-family bootstrap CI **64.3–84.4%**) and **75.8% prune** (67.4–84.1%). The descriptive trend was not explained solely by the source-dense seed-dry-mass trait: after excluding its comparisons, reproductive K remained higher in **263/344 (76.5%)** and **268/337 (79.5%)** comparisons, respectively. For fruit traits alone versus vegetative traits, the rates were **149/193 (77.2%)** and **150/189 (79.4%)**.

Nevertheless, individual family-by-trait comparisons diverged. In the original matched comparison, Fabaceae favored reproductive K in **35/36 S3** pairs, whereas Casuarinaceae did so in **2/12**. These are descriptive contrasts, not independently established family mechanisms: family-specific anatomical homology, differing study sources and sparse pair support can all alter which physical organ is measured.

### 3.2 Functional category predicts K ordering in families withheld from model training

The organ-only model achieved **64.47% S3** and **65.46% prune** sign accuracy over all eligible pair types, compared with **52.63%** and **53.82%** from the pooled other-family predictor. Its Brier loss decreased from **0.25062 to 0.21378** on S3 and from **0.25017 to 0.20671** on prune; the family-bootstrap 95% intervals for improvement were **+0.00433 to +0.06388** and **+0.01946 to +0.06338**. A more flexible named-trait predictor yielded Brier losses **0.21792 S3** and **0.21156 prune**, without establishing a statistically reliable head-to-head advantage over the one-coefficient organ model.

Thus a simple functional-organ prior has some predictive use across families within the compiled data, but is far from a deterministic rule, and cannot establish transport to genuinely new primary data sources. The **~65%** all-pair heldout accuracy and the **~77–79%** descriptive cross-organ win fraction have different denominators and must not be interchanged.

### 3.3 The tendency survives major source restrictions

When five dominant electronic floras were excluded, reproductive K remained higher in **221/283 (78.1%) S3** comparisons across 29 families and **180/233 (77.3%) prune** comparisons across 25 families. Under the more stringent common remaining non-flora DatasetID rule, the result was **120/142 (84.5%) S3** across 24 families and **81/101 (80.2%) prune** across 18 families. The strict cohort's equal-family rates were **82.2%** (95% family-bootstrap 71.1–91.4%) and **69.9%** (53.1–85.0%). These are internal sensitivity results using the same original AusTraits source universe, not independent empirical replications.

### 3.4 Taxon selection changes apparent organ superiority more than value substitution in the S3 comparison

Comparing the **same exact 142 S3 pair identities**, reproductive-higher cases changed from **110/142** on broad non-flora tips to **121/142** on the common-source-qualified narrower tips. There were **23 sign reversals**: algebraically, **17** went from vegetative-higher to reproductive-higher and **6** went in the opposite direction. Switching to only shared-source observations while holding these narrower tips/trees constant changed **121/142 to 120/142**, with **9 reversals** (**4** vegetative→reproductive; **5** reproductive→vegetative).

The prune-only counterpart used the same **101 pair identities** within that tree treatment: **82→83→81** reproductive-higher cases. The first transition comprised **7** vegetative→reproductive and **6** reproductive→vegetative changes (13 reversals); the second comprised **5** and **7**, respectively (12 reversals). The median absolute shifts in the within-pair log-K contrast were **0.1964 then 0.0758** on S3 and **0.2513 then 0.0948** on prune.

These exact sign flows resolve an important ambiguity: the seemingly stronger **84.5%** S3 advantage in the strict subset arises substantially when the available **species and tips** change, not when identical tips are given source-restricted numerical medians. The conclusion differs in strength by tree treatment, and the first transition also changes tree pruning and K scaling. We therefore do **not** interpret those shifts causally as evolutionary responses to source choice.

### 3.5 A posterior predictive discrepancy does not identify the evolutionary mechanism

On the separate original unequal-tip systems, reproductive K was higher in **302/410 (73.7%) S3** and **330/410 (80.5%) prune** comparisons. Tested homogeneous OU-plus-source-observation models underpredicted this particular post-selected organ direction across their specified cases, even though they matched the different predeclared scalar rank-portability statistic. The apparent mismatch is therefore **a descriptive model-adequacy signal for a post-selected feature**, not a preregistered rejection of homogeneous evolution, nor evidence that organ-specific OU attraction rates or stabilizing selection have been identified.

## 4. Discussion

### 4.1 Functional categories can act as fallible predictive priors

The central ecological contribution is not that phylogenetic signal differs among plant traits—already recognized in evolutionary comparative work—but that **organ function is useful for predicting the relative phylogenetic K ranking of two traits within a completely withheld plant family**, even after their own species and tree are standardized. This supports a weak, functional-module-level statistical prior rather than a universal organ law. Evolutionary inferences made with an assumed K hierarchy should incorporate uncertainty about lineage and source context; a reproductive versus vegetative label cannot substitute for examining the actual measured system.

### 4.2 Sampling determines what looks conserved

The paired three-stage analysis reveals that a more stringent source requirement can simultaneously improve citation consistency and change which species remain available. That latter change can alter the direction of comparative phylogenetic K more than switching the source measurements on otherwise identical species/trees. This is substantive for comparative biology: choosing a “better controlled” subset can accidentally strengthen the appearance of an evolutionary hierarchy if the improved source qualification selects a different slice of the lineage's phenotypic diversity.

The effect cannot automatically be corrected by subtracting “source noise”, because the selection stage changes the underlying tree-tip graph, not merely independent measurement precision. Observational studies should therefore report source qualification *and* within-identity taxon-support transitions, ideally with primary specimen-level measures.

### 4.3 What mechanisms remain plausible?

Organ developmental integration, allocation, trait covariance, variation in selection and evolutionary history are possible explanations for the reproductive K pattern. However, they cannot be identified from K sign alone. Source-specific taxon composition, unequal original measurement precision, leaf-versus-leaflet ambiguity and structures such as nutlets, samaras or infructescences also remain viable explanations. The tested homogeneous OU-plus-source model underpredicted the *particular selected direction* on original unmatched tips, but realistic cross-trait covariance and source-specific sampling dependencies were not completely represented. No claim of stronger stabilizing selection, canalization or a slower rate of reproductive evolution is warranted.

### 4.4 Scope and next evidence

This result applies to the qualified continuous morphology and source composition of AusTraits; it is not a global representative survey of every vascular-plant family. The organ grouping and sensitivity studies are post-outcome, source regimes overlap across held-out families and the two phylogenetic treatments share parts of the underlying tree information. Independent evidence requires primary individual- or specimen-level measurements of both organs on matched species, harmonized organ homology, original-reference disjointness from AusTraits and supported phylogenies across at least twelve independent families. Source qualification for those criteria has **not passed**. This manuscript should therefore be presented and reviewed as a carefully controlled exploratory discovery with specific prospective predictions, not as completed independent ecological confirmation.

## 5. Reporting, availability, and inference boundary

The original analyses, null studies, source restrictions, final S3/prune results and figure pipelines are available in [turnover](https://github.com/zuizui0223/turnover), especially [PR #33](https://github.com/zuizui0223/turnover/pull/33). The numerical claims and exact transitions above are pinned in `data/austraits_organ_paper_claim_registry_v0_2.json` and checked by `scripts/qa/validate_austraits_organ_paper_claims_v0_2.py`. Source run IDs and no-new-outcome boundaries appear there. This report adds **no newly discovered subgroup, no new fitted effect, and no new biological significance test**.

### Figure assignments

- **Figure 1: Organ K direction on common tips.** Source original 760-pair figure; distinguish whole-family averages from overlapping pairs, seed and fruit subtype denominators, and the 34 families.
- **Figure 2: Predictive transfer is limited, not absent.** LOFO Brier loss, absolute improvement with whole-family confidence intervals, paired S3 and prune axis, pooled vs organ-only vs named-trait.
- **Figure 3: A tighter source gate changes the taxa.** Original 142/101 exact pair identities: S3 110→121→120 and prune 82→83→81. Annotate paired sign flows 17/6 and 4/5 on S3, 7/6 and 5/7 on prune. Show **taxon/tip change** versus **measurement-source change** as distinct transitions.
- **Supplementary Figure S1: Source provenance and limits.** Five-flora exclusions, non-flora DatasetID restrictions, 24/18-family strict support and Kew SID warning.
- **Supplementary Figure S2: Original-tip OU model check.** Never reuse original unequal-tip simulations as the null distribution for matched-tip observations; label exploratory, post-discovery.

### Selected prior references

- Ackerly, D. D. (2009). Conservatism and diversification of plant functional traits: evolutionary rates versus phylogenetic signal. *Proceedings of the National Academy of Sciences*. https://doi.org/10.1073/pnas.0901635106
- Wang et al. (2023). Seed mass phylogenetic/functional analysis, distinct from the organ-level held-out-family estimand. https://doi.org/10.3389/fpls.2023.1266798
- Pothasin et al. (2022). Tropical tree/liana seed-size comparative case with a different signal result. https://doi.org/10.3389/fpls.2022.852167

**Editorial note:** Verify complete bibliographic metadata, journal format, author affiliations and data/source licences before submission. None are inferred or manufactured here.
