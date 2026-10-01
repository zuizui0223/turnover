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

### Trait arm — active

The trait arm remains independent of the interaction HOLD and proceeds under the pre-frozen source order:

1. BIEN 4.2
2. AusTraits independent transport
3. TRY v7 — source-access HOLD

BIEN source/schema qualification passed at exact patch **4.2.8**: 25,932,628 rows, required `agg_traits` fields present, and 54/54 expected trait names. No raw trait turnover outcome has been opened.

The primary BIEN route has now passed three successive pre-outcome gates under the frozen >=20 temporal species / >=8 spatial species / >=20 georeferenced records / >=5 25-km cells / >=12-family design:

1. **Structural support PASS** — 8,215 family × trait systems -> 1,705 temporal candidates -> **73 joint-support systems in 37 independent families**, after the RBIEN-standard non-centroid spatial filter.
2. **State-validity PASS** — 73 -> **43 semantic-valid systems in 34 families** after numeric/unit/tied-mode/within-species-variation checks. Thirty systems were excluded fail-closed.
3. **Phylogeny crosswalk PASS** — 43 -> **39 systems in 31 families** under V.PhyloMaker2 S3 with the mandatory prune-only >=20 native-tip requirement. Four systems failed only the prune-only threshold.

V.PhyloMaker2 is pinned at commit `7af3fb5...` with `GBOTB.extended.TPL`. The source preflight itself passes: 74,529 unique tree tips exactly match 74,529 `tips.info.TPL` species labels; branch lengths are finite/nonnegative, the tree is rooted, and the dated branching-time signal is present.

The active gate is now **observed-geometry known-truth informativeness**. Temporal S3 and prune-only simulations are executing for the 39 crosswalk-PASS systems; only if at least 12 independent families survive both temporal axes will the frozen spatial informativeness gate run. The benchmark is delta_rho=0.15 with median absolute recovery error <=0.10, directional recovery >=0.80, and valid-replicate fraction >=0.90. Real trait turnover is still unopened.

The predeclared independent transport, **AusTraits v7.0.0**, has also been qualified without opening raw values. Its exact 43.5 MB flattened Parquet passed byte-integrity and 68-column schema checks. An audit then showed that `observation_id` is not globally unique (39,207 IDs occur in multiple datasets), so the first support scan was conservatively invalidated as an undercount and repeated with the source-correct composite key `dataset_id + observation_id`, without changing any biological threshold. The corrected matched BIEN gate still **HOLDs**: 30,821 family × trait systems were screened, only 10 systems qualified, and those belonged to just **3 independent families (Fabaceae, Myrtaceae, Proteaceae)** versus the frozen requirement of 12. Thresholds are not relaxed. No third primary trait source is allowed; therefore the generalized trait arm now depends on the already-running BIEN gate.

For trait-time and trait-space, the complete label-permutation null has also been simplified analytically before outcomes: with all unordered pairs and whole-state label permutations, the exact expected Spearman correlation is zero. Thus the canonical trait `delta_rho` equals observed Spearman `rho`; permutations are retained only for null dispersion and implementation diagnostics, not to Monte-Carlo-estimate the null mean.
