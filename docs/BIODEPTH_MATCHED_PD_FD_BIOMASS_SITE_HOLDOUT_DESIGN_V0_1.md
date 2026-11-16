# BIODEPTH 2010 source-matched phylogenetic breadth → FD and incremental biomass prediction

**Outcome-frozen:** 2026-11-16 **after** the original 2010 height-FD→biomass model, Kew oregano correction and 999 guild-label null were observed (PRs #46–48), **after** the source-only V.PhyloMaker2 tree coverage and joint-GIFT/GBOTB support gates passed (PRs #49–50), but **before any new phylogenetic-distance predictor and its biomass/FD predictive outcomes are opened**. Therefore this is strictly a **retrospective exploratory NEW association test**, not a prospectively independent experiment.

## Source population fixed prior to new response

- Exactly the **150 original 2010 planted BIODEPTH plots across seven original field sites** meeting all prior original-height source rules AND ≥3 jointly GIFT-height + GBOTB S3 species, ≥80% original sown taxa joint coverage. Source site totals locked **Germany26, Ireland26, Portugal8, Sheffield20, Silwood24, Sweden18, Switzerland28**. Greece excluded (no original GIFT trait coverage). **84 original height+S3 source species across 17 families; 78 native tips and six S3 grafted tips.**
- The earlier 174 plot×source-corrected-height dataset is a *different target population*. Never compare the 150-cohort model prediction directly to the historical +3.83% number as if matched.
- Original 2010 Hector Community source aboveground standing dry biomass, repeated three source years; one original numeric absence among 174 source plots was reported. The predeclared 150 plot×3 possible responses may have 0–1 missing source records: use complete source `Community` numeric nonnegative outcomes, retain zeros, require **≥440** source plot-years; report missingness. No 2005 Shoots response, no year-specific Species abundance weights.
- Source original 103 genus+species; GIFT 3.1 `Plant_height_max` 88 bibliographically traced positive species; one **Origanum vulgare** 13m source outlier repaired to Kew 0.9m in ALL models (post-result source sensitivity known), no other substitutions. GIFT source fingerprint fixed.
- Source original V.PhyloMaker2 `GBOTB.extended.TPL`, commit `7af3fb5152f691af2e4ec9d5e2e467d1b50505e9`, scenario `S3`, native and bound statuses. All numeric patristic distances are derived from this tree in the runner and not tuned to biomass.
- For every source plot, calculate from the **exact same jointly present species** (equal initially planted weights, original planted richness remains an independent covariate): `h_i=log(GIFT height m)`, `CWM=mean(h_i)`, `FD=mean_{i<j}|h_i-h_j|` and `PD=mean_{i<j}patristic(i,j)`. Population is fixed before any source Community response is read.

## One primary predeclared site-transport estimand

Does original **community phylogenetic breadth** provide positive additional out-of-source-site predictive information for measured Community biomass **after** planted species richness, original functional-guild identities, source year, mean log height and log-height dispersion are present?

- Y = `log1p(original 2010 Community aboveground biomass g/m²)`.
- Baseline **M2**: `1 + log2(original planned richness) + log2(richness)^2 + original sown grass/forb/legume flags + year2 + year3 + training-standardized CWM + training-standardized FD`.
- Candidate **M3**: M2 + one **training-standardized source-tree MPD_PD** covariate. Standardize all continuous predictors using TRAINING source site records only and use those parameters on heldout site. Original M2 has *no site intercept*, because the held-out site has no learned identity. All models are OLS, fixed design, no feature selection or tuning on biomass.
- Exactly one fold leaves out each whole original field source site. Gain at heldout site `G_s=1-SSE(M3,s)/SSE(M2,s)`. **Primary (T)=equal-site average gain**. Bootstrap **10,000** whole sites, fixed seed **20261116**; positive support only when mean gain>0, 95% bootstrap lower>0 and ≥5 of seven source sites individually gain>0. Retain negative outcomes, no deletion of difficult sites.
- Check all seven training designs full rank and positive nonconstant PD before reading Community outcomes. If rank not identifiable, status `HOLD` with source design count, not alternate model.
- No inference of evolutionary trait-specific K from PD; this is phylogenetic *breadth* and cannot by itself establish evolutionary memory strength or causal biomass relationships.

## Secondary source-prediction check (one specification only)

Does PD improve out-of-original-field prediction of planted one-axis height **FD itself**? Use **exactly 150 unique original planted plots** (not three repeated biomass years). Baseline **F0** = intercept + original `log2(sown richness)` and squared + three original planned guild indicators + train-standardized mean log height. Candidate **F1** = F0 + train-standardized PD. Same leave-whole-source-site-out seven folds and `1−SSE(F1)/SSE(F0)`, same site-level bootstrap 10k / seed 20261116. This is a *secondary exploratory* structural association; a positive FD prediction does NOT demonstrate a positive biomass effect or adaptation. Never optimize predictor scale based on this or the primary outcome.

## Single mandatory sensitivity

Redo primary M3-vs-M2 study with **only original backbone-native 78 height/tree species**, same fixed rule ≥3 native and ≥80% original plot planted taxa. If fewer than **100** plots across at least **five** source sites each ≥8 plots, report `NATIVE_ONLY_UNDERPOWERED_HOLD`; otherwise report identical seven-site-style site-equal estimated gain and uncertainty on its *separate* fixed cohort. Do not compare point estimates as if two cohorts were identical.

## Strict claims, provenance and stopping

No original old BIEN/sPlotOpen 201 family×trait K/rho data are paired to these plots. A positive M3 test is observational predictive value, not proof of a phylogenetic K→FD→biomass causal path, natural selection, or globally universal BEF law. Source GIFT heights are study-external maxima, not directly measured canopy heights. Seven sites are original BIODEPTH field experiments, not independent worldwide ecosystem types. Site bootstrap uncertainty is descriptive under only seven clusters.

Do not modify frozen old results or source repair. All new preflight thresholds are explicitly recorded above. Stop on source drift, source hierarchy/plot roster disagreement, rank deficiency or joint-cohort mismatch; never swap source taxa or remove a site post-outcome. All original BIODEPTH 6-site exact-richness, original BIEN/sPlotOpen and NEON token gates remain HOLD.

**Outputs:** original source hashes, exact sample denominators/sites; seven per-field PD-increment gains and bootstrap interval; secondary PD→FD original plot-only scores; native-only sensitivity status; reproducible source-pinned scripts/Actions. Commit **nonraw aggregate only**, not raw original ecological rows or trait matrix.
