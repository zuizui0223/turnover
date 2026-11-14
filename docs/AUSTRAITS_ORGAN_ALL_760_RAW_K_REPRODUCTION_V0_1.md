# Full fresh-runtime regeneration of the original 760 AusTraits organ-K comparisons

**22 October 2026 — execution protocol, NOT a new biological experiment.**

## Scope
The analysis uses the original public AusTraits v7.0.0 flattened Parquet, with its exact original SHA256 value 5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99, the original source-native trait units and the V.PhyloMaker2 S3/native-prune trees. The original 254-system K reference, all 770 source-only candidate pair identities (including 760 qualified pairs), and all 24 original matched K batch outputs have been permanently preserved with SHA256 in the paper branch. The original individual species measurements have not been uploaded to the repository.

The GitHub Actions workflow **austraits-organ-full-760-raw-k-rebuild-v0-1.yml** reconstructs exactly those original 24 source-only batches and reruns all 760 already-qualified trait pairs in up to eight concurrent clean Ubuntu/R jobs using the original R/C++ K estimator and public source download. For each pair, the script **rebuild_austraits_organ_all_760_K_v0_1.py** checks both newly computed K values, signed log-K contrast, tree-tip support and PASS/HOLD status against the corresponding frozen historical pair. It fails closed on missing pairs, shifted species cohorts, changed native phylogenies and K numeric differences greater than relative 1e-7 or absolute 2e-8.

The independent final aggregation job must see all 24 completed batches, S3 **760 PASS**, prune **747 PASS / 13 HOLD**, and the same original cross-organ direction counts **313/406 S3** and **314/397 prune**, then upload one SHA256-backed summary. The original pair grouping and these expected outcomes are regression checks, NOT new effect estimates.

**Workflow:** https://github.com/zuizui0223/turnover/actions/runs/39713644617

## Final result — 22 October 2026, full PASS with permanent archive

[Original full-760 GitHub Actions #39713644617](https://github.com/zuizui0223/turnover/actions/runs/39713644617) **completed successfully, all 26/26 jobs**. Every one of the original 24 R/C++ batches completed; the final audit required complete source-cohort coverage and verified **S3 760 PASS / 0 HOLD, native prune 747 PASS / 13 HOLD**, **406/397 cross-organ comparisons** and **313/314 original reproductive-higher results**. Across all original K and log-K values freshly computed from public AusTraits v7.0.0 and compared to the original SHA256-frozen historical outputs, the **maximum observed absolute discrepancy was 0.0**.

[Preservation workflow #39721134903 PASS](https://github.com/zuizui0223/turnover/actions/runs/39721134903) also independently rechecked and permanently archived all 24 freshly computed K batch results, 24 complete per-batch audit outputs, full original aggregate verdict, and the file-SHA256 archive manifest at [full public v7 replay outputs](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_public_v7_full_K_replay_v0_1). The final machine status is \`PASS_ALL_760_RAW_SOURCE_K_RECOMPUTED_AND_MATCHED\`.

**Precisely qualified scope:** This establishes complete numerical reproduction of the **original 760 common-tip paired-trait K computations** within the **same** original AusTraits source and fixed GBOTB tree version. It does not remeasure plants or independently validate the selected reproductive/vegetative module; the 254 earlier separately computed single-trait reference K values and the strict 142/101 non-flora measurement-source-stage calculations were not rerun in this full matched-tip replay. Historical post-selection, source dependence, nonindependent pair/family samples and mechanistic uncertainty remain. Manuscript and coauthor review can now cite this computation reproducibility evidence without describing it as a new evolutionary conclusion.

## Interpretation and submission gates
The **completed, verified PASS** establishes numerical reproducibility **within the original AusTraits dataset**, not independent physical measurements, an evolutionary mechanism, absolute evolutionary rates, a prospective organ hypothesis, or a universal law. The independent final audit and permanent archive have both been completed successfully. Keep all K results and the original scientific claims frozen. Journal compliance, contributing-study citations, authorship, conflicts/funding and consent to submit remain separate gates.
