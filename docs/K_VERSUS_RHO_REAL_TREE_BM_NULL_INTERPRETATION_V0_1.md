# Trait-memory inference after the observed-tree Brownian null

Status: post-outcome synthesis, 2026-10-08. Scientific outcome audit complete for the **identical independent Brownian** null, not for all homogeneous evolutionary processes.

## Central result

**The same plant family × trait graph behaves very differently under two phylogenetic-structure statistics.**

- Spearman rho of phylogenetic separation against trait dissimilarity offers weak transferable trait-level ranking in AusTraits (S3 matched-log rank gain ≈ -0.2%, prune ≈ -1.76%).
- Blomberg's K, which quantifies signal relative to Brownian expectation, offers positive and robust trait rank portability (S3 +8.08%, prune +15.31%) and high family repeatability (S3 ≈ 0.531, prune ≈ 0.588).

The two statistics are *not* estimates of the same quantity. On the same 254 systems, empirical K versus rho has only modest association (Spearman ≈ 0.305 on S3, 0.217 on prune).

The lesson is not that phylogenetic trait hierarchy is everywhere absent. Instead, **what aspects of lineage-linked phenotypic structure are portable depends on the statistic being predicted**.

## Stronger evolutionary-process diagnostic

The known-truth synthetic simulation shows that independent equal-rate Brownian traits reverse order between families with probability about 1/2 under either statistic. **Near-half reversal is the no-trait-difference benchmark**, not an adaptive signature.

To test more than this descriptive property, all 254 exact source-native family × trait tree tip sets were reconstructed. For each S3 and prune tree, 64 independent equal-rate Brownian trait histories were generated. Each trajectory was processed with a validated fast-K implementation; observed-K reconstruction was checked against phytools. Complete workflows succeeded.

| Contrast | Empirical S3 | BM null mean (95% interval) | Empirical prune | BM null mean (95% interval) |
|---|---:|---:|---:|---:|
| Rank LOFO SSE gain | +0.0808 | -0.0500 (-0.0840, +0.0033) | +0.1531 | -0.0483 (-0.0877, +0.0153) |
| Absolute LOFO SSE gain | +0.0445 | -0.0505 (-0.0966, +0.0027) | +0.0616 | -0.0495 (-0.0861, +0.0101) |
| Cross-family K pair-order reversal | 0.4403 | 0.4983 (0.4793, 0.5106) | 0.3988 | 0.4977 (0.4735, 0.5120) |
| Family K conditional repeatability | 0.5306 | 0.0252 (0, 0.1132) | 0.5881 | 0.0213 (0, 0.0892) |

The observed value is on the side away from the null mean for each contrast, on both tree axes (one-sided Monte Carlo tail fraction 1/65 = 0.01538). There were only 64 replicates, so the p-value resolution is coarse. These exploratory comparisons do not control the full family-wise error across all inspected metrics.

## Centering by the actual BM expectation

Subtract each system's mean simulated log(K) from its observed log(K), using the exact system tree and tip support:

- S3 centered K rank gain **+9.37%**, standardized-excess gain **+7.90%**;
- prune centered K rank gain **+14.62%**, standardized-excess gain **+13.31%**.

For each simulated null replicate, the expectation and standard deviation come from the **other 63** replicates, not from itself. All four values exceed the 97.5% null bound (one-sided Monte Carlo 1/65).

Thus systematic phylogenetic geometry and species-count effects on the *expected* K do not explain the observed named-trait signal hierarchy.

## What has genuinely been established

1. **A reproducible mean trait hierarchy exists for Blomberg K**, beyond this specific real-tree equal-Brownian null. K rankings predict held-out families better than a no-trait-ranking baseline.
2. **There is a substantial family-specific K component** exceeding the equal-Brownian null for the actual species/tip sets.
3. **The hierarchy is not rigid**: even under K, 40–44% of between-family pairwise orderings differ, while the same-process null predicts ~50%.
4. **rho and K quantify meaningfully different patterns**. The non-portable rho ranking does not negate the portable K ranking.

## What has not been established

1. **No adaptive or ecological mechanism has been identified.** Family and trait differences in K might be induced by non-Brownian but shared processes, correlated developmental traits, data acquisition/measurement biases, source heterogeneity or true lineage-by-trait evolutionary heterogeneity.
2. **Neither rho nor K estimates an evolutionary rate.** Scaling a trait by a positive constant does not change either statistic.
3. **A 40–50% reversal rate does not itself mean trait constraints were rewired.** It is a noisy-sign statistic with a 50% exchangeability null.
4. This is **independent-compilation validation** of trait signal and not established independent-primary-source replication; source DOI recovery is incomplete.

## Novelty boundary

Variation of trait phylogenetic signal across clades and differences in relative trait evolutionary dynamics have prior literature (e.g., Blomberg et al. 2003, Ackerly 2009, Jones et al. 2013).

A defensible incremental advance here is the combination of:
- frozen matched plant family × trait graph,
- distinct out-of-family prediction questions,
- direct comparison of distance–disparity rho versus Blomberg K,
- real-tree/tip-set identically parameterized process-null calibration,
- uncertainty-aware checks and negative trait-hierarchy result for rho reported rather than hidden.

**This alone is not a new theory of adaptive evolutionary-memory allocation.**

## Next decisive process alternatives

**Homogeneous OU null:** Use one attraction strength across all family/trait trees (with an outcome-independent scale), simulate K using the same fixed observed trees and species/tip sets, and compare the same family ICC and LOFO trait rank gain.

**Correlated-trait Brownian null:** Simulate multivariate Brownian dynamics with common trait covariance under the observed co-measured species sets. Even absent trait-specific process heterogeneity, correlated leaf/seed dimensions can alter apparent rank stability and ICC.

Only after such homogeneous alternatives are tested should residual structure be attributed to lineage-by-trait evolutionary-process differences. If they remain insufficient, candidate biological drivers include differences in developmental integration, life-history strategies, and selective environments. Those mechanisms require direct trait covariance/fitness evidence.

## Provenance

- K on fixed 254 systems: GitHub Actions 37725935020 (success).
- Real-tree equal-BM K null: 37746671909 (success; all 16 batches and 64 family REML null fits).
- Frozen interpretation and BM-centered K calculation: 37750895593 (success).
- Details and code: draft PR #33, based on PR #13, \`analysis/brownian-process-null-v0-1\`.
