# MEE submission readiness — truth assignability paper

Checked against current *Methods in Ecology and Evolution* author guidance on 2026-10-05.

## Scientific status

**Primary mechanism programme: CLOSED**

No additional generator, estimator, target, parameter-grid extension or outcome-based subgroup search on the same 276 categorical systems is permitted for strengthening the primary claim.

Current title:
**Known truth is not automatically assignable in simulation-based power studies**

Primary methodological contribution:
**structural feasibility does not guarantee generator-specific accessibility, and successful assignment does not guarantee recovery.**

## Initial-submission requirements

| Requirement | Status | Current location / action |
|---|---|---|
| Research Article framing | READY | `docs/PHYLO_MEMORY_MEE_POSITIONING_V0_1.md` |
| Broad method-first title | READY | manuscript / PR |
| Abstract numbered 1–4 | READY | manuscript + abstract file |
| Data/Code for peer review statement | READY | manuscript |
| Keywords | READY | manuscript |
| Introduction independent of focal organism | READY | manuscript |
| Materials and Methods | READY | manuscript |
| AI/LLM disclosure | READY | manuscript Methods + all primary review-bundle scripts annotated |
| Results | READY | manuscript |
| Discussion | READY | manuscript |
| Primary figures | IN CI | source-backed Fig. 1–3 workflow |
| Figure captions | READY | `docs/PHYLO_MEMORY_FIGURE_CAPTIONS_V0_1.md` |
| References | PROVISIONAL READY | manuscript; final style check still needed |
| Double-anonymous manuscript | READY IN CONTENT | no author names in main draft |
| Anonymous code/data review package | DRAFT AUTOMATED | `.github/workflows/phylo-memory-anonymous-review-bundle-v0-1.yml` |
| Open-source code licence | **BLOCKER** | repository currently has no LICENSE; author must choose one, then provide author-neutral `LICENSE_REVIEW.txt` for peer review |
| Separate title page | TEMPLATE READY | `docs/PHYLO_MEMORY_MEE_TITLE_PAGE_TEMPLATE_V0_1.md` |
| Continuous line/page numbering | FORMAT STAGE | apply when manuscript is exported to submission document |
| 7,000–8,000 word maximum | READY | manuscript + primary captions ≈5,022 words |
| Pre-submission enquiry | READY | `docs/PHYLO_MEMORY_MEE_PRESUBMISSION_ENQUIRY_V0_1.md` |
| Persistent public archive/DOI | ACCEPTANCE STAGE | prepare archive after review version stabilizes |

## Desk-screen questions

The first page must make four answers obvious.

**What is the methodological gap?**  
Known-truth simulation can assume that a requested target has been assigned before that has actually been demonstrated.

**What is not new?**  
Feasible-range checks for constrained correlations, generic low power of binary traits, DGM/estimand distinctions, and simulation reporting guidance already exist.

**What is new?**  
The tested separation of structural feasibility, generator-specific accessibility and recovery, including a controlled generator intervention showing that a structurally feasible target can remain generator-inaccessible.

**What is the strongest empirical fact?**  
The categorical no-bracket rate is 79.7% even though all 276 trees contain a realizable one-transition state at or above the benchmark; changing only the generator rescues 51 original failures while creating one new failure.

## Final pre-submission sequence

1. Obtain successful paper-package, figure, and anonymous-bundle CI runs on the final head.
2. Choose and add an open-source licence plus an author-neutral `LICENSE_REVIEW.txt`; regenerate anonymous review bundle.
3. Freeze the manuscript wording and figure hashes.
4. Generate the double-anonymous manuscript file with continuous line/page numbering.
5. Fill the separate title page outside the anonymous manuscript.
6. Send the pre-submission enquiry before full submission.
7. If invited/encouraged, submit the exact frozen package rather than reopening mechanism search.


## Generated anonymous-bundle audit

A successfully generated review bundle was unpacked and inspected directly.

- bundle workflow: successful
- unpacked files: 50
- author/repository-owner identifier hits: 0
- email-address hits: 0
- explicit author-name hits checked: 0
- primary scripts carrying the AI-assisted-development disclosure: 13
- immutable aggregate evidence stages included: 7
- licence status inside bundle: `LICENSE_PENDING_AUTHOR_CHOICE`

The anonymous bundle is therefore technically ready apart from the deliberate open-source-licence blocker.
