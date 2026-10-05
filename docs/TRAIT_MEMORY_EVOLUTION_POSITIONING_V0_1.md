# Submission positioning — Evolution

Checked against current *Evolution* author guidance on 2026-10-05.

## Recommended target

**Evolution — Original Article**

Working title:

**Phylogenetic trait memory is lineage-contingent rather than trait-intrinsic across plant families**

Alternative, more predictive:

**Cross-lineage prediction reveals weak portability of phylogenetic trait memory**

## Why Evolution is the best current fit

*Evolution* asks for important, original empirical studies that bear on significant questions in evolutionary biology and materially extend understanding rather than merely reproduce a known phenomenon in another taxon.

The manuscript should therefore not be framed as:
- another demonstration that phylogenetic signal differs among clades;
- a new phylogenetic-signal index;
- a methods paper about Mantel-style statistics;
- a failed prediction exercise;
- a claim that family effects dominate trait effects.

The evolutionary question is:

> **At what biological level is the strength of phylogenetic trait memory repeatable and generalizable?**

The three hypotheses give a direct answer:

1. **Trait-intrinsic memory:** the same trait should carry a reusable memory strength into an unseen family — not supported.
2. **Family-context memory:** the same family should show a recurring memory context across different traits — modestly supported and robust to several artifact explanations.
3. **Deep hierarchical inheritance:** family context should itself vary smoothly along deeper family phylogeny — not supported in the complementary exploratory test.

The key result is therefore a scale asymmetry in evolutionary generalization, not merely heterogeneous phylogenetic signal.

## Strongest editor-facing result

Across a prospectively qualified crossed dataset of 201 family × trait systems, the family component remains close to 15% after species-level sampling uncertainty is separated and after geometry, BIEN provenance, trait-domain collapse, and a predeclared correlated-trait null are considered.

Yet trait identity provides essentially no robust held-out-family predictive information:
- arithmetic trait means: gain -0.024 (S3), -0.032 (prune-only);
- training-only BLUPs: +0.006 and -0.0048.

Thus **lineage context is repeatable while trait-specific memory is not meaningfully portable**.

## What robustness changed

The robustness programme strengthens the family-context result but weakens two earlier claims.

### Dropped
- “Most variation is system-specific.”
- “Trait identity is anti-portable.”

### Retained
- a modest family-level repeatable component;
- little cross-lineage trait-level portability.

### Added
- species-bootstrap sampling error explains roughly one quarter of typical total variation;
- correlated/redundant traits do not fully explain the family component;
- shrinkage shows that the portability failure reflects little transferable trait signal rather than a strong prediction penalty.

## Novelty boundary

Prior work already establishes:
- trait-specific differences in phylogenetic signal;
- clade-specific differences in signal and evolutionary rate;
- lineage-dependent phylogenetic imputation accuracy;
- limitations of Mantel-style phylogenetic-signal testing.

The defensible novelty is narrower:

> **The study treats the estimated strength of phylogenetic memory itself as an object of cross-lineage prediction, and contrasts trait-to-lineage portability with lineage-to-trait repeatability on the same crossed family × trait graph.**

The observed asymmetry is the new biological result.

## Desk-rejection risks

### Risk 1 — “This is just clade heterogeneity in phylogenetic signal”
Response: lead with the held-out-family generalization hypothesis rather than the variance decomposition.

### Risk 2 — “The statistic is a Mantel correlation”
Response: explicitly call rho a distance-decay descriptor, not a generic superior signal test; distinguish it from K and lambda; emphasize prospective geometry qualification and species-level bootstrap uncertainty.

### Risk 3 — “Family effect is an artifact of correlated traits or data provenance”
Response: make the correlated-trait null and the geometry/provenance robustness panel a primary figure.

### Risk 4 — “Negative portability is just a poor predictor”
Response: show the training-only BLUP result. Shrinkage eliminates most negative gain but still leaves essentially zero robust portability.

### Risk 5 — “No mechanism”
Response: do not pretend there is one. The paper is about the **scale of evolutionary generalization**. Biological mechanism is the main future question.

### Risk 6 — raw versus log trait scale
Response: report the frozen all-201 log sensitivity as HOLD because of nonpositive species medians. Do not introduce an offset after outcomes are known. Scope the inference to the predefined raw-scale distance-decay descriptor.

## Journal hierarchy

### 1. Evolution
Best balance of ambition and fit. Its scope explicitly welcomes important original empirical studies bearing on significant evolutionary questions.

### 2. Journal of Evolutionary Biology
Strong fallback. Its current scope explicitly welcomes robust negative results when they provide new, generalizable insight. The weak-portability result fits naturally.

### 3. Evolution Letters
Reach option only. The journal expects work of outstanding originality or broad field-changing interest and has a concise ~5,000-word Letter format. Without a mechanism for the family component and with unresolved raw/log-scale robustness, desk-rejection risk is substantially higher.

## Manuscript architecture for Evolution

1. **Introduction:** “Is evolutionary memory a property of a trait or of the lineage in which it evolves?”
2. **Methods:** crossed 45-family × 12-trait design, prospective geometry qualification, distance-decay response, family-blocked prediction, robustness programme.
3. **Results:** H1 portability, H2 family context, sampling-error correction and artifact audits; H3 deep-family result clearly labelled complementary/post-outcome.
4. **Discussion:** evolutionary generalization scale, implications for borrowing phylogenetic priors across clades, metric boundary, unresolved mechanisms and raw/log limitation.

The manuscript should stay well below the current 7,500-word Original Article limit.
