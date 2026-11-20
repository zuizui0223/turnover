# Evolution RC4 — anonymous files validated, remaining author-only submission gate

**Date:** 2026-11-20 (JST). **State:** ANONYMOUS REVIEW DOCUMENTS AND DERIVED REVIEW DATA COMPLETE; **NOT SUBMITTED**. Scientific design/results remain frozen.

## 1. Verified formatted anonymous files

From [GitHub Actions #44731825055](https://github.com/zuizui0223/turnover/actions/runs/44731825055), artifact #14626941673, ZIP SHA256:
\`2ecebc6c71deda84f0b4853cea4c58b4443f5f879b7447a15fc81f1440923e2c\`
(retention end recorded by Actions: 2027-02-18).

- Anonymous_Main_Manuscript_RC4.docx
- Anonymous_Main_Manuscript_RC4.pdf
- Anonymous_Figure_1.pdf
- Anonymous_Figure_2.pdf
- Anonymous_Figure_3.pdf
- all-page contact-sheet PNG and automated review report

**Layout/identity inspection:** Initial build exposed two problems under a second Word renderer: Figure 1 had separated from its caption, and Figure 2 legend obscured bars. The Word page-break and keep-with-next rules were corrected, and the Figure 2 legend moved outside the bars. The new full document was rendered both by GitHub LibreOffice and by an independent local Word rendering workflow. The result has exactly **19 pages**. **All 19 page images were inspected**, including full-resolution figure/caption pages. No blank pages, missing figure, caption separation, overlapping legend, clipped text or border overflow remains. Independent full 19-page image render from the final GitHub DOCX is pixel-identical to the manually inspected corrected local render.

**Accessibility:** python-docx document audit reports high=0 / medium=0 / low=0. Exactly three embedded figures contain alternative text; the editorial source uses Times New Roman 12pt and double-spaced body with continuous line numbering and page numbers. Author properties are set to Anonymous. PDF title/subject/author metadata and document XML were screened against personal identities and private development-repository paths.

**Content gate:** The operational “Remaining submission HOLD” paragraph was removed from the scientific manuscript Limitations and is instead tracked in the separate author-only submission gate. The neutral reviewer manuscript excludes the internal evidence/CI status section. The protected original RC3 remains an obsolete HOLD and is not used.

## 2. Anonymous 201-system data/code for review

[GitHub Actions #44731211225](https://github.com/zuizui0223/turnover/actions/runs/44731211225), artifact #14625848802, ZIP SHA256:
\`102f39152914025b7858f6181c9f439e883279c384fcb1d31b57cd50fac32d92\`.

Nested Anonymous_RC4_Evidence_Review.zip contains **201 corrected system records (49 recalculated and 152 unchanged)**, their original aggregate summaries and source-preserving R analysis/figure-generation scripts. The reviewer README explains the fixed statistical models, scientific constraints and BIEN data sources. It omits species-level BIEN records and raw observations. CI verifies all 201 unique records, archive integrity and no repository-owner identity, email, author full name or development GitHub URL inside the reviewer archive. This is a review source bundle, not yet a licensed persistent public data archive.

Unchanged original model replay on recovered input: [Actions #44542568468](https://github.com/zuizui0223/turnover/actions/runs/44542568468), **30/30 frozen checks identical**. The corrected species-state logs, 201 rho/SE table, raw/log impact, uncertainty inputs, and three figures were independently checked prior to document construction.

## 3. Current official Evolution submission rules checked

[Oxford Academic: Evolution author guidelines](https://academic.oup.com/evolut/pages/author-guidelines) specify double-anonymized review, separate identifying title page, anonymous filenames and manuscript, line numbering, Times New Roman 12pt/double spacing preferred, figures with captions and alternative text, and AI assistance disclosure in the manuscript and cover letter. Original Article guideline: **7500 words excluding abstract, tables, figure legends and references**. The manuscript is below that threshold.

The source-aware manuscript is an Original Article draft. Initial submission is free-format; standalone figure PDFs are supplied for easy review and accepted figure format. These files are not proof of acceptance or publication.

## 4. Remaining author-only decisions (submission HOLD)

1. Complete and approve separate title page: author list/order, affiliations, corresponding author, CRediT, funding, conflicts, acknowledgments; see \`docs/EVOLUTION_RC4_TITLE_PAGE_AUTHOR_ONLY_TEMPLATE_V0_1.md\`.
2. Complete and approve \`docs/EVOLUTION_RC4_COVER_LETTER_AUTHOR_ONLY_V0_1.md\`, including statements on related/overlapping manuscripts and explicit author approval.
3. Confirm data/software licences and all third-party data rights; choose and create a persistent public archive under an accepted access policy and finalize Data Availability.
4. Coauthor review of corrected raw/log results, prospective/post-outcome distinctions, figure captions, bibliography, anonymous artifacts and AI-use declaration; then authorize journal-portal submission.

**Do not merge, mark ready to submit, change scientific thresholds, retrofit new tests or submit the manuscript automatically.** Author choices and approvals remain external.
