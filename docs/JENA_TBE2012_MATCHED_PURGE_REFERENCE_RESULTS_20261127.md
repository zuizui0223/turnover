# Jena TBE: matched training subset reference for species-disjoint transfer (2026-11-27)

## Decision
The earlier species-disjoint degradation is **not unusually large relative to equal-size, exactly design-matched training subsets**. All seven combined endpoint gains and all 21 endpoint×heldout-pool gains fall within their respective central 95% descriptive reference ranges. The earlier failure to reproduce DivResource's qualitative component-transfer hypothesis is unchanged. This diagnostic does not demonstrate that training size alone caused the degradation, nor does it establish a species-sharing effect.

## Original source and frozen comparison
Original Wagg et al. (2017) Jena TBE, PANGAEA 876725, SHA-256 458f61307df217d285c972f894ca5cf23709c3524dc6e13bb4d9dd3c26c2ab56; 84 physical mixture plots, 24 original pool-specific monos, one field programme. Both prior whole-pool and species-disjoint scores reproduced, including every fold M0/M1 SSE. In each of the 3 folds, the original 28 heldout plots were unchanged; training sizes after identical-composition purge were 55,55,56 and strict shared-species purge sizes 36,27,47. Each of 2000 random reference draws samples without replacement from the ordinary training set within the exact original pool×richness×assigned high/low FD×plot-prefix coding cells, matching the strict training cell counts. The three folds are sampled independently for a combined descriptive reference, not independent field experiments. Same frozen M0/M1, same training/heldout weights, same seven signed endpoints. Every draw passes exact design counts and model rank.

## Actual verified results
| Endpoint | Ordinary gain | Strict species-disjoint | Reference median | Central 95% reference range | Fraction reference gains ≤ strict |
|---|---:|---:|---:|---:|---:|
| B | -1.015% | -2.534% | -1.627% | -5.202% to 0.757% | 30.350% |
| E | 0.065% | -0.541% | -0.285% | -1.070% to 0.256% | 25.850% |
| NDE | -1.311% | -6.088% | -3.242% | -7.059% to 0.530% | 9.400% |
| CE | -0.540% | -2.109% | -1.330% | -3.203% to 0.219% | 24.000% |
| SE | -0.313% | -2.519% | -2.102% | -6.188% to 0.221% | 40.600% |
| TDCE | -0.437% | -0.996% | -1.221% | -4.504% to -0.193% | 57.950% |
| DE | 0.979% | -1.881% | 0.578% | -2.830% to 3.055% | 7.200% |

DE and NDE have relatively low strict gains (7.2th and 9.4th percentiles respectively), but neither falls outside its reference range. Strict DE −1.8811% vs median +0.5780%; strict NDE −6.0878% vs median −3.2418%. All individual-fold component gains also remain in range. These distributions are conditional reference ranges, not confidence intervals, hypothesis-test p-values or estimates of a sampling population effect. The finite possible exact subsets per fold are 144, 829,440, and 2,160 (combined 257,989,017,600); draws can repeat subsets, especially the first fold. Among 2000 draws, the numbers with zero training plots sharing heldout taxa were 11,0,0; the combined median fraction of training plots sharing a heldout taxon was 14.55%. The strict sample is part of the possible sample space, even when it is not sampled randomly. Thus the matched reference is not a forced-overlap comparison.

## Limits and implications
The results are compatible with diminished support and nonrandom changes in training composition; matching design cells and counts cannot fix the unmeasured characteristics of a species roster or isolate an overlap intervention. Some strict training strata have very small cells. No inference of a causal FD-only effect, a causal species-sharing effect, or a general superiority of any component. No resampling of the singleton monoculture reference yields. The original physical block codebook remains HOLD; plot-prefix proxies are not certified physical randomization. This is a post-result conditional comparison in one experiment; previous DivResource, Jena, Cadotte, Chen, BIEN/AusTraits and Evolution RC4 results unchanged. Do not repeatedly search for a favorable component in this cohort.

## Reproducible execution
- [Frozen protocol](JENA_TBE2012_MATCHED_PURGE_REFERENCE_FROZEN_20261127.md).
- [Original-data run #45951493008](https://github.com/zuizui0223/turnover/actions/runs/45951493008) SUCCESS, all 6000 train-subset fits per two nested models, original artifact 15177100761, digest sha256:8e67e8772e85cd21e9d793cfec085645e234231dc32c0c80bb7417c29c21d5f3.
- [Complete aggregate results](../results/jena_tbe2012_matched_purge_reference_20261127_v0_1.json) (all seven combined and per-fold gains and M0/M1 SSE reference summaries). Raw original records not released.
