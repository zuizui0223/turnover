# Trait-memory context synthesis v0.2 — memory is lineage-contingent, not trait-intrinsic

Status: **post-robustness integrative synthesis**.

This document supersedes the interpretation in v0.1 but does not alter any historical result. It integrates the prospectively qualified 201-system temporal analyses with the frozen v0.3 robustness programme.

## Central question

**Is the strength of phylogenetic memory a transferable property of a named trait, or is it contingent on the lineage in which that trait evolves?**

A stronger hierarchical version asks:

1. Does the same trait carry a reusable memory signature across families?
2. Does the same family carry a recurring memory context across different traits?
3. Is that family context itself smoothly inherited across deeper family phylogeny?

## Answer

The evidence is asymmetric.

**Trait → unseen family:** essentially no robust transfer.

**Family → other traits:** a modest repeatable component persists.

**Family context → deeper family phylogeny:** no detectable smooth organization in the complementary post-outcome check.

The resulting pattern is:

> **Phylogenetic trait memory is lineage-contingent: family context repeats across traits, but the memory strength of a named trait is not reliably portable across families, and the recurring family context is not detectably organized as a smooth deep-phylogenetic gradient.**

## Evidence 1 — family repeatability survives measurement-error correction

Original S3 crossed-lmer shares were family 0.150, trait 0.043, residual 0.806.

The v0.3 species-bootstrap gives a median system-level rho SE of 0.058 for S3 and 0.071 for prune-only.

Using those sampling variances in a crossed meta-analysis, the S3 point decomposition of typical total variance is approximately:

- family: **15.1%**;
- trait: **5.7%**;
- residual between-system heterogeneity: **54.9%**;
- sampling error: **24.2%**.

Prune-only is approximately 14.0%, 2.2%, 58.6%, and 25.3%.

Thus the family point share is almost unchanged, whereas the original 80.6% residual is split into substantial sampling error plus residual heterogeneity.

The two-way family × trait cluster bootstrap completed 500/500 refits, but family and system heterogeneity-share intervals overlap strongly. No component should be called dominant.

## Evidence 2 — family repeatability is not explained by obvious design artifacts

The family share is stable across multiple independent audits:

- unadjusted S3 R_family = **0.150**;
- species-count adjusted = **0.154**;
- species count + prune fraction + calibration geometry adjusted = **0.146**;
- source-composition adjusted = **0.149**;
- citation-composition adjusted = **0.147**;
- five-domain trait collapse = **0.144**;
- leave-one-trait/family repeatability estimates remain in the same broad range.

The predeclared correlated-trait zero-family-effect null is especially important.

It preserves strong dependence among redundant trait outcomes and the exact sparse family × trait graph but simulates no family main effect.

Observed family repeatability exceeds that null:

- S3: p = **0.017**;
- prune-only: p = **0.009**.

The family component therefore survives the specific explanation that it is merely a mechanical consequence of redundant trait labels observed on the same family geometry.

This remains a pattern-level result, not identification of a causal family mechanism.

## Evidence 3 — trait identity contains little transferable information

The frozen arithmetic trait-mean predictor performed slightly worse than a global training mean:

- S3 gain = −0.024;
- prune-only gain = −0.032.

But BLUP shrinkage changes the interpretation:

- S3 gain = **+0.006**;
- prune-only gain = **−0.0048**.

The negative penalty mostly disappears, but robust positive portability still does not emerge.

Training trait variance is small relative to residual variation:

- S3 median training trait variance ≈0.00090 versus residual ≈0.0168;
- prune-only ≈0.00060 versus ≈0.0247.

Therefore the correct conclusion is **little transferable trait-level signal**, not anti-portability.

## Evidence 4 — family context is not a deep-phylogenetic continuum

A complementary post-outcome analysis computed family context scores after removing trait means and asked whether differences in context increased with patristic distance among the 45 family crowns.

The association is essentially zero:

- S3 rho = −0.015, permutation p = 0.822;
- prune-only rho = −0.011, p = 0.871;
- mean-score and leave-one-trait variants are similarly near zero.

This result is exploratory rather than prospectively primary, but it sharpens the scale of the pattern.

The recurring family context behaves more like a **family-specific mosaic** than a single smoothly inherited deep-phylogenetic regime.

## Evidence 5 — raw-scale generality remains unresolved

The frozen natural-log sensitivity cannot be completed on the identical 201-system population because:

- 25 S3 systems contain at least one nonpositive species median;
- 18 prune-only systems do so.

No offset, signed-log transform, or post-outcome system filtering is introduced.

The pairwise absolute-difference memory gradient must therefore be described as a **raw-scale distance-decay descriptor whose multiplicative-scale robustness is unresolved**.

## What is new versus prior literature

Already known:

- phylogenetic signal differs among traits;
- signal differs among clades;
- the same trait can evolve at very different rates in different clades;
- phylogenetic imputation accuracy can vary among lineages and individual tips;
- different phylogenetic-signal statistics answer different questions.

The distinctive contribution is the **crossed generalization test on the strength of phylogenetic memory itself**.

The response being predicted is not a trait value. It is the estimated strength of the within-lineage phylogenetic distance–dissimilarity relationship.

The study asks whether that evolutionary-memory summary can be borrowed by trait name across completely held-out families, and then asks the converse: whether family identity recurs across different traits.

The observed asymmetry — family repeatability without trait portability — is the core result.

## General principle

> **A trait can repeatedly show phylogenetic structure without having a stable amount of phylogenetic memory that is transferable across lineages.**

This matters whenever comparative analyses borrow trait-specific evolutionary priors, covariance structures, or expectations from one clade to another.

Cross-lineage borrowing should be validated as a prediction problem rather than justified by the trait label alone.

## Statistic boundary

The response is:

`rho = Spearman(patristic distance, pairwise absolute trait difference)`.

It is a Mantel-like distance-matrix effect descriptor, not a claim to replace Blomberg's K or Pagel's lambda.

Harmon & Glor's critique of Mantel tests means this rho should not be sold as a universally efficient test of phylogenetic signal.

The present study instead:

- fixes the descriptor before outcomes;
- verifies known-truth recoverability on each admitted geometry;
- treats species, not pairwise distances, as the resampling unit for SE;
- uses rho only as the common response for the portability question.

Any conclusion is conditional on this explicitly defined memory-gradient statistic.

## Revised claim hierarchy

### Primary

**The strength of phylogenetic trait memory is not a robust trait-intrinsic signature transferable across plant families.**

### Co-primary supporting pattern

**Family identity carries a repeatable cross-trait component that survives measurement-error, geometry, provenance, trait-domain, and correlated-trait-null audits.**

### Secondary

**The recurring family context is not detectably arranged along deeper family phylogenetic distance.**

### Limitation

**Raw-versus-log scale robustness is unresolved on the identical 201-system population.**

## Claims to drop

- “Most phylogenetic memory is system-specific.”
- “Trait identity is anti-portable.”
- “Family context dominates trait identity.”
- “The family component is a demonstrated biological mechanism.”
- “The same raw-scale result would hold after multiplicative trait transformation.”
- “This resolves the original time × space turnover question.”

## Working title

**Phylogenetic trait memory is lineage-contingent rather than trait-intrinsic across plant families**

Alternative:

**Cross-lineage prediction reveals weak portability of phylogenetic trait memory**

More conceptual:

**Is phylogenetic conservatism itself conserved across lineages?**

The third title is best treated as a framing question rather than a literal claim that the present rho equals all conventional definitions of phylogenetic conservatism.
