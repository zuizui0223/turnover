# Novelty boundary v0.2 — lineage repeatability versus portability of phylogenetic trait memory

Checked against targeted literature through 2026-10-05.

## What is already known

### Phylogenetic signal differs among traits and clades

Blomberg, Garland & Ives (2003) established that phylogenetic signal differs among broad trait classes and introduced K specifically to support comparisons across traits and trees.

Münkemüller et al. (2012) showed that phylogenetic-signal metrics differ in behaviour and that signal can vary strongly among phylogenies and clades.

Empirical plant literature has repeatedly shown that the same or related functional traits can be conserved in one lineage and labile in another. Reviews explicitly note cases such as specific leaf area showing signal in one genus but not others.

Therefore **do not claim novelty for lineage-specific or trait-specific phylogenetic signal**.

### Phylogenetic prediction can vary among lineages

Molina-Venegas et al. (2018, *Ecography*, DOI 10.1111/ecog.03480) studied among-lineage variability in phylogenetic trait imputation. Their simulations and cross-validation showed that prediction accuracy varies among phylogenetic tips and depends on signal strength and terminal branch length.

Molina-Venegas (2024, *Methods in Ecology and Evolution*, DOI 10.1111/2041-210X.14198) argues that phylogenetic information should not be trusted for imputation without validating whether it is minimally predictive.

Debastiani et al. (2021, *Ecological Informatics*, 63:101315) likewise showed that phylogeny can improve trait imputation but that performance depends on trait conservatism and trait correlations.

Therefore **do not claim novelty for the general proposition that phylogenetic borrowing can fail or that predictive value is lineage-dependent**.

## What is different here

The response being transferred is not the trait value itself.

For each family × trait system, the response is an estimate of **phylogenetic memory strength**: the degree to which trait dissimilarity increases with patristic separation.

The paper asks a second-order predictive question:

> If the phylogenetic memory of trait t is learned in other families, does trait identity predict the memory strength of t in a completely unseen family?

This treats evolutionary memory strength itself as the object whose portability is tested.

The empirical result is asymmetric:

- family repeatability remains around 0.15 and exceeds a conservative correlated-trait zero-family-effect null;
- trait repeatability is small;
- unshrunk trait means are mildly harmful predictors;
- shrinkage removes most of that harm but leaves essentially zero robust cross-family gain.

Thus **a signal can be repeatable with respect to lineage context without being portable as a trait-specific signature**.

Targeted searches did not identify a prior plant comparative study that explicitly estimates family × trait phylogenetic-signal strengths on a crossed graph and then uses held-out-family prediction to test whether the signal strength of the same trait transfers across lineages. This should be phrased cautiously as a targeted-search result, not proof of absence.

## Metric boundary: pairwise rho is not K or lambda

Harmon & Glor (2010, *Evolution*, DOI 10.1111/j.1558-5646.2010.00973.x) showed poor statistical performance of Mantel tests for phylogenetic comparative analyses and recommended avoiding them when standard comparative methods are available.

Hardy & Pavoine (2012, *Evolution*, DOI 10.1111/j.1558-5646.2012.01623.x) showed that Mantel-type performance depends strongly on the chosen phylogenetic and phenotypic distance metrics and that measurement error can materially affect both Mantel and K-based inference.

The present rho should therefore **not** be presented as a superior generic phylogenetic-signal statistic or as interchangeable with Blomberg's K or Pagel's lambda.

Its role is narrower:

- K measures signal relative to a Brownian expectation.
- Pagel's lambda is a covariance/tree-transformation parameter and is rate-independent.
- the present rho measures a monotone **distance-decay pattern in trait dissimilarity** over all pairs.

The paper's biological question is about whether that same distance-decay summary is transferable among lineages, not about which phylogenetic-signal statistic is universally best.

The known-truth qualification and the new species-bootstrap SE analysis are therefore essential: they characterize the estimator on the exact admitted geometries rather than relying on pair counts as independent observations.

## Important 2025 warning for interpretation

Pearse et al. (2025, *Global Ecology and Biogeography*, DOI 10.1111/geb.70012) emphasize that estimates of Pagel's lambda can differ across species subsets even when the underlying evolutionary process is invariant. More generally, differences in estimated phylogenetic signal across clades need not imply different evolutionary mechanisms.

This paper should adopt the same caution.

The surviving family component supports **repeatable lineage context in the observed summary**, but it does not identify family-specific selection regimes, niche conservatism, or distinct evolutionary processes.

## Strongest defensible novelty statement

> **Phylogenetic signal is usually treated as a property to estimate within a clade. We instead ask whether the estimated strength of evolutionary memory for a named trait is itself transferable across clades. In a crossed dataset of 45 plant families and 12 traits, lineage-level repeatability persists after measurement-error and trait-redundancy audits, yet trait identity supplies almost no robust held-out-family predictive gain.**

This is a predictive generalization result, not a new phylogenetic-signal metric and not a new ecological mechanism.

## Practical implication

The result is directly relevant to workflows that borrow evolutionary information across lineages.

A trait may show phylogenetic structure in many clades without having a stable, transferable **amount of signal** across those clades. Therefore, using an estimated signal strength, prior, or evolutionary covariance learned in one lineage as a plug-in assumption for another should be validated out-of-lineage rather than justified by the trait label alone.

## Current impact assessment

- **Novelty:** moderate, but sharper after robustness. The family-repeatability/trait-portability asymmetry is more distinctive than the original negative-gain result.
- **Biological importance:** moderate. It changes how lineage versus trait identity should be interpreted in comparative plant trait evolution.
- **Methodological importance:** moderate. Family-blocked prediction turns descriptive variation in phylogenetic signal into an explicit generalization test.
- **Mechanistic depth:** still limited. No evolutionary process generating the family component is identified.
- **Scope:** temporal comparative macroevolution only; the original time × space ecological question remains unresolved.

## Key literature

- Blomberg SP, Garland T Jr, Ives AR. 2003. *Evolution* 57:717–745. DOI 10.1111/j.0014-3820.2003.tb00285.x.
- Harmon LJ, Glor RE. 2010. *Evolution* 64:2173–2178. DOI 10.1111/j.1558-5646.2010.00973.x.
- Hardy OJ, Pavoine S. 2012. *Evolution* 66:2614–2621. DOI 10.1111/j.1558-5646.2012.01623.x.
- Münkemüller T et al. 2012. *Methods in Ecology and Evolution* 3:743–756. DOI 10.1111/j.2041-210X.2012.00196.x.
- Swenson NG. 2014. *Ecography* 37:105–110. DOI 10.1111/j.1600-0587.2013.00528.x.
- Molina-Venegas R et al. 2018. *Ecography* 41:1740–1749. DOI 10.1111/ecog.03480.
- Debastiani VJ, Bastazini VAG, Pillar VD. 2021. *Ecological Informatics* 63:101315.
- Molina-Venegas R. 2024. *Methods in Ecology and Evolution* 15:456–463. DOI 10.1111/2041-210X.14198.
- Pearse WD et al. 2025. *Global Ecology and Biogeography*. DOI 10.1111/geb.70012.
