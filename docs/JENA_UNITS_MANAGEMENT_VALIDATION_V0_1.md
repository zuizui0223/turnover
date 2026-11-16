# Jena biomass unit and sampling-management validation v0.1
Date: 2026-11-14. Post-outcome validation; NOT prospective confirmation or a new independent experiment.

## Single goal
Resolve whether the positive May 2003 functional-group association and the quantitative FD panel depend on ambiguous biomass units or the unusually carefully weeded fourth subsample.

## Sources and boundaries
- Preserve all PR #40 original result files, four trait choices, 2003–2007 / 2008–2012 split and original models.
- 2003 official PANGAEA 846317: dry biomass g/m², 82 plots, four harvested rectangles plus provided mean per campaign. Metadata explicitly states subsample 4 was in an extra carefully weeded area. Source hash 70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079.
- Compiled PANGAEA 923591 biomass02_12.zip: hash aa4e4904c200e4a7d35cfd713a47969b3c08f014bccfe330cefe245ee1e875db; original plot info hash 7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70.
- Official collection PANGAEA 866358 lists annual main-experiment sources: 2003 846317, 2004 846319, 2005 846348, 2006 846582, 2007 846583, 2008 846532, 2009 866304, 2010 866305. Download exact published year datasets, record SHA256 and source headers. Do not infer that 2011–2012 is validated from earlier years.

## Fixed validation comparisons
1. Join compiled and official individual observations by exact plotcode × year × season × replicate, never nearest value. May/June→spring, August/September→summer. Reject duplicate source keys and ambiguous month mapping. Zero is valid; -9999 and nonfinite are missing.
2. Report raw identity and candidate area/unit conversion factors 1, 10, 0.1, 100, 0.01. This is only a unit diagnostic; report all factors, no optimally fitted rescaling. Compare at absolute tolerance 0.051 g/m² and relative tolerance 1e-6, and report maximum differences. A mismatch remains unresolved, not overwritten.
3. Reproduce the 82-plot official mean estimates; separately compare equal-weight mean of subsamples 1–4 and 1–3, and subsample 4 alone. Require all planned subsamples, otherwise report affected counts and stop that comparison rather than fill zeros.
4. Use the original model log1p(sown dry biomass g/m²) ~ log2(sown richness) + functional-group richness + block for May, August, and the paired August-minus-May response. Report HC3 estimates and paired 2,000 within-block plot bootstrap intervals (seed 20261117), retaining same plot multiplicity across all variants.
5. Directly estimate the change in FG coefficient induced by excluding subsample 4 and the subsample4-versus-ordinary contrast. These are correlated post-result diagnostics, not a newly randomized weeding effect or opportunities to choose a significant result.

## Execution plan
- [ ] Test parsing, missingness, key uniqueness, unit-factor checks and paired treatment contrasts on synthetic fixtures before production implementation.
- [ ] Reproduce original May/August point estimates and verify published source hashes.
- [ ] Execute annual reconciliation and all fixed management variants in one isolated GitHub Actions run; export only aggregates, script and tests.
- [ ] Verify artifact digest, report limitations and preserve original results. No main merge, token search or NEON authentication change.

## Interpretation constraints
An apparent association difference between harvested subsamples is not a causal effect of weeding: subsample position and management are not randomized independently. This audit remains one Jena site. Annual source differences may represent source revision, aggregation or normalization; do not call them data errors without evidence. Unit verification does not turn contemporaneous cover-derived FD into a genuine future forecast.
