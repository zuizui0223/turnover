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

Mangal passed spatial-network and taxonomy-ID gates but failed the frozen species-rank joint gate: 7 programmes qualified versus 12 required. No interaction edge was opened. The finite-family contract therefore authorizes one source switch to GloBI; if GloBI fails a pre-outcome access/schema/support/informativeness gate, the primary joint interaction route stops.
