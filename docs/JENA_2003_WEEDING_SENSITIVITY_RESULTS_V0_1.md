# Jena 2003: completed sensitivity to the specially weeded quadrat

Date: 2026-11-14. This is a post-result exploratory sensitivity analysis, not a preregistered replication. Original BIEN/AusTraits results, original Jena estimates and main branch are unchanged.

## Main finding
The positive May point estimate is not removed when the specially weeded fourth quadrat is omitted. However, its uncertainty interval then includes zero. Directional consistency and statistical robustness must be reported separately.

All comparisons retain the same 82 plots and the original model: log1p(sown-species standing aboveground dry biomass, g/m2) ~ log2(sown richness) + functional-group richness + original field block. Arithmetic means are formed before log1p.

| May response | FG coefficient | HC3 95% interval | HC3 two-sided p |
|---|---:|---:|---:|
| Official mean of quadrats 1–4 | +0.167891 | +0.004585 to +0.331196 | 0.043905 |
| Ordinarily weeded quadrats 1–3 only | +0.172590 | −0.004330 to +0.349510 | 0.055877 |
| Extra-carefully weeded quadrat 4 only | +0.166053 | −0.021402 to +0.353509 | 0.082531 |

The 4,000 block-stratified paired-plot bootstrap interval for the ordinary-only May coefficient is **−0.000119 to +0.352749**. Do not round the negative lower limit to a strictly positive value.

The direct May ordinary-minus-official coefficient contrast is **+0.004699**, HC3 interval **−0.036441 to +0.045839**, p=**0.822862**. The similar point estimates do not support attributing the positive May coefficient specifically to quadrat 4, but this is not a formal equivalence test or a randomized test of weeding effects. A change from p=0.044 to p=0.056 must not be described as an effect disappearing.

## August and multiple comparisons
August FG coefficients are **+0.044329** for ordinary quadrats and **−0.183734** for quadrat 4. The directly fitted careful-minus-ordinary contrast is **−0.228063**, HC3 interval **−0.421941 to −0.034184**, nominal p=**0.021136**; paired bootstrap interval **−0.409257 to −0.058244**.

This is one of four previously specified paired contrasts. A separately labeled, post-result Holm multiplicity sensitivity gives adjusted p=**0.084545** for the August contrast. Treat it as an exploratory hint about sampling/management context, not established evidence that extra weeding changes the diversity–biomass relationship.

The ordinary-quadrat August-minus-May FG contrast is **−0.128261**, HC3 interval **−0.323548 to +0.067026**, p=**0.198000**. Thus the earlier caution that seasonal differences are unresolved remains appropriate.

## Interpretation boundary
- Quadrats 1–3 were ordinarily weeded, not unweeded controls. Quadrat 4 differed in weeding/handling and spatial position; the contrast does not isolate a randomized weeding effect.
- Weed biomass is published only as a four-quadrat plot mean, so quadrat-specific weed mediation cannot be estimated.
- The response is biomass of sown plants, not weeds plus all vegetation, roots, detached dead material or annual NPP.
- Functional-group richness is a planned categorical diversity measure, not the separate four-axis continuous FD benchmark. No phylogenetic-memory effect is tested here.
- All coefficient intervals are exploratory marginal intervals. The additional Holm diagnostic does not convert the analysis into confirmatory evidence.

## Execution and reproducibility
1. The previous delivered script was deployed unchanged: SHA256 **982f9f26432fbd3b9751c2dce53f42fad384f478c62f1a44a67efda14d123b9b**.
2. Original public TSV and plot information matched their pre-existing SHA256 values. All 820 source rows and 82 plot identities were retained. Reconstructed four-quadrat means agreed with publisher means to at most **0.0005 g/m2**.
3. The original May and August coefficients were numerically reproduced, **13 tests passed**, and **4,000/4,000** bootstrap fits were full rank.
4. Verified first run: **43604293513**, job **132475494199**, artifact **14118070606**; downloaded artifact SHA256 **ccefd87a8eb26b659b8e30f29c760586e553a138bdfc58f791d2d6fa3db846a4** matched GitHub.
5. Public input bytes were retained separately in a short-lived, attributed artifact—not committed to Git—to avoid another source-access blocker. Source-cache run **43604642543**, artifact **14117253081**, ZIP SHA256 **9646b7dade486a2f3cde7a08d89124d03570841096d886834a1a894956a270a2**. Both individual source hashes were reverified after local extraction.
6. Local replay reproduced all ten estimates, p-values, HC3 intervals and bootstrap intervals with **maximum difference 0**. A separate pandas/statsmodels reconstruction, importing none of the production helpers, agreed across all ten regressions and contrasts to **8.22e−15**.

Aggregate result: `results/biomass_jena_2003_source_v0_1/weeding_sensitivity_v0_1.json`.
Code and tests: `scripts/analysis/jena_weeding_v0_1/`.
The reproducibility bundle supplied in the conversation includes original public inputs with citation, analysis code, tests, complete coefficients, logs and independent validation.

## Source attribution
Buchmann, N.; Temperton, V. M. (2015). Aboveground community and species-specific plant biomass from the Jena Experiment (Main Experiment, year 2003). PANGAEA. https://doi.org/10.1594/PANGAEA.846317. CC BY 3.0.
Original allocation: https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt
