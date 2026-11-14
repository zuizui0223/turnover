# Why does same-DatasetID restriction reverse the original reproductive/vegetative Blomberg K ordering?

**14 November 2026 — all 12 original matched-tip K-null batches, independent 142/101 reaggregation, permanent SHA256 archive and whole-family sensitivity audit completed. Exploratory result within the SAME AusTraits v7; original core paper K results unchanged.**

## Verified fixed-tree equal-n null result and family sensitivity (14 November 2026)

[Corrected full 12-batch R/native K null #43564505854 PASS](https://github.com/zuizui0223/turnover/actions/runs/43564505854) and [independent archival #43565522112 PASS](https://github.com/zuizui0223/turnover/actions/runs/43565522112) reproduced all **142 S3 and 101 prune** original source-selected K pairs, original native tree/tip values and 128 seeded same-n family-correlated random-priority draws. Original source broad-to-strict pair K sign reversals remained **23 S3 / 13 prune**; the *actual strict survivor subsets on the FIXED original broad trees* also reversed the exact same 23/13 original pair identities. **All 142/101 original pair-level K directions matched historical tree-rebuilt Stage 2.** A separately successful [original fixed-tree versus reconstructed-strict-tree K numerical parity and plant-height audit #43566078839](https://github.com/zuizui0223/turnover/actions/runs/43566078839) further confirmed the **absolute historical stage-2 rebuilt minus original-broad-tree-pruned log K contrast was ≤4.02×10⁻⁹ S3 and ≤5.0×10⁻¹⁶ prune**. Thus in this specific source/taxon geometry the original strict-tree reconstruction did not materially change the **numeric** K contrast beyond simply pruning to the same survivor tips. This exact parity is empirical for these original pairs, not a universal guarantee for phylogenetic imputation.

| Original fixed broad tree | S3 (142) | Native prune (101) |
| --- | ---: | ---: |
| Actual source-selected same-n survivor K sign reversals | **23** | **13** |
| 128 equal-n family-correlated random-draw **mean** K sign reversals | **14.8203** | **11.2344** |
| Null median reversed comparisons | 15 | 11 |
| Random-draw total count minimum–maximum | 5–25 | 4–19 |
| One-sided empirical upper-tail probability of the actual 23/13 count | **0.0310** | **0.3566** |

The 128 random family-wide priorities were conditioned on valid K for both traits: **4 of 3,076 attempted family-level random rank draws** were rejected when a random subset gave zero trait variance, and regenerated at the family level (not independently by trait pair). This conditioning prevents an undefined K from being silently recorded as a biological non-flip. These are **finite Monte Carlo descriptive tail areas**, not preregistered p-values or a new independent ecological validation. Only S3 shows unusual original source-survivor flip counts relative to this particular null; the native prune outcome is compatible with same-n random attrition. **Neither axis demonstrates a universal effect of nonrandom source loss.**

[Family-level leave-one-out and source-survivor phylogenetic diversity (PD) robustness audit #43565935858 PASS](https://github.com/zuizui0223/turnover/actions/runs/43565935858) reconstructed all original 128 shared-family null draws from the permanent SHA256 archive, adding NO new K estimates, original species, traits or nonfrozen source subsets:

- **S3:** 21/24 leave-one-family-out descriptive upper-tail probabilities remain ≤0.05. Deleting Fabaceae removes five actual flips vs 1.367 expected from matched-n random ranks and weakens the exploratory tail to **0.1163**. Removing Elaeocarpaceae or Celastraceae yields **0.0698** or **0.0620**. The S3 signal therefore involves multiple plant families but remains **sensitive to the contribution of particular taxa/families**. It is not a fully family-robust universal comparison.
- **Native prune:** none of 18 leave-one-family-out subsets has a descriptive upper-tail probability ≤0.05. Removing Poaceae, Proteaceae or Fabaceae gives 0.6047, 0.5349, or 0.5116.
- **Phylogenetic diversity:** actual source-selected subset branch-length fraction lies **below the matched-size random 2.5th percentile in 36/142 S3 and 21/101 prune original pair contexts** (above the 97.5th percentile in four/five). But only **6 of 23 S3 flips** and **5 of 13 prune flips** fall in those low-PD groups. Branch-length loss is nonrandom in many source-subsets without directly explaining K rank inversions. The pairs/families and two native trees overlap and are NOT independent phylogenetic replicates.
- In the original 142/101 cohorts, median actual survivor PD relative to random expected PD was **0.9911 S3** and **0.9837 prune**; most deviations are modest but some extreme original source filters target phylogenetically concentrated survivors.

**What has been distinguished:** Simply deleting the same number of source-eligible original tips can readily produce K flips, but the S3 source-selected survivor identities produce more flips than this conditional equal-n randomization would typically yield. This discrepancy is source-/family-/tree-context dependent. It **does not isolate which clades, woody/annual life histories, plant height/biomass, trait-state heterogeneity, source measurement error, evolutionary rates or selection** produce the outcome. Those require explicit lineage/location/life-form contrasts or prospective independent measurements. The original reproductive organ categories were chosen post hoc, and 128 simulations give limited p-value resolution.

Permanent source-only evidence and exact scripts:
- [Original 142/101 fixed-tree null SHA256 archive](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_public_v7_tip_loss_null_v0_1)
- [Original family leave-one-out/PD SHA256 audit](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_original_tip_loss_family_PD_robustness_v0_1)

## Native tree reconstruction is numerically equivalent to broad-tree pruning for the original source survivors

[Independent original K native-tree parity, PD and plant-stature audit #43566078839 PASS](https://github.com/zuizui0223/turnover/actions/runs/43566078839), committed at [original derived audit results](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_tip_loss_null_context_v0_1), checked all 142 S3 and 101 native-prune original K comparisons against the original 128-draw archive and exact source SHA256.

**A key technical identification:** On precisely the original strict-source survivor taxa, the historically regenerated narrower V.PhyloMaker2 tree K and K computed by taking the original BROAD tree then pruning it to the very same native tips are numerically equivalent, not merely directionally the same:

| Original source-native K treatment | S3 (n=142) | Native prune (n=101) |
| --- | ---: | ---: |
| Original regenerated strict tree vs original broad-tree pruned to same actual survivor tips: sign disagreements | **0** | **0** |
| Maximum absolute original reproductive-minus-vegetative log K contrast difference between those two tree procedures | **4.02 × 10⁻⁹** | **5.00 × 10⁻¹⁶** |
| Median absolute log K contrast difference | **0** | **0** |
| Original source-qualification survivors with retained branch length below random equal-n PD 2.5th percentile | **36/142** | **21/101** |
| Of the original K sign-flipping pairs, number in those low-PD subsets | **6/23** | **5/13** |

**Interpretation:** This directly removes an important ambiguity in THIS original experiment: there is no detectable *extra* K ranking change from regenerating the strict native trees beyond simply pruning the original broad native trees to the strict survivor tip set. Nonetheless, pruning any tree necessarily changes its retained lineage/branch covariance and Blomberg K normalization, so species *identity* and its phylogenetic placement cannot be separated just by showing those tree constructions agree.

Original plant_height as vegetative comparator: S3 **13 observed flips among 57 pairs** versus **6.421875 expected** across the original 128 family-correlated equal-n draws; prune **7 among 42** versus **3.7265625 expected**. Other vegetative comparison contexts: S3 **10 observed / 8.3984375 expected** (85 pairs), prune **6 observed / 7.5078125 expected** (59 pairs). These size/stature observations are post hoc, correlated and not corrected for multiple trait/family comparisons. **Plant height is not total plant biomass** and neither this audit nor GIFT/TRY linkage directly quantifies reproductive allocation.

**Subgroup interpretation is deliberately conservative:** Only 6 of the 23 S3 original flips had actual survivor PD below the pair-specific random 2.5th percentile, so low PD is a recurring feature of source restriction but cannot itself account for most of the rank inversions by a simple low-PD threshold. The original S3 whole-family LOFO upper-tail 0.1163 after dropping Fabaceae means the suggestive original full-cohort upper-tail 0.0310 is not a universal family-robust directional discovery. No independent data source or mechanistic evolutionary selection test was added.

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

**Status:** Corrected full null, independent 142/101 final aggregation, permanent archive and original-family/PD sensitivity audit are all completed PASS as linked above. The failed original run #43563549840 was superseded by corrected #43564505854 after conditional zero-variance handling. This follow-up is exploratory and does not alter the paper's original observation or authorize peer-reviewed submission. Draft PR #38 remains unmerged and unsubmitted.
