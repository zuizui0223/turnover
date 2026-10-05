# Trait-memory statistic positioning v0.3

## What the statistic is

The temporal response is

`rho = Spearman(patristic distance, pairwise trait dissimilarity)`.

For continuous traits, dissimilarity is the absolute difference between species-level median states. The statistic is therefore a distance-matrix association and is Mantel-like in structure, although the present study uses rho as an effect-size descriptor rather than relying on a classical Mantel p-value.

## What it is not

It is **not** presented as:
- a generally superior estimator of phylogenetic signal;
- a replacement for Pagel's lambda, Blomberg's K, Abouheif's Cmean or model-based comparative methods;
- a direct estimator of an evolutionary-process parameter.

Harmon & Glor (2010, Evolution 64:2173–2178; DOI 10.1111/j.1558-5646.2010.00973.x) showed poor statistical performance of Mantel tests in phylogenetic comparative analyses, including low power for phylogenetic-signal detection relative to alternatives.

Münkemüller et al. (2012, Methods in Ecology and Evolution 3:743–756; DOI 10.1111/j.2041-210X.2012.00196.x) showed that common phylogenetic-signal indices differ in sensitivity to sample size, topology and evolutionary model, and that index choice depends on the inferential purpose.

## Safe role in this project

The distance-based rho is retained because the original turnover programme defined one common, interpretable pairwise "memory gradient" that can be computed identically over many family × trait systems and tree treatments.

The robustness paper should therefore phrase it as:

> a standardized distance-based descriptor of how quickly trait dissimilarity increases with phylogenetic separation within the admitted system.

It should not phrase it as:

> the amount of phylogenetic signal in an absolute or model-comparable sense.

## Consequence for interpretation

Any cross-family portability or repeatability result concerns **this distance-based memory descriptor**. It does not imply that Pagel's lambda, Blomberg's K or another phylogenetic-signal statistic would show identical cross-lineage repeatability.

The prune-only sensitivity addresses tree-construction ties and bind placements, but it does not solve the broader index-choice limitation.

## Future comparison

A lambda/K comparison can be motivated in Discussion as a separate validation direction. It is not added to v0.3 after robustness outcomes because that would change the estimator family after seeing the data and violate the current stop discipline.
