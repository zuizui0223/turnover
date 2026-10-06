> **SUBMISSION HOLD (2026-10-06):** RC3 passed formatting/anonymity QA, but submission is paused until draft PR #30 (`audit/trait-memory-nonpositive-values-v0-1`) completes the frozen raw-data audit of nonpositive species medians. Do not submit the current ZIP before this hold is resolved.

# Evolution submission readiness — trait-memory paper

Checked against current *Evolution* author guidance on 2026-10-05.

## Target

**Evolution — Original Article**

Working title:

**Phylogenetic trait memory is lineage-contingent, with little transferable trait-level signal across plant families**

## Scientific status

The v0.3 robustness programme is closed for claim strengthening.

Current central result:

> Family context contributes a modest repeatable component to phylogenetic trait memory, but trait identity carries little robust information that transfers to an unseen family.

## Current package

- Full manuscript draft: `docs/TRAIT_MEMORY_EVOLUTION_MANUSCRIPT_V0_3.md`
- Abstract: `docs/TRAIT_MEMORY_EVOLUTION_ABSTRACT_V0_1.md`
- Figure captions: `docs/TRAIT_MEMORY_FIGURE_CAPTIONS_V0_2.md`
- Figure plan: `data/trait_memory_figure_plan_v0_1.json`
- Novelty boundary: `docs/TRAIT_MEMORY_NOVELTY_BOUNDARY_V0_2.md`
- Statistic positioning: `docs/TRAIT_MEMORY_STATISTIC_POSITIONING_V0_3.md`
- Evolution positioning: `docs/TRAIT_MEMORY_EVOLUTION_POSITIONING_V0_1.md`
- Cover letter: `docs/TRAIT_MEMORY_EVOLUTION_COVER_LETTER_V0_1.md`
- Canonical post-robustness synthesis: `results/trait_memory_context_synthesis_v0_2/result.json`

## Evolution format

Current guidance for Original Articles:
- maximum 7,500 words excluding abstract, tables, figure captions and references;
- substantive empirical study or theoretical advance bearing on a significant evolutionary question;
- required sections: Abstract and Keywords, Introduction, Materials and methods, Results, Discussion;
- abstract maximum 200 words and no abbreviations;
- three to six keywords;
- teaser text is encouraged and must be <=100 words;
- line numbers are required in the submitted manuscript;
- double-anonymized review: all review files and filenames except the separate title page must be anonymized;
- separate title page must contain Data availability, Author contributions, Funding, Conflict of interest and Acknowledgements;
- LLM use must be disclosed in the cover letter and Methods/Acknowledgements with technical specifications and method of application.

Current direct audit:
- abstract: 176 words;
- teaser: 43 words;
- keywords: 6;
- abstract contains neither S3 nor BLUP abbreviations;
- LLM disclosure is present in manuscript and cover letter.

## Required wording boundary

Allowed:
- family-level repeatability persists after measurement-error and redundancy audits;
- trait-level portability is weak;
- shrinkage removes most apparent prediction penalty;
- roughly one quarter of typical total variation is sampling uncertainty;
- the biological cause of family context is unresolved.

Prohibited:
- “most memory is system-specific”;
- “trait identity is anti-portable”;
- “family context dominates trait identity”;
- “family effects identify a causal evolutionary regime”;
- “raw-scale results are log-scale robust”;
- any spatial-turnover conclusion.

## Remaining submission work

1. Finalize references and keep formatting internally consistent; initial submission is format-free.
2. Fill author/title-page placeholders outside the anonymous scientific text.
3. Build the anonymous peer-review data/code bundle and confirm its identity firewall.
4. Generate the final editable manuscript with continuous line numbers.
5. Confirm the final data/code archive strategy for acceptance/publication.
6. Run the Evolution paper-package and submission-freeze contracts on the final head.
7. Submit to *Evolution* first; JEB is the strongest fallback if editorial scope is judged too narrow.


## RC3 editorial audit

- Abstract primary-evidence list excludes the post-outcome provenance sensitivity; provenance remains a labeled supplementary robustness check in the main text.
- Mantel-statistic wording is balanced against Harmon & Glor (2010), Hardy & Pavoine (2012), and Pavoine & Ricotta (2013): performance depends on the chosen distance definitions and measurement error, so rho is not presented as uniformly superior or inferior to K-type statistics.
- Pavoine & Ricotta (2013) authorship and citation metadata were verified against the original *Evolution* article.
- Pearse et al. (2025), BIEN 2026, V.PhyloMaker2 2022, and Debastiani et al. 2021 bibliographic metadata were rechecked against publisher pages.
- Reviewer prebuttal: `docs/TRAIT_MEMORY_EVOLUTION_REVIEWER_PREBUTTAL_V0_1.md`.
- Anonymous DOCX RC3: 23 pages, 12-point Times New Roman, double-spaced, continuous line numbers, three figures with alt text, accessibility audit 0 issues, author/repository identifier scan 0 hits.


## Submission hold — nonpositive trait-value audit

Reason: 25 primary-tree systems and 18 prune-only systems contain at least one species median <=0. These occur in physical size/mass traits whose semantic domain is positive.

The audit is deliberately separated from outcome analysis:
- Stage A re-queries BIEN 4.2.8 raw values, units, sources and citations;
- it reconstructs frozen tree membership only to determine whether invalid medians entered rho inputs;
- it does not recompute rho or downstream manuscript statistics;
- any Stage B impact sensitivity requires a new frozen design after Stage A.

Submission hold can be lifted only after:
1. Stage A identity gate reproduces the v0.3 25/18 blocker;
2. raw-value provenance is classified;
3. any required Stage B sensitivity is prospectively frozen and completed, or Stage A shows no input-validity problem.
