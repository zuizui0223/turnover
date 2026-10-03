# Synthesis — phylogenetic trait memory is context-dependent across plant families

Status: **post-outcome integrative synthesis**. This document introduces no new inferential test. It combines three analyses that were independently frozen and qualified before their real memory-loss effects were opened.

## Shared empirical base

All three analyses use the exact same outcome-blind core:

- 201 family × trait systems
- 45 vascular-plant families
- 12 continuous traits
- every system passed temporal support, semantic validity, S3/prune-only phylogeny crosswalk, and known-truth geometry informativeness

The three independent real-effect pipelines reproduce the same 201 effects exactly:

- maximum absolute difference in S3 rho: **0**
- maximum absolute difference in prune-only rho: **0**
- maximum absolute difference in the reused S3 informativeness lambda: **0**

The observed memory gradient itself is common but heterogeneous. Across 201 systems, S3 rho has mean 0.093, median 0.053 and is positive in 75% of systems. Prune-only rho is strongly concordant with S3 (Spearman 0.832).

## Three prospective questions

### 1. How much is repeatable by family and by trait?

Crossed REML decomposition on the fixed 201 systems:

- family repeatability: **0.150** (95% bootstrap CI 0.020–0.286)
- trait repeatability: **0.043** (0–0.134)
- residual / family-by-trait-specific share: **0.806** (0.660–0.952)

Prune-only gives family 0.148, trait 0.021 and residual 0.831.

The prior variance-ratio study failed its precision gate before real effects were opened, so **these components must not be converted into a family>trait dominance claim**.

What they do show is that most heterogeneity is system-specific, while a family component is estimable and the trait component is weak/uncertain.

### 2. Does trait identity transfer to a new family?

The separate portability study leaves each family out completely and predicts its systems from the same traits in other families.

S3:

- portability gain: **-0.024**
- blocked-permutation p: **0.091**

Prune-only:

- gain: **-0.032**
- p: **0.193**

Both fail the predeclared robust criterion.

The important negative result is not “no phylogenetic memory.” Many individual systems have positive rho. It is that **knowing the trait label and its memory in other families does not robustly improve prediction for a new family**.

### 3. Is there a recurring family context after trait means are removed?

A third analysis gives every trait its own fixed mean and asks whether family identity still repeats across traits:

`rho ~ 0 + trait_name + (1 | family)`

Conditional family repeatability:

- S3: **0.183** (95% bootstrap CI 0.029–0.337)
- prune-only: **0.168**
- leave-one-trait / leave-one-family estimates: **0.121–0.227**

The interval spans the predeclared 10% practical reference, so the frozen interpretation remains **uncertain relative to 10%**. It nevertheless supports a stable estimated family-level component rather than a result driven by one trait or one family.

## Integrated biological conclusion

The most defensible synthesis is:

> **Phylogenetic memory is not a portable intrinsic property of a plant trait. Its strength is strongly context-dependent at the family × trait level, with a modest recurring family-level component across traits.**

This is an asymmetry of **generalization**, not a claim that family variance is statistically larger than trait variance.

The data therefore argue against treating “the phylogenetic conservatism of trait X” as a single transferable constant across plant clades. A memory estimate learned for one trait in one set of lineages can be real within those systems yet fail to transport to another family.

## Why this is different from prior comparative work

Classic phylogenetic-signal studies quantify whether related species resemble one another, and different signal statistics can answer different questions. The present response instead measures a within-family **memory gradient**: the monotonic increase of trait-state dissimilarity with patristic separation.

Ackerly (2009) already showed that evolutionary rates of the same plant functional traits can differ dramatically among clades. The new contribution here is not “clades differ.” It is the crossed, predictive question:

1. does the same trait carry a reusable memory signature across independent families?
2. after trait means are removed, does family identity recur across different traits?

The first answer is no under the frozen portability criterion; the second shows a modest estimated repeatable component.

## Manuscript-level claim hierarchy

### Primary

**Trait-specific phylogenetic-memory estimates do not robustly transfer across plant families.**

### Supporting

**Family identity retains a modest cross-trait repeatable component, while most family × trait variation remains system-specific.**

### Hard nonclaims

Do not say:

- family effects dominate trait effects;
- trait effects are absent;
- family repeatability confidently exceeds 10%;
- the family component has a known ecological or genetic cause;
- failed spatial qualification means spatial turnover is biologically weak.

## Suggested title family

Most conservative:

**Cross-lineage prediction reveals limited portability of phylogenetic trait memory**

More conceptual:

**Phylogenetic trait memory is context-dependent across plant families**

If emphasizing the paired evidence:

**Trait memory fails to transfer across plant families despite repeatable lineage context**

The third title should be used cautiously because the conditional family interval spans the frozen 10% practical reference.


## Publication boundary

The completed empirical paper should be scoped as a **temporal comparative plant-trait study**, not as a partially successful version of the original time × space turnover programme.

The original generalized programme remains valuable as the prospective qualification history that produced the temporal core, but its interaction and spatial arms closed before biological outcomes. Their failures are therefore not biological results to be combined with the 201-system temporal analysis.

For publication, the clean boundary is:

- **Main paper:** phylogenetic memory gradients across 201 family × trait systems; cross-lineage portability; crossed repeatability; conditional lineage context.
- **Methods / Supplement:** prospective source, semantic, phylogeny and known-truth informativeness qualification; exact-null derivation; S3/prune-only sensitivity.
- **Do not frame as a result:** the failed generalized interaction/spatial source routes.
- **Future/replication:** independently qualified AusTraits analysis, if it passes all source-native gates.

This boundary keeps the ecological question recognizable: **can the evolutionary memory learned for a trait be transported to another lineage?**
