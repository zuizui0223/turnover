# Exact zero mean of the complete label-permutation null for trait turnover

For the trait-time and trait-space cells, the frozen null permutes complete trait states among the observed labels while leaving the separation geometry fixed.

Let the complete set of unordered pairs be (E). Let (a_e) be the centered rank of separation for edge (e), and let (b_e) be the centered rank of the pairwise trait dissimilarity. For a uniformly random permutation \(\pi\) of the vertex labels, the permuted state assignment induces the edge-rank vector \(b_{\pi(e)}\).

The permutation group on labels acts transitively on the unordered edges of the complete graph. Therefore, for every fixed edge,

[
E_\pi[b_{\pi(e)}] = |E|^{-1}\sum_{e'\in E} b_{e'} = 0.
]

A label permutation preserves the complete multiset of pairwise dissimilarities and therefore preserves the norm of the centered dissimilarity-rank vector, including deterministic average ranks for ties. The separation-rank vector and its norm are fixed. Hence

[
E_\pi[\rho_S] =
\frac{\sum_e a_e E_\pi[b_{\pi(e)}]}{\|a\|\|b\|}=0,
]

provided the dissimilarity rank variance is nonzero.

Thus, for the frozen complete-label permutation null used by the trait arm,

[
\Delta\rho = \rho_{obs} - E_\pi(\rho_{null}) = \rho_{obs}.
]

This does **not** remove the null model. It removes Monte Carlo error from estimating a null mean that is known exactly by symmetry. Permutations remain useful for the null dispersion and implementation diagnostics. The result does not automatically extend to constrained interaction-network nulls, which are not simple complete vertex-label permutations.

The primary estimator must use the complete unordered-pair set for this exact identity. Systems with zero pairwise-state rank variance are undefined and fail the already-frozen state-variation/informativeness gates.
