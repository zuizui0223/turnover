# Independent published original forest sources: direct K→FD→biomass original-species data unavailable

**2026-11-18 verified public original source result** from [GitHub Actions #44300781971](https://github.com/zuizui0223/turnover/actions/runs/44300781971). New sources independent of historical TreeDivNet Jensen 2026 and BIODEPTH. All original source downloaded into transient runner storage, with original **MD5** validation of data files and nonraw source schema only. Full result: `results/independent_africa_befchina_original_source_grain_audit_20261118_v0_1.json`.

## Source A: African natural forests — public original Zenodo CSV original MD5 PASS

Original [Noulekoun et al. GEB 2023](https://doi.org/10.1111/geb.13800), public [Zenodo #10045492](https://zenodo.org/records/10045492) mirror of original Dryad DOI `10.5061/dryad.dfn2z3582`, release CC0. Public original file `dataall_Noulekoun_GEB.csv` **155,745 original bytes**, verified MD5 `60fc555c8e2942af432b09d3aeb84d57`. Original source variable description XLSX and author R script also downloaded with exact known MD5.

- **276 source plot rows**, **276 unique `plot_uniq_ID`**, 64 source columns and **five countries**. The *paper* reports 7,993 source trees and 207 tree species in 2014–2020 original inventories from Benin, Burkina Faso, Ghana, Togo and Ethiopia. **These individual/207 original species records are NOT in the public main CSV** and the source column inventory has **zero scientific species name/taxon columns**.
- Source does include `cwmwd`, `cwmsla`, `cwmlnc`, `cwmhm` and other community means, plus `sd_fdis`, `sd_richness`, `sd_agb.mg.ha`, climate/soil variables and site country/growth classes. The **only published plot mass response is already *standardized* AGB `sd_agb.mg.ha`**; original unstandardized AGB Mg ha−1 is **NOT** present in the public main CSV. Do not treat negative standardized response values as physically negative biomass.
- Country-by-country original FDis/standardized-mass external prediction can be a **different explicit derived-index estimand** because the source supplies five countries, but this cannot reconstruct individual primary SLA/leaf N, build trait-disparity FD from actual original species/abundances, or join family-specific K to source plot species. The original paper already reported **positive richness/CWM/structural diversity association** with AGB; do not call its source data an independent confirmatory trial of its own published ecological effect.

**Strict verdict for direct original species-trait phylogenetic K→FD→mass: `ORIGINAL_SPECIES_TRAIT_GRAIN_HOLD`.** This cannot be repaired by assuming compiled species trait values equal measured local species traits. Original five-country *derived-index* population support is being checked under a **distinct pre-outcome country-fold source contract**, not by silently reopening this direct K bridge.

## Source B: BEF-China planted forest experiment — public Figshare original archive source PASS, only 2 study sites

Original [Deng et al. PNAS 2025](https://doi.org/10.1073/pnas.2506750122), official [Figshare original article 29592203.v1](https://doi.org/10.6084/m9.figshare.29592203), CC BY 4.0 and publisher reports **482 original plots, 38,088 tree individuals over years 2021–2024 at only TWO original BEF-China experimental sites**. Actual public Figshare API returned **five original files**, three relatively small original Excel sources, README, R code. All three Excel originals were downloaded from advertised original Figshare file IDs and source-MD5 verified.

| Original public file | Verified original MD5 | Original worksheet schema/row elements |
| --- | --- | --- |
| `DengEtAl_PNAS_H1H2_20250718.xlsx` | `d045623a427b076d529cadb12c025242` | Original worksheet **1,928 XML row elements**, first-row headers `Plot, year, TREE_R, AGB, Canopy cover, FHD, Db` |
| `DengEtAl_PNAS_H3_20250718.xlsx` | `a39eb71df9bf507892213a1d3891bc23` | **1,252 XML row elements**, first-row `Plot, year, TREE_R, NE, SE, CE, Canopy cover, FHD, Db` |
| `DengEtAl_PNAS_Fig5_20250718.xlsx` | `270e84ad263f8d75705f7a0c8d535875` | **37 XML row elements**, processed figure-level source |
| README and author R code | Original public manifest access listed | Original files not biological raw trait/tree records |

**These XML row counts are not independently verified unique plot/year identifiers yet.** The published H1H2 archive contains already aggregated **plot×year AGB and canopy metrics**, and the H3 data contain derived net/selection/complementarity responses (`NE, SE, CE`). **No direct species×plot SLA, leaf N, original taxonomic species name, or individual measured trait row is present in the verified original table headers.** The published original authors constructed aboveground woody biomass from diameter/height with **constant assumed wood density WD=0.52 across all tree taxa**, preventing interpretation as an independent source species-WD/biomass relation.

**Strict verdict: `DIRECT_FIELD_TRAIT_GRAIN_HOLD` for K/FD biology and `INDEPENDENT_SITE_SUPPORT_HOLD` for 5+ independent ecosystem generality.** Four original years are repeated measurement of planted plots, not four spatially independent sites. We do not infer tree species trait values or original species abundance matrices from processed `TREE_R` species richness.

## Source comparison and forward research

The two published original sources **cannot yet deliver the desired direct K→FD→biomass bridge** because each lacks the original **species×plot named primary trait data** and 12-family×20-species original independent family K source architecture. This is a genuine external dataset constraint, not a negative K ecological result.

- Africa has useful **five country-level external validation domains** and original-author derived FD/CWM/AGB per plot. A *separate, clearly labelled* country-out-of-sample test of whether the **already-published standardized FDis** adds prediction beyond other already-published CWM/richness/climate predictors is feasible only after its exact country source-rank gate, and would not test K nor local measured SLA source transport.
- BEF-China supports original longitudinal stock/canopy analysis on public plotted years, and two original field sites, but independent study region transfer cannot be identified from two original sites, and there is no original plant SLA/N plot trait source in the archived small tables.
- To directly explain why phylogenetic trait memory K influences ecosystem function, we still need original data with **actual named plants per original community plot × directly measured plant traits × matched original stand mass × independent dated tree** and **≥12 families with ≥20 independently observed species each**, or externally validated independent family K under a different frozen estimand. Do not reuse the original Jensen authors' already-published positive FDis-NDE model as independent confirmation.

All former sPlotOpen/BIEN, BIODEPTH, and NEON source HOLD and previous negative TreeDivNet original-same-study transfer findings remain unchanged. No ecological response coefficients were estimated by this new source audit; PR is Draft, based directly off original `main`, with no original source rows committed.
