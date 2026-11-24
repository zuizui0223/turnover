# BioCON 2021 absolute biomass and source-component identity: verified audit (2026-11-24)

## Result before interpretation

This **independent source/units audit** reopened only author-original figure dataset component values, not original model predictors, new outcomes or any fitted FD results. Exactly the same **46 originally qualified August-2021 BioCON E141 main mixture plots** (36 with four species, 10 with nine species), plus **128 same-season original mono plots** were verified with Figshare v3 original source MD5 and original author's README and R calculation-code MD5s.

| Source row class | Plot count | Original 16-source-species mass columns | Physical original AbovegroundTotal (B) and source species accounting |
|---|---:|---|---|
| Four-species mixtures, 2021 August | **36** | **0/36 have any original species-specific biomass reported** | Original physical B is present; its equality with planted-only sum is **not auditable** |
| Nine-species mixtures, 2021 August | **10** | All 9 sown masses reported in **10/10** | Source B equals the sum of the 9 sown species in **10/10** |
| Original physical monocultures, 2021 August | **128** | Original planted species mass reported in **128/128** | Source B equals that species mass in **128/128** |

These are exact source identities within fixed absolute tolerance 0.001 g m−2 plus relative 1e−5. They do **not** establish a biological mechanism. An original source-named separate "Total Biomass" field differs from original "AbovegroundTotal Biomass (g/m^2)" in **all 174** source-auditable rows (36+10+128). Neither adding nor subtracting original "Miscellaneous Litter (g/m^2)" gives a simple equality in those 174 rows. Do **not** silently replace the source B endpoint by either "Total Biomass" or "Miscellaneous Litter", and do **not** assume litter means unsorted species.

Huang et al. (2025, Nature Communications DOI 10.1038/s41467-025-62691-0) already reported original physical community biomass samples, while **4-species 2006–2021** and 9-species 2005–2006 **species-specific biomass** was not sorted, with source-published reconstruction of species yields from cover. Our original 2021 4-species source shows exactly this missing species-level mass. The previously fitted response B is the recorded **plot-total aboveground mass**, and original mono controls are same-month/context plot totals, not model-filled 2021 species masses.

## What remains valid

Original parent [PR #77](https://github.com/zuizui0223/turnover/pull/77) retains exactly the same previously frozen 46 original plot/source rows, source 14-species secondary native-SLA coverage, two original mono replicates per source species/treatment, six CO₂ rings and original held-out composition folds. No numerical re-fit or model change occurred here. Earlier heldout prediction gains remain **−3.89% for physical B** and **−9.09% for signed plot-total NDE=B−E**, with all published six-ring uncertainty intervals spanning zero. This audit does not add another biological test or independent field experiment.

## What requires stricter wording

Because all **36** original 4-species mixtures lack directly source-reported species-specific mass, raw source accounting cannot independently prove that their B contains only the originally planted taxa. The original plots were designed and weeded but do not by themselves prove perfect exclusion of any unsorted/extraneous biomass in a sample. In result captions and ecology discussion, call B **original author-provided plot-total aboveground biomass**, E **equal-seeding-weight original species-mono plot-total expectation**, and NDE **signed plot-total excess above that expectation**. Do not say this reproduces exact planted-only Loreau–Hector CE/SE or that FD changes species-specific resource-use complementarity.

Neither PR #77's source secondary SLA time limitation (official EDI 538 direct source HTTP403) nor its one field experiment/six ring independent-unit limitation is resolved. Even a confirmed numeric identity in 138 reported source plots does not authorize a new FD-only causal mechanism or K/rho→FD→B mediation.

## Provenance

- [Original-data source integrity/identity QA](https://github.com/zuizui0223/turnover/actions/runs/45327786099) successful, [PR replay](https://github.com/zuizui0223/turnover/actions/runs/45327814717) successful.
- Author source MD5: CSV 8185b8effca37c8740ad065c53eb75d2; README 9ce824a94a0ad0ab455a9cfcc1589670; R source 3166d7b1f8ee36e974812b3c7ac2cb48.
- Nonraw artifact #14890287704, SHA256 572d3826782835e402328894de503fb60e816d617c0d7bcef7101187246b9565.
- [Permanent counts and interpretation guardrails](../results/biocon_e141_original_2021_biomass_components_accounting_v0_1.json).
- Source audit script: scripts/audit/biocon_e141_2021_mass_component_source_identity_v0_1.py. No source sample row, individual biomass or taxon state was written into the branch.

**Decision:** Preserve prior numeric scores; downgrade any wording that identifies all 46 B values with measured sown-only component sums. Original CE/SE causality not established. Keep Draft/unmerged and primary Evolution RC4 untouched.
