# Jena 2003: sensitivity to the specially weeded sampling quadrat

This is a post-result sensitivity analysis, not preregistration or independent confirmation.
The original 82-plot May/August results and the separate 78-plot longitudinal models remain unchanged.

## Question
Does the positive May association between planned functional-group richness and sown
aboveground dry biomass persist when quadrat 4 is omitted?

## Published source distinction
PANGAEA 846317 states that quadrat 4 in each 2003 harvest came from an extra-carefully
weeded part of the core plot. Quadrats 1–3 were also weeded, but with ordinary maintenance.
This is NOT an unweeded control. Weed biomass is provided only as the four-quadrat
plot mean, so a quadrat-specific weed-removal/competition pathway is not identifiable.
Source: https://doi.org/10.1594/PANGAEA.846317

## Fixed comparisons
1. Reproduce the original official-mean May and August FG coefficients.
2. Replace the response with log1p(arithmetic mean of quadrats 1–3), retaining all 82 plots,
   the same original log2(sown richness), FG richness and four-block design.
3. Fit quadrat 4 separately. One quadrat per plot is still 82 plot-level observations,
   not an extra set of independent experiments.
4. Direct paired response contrasts: ordinary-minus-official in May;
   careful-minus-ordinary in May and August; August-minus-May in ordinary quadrats.
   Do not compare p-values as a test of differences.

## Numerical checks and uncertainty
Read original source files with exact existing SHA256 identities; reject duplicate
plot/month/replicate keys, missing quadrats, -9999, nonfinite or negative community mass.
Require official means to agree with the reconstructed four-quadrat means within
0.02 g/m². Calculate arithmetic means BEFORE log1p, not means of logged quadrats.
Use the identical six-column design matrix for every outcome and direct contrast.
Report normal-Wald HC3 estimates/95% intervals and 4,000 paired plot bootstrap draws,
stratified by original field block, seed 20261117. Preserve each sampled plot's
multiplicity in both seasons and all quadrat summaries. Reject rank-deficient models;
report bootstrap rank failures. Intervals are exploratory marginal intervals,
not multiplicity-adjusted confirmatory tests.

## Claim boundaries
The response is sown-species standing aboveground dry biomass, not total ecosystem
biomass, root biomass or annual primary production. Quadrat 4 differs in operator/
weeding history and spatial position; its association is not a randomized causal
weeding effect. Any robustness or non-robustness conclusion is restricted to the
specified site, year, response and model. No claim about phylogenetic memory follows.

## Implementation and verification
- Reuse standalone source reader and paired regression already tested in the prior-turn package.
- Run the same 13 tests in GitHub Actions before any empirical estimate.
- Preserve all input hash requirements and original-coefficient replay.
- Do not replace original results. Do not merge to main.
- Export only nonraw results, validation logs and file digests.
