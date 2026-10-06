# Phylogenetic trait memory is lineage-contingent, with little transferable trait-level signal across plant families

## Teaser text

The same plant trait can show phylogenetic structure in many lineages without carrying a stable amount of that structure across them. Across 45 families, lineage context repeated across traits, whereas trait identity gave almost no predictive gain for a family withheld from training.

## Abstract

Phylogenetic signal is often discussed as a property of traits, yet the same trait can evolve differently among clades. We asked whether the strength of phylogenetic trait memory is itself transferable across lineages. Using a prospectively qualified crossed dataset of 201 family × trait systems spanning 45 vascular-plant families and 12 continuous traits, we contrasted a trait-intrinsic hypothesis, under which the same trait should predict memory strength in an unseen family, with a lineage-context hypothesis, under which family identity should recur across different traits. Shrinkage-aware leave-one-family-out prediction produced essentially no gain over a global training mean (0.006 on the primary tree and −0.0048 on the backbone-only sensitivity tree). In contrast, a family component near 0.15 persisted after species-level sampling-error correction, geometry adjustment, trait-domain collapse, and a predeclared correlated-trait null (p = 0.017 and 0.009). Species-cluster bootstrap uncertainty showed that about one quarter of typical total variation was finite-species estimation error. Thus, phylogenetic trait memory is lineage-contingent, with little transferable trait-level signal across families; cross-lineage borrowing of trait-specific evolutionary structure should therefore be validated directly.

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

Our results support a scale-asymmetric view of evolutionary memory. Family context repeats modestly across traits, but trait identity carries little robust information that transfers to an unseen family. A complementary post-outcome analysis further suggests that this family context is not smoothly arranged along deeper family phylogeny. Phylogenetic memory therefore behaves less like a fixed property of a named trait and more like a property of a trait embedded in lineage context.

## Materials and Methods

### AI-assisted development disclosure

ChatGPT (OpenAI; ChatGPT product, GPT-5.6 Sol model; accessed 5 October 2026) was used interactively to assist with drafting and debugging R and Python analysis code, editorial revision of manuscript text, and consistency checks across frozen analysis contracts and result summaries. Prompts were conversational natural-language instructions in Japanese and English that typically specified the target file or analysis, the frozen statistical constraints that had to remain unchanged, and the requested code or text transformation; no fixed prompt template or external application programming interface was used. Generated code and text were reviewed against the frozen design and canonical results, executed in continuous integration where applicable, and revised for implementation errors or clarity. The authors verified the analysis code, numerical results, citations and final manuscript claims and take full responsibility for the submitted work.

### Prospectively qualified crossed design

The empirical population comprised 201 family × trait systems spanning 45 vascular-plant families and 12 continuous traits. Every family contributed at least two traits and every trait occurred in at least five families.

The population was fixed before real phylogenetic-memory effects were opened. Systems had to pass prospective gates for data support, trait semantics, phylogenetic crosswalk, and known-truth geometry informativeness on both the primary S3 phylogeny and a backbone-native prune-only sensitivity tree.

No family or trait was subsequently added, removed or reweighted on the basis of its observed memory effect.

### Species-level trait states and phylogenies

For each family × trait system, species-level trait state was the median valid trait value for that species under the frozen Botanical Information and Ecology Network extraction contract (Enquist et al., 2026).

The primary phylogeny used the S3 placement from V.PhyloMaker2 (Jin & Qian, 2022). A mandatory sensitivity retained only backbone-native prune-only tips.

The complete 201-system raw effect matrix was independently re-extracted during the robustness programme and reproduced the archived effects for all systems at the archived four-decimal precision.

### Phylogenetic memory gradient

For every system, we calculated all unordered pairwise patristic distances and all pairwise absolute differences in species trait state.

The phylogenetic memory gradient was

`rho = Spearman(patristic distance, pairwise absolute trait difference)`.

Positive rho means that more phylogenetically distant species tend to differ more strongly in trait state.

This response is a distance-based memory descriptor, not a claim to replace standard phylogenetic-signal metrics such as Blomberg's K or Pagel's lambda (Blomberg et al., 2003; Pagel, 1999). The statistical performance of Mantel-type phylogenetic-signal tests depends strongly on how phylogenetic and phenotypic distances are defined and on measurement error; they are neither uniformly superior nor uniformly inferior to other signal statistics (Harmon & Glor, 2010; Hardy & Pavoine, 2012; Pavoine & Ricotta, 2013). Different signal indices also answer different inferential questions (Münkemüller et al., 2012; Pearse et al., 2025). Here rho was fixed because the study required one common response that could be estimated identically across all family × trait systems and subjected directly to held-out-family prediction.

The estimator was qualified on the exact admitted geometries before real effects were opened. In the robustness programme, sampling uncertainty was estimated at the species level rather than by treating pairwise distances as independent observations.

### Hypothesis 1: trait-intrinsic memory and held-out-family portability

To test whether trait identity carries transferable information, we left each family out completely.

For each family × trait system in the held-out family, the original predictor was the mean rho for the same trait estimated from all training families. The baseline predictor was the global mean rho across all training systems.

Prediction performance was summarized as

`gain = 1 - SSE_trait / SSE_global`.

Positive gain indicates that trait identity improves prediction beyond the global training mean.

The frozen primary portability analysis used 999 within-family label permutations and required positive gain with one-sided permutation p <= 0.05 on both S3 and prune-only trees.

Because unshrunk trait means can amplify noise when between-trait variance is small, a prospectively frozen robustness sensitivity repeated held-out-family prediction with training-only shrinkage. Within each training fold we fitted

`rho ~ 1 + (1 | trait_name) + (1 | family)`

and predicted the held-out family using the fixed intercept plus the training-only trait BLUP, with the unseen-family random effect set to zero.

No additional portability predictor was tested after these outcomes were opened.

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

We examined several outcome-independent or independently frozen alternatives that could masquerade as family context.

A geometry adjustment included log species count, backbone-native prune fraction and known-truth calibration lambda.

A separate post-outcome provenance audit quantified BIEN source and source-citation concentration.

The family component was also examined under leave-one-trait and leave-one-family refits.

A mandatory natural-log trait-scale sensitivity was prospectively frozen, with no offset or signed-log rescue. It required all 201 systems to be valid on the transformed scale.

### Complementary deep-family-phylogeny analysis

After the primary family-context result was known, a complementary exploratory analysis asked whether family context was itself smoothly inherited across deeper family phylogeny.

For each family we summarized its cross-trait deviation from trait means and tested whether pairwise differences in family context increased with patristic distance among family crowns.

Because this analysis was designed after primary outcomes were opened, it is not treated as a confirmatory hypothesis test.

## Results

### Phylogenetic memory was common but heterogeneous

Across the 201 systems, S3 rho averaged 0.093 with median 0.053 and was positive in approximately 75% of systems.

Prune-only effects were strongly concordant with S3 effects (Spearman rho = 0.832), indicating that the broad pattern did not depend strongly on S3 bind placements.

The robustness extraction reproduced all 201 archived raw effects at the archived four-decimal precision.

### Sampling error explains a substantial part of the original residual

The original crossed model assigned 15.0% of variance to family, 4.3% to trait and 80.6% to the residual.

Species-level sampling uncertainty was substantial. Median bootstrap SE was 0.058 for S3 rho and 0.071 for prune-only rho.

After separating estimated sampling variance from between-system heterogeneity, the S3 point decomposition of typical total variance was approximately:

- family: 15.1%;
- trait: 5.7%;
- residual between-system heterogeneity: 54.9%;
- sampling error: 24.2%.

Prune-only gave a similar decomposition: 14.0%, 2.2%, 58.6% and 25.3%, respectively.

Thus the family point contribution remained near its original value, whereas roughly one quarter of typical total variance was attributable to finite-species estimation error rather than biological heterogeneity.

The S3 two-way family × trait cluster bootstrap completed all 500 refits. Among heterogeneity components, the 95% interval for the family share was 0.123–0.749, the trait share was approximately 0–0.385, and the system share was 0.071–0.751.

System heterogeneity was the largest point estimate, but its interval overlapped strongly with the family component. We therefore do not interpret any heterogeneity component as statistically dominant (Fig. 1).

### Family context persisted beyond correlated-trait and design artifacts

Observed family repeatability was 0.150 for S3 and 0.148 for prune-only.

Several predeclared trait blocks were strongly correlated across families, including whole plant height versus maximum whole plant height (r = 0.812) and leaf area versus leaf dry mass (r = 0.805).

Despite preserving these correlations and the exact sparse incidence graph, the zero-family-effect null rarely generated family repeatability as high as observed.

For S3, the null median was 0.034 with 95% interval 0–0.139, and only 16 of 1,000 simulations reached or exceeded the observed family component after the +1 correction (p = 0.017).

For prune-only, the null median was 0.026 with 95% interval 0–0.122 (p = 0.009).

Collapsing the 12 traits into five biological domains left family repeatability nearly unchanged at 0.144 for S3 and 0.147 for prune-only.

Other audits were similarly stable. S3 family repeatability was 0.154 after species-count adjustment, 0.146 after simultaneous adjustment for species count, prune fraction and calibration geometry, 0.149 after BIEN source-composition adjustment, and 0.147 after source-citation adjustment (Fig. 2).

Thus the family component is not well explained by the measured geometry, provenance or predeclared trait-redundancy alternatives.

### Trait identity carried little robust information into an unseen family

The original held-out-family trait-mean predictor did not improve prediction.

For S3, gain was -0.024; for prune-only, -0.032. Neither passed the frozen portability criterion.

Shrinkage changed the interpretation but not the biological conclusion.

With training-only trait BLUPs, gain became +0.006 for S3 and -0.0048 for prune-only. The apparent negative prediction penalty therefore largely disappeared, but robust positive portability did not emerge across both tree treatments.

This pattern was consistent with the small amount of trait-level variation available to borrow. Median training trait variance was approximately 0.00090 for S3 compared with residual variance 0.0168; for prune-only, 0.00060 compared with 0.0247 (Fig. 3).

Trait identity therefore contributed little stable out-of-family predictive information about memory strength.

### The planned log-scale sensitivity could not be completed on the frozen population

The all-201 natural-log sensitivity failed its predeclared applicability condition because 25 S3 systems and 18 prune-only systems contained at least one nonpositive species median.

We did not introduce offsets, signed-log transformations or post-outcome removal of those systems.

The generality of the raw absolute-difference memory descriptor across multiplicative trait scale therefore remains unresolved.

### Family context was not detectably organized along deeper family phylogeny

In the complementary post-outcome analysis, pairwise differences in family context showed essentially no association with patristic distance among family crowns.

S3 Spearman rho was -0.015 (permutation p = 0.822), and prune-only rho was -0.011 (p = 0.871).

Alternative mean-based and leave-one-trait variants were similarly close to zero.

This exploratory result suggests that the recurring family component behaves more like a family-specific mosaic than a smooth deep-phylogenetic gradient.

## Discussion

### Phylogenetic memory is not a stable trait-intrinsic signature

Our central result is a mismatch between repeatability and portability.

Family identity contributes a recurring cross-trait component to the strength of phylogenetic memory, but the same named trait carries little information that can be transferred to an unseen family.

This distinction matters because phylogenetic signal is often discussed as though it were a property of a trait. A trait can indeed show phylogenetic structure in many clades while still lacking a stable **amount** of signal that generalizes among clades.

The failed portability result is therefore not evidence that plant traits lack phylogenetic structure. Rather, it shows that trait identity alone is a weak basis for transporting an estimated memory strength between families.

### The family component is modest but difficult to dismiss as a simple artifact

The family point share remained near 15% under several independent perturbations.

Importantly, accounting for species-level sampling uncertainty changed the residual interpretation but left the family point share almost unchanged.

Likewise, the family component exceeded a conservative null that preserved strong correlations among redundant trait outcomes while explicitly removing the family main effect.

Adjustments for species coverage, phylogenetic insertion geometry and BIEN source composition also had little effect.

Together, these analyses support a repeatable lineage-context pattern.

They do not identify its biological cause.

Family identity can summarize many correlated processes: developmental architecture, life history, ecological niche, lineage-specific evolutionary constraints, trait covariance structure, taxonomic or geographic sampling history, and unmeasured data-source heterogeneity.

The result should therefore be interpreted as **repeatable lineage context**, not as evidence for a particular family-specific evolutionary mechanism.

### Sampling uncertainty changes the meaning of “system specificity”

The original unweighted mixed model assigned more than 80% of variance to the residual.

Without measurement-error correction, that number could be read as evidence that phylogenetic memory is overwhelmingly idiosyncratic to each family × trait combination.

The species-bootstrap analysis rejects that interpretation.

Roughly one quarter of typical total variation is attributable to finite-species estimation error. Residual between-system heterogeneity remains substantial, but its magnitude is too uncertain to call dominant over the family component under the predeclared cluster bootstrap.

The relevant biological conclusion is therefore not that “most memory is system-specific.” It is that a large fraction remains unexplained after accounting for repeatable family and trait structure, while a material fraction of the apparent cell-level spread is estimation noise.

### Weak portability reflects little signal to borrow, not anti-portability

The shrinkage sensitivity materially changes the wording of the portability result.

Arithmetic trait means were mildly harmful predictors, but BLUP shrinkage moved those gains to approximately zero.

This indicates that the original negative gain was partly a consequence of borrowing noisy trait averages.

However, the small training trait variance means that there is little stable trait-level information available even after shrinkage.

The strongest conclusion is therefore not that trait information actively misleads prediction, but that **there is little portable trait-level memory information to borrow**.

### The scale of lineage context appears local rather than deeply hierarchical

The exploratory family-phylogeny check found no evidence that family context changes smoothly with deeper family relatedness.

This suggests that the recurring family component is not simply one slowly inherited macroevolutionary axis extending above family level.

Instead, the pattern resembles a mosaic of lineage contexts.

Because this analysis was defined after the family-context result was known, it should be treated as hypothesis-generating.

A stronger test would require an independently designed hierarchical study that samples multiple nested taxonomic levels prospectively.

### Relation to standard phylogenetic-signal metrics

The present memory gradient is intentionally a common distance-decay descriptor, not a general phylogenetic-signal estimator.

Blomberg's K, Pagel's lambda and model-based evolutionary parameters answer related but distinct questions (Blomberg et al., 2003; Pagel, 1999; Pearse et al., 2025).

Mantel-type approaches are sensitive to the chosen distance metrics and measurement error, and their performance relative to K-type statistics can reverse across conditions (Harmon & Glor, 2010; Hardy & Pavoine, 2012; Pavoine & Ricotta, 2013). We therefore do not interpret rho as a universally optimal index or infer mechanism from its absolute value.

The inferential target here is narrower: whether the same predefined distance-decay summary can be predicted across lineages.

Prospective known-truth qualification and species-level bootstrap uncertainty are central to that interpretation.

A future independent replication using K, lambda or model-based parameters would test whether the **portability asymmetry itself** generalizes across definitions of phylogenetic signal.

### Implications for comparative evolution

Comparative analyses often borrow evolutionary information across clades.

Our results indicate that such borrowing should not be justified solely by trait identity.

A trait may be phylogenetically structured in many lineages but still lack a stable, transferable signal strength.

Accordingly, trait-specific phylogenetic priors, covariance assumptions or imputation rules learned in one lineage should be validated out of lineage whenever they are intended to generalize.

More broadly, evolutionary generalization should be treated as an empirical prediction problem rather than assumed from biological labels.

## Limitations

The study uses a distance-based memory gradient rather than K, lambda or a fitted evolutionary-process parameter, and conclusions apply directly to that response.

The raw-versus-log scale sensitivity remains unresolved because the identical 201-system population contains nonpositive species medians and the analysis did not introduce an outcome-dependent rescue transformation.

The family component is repeatable but mechanistically unidentified.

The deep-family-phylogeny result is exploratory.

Finally, this temporal comparative study does not answer the original broader time × space turnover question, whose spatial arm stopped at prospective qualification before biological outcomes were opened.

## Conclusion

Phylogenetic trait memory is neither purely trait-intrinsic nor overwhelmingly system-specific.

Across 45 plant families and 12 traits, family identity contributes a modest repeatable context that survives several statistical and data-structure audits. Yet trait identity provides almost no robust information that predicts memory strength in an unseen family.

The evolutionary structure associated with a trait should therefore be treated as **lineage-contingent unless its portability has been demonstrated directly**.

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

## Figure legends

## Figure 1. Sampling error accounts for a substantial part of apparent cell-level variation

**A**, Original S3 crossed-lmer variance shares compared with the measurement-aware point decomposition. The original residual share of 0.806 is not interpreted as biological system specificity. After incorporating species-cluster bootstrap sampling variances, typical total variance is partitioned approximately into family 15.1%, trait 5.7%, residual between-system heterogeneity 54.9%, and sampling error 24.2%. **B**, Measurement-aware S3 heterogeneity shares with pre-frozen two-way family × trait cluster-bootstrap 95% intervals. System heterogeneity is the largest point estimate, but its interval overlaps strongly with the family component; no heterogeneity component is interpreted as dominant. **C**, Mandatory prune-only sensitivity, showing a similar point decomposition (family 14.0%, trait 2.2%, system heterogeneity 58.6%, sampling error 25.3%).

## Figure 2. Correlated traits and measured design artifacts do not explain the family component

**A**, Observed family repeatability compared with the predeclared zero-family-effect correlated-trait null. The null preserves trait-specific means and variances, the exact sparse family × trait incidence graph, and correlations within three predeclared redundant-trait blocks while simulating no family main effect. Observed family repeatability exceeds the null on both S3 (R_family = 0.150, p = 0.017) and prune-only trees (0.148, p = 0.009). Thick lines show null 95% intervals, circles null medians, and diamonds observed values. **B**, S3 family repeatability across independent robustness audits. Values remain close to 0.15 after species-count adjustment, full geometry adjustment, BIEN source-composition adjustment, source-citation adjustment, and collapse of 12 trait labels into five predeclared biological domains. These analyses support a repeatable lineage-context pattern but do not identify its biological cause.

## Figure 3. Trait identity carries little robust phylogenetic-memory information across families

**A**, Leave-one-family-out portability gain using unshrunk same-trait means versus training-only BLUPs. Shrinkage changes S3 gain from −0.024 to +0.006 and prune-only gain from −0.032 to −0.0048. Thus the apparent prediction penalty largely disappears, but robust positive portability does not emerge across both tree treatments. **B**, Median training trait variance is small relative to residual variance in the same LOFO mixed models, explaining why there is little stable trait-level information to borrow. **C**, Generalization hierarchy. The trait-intrinsic hypothesis is not supported; the family-context hypothesis receives modest support; a complementary post-outcome test of smooth deep-family inheritance is not supported. The latter is exploratory and not treated as a confirmatory primary result.
