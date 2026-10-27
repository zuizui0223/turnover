# Full original 254 single-trait Blomberg K source-to-phytools reproducibility

**28 October 2026 — original sources permanently pinned; full clean-runtime phytools K rerun started. Full result must be checked from completed Actions, not inferred from a launched job.**

## Why run the original 254 separate K systems?
The paper's original **760 matched-tip trait-pair K comparisons** (760 S3/747 native prune) and **283 broad plus 142 strict nonflora source-stage K comparisons** have now been reproduced from the exact public AusTraits v7.0.0 file with historical K/log-K numerical difference 0.0, and permanently archived. But the earlier separately fitted **254 single-trait K system table** is an original reference input to the source/tip contrast calculation and had not been re-executed. This closes a technical reference dependency, not a new biological sample.

## Exact original per-system K reference preservation
Original full R K source run: https://github.com/zuizui0223/turnover/actions/runs/37725935020

Before the historical 16 original run artifacts expire, all 254 original per-system nonraw K JSONs were downloaded, checked and permanently committed with SHA256 by https://github.com/zuizui0223/turnover/actions/runs/40540814335 (PASS).

Repository source reference: https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_original_254_single_K_v0_1

The fixed source population comprises **254 K systems, 42 plant families and 13 named traits**, from the 259-system source core. Original individual measurements, specimen IDs and original record IDs have not been redistributed. They remain in the versioned publicly available AusTraits v7 Parquet (DOI 10.5281/zenodo.15718081, SHA256 5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99).

### Different, not interchangeable, species and phylogeny cardinalities
The source eligibility count, the V.PhyloMaker prune/bind crosswalk status count and the final native S3 K tree tip count are not always equal.

- Chenopodiaceae, leaf_length: 305 original input species, 67 prune + 229 bind, and 296 realized S3 K tips.
- Poaceae, leaf_length: 1,268 original input species, 456 prune + 812 bind, but 1,267 realized S3 K tips.

The original archived per-system phylogenetic tip counts are the authoritative numerical regression target. Do not alter biological observations or assume that the whole input/crosswalk species count must equal the actual realized K tree. This explains and repairs the earlier source-archive QA's faulty equality premise.

## Complete phytools K clean-source replay (running)
- The original unchanged R numerical estimator (scripts/analysis/run_austraits_blomberg_k_system_v0_1.R) computes phytools::phylosig K on the original S3/native prune trees, called from the unchanged Python source-native positive median-state compiler.
- The pinned native phylogeny uses V.PhyloMaker2 at 7af3fb5152f691af2e4ec9d5e2e467d1b50505e9 and the original traits units at AusTraits build commit 7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c.
- The new original reference comparator (scripts/qa/rebuild_austraits_original_254_single_K_v0_1.py) restores 16 original workload bins and compares every original family/trait ID, realized S3/prune tip support, both K values and both log K values with SHA256-frozen historical per-system R JSON.
- Original jsonlite serializes K and log K to four decimal places. Numerical matching therefore uses absolute tolerance 5.1e-5, relative 1e-7, without relaxing exact family/trait/native-tip identity.

Full run: https://github.com/zuizui0223/turnover/actions/runs/40541276639

## Retention and scientific scope
A gated archival workflow is staged at .github/workflows/austraits-organ-archive-public-254-single-K-replay-v0-1.yml. It requires an actually completed all-16-batch K and final 254-system numerical regression PASS before its trigger file may be added. If successful, it will permanently store 254 new per-system K reports, 16 batch audits, final summary and SHA256 provenance without any original raw species measurements.

**The full 254 K rerun is not yet verified until its entire CI and final aggregation actually pass.** This original-data numerical reproduction does not certify independent primary source data, a new evolutionary mechanism, future model performance, universal reproductive conservation, prospective organ grouping or journal submission readiness. Coauthor scientific approval, source attributions and journal-level data/metadata/code/access remain separate human gates.
