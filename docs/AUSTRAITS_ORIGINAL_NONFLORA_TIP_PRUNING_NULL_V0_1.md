# Why does same-DatasetID restriction reverse the original reproductive/vegetative Blomberg K ordering?

**14 November 2026 — original 142/101 paired-source K null test, within the same original public AusTraits v7.0.0 compilation. Original K results and focal paper hypothesis remain unchanged.**

## Completed observational evidence BEFORE this new null

The original 142 S3 / 101 native-prune fixed family×named trait pair identities have original broad/strict K rankings fully numerically reproduced from the same AusTraits v7.0.0 Parquet, native units and pinned Rcpp/phytools K. Source-only restriction changed original broader nonflora source species/tips/native geometry together:
- S3: original K reproductive-higher counts 110→121→120, 23 K sign reversals in the species/tip/tree stage and 9 in the measurement-source-only stage.
- Native prune: 82→83→81, 13 then 12 sign reversals.
- The origin of K sign flips cannot be attributed to *number of taxa* using these three historical stages alone because the strict source condition also selects taxon identities and changes native tree geometry.
- The source-only descriptive pair-K follow-up (CI #43561468098 PASS) found higher attrition and smaller baseline absolute log K margins in flipped comparisons, and a plurality of flips involved plant_height contrasts. All pair/family interpretations remain post hoc and are not statistically independent.

## New conditional, phylogeny-fixed matched-size null

[Corrected original-data R/Python 12-batch fixed-tree Rcpp K workflow](https://github.com/zuizui0223/turnover/actions/runs/43564505854). The initial run #43563549840 reached a mathematically undefined K in a random subset with zero trait variance; that run was NOT successful and is not the null result.

For every originally source-qualified family×named reproductive/vegetative trait pair, reconstruct the **original stage-1 broader nonflora source-native positive medians** directly from the SHA256-pinned public AusTraits v7.0.0 Parquet and pinned native trait unit definitions. Recompute original stage-1 Blomberg K for both organs using original V.PhyloMaker2 S3 and native prune construction and validate against the archived original pair K values and realized original tip counts before opening randomized outcomes.

The *actual survivor subset* is determined by the **historical stricter common-remaining-DatasetID positive source-median rule**, which was originally K-blind within that stage. The new null **does not regenerate a strict smaller V.PhyloMaker tree for this comparison**: instead it prunes the original broad native S3/prune tree to actual source survivor names and recalculates both K values from **the original broad nonflora state values**. This isolates a well-defined, same-tree taxon identity/phylogenetic covariance composition difference from simply dropping the same number of tips at random. The original stricter tree-rebuilt stage-2 K is recorded separately and **must never be equated with the broad-tree-pruned K estimate**.

The null uses **128 fixed-seed draws per original family×trait-pair native tree**, 12 source-only balanced family work-batches containing all original 24 plant families and the original 142 S3/101 prune K pair identities. For each draw, keep exactly the same number of broad-tree native tips as the actual source-qualified survivor set. All original trait states, normalized K estimator, branch lengths and topology from the broad original tree are fixed except for pruning to the subset. **When an equal-n random subset has constant values for either original organ trait, K is mathematically undefined.** The null therefore conditions on BOTH original organ K values being estimable in every relevant pair: reject that entire candidate **family-wide** random-priority draw and regenerate the family's common rank. **All rejected candidates and attempts are counted and reported**; no per-pair independent redraw is allowed, since that would artificially destroy correlations across shared trait pairs. To preserve shared original taxon structure across overlapping trait pairs in a family, each draw uses one **family-wide uniform random species priority**, and every pair within that family retains the highest-ranked required number of its own eligible broad-tree tips. Different families have separately seeded priorities. The observed total flip count is compared with the **family-correlated ensemble of 128 randomized total flip counts**, not falsely with 142 independent Bernoulli comparisons. Both original tree treatments share source phylogeny and are not independent biological replications.

Primary diagnostics per native axis:
- Original exact broad K and native tip-count parity.
- Actual source-survivor K direction on the *fixed broad tree*.
- Random same-n null K direction flip probability, original log K shift, and original broad-tree branch length/PD fraction for the actual survivor subset versus random subsets.
- Distribution of **total original matched-family pair sign inversions under family-correlated randomized removal**, compared with the original-source survivor value, with finite-draw empirical upper/lower tail probabilities. No preregistered confirmatory p-value is claimed.
- Original strict tree-rebuilt stage 2 K minus actual strict-survivor-on-broad-tree K is retained as a separate **tree reconstruction context**; because the original tree construction and original tips both changed, it cannot automatically be construed as a causal independent topological effect.

**Decision boundary:** If the fixed-tree actual survivor flip count lies near the random equal-n ensemble, source qualification may not require any special taxonomic pattern beyond attrition at the observed n for this statistic. If substantially unusual, extra structure in which taxa survive may matter; the null alone still does not identify growth form, biomass, dispersal, pollinator context or evolutionary selection as the driver. Simulation uncertainty is coarse at 128 replicates; no new original source K cohort or adaptive threshold search is allowed.

## Biological interpretation and limitations

- The original reproductive-vs-vegetative label was **post-selected after seeing K**. This additional null is retrospective and conditional on the selected historical pair set; the reported finite simulation tail is descriptive, not a clean hypothesis test of previously unobserved biological data.
- Species among pairs and trait measurements within the 24 families overlap; do not use pair n as an evolutionary replication count. The random-priority design models some shared survival correlation, not the unknown actual multi-study missingness mechanism.
- Dropping original tips changes the covariance, sample trait variance and K normalization. Difference between original stage 1 and original stage 2 also includes V.PhyloMaker's new scenario construction; the new null deliberately keeps original stage 1 tree geometry.
- The original raw species names, trait medians, original observation IDs and datasets are **runner-local**. Only derived source-only pair K null summaries and SHA256 verification outputs may be archived.
- A negative or positive result does not determine reproductive allocation, total biomass, body size, OU selection parameters or universal plant evolutionary memory.

## Next biological extension (separate from this source-only K null)

[Original public GIFT 3.1 exact-name and woodiness/height coverage #43562257361 PASS](https://github.com/zuizui0223/turnover/actions/runs/43562257361) had 13,848/15,305 (90.5%) names matched in original 254 species, 12,384/13,436 (92.2%) in original 760, 3,409/3,625 (94.0%) in strict 142. The conditional null should first identify whether actually retained species are unusual relative to equal-n random pruning. Only then link *original species identity* to woodiness, growth form, height, branch/genus placement or independently measured biomass, under source overlap and rights checks. GIFT height and single-seed dry mass are **not** whole plant biomass or reproductive biomass allocation. TRY v7 row retrieval/independent-study claims require actual applicable access, permission, provenance and citation checks; no restricted TRY source rows were used here.

**Current execution status is to be read from GitHub Actions, not inferred from a launched workflow.** A separate archive workflow is staged, but may only be triggered if all original 12 K-null batches and final 142/101 aggregate finish PASS. Draft PR #38 remains unmerged and not submitted.
