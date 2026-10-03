# Manuscript v0.2 — Cross-lineage portability of phylogenetic trait memory

## Working title

Cross-lineage prediction reveals limited portability of phylogenetic trait memory across plant families

Alternative: Phylogenetic trait memory is context-dependent across plant families.

Avoid titles that say lineage effects dominate trait effects, trait identity is absent, or family-specific mechanism.

## One-sentence result

The memory gradient associated with a named plant trait does not robustly improve prediction of that trait's memory gradient in a completely held-out family, while family identity retains a modest recurring cross-trait component and most remaining variation is unresolved at the system/residual level.

## Conceptual gap

Phylogenetic signal and evolutionary rates are commonly estimated within a clade, and both are known to depend on trait, clade and phylogenetic scale. Predictive phylogenetic modelling is also well established.

The unresolved question here is narrower and second-order: is a trait's estimated phylogenetic memory itself portable across independent lineages?

This is not a trait-value prediction problem. Each observation in the final analysis is already a family-specific macroevolutionary summary: the association between within-family patristic separation and trait-state dissimilarity.

The study separates within-family memory, cross-family portability, and cross-trait lineage context.

## Data and prospective qualification

The empirical core was fixed before real memory-loss effects were opened:

- 201 family x trait systems;
- 45 vascular-plant families;
- 12 continuous traits;
- BIEN 4.2.8;
- pinned V.PhyloMaker2 / GBOTB.extended.TPL;
- every system passed support, semantic validity, S3 plus prune-only crosswalk, and known-truth geometry informativeness.

Three separately authorized execution routes reproduce the same 201 S3 and prune-only effects exactly; maximum numerical difference is zero.

The original generalized time-space programme and the later trait-versus-lineage variance-ratio question both remain terminal pre-outcome HOLD. Neither was relaxed to generate the present claims.

## Memory-gradient estimand

For every admitted family x trait system, species state is the median valid trait measurement, trait-state dissimilarity is absolute species-state difference, evolutionary separation is all unordered patristic distances, and memory-loss rho is Spearman(separation, dissimilarity).

The exact complete-label permutation-null mean is zero.

Larger positive rho means a stronger monotonic loss of trait similarity with phylogenetic separation. It is not a time-calibrated decay rate, Brownian variance parameter, Blomberg K or Pagel lambda.

Across 201 systems, S3 rho has mean 0.093, median 0.053, range -0.183 to 0.709, and is positive in 74.6% of systems. S3 and prune-only estimates are strongly concordant (Spearman 0.832).

## Result 1 — Repeatability decomposition

| Component | S3 share | 95% bootstrap CI | Prune-only |
|---|---:|---:|---:|
| Family | 0.150 | 0.020–0.286 | 0.148 |
| Trait | 0.043 | 0–0.134 | 0.021 |
| Residual / unresolved system-level | 0.806 | 0.660–0.952 | 0.831 |

The failed pre-outcome variance-ratio study forbids a formal claim that family effects exceed trait effects.

The residual term must not be interpreted as pure biological family x trait interaction. It also contains system-level estimation error, measurement heterogeneity and model residual.

The correct inference is that most variation is not repeatable as a family main effect or trait main effect.

## Result 2 — Trait memory is not robustly portable to a held-out family

Family-blocked prediction leaves one family out completely. The trait predictor is the mean rho for the same trait among training families; the baseline is the mean rho across all training systems.

S3: gain = -0.0242, SSE same-trait = 4.251, SSE global = 4.151, blocked-permutation p = 0.091.

Prune-only: gain = -0.0324, SSE same-trait = 6.184, SSE global = 5.990, p = 0.193.

The predeclared positive result required gain > 0 and p <= 0.05 on both tree treatments. It fails.

This does not imply zero within-family phylogenetic memory or zero trait repeatability. It means that trait identity does not provide a robust prediction advantage for a new family under the frozen family-blocked criterion.

## Result 3 — Family-level lineage context recurs across traits

A separate prospectively qualified model removes trait means first: rho ~ 0 + trait_name + (1 | family).

Conditional family repeatability:

- S3 = 0.183;
- 95% bootstrap CI = 0.029–0.337;
- prune-only = 0.168;
- leave-one-trait / leave-one-family estimates = 0.121–0.227.

The CI spans the predeclared 0.10 practical reference, so classification relative to 10% remains uncertain.

The result supports an estimable family-level context shared across traits, not a family-specific mechanism. Because the model treats families as grouping levels rather than modelling covariance among family clades, deeper phylogenetic structure may contribute to this component.

## Integrated interpretation

The combined evidence supports a limited-portability, context-dependent architecture:

- phylogenetic memory can be real inside individual family x trait systems;
- the trait label alone is not a robust transferable predictor of that memory in an unseen family;
- family identity contains a modest recurring cross-trait component;
- most heterogeneity remains in an unresolved system-level/residual component.

The central distinction is between existence of phylogenetic memory and transportability of a memory estimate across clades.

## Relation to previous work

Ackerly (2009) already showed dramatic clade heterogeneity in evolutionary rates of the same plant traits. Graham, Storch & Machac (2018) formalized phylogenetic scale dependence.

Prediction itself is not novel. Guénard, Legendre & Peres-Neto (2013) argued that phylogenetic signal does not guarantee useful trait prediction and advocated predictive evaluation. Brown & Thomson (2018) emphasized predictive checks in evolutionary models, while Richard-Bollans & Silvestro (2026) showed that model-based methods can perform well for single-trait phylogenetic prediction.

The new contribution is the object and block of prediction: a within-family macroevolutionary memory statistic is learned repeatedly across a crossed family x trait matrix and tested for transfer to an entirely held-out lineage.

The paired family-repeatability analysis then asks the orthogonal question of whether lineage context recurs across traits after trait means are removed.

## Figure plan

Figure 1: crossed design and leave-one-family-out portability scheme.

Figure 2: observed S3 memory rho across the 201 fixed systems.

Figure 3: three-way triangulation — repeatability shares, portability gains/permutation nulls, conditional family repeatability with 0.10 reference.

Figure 4: S3 versus prune-only rho with 1:1 line and descriptive Spearman 0.832.

## Abstract v0.2

Phylogenetic signal is often summarized as a property of a trait, yet evolutionary dynamics can vary among clades and phylogenetic scales. We asked a predictive question: does a phylogenetic-memory estimate learned for the same plant trait in other families transfer to a completely held-out family? Using BIEN trait data and an outcome-blind qualified matrix of 201 family x trait systems spanning 45 families and 12 continuous traits, we measured memory loss as the Spearman association between patristic separation and trait-state dissimilarity. Family-blocked prediction showed no robust portability advantage for trait identity over a training-set global mean (S3 gain = -0.024, p = 0.091; prune-only gain = -0.032, p = 0.193). In crossed REML decomposition, family identity accounted for an estimated 0.150 of total variance (95% bootstrap CI 0.020–0.286), trait identity 0.043 (0–0.134), and 0.806 remained in the residual/system-level component; a prospectively failed precision gate precluded a family-versus-trait dominance claim. In a separate qualified model that removed trait-specific means, conditional family repeatability was 0.183 (0.029–0.337; prune-only 0.168), although its interval spanned a predeclared 0.10 practical reference. Thus within-family phylogenetic memory does not imply a robustly portable trait-specific memory signature across plant families; instead, memory strength is context-dependent with a modest recurring family-level component.

## Hard nonclaims

- Do not say family effects dominate trait effects.
- Do not say trait effects are zero.
- Do not say 80.6% is pure family x trait biological interaction.
- Do not say family repeatability confidently exceeds 10%.
- Do not attribute the family component to a specific ecological or genetic mechanism.
- Do not treat families as phylogenetically independent causal units.
- Do not call rho a decay rate, timescale, K, lambda or Brownian rate.
- Do not revive the failed spatial-turnover programme.
