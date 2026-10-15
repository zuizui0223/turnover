# When does the Blomberg K ordering of two traits change after matching their species and phylogenetic tree?

**2026-10-15; fully reproduced post-outcome exploratory diagnostic.** A completed [42-family cluster/bootstrap/GEE workflow #38683556548](https://github.com/zuizui0223/turnover/actions/runs/38683556548) retrieved and revalidated **all 24 original matched-tip K batch outputs**, their frozen [source-only 760-pair support graph #38673955087](https://github.com/zuizui0223/turnover/actions/runs/38673955087), and the canonical [full source-native K calculation #38674635870](https://github.com/zuizui0223/turnover/actions/runs/38674635870). Synthetic 760-pair corruption tests, all original K identities and 5,000 family-cluster bootstrap replicates passed. The original equal-Brownian, homogeneous OU and source-calibrated process-null decisions were **not** reestimated.

The 760 source-qualified pairs are repeated contrasts among 42 plant families and 66 unique named trait pairs, **not independent data points**. Each comparison uses **identical shared taxa and exact same phylogeny for the two trait K values**, and is compared to the original separately sampled K contrast.

## Result 1. Family balance changes the apparent reversal frequency

| Estimand | S3 | Original prune-only |
|---|---:|---:|
| Valid family×trait contrasts | 760 | 747 |
| Original-to-same-tip K sign reversals | 151 | 137 |
| Pair-weighted reversal frequency | **19.87%** | **18.34%** |
| 42-family cluster-bootstrap 95% interval, pair-weighted | **16.28–23.31%** | **14.05–21.75%** |
| Equal-family-average reversal frequency | **14.69%** | **12.64%** |
| 42-family bootstrap 95% interval, equal-family | **11.10–18.25%** | **9.43–15.94%** |

The family-equal estimates are smaller because a few families with many pair comparisons contribute more rows and more reversals to the pair-weighted summary. One cannot claim "20% of independent plant families" invert their K rankings. Bootstrap units are whole families, resampled **5,000 times with frozen seed 20261015**, preserving all original trait pairs from a sampled family.

## Additional generalization-unit sensitivity: traits and families are different targets

Because some named-trait pairs occur in only one or two families while others recur many times, **averaging first across all 66 trait-pair types** changes the estimand again:

| Equal-weight target (descriptive) | S3 reversal frequency | Prune reversal frequency |
|---|---:|---:|
| Every valid family×pair observation | 19.87% | 18.34% |
| **Every family** | **14.69%** | **12.64%** |
| **Every one of 66 named-trait-pair types** | **28.03%** | **28.79%** |
| Pair types recurring in ≥5 families only | **24.22% (54 types)** | **22.33% (53 types)** |

These are **four different descriptive sampling targets**, not four estimates of one universal true rate. The equal-66-type mean is particularly unstable because several trait combinations occur in very few families and receive the same weight as heavily replicated combinations; it has **no defensible 66-independent-type confidence interval** here. The ≥5-family restriction is presented only as a support diagnostic; it is not a new primary outcome-driven selection criterion.

**Support-defined rare versus well-replicated trait pairs:** Using the **five-independent-family threshold already fixed by the original pre-matched-K species-support protocol**, 12 trait-pair types with <5 eligible families produce **18/41 reversals (43.9%) on S3**, versus **133/719 (18.5%)** among 54 pair types with ≥5 families. For prune the corresponding figures are **20/42 (47.6%)** versus **117/705 (16.6%)** for 13 versus 53 types. Their typical common-species count is similar (S3 median **101 vs 105**), but rare pair types have much lower **larger-cohort coverage** (S3 median **24.9% vs 61.1%**). Their reversal excess therefore co-occurs with strongly unbalanced trait taxon support, not simply fewer shared species. This is descriptive and cannot prove rare traits intrinsically have more labile K: taxon/source regimes and pair identity differ substantially.

The substantive point is that a statement about "the proportion of lineages" (families), "the proportion of available family×trait contrasts", and "the proportion of named-trait-pair categories" is *not interchangeable*. This is central to the project's question of transporting named-trait phylogenetic K order across lineages.

## Result 2. Original K contrast margin predicts a sign flip

Sign reversal is defined by `ΔlogK_original × ΔlogK_matched < 0`, so its negative relationship with `|ΔlogK_original|` is partly **mathematical**, not proof of biology.

| Original absolute log(K) gap | S3 flips / N | Prune flips / N |
|---|---:|---:|
| <0.10 | **27/52 (51.9%)** | **22/63 (34.9%)** |
| 0.10–0.25 | 31/113 (27.4%) | 20/88 (22.7%) |
| 0.25–0.50 | 34/146 (23.3%) | 32/146 (21.9%) |
| 0.50–1.00 | 33/227 (14.5%) | 27/194 (13.9%) |
| ≥1.00 | **26/222 (11.7%)** | **36/256 (14.1%)** |

The stratum-specific uncertainty intervals were obtained by resampling 42 families rather than treating dozens of pairs from the same family as independent. These thresholds were selected for this **post-data diagnostic**, not as a prospective hypothesis.

## Result 3. Asymmetric trait coverage matters more than a superficially high overlap percentage

Among same-family trait pairs, the median fraction of the **smaller** original species support preserved is **95.4%**, but the median fraction of the **larger** species support preserved is only **59.3% (S3)** and **59.8% (prune)**. These are different denominators. Thus a small trait's entire taxon set may be included while a large trait's tip sample is substantially reduced.

| Fraction of *larger* original trait's species retained in pair | S3 flips / N | Prune flips / N |
|---|---:|---:|
| <25% | **44/110 (40.0%)** | **41/103 (39.8%)** |
| 25–50% | 46/198 (23.2%) | 43/193 (22.3%) |
| 50–75% | 35/197 (17.8%) | 28/196 (14.3%) |
| 75–90% | 20/150 (13.3%) | 18/150 (12.0%) |
| ≥90% | **6/105 (5.7%)** | **7/105 (6.7%)** |

This is a strong descriptive gradient across the 760 original comparisons. It does **not** establish that reducing taxon coverage is the sole causal reason for these differences; relative overlap covaries with trait identity, actual K margin, original sample support and which species are missing.

## Result 4. Dependence and covariate adjustment: two different answers

The exploratory **exchangeable working-correlation GEE logistic model**, with families as clusters and predictors `original |ΔlogK|`, `1 - common_species/max(nA,nB)`, and `log(n_shared)`, gives:

| Conditional association | S3 | Prune |
|---|---:|---:|
| Odds ratio for a further 10 percentage points *missing from larger trait cohort* | **1.36 (95% CI 1.27–1.46)** | **1.36 (1.25–1.49)** |
| Original absolute K margin coefficient on logit scale | −1.50 | −0.74 |
| Log common-species count coefficient | −0.47 | −0.39 |

These are exploratory model coefficients; model-dependent confidence intervals should not be interpreted as pre-registered discoveries.

As a stronger sensitivity, a cluster-robust linear probability model including **family fixed effects and named-trait-pair fixed effects** still finds negative coefficients for original K margin on S3/prune (−0.109/−0.055). The missing-larger-species coverage coefficient remains positive for S3 (+0.445, exploratory p=0.0031) but becomes uncertain for prune (+0.188, exploratory p=0.250). **Therefore we must not claim a stable within-family causal overlap effect on both trees.**

## Result 5. Two-tree concurrence is only partial

For the **747** pairs where both S3 and prune estimates qualify:

| Classification | Pairs |
|---|---:|
| K order stable on BOTH trees | **540 (72.3%)** |
| K order reversed on BOTH trees | **78 (10.4%)** |
| K order reversed on S3 only | 70 |
| K order reversed on prune only | 59 |

A total of **129/747 (17.3%)** have axis-specific reversal classifications. The general phrase "about 20% reversed" therefore includes sensitivity to tree construction; only 10.4% of the mutually supported pairs exhibit the reversal on both trees.

## Scientific conclusion and manuscript language

The original approximately 80% pairwise K sign portability is *conditional* on the original K contrast being distinguishable from zero and on taxonomic coverage. Much of the residual ranking instability lies in comparisons with a small original K gap and/or pronounced imbalance in the two traits' taxon coverage. Even on exact same tip sets within pairs, there are real differential K estimates, but **neither their amount nor their sign identifies a different evolutionary OU alpha, a selective process, or an intrinsic 'evolutionary memory' coefficient of a trait**.

This is a **post-original-K, within-AusTraits** sensitivity, not external replication. The other previously frozen result still stands: homogeneous OU plus independent source-calibrated observational variation can reproduce the *scalar amount* of K rank portability, while a new *post-outcome* named-trait rank-profile discrepancy remains unexplained. The five selected trait signs are discovery-generated, and current TRY v7 primary measurement independence has not been demonstrated.

A defensible manuscript claim is:

> Cross-trait differences in phylogenetic K partly persist on identical species and phylogenies, but their direction is substantially conditional on original contrast magnitude and uneven taxonomic coverage. A family-balanced estimate suggests lower reversal prevalence than a naive pair-weighted count. Source variation and phylogenetic sampling must be modeled before treating a named-trait K hierarchy as evolutionarily transferable.

## Reproducibility

- [Frozen post-outcome margin/overlap analysis contract](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_k_shared_tip_margin_sensitivity_v0_1.json)
- [Full audited source code](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/scripts/analysis/audit_austraits_k_shared_tip_margin_sensitivity_v0_1.py)
- [42-family bootstrap, GEE, fixed-effects synthetic tests and archived data output](https://github.com/zuizui0223/turnover/actions/runs/38683556548)
- [Full frozen 760-pair same-tip K results](https://github.com/zuizui0223/turnover/actions/runs/38674635870)
- No species-level raw trait values or IDs were exported by the margin workflow.
