# Submission positioning — Methods in Ecology and Evolution

Checked: 2026-10-05

## Recommended article type

**Research Article**

Current MEE guidance states that Research Articles should describe new methods or methodological approaches in ecology and evolution, normally test computational methods with simulations or benchmark datasets, and demonstrate broad applicability across taxa or systems. The journal explicitly defines methods broadly enough to include conceptual methodological developments.

This manuscript should not be sold as:
- a plant-trait result;
- a new phylogenetic-signal index;
- a workflow assembling existing tools;
- a comparison showing only that binary traits have low power.

It should be sold as a **general diagnostic framework for simulation-based power studies with constrained representations**.

## Editor-facing methodological gap

Simulation studies routinely distinguish data-generating mechanisms, estimands, estimators and performance measures. What is usually left implicit is that a user-declared target summary is actually assignable on the realized design.

The present method inserts two diagnostics before conventional recovery:

1. **structural realizability** — does the representation × realized design contain an explicit state capable of the requested target?
2. **generator accessibility** — can the declared stochastic generator reach the target while satisfying validity rules?
3. **recovery** — only after assignment, does the estimator recover the target?

The phylogenetic-memory analysis is a stress test of that framework, not the scope boundary of the method.

## Why the current evidence is more than a workflow

The paper does not simply sequence existing procedures. It defines distinct inferential objects and supplies prospective diagnostics that change the interpretation of a failed power simulation.

The empirical separation is sharp:
- the target is structurally realizable in 276/276 categorical trees;
- latent-OU thresholding is no-bracket in 220/276;
- Mk2 generator substitution reduces no-bracket to 170/276;
- exact state-balance normalization reduces the remaining full-population no-bracket rate to 42.4–43.8%;
- 34.9% of successfully Mk2-calibrated systems still fail downstream recovery.

These stages demonstrate that “failed known-truth recovery” is not one statistical event.

## Broad applicability paragraph

The framework should be presented as applicable whenever the target quantity is a summary of simulated data rather than a freely assignable parameter of the generator. Candidate domains include binary and ordinal traits, compositional outcomes, bounded indices, zero-inflated responses, network summaries, occupancy/detection summaries and other constrained state spaces. These examples are conceptual extensions; only the phylogenetic-memory case is empirically tested here.

## Desk-rejection risks and fixes

### Risk 1 — looks like a biological case study
Fix: open the Introduction with the simulation-design problem; plant phylogenies appear only as the stress-test geometry.

### Risk 2 — looks like “binary traits have low power”
Fix: lead with 276/276 structural realizability and the sequential paired rescues. Prior work already covers generic discrete-trait power limitations.

### Risk 3 — looks like a workflow rather than a method
Fix: define the three gates as different inferential objects, explain how each changes the valid interpretation of a failed simulation, and end with a reusable audit protocol.

### Risk 4 — looks over-explored
Fix: foreground the prospective freeze/stop sequence and the final unconditional mechanism stop. Do not execute additional estimator searches on the same 276 systems.

## Length and packaging

MEE current author guidance allows approximately 7,000–8,000 words for Research Articles including references, captions and statements. The current v0.2 draft should therefore remain concise; the three primary figures should carry most of the numerical detail.

MEE encourages pre-submission enquiries. The enquiry should contain:
- working title;
- abstract;
- one short paragraph explaining why this is a broadly useful methods paper rather than a phylogenetic case study.

## Current primary package

- Full draft: `docs/PHYLO_MEMORY_ASSIGNABILITY_MANUSCRIPT_V0_2.md`
- Abstract: `docs/PHYLO_MEMORY_ABSTRACT_V0_1.md`
- Figure plan: `data/phylo_memory_figure_plan_v0_1.json`
- Figure captions: `docs/PHYLO_MEMORY_FIGURE_CAPTIONS_V0_1.md`
- Novelty boundary: `docs/PHYLO_MEMORY_NOVELTY_BOUNDARY_V0_1.md`
- Mechanism closure: `data/phylo_memory_mechanism_close_v0_5_3.json`

## Current MEE sources

- Aims and scope: https://besjournals.onlinelibrary.wiley.com/hub/journal/2041210X/aims-and-scope/read-full-aims-and-scope
- Author guidelines: https://besjournals.onlinelibrary.wiley.com/hub/journal/2041210x/author-guidelines
- Ellison 2023 editorial on a good Methods paper: https://doi.org/10.1111/2041-210X.14232
