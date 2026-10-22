# Full fresh-runtime regeneration of the original 760 AusTraits organ-K comparisons

**22 October 2026 — execution protocol, NOT a new biological experiment.**

## Scope
The analysis uses the original public AusTraits v7.0.0 flattened Parquet, with its exact original SHA256 value 5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99, the original source-native trait units and the V.PhyloMaker2 S3/native-prune trees. The original 254-system K reference, all 770 source-only candidate pair identities (including 760 qualified pairs), and all 24 original matched K batch outputs have been permanently preserved with SHA256 in the paper branch. The original individual species measurements have not been uploaded to the repository.

The GitHub Actions workflow **austraits-organ-full-760-raw-k-rebuild-v0-1.yml** reconstructs exactly those original 24 source-only batches and reruns all 760 already-qualified trait pairs in up to eight concurrent clean Ubuntu/R jobs using the original R/C++ K estimator and public source download. For each pair, the script **rebuild_austraits_organ_all_760_K_v0_1.py** checks both newly computed K values, signed log-K contrast, tree-tip support and PASS/HOLD status against the corresponding frozen historical pair. It fails closed on missing pairs, shifted species cohorts, changed native phylogenies and K numeric differences greater than relative 1e-7 or absolute 2e-8.

The independent final aggregation job must see all 24 completed batches, S3 **760 PASS**, prune **747 PASS / 13 HOLD**, and the same original cross-organ direction counts **313/406 S3** and **314/397 prune**, then upload one SHA256-backed summary. The original pair grouping and these expected outcomes are regression checks, NOT new effect estimates.

**Workflow:** https://github.com/zuizui0223/turnover/actions/runs/39713644617

## Interpretation and submission gates
A successful workflow would establish computational reproducibility **within the original AusTraits dataset**, not independent physical measurements, an evolutionary mechanism, absolute evolutionary rates, a prospective organ hypothesis, or a universal law. A started workflow or successful workload-planning step does not establish success for all K results. Report a full replay as PASSED only after its final aggregation has completed successfully. Keep all K results and the original scientific claims frozen. Journal compliance, contributing-study citations, authorship, conflicts/funding and consent to submit remain separate gates.
