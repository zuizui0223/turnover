# Plant trait phylogenetic memory spectrum v0.1

## Question

When trait similarity decays across phylogenetic distance, is the rate of decay mainly a property of **what trait is measured**, or of **which lineage the trait evolves in**?

This is a new temporal-only follow-up. It does not reopen or relax the terminal time-space programme. The previous programme closed before generalized real turnover effects because the spatial informativeness requirement could not reach 12 independent families.

## Competing biological architectures

### Trait-dominant memory

Traits carry characteristic evolutionary memory depths across lineages. Under this architecture, the same trait tends to be conserved or labile across many families, and between-trait variance in memory-loss rho exceeds between-family variance.

### Lineage-dominant memory

Families carry broadly fast or slow evolutionary regimes that affect multiple traits together. Under this architecture, between-family variance exceeds between-trait variance.

### Mixed architecture

Trait and lineage effects are of comparable magnitude, or the bootstrap interval for their variance ratio overlaps parity.

## Response

For each admitted family x trait system:

- continuous trait state = median valid measurement per species;
- categorical trait state = unique modal category;
- continuous dissimilarity = absolute difference;
- categorical dissimilarity = 0/1 mismatch;
- separation = all unordered S3 patristic distances;
- primary response = Spearman(separation, trait dissimilarity).

Under the already-proven complete whole-state label-permutation theorem, the exact null mean Spearman rho is zero. Therefore the response is directly the null-centered memory-loss effect.

Larger positive rho means faster loss of trait-state information with phylogenetic separation.

## Source

Primary source: BIEN 4.2.8.

Phylogeny: V.PhyloMaker2 commit `7af3fb5152f691af2e4ec9d5e2e467d1b50505e9`, `GBOTB.extended.TPL`, S3 primary with a mandatory prune-only native-tip sensitivity.

The trait universe is all 52 traits that were semantically classified before any generalized trait outcome was opened: 43 continuous scalar and 9 nominal categorical. The two prior fail-closed traits remain excluded.

## Eligibility chronology

1. Temporal structural support: >=20 species.
2. Semantic validity: numeric/unit rules or categorical unique-mode rules; >=20 resolvable species; >=2 species states.
3. Phylogeny: >=20 S3-resolvable species and >=20 prune-only native tips.
4. Known-truth temporal informativeness: benchmark rho=0.15, median absolute recovery error <=0.10, directional recovery >=0.80, valid replicate fraction >=0.90 on both S3 and prune-only geometry.
5. Crossed analysis core: iteratively require family degree >=2 traits and trait degree >=5 families; final core must retain >=12 families, >=4 traits and be one connected bipartite graph.
6. Only after all five gates pass may real memory-loss rho be computed.

No geographic-support requirement is imposed because this is explicitly not a time-space coupling study.

## Primary model

Unweighted crossed random-intercept model:

```
memory_loss_rho ~ semantic_class + (1 | family) + (1 | trait_name)
```

Primary quantities:

- family variance;
- trait variance;
- residual variance;
- family share of total variance;
- trait share of total variance;
- log(trait variance / family variance).

Uncertainty uses 2,000 fixed-seed parametric bootstrap replicates.

Interpretation:

- bootstrap CI entirely > 0: trait-dominant;
- bootstrap CI entirely < 0: lineage-dominant;
- CI overlaps 0: mixed architecture.

## Sensitivities

The identical admitted system set is re-estimated with prune-only rho replacing S3 rho.

Trait biological modules are pre-annotated for descriptive summaries only. They do not determine system admission or the primary variance decomposition.

## Hard nonclaims

- No spatial turnover inference.
- No claim that temporal and spatial turnover share a mechanism.
- Spatial failures from the previous programme are not treated as biological zero effects.
- No outcome-driven family or trait deletion.
- No third-source rescue if BIEN temporal-only eligibility fails.
