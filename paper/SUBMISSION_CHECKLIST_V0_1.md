# Submission checklist v0.1

## Scientific claim

Primary manuscript claim:

> Trait-specific phylogenetic-memory estimates do not robustly transfer across plant families; most heterogeneity is family × trait specific, while family identity carries a modest recurring cross-trait component.

Do not replace this with a family-versus-trait dominance claim.

## Required numerical consistency

- final core: 201 systems / 45 families / 12 traits;
- S3 mean rho: 0.0928;
- S3 median rho: 0.0531;
- S3 positive fraction: 0.746;
- prune-only Spearman correspondence: 0.832;
- family repeatability: 0.1504, CI 0.0204–0.2861;
- trait repeatability: 0.0433, CI 0–0.1335;
- residual share: 0.8063, CI 0.6600–0.9522;
- S3 trait-portability gain: -0.0242, p=0.091;
- prune-only trait-portability gain: -0.0324, p=0.193;
- conditional family repeatability: 0.1825, CI 0.0285–0.3369;
- prune-only conditional family repeatability: 0.1680.

## Hard nonclaims

Do not state or imply:

- family variance is statistically larger than trait variance;
- trait effects are absent or equal to zero;
- family repeatability is confidently greater than 10%;
- the family component has a known ecological/genetic cause;
- failed family-context portability proves no lineage generalization;
- failed spatial qualification means spatial trait turnover is weak;
- rho is an evolutionary rate, half-life, decay constant, or timescale;
- the 201 systems are a random sample of all plant family × trait combinations.

## Methods transparency

Mention:

- BIEN 4.2.8;
- V.PhyloMaker2 exact pinned commit and GBOTB.extended.TPL;
- outcome-blind qualification sequence;
- exact permutation-null mean zero for complete pair set;
- known-truth admission gates;
- S3 plus mandatory prune-only sensitivity;
- post-outcome complementary questions that were not opened because their model-informativeness gates failed.

## Figure integrity

- no outcome-based clustering in the heatmap;
- no selected subset of systems in the S3/prune scatter;
- display all 201 systems;
- show uncertainty intervals where they are part of the frozen analysis;
- do not annotate unplanned family/trait rankings.

## References to verify before submission

- Blomberg et al. 2003;
- Ackerly 2009;
- Münkemüller et al. 2012;
- Revell 2018;
- Jin & Qian 2022;
- Enquist et al. 2026.

## Remaining editorial work

- choose journal-specific word count and reference format;
- write author contributions / acknowledgements / conflict statement;
- add permanent repository release/DOI after manuscript freeze;
- archive exact figure artifact and analysis commit;
- final line-by-line numerical audit against result JSON files.
