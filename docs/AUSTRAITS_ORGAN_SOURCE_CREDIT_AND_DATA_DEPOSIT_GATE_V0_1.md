# AusTraits organ-K: original study attribution and data/code submission gate

**28 October 2026 — empirically verified original-source audit, but NOT a human-approved bibliography or journal submission.**

## What is actually reconstructed

- Public original dataset: AusTraits v7.0.0, https://doi.org/10.5281/zenodo.15718081
- Exact original measurement Parquet SHA256: 5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99
- Exact original compiled v7.0.0 ZIP SHA256: 2995fb9e5eebf9271f9241b5a6c2e2cbb7b45e8eda5ce4db43c14c68f95e2f3f
- The same ZIP contains source citation metadata in methods.csv and 509 entries in sources.bib. The flattened Parquet contains DatasetID, source_id, method_id, basis_of_value, primary citation and, where available, secondary/original-source citation fields.

[Original public v7 record-selection/citation audit #40612020973 PASS](https://github.com/zuizui0223/turnover/actions/runs/40612020973) repeated the original source-native exact-unit, observation deduplication and positive-species-median eligibility for **254 single K systems**, the **760 originally supported common-species trait pairs**, and the original **142 strict same-remaining-DatasetID trait pairs**. No phylogenetic K was re-fitted and no biological effect was newly tested.

| Original analysis population | Distinct AusTraits DatasetIDs | Original deduplicated measurement rows within eligible states |
| --- | ---: | ---: |
| 254 single-trait K systems | 190 | 228,110 |
| 760 matched-taxon paired K population | 190 | 222,586 |
| 142 original strict common-DatasetID pairs | 44 | 31,401 |

**Denominator warning:** These are rows of original measurements after the stated source/species deduplication, NOT independent specimens, independently measured organismal pairs, family-level K comparisons, biological replicates or publications. One original measurement can contribute to multiple system-level K contexts and conditions. DatasetIDs are indexing units, not proven primary literature or source-level independence.

## Source concentration in the strict 142-pair cohort

The first five original DatasetIDs account for **23,122 of 31,401 (73.6%)** deduplicated source measurement rows participating in the strict same-DatasetID comparison:

| DatasetID | Source rows | Strict-source share | Publication attribution status |
| --- | ---: | ---: | --- |
| Kooyman_2011 | 8,178 | 26.0% | One primary citation key, method-linked |
| Maslin_2012 | 5,419 | 17.3% | One primary citation key; WATTLE identification resource, not automatically an independent specimen measurement |
| Cooper_2013 | 4,167 | 13.3% | One primary citation key; book-derived descriptions require organ/measurement concept review |
| GrassBase_2014 | 3,033 | 9.7% | Primary citation text is available, but its key is unresolved against the compiled v7 sources.bib |
| Everingham_2020 | 2,325 | 7.4% | One primary citation key, method-linked |
| Other 39 DatasetIDs | 8,279 | 26.4% | Mixed original/method/source credit requirements |

This is **descriptive provenance concentration**, not a new K/trait effect, an effective number of independent source studies or an observed bias estimate. In particular, the finding strengthens the manuscript's caveat that source-restricted K is not an independent primary-data replication; family-level bootstrap intervals alone do not represent uncertainty arising from shared original source publications.

## Bibliography inventory for coauthor review

[Compact original public v7 citation-review CI #40612516608 PASS](https://github.com/zuizui0223/turnover/actions/runs/40612516608) generated:

- dataset_priority_and_credit_gaps.csv: **190 DatasetIDs**, ranked first by **44 strict-cohort** inputs, then the remaining 146. Each row reports the original analysis tier's record exposure, primary/secondary/original-study citation keys, source/method-ID diversity, and unresolved credit flags.
- cited_original_publication_candidates.csv: **299 DatasetID-by-citation-role** entries. Semicolon-separated keys in compiled source metadata were split into individually checkable BibTeX references; the v7 original citation strings were retained as **metadata candidates**, not automatically author-certified reference text.
- original_AusTraits_v7_contributing_citations.bib: **247** individual entries copied from the same compiled 509-entry original release bibliography, selected using the original candidate keys, not external bibliography databases.
- basis_of_value_review_summary.csv: categories originally marked measurement or expert_score, with an explicit count of multiple citation/basis labels per original deduplicated record. These are **metadata label counts**, not unique observation counts and not a measure of all original studies' data quality.
- original_source_citation_priority_verdict.json: explicit source SHAs and HUMAN_APPROVAL_FALSE status.

**Unresolved original-source mapping is nonzero and important.** Across all 190 DatasetIDs, the audit flagged **30** with at least one individual citation key absent from the compiled v7 BibTeX, **12** with multiple source_id values and **30** needing secondary/original dataset credit examination. For the highest-priority strict **44 DatasetIDs**, these groups involve **11**, **4**, and **8** DatasetIDs, respectively. There are **51** unresolved individual BibTeX keys across the selected reference roles; these are *not* automatically 51 missing citations, because the original flattened methods table may still contain human-readable citation text, and some may be resource URLs or source-key aliases. Zero of 190 DatasetIDs lacked a primary-citation key in the direct metadata matching audit.

This is not proof that 190 primary publications have been individually checked. A single DatasetID may reflect a secondary flora, compilation or book, a source_id may reference a particular source within that compilation, and method_id may distinguish measurement protocols. Coauthors must verify primary versus secondary/source-original keys before any bibliography is submitted, especially for the strict 44 DatasetIDs.

## Submission gate of the provisional Ecology and Evolution venue (28 October 2026)

Current official instructions (https://onlinelibrary.wiley.com/page/journal/20457758/homepage/forauthors.html) require all source **data, metadata and code at submission** for editorial/referee review. The journal's minimum data/code standards (Jenkins et al. 2023, https://doi.org/10.1002/ece3.9961) discourage unnecessary redeposition of data already publicly versioned, but request an accessible **permanent DOI for code archives**; GitHub's current draft branch and expiring Actions artifacts are not a substitute for a permanent submission archive.

Current concrete evidence:
1. All three original numerical K computation paths (254 original single-trait, 760 common-tip pairs, and 283/142 source-restricted K plus original 5,000-family bootstrap) have been cleanly rerun with pinned public v7 release SHA256 and permanently archived derived results on the draft paper branch.
2. Original compiled v7 data and source metadata are available via the cited release DOI, and a source-linked DatasetID/bibliography review index is committed. The original measurements have not been copied or redistributed by this paper.
3. The **author-verified contributing-study bibliography**, original observation/source credit validation, complete submission metadata README, and a **permanent DOI-bearing snapshot of analysis code and derived inputs** remain unverified. None has been automatically approved or deposited.

**Next human checkpoint:** coauthors should first review the top 44 strict-cohort DatasetIDs and 11 strict unresolved BibTeX mappings, confirm original study versus secondary compilation credits and acceptable source/data rights, and authorize a final data+code DOI deposit strategy. Do **not** create a Zenodo/Dryad record, claim editorial compliance, merge PR #38 or submit a manuscript on the basis of this automated citation-index alone.

## Code snapshot candidate is now prepared, NOT deposited (28 October 2026)

[Review-only code/derived data snapshot #40613783734 PASS](https://github.com/zuizui0223/turnover/actions/runs/40613783734) produced an independently SHA256-checked **1,037-file / 1,800,889-byte ZIP** from exact Git snapshot fe63f622edb8a8ec23b86673300e582140c8f7b7. Its ZIP SHA256 is 0eb593f07003c55f3a1e2b66e66b64cdd115700d253f8a5a36ac7d3d74a0e1f0. Exact per-file source checksums and the ZIP integrity verdict were permanently committed to results/austraits_organ_paper_code_snapshot_candidate_v0_1/, and the ZIP itself is available as a **time-limited GitHub Actions artifact**. No source-level AusTraits measurement records were redistributed.

The [review-candidate scope and author approval checklist](https://github.com/zuizui0223/turnover/blob/paper/austraits-organ-ecology-v0-2/docs/AUSTRAITS_ORGAN_CODE_SNAPSHOT_REVIEW_CANDIDATE_V0_1.md) state precisely that this is not an author-approved final release and **does not have a code DOI**. It references the existing public original AusTraits v7 data DOI/SHA, pinned source-native units, native V.PhyloMaker2 and prior full 254/760/283/142 original-data K numerical reproduction.

**The concrete build-workflow gap is now closed, but the publication/DOI gate remains open.** Authors must approve bibliography/source study credit, a final immutable paper/code snapshot and appropriate versioned Zenodo or equivalent deposit licence, metadata, DOI and target-journal data+code policy. Do not create a code DOI or journal submission without explicit coauthor authorization. The current candidate commit is not automatically the latest paper PR HEAD.

## Interpretation preserved

The organ K direction remains retrospective 313/406 S3 and 314/397 native prune on matched tips. The source/taxon change remains 110→121→120 S3 and 82→83→81 prune on the exact original 142/101 family×named-trait-pair identities. Source selection changes species/tree geometry jointly, while the final value substitution uses the same eligible species/tree. Neither data-source concentration nor a completed numerical reconstruction identifies evolutionary rates, developmental constraint, OU selection or causal mechanisms.
