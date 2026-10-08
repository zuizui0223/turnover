# Scientific estimand audit: distance-dissimilarity rho versus phylogenetic conservatism

Status: mandatory interpretation audit before final manuscript claims. Post-outcome; does not reclassify any prospectively frozen test.

## What the primary response actually measures

For a family f and trait t,

  rho_ft = Spearman(d_phylo(i,j), |z_i-z_j|), over all unordered species pairs.

This is a **phylogenetic distance-dissimilarity association**. It is an ordinal measure of whether trait differences tend to be larger for phylogenetically distant species.

It is NOT an estimate of:
- the evolutionary rate sigma^2;
- the time constant or physical speed at which trait similarity decays;
- Blomberg's K, Pagel lambda, or a directly exchangeable measure of phylogenetic signal;
- the developmental/fitness cost of retaining a trait.

If a positive rho is labelled "greater evolutionary lability" and a low rho is labelled "stronger conservatism", the biological orientation is not established by the statistic itself.

## Exact affine-invariance result

For any real trait vector \(z\), any constant \(b\), and nonzero scalar \(a\),

$
\left|(az_i+b)-(az_j+b)\right|=|a|\,|z_i-z_j|.
$

Multiplying *all* trait dissimilarities by the same strictly positive constant leaves their ranks unchanged. Thus, for a fixed tree and sampled species set,

$
\rho_{\mathrm{distance,disparity}}(az+b)
=\rho_{\mathrm{distance,disparity}}(z),\quad a\ne0.
$

This equality is exact whenever the Spearman correlation is defined (and preserves any ties). It has a direct evolutionary implication: for a fixed Brownian tree, a realization at diffusion variance \(\sigma^2\) can be written \(z=\mu+\sigma W\), where \(W\) is the unit-rate Brownian tip vector. Therefore

$
\rho(\mu+\sigma W)=\rho(W)
$

for every realization \(W\) and every \(\sigma>0\). The entire distribution of this rho statistic under the simple homogeneous BM model is invariant to the BM evolutionary rate **on a fixed phylogeny**.

This is stronger than 'the rho statistic may be only weakly related to rate': homogeneous rate is mathematically non-identifiable from this ordinal rho statistic in the BM model.

A nonlinear transform such as \(z\mapsto\log z\) does *not* preserve the ranks of all absolute pairwise trait differences, explaining why cleaned raw and log analyses can differ even with identical systems. Changes in species sets, trees or evolutionary process can also change rho.

## Brownian-motion diagnostic

Under homogeneous Brownian evolution with rate sigma^2 on a fixed ultrametric phylogeny,

  E[(z_i-z_j)^2 | d_ij] = sigma^2 * d_ij.

Thus a positive association between phylogenetic distance and squared trait dissimilarity is expected under Brownian phylogenetic structure. Increasing sigma^2 under a homogeneous Brownian model multiplies realized dissimilarities uniformly and therefore leaves the Spearman rank correlation exactly unchanged on the same fixed tree and realization.

Conversely, phylogenetically independent tip states may exhibit rho near zero despite substantial raw trait variance.

Therefore a stronger positive distance-dissimilarity rho is fully compatible with MORE conspicuous phylogenetic organization, not automatically greater evolutionary lability.

## Why a standard-signal sensitivity matters

Blomberg's K measures the amount of phylogenetic signal relative to the expectation under Brownian motion; K=1 is the Brownian benchmark.

K and rho answer distinct questions. A K analysis must not be called a replicate of the same estimand. Its purpose is to test **convergence or discrepancy across estimators**.

Predecessors:
- Blomberg, Garland & Ives (2003), Evolution, DOI 10.1111/j.0014-3820.2003.tb00285.x.
- Revell, Harmon & Collar (2008), Systematic Biology, DOI 10.1080/10635150802302427.

Revell et al. explicitly warn against treating phylogenetic signal as evolutionary rate/process.

## Manuscript guard

Until a standard phylogenetic-signal sensitivity is available:

ALLOWED:
- "Lineages differ in the strength of the phylogenetic distance-dissimilarity relationship for traits."
- "Trait identity offers weak portability for average rho, but within-lineage rho rankings are extensively reorganized."
- "The rho architecture has separable family-level and trait-allocation components."

NOT YET SUPPORTED:
- "Trait A evolves faster than trait B because it has greater rho."
- "The higher-rho trait is evolutionarily more labile."
- "Our result proves that the degree of evolutionary conservatism is not portable across clades."
- "Lineages actively rewire developmental pathways or natural selection because their rho rankings reverse."

Interpret L and A as properties of **the specified rho estimator on the specified tree and trait scale**. Terms such as memory level or memory allocation are conceptual shorthand, not observed evolutionary processes.

## Decision boundary after K sensitivity

1. If rho and log(K) rankings/architectures broadly agree, the main interpretation can cautiously generalize to more than one signal-related estimator, with estimator-specific effect sizes preserved.
2. If rankings disagree strongly or K lacks lineage-specific reordering, narrow the central claim to distance-dissimilarity coupling; do not claim a general evolutionary-memory architecture.
3. If K fails computationally or lacks sufficient matched support, report it as unavailable. Never substitute a partial K result without a documented source-independent subset rule.

This audit does not redefine the primary result; it prevents biological over-interpretation.
