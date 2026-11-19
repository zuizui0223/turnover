# Evolution RC4 — figure captions, source identity, and accessibility text (2026-11-19)

**Scientific source cut:** October 6, 2026 frozen Stage B (`37443037590`) and October 5, 2026 original raw-scale v0.3 (`37281031394`). All three figure concepts are *presentations of these existing outcomes*, not new inferential tests.

**Source data:** `results/trait_memory_positive_only_cleaning_impact_v0_2/effects_positive_only_cleaned_recovered_v0_2.csv` (**201 family×trait rows, 30 columns**) and same-directory `result.json`. Original job-log JSON fragments and `recovered_201_provenance_v0_1.json` retain each recovered source and the 49 corrected / 152 inherited split. Independent row and total-variance identity QA: [Actions #44541550788](https://github.com/zuizui0223/turnover/actions/runs/44541550788) **PASS**, artifact #14538043215 (90-day retention). Figures are regenerated deterministically by `scripts/figures/render_trait_memory_rc4_cleaned_v0_1.py`.

## Figure 1. Source-value correction and phylogenetic memory gradients

**Caption.** Relationship between original and positive-only cleaned Spearman correlation of patristic separation with absolute species trait differences across all **201** prospectively qualified family×trait systems. Panels show the primary S3 phylogeny and a backbone-native prune-only sensitivity. Separately plotted unchanged and corrected markers distinguish the **152** source-valid systems inherited without alteration from the **49** systems recomputed after removing inadmissible nonpositive source records in the five predeclared strictly positive physical traits. The dashed line is identity, not a regression fit. Original-vs-cleaned rho Spearman association was **0.9910** (S3) and **0.9936** (prune-only), with **2** and **3** gradient sign changes. The image does not depict an evolutionary rate or demonstrate selective constraint.

**Alt text.** Two scatter panels compare 201 original and corrected phylogenetic memory gradient estimates. Most points lie on the diagonal; a subset of 49 corrected systems shows deviations. The two tree treatments yield similar near-identity patterns.

## Figure 2. Uncertainty-aware variation in cleaned memory gradients

**Caption.** Point decomposition of the *typical total variation* in phylogenetic memory gradients from the same crossed measurement-error-aware model applied to both **cleaned raw** and **cleaned log** species trait states, each on S3 and prune-only trees. Point shares sum to 100% within each representation and tree and partition estimated family-level, trait-level, between-system heterogeneity and finite-species bootstrap sampling error. On raw S3, these were **16.22% family, 6.38% trait, 54.22% system heterogeneity and 23.18% sampling uncertainty**. On log S3, they were **12.46%, 8.96%, 55.13% and 23.45%**, respectively. Shares are **point estimates without plotted confidence intervals**. The original 500-fit two-way cluster-bootstrap uncertainty is broad and overlapping; the figure does **not** support ranking variance components by statistical dominance. Repeated species pairs are not independent sampling units.

**Alt text.** Four 100-percent stacked bars show how family, trait, unresolved between-system variability and finite-species sampling error contribute to corrected memory gradients on raw and logarithmic scales for both phylogenetic treatments. Sampling uncertainty occupies roughly one quarter of each bar.

## Figure 3. Trait identity transfers differently on raw versus logarithmic scale

**Caption.** Leave-one-family-out prediction gains from the **same training-only shrinkage trait BLUP** relative to the held-out-family global training-mean baseline, using the same 201 qualified systems. The result is expressed as `100 × (1 − SSE_BLUP / SSE_global)`, and the thin horizontal reference line marks no incremental prediction. Gains on corrected raw trait states were **+1.21% (S3)** and **+0.003% (prune-only)**; on corrected log states they were **+5.92%** and **+5.51%**. No new permutation significance test of the scale contrast was performed. This comparison should not be described as demonstrating the absence of all portable trait information or as evidence for faster or slower evolutionary rates.

**Alt text.** Two pairs of bars compare the incremental predictive information from trait identity across unseen plant families. Gains are near zero for raw trait states and approximately five to six percent for logarithmic states across both tree treatments.

## Provenance, limits, and packaging

The original 201-system per-system tables were recovered from source GitHub job stdout, not imputed from summary statistics. Corrected rho and SEs for the 49 contaminated systems and original raw values for these systems were independently matched, and the final recovered table reproduces the published Stage B change statistics, all original species-removal totals, and the four means of species-bootstrap SE squared used in the crossed meta-analysis. **No species identity, raw trait measurement, raw plot row or biological response was redistributed** in these figures or tables.

These are proposed **three RC4 main figure concepts**, not final figures approved by all authors. Check 100%-zoom rendering, legend wording, journal typography and page fit. The source-verified six PNG/SVG files are currently available through the temporary GitHub Actions artifact; all inputs and figure-generating code remain in this repository for regeneration. Main manuscript submission still requires a newly rendered anonymous DOCX/PDF, a check for links and labels, source licences, coauthor review and explicit submission authorization. Old RC3 figures remain invalid for RC4.
