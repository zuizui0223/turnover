# BIODEPTH cross-site guild-composition and biomass reproducibility — prospectively scoped source-first extension v0.1

Frozen: 2026-11-15. **No BIODEPTH raw biomass effect opened before source/schema support review.** Research question selection followed existing Jena (2003) and Cedar Creek (1998) exploratory outcomes; this is explicitly a new **retrospective methodological reanalysis**, not a preregistered external confirmation of novelty.

## Purpose and sources
**Do a multi-site extension**: Is a coarse guild *count* effect robust to exact sown richness and site×year controls? Are apparent guild *identity* coefficients stable across independent experimental fields under identical support and response definitions?

Official original consortium publication Spehn et al. (2005), *Ecological Monographs*, DOI https://doi.org/10.1890/03-4101, Supplement 1 original project data Figshare DOI https://doi.org/10.6084/m9.figshare.3565170, linked from https://esajournals.onlinelibrary.wiley.com/doi/10.1890/03-4101. Original source **eight field sites / ~480 original plots / three main years**, sown richness 1–32, graminoids/grasses, nitrogen-fixing legumes and other herbs as **three**, not four, functional groups.

Second source for provenance/cross-check only: original consortium data used in Hector et al. 2010, https://esapubs.org/archive/ecol/E091/155/ . A republished value from this is **not an independent experiment** from the 2005 data. Older DOI 10.1890/03-4101 supplementary files are metadata-first preferred; alternative Figshare article APIs / ESA archive may fail separately due transport. Do not invent a qualified raw dataset from descriptions alone.

## Tier 0: no outcome opening
1. Probe the official Figshare article and collection endpoints, available file IDs, original filenames, file sizes, checksums, licenses, DOI and release/edition; original ESA archive index if Figshare fails.
2. Download only source files with a suitable original treatment-and-response table after identifying provenance. Verify cryptographic checksum and tabular schema. Before any effect, report **exact** original unique site, plot and site×plot×year counts; sowing treatment species-richness categories; planned FG count; guild presence indicators; block; observed vs sown richness; aboveground biomass units and timing. Qualify positive source support from actual files, not publication claims.
3. Primary feasibility requires **≥6 distinct authentic BIODEPTH field sites**, ≥250 source-identified unique plots, ≥2 observed years, and ≥6 sites with ≥20 original plots spanning at least two distinct guild-count treatments *within one fixed sown-richness level*. The thresholds are prospective source geometry, not p-value filters.
4. Exclude all transcribed or article-figure values unless original row keys and units are resolved. No species/functional-guild assignment from outcome-driven abundance.

## Tier 1 analysis: only if source passes
- One unique site × original experimental plot × year, *never* a species-biomass row or plot × year abundance replicate as an independent unit; preserve original repeated-measure identity.
- Response must be genuinely measured **aboveground biomass or annual production g m^-2**, labeled original source; no conversion between seasonal standing biomass and ANPP without methods. Analyze site/year in harmonized original units, separate any distinct harvest protocols.
- Contrast models on the **same eligible rows**:
  1. `log1p(biomass) ~ C(site) + C(year) + C(exact_sown_richness) + C(site):C(sown_richness) + FG_count`;
  2. replace `FG_count` by three planted guild indicators `grass+legume+forb`, **never** both count and all indicators simultaneously as they are collinear;
  3. site-specific estimands `~ C(year)+C(richness)+FG_count`, then site-split guild identity heterogeneity with uncertainty and no outcome-dependent subset selection.
- Site-blocked CV: leave an entire field *site* out; no site fixed-effect for novel site in prediction, and site-specific difference is not pooled as independent source replications of the same article. Plot-cluster bootstrap and independently estimated site-level effects, preserving nested structure. Within-richness guild-vector permutations only where original experimental assignment has actual exchangeability support; report effective number of swappable plots and how it differs by site. No p-hacking or assumed causal guild mechanisms.
- Headline should be transportability and **support-conditioned ecological heterogeneity**, not a new claim that species richness or legumes affect biomass. Original Spehn 2005 already reported such associations. Original Schmid / Hector literature already highlighted richness×functional-group design confounding.

## Hard boundaries
Jena 2003/longitudinal and Cedar E120 analyses remain prior exploratory evidence:
- Jena same-richness 62 plots count β≈+0.129 p≈0.168, identity equality p≈0.309 and only 16 source-swappable plots (eight pairs).
- Cedar 1998 E120 count β≈+0.083 p≈0.544, strong identity heterogeneity but different original 4+Woody sowing guild scheme.
- BIODEPTH three guilds differ from both; do not pretend matching guild identities or meta-pool coefficients by labels.
- Frozen original sPlotOpen×GIFT×BIEN 201-system `rho → PD–FD` main source HOLD, NEON official source authentication HOLD, and original trait-memory/organ-K manuscripts all unchanged.
