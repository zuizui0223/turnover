# BioCON E141 original 2021 aboveground-component provenance gate

Frozen 2026-11-24 after secondary-author 2021 FD held-out predictive results, **no new FD effect fit or posthoc predictor selection**.

## Problem
The original author Figshare 26841637.v3 contains AbovegroundTotal Biomass (g/m^2), 16 species-level (g/m^2) columns, Miscellaneous Litter (g/m^2) and Total Biomass. It is not safe to presume that these are interchangeable or that Miscellaneous Litter equals all unsorted species material.

Published Huang et al. (2025, Nature Communications, 10.1038/s41467-025-62691-0) describes unsorted original species-level biomasses for 4-species plots in 2006-2021 and 9-species plots in 2005-2006, estimating species-level biomass from plant cover when needed. The previously fitted pilot instead used the original physical plot-level AbovegroundTotal Biomass as B and source mono total as E. Source identity is therefore essential to the **interpretation** of the existing B and signed NDE, even though that existing model did not use imputed 2021 species-level contributions.

## Inference and source hierarchy
- Original author v3 Figshare CSV exact MD5 = 8185b8effca37c8740ad065c53eb75d2.
- Original author README and 2025 R calculation code exact MD5s = 9ce824a94a0ad0ab455a9cfcc1589670 and 3166d7b1f8ee36e974812b3c7ac2cb48.
- Audit same original 46 August 2021 main 4/9-mixture physical plots under original source richness, no extra water/temperature, 80% candidate E141 SLA coverage and two original source monoculture controls for each sown species in same CO2/N year/season. Also audit 128 original August 2021 physical mono controls. Never select a different sample after results.
- Compare, **only where all components needed are genuinely reported**, original B versus 16 species mass sum, planted-species sum, original alternate Total Biomass and alternate total with separate litter. Missing species mass means missing: never recode it as zero and never infer an identity when sum is incomplete. Pure unit/accounting tolerance 0.001 g/m2 plus 1e-5 times the largest magnitude.
- Count original species biomass coverage, especially in 4-species rows in which source literature reports that species-level biomass was unsorted. Check whether any reported original non-planted species mass is nonzero. Report counts for true identity, false identity and not auditable separately.
- No source individual biomass/plot/trait/taxon data are printed or committed, only aggregate counts and identity classifications. No FD model, sample choice, target variable or CI is retroactively modified.

## Decision
If B cannot be proven equal to planted-species biomass from source columns, phrase prior B endpoint precisely as original physically collected total aboveground mass (including any unsorted source material within that quantity), not the directly reassembled live biomass of only planted species. Do not claim pure planted-species NDE, CE, SE or a causal resource-compensation mechanism. If author source proves an identity, add only that qualified identity and retain original already frozen numerical predictive results; do not mine other interpretations.

This is an independent QA branch stacked on PR #77, still Draft/unmerged; EDI 538 original trait timing remains HTTP403 access HOLD. No original primary trait-memory RC4 or 21-claim registry changes.
