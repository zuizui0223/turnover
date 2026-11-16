# Independent field-observed plant traits × biomass: source-first screening, 2026-11-16

**New source programme, separate from the closed BIODEPTH retrospective sequence (Draft PRs #46–53).** No original BIODEPTH result, AusTraits K effect, or BIEN family-rho is modified or transported in this gate.

## Scientific question and grain

Can *new independent field data* provide co-located, source-measured species-level plant traits, real plot-level aboveground biomass/biomass-derived carbon, and a correctly identified plant-community composition from which a phylogeny can later be built? The eventual study would distinguish (1) genuine community trait dissimilarity, (2) tree phylogenetic breadth and (3) external family-specific phylogenetic trait memory **without assuming any are interchangeable**.

The first qualifying unit is unique original **source PROJECT × PLOT_ID**, with repeat years explicitly accounted for; a leaf sample is not an independent plot. Traits must have original individual/tree measurements with original taxon and date; biomass must be an independent measured/model-derived source response (not same-year species biomass used as predictor). No new ecological regression or selection of traits by outcome permitted at source-gate stage.

## Candidate A (primary): NASA ORNL DAAC / NACP TERRA-PNW (doi:10.3334/ORNLDAAC/1292)

- Official original data: plant leaf-trait measurements (`NACP_TERRA_PNW_leaf_trait.csv`) including `PROJECT,PLOT_ID,YEAR,GENUS,SPECIES,SLA_HSA,LEAF_NITROGEN`; biomass/productivity (`NACP_TERRA_PNW_biomass_productivity.csv`) including `PROJECT,PLOT_ID,YEAR,AG_BIOMASS_TREE_TOTAL_AS_CARBON`, `AG_PROD_TREE_TOTAL_AS_CARBON`; optional soil file. Original paper describes 1,296 individual trait records and 266 stand-biomass records, six underlying projects, 35 species, and explicit `PLOT_ID` join.
- These published row counts are **catalogue expectations only**, not verified file results. Do not infer 1,296 independent plots or 266 co-located complete trait–biomass cases.
- Strict source preflight, *before any numerical mass or FD outcome*: publicly accessible original CSV files (or official, credentialed data later, not scraped); bytes fingerprinted SHA256; each file includes advertised original fields and valid key. Sentinel `-9999` is missing, not zero.
- Determine **exact** `PROJECT×PLOT_ID` matches and optional `PLOT_ID_ALT` resample identities; no fuzzy coordinate matching or cross-project accidental plot collisions. Trait–biomass temporal difference ≤2 calendar years (report 0/1/2 separately); if longer, no matched analysis.
- Admission for a *separate subsequently frozen regional ecological test*: ≥40 distinct original project×plot identities containing at least two distinct measured original species with finite positive `SLA_HSA` or `LEAF_NITROGEN`, valid matched total-tree aboveground carbon, and ≥3 source projects/ecoregions represented with ≥8 matched plots apiece. No automatic gap filling from TRY. Need quantify independent sites vs ecoregions; six project labels are NOT necessarily six independent sites.
- The annual tree biomass field is estimated/derived standing woody+foliage carbon, **not harvested plant dry mass or annual NPP**. Distinguish `AG_BIOMASS_TREE_TOTAL_AS_CARBON` (g C m−2) from `AG_PROD_TREE_TOTAL_AS_CARBON` (g C m−2 yr−1); never pool them or convert to g dry mass without fixed carbon fraction evidence.
- Caveat: original composition may include only **four listed overstory taxa** by basal fraction and may not represent all taxa with locally measured leaves. Taxon/guild conversion requires a separate source-verified species-abbreviation crosswalk; direct plot-level within-measured-taxa FD is only a partially sampled community unless representativeness demonstrated. Without original directly matching sample IDs, SOURCE_HOLD, do not use species-level trait statistics as whole-stand community FD.
- Official ORNL DAAC/NASA Earthdata may require authentication for downloading original files even when descriptive metadata are public. Discover only through **official NASA CMR metadata** and original file endpoints; do not invent signed URLs, bypass restrictions or ask a token in chat. Report `AUTH_HOLD` with HTTP status if needed.

## Candidate B (independent secondary): 2026 Dryad Myers et al. (doi:10.5061/dryad.kprr4xh8v)

- Public metadata: 304 Massachusetts Continuous Forest Inventory plots, 626 unique plot×inventory-year records across seven state forests; local original measurements of 142 individual trees in **26** of those plots (`trait_obs.csv`), covering SLA, wood density, leaf N/P, leaf C:N. Biomass is modelled using species-specific Jenkins allometry (`CFI_AGB_covars_092026.csv`); species abundances as relative basal area by species in `cfi_ba.csv`.
- At most 26 original plots can support **locally observed** trait predictors. Do **not** treat all 304 inventory plots as locally measured traits. `TRY_means.csv` are compiled database means, not independent primary measurements and do not rescue the local original traits gate.
- Read via published Dryad REST API `/api/v2/datasets/{encoded DOI}`, follow advertised version/file metadata IDs, and fetch only source `trait_obs.csv`, `cfi_ba.csv` and `CFI_AGB_covars_092026.csv` with recorded checksums. Do not load 1.22 GB CV.zip or 78 MB FinalModel.zip.
- Qualification gate: ≥15 distinct original `PLOT` keys among local `trait_obs` and original `CFI_AGB_covars`; for ≥15 plots, ≥2 *distinct locally measured species* whose exact species common-name labels can be matched to *positive* original `cfi_ba` species columns (no fuzzy name heuristics), and nonnegative valid original plot-year `agb.plot` or `agb.ha`. At least 3 distinct original state forests must have ≥3 such plots. If authors provide unambiguous taxon mapping but not in CSV, status `TAXON_CROSSWALK_HOLD` rather than invent a taxonomic alias.
- The plot-level allometrically derived biomass response is **mt acre−1** (`agb.plot`) or **mt hectare−1** (`agb.ha`), distinct from NASA gC m−2, and repeated inventory years (2000–2021) are not independent sites.
- Original 142 individual-tree measurements are real local field traits but only a 26-plot subsample; further trait-to-community completeness is a separate future source gate.

## Not acceptable as the same target by default

- 2025 TreeDivNet Dryad Jensen (10.5061/dryad.dz08kps9x): 21 experimental sites / 1,609 plots, species wood density and leaf N but outcome is **annual basal area increment** (m² ha−1 yr−1), **not** biomass stock. May be worthwhile as a separate independent *growth* study, but not same biomass target.
- 2026 Andraczek Zenodo main grassland `10.5281/zenodo.20044909`: embargoed until 2026-12-31. Public NutNet derived CWM subset is already aggregated (not original independent species-level measurements); no new K/FD inference from those derived CWM alone.
- NEON RELEASE-2026 DP1.10023.001 × DP1.10058.001 remains `AUTH_HOLD` under official token requirement since 2026-06-30; original historical 201-system BIEN/sPlotOpen family×trait gate remains terminal `HOLD`.
- Historical BIODEPTH 2005/2010 publications are **one experiment set**, not an independent replication.

## Operational source-only decision, no effect access

1. Check official source metadata identity and external file accessibility with bounded size and response status (no credential logging), and store DOI, version, SHA256/file IDs.
2. If data can be downloaded, compute **source-only** column/ID/overlap/measurement-coverage counts and source-stratum composition; the mass/AGB response may only be tested for numeric presence and unit, not used for statistical association, filtering based on response magnitude or label selection.
3. Declare each candidate `SOURCE_GATE_PASS`, `AUTH_HOLD`, `DATA_ACCESS_HOLD`, `TAXON_CROSSWALK_HOLD`, `INSUFFICIENT_SUPPORT_HOLD` or `METADATA_ONLY` without changing thresholds by observed effects. Do not blindly merge unrelated forests or measurement scales.
4. If a candidate PASSes, create another **pre-effect frozen** model with original field-site heldouts (never plot-year split), composition/coverage guards and separate response options. The **≥12 families × ≥20 native species** original trait-K architecture remains unavailable on either single study; do not conflate any site/plot source-check PASS with general family-K inference.

Output only lightweight source audit JSON and DOI/reproducible scripts. Do not commit original rows, live Earthdata tokens or unexpired signed links.
