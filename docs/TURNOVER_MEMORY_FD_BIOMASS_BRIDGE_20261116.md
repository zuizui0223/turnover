# Trait memory → functional diversity → biomass: source-aware bridge (2026-11-16)

**Status: a post-result analytical bridge and newly calculated site-influence descriptive, not a new confirmed biological effect.** This branch builds on Draft PR #46; it does not merge/alter original outputs, reopen closed prospective source gates, or assign phylogenetic-memory mechanisms to biomass.

## What the repository actually establishes

| Evidence family | Result | Status |
| --- | --- | --- |
| BIEN temporal trait-memory rho: 201 family×trait systems, 45 families | Family repeatability 0.1504 (95% CI 0.0204–0.2861); conditional 0.1825 (CI 0.0285–0.3369). Raw-scale trait-name LOFO gains −0.0242/−0.0324. | Completed within-source temporal study, not a family>trait variance dominance test |
| AusTraits K: 254 matched-log systems, 42 families | Family repeatability 0.5306/0.5881 (S3/prune), held-out family rank prediction gains +8.08%/+15.31%. An equal-process BM null does not reproduce these K results. | Independent compilation validation, not verified primary-source independent replication nor selection mechanism |
| AusTraits reproductive–vegetative K | Reproductive K larger in 313/406 (77.1%, S3), 314/397 (79.1%, prune); nonflora source-qualified 221/283 (78.1%, S3). | Post-selected organ grouping, species/tip and source-sensitive; no universally slower rate demonstrated |
| Cedar Creek 1998 guild identity | Within single site, geographically conditioned permutation p=0.0070 with 18 field rows. | Positive within-site exploratory association; nonreplicating Jena, not general guild-count or causal effect |
| Jena 2003 function-group count | Historical log-richness May p=0.0439; with exact richness factor p=0.1510, matched 62-plot p=0.1676. | Specification-sensitive, not confirmed universal positive |
| BIODEPTH 8-site matched planted guild contrast | 6/8 positive sites; equal-site mean log1p biomass +0.17147, site bootstrap 95% CI −0.54832 to +0.91837. | Descriptive post-source-failure heterogeneity |
| BIODEPTH 2010 planned one-axis height-FD adds to source-heldout biomass prediction | Original GIFT oregano=13m: seven-site equal gain −123.09%; source-based Kew 0.9m sensitivity: +3.83%, original 95% bootstrap CI −10.92% to +18.29%, only 4/7 sites positive. | One trait-source anomaly radically changes extrapolation; corrected positive FD increment **not** established |

**Independence boundary:** BIODEPTH 2005 and 2010 are the same eight experiments, and the two versions of the source biomass measurements are not numerically interchangeable. Cedar Creek, Jena and BIODEPTH use nonidentical guild definitions and biomass targets; do not meta-pool their coefficients as interchangeable experiments.

## Newly executed source-consistency + site-influence audit

The accompanying Python script checks the original 174 plots, 521 source response rows, archived original seven-site fold scores and corrected original JSON against the *already published* two-decimal per-site Kew correction table. Recomputed mean from rounded corrected scores is +3.8314%, compared with original archived +3.8300%. This tiny difference is **only source-publication rounding**. The original source exact mean is −123.0854%.

| Heldout field excluded | Mean of other six corrected heldout FD score gains, % (approx.) |
| --- | ---: |
| Germany | +1.377 |
| Ireland | +1.615 |
| **Portugal** | **−0.592** |
| Sheffield | +8.978 |
| Silwood | +6.425 |
| Sweden | +1.963 |
| Switzerland | +7.053 |

Thus, **one-site deletion (Portugal) changes the corrected +3.83% site-average sign**. The corrected score remains only four positive versus three negative sites, and its existing original site-bootstrap interval spans zero. This is a robustness diagnostic, not a new hypothesis test, and it does not mean Portugal is an outlier to discard.

Run from the PR#46-based branch:

```bash
python3 scripts/analysis/audit_height_fd_transport_memory_bridge_v0_1.py --output build/biodepth_fd_site_influence_v0_1.json
```

The script fails closed if the original or corrected source denominators, source numeric aggregates or published per-site table stop matching; it needs no raw traits or plot responses.

## Why K and rho cannot directly identify community functional diversity

The 201-system BIEN distance–disparity statistic rho, AusTraits Blomberg's K, realized community functional diversity, and aboveground standing mass are **four distinct estimands**, not competing ways to measure the same latent biological magnitude.

For independent equal-rate BM on a known tree, let log trait states have Brownian variance rate `sigma²`, and let `d_ij` denote patristic separation. For two tips:

```
E[(x_i - x_j)^2 | tree] = sigma² * d_ij
E[|x_i - x_j| | tree] = sigma * sqrt(2 * d_ij / pi)
```

Therefore, the *expected* equal-species-weighted mean absolute pairwise trait difference of an actual community is `sigma * sqrt(2/pi) * mean_pairs(sqrt(d_ij))`; its squared-difference analogue has expectation `sigma² * mean_pairs(d_ij)`. For a balanced four-tip illustration, pair distances 2 versus 4 imply a `sqrt(2)` expected difference in absolute FD for same-sigma communities. Uniformly doubling measured trait amplitude doubles absolute FD and quadruples squared FD **without changing Blomberg K or rank-based distance–disparity rho** on the unchanged tip set and tree. BM is a mathematical counterexample to direct K→FD identification, *not* a fitted ecological null for BIODEPTH.

Hence a species sampling change can affect community FD simply by altering the sampled phylogenetic distances, even if an intrinsic tree-wide signal statistic is unchanged. Trait scale, community membership, and original observation/source quality must be handled explicitly. Nothing in this identity predicts actual plant biomass or establishes causal mediation by phylogenetic memory.

## The next genuine empirical test, with an explicit gate

For a **new independent plot dataset**, freeze the biological cohort and original source identities before accessing response values. Require: original plot × time dry-mass responses with unit and harvest context; original independently measured species traits with sample/source traceability and plausibility QC; complete community membership with planted versus realized composition distinguished; tree, phylogenetic distances and ecological guild identities from matching taxa; replication across independent source sites. Check the relevant >=12 independently supported families and at least five source sites **before** attempting a general K→FD→biomass inference. This is a new study qualification, not permission to weaken the original frozen 201-system gate.

Only once support is demonstrated, test (i) trait diversity prediction beyond same-plot CWM, richness, guild and site context on held-out **entire field sites**, (ii) whether PD plus independent trait amplitude predict observed FD more robustly than K alone, and (iii) separately whether adding the *K×phylogenetic-breadth interaction* improves out-of-site FD prediction. Keep site/field as the replication unit, not repeated plot-years or pairwise comparisons; use a predetermined one-direction primary test and its site-level uncertainty. Do not interpret predictive gain as causal selection or biomass mediation without manipulation/exogenous evidence.

**Current decision:** The archival corrected BIODEPTH seven-site FD gain fails its own ≥5 positive-site and lower-CI>0 thresholds. Therefore no positive K→FD→biomass relation can be claimed today. Further global tests remain blocked by source support and/or authorization, not by an empirically demonstrated zero effect.
