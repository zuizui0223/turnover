# Cadotte 2017 single-experiment FD / selection / complementarity pilot

**2026-11-20 freeze before ANY new *model fitting*, but not fully outcome-blind.**
This source is identified *after* publication and after online sample rows and original author-positive results were visible. All inference is explicitly **retrospective descriptive**, not pre-registered prospective validation and not new independent confirmation of Cadotte's published finding.

## Data and provenance

- Original paper: Cadotte (2017), *Ecology Letters*, DOI [10.1111/ele.12796](https://doi.org/10.1111/ele.12796). It already found trait dissimilarity relates to complementarity and selection in opposing ways.
- Source-derived CC0 public deposit at [Zenodo 5022435](https://zenodo.org/records/5022435), originally Dryad DOI 10.5061/dryad.627rt. ORIGINAL exact files and displayed MD5:
  - `comp_select.csv`: `079c2ef9fdf62a9b3c6bd40877d3e0d2`; `COMP,SELECT,DeltaY,SPP_NUM,Biomass,PD` + plot ID
  - `planted.csv`: `4e2bb17177a7f2be0347182b1f60ce27`; pre-sown species membership columns per plot ID
  - `raw_biomass.csv`: `73de6c8957f5a1c7729898057c4c339b`; `Plot,Real.rich,PD,biomass`
  - `species_traits_final2016.csv`: `c4211aacdf298f9c2bee62dca95ee9f6`; species-specific original *SLA* and *field.height* among other traits.
- Deposited source metadata preview indicates **40 mixtures with NDE/COMP/SELECT**, **14 trait species**, ~89 biomass plot rows; all *published* counts are preflight expectations and must be verified from bytes. This is only **one Canadian plant assemblage experimental dataset**; there is no site-level independent holdout and no generality to other sites.

## Frozen source gate before any outcome model fit

1. Official Zenodo anonymous-download source-only preflight with original MD5, file byte limits 20 KB/each, unique plot identifiers, original CSV required header checks and **exact plot ID join**, no automatic fuzzy matching.
2. `COMP+SELECT ≈ DeltaY` tolerance ≤0.00001 absolute original units and `comp_select.Biomass` versus `raw_biomass.biomass` tolerance ≤0.15 original units (the latter file has two decimal rounding). A discrepancy yields hard `SOURCE_IDENTITY_HOLD` before regression. All matched `SPP_NUM >=2`, and planted source roster size/meaning must be audited explicitly; if differences between planted vs realized richness, report them and use ***planted*** source richness as the baseline covariate.
3. Raw species trait values `SLA` and `field.height` must be finite and strictly positive in all source-selected mixture species. One recognized planted taxon code must map to exactly one source taxon; no external TRY substitutions. At least 30 independently identified mixtures with exactly matched trait and response support and 10+ original trait species.
4. Original NDE and components can be negative. No log(NDE), offset, signed log or selection of favourable response transforms. Retain all mixture plots except missing source data; no outlier removal based on response magnitude. Plot composition fingerprint = sorted original sown species IDs; all identical fingerprints across plots must stay in same held-out fold.

## Frozen pilot comparison (if source gate passes)

**Same exact plot set**, same covariates and same held-out composition folds for three outcomes:
- `absolute_biomass` = original total community biomass (from comp_select, crosschecked against raw_biomass);
- `net_diversity_effect` = original `DeltaY` (cannot equate with proportional NDE);
- `complementarity` = `COMP` and `selection` = `SELECT` as declared supplementary endpoints.

**Fixed trait diversity:** equal-pre-sowing-planted-species mean pairwise Euclidean distance across **exactly TWO** traits, log(SLA) and log(field.height), scaled by training-fold species reference SD determined only from the training mixtures' species pool. No functional trait outcomes used to select axes. Identical 2D pairwise-FD definition in all endpoints.

**Baseline M0**: intercept + log2(planted richness) + equal-planted-species CWM log SLA and log height, with each CWM centered/scaled using source-train-fold only. **M1** = M0 + pre-sown two-trait FD. Unweighted OLS, no model/regularization hyperparameter searches. Predict all left-out original *species-composition* groups. Model rank check on all folds and 30+ qualified plot support; no response-dependent fold deletion. No multiple-comparison search among individual traits, species or site subsets. For each target, report `1−SSE(M1)/SSE(M0)` (dimensionless) across identical plots. Primary diagnostic comparison is the **paired gain difference** `gain_NDE − gain_absolute_biomass`. Summarize COMP and SELECT only in the prespecified source order.

Uncertainty: 1000 composition-cluster paired bootstrap draws of held-out squared-error vectors (seed **20261120**), not resampling species pairs as independent, reporting percentile 95% CI of paired gain contrast and response-specific gains. Use source-fold predictions, no extra model fitting within bootstrap. Exploratory effect not hypothesis-testing based on unobserved data selection: the original authors' positive COMP or negative SELECT directions were already published and displayed; significance must be called **descriptive**, never independent confirmatory validation. If the original source has fewer than 30 qualified mixtures, no effects are fitted.

## Interpretation and stop conditions

Even if FD boosts NDE prediction, this does not identify a causal **FD intervention**: species identity, abundance interactions and treatment composition are inseparable. Mixed assemblages may have been planted experimentally, but continuous FD is a deterministic attribute of species membership and is not manipulated independently. No environmental-context interaction identifiable because there is only **one study site**. The wide 21-experiment forest network and 216/336 PaNDiv experiment datasets remain separate SOURCE_ACCESS_HOLD (PR #68); do not pool a small Cadotte sample into a claimed meta-analysis or global FD law.

**No raw original species/plot rows are to be committed** in result paths. Artifact only reports aggregate source qualification, summary model performance and group-bootstrap uncertainty with explicit single-site/retrospective restrictions. Source file records may be transiently read by GitHub Actions and checked via MD5. No overlap with BIEN/K and no phylogenetic memory mediation is inferred.
