# Jena 2003 within-sown-richness positivity and FG-effect sensitivity — analysis contract v0.1
Date: 2026-11-15 (JST). **Retrospective/post-result exploratory robustness test**; original May 2003 group slope already known. This is NOT a new preregistered or confirmatory independent experiment.

## Question
Can the positive 2003 May relationship between number of planted functional groups (FG) and sown-species harvested aboveground dry biomass still be observed *within the same exact planted species richness level*? Is the original linear `log2(richness)` adjustment extrapolating across unsupported richness/FG corners?

## Original fixed sources
- PANGAEA 846317 `biomass2003.tab` SHA256 `70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079`, 820 rows, 82 original experimental plots, 4 quadrats+mean × 2 harvest campaigns; primary response is only official `Repl=="mean"` dry weight for sown plants in May, `log1p(g/m²)`.
- Original Jena plot allocation `plotinfo.txt` SHA256 `7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70`, 82 plot codes, original field blocks B1–B4, treatment richness and planned FG count.
- No raw data committed to Git. Original response and existing models/PR #40 remain unchanged.

## Outcome-blind design support from allocation metadata (before *this test* outcome fitting)
- 1-species: 16 plots all 1 FG; 60-species: 4 plots all 4 FG. Neither has within-richness FG contrast.
- 2-species: 16 plots, FG1 8 and FG2 8.
- 4-species: 16 plots, four FG levels ×4.
- 8-species: 16 plots, four FG levels ×4.
- 16-species: 14 plots, FG1 2 and FG2–FG4 4 each.
- Therefore **n=62 plot intersection with within-richness FG positivity**. All 62 retained regardless of any outcome; original 82 used as source support sensitivity with 1 and 60 fixed levels.

## Fixed models (do not select by p values)
1. Historical replay `log1p(May sown mean) ~ 1 + log2(planted richness) + FG + block` for all 82.
2. **Full discrete-richness sensitivity** `log1p(May sown mean) ~ 1 + C(planted richness) + FG + block`, same 82 plots; richness references 1 species, fixed effects for 2/4/8/16/60.
3. **Supported-region primary exploratory contrast** same categorical richness model restricted to richness 2/4/8/16 (n=62), with original block fixed effects. FG slope is per additional planned group *within* richness levels, but not a randomized isolate of FG count independently of original group/species composition.
4. Same restricted 62 plots with `log1p(Aug sown mean)`; and original official May **combined sown+non-sown** mean response only on complete cases (no non-sown missing filled as zero), preserving sample support.
5. Alternate raw-scale May sown biomass per m² with categorical richness + block, and leave-one-richness-level-out refits (2,4,8,16); all *descriptive*.
6. Two-sided HC3 robust Wald CI and p for regression FG coefficient, plus 4,000 draws block-stratified plot bootstrap for May FG 62-plot coefficient (seed 20261119). Each draw must preserve original separate plot identity, and stay full-rank; at least 95% valid draws required.
7. Two-sided 9,999 **within-richness × block label randomization**: permute the realized responses within each supported richness×block stratum (at unchanged group allocation), recalc residualized FG slope, exact same baseline X. This tests conditional exchangeability and is a **design-based *approximation***, since specific species composition, not just FG, was assigned. Report the result beside parametric methods, do not claim causal pure FG mechanism. RNG seed 20261120; `p=(1+#{|beta_perm|>=|beta_obs|})/(9999+1)`.
8. Descriptor: counts per richness×FG×block; effective partial X rank, coefficient support and leverage; predeclare no outcome-based exclusions.

## Interpretation rules
- Positive slopes in the within-richness 62 subset would establish only *association of treatment FG richness after controlling exact species number*, not evidence of mechanism or generalizable functional diversity–ecosystem production law.
- If the 62-plot HC3 interval includes zero, label uncertain even if the 82-plot categorical or log-richness fit is positive. Randomization inference is exploratory and can disagree; do not select the most favourable procedure.
- Do not treat positive May and nonsignificant August as proof of seasonal interaction; prior direct paired test p=0.088 is unchanged.
- Neither Jena study tests phylogenetic temporal rho, plant functional diversity Rao Q, total whole ecosystem biomass, or multiregion macroecological generality. Earlier PRE_OUTCOME HOLD sPlotOpen/GIFT/BIEN and NEON AUTH HOLD remain unchanged.
