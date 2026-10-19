# Brownian exchangeability null: a challenge to biological trait-memory rewiring

**Status:** POST-OUTCOME KNOWN-TRUTH COUNTEREXAMPLE, NOT A CALIBRATED EMPIRICAL NULL. The original prospective decisions and numeric results are unchanged.

## Exact null argument

For traits a,b inside a family f, write their sampled phylogenetic distance–dissimilarity statistics as R_fa and R_fb.

If the two traits evolve independently under identical evolutionary processes on the **same tree and species set**, R_fa and R_fb are exchangeable. With no contrast ties:

$$
P(R_{fa}>R_{fb})=P(R_{fb}>R_{fa})=1/2.
$$

If family histories are independent conditional on the family trees, contrast signs from two different families f,g are independent:

$$
\boxed{P[(R_{fa}-R_{fb})(R_{ga}-R_{gb})<0]=1/2.}
$$

Therefore **50% pair-order reversal is expected under the identical-process null**. It is not an extreme biological re-wiring effect size.

Empirical paired-species AusTraits S3/prune reversals are approximately 47.1% and 47.3%, respectively; these are near the exchangeable null, not excess reversals.

## Why split-half reliability does not rule this out

There are three types of variation:

1. Uncertainty in estimating rho from finite species.
2. Stochastic realized trait histories even when all families and traits share exactly the same Brownian evolutionary rate.
3. Differences in evolutionary processes, ecological regimes, developmental constraints, optima or rate parameters among lineages and traits.

The previous split-half test addresses the first. It does **not** eliminate the second. Brownian stochastic realization is biological variation, but it need not be lineage-specific evolution of a constraint or adaptation.

## Known-truth simulation

Reproducible source: scripts/analysis/simulate_brownian_exchangeability_null_v0_1.py

- 24 **synthetic** ultrametric family trees, 24–72 species per family;
- deep, standard and star-like branch geometry;
- eight independent traits under the **same rate and same Brownian process in every family**;
- 128 independent stochastic trait realizations, seed 20261008;
- rho = Spearman(patristic distance, absolute trait difference);
- Blomberg K computed using the phylogenetic covariance formula of phytools;
- balanced two-way ANOVA method-of-moments family and trait components, not empirical REML.

| Simulation quantity | Mean under identical BM processes |
|---|---:|
| rho cross-family trait-pair reversal | 50.04% |
| K cross-family trait-pair reversal | 49.98% |
| rho family component L | 0.186 |
| rho trait allocation component A | 0.009 |
| log(K) family component L | 0.041 |
| log(K) trait allocation component A | 0.009 |
| mean rho, deep vs star-like family trees | 0.563 vs 0.457 |
| mean K, deep vs star-like family trees | 1.010 vs 0.998 |

These outcomes arose with **no differences whatsoever in evolutionary-process rate parameters among families or traits**. Tree geometry alone altered mean rho substantially, while K remained near its Brownian benchmark.

The resemblance of simulated rho L≈0.186 to BIEN empirical L≈0.184 is **not a fitted comparison**: synthetic phylogenies, balanced trait coverage and random sampling are not the real data.

Both rho and K are invariant to multiplying a trait's states by a constant, and neither is a direct estimator of the Brownian evolutionary rate.

## Revisions to biological interpretation

**The following strong claim is unestablished**:

> Lineages actively rewire how phylogenetic memory is allocated among traits.

What remains well supported *descriptively*:
- modest but nonzero cross-family predictive information in mean rho by named trait;
- weak portability of trait rankings to previously unseen families;
- near-half observed pair-order reversal;
- finite-species estimation noise and inter-trait species-composition differences alone cannot account for all the observed variation;
- an empirically positive family-level rho variance component.

These do **not** prove the latent **evolutionary process parameters** differ. Stochastic Brownian outcomes and tree geometry may reproduce them.

**A future K result with 50% trait-rank reversals would not by itself solve the problem**: exchangeable Brownian traits produce 50% K-rank reversals too.

## Required empirical process null

1. Simulate traits on the actual frozen BIEN and AusTraits family trees, with their original S3/prune treatments and actual trait-specific species subsets.
2. Under identical-rate Brownian motion, reproduce the entire empirical analysis, including family repeatability, absolute trait portability, rank portability and direct pair-order reversal.
3. Calibrate the observed family component and deviation amplitude against that process-null distribution, respecting trait and family dependence.
4. Compare against explicit alternative biological models: heterogeneous branch rates, lineage-specific OU regimes, correlated trait evolution, environment-dependent evolutionary variance and measured life-history mechanisms.
5. Use held-out-lineage or posterior-predictive fit to distinguish processes. Do not interpret a descriptive 50% reversal as excess signal.

No empirical p-value can be derived from this toy simulation because its family trees and data coverage are synthetic.

## Defensible submission claim until process-null validation

> Global trait-average phylogenetic distance–dissimilarity relationships offer weak cross-lineage prediction, but realized lineage-specific trait rankings are poorly portable.

Avoid interpreting rho rank reversals as direct evidence that evolutionary constraints or developmental pathways are adaptively rewired.
