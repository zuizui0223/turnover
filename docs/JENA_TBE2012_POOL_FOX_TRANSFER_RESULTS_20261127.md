# Jena TBE 2012: whole-pool transfer and strict species-disjoint sensitivity
2026-11-27; post-DivResource, retrospective qualitative hypothesis test, not a new independent field trial.

## Verified source and method
Wagg et al. 2017, Functional Ecology, 31, 2320–2329, DOI 10.1111/1365-2435.12945; original PANGAEA data 10.1594/PANGAEA.876725, SHA-256 458f61307df217d285c972f894ca5cf23709c3524dc6e13bb4d9dd3c26c2ab56. Fox (2005), DOI 10.1111/j.1461-0248.2005.00795.x. Equal initial sown proportions. 138 physical plots, 24 pool-specific monos, exactly 84 previously matched physical mixtures, 3 partially overlapping pools, each with 16 two-species and 12 three-species plots. Reproduced parent WLS CE/SE/NDE coefficients to <= 8.53e-14; all 84 original species-yield partitions and Fox identities pass, max arithmetic discrepancy 2.27e-13 g/m². The previous single physical Block field level is retained as HOLD; the 3 plot-prefix codes are proxies only. No new primary data or causal FD-only identification.
 
M0 planted richness categorical + source plot prefix, M1 adds existing preassigned high FD (wFDc 3–4 vs 1–2). Pool×richness equal weights; same heldout rows, weights and splits for all endpoints. Primary: 55,55,56 train and 28 test plots/fold after exact-composition purge. Secondary (explicitly post-result): all training plots containing any heldout species removed, 36,27,47 train, 28 each heldout. All three support and full-rank checks pass; zero train–test shared taxa; some training strata have just one low or high plot. No changes to endpoint definitions, FD contrast or test cohort.

## Actual aggregate results
Gain = 1 − SSE(M1)/SSE(M0). Positive = lower heldout error, not positive causal effect of FD. DivResource columns show the prior qualitative benchmark (different predictors, fold counts, and resource baseline; not a pooled meta-analysis).

| Endpoint | DivResource combined | Jena primary | positive folds | Jena species-disjoint | positive folds |
|---|---:|---:|---:|---:|---:|
| CE | -6.3744% | -0.5404% | 1/3 | -2.1088% | 0/3 |
| SE | +2.9219% | -0.3133% | 2/3 | -2.5187% | 1/3 |
| TDCE | +3.2575% | -0.4375% | 0/3 | -0.9957% | 0/3 |
| DE | +1.8871% | +0.9791% | 2/3 | -1.8811% | 2/3 |
| NDE | -7.2185% | -1.3114% | 2/3 | -6.0878% | 0/3 |
| B | not compared here | -1.0154% | 1/3 | -2.5337% | 1/3 |
| E | not compared here | +0.0649% | 2/3 | -0.5408% | 0/3 |

The frozen joint criterion (positive SE, TDCE, DE in all three Jena pools plus positive combined gains) **fails**. Only DE had a small positive combined gain among components in primary Jena, +0.9791%; even that was negative after strict shared-species removal (−1.8811%). The disjoint sensitivity has all seven combined gains negative. In strict DE, the three heldout gains were +1.1174%, +3.0574%, −12.0664%; in the primary comparison +4.4522%, +0.2986%, −5.0372%. This does not show that shared species *caused* the difference: training sample size and composition changed; strong imbalance of some surviving treatment cells limits interpretation. Positive training FD coefficients are not equivalent to lower prediction error for a new pool. SE/TDCE/DE gains in DivResource and Jena are not direct estimates of one identical biological parameter, because DivResource used binary grass/forb and stature differences with two disjoint pools while Jena uses the source high/low spatial/temporal trait pool design. Neither study supplies population-level confidence intervals for the new transport comparisons. One mono plot per species×pool (or species×resource treatment in DivResource) limits uncertainty in the derived reference. Fox components are statistical partitions of realized species yield, not a direct intervention on dominance or a demonstrated competition mechanism.

## Scientific decision
Do not elevate the small DivResource SE/TDCE/DE gains to a transferable biological law. Jena provides a distinct field-programme stress test of the qualitative hypothesis and does not support joint generalization. Earlier fixed Cadotte 2017 and Chen 452 author-study-ID CE/SE tests likewise do not establish positive SE prediction across broader designs (different predictors, endpoints and splits, no new pooled estimates). Overlap of the individual field programmes with the pooled Chen meta-analysis remains unverified. The methodological message is to separate within-experiment association, same-pool prediction and novel-species transport, and avoid declaring statistical partitions causal or preferentially pursuing the remaining positive metric after outcome inspection. Next independent study should freeze the disjoint-species split, measure coverage and baseline comparison before response access. Original K/rho → FD causal chain remains unproven. Preserve previous results and all drafts.

## Verified execution
- [Primary original-data run #45947136947](https://github.com/zuizui0223/turnover/actions/runs/45947136947), SUCCESS. Artifact 15175048037, sha256:860546520d03c68aeb9299ebd98ca1fbe5a94fae3c4e130f9904b20bc1a70ff9.
- [Strict species-disjoint run #45947260626](https://github.com/zuizui0223/turnover/actions/runs/45947260626), SUCCESS. Artifact 15175088170, sha256:988ca6f91acc2f3b1d7eb68b1fe6ee5fe0f169c68c0fca8527dd9b3e58a337e7.
- [Primary JSON](../results/jena_tbe2012_84plot_pool_fox_transfer_20261127_v0_1.json) and [sensitivity JSON](../results/jena_tbe2012_species_disjoint_sensitivity_20261127_v0_1.json). No source raw rows/IDs committed.
