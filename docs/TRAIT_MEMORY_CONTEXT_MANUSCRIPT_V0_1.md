# Manuscript skeleton — Context dependence of phylogenetic trait memory

## Working title

**Phylogenetic trait memory is context-dependent across plant families**

Alternative:

**Cross-lineage prediction reveals limited portability of phylogenetic trait memory**

Avoid titles that say lineage effects "dominate" trait effects. The prospectively frozen variance-ratio study did not pass its precision gate.

## One-sentence result

Trait-specific phylogenetic-memory estimates do not robustly predict the same trait in a held-out plant family; instead, most variation is family-by-trait specific, with a modest repeatable family-level component across traits.

## Gap

Phylogenetic signal is usually estimated for one trait in one phylogeny or compared among traits/clades. Those approaches establish whether traits are conserved and whether evolutionary tempo differs among clades, but they do not directly test whether a trait's estimated memory is **portable to an unseen lineage**.

The study separates three questions that are often conflated:

1. How much family × trait variation is repeatable by trait identity?
2. Does trait identity improve prediction for a completely held-out family?
3. After trait-specific means are removed, is there a recurring family context across multiple traits?

## Data and qualification

The final empirical core was selected entirely before real memory effects were opened:

- 201 family × trait systems
- 45 vascular-plant families
- 12 continuous traits
- BIEN 4.2.8
- V.PhyloMaker2 / GBOTB.extended.TPL
- every system passed support, semantic validity, S3 + prune-only crosswalk, and known-truth geometry informativeness

Three independent execution routes produced exactly the same 201 S3 and prune-only memory effects; the maximum numerical difference is zero.

## Memory-gradient response

For every family × trait system:

- species state = median valid trait value;
- trait-state dissimilarity = absolute difference;
- phylogenetic separation = all unordered patristic distances;
- memory-loss strength = Spearman correlation between separation and dissimilarity.

The exact complete-label permutation-null mean is zero.

Larger positive rho means a stronger monotonic erosion of trait similarity across phylogenetic separation. It is not a time-calibrated decay rate.



## Why call this a memory gradient rather than phylogenetic signal?

The statistic is deliberately narrower than a general claim of “phylogenetic signal.” For a given family × trait system, it asks whether **trait-state difference tends to increase as two species are separated by more patristic distance**. It therefore describes the erosion of pairwise similarity along the realized phylogenetic geometry of that system.

This distinction matters for the biological question. A global signal statistic can establish that close relatives resemble one another, but the present study needs a response that can be calculated identically for the same trait in many separate families and then subjected to held-out-family prediction. The memory gradient supplies that common response.

Accordingly:

- rho > 0 means more distant relatives tend to differ more strongly in trait state;
- rho near 0 means that monotonic distance–dissimilarity gradient is weak, not necessarily that the trait has no phylogenetic structure of any kind;
- rho < 0 is possible and should not be translated into “negative evolutionary rate”;
- rho is not an OU alpha, evolutionary rate, half-life, or elapsed-time decay constant.

The manuscript should therefore use **phylogenetic memory gradient** for the measured response and reserve **phylogenetic signal** for the broader literature to which it is being related.

## Result 1 — Most heterogeneity is system-specific

Crossed REML decomposition:

| Component | S3 repeatability share | 95% bootstrap CI | Prune-only |
|---|---:|---:|---:|
| Family | 0.150 | 0.020–0.286 | 0.148 |
| Trait | 0.043 | 0–0.134 | 0.021 |
| Unresolved system-level / residual | 0.806 | 0.660–0.952 | 0.831 |

The analysis was prospectively forbidden from converting these estimates into a family-versus-trait dominance test.

Residual variance here is not a pure interaction term. It can include true family × trait interaction, estimation error in system-level rho, BIEN measurement heterogeneity, and other unmodeled variation. The manuscript therefore calls it the **unresolved system-level/residual component**, not a demonstrated interaction effect.

## Result 2 — Trait identity does not transport across families

Family-blocked prediction:

### S3
- gain = -0.024
- permutation p = 0.091
- same-trait predictor SSE = 4.251
- global-mean baseline SSE = 4.151

### Prune-only
- gain = -0.032
- p = 0.193
- same-trait predictor SSE = 6.184
- global baseline SSE = 5.990

The robust criterion fails on both tree treatments.

Interpretation:

> A trait may show real phylogenetic memory within particular lineages without carrying a transferable memory signature that predicts another family.

## Result 3 — Family context recurs across traits

After assigning each trait its own fixed mean:

`rho ~ 0 + trait_name + (1 | family)`

- conditional family repeatability = 0.183
- 95% bootstrap CI = 0.029–0.337
- prune-only = 0.168
- leave-one-trait / leave-one-family range = 0.121–0.227

The interval spans the predeclared 0.10 practical reference, so the frozen classification is **uncertain relative to 10%**.

The result nevertheless shows that the estimated family component is not produced by one trait or one family.

### Pre-frozen geometry and coverage robustness

A mandatory sensitivity specified before the real memory effects were opened adjusted the same 201 systems for three outcome-blind features that could otherwise masquerade as family context: log species count, the fraction of backbone-native (prune-only) tips, and the log calibration lambda required for the known-truth informativeness benchmark.

The family repeatability share was essentially unchanged: **0.150 unadjusted versus 0.146 after geometry adjustment**. The trait share changed from 0.043 to 0.049 and the unresolved/residual share from 0.806 to 0.805. The standardized fixed effects were also small (log species count 0.0002, prune fraction 0.0064, calibration lambda 0.0025).

Thus the recurring family component is not explained by these measured differences in taxon coverage, taxonomic insertion, or phylogenetic measurement geometry. This does **not** establish a causal biological family effect: unmeasured BIEN study heterogeneity and other family-correlated features can still contribute.

### Complementary deep-phylogeny check

A post-outcome exploratory analysis asked whether this recurring family context is itself smoothly organized across deeper family phylogeny. For each of the 45 focal families, a context score was computed as the median trait-specific deviation from the leave-self-out mean for that trait, and family positions were defined by their full GBOTB family crowns.

There was essentially no association between family patristic distance and difference in context score (S3 Spearman rho = -0.015, 9,999-permutation p = 0.822; prune-only rho = -0.011, p = 0.871). Using mean rather than median context scores gave rho = -0.009 (p = 0.887), and leave-one-trait-out S3 estimates ranged only from -0.038 to +0.017.

Because this analysis was designed after the real memory effects had been opened, it is complementary rather than a prospective primary result. It nevertheless sharpens the scale of the family component: the recurring context is detectable at the family level but is not detectably arranged as a smooth function of deeper family relatedness. At this resolution it is better described as a **family-specific mosaic** than as one continuously inherited deep-phylogeny regime.

## Core ecological novelty

The strongest contribution is **not** that phylogenetic signal differs among clades; that is already well established. The new result is a directional asymmetry in what can be generalized from a crossed family × trait design.

- **Trait → new lineage fails:** knowing the memory gradient of the same named trait in other families does not robustly predict that trait in a held-out family.
- **Lineage → other traits leaves a residue:** after trait-specific means are removed, family identity retains a modest repeatable deviation across multiple traits.
- **Deep lineage distance does not organize that residue:** the complementary family-phylogeny analysis finds no smooth increase in context difference with deeper family separation.

Together, these results point away from a single transferable “memory of trait X” and also away from one smooth deep-phylogenetic conservatism axis. The empirical unit that remains is closer to a **trait embedded in a particular lineage context**.

This asymmetry concerns predictive generalization. It is not a statistical claim that family variance exceeds trait variance.

## Integrated interpretation

The evidence supports a **context-dependent memory architecture**:

- trait identity alone is not a robust cross-lineage predictor;
- family identity contains a modest recurring cross-trait component;
- that family context is not detectably continuous across deeper family phylogeny in a post-outcome complementary check;
- most variation remains unresolved at the individual family × trait system level.

This is not equivalent to saying family effects are statistically larger than trait effects.



## Mechanistic hypotheses generated by the result

The observed context dependence does not identify a mechanism, but it sharply narrows what a mechanism must explain: **the same measured trait can carry real phylogenetic memory within a family without exporting a stable memory strength to another family, while family identity recurs modestly across different traits.**

Four non-exclusive mechanisms are therefore natural targets for future, independently designed tests.

1. **Whole-organism life-history context.** The selective meaning of a leaf, stem or size trait depends on the growth form, woodiness, longevity and demographic strategy in which it is embedded. A nominally identical trait may therefore experience different effective constraints in different families.
2. **Lineage-specific developmental and genetic constraint.** Families differ in developmental architecture, historical contingency and accessible phenotypic variation. These differences can make several traits jointly conservative or labile without requiring one universal family-wide evolutionary rate.
3. **Clade-specific environmental occupancy.** Families occupy different climatic, edaphic and biogeographic domains. Persistent environmental structure can alter the realized evolutionary memory of multiple traits within the same lineage.
4. **Observation and taxon-composition heterogeneity.** BIEN combines measurements from heterogeneous studies and species sets. Although the prospective semantic and geometry gates remove many obvious failures, residual differences in measurement replication and taxonomic composition could contribute to the large family × trait-specific component.

These mechanisms are **not tested in the present manuscript**. They define falsifiable follow-ups. In particular, a future mechanism study should predict family-level memory deviations from independently measured life-history, environmental or developmental covariates and evaluate those predictions on held-out families. Re-explaining the present 201 systems with post-hoc covariate selection would not provide an independent test.

## Ecological implication

The result changes how phylogenetic signal should be transported in comparative ecology. A published estimate that a trait is strongly or weakly conserved in one clade should not automatically become a prior for that trait in another clade. The relevant unit of generalization is closer to a **trait-in-lineage context** than to the trait label alone.

This does not make trait identity irrelevant. It means that trait identity by itself is insufficient for cross-lineage prediction under the present criterion. Comparative models that borrow information across clades should therefore allow lineage context to modify trait-specific phylogenetic structure rather than imposing one transferable signal parameter per trait.

## Relation to previous work

Ackerly (2009) showed that evolutionary rates of the same plant traits can differ markedly among clades. The present study therefore should not claim that clade heterogeneity is novel.

The advance is the crossed predictive formulation:

- repeated measurement of the same traits across many independent families;
- explicit family-blocked prediction of portability;
- explicit cross-trait family repeatability;
- common outcome-blind qualification before real effects.

Münkemüller et al. (2012) emphasized that phylogenetic-signal metrics differ in behavior and interpretation. This study likewise treats its memory gradient as a specific estimand rather than a universal replacement for K, lambda, or evolutionary-rate models.

## Figure plan

### Figure 1 — Crossed design and three questions

A family × trait incidence matrix for the 201 qualified systems, with diagrams showing:
- trait repeatability,
- held-out-family trait portability,
- cross-trait family repeatability.

### Figure 2 — Observed memory gradients

Heatmap or dot matrix of S3 rho for all 201 systems, ordered by family and trait.

Do not use the ordering to generate new inferential clusters.

### Figure 3 — Triangulation

Three aligned panels:
- repeatability shares with bootstrap intervals;
- S3/prune portability gains with permutation null intervals;
- conditional family repeatability with bootstrap interval and the predeclared 0.10 reference.

### Figure 4 — Backbone sensitivity

S3 versus prune-only rho for all systems; report the descriptive Spearman correspondence (0.832) and show the 1:1 line.

## Abstract skeleton

Phylogenetic signal is often treated as a property of a trait, yet the same trait can evolve differently among clades. We asked whether phylogenetic memory measured for a plant trait is transferable among lineages. Using BIEN trait data and a prospectively qualified crossed matrix of 201 family × trait systems spanning 45 families and 12 traits, we quantified memory-loss strength as the association between patristic separation and trait-state dissimilarity. Three separately preregistered analyses converged on a context-dependent picture. Family identity accounted for an estimated 15% of crossed variation, trait identity 4%, and approximately 81% remained unresolved at the system/residual level; no dominance comparison was made. In leave-one-family-out prediction, the same trait measured in other families did not outperform a global baseline (S3 gain -0.024, p=0.091; prune-only gain -0.032, p=0.193). Conversely, after trait-specific means were removed, family identity retained an estimated cross-trait repeatability of 0.183 (95% CI 0.029–0.337; prune-only 0.168), though uncertainty spanned a predeclared 10% practical reference. Thus phylogenetic memory is not a robustly portable intrinsic property of trait identity across plant families; instead, it is largely family × trait specific with a modest recurring lineage context.

## Discussion sequence

1. Distinguish within-lineage phylogenetic memory from cross-lineage portability.
2. Explain why clade-dependent evolutionary regimes are compatible with real signal inside each clade.
3. Interpret the modest family repeatability as lineage context, not continuous deep-phylogeny covariance.
4. Emphasize that most variation remains unresolved at the system/residual level; do not equate residual variance with a proven family × trait interaction.
5. Relate to clade heterogeneity in evolutionary rates and signal.
6. Discuss implications for comparative ecology: trait-specific phylogenetic priors learned in one clade should not automatically be exported to another.
7. Limitations: BIEN measurement heterogeneity, family scale, S3 taxonomic insertion, Spearman memory gradient rather than evolutionary-rate parameter.

## Hard nonclaims

- Do not say family effects dominate trait effects.
- Do not say trait effects are zero.
- Do not say family repeatability exceeds 10% with high confidence.
- Do not infer a mechanism for family context.
- Do not revive spatial-turnover conclusions.
- Do not call rho a decay rate or timescale.
