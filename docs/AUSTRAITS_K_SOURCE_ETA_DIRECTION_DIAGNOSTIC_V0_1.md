# Exploratory source-variance direction check (2026-10-08)

**Status:** post-observed-K, post-BM/OU source-dispersion diagnostic. **Not a frozen primary hypothesis or the source-noise OU verdict.**

The exact observed 254-system K archive and K-blind source variance calibration artifact were matched, excluding only the source-coverage-ineligible `seed_height`. Remaining fixed support: **249 family×trait systems, 42 families, 12 traits**. For each within-family pair, ask whether the trait with the higher source variance/among-species variance ratio also has a lower observed Blomberg `logK`.

The source ratio is **not** pure measurement error. The permutation shuffles its 12 named-trait labels *globally*, keeping observed family-pair dependence, missingness and support fixed. The 770 within-family pairs are not 770 independent observations; ordinary binomial pair p-values would be invalid.

| Estimator | Within-family pairs agreeing with greater source variation → lower K | Shuffled-trait-label 95% interval | One-sided global-label Monte Carlo p |
|---|---:|---:|---:|
| S3 | **59.35%** (770 pairs) | 39.22–60.91% | **0.0550** |
| prune-only | **60.78%** (770 pairs) | 36.36–63.77% | **0.0735** |

20,000 fixed-seed global trait-label permutations (`seed=20261008`), descriptive and uncorrected for both tree treatments. This is a *weak directionally compatible trend*, not strong evidence that source dispersion generated K portability. The adjusted trait-mean K versus eta Spearman correlations were also weak (S3 approximately **−0.182**, prune **−0.140**, 12 traits). The latter are descriptive, not a new independence claim.

**Interpretation:** greater K-blind cross-dataset variability does not give a strong transferable rank map by itself. Independent source noise could still yield nontrivial K effects through actual nonstar tree covariance and source/taxon overlap, so this check neither validates nor invalidates the frozen exact-tree source-noise OU scenarios. Their final metric results remain pending.

Reproduction: `scripts/analysis/audit_austraits_k_source_eta_direction_v0_1.py --observed-K effects.csv --source source_dispersion.json --out result.json` with artifacts from GitHub Actions **#37725935020** (K) and **#37784017236** (source dispersion). The [full OU+source null](https://github.com/zuizui0223/turnover/actions/runs/37785257795) must remain the decision endpoint, not this post-outcome directional probe.
