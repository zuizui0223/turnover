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

**Stronger next mechanistic audit:** Keep the broad-stage trait states and tree construction rule fixed, sample the same number of species as the actual strict-source retained subset many times *without looking at the K outcome*, and compare random matched-n changes with the actual observed K change; repeat stratified by genus/branch and quantify phylogenetic dispersion of the retained/lost lineages. Those tests have not yet been run and are post-discovery even when performed. Number of tips alone cannot be equated with lineage-specific pruning.

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
3. **Mechanism discrimination remains open:** equal-n random tip pruning, genus/branch position, original baseline log-K margin and family-block uncertainty; source and numerical artifacts do not determine a unique cause.
4. **TRY-based direct biomass analysis remains external-input-dependent:** user account/IPG, correct source references, actual biomass and seed-production coverage and non-overlap constraints.
5. **Original article inference must remain unchanged:** same compilation, retrospective organ grouping, dependent pairs/families and two non-independent trees. PR #38 stays Draft, unmerged and unsubmitted.

This note is an exploratory hypothesis and test protocol. It is not a new core paper result or a journal-ready independent mechanistic confirmation.
