# Post-outcome manuscript skeleton v0.2 — lineage repeatability without trait portability

## Working title

**Phylogenetic trait memory shows family-level repeatability but little cross-lineage portability in vascular plants**

Alternative shorter title:

**Trait phylogenetic memory is weakly portable across plant lineages**

## Central question

If we learn how strongly a trait tracks phylogenetic distance in some plant families, can that information be transferred to an unseen family?

The answer is now more specific than the original portability HOLD:

> **There is a repeatable family-level component in phylogenetic trait memory, but trait identity carries little robust information that can be borrowed across families.**

This is not because family repeatability is an obvious artifact of redundant traits, and it is not because the unshrunk trait predictor is uniquely bad. It is also not evidence that most family × trait variation is biological: species-level sampling error is substantial.

## Data and response

The analysis uses the frozen outcome-blind crossed core:

- 201 family × trait systems;
- 45 vascular-plant families;
- 12 continuous traits;
- every family has at least 2 traits;
- every trait occurs in at least 5 families;
- identical S3 and prune-only sensitivity populations.

For each system, phylogenetic trait memory is summarized as the Spearman association between patristic separation and absolute species-state difference.

The raw effect matrix was independently re-extracted in v0.3 and reproduced the archived effects for all 201 systems at the archived four-decimal precision.

## Result 1 — the original 80.6% residual was not 80.6% biological system specificity

The original unweighted crossed model gave S3 variance shares:

- family: 15.0%;
- trait: 4.3%;
- residual: 80.6%.

Species-cluster bootstrap SEs are not negligible: median SE is 0.058 for S3 rho and 0.071 for prune-only rho.

After treating those SEs as known sampling variances in a crossed meta-analytic model, the S3 point decomposition of total typical variance is approximately:

- family: **15.1%**;
- trait: **5.7%**;
- residual between-system heterogeneity: **54.9%**;
- sampling error: **24.2%**.

Prune-only gives approximately:

- family: **14.0%**;
- trait: **2.2%**;
- residual between-system heterogeneity: **58.6%**;
- sampling error: **25.3%**.

The family point share is therefore remarkably stable after accounting for measurement error. What changes is the interpretation of the old residual: roughly a quarter of typical total variance is attributable to finite-species estimation error.

The pre-frozen two-way family × trait cluster bootstrap is broad. For S3 heterogeneity shares, the 95% intervals are approximately:

- family: 0.123–0.749;
- trait: ~0–0.385;
- system: 0.071–0.751.

Therefore **no variance component should be described as dominant**. In particular, drop any claim that “most memory is system-specific.”

## Result 2 — family repeatability is not explained by the predeclared redundant-trait null

Several nominally distinct traits are strongly correlated across families:

- whole plant height vs maximum whole plant height: S3 r = 0.812;
- leaf area vs leaf dry mass: r = 0.805;
- leaf dry mass vs leaf area per dry mass: r = −0.725.

The conservative v0.3 null preserves these predeclared trait-block correlations, trait means/variances, and the exact sparse family × trait incidence graph while simulating no family main effect.

Observed family repeatability exceeds this null:

- S3: observed R_family = 0.150; null median = 0.034, 95% interval 0–0.139, p = 0.017;
- prune-only: observed R_family = 0.148; null median = 0.026, 95% interval 0–0.122, p = 0.009.

Collapsing the 12 labels into five predeclared trait domains also leaves R_family essentially unchanged:

- S3: 0.144;
- prune-only: 0.147.

Thus the family component survives this specific correlated-trait/shared-design explanation. This is evidence for **repeatable lineage context**, not identification of a biological mechanism.

## Result 3 — shrinkage changes the meaning of the portability failure

The frozen arithmetic trait-mean predictor had negative gain:

- S3: −0.024;
- prune-only: −0.032.

With training-only BLUP shrinkage:

- S3 gain becomes **+0.006**;
- prune-only remains **−0.0048**.

So the apparent prediction penalty largely disappears. However, a robust positive portability signal does not emerge across both tree treatments.

Training trait-level variance is tiny relative to residual variation:

- median S3 trait variance ≈0.00090 versus residual ≈0.0168;
- median prune trait variance ≈0.00060 versus residual ≈0.0247.

The defensible interpretation is therefore:

> **Trait labels contain little transferable phylogenetic-memory information across families. Unshrunk means add noise; shrinkage removes most of that penalty, but there is little stable trait-level signal to borrow.**

Do not describe the result as “anti-portability.”

## Result 4 — log-scale robustness remains unresolved

The mandatory all-201 natural-log sensitivity cannot be executed under the frozen no-offset rule:

- 25 S3 systems contain at least one nonpositive species median;
- 18 prune-only systems do so.

No offset, signed log, or post-outcome system deletion is introduced.

Therefore the raw absolute-difference memory metric remains **not fully validated against multiplicative trait scale**. This is a real limitation, not something to optimize away after seeing the data.

A separate future data-quality study could ask what the nonpositive BIEN values mean biologically or procedurally, but it must not be used to retroactively rescue the v0.3 sensitivity.

## Revised biological interpretation

The original story “phylogenetic memory is mostly idiosyncratic to each family × trait system” is too strong.

The stronger supported pattern is asymmetric:

1. **Family context repeats.** A roughly 15% family component persists after measurement-error correction and exceeds a conservative correlated-trait zero-family null.
2. **Trait identity transfers poorly.** Trait-level variance is small, and even shrinkage-aware out-of-family prediction is essentially neutral.
3. **A large remainder is real but poorly localized.** Residual between-system heterogeneity remains substantial, while about one quarter of typical variance is finite-species sampling error.
4. **The metric remains scale-sensitive in principle.** The planned all-system log test is unavailable because of nonpositive trait medians.

This suggests that the evolutionary memory of a trait is not a fixed property of the trait label. It is partly repeatable at the lineage level, but the same named trait does not carry a strong portable memory signature across families.

## What this paper does not solve

This result remains temporal/comparative only.

It does not answer whether the same biological properties predict spatial turnover.

It does not identify the biological cause of the family component.

It does not show that family effects dominate system heterogeneity.

It does not establish that the raw absolute-difference metric is invariant to trait scale.

## Main figures

**Figure 1 — Measurement error changes the residual story.**  
Naive S3 variance shares versus the measurement-aware point decomposition, with cluster-bootstrap intervals shown separately for heterogeneity-component shares.

**Figure 2 — Family repeatability exceeds a correlated-trait artifact null.**  
Observed S3 and prune R_family against the corresponding predeclared null distributions.

**Figure 3 — Shrinkage removes the portability penalty, not the information bottleneck.**  
Unshrunk versus BLUP portability gain for S3 and prune-only, alongside the small training trait-variance estimates.

## Publication-level one-sentence conclusion

> **Phylogenetic trait memory contains repeatable lineage-level structure, but little trait-level information that can be safely transferred across plant families, and a substantial share of apparent system-level variation is sampling uncertainty rather than biological specificity.**

## Frozen robustness evidence

- `results/trait_memory_robust_effects_v0_3/result.json`
- `results/trait_memory_measurement_aware_v0_3/result.json`
- `results/trait_memory_correlated_trait_null_v0_3/result.json`
- `results/trait_memory_portability_blup_v0_3/result.json`
- `results/trait_memory_robustness_synthesis_v0_3/result.json`

No further estimator, transform, trait grouping, filtering, or portability predictor should be selected on these outcomes to strengthen this manuscript.
