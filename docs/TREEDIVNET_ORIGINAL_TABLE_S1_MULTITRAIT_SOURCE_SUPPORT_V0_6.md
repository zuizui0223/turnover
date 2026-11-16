# TreeDivNet Table S1 matched multispecies multivariate FD source support

**Source-only diagnostic frozen on 2026-11-16 before opening new joint-axis plot coverage counts**, after the source-verified single-axis time gate passed on the previously declared 2-calendar-year window (141 ECOLINK-excluded plots, with individual SLA=117, LNCM=120, WD=56 plot support). These earlier counts were known; this test is a *post-source* feasibility diagnostic, not a new ecological effect or independent field experiment.

## Original source contract
- Same user-uploaded original publisher Table S1 (16,088 bytes, SHA256 `245fdf2002240b905b032c9f444a9a359991212be93032637c9ed80a27516fee`) and the source-only 11-experiment Table S1 inventory-year metadata preserved in `results/treedivnet_uploaded_original_TableS1_inventory_years_source_v0_6.json`. No original workbook in GitHub.
- Same public original Figshare DS1 and DS2 MD5-pinned 328-plot exact join; same 186 plots with nonnegative DS1 woody and >=2 source species positive in some single trait, original 153 after ECOLINK genotype-coppice exclusion and 143 after further MataDIV fertilized-context exclusion.
- Every feature uses **only original DS2 `site × block × plot × species` SLA, LNCM and WD values**, strictly positive and finite; original species labels are preserved and no missing or measured years imputed. A source species must have *all required trait values on the same original DS2 species row* to be considered jointly covered; two distinct species with complete same-row traits are required per original plot for a distance/FD to be computable.
- Original site-specific inventory year for **each** included trait axis and unique original stand woody inventory year must differ by <=2 calendar years; no site-age or original publication-year substitution. ECOLINK never admitted into the standard single-standing-stock inference cohort (cumulative 2017+2020+2023 harvested woody and genetically manipulated willow diversity).
- Original DS1 is the unique stand woody response; DS2 species woody values are not summed or used as FD weights.

## Three prospective source-only trait bundles and predeclared support

1. **SLA + LNCM** — both leaf economic traits on each of at least two original source species per plot, and both Table S1 inventory years <=2 years from the same site woody biomass inventory.
2. **SLA + WD** — leaf surface area plus xylem wood density on same species, temporal rule for each.
3. **SLA + LNCM + WD** — 3-trait multivariate source support on same two or more original species with positive measured DS2 values and independent original years.

Report the original plot count, unique source species count, original site count and number of sites with >=8 qualifying original plots for **all experiments (for diagnostics), excluding ECOLINK (primary source population), and excluding both ECOLINK and MataDIV (fertilized design sensitivity)**. Require **>=80 plots, >=5 sites each with >=8 plots, >=20 distinct original taxa** to label any bundle `MULTIAXIS_SOURCE_NUMERIC_SUPPORT_PASS`; otherwise `MULTIAXIS_SOURCE_NUMERIC_SUPPORT_HOLD`. Do not loosen this after seeing counts. Distinguish source numeric support from genuinely measured original per-tree trait provenance.

A single trait axis count (SLA117, LNCM120, WD56 after ECOLINK removal) is **not** an upper bound on two-axis correlation or multivariate ecological response: it only bounds the potential same-plot/fully measured pair count. This diagnostic may show that 2D is eligible while 3D is not, or both fail, with no change to the already verified 141 source-year eligible plots.

## Stop conditions and nonclaims

No current ecological trait-distance–mass response is opened. Original dataset authors have already published their own diversity–carbon relationships; this is NOT independent confirmation. There is no source original family-specific Blomberg K (40 total study species); phylogenetic distance breadth and observed FD are distinct variables. Original individual source sampling identities and DS1-vs-DS2 woody normalization remain HOLD under the earlier source gate, even if a multiaxis numeric support test passes. The original published methods evidence is distinct from original per-row verified sample IDs.

No copyrighted biological source records, plots or original user XLSX are exported. All computations are original-source quality checks in GitHub CI.
