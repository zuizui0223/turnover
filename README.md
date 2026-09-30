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
1. Mangal curated networks — joint time/space route closed at species-rank support gate; retained as possible spatial validation
2. GloBI stable versioned archive — active second and final primary joint source

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

The next active development gate is BIEN source/schema/support qualification before any generalized trait-turnover response is opened.
