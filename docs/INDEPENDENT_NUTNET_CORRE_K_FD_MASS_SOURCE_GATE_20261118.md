# Independent grassland response and raw trait-source gate: NutNet × CoRRE, frozen 2026-11-18

**Separate original-source study.** No change to the closed generalized time/space BIEN prospective programme, no reopening original 201-family BIEN×sPlotOpen structural gate, no use of the same BIODEPTH or TreeDivNet plots already examined in Draft PRs #46–57. This gate is strictly about *source identity, granularity, taxonomy, independent K feasibility, plot biomass and provenance*, not positive effects or mechanisms.

## Data A — independent global grassland biomass/derived CWM candidate

Original [Nutrient Network subset of Andraczek et al. (2026)](https://doi.org/10.5281/zenodo.20070363), publicly archived record version [20070364](https://zenodo.org/records/20070364). Original description: untreated **NutNet control plots during pre-treatment baseline year**, standardized dry aboveground biomass (g dry weight/m²), community-weighted belowground trait means and trait coverage, where trait values come from **UNDERPLOT**, not separately field-measured species traits in each study plot. Original declared inputs `full-cover_2025-01-31.csv` and `comb-by-plot_2025-01-31.csv` from NutNet, but the aggregate public Zenodo subset is a **derived plot-level source**, not by itself a redistribution of original species-level coverage raw records.

Public file candidates on Zenodo:
- `Andraczek_et_al_Belowground_traits_and_aboveground_biomass_NutNet_subset.csv` (~560 KB)
- `Andraczek_et_al_Belowground_traits_and_aboveground_biomass_NutNet_subset_metadata.txt` (~7.3 KB).

The current full main Andraczek `10.5281/zenodo.20044909` dataset is **EMBARGOED until 2026-12-31**: never use that data or infer that the public NutNet subset also contains its underlying original individual traits.

**Source gates (prior to reading any biomass association):**
1. Open official `https://zenodo.org/api/records/20070364` and check numeric ID, Zenodo DOI, version/publish time, original file inventory, official `checksum: md5`, license and each original file byte count. Only download files advertised under the official 20070364 metadata with DOI identity. Do not invent links, scrape a different site, or access embargoed 20044909 data.
2. Original CSV version pin: size bounded <=2 MB, file bytes must hash to advertised Zenodo MD5; original metadata text file <=100 KB and checksum pinned. On any mismatch, `SOURCE_HOLD`.
3. Record original row count, original column names/types, direct unit/response convention and keys **as exposed by the original metadata**; distinguish source unique site, plot, year and any replicated plots from source plot×year duplicates. Missing source identifiers are `PLOT_GRAIN_HOLD` (do not invent a synthetic plot ID). Repeated years from one site are not independent site replicates.
4. For a *future separate global source response test*, require >=12 original independent sites, >=80 **source-identified** unique plot-year records with valid nonnegative original dry aboveground biomass, >=5 original sites each with >=5 valid unique source plots, at least one numeric continuous trait CWM with >=80% coverage. Source biomass must come from source original NutNet measurement and not be algebraically constructed from the same trait predictor.
5. **Crucial taxonomic gate**: ask whether original source rows expose a full botanical `site×plot×year×species` incidence/cover matrix or merely **CWM**, species richness or coverage. Without species rows and exact genus/species identifiers, `COMMUNITY_FD_PLOTTED_SPECIES_HOLD`, even if site/biomass/CWM qualifies. Derived CWM alone cannot reconstruct plot FD, species pool phylogenetic breadth, original family-specific K composition, nor be treated as a genus-level actual field measurement. Author-specific trait CWM predictor is not independently measured source individuals.
6. No new biomass regression, K, rho, FD or causal effect opened in this gate. Auth/HTTP/network/embargo errors reported honestly with verified source statuses. No original raw data uploaded to Git.

## Data B — CoRRE continuous trait lineage K candidate, distinct source

Original Komatsu et al. 2024 [Scientific Data DOI 10.1038/s41597-024-03637-x](https://doi.org/10.1038/s41597-024-03637-x), EDI original dataset DOI [10.6073/pasta/a33c9be2bd819d6b1a2c52663d561158](https://doi.org/10.6073/pasta/a33c9be2bd819d6b1a2c52663d561158). Original overview: **4,079 species/173 families** across 390 CoRRE and GEx experiments, 17 total categorical+continuous traits; **2,927 species and 147 families** have near-complete **imputed** eight continuous traits. The paper also identifies **observed original imputation-training trait records** (206,113 plant-individual references across 3,188 species/151 families before final imputation). These large counts are **published totals, not directly confirmed K-eligible 20-species×12-family trait subgraphs**.

**Frozen anti-circularity condition:**
- **NEVER calculate Blomberg's K or phylogenetic persistence on imputed continuous traits** where the imputation uses phylogenetic information. Doing so would induce artificial phylogenetic signal and may mechanically inflate covariance/K. Do not merge this with original BIEN/AusTraits memory estimates and call it independent: authors' original training pool includes **TRY v6, BIEN v4.2, AusTraits v4.1, TiP Leaf and Chinese Plant Trait DB**, with potentially repeated source original observation IDs.
- Locate exact EDI official package metadata (DataCite DOI metadata and EDI PASTA package), specifically the **original raw *observed imputation training data***, not the completed imputed species means. Record original license restrictions and data provenance. If inaccessible, status `ORIGINAL_TRAIT_ACCESS_HOLD`.
- For an *independent* source-family K validation in the future, require source-qualified actual per-species positive continuous trait observations for **>=20 distinct native botanical species per family for >=12 independent families** on the same named axis, original observation IDs deduplicated and original GBOTB native/prune tips verified; remove observations duplicated with previously used BIEN/AusTraits K training data by original source key, not merely species name. Those calculations are a separate future source-first frozen contract; **DO NOT** run K estimates in this metadata gate.
- Ensure the original CoRRE/GEx *site species communities* or biomass plot record could be joined by original species ID; this trait dataset alone is not source biomass. A categorical trait is not interchangeable with the continuous trait signal K.

## Primary next step / verdict

For both candidates write a **single nonraw original-source quality JSON**: source URL, record ID/DOI, checksum and size metadata, actual verified original source rows/columns and site/plot counts where accessible, independent biomass source qualification status, botanical species-level FD join status, and observed-only trait-K availability status. A source PASS for the NutNet response cannot rescue the older closed time-space BIEN, NEON or BIODEPTH gates. No new `K→FD→mass` result until both the species-level and actual original trait source gates independently pass.

Data access, measurement grain and family×trait K conditions are strict, not targets to tune until a desired significance is obtained.
