# DivResource 2013: two disjoint species pools, fixed 48-pair transfer result and exact design identity

## Actual original-source result (2026-11-26)

Original source: Siebenkäs, Schumacher & Roscher (2016), [PLOS ONE](https://doi.org/10.1371/journal.pone.0158110), S5 (annual sown biomass in 2013), S6 (published NE and tripartite diversity components). Distinct field programme from Cedar Creek and Jena TBE, but overlap of this source with any earlier pooled meta-analysis author StudyIDs has not been checked. One field, eight physical blocks (four shaded), two disjoint pools of four species. Source author S5/S6 bytes pinned at SHA-256; 96/96 original species sums agree with BM at reported precision; 64/64 original mixture NE entries match independently computed B−E, and 64/64 NE match TICE+TDCE+DE at reported precision. TICE is Loreau–Hector CE, and TDCE+DE corresponds to SE; no separate CE/SE regression is fitted here.

Exactly 48 source two-species plots (24 per pool), full 6-pair×4-condition design, source one original monoculture per species×resource context. Four-species plots not used in predictive comparison. Planted equal seed weights; no observed-biomass-weighted CWM/FD (S7) leakage. M0 = resource-treatment categorical fixed effects + equal-weighted sown grass and tall mean; M1 = M0 + fixed two-axis binary dissimilarity D. Train pool A, test B, then reverse. Same held-out rows for B and NDE. This retrospective test does not identify causal scalar FD separately from species assignments. Two pools within one field do not yield a population confidence interval; no confidence interval or p-value fabricated.

| Direction | B gain | NDE gain |
|---|---:|---:|
| A→B | −5.6873% | −5.6634% |
| B→A | −8.3680% | −8.4853% |
| Equal-pool combined | −7.1813% | −7.2234% |

Both directions have worse heldout predictions when the fixed categorical difference is added, for both outcomes. This is not evidence that FD reduces actual biomass or that every other trait metric lacks predictive information. It does not validate any BIEN/AusTraits K→FD mediation. Original model [Actions #45760171070](https://github.com/zuizui0223/turnover/actions/runs/45760171070) passed the source checks and known-truth synthetic test.

## New post-result analytical insight: an endpoint comparison degeneracy

The nearly equal percentage scores **must not be read as two independent biological confirmations**. The original absolute increments in heldout squared error from adding D are almost exactly the same:

| Direction | ΔSSE(B) | ΔSSE(NDE) | Δ difference |
|---|---:|---:|---:|
| A→B | 77169.88395833 | 77169.88395833 | −6.98e−10 |
| B→A | 142929.89062500 | 142929.89062500 | −3.73e−9 |

This is not a chance result. With four functional types {(0,0),(0,1),(1,0),(1,1)}, the six pairs have D = 1/2 for four one-axis differences, and D = 1 for two two-axis differences. Thus mean(D)=2/3. Let d=D−2/3. Every species belongs to two pairs with d=−1/6 and one pair with d=1/3, so the sum over its incident pairs is exactly zero. With Z the pair×species equal-sown-weight matrix, dᵀZ=0. This holds separately for each resource treatment. The expected monoculture baseline E=Zm is additive in the planted species; hence dᵀE=0 for arbitrary matched monoculture yields. The baseline model's mean-trait columns and condition indicators are likewise orthogonal to d, and the complete balanced train/test designs have identical X and d.

For each training pool, the added FD coefficient is dᵀy/(dᵀd). It is exactly unchanged when replacing y=B by y=B−E. The additional heldout prediction is the same vector along d. The heldout baseline residual difference after subtracting E is orthogonal to d, because both heldout E and baseline fitted values are orthogonal to d. Therefore the **absolute held-out squared-error change** on adding D is exactly the same for B and B−E for each transfer direction. Their percentage gains differ only because the baseline SSE denominators differ.

The source result conforms to this identity to numerical precision. Independent locally executed algebraic/synthetic verification used 1,000 arbitrary synthetic B vectors and arbitrary species×treatment mono baselines in both pools: maximum numerical ΔSSE difference 1.12e−8; dᵀZ zero up to floating precision. This is a post-result **design theorem**, not a new empirical effect and not a population-general claim. It applies to complete regular balanced pair designs with matching residual feature and equal weighting (here the specified exact two-class factorial design); it does not generally apply to incomplete, unequal-weight, nonorthogonal or unequal-design communities. Do not generalize it to BioCON, Jena or the Chen meta-analysis without verifying their design.

## Decision and limitations

The original exploratory cross-species-pool test supplies no positive transfer result. More importantly, the particular balanced pair design cannot independently discriminate a stronger absolute FD prediction increment for mixing excess than for absolute biomass. An appropriate future contrast must first verify that its residual FD feature is not orthogonal to additive monoculture expected production, or test a different estimand such as cross-pool transfer of separately reconstructed complementarity vs selection rather than reading a forced equality as biological invariance. Avoid post-result outcome/predictor selection. One source mono per species×resource context; no resampled mono uncertainty. Source S7 observed biomass weights remain excluded. Original published positive mean NE and fertilization effects belong to the original authors and are not new findings. Earlier BioCON results, Evolution RC4 and original 21-claim registry unchanged.

Provenance: original S5/S6 schema [#45759879363](https://github.com/zuizui0223/turnover/actions/runs/45759879363), original result [#45760171070](https://github.com/zuizui0223/turnover/actions/runs/45760171070), aggregate ZIP artifact 15090110606 SHA256 48319fafa81ff58e7ce4493ad66fac285958348e4872438359f7edf4373d7487. See [committed exact numeric results](../results/divresource_2013_pool_transfer_v0_1.json). No individual biological source rows committed.
