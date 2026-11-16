# TreeDivNet 2026: published supplementary access gate and woody source formula — v0.3

**Checked 2026-11-16** on the separate original-source Draft PR #55. The result preserves the earlier **328 original DS1×DS2 exact joins (11 sites)**, **186** woody-source-positive plots with ≥2 same-trait-axis source species and **38** represented trait species. Those constitute a **data-geometry PASS**, not a new independent original K/FD/woody-biomass effect.

## Original-source chronology: cannot verify per-plot years yet

- Read/MD5-verified the original public Figshare README.txt (file #61014400, MD5 `8fd3551d0a2b69fb9dca54b7cdbca422`, 8,130 bytes, 171 lines).
- README states that **DS1.xlsx contains plot-level biomass**, whereas **DS2.xlsx contains species-per-plot-level woody and trait values**, and reports woody mass in Mg ha−1. It has no original individual sample ID, per-plot tree/trait measurement year, or explicit species-row woody transformation formula. Do not interpret the 2026 article's publication date or experiment planting age as the date of measurement.
- Original journal methods state individual woody stock was derived from tree-diameter-based allometric equations, chosen by study site, aggregated at species and plot scales, then normalized per hectare. Original §2.5 restricts the 283 site-specific monoculture and 17 external trait substitutions to FDis, while other trait/biomass analyses used measured values. These are **author-study-method statements**, not independent verification of each original sample ID/time.
- Three additional publisher sources are explicitly advertised by the article: `fec70320-sup-0001-FigureS1-S12-TableS5-S6.docx` (Methods S2/S3), `fec70320-sup-0002-TableS1.xlsx` (site characteristics) and `fec70320-sup-0004-TableS3.xlsx` (original allometries). Bounded original publisher link attempts from BOTH official Wiley/BES Wiley hostnames returned **HTTP 403 for all three**. These direct-path access attempts do not establish that the original authors' supplements do not exist or that users with browser access cannot read them.
- Therefore the original **TRAIT INDIVIDUAL LINEAGE** and **≤2-year biomass–trait measurement timing** support criteria **remain HOLD**. No per-site same-year source match was invented.

## Plot response mathematical hierarchy: unresolved source conversion despite strong empirical identity

The previous immutable original Figshare numerical source row check demonstrated **321/328 exact plot matches** for:
`DS1 plot woody = arithmetic mean of the DS2 species-row woody observations in that plot`.
Only **135/328** originally joined plots had:
`DS1 plot woody = sum of DS2 species-row woody`.

New explicit posthoc source-only diagnostic tested an alternative mathematical reconciliation:
`DS1 woody = sum(DS2 species-row woody) / DS1 reported species_richness`.

| Original source check | Exact matches out of 328 plots |
| --- | ---: |
| Mean of DS2 species-row values = DS1 response | **321** |
| Sum of DS2 species-row values = DS1 response | **135** |
| **Sum of DS2 species-row values ÷ original DS1 species richness = DS1 response** | **321** |
| DS1 original reported richness = original DS2 number of rows | **322** |

The new denominator does **not** explain any of the six original plots with DS1 richness different from DS2 source species-row count (zero of six source discrepancies resolved). Of the seven remaining mismatches under the new formula, two are within 1% and five remain further apart. The source species-row mass formula is therefore **NOT uniquely verified by arithmetic**.

Do not call the original seven mismatches "data errors", or derive raw individual-tree biomass proportions by dividing/multiplying source DS2 rows. The original source grouping/area normalization may explain the numerical pattern but its physical meaning cannot be inferred from these aggregates. The **only admitted woody response** in a later model is **one DS1 Mg dry woody mass ha−1 per exact `site×block×plot`**, not a sum or synthetic duplicated DS2 response. All comparisons currently remain **source quality diagnostics only**.

## Conditional scientific claims and stopping rule

Source completeness (186 plots in 10 sites, some direct source measured trait values) is encouraging, but:
- The original published experiment already claimed mixture–woody biomass and functional-trait associations, so it is not an independent replication of its own published positive findings.
- Author-method support for measured species-plot traits is different from **individual-level sample-year provenance** and same-plot time-alignment confirmation.
- At most ~40 original tree taxa, far below a source-native **12 families ×20 species** trait-K study (≥240 species), are present. Neither species-phylogeny breadth nor original functional dispersion alone estimates family-specific trait memory.
- A current independent same-plot trait→woody-mass model is **not authorized** by the frozen original source contract. Do not search for positive subgroups or loosen year/provenance thresholds based on results.

**Decision:** current TreeDivNet source lane `PLOT_JOIN_PASS / PUBLISHER_SUPPLEMENT_ACCESS_HOLD / TEMPORAL_ALIGNMENT_HOLD / SPECIES_WOODY_SCALING_HOLD`. Do not fit new ecological effects on this study now; move any further work to an independently qualified dataset or to original author-supplied Methods S2/S3 + site-specific measurement chronology.

## Permanent evidence and what actually ran

- Prior original-data joins and source hierarchy are preserved in `results/treedivnet_2026_original_DS1_DS2_plot_source_gate_v0_2.json`.
- Original public README and official publisher supplemental access check [Actions #43869912574](https://github.com/zuizui0223/turnover/actions/runs/43869912574) **SUCCESS for source audit, with data access HOLD**; artifact #14227450972, digest `sha256:77559918aa11afcc3987f3256724d2ce2053bfb8e4dbdffc78b6a9a331105d25`.
- New original source 328-plot denominator test [Actions #43870526893](https://github.com/zuizui0223/turnover/actions/runs/43870526893) **SUCCESS**; artifact #14227206669, digest `sha256:440e36e925a09e72835db4c47db07a4cd965d6ef56daa7f7fd62c845be016633`.
- Nonraw permanent all-source aggregate: `results/treedivnet_2026_supplement_and_woody_reconciliation_v0_3.json`. Scripts `scripts/source/probe_treedivnet_wiley_methods_and_readme_v0_1.py` and `scripts/source/audit_treedivnet_woody_richness_denominator_v0_3.py`.
- Existing original programme global BIEN/sPlotOpen, historical 6-site BIODEPTH and NEON authentication gates remain HOLD. No raw study data, individual plot/species labels, or transient links committed. No `main` merge.
