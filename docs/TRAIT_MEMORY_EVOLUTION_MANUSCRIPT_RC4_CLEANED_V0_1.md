# Repeatable lineage context and scale-dependent trait portability in plant phylogenetic memory

## Teaser text

Across 45 plant families, the phylogenetic memory of functional traits contains a repeatable lineage-level component after correction of invalid source values. The predictive value of a named trait in unseen families also depends on whether trait values are analysed on their raw or logarithmic scale.

## Abstract

When a trait shows phylogenetic structure in one lineage, can its measured strength predict that trait's structure in another? We quantified phylogenetic distance–dissimilarity gradients in a prospectively qualified matrix of 201 family–trait systems spanning 45 vascular-plant families and 12 continuous traits. A separately frozen data-validity correction removed inadmissible nonpositive source records in five physical traits, retaining all 201 systems. Crossed family repeatability remained 0.149–0.161 across raw/log trait representations and two phylogenetic treatments. A prespecified correlated-trait zero-family-effect null was exceeded on cleaned raw data (p=0.017 S3; p=0.013 prune-only), while measurement-error-aware modelling attributed approximately one quarter of typical variance to finite-species estimation uncertainty. In held-out-family prediction, training-only trait shrinkage improved squared error by 1.21% (S3) and 0.00% (prune-only) for cleaned raw states, versus 5.92% and 5.51% for cleaned log states. These results reveal a modest repeatable lineage context and scale-dependent borrowing of trait information. Phylogenetic memory cannot be summarized by a universal trait-specific gradient without validating its transport across lineages and trait representations.

## Keywords

comparative methods; phylogenetic signal; plant functional traits; predictive generalization; trait evolution; vascular plants

## Introduction

Closely related species often resemble one another, but the strength of that resemblance is not fixed across traits, clades or ecological contexts. Classic comparative work has established strong variation in phylogenetic signal among traits and lineages, and evolutionary rates for the same plant functional trait can differ greatly among clades (Blomberg et al., 2003; Ackerly, 2009; Münkemüller et al., 2012). These patterns motivate a deeper question: **what exactly is generalizable about phylogenetic signal?**

Most analyses treat phylogenetic signal descriptively. A trait is analysed within one clade, or several traits are compared within a phylogeny, and variation in the resulting signal estimates is interpreted biologically. Yet comparative studies increasingly borrow information across lineages: phylogenetic structure is used to inform trait imputation, priors, covariance models and expectations in incompletely sampled clades (Molina-Venegas et al., 2018; Debastiani et al., 2021; Molina-Venegas, 2024; Pearse et al., 2025). Such borrowing implicitly assumes that the evolutionary structure associated with a named trait is transferable.

That assumption is stronger than the statement that a trait can show phylogenetic signal in many clades. A trait could repeatedly show phylogenetic structure while the **amount** of structure varies unpredictably among lineages. If so, “leaf area is phylogenetically conserved” might be broadly true, while an estimate of how strongly leaf area tracks phylogeny in one set of families could still be uninformative for another family.

We therefore framed phylogenetic signal as a generalization problem. We asked two competing questions on the same crossed family × trait design.

Under a **trait-intrinsic hypothesis**, trait identity carries a reusable memory signature. If the phylogenetic memory of trait t is learned from many training families, that estimate should improve prediction of trait t in a family that was completely excluded from training.

Under a **lineage-context hypothesis**, phylogenetic memory depends partly on the lineage in which the trait evolves. If so, family identity should contribute a recurring deviation across different traits even after trait means are controlled.

These hypotheses are not equivalent to asking whether family variance is statistically larger than trait variance. The first is predictive: does trait information transfer across lineages? The second is repeatability-based: does lineage identity recur across traits? Their asymmetry allows a biologically interpretable distinction between a trait-intrinsic memory signature and a lineage-contingent memory architecture.

We tested these hypotheses using 201 prospectively qualified family × trait systems spanning 45 vascular-plant families and 12 continuous traits. All systems were fixed before real memory effects were opened and were required to pass support, semantic, phylogenetic-crosswalk and known-truth geometry-informativeness gates on both a primary S3 tree and a backbone-native prune-only sensitivity tree.

Because the response is estimated from finite species samples, we also explicitly tested three alternative explanations for the observed variance architecture. First, we estimated species-cluster bootstrap standard errors for every system and separated sampling error from between-system heterogeneity. Second, we tested whether apparent family repeatability could arise mechanically from redundant correlated traits measured on the same sparse family × trait graph. Third, we tested whether the weak portability result was merely an artifact of using unshrunk trait means by repeating held-out-family prediction with training-only BLUP shrinkage.

The revised evidence supports a scale-qualified perspective. A family-level component recurs across traits, while prediction of a named trait's gradient in an unseen lineage depends on representation. We report both raw and log outcomes after a strictly rule-based correction of invalid physical measurements, rather than choosing the more favourable scale.

## Materials and Methods

### AI-assisted development disclosure

ChatGPT (OpenAI; ChatGPT product, GPT-5.6 Sol model; accessed 5 October 2026) was used interactively to assist with drafting and debugging R and Python analysis code, editorial revision of manuscript text, and consistency checks across frozen analysis contracts and result summaries. Prompts were conversational natural-language instructions in Japanese and English that typically specified the target file or analysis, the frozen statistical constraints that had to remain unchanged, and the requested code or text transformation; no fixed prompt template or external application programming interface was used. Generated code and text were reviewed against the frozen design and canonical results, executed in continuous integration where applicable, and revised for implementation errors or clarity. The authors verified the analysis code, numerical results, citations and final manuscript claims and take full responsibility for the submitted work.

### Prospectively qualified crossed design

The empirical population comprised 201 family × trait systems spanning 45 vascular-plant families and 12 continuous traits. Every family contributed at least two traits and every trait occurred in at least five families.

The population was fixed before real phylogenetic-memory effects were opened. Systems had to pass prospective gates for data support, trait semantics, phylogenetic crosswalk, and known-truth geometry informativeness on both the primary S3 phylogeny and a backbone-native prune-only sensitivity tree.

No family or trait was subsequently added, removed or reweighted on the basis of its observed memory effect.

### Species-level trait states and phylogenies

Species-level states were medians of valid BIEN 4.2.8 measurements within the original outcome-blind 201-system family×trait graph. The original V.PhyloMaker2 S3 placements and backbone-native prune-only sensitivity were preserved. The raw source audit subsequently found invalid ≤0 records in five physical traits with prespecified positive measurement domains (height, seed mass, leaf area, diameter at breast height and leaf dry mass).

Before inspecting cleaned biological outcomes, Stage B froze a rule to exclude only those raw nonpositive values before species aggregation. Of 201 systems, 49 with invalid source records were recomputed, 152 were inherited unchanged, and every system retained the original minimum tip support. No offset, winsorization, source deletion, trait deletion, or tree re-placement was permitted. For every corrected species state, the natural logarithm was also computed under the frozen all-201 source-support rule. The corrected raw and matched log matrices are both analysed; the uncleaned extraction remains a historical data-quality reference.

### Phylogenetic memory gradient

For every system, we calculated all unordered pairwise patristic distances and all pairwise absolute differences in species trait state.

The phylogenetic memory gradient was

`rho = Spearman(patristic distance, pairwise absolute trait difference)`.

Positive rho means that more phylogenetically distant species tend to differ more strongly in trait state.

This response is a distance-based memory descriptor, not a claim to replace standard phylogenetic-signal metrics such as Blomberg's K or Pagel's lambda (Blomberg et al., 2003; Pagel, 1999). The statistical performance of Mantel-type phylogenetic-signal tests depends strongly on how phylogenetic and phenotypic distances are defined and on measurement error; they are neither uniformly superior nor uniformly inferior to other signal statistics (Harmon & Glor, 2010; Hardy & Pavoine, 2012; Pavoine & Ricotta, 2013). Different signal indices also answer different inferential questions (Münkemüller et al., 2012; Pearse et al., 2025). Here rho was fixed because the study required one common response that could be estimated identically across all family × trait systems and subjected directly to held-out-family prediction.

The estimator was qualified on the exact admitted geometries before real effects were opened. In the robustness programme, sampling uncertainty was estimated at the species level rather than by treating pairwise distances as independent observations.

### Hypothesis 1: trait-intrinsic memory and held-out-family portability

Each family was withheld completely from training and its trait-specific gradients predicted from other families. The original frozen analysis compared unshrunk same-trait means with a global training mean using gain = 1−SSE_trait/SSE_global and a blocked permutation criterion; these original uncleaned results are retained as history, not new inference on corrected data.

A separately frozen training-only BLUP sensitivity modelled family and trait random intercepts and predicted each held-out family from its estimated trait mean with the unseen-family effect set to zero. That same predictor and identical family folds were applied to the cleaned raw and cleaned log gradients. Gains describe predictive squared-error improvement; the contrast between representations was not selected or re-tested to optimize significance.

### Hypothesis 2: repeatable lineage context

We first decomposed raw rho with the crossed random-effects model

`rho ~ 1 + (1 | family) + (1 | trait_name)`.

The original model treated system-level rho values as measured without error. We therefore estimated uncertainty for every rho using a species-cluster nonparametric bootstrap with 199 replicates. Species, rather than species pairs, were the resampling unit. For computational efficiency, bootstrap multiplicities were represented with an exact weighted-midrank formulation verified against fully expanded species bootstrap samples to numerical tolerance 1e-12.

We then fitted a measurement-error-aware crossed meta-analytic model with `metafor::rma.mv`, using bootstrap SE squared as known sampling variance and random intercepts for family, trait and system.

For the primary S3 model, uncertainty in variance-component shares was evaluated by 500 two-way family × trait cluster-bootstrap refits under the frozen resampling contract.

### Correlated-trait zero-family-effect null

Several nominally distinct traits were biologically and empirically correlated. We therefore tested whether family repeatability could arise mechanically from redundant trait outcomes measured on the same sparse graph.

Before opening the null result, we defined three correlated trait blocks:

- whole plant height + maximum whole plant height;
- leaf area + leaf dry mass + leaf area per leaf dry mass;
- leaf nitrogen per mass + leaf nitrogen per area.

Within each block we estimated observed cross-family rho correlations and simulated 1,000 outcome matrices that preserved trait means, trait variances, the predeclared within-block covariance structure, and the exact family × trait incidence graph, but contained no family main effect.

For each simulated matrix we refitted the original unweighted crossed model and recorded R_family.

The null p-value was the fraction of simulated R_family values at least as large as the observed value, with the standard +1 correction.

As a descriptive robustness check, the 12 trait labels were also collapsed into five predeclared biological domains: stature, leaf size/mass, leaf nutrients, seed and wood.

### Additional robustness audits

The earlier geometry and species-coverage adjustments were frozen before the original effects. BIEN source-composition and deep-family phylogeny checks were post-outcome. These historical sensitivities were **not** recomputed on the cleaned primary dataset and are labeled accordingly.

A Stage A source validity audit identified the exact raw nonpositive traits; the distinct frozen Stage B used the same phylogenetic support, species-cluster bootstrap estimators, 500-refit two-way crossed uncertainty contract, correlated-trait null, and training-only BLUP prediction. Cleaned log gradients were fitted only after all 201 systems passed the source-validity and positivity gates. Results on raw and log scales are both retained regardless of their predictive direction.

### Complementary deep-family-phylogeny analysis

After the primary family-context result was known, a complementary exploratory analysis asked whether family context was itself smoothly inherited across deeper family phylogeny.

For each family we summarized its cross-trait deviation from trait means and tested whether pairwise differences in family context increased with patristic distance among family crowns.

Because this analysis was designed after primary outcomes were opened, it is not treated as a confirmatory hypothesis test.

## Results

### Phylogenetic memory was common but heterogeneous

Before cleaning, the prospectively qualified 201-system rho matrix had an S3 mean 0.093, median 0.053, with approximately 75% of gradients positive. Those summary values describe the historical uncleaned state and are not silently relabelled as cleaned means.

After removing source-invalid raw measurements, **201/201** systems remained qualified. Spearman concordance of original and cleaned rho was 0.9910 S3 and 0.9936 prune-only. Respectively 17 and 15 systems changed by absolute rho≥0.01; 2 and 3 changed sign. The maximum absolute changes were 0.0850 and 0.1438. Most estimates were numerically close, but the corrected inputs are mandatory because the source measurement domain was violated.

### Sampling error explains a substantial part of the original residual

The original uncorrected crossed model attributed 15.0% of estimated variability to family, 4.3% to trait and 80.6% to an unresolved residual. This residual also contained measurement uncertainty.

With corrected raw states, S3 and prune-only unweighted family repeatability were 0.1564 and 0.1541. The corresponding corrected log values were 0.1489 and 0.1615.

Using species-bootstrap sampling variances in the corrected measurement-aware model, the typical S3 total variance **point** shares were family 16.22%, trait 6.38%, unresolved system 54.22%, and finite-species sampling 23.18% on the raw scale. On the log scale they were 12.46%, 8.96%, 55.13%, and 23.45%. The 500-refit two-way cluster bootstrap passed its execution gate but yielded broadly overlapping component-share intervals; it does not establish variance dominance.

### Family context persisted beyond correlated-trait and design artifacts

The predeclared zero-family-effect null preserved selected correlations among redundant traits, their marginal means and variances, and the exact sparse incidence graph. After source-validity cleaning, observed raw crossed family repeatability exceeded this null on S3 (p=0.0170) and prune-only (p=0.0130). This supports a repeatable family-level component under that specified null.

Pre-cleaning geometry, species count and BIEN provenance audits also retained nonzero family estimates, but were not re-run on cleaned states. They therefore remain historical supporting analyses, not proof that the corrected-data family component is causal or immune to all data-source confounding.

### Trait identity carried little robust information into an unseen family

On cleaned raw states, training-only trait BLUPs gave held-out-family SSE gains of 1.21% (S3) and 0.00% (prune-only). Unshrunk trait-mean prediction instead gave -1.63% and -2.63%. Shrinkage removed most of the raw-scale penalty from noisy trait averages.

For the matched cleaned log representation, the same BLUP protocol yielded positive gains of 5.92% and 5.51%. These are predictive point estimates, not a newly calibrated raw–log difference p-value. Trait identity has **scale-dependent modest portability**, not a universally zero or biologically negative transferable signal.

### Positive-only source correction enables matched raw and log analyses

The initial log sensitivity was blocked by nonpositive source medians in 25 S3 and 18 prune-only systems. Stage A established invalid physical measurement coding, and Stage B removed those records according to a separately fixed source-validity rule. All 201 systems then retained sufficient tips and strictly positive species states for the original raw and matched log-scale gradients.

Log-scale family repeatability remained nonzero while trait-level prediction showed larger positive gains than on the raw scale. No system was dropped, no offset introduced, and neither representation was selected after seeing the results.

### Family context was not detectably organized along deeper family phylogeny

In the complementary post-outcome analysis, pairwise differences in family context showed essentially no association with patristic distance among family crowns.

S3 Spearman rho was -0.015 (permutation p = 0.822), and prune-only rho was -0.011 (p = 0.871).

Alternative mean-based and leave-one-trait variants were similarly close to zero.

This exploratory result suggests that the recurring family component behaves more like a family-specific mosaic than a smooth deep-phylogenetic gradient.

## Discussion

### Phylogenetic memory is not a stable trait-intrinsic signature

A named trait cannot be assigned a universal transferable rho gradient from this evidence. After correction, a family-associated component recurs across traits, while trait-specific prediction is nearly neutral on raw states and modestly positive on log states. Neither an intrinsic fixed trait parameter nor total trait nonportability is supported. The appropriate unit of generalization is trait-in-lineage **and trait representation**.

### The family component is modest but difficult to dismiss as a simple artifact

The family point component remained approximately 15% across cleaned raw and log states and exceeded the predeclared correlated-trait zero-family null on cleaned raw effects. Species-level uncertainty contributed materially to observed gradient variation.

Historical geometry and source-concentration sensitivities were computed on the earlier uncleaned matrix and were not repeated on the corrected primary sample. We interpret the result as lineage-associated repeatability, not proof of developmental constraints, selection, life-history drivers, or a family-specific evolutionary-rate parameter.

### Sampling uncertainty changes the meaning of “system specificity”

The original unweighted mixed model assigned more than 80% of variance to the residual.

Without measurement-error correction, that number could be read as evidence that phylogenetic memory is overwhelmingly idiosyncratic to each family × trait combination.

The species-bootstrap analysis rejects that interpretation.

Roughly one quarter of typical total variation is attributable to finite-species estimation error. Residual between-system heterogeneity remains substantial, but its magnitude is too uncertain to call dominant over the family component under the predeclared cluster bootstrap.

The relevant biological conclusion is therefore not that “most memory is system-specific.” It is that a large fraction remains unexplained after accounting for repeatable family and trait structure, while a material fraction of the apparent cell-level spread is estimation noise.

### Weak portability reflects little signal to borrow, not anti-portability

BLUP shrinkage reduced the raw-scale penalty of predicting from unshrunk trait means. After cleaning, raw-scale trait prediction improved little (1.21% S3; 0.00% prune), whereas corresponding log gains were 5.92% and 5.51%. Trait identity therefore carries a **weak-to-modest, representation-dependent prior**, not reliably zero or uniformly large information.

### The scale of lineage context appears local rather than deeply hierarchical

The original complementary family-crown phylogeny audit found little deep-distance organization of family context. It was post-outcome and used pre-cleaning effects, so the corrected study does not establish a stable deep-family phylogenetic pattern. The mosaic interpretation remains exploratory.

### Relation to standard phylogenetic-signal metrics

The present memory gradient is intentionally a common distance-decay descriptor, not a general phylogenetic-signal estimator.

Blomberg's K, Pagel's lambda and model-based evolutionary parameters answer related but distinct questions (Blomberg et al., 2003; Pagel, 1999; Pearse et al., 2025).

Mantel-type approaches are sensitive to the chosen distance metrics and measurement error, and their performance relative to K-type statistics can reverse across conditions (Harmon & Glor, 2010; Hardy & Pavoine, 2012; Pavoine & Ricotta, 2013). We therefore do not interpret rho as a universally optimal index or infer mechanism from its absolute value.

The inferential target here is narrower: whether the same predefined distance-decay summary can be predicted across lineages.

Prospective known-truth qualification and species-level bootstrap uncertainty are central to that interpretation.

A future independent replication using K, lambda or model-based parameters would test whether the **portability asymmetry itself** generalizes across definitions of phylogenetic signal.

### Implications for comparative evolution

Cross-lineage phylogenetic priors should explicitly state which trait representation and which signal estimator they transfer. The same trait can carry a modest reusable gradient on a log scale without defining a single universal gradient across families.

Independent AusTraits results based on Blomberg's K and the present rho gradient need not exhibit identical trait-rank portability. Therefore differences in trait-signal transfer are **estimand- and scale-dependent**; our analysis does not establish an adaptive evolutionary mechanism or a causal connection to community diversity and biomass.

## Limitations

The studied Spearman association of patristic distance and pairwise trait-state difference is a distance-gradient descriptor, not an evolutionary rate, OU half-life, Blomberg K or Pagel lambda. Raw and log trait states represent different dissimilarities, and the positive cleaned-log prediction gains are descriptive rather than newly calibrated permutation-significant effects.

Stage B's measurement validity rule was frozen before cleaned outcomes but followed a post-result raw-data audit; the chronology is explicit. Uncertainty intervals on crossed heterogeneity shares are broad; family context remains mechanistically unidentified. The deep-family and provenance checks were not re-run on the corrected matrix. This study provides no causal K→FD→biomass evidence and does not generalize to the closed spatial/interaction source programme.

**Submission HOLD:** The corrected Stage B scientific summary was recovered from successful October 2026 Actions logs and committed permanently. The original 201-row cleaned-effects/SE tables and graphics were in finite-retention Actions artifacts and must be source-reconstructed and independently verified before a submission-grade Word/PDF package is rebuilt. The present RC4 Markdown is not a completed submission.

## Conclusion

In 201 comparisons spanning 45 vascular-plant families and 12 continuous traits, phylogenetic memory gradients contain a modest family-associated repeatable component after correcting invalid physical measurements. Trait identity additionally contains scale-dependent predictive information: close to zero on raw states and modestly positive on log states.

These results favour **repeatable lineage context with scale-qualified trait portability** over either a universal trait-specific memory signature or a categorical absence of transferable trait information.

## RC4 evidence and figure status

This is a complete scientific manuscript draft but not a submission-ready replacement of the earlier anonymous RC3 DOCX or figures. Before using it for submission, recover or regenerate the exact cleaned 201-system source-effect/SE tables, reproduce the source-verified aggregate in [Stage B run #37443037590](https://github.com/zuizui0223/turnover/actions/runs/37443037590), rebuild Figures 1–3 and verify that all panels and text use the **same corrected dataset and named scale**. Preserve the blocked earlier RC3 in PR #29 without submitting it. No new analytic estimand, scale optimization or threshold relaxation is permitted.

## References

Ackerly, D. D. (2009). Conservatism and diversification of plant functional traits: Evolutionary rates versus phylogenetic signal. *Proceedings of the National Academy of Sciences of the United States of America, 106*(Suppl. 2), 19699–19706. https://doi.org/10.1073/pnas.0901635106

Blomberg, S. P., Garland, T., Jr., & Ives, A. R. (2003). Testing for phylogenetic signal in comparative data: Behavioral traits are more labile. *Evolution, 57*, 717–745. https://doi.org/10.1111/j.0014-3820.2003.tb00285.x

Debastiani, V. J., Bastazini, V. A. G., & Pillar, V. D. (2021). Using phylogenetic information to impute missing functional trait values in ecological databases. *Ecological Informatics, 63*, 101315. https://doi.org/10.1016/j.ecoinf.2021.101315

Enquist, B. J., Boyle, B., Maitner, B. S., et al. (2026). BIEN: A biodiversity informatics ecosystem advancing open and reproducible workflows for plant observation, plot and trait data. *Methods in Ecology and Evolution, 17*, 1556–1584. https://doi.org/10.1111/2041-210X.70274

Hardy, O. J., & Pavoine, S. (2012). Assessing phylogenetic signal with measurement error: A comparison of Mantel tests, Blomberg et al.'s K, and phylogenetic distograms. *Evolution, 66*, 2614–2621. https://doi.org/10.1111/j.1558-5646.2012.01623.x

Harmon, L. J., & Glor, R. E. (2010). Poor statistical performance of the Mantel test in phylogenetic comparative analyses. *Evolution, 64*, 2173–2178. https://doi.org/10.1111/j.1558-5646.2010.00973.x

Jin, Y., & Qian, H. (2022). V.PhyloMaker2: An updated and enlarged R package that can generate very large phylogenies for vascular plants. *Plant Diversity, 44*, 335–339. https://doi.org/10.1016/j.pld.2022.05.005

Molina-Venegas, R., Moreno-Saiz, J. C., Castro Parga, I., Davies, T. J., Peres-Neto, P. R., & Rodríguez, M. Á. (2018). Assessing among-lineage variability in phylogenetic imputation of functional trait datasets. *Ecography, 41*, 1740–1749. https://doi.org/10.1111/ecog.03480

Molina-Venegas, R. (2024). How to get the most out of phylogenetic imputation without abusing it. *Methods in Ecology and Evolution, 15*, 456–463. https://doi.org/10.1111/2041-210X.14198

Münkemüller, T., Lavergne, S., Bzeznik, B., Dray, S., Jombart, T., Schiffers, K., & Thuiller, W. (2012). How to measure and test phylogenetic signal. *Methods in Ecology and Evolution, 3*, 743–756. https://doi.org/10.1111/j.2041-210X.2012.00196.x

Pagel, M. (1999). Inferring the historical patterns of biological evolution. *Nature, 401*, 877–884. https://doi.org/10.1038/44766

Pavoine, S., & Ricotta, C. (2013). Testing for phylogenetic signal in biological traits: The ubiquity of cross-product statistics. *Evolution, 67*, 828–840. https://doi.org/10.1111/j.1558-5646.2012.01823.x

Pearse, W. D., Davies, T. J., & Wolkovich, E. M. (2025). How to define, use, and interpret Pagel's lambda in ecology and evolution. *Global Ecology and Biogeography, 34*, e70012. https://doi.org/10.1111/geb.70012
