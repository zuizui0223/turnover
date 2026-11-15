# GIFT v3.1 Origanum vulgare max-height 13 m: original-source diagnosis and mechanism for BIODEPTH heldout model failure

Checkpoint 2026-11-15. **This is an observed trait-database anomaly and original source audit**, discovered after the 7-site BIODEPTH one-axis height-FD predictive model unexpectedly had extreme error when Sheffield was held out. No plant biology selection mechanism is inferred from the anomaly, and the original unmodified model remains frozen.

## Original species source is an implausible outlier
- GIFT v3.1 original accepted plant `Origanum vulgare` (`work_ID=31210`) returns aggregated `Plant_height_max` `traitid=1.6.2` = **13 metres**, **n=14** GIFT source entries, original aggregated `coeff_var=2.102`, nine bibliographic reference IDs.
- Species is a small perennial herb. Independent horticultural/botanical published source ranges are:
  - [Kew Science POWO `Origanum vulgare`](https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:453395-1/general-information): **20–90 cm** in general botanical profile.
  - [Royal Horticultural Society](https://www.rhs.org.uk/plants/11923/origanum-vulgare/details): stems typically 20–80 cm, ultimate maximum height .5–1 m.
  - [Pladias original Czech flora species record](https://pladias.cz/en/taxon/data/Origanum%20vulgare): source height .25–.7 m.
- This confirms a **large GIFT-record versus botanical-source discrepancy**, *not* whether the 1997 published book itself contains an erroneous value. The source GIFT 13 m has not been silently converted, censored, or modified in the stored original result.

## Individual original GIFT raw trait sources (exact v3.1 API)
The original aggregated `13` is sourced from original GIFT nonaggregated `traits_raw` with `ref_ID=263`:
- ref **263**, Schönfelder & Schönfelder (1997), *Die Kosmos-Kanarenflora*: **GIFT raw record = 13 m**.
- ref **10224**, Artemov (2012) Siberian flora: **0.7 m**.
- ref **10247**, Schaefer et al. (2011) Azores flora study: **0.6 m**.
- ref **10302**, Fischer et al. (2008) Austrian flora: **0.6 m** (original GIFT has three rows at same value).
- ref **10315**, Tamis et al. (2004) Netherlands flora: **0.6 m**.
- ref **10320**, Australian PlantNET (2017): **0.5 m**.

GIFT original aggregated maximum 13 m is the maximum across all available source observations (official [GIFT original tutorial](https://biogeomacro.github.io/GIFT/articles/GIFT.html)), which is why even one source outlier dominates the aggregated maximum. The GIFT v3.1 original species-level reference metadata `references` include nine IDs; the six sources above were inspected raw with source-reference-scoped GIFT API. Thus **remaining three raw source records were not personally inspected in this source audit**.

[Verified exact GIFT3.1 source audit: GitHub Actions #43724523438](https://github.com/zuizui0223/turnover/actions/runs/43724523438), artifact #14165628693 digest sha256 70e74dafc27865b136c96241bbf415702cf04a715d5ddae108f158aff0ef8d02. Nonraw source summary `results/biodepth_2010_species_source_v0_1/gift_origanum_maxheight_anomaly_source_summary_v0_1.json`.

## Impact on original seven-site BIODEPTH source sample
- 174 planned-species-height-eligible plots across seven original sites, 521 plot×year original 2010 Community biomass responses; source-complete 150 plot sensitivity still showed issue. **20 Sheffield** eligible original plots, **10 with this species planted**, source species max-height distance in 10 exceeds 3 training-site SD and in six original plot cases exceeds the entire observed training feature range; maximum |z|10.71. Original Sheffield M1 (meanheight only) SSE45.47 and M2 (+height dispersion) SSE458.58. Original training FD conditional VIF≈1.34 (not severe collinearity).
- The combination of source-trait implausible 13 m **and** original Sheffield source 10 site plots is a compelling *measurement/prediction external validity failure mode*. It does not prove the 1997 flora printed 13 m or a specific upstream decimal-conversion bug.
- The previously frozen original seven-site M2-vs-M1 equal-site gain −123.09% (CI spans zero) is **retained as a valid result of the original GIFT traits and original model**, but no longer interpretable as direct evidence that ecological height differentiation itself is nonportable.
- A **post-result** fixed botanical-source sensitivity has been frozen before alternate model execution: replacing this one species' 13 m only with **0.9 m Kew upper range**, plus 0.7 m Pladias and 1.0 m RHS as transparent original botanical range checks, keeping the same 174 original plots, 521 original Community response cells, model formula and 7-site CV. This is exploratory data-quality stress testing, not a new confirmatory positive ecological finding.

## Do not over-claim
Trait record provenance is not a complete audit of every species in GIFT, GIFT max heights of other 87 original height species retain CV/sampling biases, and source records may contain unverified typographical/unit errors. A successful botanical correction would **not** constitute a universal FD–biomass ecological law, causal competitive mechanism, nor a test of the original 201 family×trait BIEN phylogenetic-memory rho. Original BIODEPTH exact richness high-support source gate (only 1/8 sites), sPlotOpen GIFT BIEN and NEON authenticated source gates remain HOLD.
