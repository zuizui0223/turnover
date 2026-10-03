# turnover

General comparative programme on **how biological information is lost with separation**.

The repository asks:

> **Do the same biological properties predict how rapidly organismal traits and biotic interactions turn over across evolutionary time and geographic space?**

## Core design

| Biological state | Evolutionary separation | Geographic separation |
|---|---|---|
| organismal trait | trait memory loss | within-species trait spatial turnover |
| biotic interaction | partner-profile evolutionary turnover | interaction rewiring across space |

All four cells use one common effect convention: **null-centered distance–dissimilarity correlation**.

The programme is explicitly not flower-colour-specific. CHUN and FCP are motivating temporal/spatial proofs of concept only; their existing outcomes are not used to choose generalized traits, networks, predictors or thresholds.

## Frozen biological predictors

1. **Context heterogeneity** — candidate common driver of faster turnover on both axes.
2. **Ecological specialization** — candidate decoupler; opposite time/space effects are predeclared as biologically meaningful.
3. **Dispersal / mobility** — secondary decoupler expected to affect geographic turnover more strongly than evolutionary memory.

Biotic interaction type is an explicit moderator. Interaction turnover is decomposed into **species turnover** and **rewiring among shared/available species**; only rewiring enters the primary cross-axis interaction test.

## Start here

- Programme design: data/spatiotemporal_memory_turnover_design_v0_1.json
- Scientific programme: docs/SPATIOTEMPORAL_MEMORY_TURNOVER_PROGRAM_V0_1.md
- Source-first eligibility matrix: data/spatiotemporal_memory_turnover_source_matrix_v0_1.csv

## Source order

Trait arm:
1. BIEN 4.2
2. AusTraits independent transport
3. TRY v7 — currently source-access HOLD

Interaction arm:
1. Mangal curated networks — joint time/space route closed at species-rank support gate; retained only as non-primary spatial validation candidate
2. GloBI stable versioned archive — second and final primary source; terminal pre-outcome HOLD at source-semantic gate

No biological response is opened until source identity, schema/support eligibility and observed-geometry informativeness are frozen.

## Project boundary

This repository is independent of current submission claims in CHUN, FCP and IWE. Those repositories remain external anchors and are not silently modified by this programme.

## Current source-gate state

### Interaction arm — terminal pre-outcome HOLD

Mangal passed spatial-network and taxonomy-ID gates but failed the frozen species-rank joint gate: 7 programmes qualified versus 12 required. No interaction edge was opened. The finite-family contract therefore authorized one pre-outcome switch to GloBI.

GloBI then passed several increasingly strict gates:

1. Stable Zenodo archive identity (record 22691479, version 0.11): **PASS**.
2. Archive schema / aliases: **PASS** without row opening.
3. Structural support v0.4: **PASS** — 815 candidate systems -> 92 structural systems -> 62 sourceNamespace clusters.
4. Correct-grain support v0.5.2: **PASS** — 58 provenance-resolved programme blocks in 20 namespaces independently satisfy the same frozen 20-focal / 5-site-year / 10-repeated-focal thresholds.
5. Source-semantic / provenance gate v0.5: **HOLD**.

The terminal HOLD is fail-closed. Nine of the 20 remaining namespaces are definitively ineligible under rules frozen before any turnover outcome: occurrence/specimen/collection aggregators, a citizen-science aggregation, an IPT occurrence archive, or the GloBI mirror of the already-failed first source Mangal. Therefore at most 11 independent namespaces can remain, below the frozen requirement of 12.

No turnover, rewiring, distance-dissimilarity, phylogenetic, predictor-response or time-space coupling outcome was opened. The threshold is not lowered and a third primary interaction source is not introduced.

See: `docs/GLOBI_SOURCE_SEMANTIC_V0_5.md`.

### Trait arm — terminal pre-outcome HOLD

The trait arm also closes **before any generalized biological turnover effect is opened**.

BIEN source/schema qualification passed at exact patch **4.2.8**: 25,932,628 rows, required `agg_traits` fields present, and 54/54 expected trait names. It then passed three increasingly strict prospective gates under the frozen >=20 temporal species / >=8 spatial species / >=20 georeferenced records / >=5 25-km cells / >=12-family design:

1. **Structural support PASS** — 8,215 family × trait systems -> 1,705 temporal candidates -> **73 joint-support systems in 37 independent families**.
2. **State-validity PASS** — 73 -> **43 semantic-valid systems in 34 families**.
3. **Phylogeny crosswalk PASS** — 43 -> **39 systems in 31 families** under pinned V.PhyloMaker2 S3 plus the mandatory prune-only >=20 native-tip sensitivity.

The geometry-only informativeness gate then selected much more strongly:

4. **Temporal informativeness PASS** — 39 -> **24 systems in 21 independent families**, requiring both S3 and prune-only recovery of benchmark delta_rho=0.15 with median absolute recovery error <=0.10, directional recovery >=0.80, and valid-replicate fraction >=0.90.
5. **Spatial informativeness HOLD** — among those 21 temporal-PASS families, **11 independent families are already confirmed spatial HOLD** under the identical benchmark/recovery rules. Even if every unresolved family passed, at most **10 families** could remain, below the frozen requirement of 12.

That upper bound makes exhaustive completion unnecessary. The BIEN route is therefore **terminal pre-outcome HOLD** at spatial informativeness. The first spatial implementation attempts exposed two technical-only matrix/indexing bugs before any spatial scientific result; both are retained in the audit trail and fixed without changing generator, benchmark, pair set, thresholds, seeds, or coordinates. The terminal HOLD uses only corrected-run scientific results.

The predeclared independent transport, **AusTraits v7.0.0**, is independently terminal structural HOLD: after correcting its non-global `observation_id` to the source-faithful composite `dataset_id + observation_id`, the unchanged matched gate still produced only **10 joint-support systems in 3 independent families (Fabaceae, Myrtaceae, Proteaceae)** versus 12 required.

The finite source family is exhausted: BIEN + AusTraits were the two predeclared primary trait sources. **No third primary source is introduced, no threshold is lowered, and the frozen real-effect design is not executed.** TRY v7 remains a future source-access HOLD rather than a rescue route for this prospective programme.

For trait-time and trait-space, the complete label-permutation null has also been simplified analytically before outcomes: with all unordered pairs and whole-state label permutations, the exact expected Spearman correlation is zero. Thus the canonical trait `delta_rho` equals observed Spearman `rho`; permutations are retained only for null dispersion and implementation diagnostics, not to Monte-Carlo-estimate the null mean.


## Independent temporal follow-up

The generalized time-space programme above remains terminal pre-outcome HOLD and is not being relaxed. A separate prospective follow-up is being developed on `followup/trait-memory-spectrum-v0-1`: **is phylogenetic trait-memory loss primarily trait-specific or lineage-specific?**

This follow-up uses BIEN 4.2.8 and the same pinned V.PhyloMaker2 backbone but drops the geographic question entirely. Before any real family × trait memory-loss rho is opened, it has passed:

- temporal structural support: **1,455 systems / 240 families / 49 traits**;
- temporal semantic validity: **1,219 systems / 219 families / 47 traits**;
- S3 + prune-only phylogeny crosswalk: **802 systems / 160 families / 47 traits**;
- exact necessary crossed-repeat pruning: **722 systems / 120 families / 25 traits**, one connected family–trait graph.

The inherited known-truth temporal informativeness test is now running on those 722 systems. The 39 systems already evaluated under the identical frozen contract reuse their prior result exactly; only 683 novel systems are simulated. If the final informativeness-PASS graph retains family degree ≥2, trait degree ≥5, ≥12 families, ≥4 traits and one connected component, the pre-frozen primary model is an unweighted crossed REML variance decomposition `rho ~ 1 + (1|family) + (1|trait_name)`. Its primary contrast is `log(var_trait / var_family)` with 2,000 fixed-seed parametric bootstrap replicates.

Real trait-memory effects remain unopened until that final gate passes.
