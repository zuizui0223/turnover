# Phylogenetic trait memory is context-dependent across plant families

## Abstract

Phylogenetic signal is often discussed as if a trait carries a characteristic degree of evolutionary conservatism, yet the same trait can evolve under different regimes in different clades. We asked a predictive version of this problem: does the strength of phylogenetic memory associated with a plant trait transfer across independent lineages? We used BIEN 4.2.8 trait data and a pinned V.PhyloMaker2 vascular-plant phylogeny to construct a prospectively qualified crossed matrix of family × trait systems. Before opening real trait-memory effects, systems had to pass species-support, semantic-validity, phylogenetic-crosswalk, and known-truth geometry-informativeness gates. The final core contained 201 systems spanning 45 vascular-plant families and 12 continuous traits. For each system, we defined memory-loss strength as the Spearman association between all-pair patristic separation and absolute trait-state dissimilarity among species. The mean memory-loss correlation was 0.093, but effects were strongly heterogeneous. A crossed REML decomposition attributed 0.150 of total variance to family identity (95% bootstrap CI 0.020–0.286), 0.043 to trait identity (0–0.134), and 0.806 to residual or family × trait-specific variation (0.660–0.952). In a separately prequalified leave-one-family-out prediction, the same trait measured in other families did not improve prediction over a global training mean (S3 gain = -0.024, permutation p = 0.091; prune-only gain = -0.032, p = 0.193). Conversely, after trait-specific means were controlled, family identity retained a conditional cross-trait repeatability of 0.183 (0.029–0.337), with a prune-only estimate of 0.168. Thus phylogenetic memory is not a robustly portable intrinsic property of trait identity across plant families. Most heterogeneity is specific to the family × trait combination, while family identity carries a modest recurring context across traits.

## Introduction

Closely related species often resemble one another, and the resulting phylogenetic signal is a central object of comparative biology. Classical approaches quantify this structure with statistics such as Blomberg's K or model-based branch-length transformations and ask whether observed trait values are more similar among relatives than expected by chance or under a reference evolutionary process (Blomberg et al. 2003; Münkemüller et al. 2012). These methods established an important general point: phylogenetic structure is common, but its magnitude and interpretation depend on the trait, the lineage, the phylogeny, and the evolutionary process generating the data.

This context dependence is especially relevant for plant functional traits. Ackerly (2009), for example, showed that evolutionary rates of the same functional traits can vary strongly among woody plant radiations. More generally, comparative methods now distinguish among phylogenetic signal, evolutionary rate, model fit, and multivariate structure rather than treating any single signal statistic as a universal descriptor of evolutionary conservatism (Münkemüller et al. 2012; Revell 2018). The fact that clades differ, however, leaves a different question unresolved. If a trait exhibits a certain amount of phylogenetic memory in one collection of lineages, is that estimate useful for predicting the same trait in a lineage that was not used to estimate it?

That question is about **portability**, not merely about the presence of phylogenetic signal. A trait can exhibit clear within-clade phylogenetic structure and still fail to carry a transferable signature across clades. Conversely, lineage identity can contribute a recurring evolutionary context across multiple traits without implying that lineage effects dominate trait effects. These distinctions are difficult to make from the common design in which one trait is analyzed on one phylogeny, or several fitted signal statistics are compared after the fact. They require repeated representation of the same traits across multiple independent clades and multiple traits within the same clades.

We therefore constructed a crossed family × trait design for vascular plants and separated three questions that are often conflated. First, how much variation in phylogenetic memory is repeatable by trait identity and by family identity? Second, does trait identity improve prediction for a completely held-out family? Third, after each trait is allowed its own mean memory level, does family identity recur across multiple traits? We treated these as separate estimands rather than using one analysis to choose among them.

A central design feature was prospective qualification. The generalized time-space turnover programme that motivated this repository closed before any generalized trait-turnover effect was opened because the spatial informativeness criterion could not be met across the required number of independent families. A later temporal trait-versus-lineage variance-ratio analysis likewise stopped before real effects because its fixed crossed graph could recover the direction, but not the predeclared precision, of a twofold variance contrast. The analyses reported here were then independently frozen, tested on known-truth simulations where required, and only executed after their own admission criteria passed. The resulting evidence supports a context-dependent view of plant trait memory: trait identity is not robustly portable across families, family identity contributes a modest recurring component across traits, and most heterogeneity remains specific to particular family × trait combinations.

## Materials and methods

### Data source and phylogeny

Trait records came from BIEN database version 4.2.8, accessed through a pinned RBIEN implementation. BIEN integrates plant trait, occurrence, plot, and taxonomic information in a standardized global infrastructure (Enquist et al. 2026). The live `agg_traits` table used for qualification contained 25,932,628 rows at the time of analysis.

Phylogenetic relationships were taken from V.PhyloMaker2 (Jin & Qian 2022), pinned to repository commit `7af3fb5152f691af2e4ec9d5e2e467d1b50505e9` and the `GBOTB.extended.TPL` backbone. The source tree contained 74,529 unique tips, all matched exactly to the associated tip metadata in the source preflight. We used scenario S3 as the primary tree-building rule. Because S3 can place species absent from the backbone at genus- or family-level positions, every primary system was also required to retain at least 20 backbone-native ("prune") tips, and all reported analyses were repeated on those native tips as a mandatory sensitivity.

### Trait universe

Before any generalized trait-memory effect was opened, BIEN trait names were assigned to semantic classes. Forty-three traits were classified as continuous scalar traits and nine as nominal categorical traits. Two additional traits were fail-closed for the primary programme and remained excluded. The final empirical core reported here contained only continuous traits.

Continuous trait records had to be finite numeric values with one nonempty unit within a family × trait system. Species state was the median of all eligible measurements for that species. Nominal categorical traits, in earlier qualification stages, were represented by a unique modal category; species with tied modes were excluded. No family or trait was removed after inspecting its real memory-loss effect.

### Outcome-blind qualification of family × trait systems

System selection was completed before real family × trait memory-loss correlations were opened.

The temporal-only follow-up began with all preclassified BIEN traits and required at least 20 species with nonmissing trait values per family × trait system. An exact reuse of a previously generated outcome-blind BIEN aggregate identified 1,455 structurally supported systems across 240 families and 49 traits.

A semantic-validity gate then required numeric and unit consistency for continuous traits, or a unique modal state and blank unit for categorical traits, together with at least 20 resolvable species and at least two distinct species states. This retained 1,219 systems across 219 families and 47 traits.

Next, systems were crosswalked to the pinned V.PhyloMaker2 backbone. Each system had to retain at least 20 species under the S3 placement and at least 20 exact backbone-native tips. This retained 802 systems across 160 families and 47 traits.

Before running known-truth informativeness simulations, we applied a mathematically lossless necessary-core pruning rule: because informativeness can only remove family × trait edges, any family represented by fewer than two traits or trait represented in fewer than five families could never enter the final crossed analysis. Iterative simultaneous pruning reduced the simulation set to 722 systems across 120 families and 25 traits.

For each remaining system, we asked whether its observed S3 and prune-only phylogenetic geometry could recover a synthetic benchmark memory correlation of 0.15. The synthetic state process and calibration rules were frozen before simulation. Admission required, on both S3 and prune-only geometries, a median absolute recovery error <= 0.10, directional recovery >= 0.80, and valid-replicate fraction >= 0.90 over 1,000 evaluation replicates. Previously evaluated systems reused their frozen result exactly; novel systems were simulated under the identical contract.

Informativeness retained 255 systems across 70 families and 22 traits. We then iteratively imposed the final crossed-replication rule: each family had to contribute at least two traits, each trait had to occur in at least five families, the final graph had to contain at least 12 families and four traits, and the bipartite graph had to be connected. The final core contained 201 systems, 45 families, and 12 continuous traits.

The 12 final traits were: diameter at breast height (1.3 m), leaf area, leaf area per leaf dry mass, leaf dry mass, leaf dry mass per leaf fresh mass, leaf nitrogen content per leaf area, leaf nitrogen content per leaf dry mass, leaf phosphorus content per leaf dry mass, maximum whole plant height, seed mass, stem wood density, and whole plant height.

### Phylogenetic memory-loss effect

For each admitted family × trait system, we estimated one effect on the S3 tree and one on the prune-only tree.

For continuous traits, species state was the median eligible trait value. For every unordered species pair, trait-state dissimilarity was the absolute difference between the two species states, and phylogenetic separation was the patristic distance between the corresponding tips. We defined

[
ho_{ft} = operatorname{Spearman}(d^{phylo}_{ij}, |z_i-z_j|)
]

for family (f) and trait (t).

Larger positive (ho) means that trait-state dissimilarity tends to increase with phylogenetic separation: a stronger monotonic loss of trait similarity over evolutionary divergence. We call this quantity **memory-loss strength** or a **phylogenetic memory gradient**. It is not a time-calibrated decay rate and is not intended as a replacement for Blomberg's K, Pagel-type parameters, or explicit evolutionary-rate models.

For the complete set of unordered pairs and whole-state label permutations, the exact expected permutation-null Spearman correlation is zero. This identity was proven analytically and verified by exact small-(n) enumeration before real effects were opened. Thus the observed (ho) is already the null-centered effect; permutations are not required to estimate its null mean.

### Analysis 1: crossed repeatability decomposition

The first admitted analysis asked how much family × trait variation was repeatable along the family and trait axes separately, without comparing which variance was larger. We fit

[
ho_{ft} = mu + u_f + v_t + epsilon_{ft},
]

where (u_f sim N(0,sigma^2_F)), (v_t sim N(0,sigma^2_T)), and (epsilon_{ft} sim N(0,sigma^2_E)). The model was fit by REML with unweighted family × trait systems.

We reported

[
R_F = rac{sigma_F^2}{sigma_F^2+sigma_T^2+sigma_E^2},quad
R_T = rac{sigma_T^2}{sigma_F^2+sigma_T^2+sigma_E^2},quad
R_E = rac{sigma_E^2}{sigma_F^2+sigma_T^2+sigma_E^2}.
]

A known-truth gate verified that each repeatability share could be recovered with the predeclared accuracy on the realized 201-edge graph. Uncertainty was quantified with 2,000 parametric bootstrap replicates under seed 20261003. We repeated the model on prune-only effects and conducted predeclared leave-one-trait-out and leave-one-family-out robustness analyses. A prior attempt to classify trait-versus-family **dominance** had failed its separate precision gate before real effects were opened; therefore (R_F) and (R_T) were not compared with a formal dominance test.

### Analysis 2: cross-lineage portability of trait identity

The second analysis asked whether a trait's memory estimate transfers to a completely held-out family.

For each family in turn, all systems belonging to that family were removed from the training data. For each held-out system ((f,t)), the trait-based predictor was the arithmetic mean (ho) of trait (t) among training families. The baseline predictor was the arithmetic mean (ho) across all training systems. Every held-out family × trait system contributed once, with no family, trait, species-count, or precision weighting.

We defined portability gain as

[
G_T = 1 - rac{SSE_{trait}}{SSE_{global}}.
]

Positive values mean that knowing the trait identity improves prediction of a new family relative to a global training mean.

The null test permuted observed (ho) values among trait labels **within each family**, preserving each family's response distribution and the exact family × trait incidence graph while breaking cross-family trait correspondence. We used 999 permutations with seed 20261003. The directional positive criterion was (G_T>0) and permutation (ple0.05), and a robust portability claim required the criterion to pass on both S3 and prune-only effects.

The prediction statistic, graph, permutation structure, signal benchmark, and false-positive benchmark were subjected to a known-truth admission gate before real effects were opened.

### Analysis 3: conditional family repeatability across traits

The third analysis asked whether family identity contributes a recurring context after differences in average memory among traits are removed. We fit

[
ho_{ft} = alpha_t + u_f + epsilon_{ft},
]

where each trait received its own fixed mean (alpha_t), (u_f sim N(0,sigma_F^2)), and (epsilon_{ft} sim N(0,sigma_E^2)).

The primary parameter was

[
R_{F|T} = rac{sigma_F^2}{sigma_F^2+sigma_E^2}.
]

Before real effects were opened, we froze 0.10 as a practical reference: a 95% bootstrap interval entirely above 0.10 would be described as repeatable above that reference; an interval entirely below 0.10 as weak relative to it; otherwise the result would remain uncertain relative to 0.10. The model passed its own known-truth gate and was then fit to S3 effects, with 2,000 parametric bootstrap replicates, prune-only sensitivity, and leave-one-trait and leave-one-family robustness.

### Additional analyses that were not opened

Two later complementary analyses were proposed after the 201 effects had been estimated but were required to pass their own known-truth gates before real results were calculated.

First, a repeated-measures S3-versus-prune model was intended to estimate how much family × trait-specific variation was stable across backbone treatments. Its high-stability benchmark produced 0.899 valid nonsingular fits, below the frozen 0.900 criterion, so the real decomposition was not fit.

Second, a leave-one-trait-out test was intended to ask whether family context estimated from other traits predicts a completely unseen trait. Its null calibration passed, but known-truth power was 0.582, below the frozen 0.80 criterion. The real test was therefore not executed.

These failed gates were retained to avoid turning weakly identified post-outcome questions into nominal findings.

## Results

### Outcome-blind qualification produced a broad crossed core

The temporal-only qualification sequence began with 1,455 structurally supported systems across 240 families and 49 traits. Semantic filtering retained 1,219 systems across 219 families and 47 traits; phylogenetic crosswalk retained 802 systems across 160 families and 47 traits. Known-truth geometry informativeness reduced the set to 255 systems across 70 families and 22 traits. The final degree and connectivity constraints yielded 201 systems spanning 45 families and 12 continuous traits.

The final graph was connected. Every family was represented by at least two traits and every trait by at least five families. Thus both the family and trait axes were repeatedly observed rather than being inferred from largely disjoint sets of systems.

### Memory-loss strength was commonly positive but highly heterogeneous

Across the 201 S3 systems, memory-loss (ho) had mean 0.0928, median 0.0531, and standard deviation 0.1429. Effects ranged from -0.1829 to 0.7093, and 74.6% were positive.

Prune-only effects were similar but somewhat larger on average: mean 0.1143, median 0.0652, standard deviation 0.1716, range -0.2087 to 0.7661, with 71.6% positive. S3 and prune-only system effects were strongly concordant (Pearson (r=0.848), Spearman (ho=0.832)).

Thus many systems showed a positive phylogenetic memory gradient, but its strength varied widely among family × trait combinations.

### Most crossed variation was family × trait specific

The crossed repeatability model estimated

- (R_F=0.1504) for family identity,
- (R_T=0.0433) for trait identity, and
- (R_E=0.8063) for residual or family × trait-specific variation.

The 95% parametric-bootstrap intervals were 0.0204–0.2861 for (R_F), 0–0.1335 for (R_T), and 0.6600–0.9522 for (R_E).

The prune-only sensitivity was similar: family 0.1482, trait 0.0207, residual 0.8312. Leave-one-out refits yielded family-repeatability estimates from 0.0935 to 0.1897 and trait-repeatability estimates from 0.0241 to 0.0606.

The analysis did not test whether family repeatability exceeded trait repeatability. The supported conclusion is instead that most variation was not captured by either marginal identity alone, while a family-level component was estimable and the trait-level component was small and uncertain.

### Trait identity did not improve prediction for a held-out family

In leave-one-family-out prediction, the trait-specific predictor did not outperform the global training baseline.

For S3 effects, (SSE_{global}=4.151) and (SSE_{trait}=4.251), giving portability gain (G_T=-0.0242). The blocked-permutation p-value was 0.091.

For prune-only effects, (SSE_{global}=5.990) and (SSE_{trait}=6.184), giving (G_T=-0.0324) with p=0.193.

Neither tree treatment met the predeclared positive criterion. This negative result does not mean that phylogenetic memory is absent. Rather, the memory estimate associated with a named trait in other families did not provide robust predictive information for the same trait in a new family.

### Family identity retained a recurring component after trait means were removed

After assigning each trait its own fixed mean, conditional family repeatability was

[
R_{F|T}=0.1825
]

for S3 effects, with 95% bootstrap interval 0.0285–0.3369. The prune-only estimate was 0.1680.

Leave-one-trait and leave-one-family estimates ranged from 0.1205 to 0.2268, indicating that the fitted family component was not created by a single trait or family.

Because the confidence interval crossed the predeclared 0.10 practical reference, the frozen classification was **uncertain relative to 10%**. The estimate nevertheless indicates a recurring family-level component after trait-specific mean differences were removed.

## Discussion

### Phylogenetic memory is not a portable intrinsic property of trait identity

The central result is a failure of portability, not a failure of phylogenetic memory. Across the admitted systems, three quarters of S3 effects were positive, and many individual family × trait combinations therefore exhibited the expected increase in trait dissimilarity with evolutionary separation. Yet the same trait measured in other families did not improve prediction for a family that had been withheld completely.

This distinction matters. Describing a trait as "phylogenetically conserved" can encourage an implicit assumption that its degree of conservatism is a property of the trait itself. Our predictive analysis shows why that assumption can fail. A trait can carry real phylogenetic structure within multiple lineages while lacking a single transferable memory signature across those lineages.

The result is consistent with, but not redundant with, earlier demonstrations of clade-dependent trait evolution. Ackerly (2009) showed that evolutionary rates of the same functional traits can differ sharply among plant radiations. Our contribution is to turn that heterogeneity into an explicit prediction problem. Rather than asking only whether fitted rates or signal statistics differ among clades, we ask whether knowing a trait's memory in other clades helps predict a lineage that was not used for estimation. Under the predeclared family-blocked criterion, it did not.

### Lineage context recurs, but most heterogeneity remains system specific

The crossed decomposition and conditional family model point to a modest lineage context. Family identity accounted for an estimated 15% of total crossed variation, and after trait-specific means were removed the conditional family repeatability was 0.183. The latter estimate was robust to omitting individual traits or families and similar under the prune-only phylogeny.

At the same time, approximately 81% of variation in the crossed model remained residual or family × trait specific. This is the dominant empirical fact in the descriptive decomposition. The memory associated with a trait cannot be reduced to a universal trait constant, but neither can it be reduced to a single family-wide constant. The particular combination of lineage and trait matters.

We deliberately do not convert the family and trait repeatability estimates into a statistical dominance claim. The prospective variance-ratio analysis that would have supported such a claim failed its known-truth precision gate before real effects were opened. The correct interpretation is therefore asymmetric but narrower: trait identity failed a direct cross-lineage portability test, whereas family identity retained a modest recurring cross-trait component.

### Portability is a useful complement to phylogenetic-signal statistics

Phylogenetic-signal metrics answer important but different questions. Blomberg et al. (2003) defined signal in terms of resemblance among relatives and showed how both trait type and evolutionary process affect it. Münkemüller et al. (2012) demonstrated that common metrics can differ substantially in behavior and interpretation. Recent work on multivariate phylogenetic signal likewise emphasizes that apparent signal depends on how phenotypic dimensions are represented and summarized.

Our memory-loss (ho) is intentionally simple: it is a rank association between patristic separation and trait-state dissimilarity within a family. It should not be interpreted as a universal replacement for K, (lambda), or evolutionary-rate models. Its advantage here is that the same estimand can be applied consistently to many family × trait systems and placed inside an explicit held-out prediction design.

The portability question also changes the interpretation of "general" phylogenetic conservatism. A trait-specific prior estimated from one set of clades is useful for another clade only if it improves out-of-sample prediction there. Our results suggest caution when exporting such priors across plant families without lineage-specific recalibration.

### Why the family component should not be overinterpreted

The recurring family component does not identify a mechanism. Families can differ in life history, morphology, ecology, developmental constraint, species richness, measurement composition, and the historical mixture of environments represented in BIEN. Any of these could contribute to a family-level shift in the observed memory gradient.

The result also operates at the taxonomic scale of families. It does not establish a continuously evolving deep-phylogenetic process among families. A proposed post-outcome test of whether family context itself generalized to a completely held-out trait failed its known-truth power gate, and a proposed repeated S3/prune stability decomposition narrowly failed its predeclared valid-fit criterion. We therefore retain the family component as a repeatability pattern rather than assigning it a deeper phylogenetic or mechanistic explanation.

### Prospective qualification changed the scientific conclusion

The analysis history is itself informative. The original programme sought a generalized comparison of trait turnover through evolutionary time and geographic space. That programme stopped before generalized effects were opened because spatial informativeness could not be established across the required number of families. A subsequent trait-versus-lineage variance-ratio question also stopped before real effects because the crossed graph could not recover the magnitude of a twofold variance contrast with the required precision.

Those failures narrowed the scientific question rather than being repaired by weaker thresholds. The analyses reported here were only opened after their own known-truth gates passed. Two additional post-outcome questions were also left unopened when their power or valid-fit gates failed. This sequence reduces the risk that the final story reflects repeated optimization toward a favorable result.

### Limitations

First, BIEN is a heterogeneous compilation. We used strict semantic rules, species-level medians, and outcome-blind qualification, but remaining measurement heterogeneity contributes to the residual component. The large residual share should therefore not be read as a pure biological family × trait interaction.

Second, the final 201-system core contains 12 continuous traits. Categorical traits failed earlier informativeness or crossed-replication requirements and are not represented in the reported empirical synthesis. The conclusions therefore apply most directly to the continuous plant traits represented in the qualified core.

Third, S3 can place species that are not native tips in the backbone. We required at least 20 native tips per system and repeated all empirical analyses on the native-tip subset. S3 and prune-only effects were strongly concordant, but phylogenetic uncertainty remains broader than this single sensitivity captures.

Fourth, memory-loss (ho) is a monotonic rank-gradient, not a mechanistic evolutionary parameter or time constant. Explicit models of Brownian motion, OU processes, rate heterogeneity, or adaptive regimes answer different questions.

Finally, the data support context dependence but not its cause. Testing whether lineage context reflects particular ecological regimes, life histories, environments, or developmental constraints will require a new study with those predictors defined before examining the family-level effects.

## Conclusions

Across a prospectively qualified matrix of plant families and functional traits, phylogenetic memory was common but not portable in the simple sense of being a stable property of trait identity. The same trait's memory in other families did not improve prediction for a held-out lineage. Family identity, in contrast, retained a modest repeatable component across traits after trait-specific means were removed, while most heterogeneity remained specific to the family × trait combination.

The practical implication is straightforward: a phylogenetic-memory estimate learned for trait (t) in one set of plant clades should not automatically be exported to another clade as though trait identity alone determined its evolutionary conservatism. Comparative inference is better framed as context dependent, with trait identity, lineage identity, and their particular combination all contributing at different levels.

## Data and code availability

All qualification contracts, source pins, known-truth gates, analysis scripts, audit trails, and result summaries are maintained in the `zuizui0223/turnover` repository.

Primary data source: BIEN 4.2.8.

Phylogeny source: V.PhyloMaker2, pinned commit `7af3fb5152f691af2e4ec9d5e2e467d1b50505e9`, `GBOTB.extended.TPL`.

The repository records failed as well as passed prospective gates. Raw BIEN trait measurements, species-level states, and species names were not persisted as manuscript result artifacts.

## References

Ackerly DD. 2009. Conservatism and diversification of plant functional traits: evolutionary rates versus phylogenetic signal. *Proceedings of the National Academy of Sciences USA* 106:19699–19706. doi:10.1073/pnas.0901635106.

Blomberg SP, Garland T Jr, Ives AR. 2003. Testing for phylogenetic signal in comparative data: behavioral traits are more labile. *Evolution* 57:717–745. doi:10.1111/j.0014-3820.2003.tb00285.x.

Enquist BJ, Maitner BS, Boyle B, et al. 2026. BIEN: A biodiversity informatics ecosystem advancing open and reproducible workflows for plant observation, plot and trait data. *Methods in Ecology and Evolution* 17:1556–1584. doi:10.1111/2041-210X.70274.

Jin Y, Qian H. 2022. V.PhyloMaker2: An updated and enlarged R package that can generate very large phylogenies for vascular plants. *Plant Diversity* 44:335–339. doi:10.1016/j.pld.2022.05.005.

Münkemüller T, Lavergne S, Bzeznik B, Dray S, Jombart T, Schiffers K, Thuiller W. 2012. How to measure and test phylogenetic signal. *Methods in Ecology and Evolution* 3:743–756. doi:10.1111/j.2041-210X.2012.00196.x.

Revell LJ. 2018. Comparing evolutionary rates between trees, clades and traits. *Methods in Ecology and Evolution* 9:994–1005. doi:10.1111/2041-210X.12977.
