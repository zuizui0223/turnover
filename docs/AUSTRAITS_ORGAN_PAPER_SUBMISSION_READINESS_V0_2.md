## Coauthor review package validated — 2026-10-19 (latest editorial state)

**Status: ready for coauthor scientific review; NOT submitted or merged.**

The final GitHub Actions [coauthor review bundle #39236507614](https://github.com/zuizui0223/turnover/actions/runs/39236507614) completed successfully. Its full bundle is `austraits-organ-K-coauthor-review-v0-1`, containing:

- 10-page editable **manuscript DOCX** and static **PDF**, including **three exact source-backed figures** with one full page per figure and their scientific captions.
- 3-page landscape **Supplementary Tables S1–S3 DOCX/PDF**, rendered as four proper native Word tables rather than the original collapsed Pandoc table layout.
- Figure 1–3 original PNG and vector SVG, `figure_manifest.json`, `source_manifest.json` with SHA256 and pinned prior original result archives, plus README.

### Verified render and editorial QA

An actual image inspection found that the **earlier Figure 1 legend overlapped the last family's pair-count label**; it was moved into empty upper-left plot space. [Corrected figure source CI #39233969489](https://github.com/zuizui0223/turnover/actions/runs/39233969489) passed and those corrected source-verified figures are used in the compiled package.

The first supplement PDF broke column formatting across 5–6 pages; a direct native Word table formatter corrected the layout. The latest 3-page supplement was visually reviewed page by page and all original values/columns were retained. The 10-page manuscript was also rendered page by page. No more overlaid legend or unnecessary duplicate “Original archival Figure” captions remain. Source-linked figure alt descriptions are attached to all three Word figures, but not printed as duplicate captions.

Post-render counts were **10 manuscript pages and 3 supplement pages**. Both Word files passed the bundled accessibility audit with **zero high, medium or low findings**. The archival main-source and supplementary claims remain the original frozen AusTraits observations, not new biological inference.

A separate [coauthor referee-risk review](https://github.com/zuizui0223/turnover/blob/paper/austraits-organ-ecology-v0-2/docs/AUSTRAITS_ORGAN_K_COAUTHOR_REFEREE_RISKS_V0_1.md) identifies priority objections: non-nested organ selection, K versus absolute evolutionary rates, unequal source-tip null geometry, species-selection versus source-value changes, and source/family nonindependence.

**Last scientific/editorial blocks:** Coauthor approvals, target journal and formatting, data-source redistribution/citation rights and explicit manuscript submission consent remain unresolved. Do not claim new independent primary-source replication or evolutionary selection from this paper package.

---

# AusTraits organ-function K paper — submission readiness (2026-10-19)

**Scope:** completed exploratory paper package on `paper/austraits-organ-ecology-v0-2`,
based on the fixed empirical branch `analysis/brownian-process-null-v0-1`.
**No new trait K, OU parameter, subgroup selection, database search, phylogenetic
reanalysis or biological p-value is performed in this branch.**

## 2026-10-19 editorial and reproducibility review (newly completed)

- **Exact original method trace:** The main Methods now documents species-rank records; nonmissing source DatasetID/ObservationID/genus/binomial; exact unit match; finite values; duplicate-record removal; original per-species medians strictly >0; natural-log transformation; pair-specific >=20 identical species; V.PhyloMaker2 S3, native GBOTB prune; invalid-tree/zero-variance holds; and parity checks with `phytools::phylosig`. These were verified against the original Python/R matched-tip source scripts. No new K was fitted.
- **Bibliographic correctness:** Formal titles, authors, volume, pages/article IDs and DOIs for Ackerly (2009), Wang et al. (2023) and Pothasin et al. (2022) were cross-checked against journal/PubMed records. No new hypothesis-discovery literature mining occurred.
- **Reviewer-facing supplementary tables:** `docs/AUSTRAITS_ORGAN_K_SUPPLEMENTARY_TABLES_V0_2.md` now reports original vs source-restricted denominators, 42-fold conditional LOFO skill, and all 142/101 stage transitions. A reporting-only QA gate verifies each numerator/denominator against the immutable claim registry.
- **Archived source provenance:** `data/austraits_organ_paper_claim_registry_v0_2.json` now points to the final complete original 34-family LOFO artifact **#38686389859** (not an earlier preliminary run); original empirical outcomes remain unchanged.
- **Data availability:** Clarifies that original measured AusTraits values are not redistributed in `turnover`; paper figures use aggregated source-linked artifacts and SHA256 provenance. External data access/licences and archival retention must be followed.
- **Statistical limit:** In addition to post-discovery organ-category selection, deep phylogenetic correlation between families and shared original studies can invalidate strict independence between bootstrap family clusters. Whole-family CIs are conditional/descriptive, not full evolutionary mechanism or post-selection uncertainty.

**CI verified after new Methods, references and supplement:**
[Manuscript + supplement reporting QA PASS #39229059135](https://github.com/zuizui0223/turnover/actions/runs/39229059135);
[three source-linked main figures PASS #39229059022](https://github.com/zuizui0223/turnover/actions/runs/39229059022).

**Editorial status: READY FOR AUTHOR/COAUTHOR SCIENTIFIC REVIEW, NOT SUBMISSION.**
No target journal, author approvals, redistribution permission for the full source matrix, submission consent or final journal formatting has been supplied. Preserve the original external confirmation gate and keep the PR as draft until those requirements are resolved.

---

## What actually passed

- **Manuscript claim QA: PASS** — [GitHub Actions #39227341212](https://github.com/zuizui0223/turnover/actions/runs/39227341212),
  including exact 142/101-pair sign-transition arithmetic and mandatory
  post-selection caveats.
- **Figures from immutable source outputs: PASS** — [GitHub Actions #39227341239](https://github.com/zuizui0223/turnover/actions/runs/39227341239),
  complete Figure 1–3 PNG+SVG files and a provenance/sha256 manifest.
- All three figure inputs are the **pre-existing** original outcome artifacts:
  [full original module/LOFO 34-family run #38686389859](https://github.com/zuizui0223/turnover/actions/runs/38686389859);
  [exact 142/101-stage transition run #39202352075](https://github.com/zuizui0223/turnover/actions/runs/39202352075);
  [strict shared-nonflora source K run #39006469805](https://github.com/zuizui0223/turnover/actions/runs/39006469805).
- No result was promoted from unmerged source discovery branches into the
  original 201-system BIEN temporal rho paper.

## Scientific claim hierarchy

| Evidence | Reportable claim | Explicit prohibition |
| --- | --- | --- |
| 313/406 S3, 314/397 native-prune same-species K comparisons, 34 families | In AusTraits, post-selected reproductive morphology **frequently exhibits higher estimated phylogenetic K** than sampled vegetative morphology | Not a universal slower evolutionary rate, stabilizing selection, or developmental constraint |
| One-parameter organ model, LOFO accuracy 64.5%/65.5%, Brier improvements on both native tree axes | The **retrospectively chosen** organ category contains limited within-compilation predictive information for K ordering when family model coefficients are held out | Not unbiased prospective performance: grouping was chosen after seeing original K outcomes, thus **non-nested hypothesis selection** and conditional family-bootstrap uncertainty |
| Fixed 142 S3 identities: 110→121→120 and 23 versus 9 reversals; prune: 82→83→81 and 13 versus 12 | Taxon/tip qualification can alter the observed organ difference **more** than identical-tip source-value substitution on S3; the pattern is weaker/different on prune | Do not attribute the stage 1→2 shift to species sampling **alone**: it also changes the tree and K normalization; no causal effect estimate |
| Original-tip homogeneous OU + calibrated source-noise posterior predictive discrepancy | A selected organ-direction feature is not fully reproduced by the tested source-OU scenario family, **conditional on its narrow assumptions** | The predeclared scalar rank-portability test was accommodated; the post-discovery discrepancy is not a preregistered model rejection or a test on matched tips |

**Preferred ecological one-sentence conclusion:** A coarse biological grouping
of reproductive versus vegetative morphology predicts the *relative ranking
of estimated plant phylogenetic signal* with modest retrospective portability,
while the choice of species and underlying observation sources materially
affects how strong that grouping appears.

The wording "modest retrospective portability" explicitly avoids mistaking
a 42-fold family holdout for independent original-source confirmation.

## Publication materials

| Component | Path | Current condition |
| --- | --- | --- |
| Full exploratory manuscript with figures/captions | `docs/AUSTRAITS_K_ORGAN_ECOLOGY_MANUSCRIPT_V0_2.md` | Text drafted, substantive claim guard passed |
| Numerical provenance registry | `data/austraits_organ_paper_claim_registry_v0_2.json` | Immutable source run IDs and fixed empirical observations |
| Claim QA | `scripts/qa/validate_austraits_k_organ_paper_claims_v0_2.py` | Positive and corruption tests PASS |
| Figure generator | `scripts/analysis/render_austraits_organ_k_paper_figures_v0_2.py` | Original source-linked family/margin summaries only |
| Figure workflow | `.github/workflows/austraits-organ-ecology-figures-v0-2.yml` | PASS; Figure 1–3 PNG/SVG + `figure_manifest.json` |
| Main pull request | [PR #38](https://github.com/zuizui0223/turnover/pull/38) | Draft, not merged/submitted |

## Actual blockers to sending a manuscript

1. **Authorship / target journal / formatting** and consent to submit have not
   been supplied. Preparing a draft is not authorization to submit it.
2. Complete bibliographic metadata, reference cross-check, availability/citation
   terms, and final language/style quality control remain editorial tasks.
3. Original-data limitation must be disclosed, prominently and early:
   original post-outcome group selection, non-nested family model-selection,
   reused source regimes and mixed organ homology. Neither a novel adaptive
   process nor a *confirmed* universal reproductive signal hierarchy is shown.
4. If targeting a journal that requires a **prospectively tested independent
   phylogenetic macroevolutionary hypothesis**, the current paper does not
   meet that bar. Do not redefine the frozen external-data requirement or
   disguise original source sensitivities as independent validation.

**Boundary reached:** the *exploratory manuscript text + reporting controls +
source-backed main figures* are complete. The next allowed changes here are
presentation, citation, language and publication format—not exploratory
re-analysis to find a stronger biological p-value. No new database is needed
to preserve and report the existing result.
