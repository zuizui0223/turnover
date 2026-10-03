# Novelty audit — Plant trait phylogenetic memory spectrum

Status: literature positioning drafted before real family x trait memory-loss effects are opened.

## Closest conceptual precedent

Ackerly (2009, PNAS; DOI 10.1073/pnas.0901635106) explicitly argued for comparing phenotypic evolutionary rates among traits and clades. The empirical demonstration estimated rates for three functional traits (plant height, leaf size, seed size) across four to six woody plant clades. This is the clearest conceptual ancestor of the present question.

The present design differs in three structural ways:

1. It treats **family and trait as crossed replicate axes** rather than presenting a small collection of clade-specific rate estimates.
2. It estimates one common effect definition, phylogenetic memory-loss rho, across a prospectively qualified family × trait graph.
3. It directly partitions variation in that effect into **family identity versus trait identity** using crossed random effects.

The biological question is therefore not simply whether traits differ in phylogenetic signal or whether clades differ in evolutionary rate, but which identity carries the portable information about evolutionary memory.

## Multi-trait phylogenetic-signal precedent

Zheng et al. (2009, Functional Ecology; DOI 10.1111/j.1365-2435.2009.01596.x) developed multivariate tests for phylogenetic signal and trait correlation, applying them to 13 ecophysiological traits in nine Manglietia species. The work shows that groups of traits can share or differ in phylogenetic signal and that measurement error matters.

That design is **many traits within one narrow lineage**, not repeated family × trait cells across many independent families. It therefore does not estimate a trait-versus-lineage variance architecture.

## Evidence that clade context matters

Ackerly (2009) found that height and leaf-size evolutionary rates differed by orders of magnitude among several woody clades, including exceptionally rapid rates in Hawaiian radiations. This is direct precedent for lineage dependence of trait evolution.

Reviews of phylogenetic conservatism also note that a trait can show signal at broad scales but be labile within particular clades, and that repeated tests of the same trait in different clades remain uncommon. This motivates treating lineage identity as a competing source of repeatable structure rather than as nuisance heterogeneity.

## Evidence that trait identity matters

Many studies compare phylogenetic signal or half-life among traits within one clade or one broad tree. Examples include:

- Ackerly & related leaf-economics analyses comparing different leaf traits;
- Zheng et al. comparing ecophysiological trait groups;
- OU/half-life studies where plant size, leaf traits, reproductive traits or niches show different persistence times.

These establish that traits differ in evolutionary persistence, but do not test whether those trait differences are portable across many lineages.

## Gap filled by the present study

The gap can be stated narrowly:

> Existing work shows both trait-to-trait differences in phylogenetic conservatism and clade-to-clade differences in trait evolution, but does not appear to ask, in a large crossed replication design, whether **trait identity or lineage identity explains more of the variation in a common phylogenetic-memory effect**.

The crossed design is important because a trait-only analysis confounds trait identity with the lineages in which that trait happens to be well sampled, while a lineage-only analysis confounds lineage evolutionary regime with which traits were measured.

## Methodological distinction

The canonical response here is not Pagel's lambda, Blomberg's K, or an OU alpha fitted independently and then compared despite different estimability. It is the same pairwise rank effect in every admitted system:

`rho = Spearman(patristic separation, trait-state dissimilarity)`.

The response is scale-invariant for continuous traits, extends to nominal categorical traits via 0/1 mismatch, and has an exact zero complete-permutation null mean. Known-truth geometry simulations are used before the biological effect is opened.

## Claims to avoid

Do not claim that no previous study has ever compared traits among clades. Ackerly (2009) clearly did.

Do not claim that this is the first multivariate analysis of phylogenetic signal. It is not.

The defensible novelty claim is the **large crossed trait × lineage variance decomposition of a common prospectively qualified memory-loss effect**.
