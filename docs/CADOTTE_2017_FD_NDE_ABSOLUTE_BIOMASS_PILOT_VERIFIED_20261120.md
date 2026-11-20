# Cadotte 2017: FD predicts absolute biomass or its net diversity effect? Actual source-verified pilot

**Checked 2026-11-20, exploratory one-experiment analysis.** [Original-source GitHub Actions #44750171096](https://github.com/zuizui0223/turnover/actions/runs/44750171096) **SUCCESS**; [separate aggregate arithmetic QA #44751586875](https://github.com/zuizui0223/turnover/actions/runs/44751586875) **SUCCESS**. Official CC0 [Zenodo 5022435](https://zenodo.org/records/5022435) (original Dryad `10.5061/dryad.627rt`), four original source files individually verified against predeclared MD5. This is one original Canadian experimental study, **not 34 independent studies**, and its authors previously examined FD, selection and complementarity. The choice of this pilot followed access failures for other candidates and exposure to the published result directions; no confirmatory, prospective-discovery claim is permitted.

## Exact source qualification

| Audit | Verified original value |
|---|---:|
| Original mixture records with NDE, selection, complementarity | **40** |
| Exact matched planted-species roster rows | **40 / 40** |
| Exact matched absolute-biomass records | **40 / 40** |
| Original species present in source trait file | **14** |
| Qualifying original distinct planted-composition holdout groups | **34** |
| `COMP+SELECT=DeltaY` mismatches | **0** |
| Independent biomass-table discrepancies >0.15 original units | **0** |
| Planted vs source SPP_NUM count mismatches | **0** |
| Original raw species or mixture observations redistributed | **0** |

The official 2017 original observed biodiversity outcomes were not used to select individual traits, plots or a response axis once this pilot protocol had been frozen. The pre-sowing trait predictor was equal-planted-species two-axis mean pairwise Euclidean dispersion in *log SLA* and *log original field.height*, source-trained trait-axis scaling only. Baseline M0 = `log2(planted richness)+CWM_logSLA+CWM_logheight`, M1 = M0+FD, unweighted OLS. Leave-one-unique-species-composition-out CV uses **identical original plots/folds and M0/M1** for all four outcome definitions. Uncertainty uses paired **1000 composition-group bootstrap resamples of the heldout error vectors** with fixed original out-of-fold predictions (not a full model-refit cluster bootstrap).

## Actual numerical result

| Original outcome on the SAME 40 mixtures | Additional FD held-out SSE gain | 95% composition bootstrap interval |
|---|---:|---:|
| **Absolute aboveground biomass** | **+8.82%** | **[−13.51%,+25.78%]** |
| **Net diversity effect**, original `DeltaY` (signed) | **−3.62%** | **[−15.52%,+4.09%]** |
| Complementarity, original `COMP` (signed) | **−6.25%** | **[−15.15%,+0.08%]** |
| Selection, original `SELECT` (signed) | **−1.24%** | **[−10.06%,+3.11%]** |

The **predeclared descriptive paired contrast** `gain_NDE − gain_absolute` was **−12.44 percentage points**, 1000 composition-group-bootstrap 95% interval **[−26.56,+0.84] points**. Every individual endpoint interval and the paired contrast contain zero; none provides an established new positive/negative general predictive benefit.

## Interpretation (what this DOES / DOES NOT show)

This one-site pilot **does not support** the attractive prediction that FD is intrinsically better at predicting NDE than absolute biomass. The point estimate goes in the opposite direction. This does **not** prove an NDE-wide null, a globally better absolute-biomass model or a causal negative FD effect; the confidence interval spans 0, there are only 40 plot observations and 34 related composition identities, and no independent site is held out.

The original **published** claim that trait dissimilarity can have opposing relationships to selection/complementarity is a different association/pathway estimand from incremental **out-of-composition predictive gain of a TWO-AXIS FD conditional on planted richness and CWM**. Hence its published association, our negative/uncertain predictive increment, and the TreeDivNet 2026 absolute-stock test can coexist without contradiction. They do not identify an FD-only causal mediator, and signed components must not be log-transformed.

The scientific hypothesis worth pursuing requires source-qualified **independent multiple experiment** held-out tests with the same FD source on NDE and absolute productivity and explicit source-level treatment/monoculture expectations. The 21-forest experiment and PaNDiv releases in [PR #68](https://github.com/zuizui0223/turnover/pull/68) are **DOI-metadata-only, original file HTTP 401 HOLD**. Do not re-open them by replacing original values with manufactured data, unknown site relabelling or result-guided choice of species/traits.

**No phylogenetic K/ρ→FD→NDE/biomass mediation measured.** BIEN, AusTraits, TreeDivNet older heldout study decisions and *Evolution* RC4 are unchanged.

## Source integrity, models and identity

- Frozen source protocol: `docs/CADOTTE_2017_FD_NDE_SINGLE_EXPERIMENT_PILOT_FROZEN_20261120.md`.
- Source-frozen code: `scripts/analysis/cadotte_2017_fd_nde_same_plot_exploratory_v0_1.py`.
- Original aggregate-only result: `results/cadotte_2017_same_mixture_fd_nde_pilot_v0_1.json`.
- Independent no-refit SSE algebra and zero-crossing check: `scripts/analysis/verify_cadotte_2017_fd_nde_pilot_v0_1.py`.
- [Original fit action #44750171096](https://github.com/zuizui0223/turnover/actions/runs/44750171096), nonraw artifact #14636005346, digest `sha256:c9aaacc22703202c56608199b18c60ca58e3d1d2dc269f91ab1ed880667aff29`.
- Original initial source parser failed on legacy CSV newlines; only Python CSV newline parsing was corrected (commit `053477c6`), original MD5 and all predeclared scientific thresholds unchanged. Successful rerun preserved one original source population.
- The project does **not** claim an independent meta-analysis, experimental intervention on FD alone, causally identified complementarity mechanism or novel independent published-study replication.
