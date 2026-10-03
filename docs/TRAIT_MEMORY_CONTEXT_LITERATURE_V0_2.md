# Literature positioning v0.2 — portability and context dependence of phylogenetic trait memory

Status: post-outcome positioning only. No new empirical test or system selection is introduced here.

## What is already established

### Phylogenetic signal and evolutionary rate are not interchangeable

Ackerly (2009) showed directly that rates of evolution for the same plant functional trait can differ by orders of magnitude among clades. Clade heterogeneity in evolutionary tempo is therefore not new.

Münkemüller et al. (2012) showed that common phylogenetic-signal statistics differ in behavior and interpretation. The present memory-gradient rho is therefore treated as a specific estimand, not as a replacement for Blomberg's K, Pagel's lambda, or evolutionary-rate models.

Revell (2018) formalized likelihood-based comparisons of evolutionary rates among trees, clades and traits.

### Phylogenetic scale is itself context

Graham, Storch & Machac (2018) formalized phylogenetic scale dependence: an evolutionary attribute can vary among clades or scales such that conclusions at one phylogenetic extent need not extrapolate to another. This is conceptually close to the present result and means that the manuscript must not claim that context dependence itself is novel.

The family scale used here is one deliberately repeated grain. The analysis does not show that family is the uniquely correct phylogenetic scale and does not decompose the family component into deeper shared ancestry versus family-specific ecology/history.

### Prediction from phylogeny is not new

Guénard, Legendre & Peres-Neto (2013) explicitly argued that significant phylogenetic signal does not by itself guarantee useful prediction and proposed cross-validated predictive performance as a more direct criterion for phylogenetic modelling.

Brown & Thomson (2018) likewise emphasized predictive checks, cross-validation and absolute model performance in evolutionary biology.

Richard-Bollans & Silvestro (2026) showed that model-based phylogenetic methods can remain effective for single-trait prediction across a range of evolutionary scenarios.

Therefore this study must not claim novelty for using prediction or cross-validation in phylogenetic comparative biology.

## The narrower remaining gap

The unit being transferred here is not a species trait value.

For each family x trait system, the response is a within-family phylogenetic memory gradient: rho = Spearman(patristic separation, trait-state dissimilarity).

The portability question is then second-order: does knowing the memory gradient of trait X in other plant families improve prediction of the memory gradient of trait X in a completely held-out family?

This differs from predicting an unmeasured species' trait value from its relatives.

The study also asks the orthogonal crossed question: after every trait receives its own fixed mean memory gradient, is there a recurring family-level shift shared across multiple traits?

The contribution is the combination of these two generalization tests on one prospectively qualified crossed family x trait matrix.

## What the data support

### Cross-lineage trait portability

The same-trait predictor does not improve over a family-blocked training-set global mean under the predeclared robust criterion.

- S3 gain = -0.0242, blocked-permutation p = 0.091.
- prune-only gain = -0.0324, p = 0.193.

The correct language is limited or non-robust portability, not proof that trait identity contains zero repeatable information.

### Family-level context

After removing trait-specific means, estimated family repeatability is 0.183 (95% bootstrap CI 0.029–0.337), with prune-only 0.168 and leave-one-out estimates 0.121–0.227.

This supports an estimable recurring family-level component. Because families are treated as grouping levels rather than as tips in a second deep-family phylogeny, the component should be described as family-level lineage context, not a uniquely family-specific causal effect.

### Residual/system-level component

In the crossed REML decomposition, residual share is 0.806.

This quantity is not identifiable as pure family x trait interaction. It contains any true family x trait interaction plus system-level estimation error, measurement heterogeneity and model residual. The defensible statement is: most variation is not repeatable as a family main effect or a trait main effect and remains in the residual/system-level component.

Do not write that 80.6% is proven biological family x trait interaction.

## Precise novelty claim

The strongest defensible novelty is: a trait can exhibit phylogenetic memory within many plant families without carrying a robustly portable memory signature across families; at the same time, family identity retains a modest recurring cross-trait component.

The study therefore separates within-clade memory from cross-clade transportability of that memory.

## Central references

- Ackerly, D.D. 2009. PNAS 106:19699–19706. doi:10.1073/pnas.0901635106.
- Münkemüller, T. et al. 2012. Methods in Ecology and Evolution 3:743–756. doi:10.1111/j.2041-210X.2012.00196.x.
- Guénard, G., Legendre, P. & Peres-Neto, P. 2013. Methods in Ecology and Evolution 4:1120–1131. doi:10.1111/2041-210X.12111.
- Graham, C.H., Storch, D. & Machac, A. 2018. Global Ecology and Biogeography 27:175–187. doi:10.1111/geb.12686.
- Revell, L.J. 2018. Methods in Ecology and Evolution 9:994–1005. doi:10.1111/2041-210X.12977.
- Brown, J.M. & Thomson, R.C. 2018. Annual Review of Ecology, Evolution, and Systematics. doi:10.1146/annurev-ecolsys-110617-062249.
- Richard-Bollans, A. & Silvestro, D. 2026. Methods in Ecology and Evolution 17:1032–1041. doi:10.1111/2041-210X.70258.
