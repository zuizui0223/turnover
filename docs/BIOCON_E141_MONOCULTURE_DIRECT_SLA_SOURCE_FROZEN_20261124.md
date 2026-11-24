# BioCON E141: outcome-blind monoculture and source-measured SLA preflight

Frozen 2026-11-24 after original plantation-key check, **before opening original biomass outcome columns**.

## Original inputs fixed

- E141 author Figshare v3 original CSV MD5 `8185b8effca37c8740ad065c53eb75d2`; 16 original sown flags, measured 1998–2021 twice annually. Author v3 contains 16 species biomass columns but these numerical responses remain **unopened**.
- Published Ohlert et al. (2024) PLOS ONE original [code source](https://github.com/kaitkimmel/FDiv/blob/e61c8814f3fc8e8fa7cac6141ee462c3e8b22554/R/CDRTraitCleaning.R), immutable upstream commit `e61c8814f3fc8e8fa7cac6141ee462c3e8b22554`, code git blob `e418bde5f8e09b515c3cd3a3b4f678ae24e97140`. Source 4 treated trait tables pinned to Git blob SHAs by the audit script. These are **derived and partly filled tables**, not all directly measured native E141 traits.

## Predeclared original assignment-only eligibility

1. Count unique original **physical Ring×Plot** monocultures, by exact source **CO₂×N×sown species** (4 source environments × 16 original E141 planted species = 64 original expected baseline cells). Minimum **2 distinct physical mono plots in each**; the same mono plot remeasured in 24 years does not become a new replicate. If any source cell absent or fewer than 2, reject any proposed full 16-species same-treatment NDE calculation (never impute or pool CO₂/N contexts).
2. For baseline one-trait **SLA** sensitivity, **exclude** *Bouteloua gracilis* and *Poa pratensis* from the directly measured candidate set. The original Ohlert cleaning code writes Big Bio/E120 substituted SLA for those two species, says original SLA **56 of 64 species×CO₂×N cells**; DO NOT treat the published complete 16-species tables as 64 direct E141 observations. Also flags cross-treatment Anemone root C/N copy and five seed mass Big Bio replacements.
3. A source **candidate** trait-FD support check, before inspecting yields: main experimentally sown plots at richness 4,9,16 are eligible for one-trait FD only if **≥2 directly provenance-supported sown species AND ≥80% of the sown species** fall outside the two SLA source substitutions. The 80% minimum was fixed before auditing per-mixture trait coverage. Retain all original noneligible mixtures in the audit denominator; do not lower thresholds or selectively relabel missing taxa.
4. This is merely source coverage. Exact original raw EDI trait rows and measurement **year/time** remain unavailable; 2024 cleaned data span post-establishment treatment conditions. **No claim of preplant/causal FD independent of planted species identity.** Original mono source support does not validate the published CE formula or whether per-plot seasonal yields are available for matching years.
5. Whole E141 CO₂ treatment assignment is at **6 rings**, not 371 plots, 8,904 plot-years or 17,808 biomass CSV lines. The original published 2025 paper's CE/SE is known; no new independent meta-analysis or general transport claim.

## Executed source-only output

The CI and immutable summary are linked from this PR. **No ecological effects are fitted or original numeric source observations redistributed.** If EDI traits cannot be verified, status remains `TRAIT_TIME_HOLD` even when the mono and sown-composition source supports pass.

Run: `python scripts/source/audit_biocon_e141_mono_trait_provenance_v0_1.py --selftest`, then `--source`.
