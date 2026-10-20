# AusTraits organ-K — coauthor submission decision and unresolved gates (v0.1)

**20 October 2026. Status: COAUTHOR REVIEW ONLY — NOT SUBMISSION AUTHORIZATION.**
Applies to [turnover draft PR #38](https://github.com/zuizui0223/turnover/pull/38) at its checked paper branch. This document is not a journal selection, author declaration, new ecological dataset or peer-review response.

## Scientific result being offered
- **Observation 1:** On the *same species and same native tree for each matched pair*, the retrospectively selected reproductive-versus-vegetative grouping yields higher reproductive Blomberg's K in **313/406 S3** and **314/397 native-prune** family-by-trait-pair comparisons, across 34 families. Original family-equal rates: **74.7%** and **75.8%**. At family-majority level, **27/34 S3** and **30/34 prune** favor reproductive K in their sampled comparisons. These are dependent rows, not hundreds of independent evolutionary origins.
- **Observation 2:** On exactly the same original pair identities under stronger non-flora source qualification, **110→121→120/142 S3** and **82→83→81/101 prune** reproductive-higher contrasts show that available species/tips/tree geometry and measured-source values can change the apparent regularity. The first transition changes species, pruning and K normalization jointly; it is not a causal estimate of species selection alone.
- **Not an independent third discovery:** 64.47%/65.46% organ-only LOFO hard accuracy is an algebraic re-expression of observation 1 with half-credit within-organ ties. Brier gains remain *post-selected conditional* probabilistic scores.
- No inferred rate of evolution, OU stabilizing selection, universally conserved organ property, prospectively chosen grouping, or original-publication-independent validation.

## Nonbinding publication venue comparison
**Provisional first fit: *Ecology and Evolution* (Wiley), Research Article.**
- Publisher scope: https://onlinelibrary.wiley.com/journal/20457758
- Publisher author guidelines, checked **20 October 2026**: https://onlinelibrary.wiley.com/page/journal/20457758/homepage/forauthors.html
- Broad empirical/descriptive ecological and evolutionary research is within scope; initial **free-format** manuscript preparation is allowed. The specified initial-submission checklist includes **4–6 keywords**, full author/affiliation/title details, a concise cover letter, Data Accessibility Statement, competing interests, author contributions, funding and acknowledgments. Separate figure files may be requested by the journal.
- **Potentially decisive constraint:** Authors must supply **data, metadata and code at submission** for editorial and referee examination, with subsequent public data/code archiving obligations. Having a versioned public AusTraits DOI, code repository and reproducible *aggregate figures* is meaningful evidence, but **is not a verified pass of the journal's complete-data gate**; the original full matched analytic data subset has not been independently reconstructed and checked here.
- **Costs and correspondence:** Fully open access, potentially charge-bearing. Do not promise funding, waivers or institutional eligibility. The authors must decide venue, APC coverage and corresponding author.

**Other possible fits, not selected:**
- *Journal of Plant Ecology* (Oxford): https://academic.oup.com/jpe/pages/General_Instructions . Plant evolutionary ecology is in scope, but since August 2025 the journal specifies **double-anonymous review**, a separate identified title page, journal-style/line-numbered Word manuscript and other submission requirements. **The current named GitHub review package is not an anonymized JPE submission file.**
- *American Journal of Botany* (Botanical Society of America): https://bsapubs.onlinelibrary.wiley.com/hub/journal/15372197/homepage/productinformation . Good topical plant evolution fit, but it expressly expects broadly **significant, innovative** botanical research; the current non-nested, within-AusTraits exploratory analysis may face a stronger novelty/independent-validation objection.

These are **scope-based editorial judgments, not promises of acceptance**. Do not target *Methods in Ecology and Evolution* as a standalone new method paper: the work uses existing comparative methods rather than introducing and validating a new broad method.

## Existing machine-checkable evidence (already completed)
1. Original source-only aggregates and file-SHA256 provenance manifest are committed under \`results/austraits_organ_paper_frozen_aggregate_inputs_v0_1/\`.
2. Core analytical source files, matched-tip R/Python scripts, manuscript and source-linked figure builders are in the repository.
3. Original analytical K/LOFO outputs, stage transitions, family compositional descriptors and their inferential limits are covered by automated source/claim checks.
4. Two main figures + one supplementary Brier graphic and editable manuscript/supplement DOCX/PDF can be regenerated by CI from the PR. Successful figure regeneration is **not** the same as independent raw-trait-to-K reconstruction.

## Human verification — still OPEN, not silently inferred
- [ ] **Author/affiliation/correspondence approval:** actual complete authors, roles, contribution approvals, institution names and corresponding author. No author names, addresses, acknowledgments or declarations were fabricated.
- [ ] **Conflicts/funding/AI tool disclosures:** corresponding author obtains truthful statements from all authors and checks journal-specific requirements. No auto-generated "none" claims.
- [ ] **Data+metadata+code compliance:** verify the exact AusTraits v7.0.0 source-native records, original DatasetID and ObservationID metadata, attribution, analytical subset/provenance, and an executable path from public data+code to the primary K outputs. Currently aggregate reproduction is verified; **full original raw-to-K reconstruction was not rerun on an independent clean environment as part of this paper package**. Confirm this suffices with target-journal rules before submission.
- [ ] **Journal and APC decision:** coauthors actually select a venue, article category and publication-charge route (if applicable); check the current publisher instructions once more before pressing Submit.
- [ ] **Submission authorization:** coauthors review the final PDFs, source limits and declarations, and give explicit permission. PR remains Draft/unmerged and no journal submission is authorized.

## Suggested coauthor scientific decisions
1. Accept the two-observation evidence hierarchy, including non-nested selection and the LOFO algebraic identity, or identify a specific claim that must be weakened.
2. Confirm that the source/tip staging does **not** justify a causal measurement-error or evolutionary mechanism inference.
3. Resolve measurement concepts and original contributing-study credits (e.g., leaf vs leaflet, fruit vs dispersal unit).
4. Decide whether to submit as an **exploratory AusTraits comparative paper**, without new trait or phylogenetic refitting.
5. Approve the author/COI/funding/data-code checklist, then explicitly authorize a chosen venue or request targeted corrections.

## Final state
This branch is **ready to be read and commented on by real coauthors**, but **not verified ready for journal submission**. No TRY or new external trait database is opened; this paper remains a frozen observational synthesis. No fictitious editorial review decisions, independent replications or author approvals are asserted.
