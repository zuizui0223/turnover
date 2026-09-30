# BIEN trait-arm gate chronology

The BIEN lane remains prospective: no raw trait value, real trait dissimilarity, real `delta_rho`, or predictor-response result has been opened.

## Source qualification

1. **Metadata v0.1 — HOLD (version granularity only).** The programme named BIEN 4.2; the live database reported patch **4.2.8**. All other checks passed.
2. **v0.1.1 — technical HOLD.** The 4.2.x regex was JSON-overescaped. No biological rule changed.
3. **v0.1.2 — PASS.** Exact downstream patch is pinned to **4.2.8** (release date 2023-06-27), with **25,932,628** `agg_traits` rows, all required fields, and **54/54** expected trait names.

## Structural support contract

The frozen family × trait gate requires:

- at least 20 temporal species;
- at least 8 spatial species;
- each spatial species must have at least 20 geovalid measurements in at least 5 deterministic 25-km equal-area cells;
- at least 12 independent plant families.

A stricter-only amendment requires nonmissing `trait_value` presence, but the value is never selected or returned by the structural support query. The support workflow is manual-only after freezing to prevent repeated 25.9M-row scans on unrelated PR changes.

## Trait semantics frozen before support results

- 43 continuous-scalar traits;
- 9 nominal-categorical traits;
- 2 primary HOLD traits: `plant flowering begin` and `whole plant growth form diversity`.

The effective categorical unit rule is the stricter intersection of two pre-result drafts: only NULL/empty unit fields are admitted. Continuous traits require 100% numeric parseability and exactly one nonempty unit. State-validity also requires actual temporal and within-species spatial state variation.

## Plant phylogeny

Pinned source:

- repository: `jinyizju/V.PhyloMaker2`;
- commit: `7af3fb5152f691af2e4ec9d5e2e467d1b50505e9`;
- backbone: `GBOTB.extended.TPL`;
- scenario: S3;
- mandatory sensitivity: prune-only backbone-native subset must retain at least 20 species.

The first source checker falsely held because it converted tree tip underscores to spaces but left `tips.info.TPL$species` unchanged. V.PhyloMaker2 itself uses underscore-form tip labels. After a technical-only correction, the pinned source **PASSed** with:

- 74,529 expected / observed tips;
- 74,529 complete and unique metadata species;
- exact raw tip-set match;
- 149,000 edges;
- finite, nonnegative branch lengths;
- rooted tree;
- dated branching-time signal (maximum 400.7877);
- 11,098 node-information rows.

## Frozen post-support order

A structurally supported system must then pass, in order:

1. aggregate-only trait-state validity;
2. S3 phylogeny crosswalk, including prune-only >=20;
3. observed-geometry known-truth simulations.

The informativeness benchmark is fixed at `delta_rho = 0.15`. Admission requires median absolute recovery error <=0.10 and at least 80% directional recovery for both temporal and spatial estimators, including the prune-only temporal sensitivity.

Only after all gates pass may real trait states be used to compute the first biological turnover response.
