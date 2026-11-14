# Why original AusTraits reproductive-versus-vegetative K changes after species restriction

**14 November 2026. Exploratory original-data follow-up only; do not alter frozen paper K effects or claim independent GIFT/TRY validation.**

## 1. Empirically reproducible commonalities of the 142/101 original K reversals

The frozen original 283 broader nonflora and 142 common-remaining-DatasetID pair-level K results have been individually rebuilt from the same byte-verified public AusTraits v7.0.0 source (28 original R K batches, full original 5,000-family bootstrap). The new *descriptive* pair-identity audit [CI #43561468098 PASS](https://github.com/zuizui0223/turnover/actions/runs/43561468098) uses no new biological measurements, K models or source selection. Its SHA256-verified result is in results/austraits_organ_paper_nonflora_flip_commonalities_v0_1/.

| Original same pair IDs | S3 | Native prune |
| --- | ---: | ---: |
| Strict pair IDs with valid original K | 142 (24 families) | 101 (18 families) |
| Stage 1→2 sign changes when eligible species and native K tree change together | 23 | 13 |
| Stage 2→3 sign changes when only source measurements change on exactly the same tips/tree | 9 | 12 |
| Families containing at least one stage 1→2 sign change | 10 | 5 |
| Median fraction of broad-stage species retained in stage 1→2 *flipped pairs* | 0.800 | 0.326 |
| Median retained fraction in original non-flipping pairs | 0.900 | 0.907 |
| Original pre-restriction median absolute reproductive-minus-vegetative log K for flipped pairs | 0.299 | 0.228 |
| Same baseline margin for non-flipped original pairs | 0.699 | 0.692 |
| Stage 1→2 reversed comparisons involving plant_height | 13 of 23 flips (57 available height comparisons) | 7 of 13 flips (42 available height comparisons) |

These comparisons show **retained species fraction, initial K decision margin and some family/vegetative-trait contexts** are associated with original reversal occurrence. They do NOT show that small n, basal lineage loss, woody versus herbaceous sampling, biomass investment or evolutionary selection caused it. A small original difference is mathematically easier to push across zero, so baseline-margin association is partly expected by thresholding. A change in species composition changes BOTH the measured trait pattern and the covariance/normalization of Blomberg K on the reconstructed tree; pure specimen-number attrition has not been isolated.

Family clustering is substantial: S3 taxon/tree flips include Fabaceae (5), Proteaceae (4), Celastraceae (3), Elaeocarpaceae (3), with others spread over six families. Prune flips include Poaceae (4), Proteaceae (4), Fabaceae (3), Elaeocarpaceae (1) and Solanaceae (1). The two original phylogenies and repeated pairs within the same families are NOT independent biological replications. Original complete sign sequences remain **110→121→120 on S3**, **82→83→81 on native prune**, based on identical original pair IDs.

Across the **101 original pair identities valid in both S3 and native-prune**, 13 S3 and 13 prune comparisons reversed their organ-K rank during the taxon/tree stage, and **8 of those comparisons reversed under BOTH tree treatments**. These eight same-pair common changes occurred in Proteaceae (4), Fabaceae (2), Poaceae (1), and Elaeocarpaceae (1), and five involved plant_height as the vegetative comparator. The trees share original underlying phylogenetic information, so this is not eight independent evolutionary validations. It is an exact paired-axis descriptive reproducibility feature.

**Mechanistic follow-up after completed equal-n null:** The broad native tree and source-state fixed, matched-n family-correlated random survival test above has now passed. Unresolved tests are genus/branch placement and joint life-history/missingness stratification; the current same-data randomized result remains retrospective and no mechanism or biomass-causal result has been established.

## Completed equal-n random tip-pruning and family robustness result (14 November 2026)

[Fixed source-native tree null #43564505854 PASS](https://github.com/zuizui0223/turnover/actions/runs/43564505854) re-fit only the **already fixed original K estimand under conditional randomization** (not a new independent biological dataset). On the **same original broad phylogeny and broad nonflora trait values**, the actual strict-source survivors and 128 equal-n family-wide randomized survivor priority draws gave:

- **S3, 142 pairs:** 23 actual original strict-survivor sign flips vs 14.82 mean in 128 family-correlated random draws; empirical one-sided upper-tail proportion **0.0310**.
- **Native prune, 101 pairs:** 13 actual flips vs 11.23 expected at random; upper-tail **0.3566**.
- Every actual strict-survivor sign decision on the original BROAD tree agreed with the corresponding *rebuilt* strict native K tree sign in the original 142/101 pair cohort. The numeric K magnitudes/PD need not be identical.
- [Permanent null archive #43565522112 PASS](https://github.com/zuizui0223/turnover/actions/runs/43565522112) contains 128-draw results and SHA256 proof. Four of 3,076 candidate whole-family random-rank draws were rejected because K is undefined on constant-trait subsets; the published null conditions on K being estimable.

[Original K-family deletion and phylogenetic diversity audit #43565935858 PASS](https://github.com/zuizui0223/turnover/actions/runs/43565935858) reused the EXACT original 128 draws, without changing species/tip K values or estimating a new biological effect. In S3 the descriptive upper-tail probability remains ≤0.05 after 21/24 single-family omissions, but removing **Fabaceae gives 0.1163**, Elaeocarpaceae 0.0698 and Celastraceae 0.0620. Native prune has **0/18** omissions with an upper-tail ≤0.05. Actual strict survivors had *less retained native branch-length/PD than the same-n random 2.5th percentile* in **36 S3** and **21 prune** pair contexts, but only **6/23 S3 flips** and **5/13 prune flips** coincided with those unusually low-PD cases.

**Interpretation:** Under this specific conditional fixed-tree same-n null, S3 source-selected species composition sometimes carries more K sign-change information than random taxon number loss. This is not a cross-tree-universal, family-independent or preregistered finding; shared source/publication structure, trait state variance and tree geometry may still be involved. Retained phylogenetic PD does not by itself explain which original pairs reverse. Further mechanism claims, especially about reproductive allocation or biomass, require independent measurements of appropriate quantities or targeted source-/lineage-controlled tests.

## Extra source-tree mechanism audit: exact strict original tree parity and size context

[Original 142/101 tree-reconstitution/size/PD audit #43566078839 PASS](https://github.com/zuizui0223/turnover/actions/runs/43566078839) confirmed that after strictly retaining original actual taxa, the historical narrow V.PhyloMaker2 K and the original broad tree pruned to those exact tips gave **zero mismatched reproductive-vs-vegetative K directions** (142 S3 and 101 prune), with maximum absolute log-K contrast difference 4.02×10⁻⁹ S3 and 5.00×10⁻¹⁶ prune. In this original source stage, **extra native tree re-insertion/rebuilding differences are negligible beyond the change of tip identities and their retained covariance**, rather than an alternative mechanism for the 23/13 K sign flips. Native tree pruning itself DOES change branch covariance, normalization and trait variation.

In S3, the plant-height comparison subset gave **13 actual** vs **6.421875 random-expected** flips (57 original pairs). Other vegetative traits: 10 actual vs 8.398438 expected (85 pairs). In prune, height 7 actual vs 3.726563 expected (42 original pairs); others 6 actual vs 7.507813 (59 pairs). These uncorrected exploratory group summaries make a **size/stature sampling-bias hypothesis plausible**, not proven. GIFT woodiness and height coverage can establish population composition but not individual biomass or reproductive allocation, and the two trees and trait pair rows are dependent.

The original strict subsets had unusually low retained phylogenetic branch length below the random 2.5th percentile in **36/142 S3 and 21/101 prune** pair contexts; **only 6/23 S3 and 5/13 prune actual K rank flips** occurred in those unusually low-PD contexts. Thus systematic source/phylogenetic clustering is present, but it is insufficient by itself to claim that PD loss *causes* K reversals. Original family sensitivity also matters: excluding Fabaceae yields exploratory S3 upper-tail 0.1163 despite original full-cohort 0.0310.

[Verified native-tree parity and context summary](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_tip_loss_null_context_v0_1).

## After conditioning on observed GENUS loss, the original excess K-flip signal disappears

The [full original 142/101 genus-stratified same-n K-null source-matrix plus independently corrected audit #43567784678 PASS](https://github.com/zuizui0223/turnover/actions/runs/43567784678) explicitly preserves the original stricter-source number of surviving native tips in **each original genus** while selecting random available species within those genera on the exact same original broad S3/prune tree and unchanged K trait values. Every one of the 12 original R matrix jobs succeeded; a separate SHA-type error in the original final reporting was fixed through independent reaggregation and permanent archiving, not falsely represented as overall original run success.

| Axis | Actual stricter-source K flips | Random same TOTAL native-tip n only, mean | Random same **genus-specific native-tip counts**, mean | Genus-conditioned finite null upper-tail |
| --- | ---: | ---: | ---: | ---: |
| S3 | 23 | 14.8203 | **23.5703** | **0.6047** |
| Native prune | 13 | 11.2344 | **13.2188** | **0.6822** |

Across S3 142 and native prune 101 original pair identities, the actual source-surviving *total rank-flip count* is unexceptional once the **which-genera-and-how-many-tips-from-each-genus** selection is fixed. This is a stronger commonality than simply noting lost species or phylogenetic PD: the source-restricted observational sample is highly structured in terms of lineage identities. Yet a conditioned genus quota null neither proves that genera *causally* determine K nor identifies any unique physiological trait, pollinator, growth form, whole-plant biomass or reproductive investment mechanism. Original organ grouping and the new null remain exploratory/post-selected, two native trees and dependent pairs are not independent confirmations, and the source compilation is the same.

**Direct validation of what was actually lost:** [AusTraits v7 original genus attrition source audit #43568302693 PASS](https://github.com/zuizui0223/turnover/actions/runs/43568302693) reconstructed the original 142/101 pair-specific species and genus identity *ephemerally* and committed only genus counts. In K-reversed original pairs, median whole genera lost was **4 in S3 (vs 2 for stable pairs)** and **19 in prune (vs 1.5)**. The retained genus fraction median was **0.786 vs 0.846** in S3 and **0.553 vs 0.877** in prune. **Every one of the 23 S3 and 13 prune flipped pairs had at least one entirely lost genus**, but so did **98/119 stable S3** and **70/88 stable prune** pair comparisons: wholesale genus attrition is common and not sufficient on its own to force a K rank reversal. Among K-flipping S3 pairs, median **63.3% of the species removed** belonged to completely absent genera, versus **33.3% among stable pairs**. The remaining source-qualified genus identities, positions and original organ states — not just a binary loss flag — must be part of the analysis context. This is the **same original AusTraits compilation**, still no direct biomass allocation or external biological replication.

[Full source-checked genus-quota conditional design/results](https://github.com/zuizui0223/turnover/blob/paper/austraits-organ-ecology-v0-2/docs/AUSTRAITS_ORIGINAL_GENUS_CONDITIONED_NULL_V0_1.md). [SHA256-fixed derived null data](https://github.com/zuizui0223/turnover/tree/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_public_v7_genus_quota_tip_loss_null_v0_1).

### Plant stature is a prominent sampling-sensitive comparison, not measured biomass

The [original full fixed-tree/native tip K parity and plant_height audit #43566078839 PASS](https://github.com/zuizui0223/turnover/actions/runs/43566078839) compared the *same fixed original 128 family-correlated random pruning draws* against the actual strict-source survivor subsets and separated the vegetative comparator being plant_height from other vegetative dimensions:

| Original axis | Plant-height compared pairs | Actual height-pair K flips | Matched-n random mean height flips | Other vegetative pairs: actual vs matched-n random mean |
| --- | ---: | ---: | ---: | ---: |
| S3 | 57 | 13 | 6.4219 | 10/85 vs 8.3984 |
| Native prune | 42 | 7 | 3.7266 | 6/59 vs 7.5078 |

Most of the original S3 observed-minus-matched-n-random flip excess is associated with the *plant_height* comparator (**13−6.4219 ≈ +6.58 of total 23−14.8203 ≈ +8.18**). These comparisons are original family×trait-pair rows with overlapping species/families, not independent tests. The comparison was defined after the original reproductive K pattern was observed; do not treat it as a predeclared subgroup-effect p-value.

This **supports prioritizing plant stature, growth form, lineage composition and source-specific height measurement availability** as explanatory contexts. Height is a coarse size proxy; it does NOT quantify whole-plant dry biomass, leaf/stem/root allocation or reproductive carbon allocation. A direct biomass mechanism remains unverified. The source audit found 3,015/3,625 exact strict species with GIFT woodiness metadata and 2,363/3,625 with GIFT maximum height, but these data have not independently validated a biomass mechanism.

## 2. Where whole-plant biomass enters (and where it does NOT)

The original 12 named organ traits are length, area, leaf mass/area, height, fruit/seed dimensions and **seed_dry_mass**. None is a complete measured aboveground biomass, belowground biomass, individual reproductive biomass or allocation-rate dataset. **Plant height is a size proxy, not total biomass**. **Mass of one seed is not total reproductive allocation** without seed production and other reproductive tissue mass.

A plausible *size/life-history mixture* hypothesis is that the species dropped by same-DatasetID measurement matching are unevenly distributed across woody/perennial and herb/annual lineages and across the stature/seed mass allometric spectrum. This can alter K ranking via phylogenetic covariance and within-family variance, particularly where height is the vegetative comparator. It cannot be defended as a selection/constraint mechanism without explicit lost-species classification and controlled tip-loss nulls.

Useful distinct ecological quantities:
- **Trait size spectrum:** adult height, woodiness, life span, leaf area and seed/diaspore mass. These are not measured whole-plant biomass.
- **Biomass distribution:** live leaf, stem and root dry mass, leaf mass fraction (LMF), root mass fraction (RMF), root:shoot mass ratio (R:S), total aboveground/belowground plant biomass. An individual allometric model also needs growth form, age/stage, DBH or basal diameter and wood/stem density (often site/light and calibration), not just species height.
- **Reproductive allocation:** individual reproductive biomass fraction or total seed output times mass per seed PLUS other reproductive tissues, for a comparable time interval and phenological stage. Realized organ biomass fraction is not identical to dynamic carbon allocation flux.

An informative analysis would compare original K reversals across retained/lost woody:herb proportion **after accounting for baseline K decision margin and family**. Direct biomass hypotheses must be separately tested on genuinely observed compatible whole-plant biomass/seed-output records, not inferred from single-seed mass.

Background: Díaz et al. (2016, 2022) global plant form and function size/economic axes; Poorter et al. (2015, New Phytologist, doi:10.1111/nph.13571) plant biomass allometry and ontogeny. The former 6-trait spectrum is partly TRY-derived and is NOT automatically an independent source from original AusTraits.

## 3. Explicit GIFT 3.1 and TRY 7 cross-database plan

### GIFT (public, versioned, testable without member account)

GIFT 3.1 provides a public versioned API (https://gift.uni-goettingen.de/api/extended/index3.1.php) and species-level standard work_ID/work_species taxonomy (GIFT_species); GIFT_traits_meta and GIFT_traits provide source-aggregated traits. [Original public API smoke test #43561499645 PASSED](https://github.com/zuizui0223/turnover/actions/runs/43561499645): GIFT species paging, names_matched_unique lookup, trait metadata (109 entries) and un-biased growth-form query returned valid 200/JSON.

Frozen trait IDs from its documented metadata: **1.1.1 woodiness**, **1.2.1 growth form**, **1.6.2 plant maximum height**. The versioned GIFT API is accessible, and the [complete source-eligible 254/760/142 exact accepted-name and trait linkage audit #43562257361 PASSED](https://github.com/zuizui0223/turnover/actions/runs/43562257361), using the original public AusTraits v7.0.0 Parquet byte SHA256 and unchanged fixed source species cohorts. The verified original-source-only aggregate report is permanently saved under results/austraits_organ_paper_gift_original_K_linkage_v0_1/gift_exact_name_growthform_linkage_verdict.json.

| Original fixed AusTraits K source cohort | Unique original species | Exact accepted GIFT 3.1 name matches | Match % | GIFT woodiness available | GIFT growth form available | GIFT maximum plant height available |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 254 original single-K systems | 15,305 | 13,848 | 90.5% | 11,921 | 11,407 | 9,983 |
| 760 original common-tip K pairs | 13,436 | 12,384 | 92.2% | 10,639 | 10,125 | 8,833 |
| Strict 142 original same-DatasetID pairs | 3,625 | 3,409 | 94.0% | 3,015 | 2,743 | 2,363 |

All traits were retrieved from the version-pinned public GIFT API with biased/derived-only source options excluded; taxonomy was matched on exact canonical species binomials, with **no synonym/resolution adjustments**. This is **real species-name and trait-coverage feasibility**, not validation of external primary measurements or of the original reproductive-K pattern.

Exploratory pair-level woodiness context gave **no simple consistent woody-versus-herbaceous contrast that already explains the 23/13 original K reversals**: among S3 flipped comparisons, the median GIFT-woodiness-classified woody share was 1.00 in retained species and 0.939 in excluded species; among non-flipped comparisons it was 0.964 and 0.929. On native prune the flipped medians were 0.972 and 0.927 versus non-flipped 0.982 and 1.00, respectively. These are highly woody-dominated original measurement pools and correlated pair-level observations, not statistically independent proportions or a causal environmental model. The original K values were **not** refitted with GIFT trait values.

Species join should use exact accepted binomial matches first, then one-to-one audited synonym mapping based on GIFT_species_lookup() and the original AusTraits taxonomy; require correct genus/family, avoid ambiguous duplicates and retain unmatched taxa as missing rather than dropping them silently. GIFT trait aggregation can combine multiple references and inferred/bias-prone resources; requests should exclude biased-reference/derived-only records where possible and audit GIFT trait reference/source overlap with AusTraits. A GIFT species occurrence on an island is not proof of the original AusTraits measurement's island site.

### TRY v7 (requires user/PI request and source licensing)

Official current TRY v7 (released **4 September 2026**) contains about **22.86 million records**, covering **306,701 taxa**. The official request workflow (https://www.try-db.org/TryWeb/Prop0.php) requires member registration, acceptance of intellectual property guidelines, selected traits/species and PI acknowledgement; open data generally come under CC BY but source-restricted rows still require authorization. No user TRY account was accessed and no controlled/privately released raw trait data were downloaded.

If the user or authors acquire an approved TRY export, the schema should preserve **AccSpeciesID / AccSpeciesName**, the original names, **TraitID**, **DatasetID**, **ObservationID**, **StdValue/UnitName**, **Reference** and permission flags; accepted name harmonization must be documented. Align plant height/woodiness/leaf mass/area/seed mass to original definitions only after unit and organ ontology checks. Separately test aboveground, leaf/stem/root biomass and seed output where actually available, but expect much sparser coverage than universal height/leaf traits.

**Independence audit:** Original AusTraits, GIFT and TRY may reuse the same field studies, literature measurements, resources and taxonomic harmonization. A joined row with a new database ID is not external replication. Require original contributing-publication DOIs, specimen IDs/record fingerprints and source-license compatibility before declaring source independence; rerun original K only as a separately labelled future extension if sufficient genuinely independent primary source records exist.

## 4. Analysis gates

1. **Already passed:** 254/760/283/142 original public-v7 K numeric replay, and original 142/101 descriptive sign-flip group comparison; only original data.
2. **Public GIFT linkage verified:** the exact original 15,305/13,436/3,625 species K populations are now joined to stable GIFT 3.1 public accepted names, with 90.5/92.2/94.0% exact match and 3,015 strict species having woodiness. No K refit, no source independence and no measured biomass output. Missing GIFT names remain missing; no hidden complete-case K reselection.
3. **Equal-n AND observed-genus-quota randomization completed:** In S3, the original 23 actual flips exceed unrestricted equal-n mean 14.82 (finite upper-tail 0.0310) but agree with genus-quota mean 23.57 (upper-tail 0.6047); prune 13 actual vs unrestricted 11.23 and genus quota 13.22 (tails 0.3566 and 0.6822). This supports prioritizing which genera are systematically retained under original DatasetID availability. Direct branch/genus-specific source mechanism, independent data, biomass allocation, and prospective confirmation remain incomplete.
4. **TRY-based direct biomass analysis remains external-input-dependent:** user account/IPG, correct source references, actual biomass and seed-production coverage and non-overlap constraints.
5. **Original article inference must remain unchanged:** same compilation, retrospective organ grouping, dependent pairs/families and two non-independent trees. PR #38 stays Draft, unmerged and unsubmitted.

This note is an exploratory hypothesis and test protocol. It is not a new core paper result or a journal-ready independent mechanistic confirmation.
