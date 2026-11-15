# Jena PANGAEA 923591 longitudinal source-only crosswalk v0.1
Frozen 2026-11-14 **before opening any new 2004–2012 FD–biomass effects**.

## Purpose and boundary
Primary macroecological NEON RELEASE-2026 DP1.10023.001 × DP1.10058.001 is AUTH-HOLD since June 2026; legitimate API requires a NEON account token. Separately inspect whether the already available Jena 2003–2012 panel supports a *temporal transport* test of functional traits. Jena remains **one grassland experiment**, not multisite validation.

PANGAEA [923591](https://doi.org/10.1594/PANGAEA.923591) public attachment hashes from verified GitHub Actions run 43576995999:
- traits.st.zip SHA256 5ae74c473ff2e36861f137f4fc8a28740725a90dda9e265350fd45bcb38996c5
- predictors_raw.zip SHA256 4af2ccca7b85b7a15b47ace87acfe0386feab79da51d3d5f67b3cf6034442e4b
- biomass02_12.zip SHA256 aa4e4904c200e4a7d35cfd713a47969b3c08f014bccfe330cefe245ee1e875db
- CoverMain-JenaExp2003-2015all.zip SHA256 40a4a88bbf324cf1a5e8a16086f73aa5c847b7bd17380708f835f3a1a9056490
- Plot information original DOI 846317 ancillary file hash 7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70
Always cite original sources. PANGAEA warns that dataset 923591 lacked the normal final author approval. Previous 2020 original research already studied 41 traits and 42 ecosystem functions; 2023 published Matters Arising disputes the inference, emphasizing mechanistic trait selection.

## Tier 0 (execute first)
- Inspect CSV column naming and **key semantics only**: exact plotcode vs plot ID; year, season/month, subsample and target.biomass columns; distinct plot keys and year/month ranges; predictors FD_h1, FD_sla, FD_leafN, FD_SeedsTCW, FI counterparts; code missingness.
- File-level SHA256 and source row counts; count candidate plot × year × season join intersections with externally measured sowing richness and number of functional groups. **Do not estimate biomass–FD effect or output correlations.**
- Require ≥50 unique exactly crosswalked plots, ≥4 observed years, ≥100 valid plot-year-season paired cells and ≥60% available each prespecified `FD_h1`, `FD_sla`, `FD_leafN`, `FD_SeedsTCW` candidate (before using any effect). Source overlap and data semantics must be reviewed before modeling.
- Realized FD is from 3×3m observed vegetation and may be mechanically related to biomass via species abundance; evaluate study-level predictor independence, avoid causal or forecast claim.
- If the source structurally qualifies, **separately freeze** any future-year prediction model, common outcome years, and missingness thresholds BEFORE reading numerical target.biomass into a fitting script. No post-outcome trait selection or search for significant axes.

## Future interpretation (not a result)
A successful long-term Jena plot×year crosswalk would enable a *within-one-site temporal generalization* comparison, not biological independence from the published original analysis or evidence that trait evolutionary memory predicts biomass. Neither the earlier sPlotOpen HOLD nor NEON AUTH HOLD is changed.
