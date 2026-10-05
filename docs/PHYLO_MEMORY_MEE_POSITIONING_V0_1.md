# Submission positioning — Methods in Ecology and Evolution

Checked: 2026-10-05

## Recommended article type

**Research Article**

Current MEE guidance defines Research Articles as papers that introduce new methods in ecology and evolution, normally test computational methods with simulations or benchmark datasets, and demonstrate applicability beyond a single taxon or system. MEE also defines methods broadly enough to include conceptual methodological developments.

Since 2026, MEE also has a distinct **Workflow** article type for novel, broadly useful pipelines or procedural assemblages, especially for complex or Big datasets. Workflow papers require substantial improvement over existing workflows plus code/instructions, error-propagation analysis, sensitivity analysis and benchmark testing where relevant. This manuscript is **not** positioned as a Workflow: its novelty is an inferential decomposition of failed known-truth simulation, not a pipeline assembled from existing tools.

## Proposed title

**Known truth is not automatically assignable in simulation-based power studies**

The title intentionally omits phylogenetic memory. The phylogenetic system is the stress test; the methodological problem is broader.

## Editor-facing methodological gap

Simulation studies routinely distinguish data-generating mechanisms, estimands, estimators and performance measures. A less explicit assumption is that a requested target summary is actually assignable by the declared generator on the realized design.

The present method separates three inferential events:

1. **structural feasibility** — does the representation × realized design contain a state capable of the target?
2. **generator accessibility** — can the declared generator reach the target while satisfying validity rules?
3. **recovery** — after successful assignment, can the estimator recover the target?

A failed simulation at gate 1 or gate 2 is not evidence of low estimator power. This interpretive distinction is the methodological contribution.

## Why this is a Research Article rather than a case study or Workflow

The paper does not merely report that categorical traits have low power, nor does it assemble an analysis pipeline. It defines distinct inferential objects and tests them with controlled interventions that change one mechanism at a time.

The empirical separation is sharp:
- 276/276 categorical trees contain a realizable one-transition state at or above the benchmark, excluding a hard one-transition ceiling below it;
- latent-OU thresholding is no-bracket in 220/276;
- changing only the generator to Mk2 reduces no-bracket to 170/276;
- removing the exact state-balance attenuation term reduces the full-population no-bracket rate to 42.4–43.8%;
- 34.9% of successfully Mk2-calibrated systems still fail downstream recovery.

These stages show that “failed known-truth recovery” is not a single statistical event.

## Broad applicability

The claim should be scoped to settings in which a target is a constrained summary of generated data rather than a free generator parameter. Plausible domains include binary and ordinal outcomes, compositional data, bounded indices, zero-inflated responses, network summaries and other constrained state spaces. These are conceptual extensions; the present paper empirically demonstrates the method only for phylogenetic-memory simulation.

## Desk-screen test

A senior editor should be able to answer four questions from the first page alone:

1. **What methodological gap is independent of the organism?**  
   Known-truth simulation assumes truth assignment before testing it.

2. **What is new?**  
   A tested separation of structural feasibility, generator accessibility and recovery, with the empirical structural test explicitly interpreted as a one-sided ceiling diagnostic.

3. **Why is this not merely binary low power?**  
   All 276 categorical trees can express the target, yet accessibility changes strongly under controlled generator and balance interventions.

4. **Why should readers outside phylogenetics care?**  
   Any constrained simulation target that is not a free generator parameter can fail before recovery is defined.

## Desk-rejection risks and fixes

### Risk 1 — looks like a phylogenetic case study
Fix: keep the title, first paragraph and Fig. 1 system-independent; introduce plant phylogenies only as the benchmark geometry.

### Risk 2 — looks like “binary traits have low power”
Fix: foreground 276/276 structural feasibility and the asymmetric paired rescues; generic discrete-trait power limitations are already known.

### Risk 3 — looks like a Workflow
Fix: do not describe the three gates as a convenient pipeline. Describe them as different inferential objects whose failure supports different conclusions.

### Risk 4 — looks like an untested framework
Fix: emphasize that every gate is operationalized and tested, with a realizability witness, controlled generator substitution, exact attenuation factorization and downstream recovery evaluation.

### Risk 5 — looks over-explored
Fix: foreground prospective freezes and the unconditional mechanism stop; do not add another estimator/generator search on the same 276 systems.

## Length and packaging

Current MEE guidance allows 7,000–8,000 words for Research Articles including references, figure captions and statements. The main manuscript should remain compact, with the three primary figures carrying most numerical detail.

MEE currently encourages pre-submission enquiries and asks authors to send a title, abstract and brief explanation of fit. The enquiry should make the Research Article distinction explicit because the journal now has a separate Workflow category.

## Current primary package

- Full draft: `docs/PHYLO_MEMORY_ASSIGNABILITY_MANUSCRIPT_V0_2.md`
- Abstract: `docs/PHYLO_MEMORY_ABSTRACT_V0_1.md`
- Figure plan: `data/phylo_memory_figure_plan_v0_1.json`
- Figure captions: `docs/PHYLO_MEMORY_FIGURE_CAPTIONS_V0_1.md`
- Novelty boundary: `docs/PHYLO_MEMORY_NOVELTY_BOUNDARY_V0_1.md`
- Mechanism closure: `data/phylo_memory_mechanism_close_v0_5_3.json`

## Current MEE sources

- Aims and scope: https://besjournals.onlinelibrary.wiley.com/hub/journal/2041210X/aims-and-scope/read-full-aims-and-scope
- Author guidelines and article types: https://besjournals.onlinelibrary.wiley.com/hub/journal/2041210x/author-guidelines
- Workflow guidance: https://besjournals.onlinelibrary.wiley.com/hub/journal/2041210x/features/workflows
- Ellison 2023 editorial on a good Methods paper: https://doi.org/10.1111/2041-210X.14232
- Ellison 2026 editorial introducing Workflows: https://doi.org/10.1111/2041-210X.70207
