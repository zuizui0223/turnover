# NEON multi-site measured biomass + species cover | independent source preflight v0.1
Frozen 2026-11-14. **No new biomass–FD estimate**; this is separate from the Jena single-site completed pilot and the closed sPlotOpen–GIFT–BIEN 201-system programme.

## Source definitions and audited public facts
- Biomass: NEON [DP1.10023.001](https://data.neonscience.org/data-products/DP1.10023.001/RELEASE-2026), RELEASE-2026, DOI https://doi.org/10.48443/72bn-6r43. Lab-oven-dried **herbaceous clip harvest by functional group** from 0.1×2m strips, targeted in plots/subplots. The NEON product currently reports data from 47 NEON terrestrial sites. This is **not species-specific biomass**, not total woody biomass and not area-normalized without actual strip metadata.
- Species composition: NEON [DP1.10058.001](https://data.neonscience.org/data-products/DP1.10058.001/RELEASE-2026), RELEASE-2026, DOI https://doi.org/10.48443/9g4s-hq52. Percentage cover recorded by species in nested **six 1m² subplots within a 400m² plot**. This is **not a measurement from the harvested strip**; only plot-level or carefully spatially aggregated relationships may be inferred. Species composition also documented at larger scales by presence only. Cover sampling suspended in 2026.
- Fixed data source: official NEON public API product metadata `GET https://data.neonscience.org/api/v0/products/DP1.10023.001?release=RELEASE-2026` and comparable `DP1.10058.001`, not the rolling provisional latest snapshots. Pin response SHA256 and site/month coverage. Do not confuse product availability with matched actual plot records or valid biological measurements.

## Pre-outcome Tier 0 (current)
Retrieve both product metadata and intersect site×YYYY-MM available-month cells in RELEASE-2026 only, without opening site biomass or species-cover rows. Requirement: ≥12 distinct matching sites, ≥4 NEON ecoregion domains and ≥24 site-month cells (same month), with both product metadata retaining correct quality-controlled source names. Failure is HOLD, not a biological null.

## Tier 1 (mandatory if Tier 0 passes; not yet executed)
On explicitly overlapping site-month files, identify exact `plotID` and if possible `subplotID`, harmonize pre-2024 renamed subplot identifiers, then allow biomass dry mass per **actual sampled clip area** and coverage of species in the larger matched plot. Require ≥12 source sites, ≥4 domains, ≥100 matched unique plot×event cells, ≥5 sampled plots/site where this is feasible, date differences ≤30 days **for observed sample dates**, valid event timing and same release, missing denominator audit. Exclude disturbed/grazed plots unless exclosure correction and site management is documented. Repeated years and clips are not independent plots or sites. Species name harmonization, trait source independence, and native phylogenetic tips must be checked before Rao FD or phyloMPD.

## Analytical question, only after data source gates
Does independently measured plot-level plant trait FD improve hold-out-**site** predictive accuracy for measured harvested herbaceous dry biomass, after plot area, observed species cover, species richness, measured phenology/campaign, site and ecoregion context? Do not use harvested biomass to derive predictor weights and avoid the same year as a source of both a postharvest realized community state and original pre-sowing trait definition. Site-blocked cross-validation and comparison to richness-only baseline are mandatory. Biomass is the response **after dry-mass/area QA**, not annual NPP.

## Hard scientific boundaries
- The original 201-system BIEN temporal-memory rho and sPlotOpen×GIFT primary PD–FD route remain HOLD. Neither NEON nor Jena can be introduced as a post-result 'rescue' of their pre-fixed source family.
- **External** NEON ecosystem sites are an actual new spatial population compared with **single** Jena site, but both products within NEON are NOT two independent biological sources.
- Current macro Jena 2003 sentinel is positive for May FG richness but null for August, and predictive gain only +0.8%; no cross-site effect established.
- NEON historic Cover substrate is species-per-1m², harvest is groups-per-0.2m² strip. Plot-level co-location is necessary but not sufficient to infer small-area direct causality.
- Site-matched data must contain actual **trait FD** to be a biological follow-up; not just availability of both products.

## Tier 1 access diagnosis — 2026-11-14

- Eight predeclared unauthenticated `/api/v0/data/{product}/{site}/{YYYY-MM}?release=RELEASE-2026` probes returned HTTP 403 [run #43577609259](https://github.com/zuizui0223/turnover/actions/runs/43577609259). This does **not** mean no plot data exist.
- Official [NEON-utilities-python `auth_check`](https://github.com/NEONScience/NEON-utilities-python/blob/main/src/neonutilities/helper_mods/api_helpers.py) explicitly states that an API token has been required for data download **since June 2026**. The official request header is `X-API-TOKEN`. Catalog product and site metadata endpoints are separately accessible without it.
- An optional **manual-only** workflow is now ready at `.github/workflows/neon-authorized-source-manifest-v0-1.yml`. It reads `secrets.NEON_API_TOKEN` from GitHub Actions Secrets, checks four fixed cross-domain source file lists, never prints the token/temporary download URLs, and does not open measured records.
- Do not hard-code a token in workflow, Git branch, chat, issue, logs or artifact. No credential is available to this session; the full Tier 1 sample crosswalk therefore stays AUTH HOLD. If the user configures a NEON account token as a GitHub repository Actions secret and explicitly runs the manual action, only authorized source metadata are opened. Only then can a separate plot/date crosswalk begin, retaining the ≥12-site/4-domain/100-plot-cell/≤30-day gates and NEON 2026 release pin.
