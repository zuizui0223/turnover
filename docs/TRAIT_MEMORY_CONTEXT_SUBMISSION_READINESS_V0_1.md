# Submission readiness — trait-memory context manuscript v0.2

Status: manuscript/reproducibility audit. No new inference.

## Scientific claim

### Primary claim — ready

Trait identity provides no robust incremental cross-lineage prediction of phylogenetic-memory strength on the prospectively qualified family x trait matrix.

Evidence:
- fixed 201-system core;
- same-trait leave-one-family-out gain = -0.0242 on S3, p = 0.091;
- prune-only gain = -0.0324, p = 0.193;
- positive result had required gain > 0 and p <= 0.05 on both tree treatments;
- known-truth portability gate passed before real effects were opened.

### Supporting claim — ready with qualification

Family identity retains a modest recurring cross-trait grouping-level component after trait-specific means are removed.

Evidence:
- conditional family repeatability S3 = 0.1825;
- bootstrap CI 0.0285–0.3369;
- prune-only = 0.168;
- leave-one-out range 0.1205–0.2268.

Required qualification:
- interval spans the predeclared 0.10 practical reference;
- do not claim the family component confidently exceeds 10%;
- do not infer a mechanism;
- deeper covariance among families was not modelled.

### Residual interpretation — wording corrected

R_residual = 0.8063 is an unresolved system-level/residual component. It can include true family x trait interaction, effect-estimation error, heterogeneous BIEN measurements and other model residual.

Do not call it pure family x trait biological interaction.

## Reproducibility

### Complete

- Main numerical results are committed as JSON.
- Three independent real-effect routes have exact identity checks.
- Canonical 201-system effect table is now persisted at:
  - results/trait_memory_context_synthesis_v0_1/effects.csv
- Expected SHA256:
  - 5fffdfbc9ab50ff7bf568e80537a290e11c2bfde02f1d5484c7e896ed5f9415b
- Figure renderers are versioned.
- Source pins:
  - BIEN 4.2.8
  - RBIEN commit 531cb221bd44cf43419e89b2354f6424e718cd53
  - V.PhyloMaker2 commit 7af3fb5152f691af2e4ec9d5e2e467d1b50505e9
  - GBOTB.extended.TPL
- Prospective failed routes remain in history rather than being deleted.

### Recommended before submission

- Add a compact machine-readable manifest listing the exact result JSONs, effect-table SHA, source commits and figure files.
- Export a tagged release or archival DOI for the exact submission commit.
- State that BIEN source data remain under their source terms rather than redistributing raw measurements.

## Manuscript

### Complete

- Full manuscript draft:
  - paper/trait_memory_context_manuscript_v0_2.md
- Literature positioning v0.2:
  - docs/TRAIT_MEMORY_CONTEXT_LITERATURE_V0_2.md
- Reviewer-facing claim audit:
  - docs/TRAIT_MEMORY_CONTEXT_REVIEWER_AUDIT_V0_1.md
- Conservative synthesis wording is aligned in README and result metadata.

### Still needed before journal upload

1. Journal-specific formatting and word-count reduction.
2. Final bibliography style pass against the selected journal.
3. Author list / affiliations / acknowledgements / funding / conflicts.
4. Final figure resolution/font-size inspection after journal sizing.
5. Archive the exact merged submission commit in a tagged release / DOI.

## Figures

### Figure 1 — crossed design

Input:
- canonical 201-system effects table.

Purpose:
- show incidence only;
- 45 families x 12 traits;
- no clustering-based inference.

### Figure 2 — observed memory gradients

Input:
- canonical 201-system effects table.

Purpose:
- descriptive S3 rho across fixed systems.

Hard rule:
- ordering is graphical only and must not generate new clusters/hypotheses.

### Figure 3 — triangulation

Inputs:
- repeatability result;
- portability result;
- conditional family repeatability result.

Purpose:
- align the three separately qualified analyses without creating a new combined test.

### Figure 4 — S3/prune-only sensitivity

Input:
- canonical 201-system effect table.

Purpose:
- descriptive backbone sensitivity;
- report Spearman correspondence 0.832.

## Reviewer risks that remain

### Highest

1. Novelty could be overstated as "prediction is new".
   - Fix: novelty is the transferability of a within-family macroevolutionary memory statistic to a held-out lineage.

2. Residual could be mistaken for biological interaction variance.
   - Fix: use unresolved system-level/residual language consistently.

3. Family random effects could be interpreted as independent or causal.
   - Fix: explicitly state that deeper family phylogenetic covariance was not modelled.

### Moderate

4. Global-mean portability baseline is simple.
   - Frame it as an incremental test of whether trait identity adds information, not as the best possible predictor.

5. Family is one phylogenetic grain.
   - Explicitly connect this limitation to phylogenetic scale dependence.

6. BIEN source heterogeneity can attenuate repeatability.
   - Keep as a limitation; do not introduce post-outcome precision weighting as a new primary analysis.

## No further primary same-data mechanism fishing

The current manuscript has a coherent and prospectively defended primary result. Additional analyses of ecological mechanisms, trait modules, family rankings or outcome-derived clusters should not be promoted to new primary claims from this same fixed effect table.

Future mechanism tests should be preregistered as independent follow-ups or use new data.

## Readiness assessment

- Core analysis: READY
- Claim boundaries: READY
- Full prose draft: READY
- Data and Code Availability: READY
- Figure captions: READY
- Manuscript consistency CI: PASS
- Canonical effect data: READY
- Figures: RENDERED (Figures 1–4, PNG + PDF) / final journal sizing inspection pending
- Reproducibility manifest: READY
- Supplementary gate chronology: READY
- Journal formatting: TODO
- Archival release / DOI: TODO
