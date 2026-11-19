# Turnover evidence map — what is positively supported, and what is not

## 2026-11-19 submission-critical correction — original Stage B completed (supersedes historical log HOLD for manuscript)

**Source provenance:** [original completed Stage B Actions #37443037590](https://github.com/zuizui0223/turnover/actions/runs/37443037590) (2026-10-06), [audited derived aggregate result and review in PR #30](https://github.com/zuizui0223/turnover/pull/30), and [new corrected manuscript draft PR #67](https://github.com/zuizui0223/turnover/pull/67). The original RC3 [PR #29](https://github.com/zuizui0223/turnover/pull/29) remains **submission HOLD**.

Stage A showed invalid raw ≤0 values in five predeclared positive-only physical traits. Stage B, frozen before its corrected outcomes, excluded only those raw records, recomputed **49** impacted family×trait systems, inherited **152** unchanged and retained all **201/201** systems on original trees. The previously **blocked uncleaned** 25-S3/18-prune log sensitivity is not retrospectively passed; **a different, semantically valid cleaned primary source** now supports all-201 raw and log tests.

| Corrected BIEN statistic | Raw S3 | Raw prune | Log S3 | Log prune |
|---|---:|---:|---:|---:|
| Crossed family repeatability | 0.1564 | 0.1541 | 0.1489 | 0.1615 |
| Held-out-family trait BLUP gain | +1.21% | ≈0.00% | +5.92% | +5.51% |

A corrected correlated-trait zero-family null supports a raw family component (p=0.017 S3, p=0.013 prune). Corrected measurement-aware S3 **point** variance shares are family **16.22%**, trait **6.38%**, system heterogeneity **54.22%**, and finite-species sampling error **23.18%**; overlapping bootstrap CIs prohibit a dominance claim. The revised conclusion is **family-associated repeatability plus scale-dependent modest trait portability**. There is no biological K/FD/biomass mediation or evolutionary-rate inference.

The October run's original 30-day Actions ZIP expired, but the GitHub calculation **job stdout** remained accessible. The exact original 201-system and Stage B corrected 49-system per-row rho/SE outputs have now been recovered into a durable **201×30 corrected-effects CSV** on [RC4 PR #67](https://github.com/zuizui0223/turnover/pull/67). Source-identity, all original Stage B change statistics, and all four mean(SE²) values match; [Actions #44541550788](https://github.com/zuizui0223/turnover/actions/runs/44541550788) independently validated the table and produced three source-linked RC4 figure concepts as SVG/PNG (six files). The source species-state records were **not** reconstructed or republished, no new ecological hypothesis was fitted, and RC4 remains an **anonymous Word/PDF and author-review submission HOLD**, not a data-table HOLD.


**Evidence cut:** 2026-11-19 (JST). **Scope:** editorial synthesis only; `main` frozen BIEN programme plus explicitly referenced open PRs. **No new biological effects, thresholds, datasets, pooled estimators, nulls, or outcomes** are introduced by this document.

## Scientific conclusion for the programme

> Plant phylogenetic trait memory contains a recurring family-level component, while the transferability of trait-specific memory **depends on which aspect of phylogenetic structure is measured**. A lineage's overall memory level and the allocation of memory among traits are different inferential targets; neither has yet been linked causally to community functional diversity or ecosystem biomass.

This replaces **both** overstatements: “traits contain no portable information” and “the trait ranking is universally nonportable.” The new claim is about **predictive generalization and estimand dependence**, not discovery of clade variation per se, proof of evolutionary rates, or adaptive reallocation.

### Level vs allocation are distinct

For any particular statistic `m` (e.g. distance–disparity Spearman `rho` **or** Blomberg's `K`), one can *conceptually* write:

`memory[f,t,m] = mean[m] + family_level[f,m] + trait_average[t,m] + family_trait_deviation[f,t,m] + estimation_error[f,t,m]`.

This is a diagrammatic decomposition; **no joint new rho+K model is fitted here**. A repeatable family-level shift does not imply that the same family preserves the same within-family trait ordering. `rho` is Spearman(patristic distance, absolute trait-state difference), not an OU alpha, Brownian diffusion rate, or half-life. `K` measures agreement with a phylogenetic covariance expectation; an effect under one is not an estimate under the other.

## Evidence ledger (non-overlapping claims)

### E01 — Prospectively qualified BIEN memory gradient; **SUPPORTED**

- Main-branch primary evidence: **201 family × trait systems, 45 vascular-plant families, 12 numeric traits** selected before real effects; positive `rho` in **74.6%**; S3 mean **0.093**, median **0.053**; S3/prune agreement Spearman **0.832**.
- Crossed S3 shares: `R_family=0.1504` (95% ordinary bootstrap CI **0.0204–0.2861**), `R_trait=0.0433` (**0–0.1335**), unresolved/residual **0.8063**; prune family **0.1482**. **No family>trait dominance claim**: the specifically frozen variance-ratio precision gate failed.
- Trait-fixed conditional family repeatability: S3 **0.1825** (CI **0.0285–0.3369**), prune **0.168**; CI crosses the predefined 0.10 practical reference.
- Main branch source/geometry checks: S3 family **0.1458** after taxon/geometry adjustment and **0.1492/0.1470** after source/source-citation adjustment, compared with **0.1504** original. They rule out selected simple measured alternatives, not all confounding.
- Original raw-scale held-out-family same-trait prediction: S3 gain **−0.0242** (`p=0.091`), prune **−0.0324** (`p=0.193`); **no robust positive performance under the original criterion**, not evidence that the true effect is exactly zero.
- Sources: [main README](https://github.com/zuizui0223/turnover/blob/main/README.md), [main publication boundary](https://github.com/zuizui0223/turnover/blob/main/docs/PUBLICATION_BOUNDARY_V0_1.md).

### E02 — BIEN error-aware robustness and scale-qualified trait signal; **SUPPORTED WITH DISTINCT ESTIMANDS / UNMERGED**

- [Draft PR #28](https://github.com/zuizui0223/turnover/pull/28): raw effects replicated for **201/201**; median species-cluster bootstrap SE **0.058 S3 / 0.071 prune**. Measurement-aware S3 *point* partition of typical total variance: family **15.1%**, trait **5.7%**, between-system residual **54.9%**, sampling error **24.2%**. The two-way cluster-bootstrap uncertainty criterion was not satisfied; do not promote this point partition to a definitive biological dominance ordering.
- Correlated-trait zero-family-effect null is exceeded: **p=0.017 S3 / 0.009 prune**; after collapsing to five trait domains, family repeatability **0.144/0.147**. This supports recurring family structure under the specific null.
- Training-only shrinkage changes raw-scale family-holdout gain to **+0.006 S3 / −0.0048 prune**; **little** robust transferable raw trait-level information, *not* demonstrated anti-portability.
- The original all-201 unaltered natural-log sensitivity is **HOLD** (25 S3, 18 prune systems have nonpositive species medians); do not retrofit offset or remove systems.
- [Separate exploratory PR #31](https://github.com/zuizui0223/turnover/pull/31) uses positive-only cleaning and reports log-scale gains **+5.9%/+5.5%** for absolute shrinkage prediction and **+6.8%/+2.8%** for rank prediction. These are a **different preprocessing and estimand route**, not a retroactive PASS of PR #28's no-offset all-201 gate. Never use the blanket claim “trait identity has zero portable signal.”

### E03 — AusTraits family context replicates; metric-specific allocation; **SUPPORTED WITH COMPILATION LIMITS / UNMERGED**

- [PR #13](https://github.com/zuizui0223/turnover/pull/13): qualified source-native core **259 systems / 42 families / 14 traits**; matched positive log core **254 / 42 / 13**. Provenance = **independent-compilation validation**, **not independent primary measurements** (193 contributing datasets, 130 recoverable primary DOIs, DOI recovery only **67.4%**, overlap among recovered DOIs **0.77%**).
- For source-native `rho`: conditional family repeatability **0.2958 S3 / 0.3910 prune**; held-out-family absolute trait gain **+1.39%/+1.63%** (p **0.0188/0.0180**); within-family trait-rank gain **−3.78%/−1.55%**. There is modest trait-average information but no robust rho rank-transfer.
- For **Blomberg's K on the matched 254 systems**: family repeatability **0.5306/0.5881**; absolute log K prediction gain **+4.45%/+6.16%**; held-out-family rank prediction gain **+8.08%/+15.31%** (`p=0.0002/0.0001`); cross-family rank reversal **44.03%/39.88%**. Consequently, **metric-invariant failure of trait-rank portability is false**.
- A matched-tree equal-parameter Brownian null did not reproduce the observed K architecture (64 simulations, coarse minimum one-sided p **1/65**); a different predeclared homogeneous OU + K-blind source heterogeneity envelope could reproduce the scalar rank portability amplitude. These nulls do not license claims about adaptive constraint, lineage-specific rate shifts, or universal process differences.
- Family-specific point scores are not established to transport robustly between BIEN and AusTraits after source/geometry adjustment. Do **not** numerically pool family repeatability across source compilations as if independent causal studies.

### E04 — Reproductive vs vegetative K; **EXPLORATORY POSITIVE WITH ASCERTAINMENT DEPENDENCE / UNMERGED**

- [PR #33](https://github.com/zuizui0223/turnover/pull/33), [paper draft #38](https://github.com/zuizui0223/turnover/pull/38): Same-tip/tree seed+fruit vs leaf/petiole/height comparisons yield reproductive `K` higher in **313/406 = 77.1% S3** and **314/397 = 79.1% prune** across **34 families**.
- Excluding five major electronic floras: **221/283 = 78.1% S3** and **180/233 = 77.3% prune**. Further strict matched remaining source IDs and tips: **120/142 = 84.5% S3 (24 families)** and **81/101 = 80.2% prune (18 families)**.
- Cohort/tip restriction and source substitution can change pair ordering; the apparent strict-cohort increase is **not** proof of stronger intrinsic reproductive conservatism. The reported ~65% organ-only leave-family-out sign score is an algebraic reformulation of the same pairwise wins, **not an independent confirmation**.
- Organ categories were fixed **after** initial K outcomes; external independent primary-measurement replication remains outstanding. No inference of slower reproductive evolutionary rates, OU alpha, or adaptive selection.

### E05 — Ecological biomass associations: some site-specific observations, **NO ROBUST COMMON POSITIVE FD/PD TRANSPORT**

| Source and estimand | Verified result | What can be claimed |
|---|---|---|
| [Cedar Creek E120 #44](https://github.com/zuizui0223/turnover/pull/44), 1998 n=94 teaching-secondary dataset | Functional-guild identity heterogeneity remains under 18-field-row conditioning; conditional permutation **p=0.0070** | Site-specific observational species/guild mixture differences; no pure guild causality or out-of-study generality |
| [Jena #40](https://github.com/zuizui0223/turnover/pull/40), same-richness n=62 | FG count May `beta=+0.12867`, HC3 **p=0.168** after categorical richness and block | Nominal positive direction but independent FG count effect **not established**; Cedar pattern not replicated |
| [BIODEPTH #45](https://github.com/zuizui0223/turnover/pull/45), 110 matched plots/8 sites | Legume–nonlegume-forb source equal mean log biomass **+0.17147**, site-bootstrap CI **−0.548 to +0.918** | Direction and magnitude heterogeneous; no pooled significant positive replacement |
| [BIODEPTH #46](https://github.com/zuizui0223/turnover/pull/46), 174 plots/7 sites | Height-FD incremental held-out SSE gain unmodified GIFT **−123.09%** vs botanically corrected oregano-height scenario **+3.83%** (CI **−10.92 to +18.29%**) | **Data-quality and extrapolation sensitivity**; post hoc correction does not prove positive FD–mass transfer |
| [BIODEPTH #51](https://github.com/zuizui0223/turnover/pull/51), 150 plots/7 fields | Additional community PD held-out standing-mass SSE gain **−1.451%**, CI **−7.291 to +3.151%** | No robust additive PD transport under exact baseline/feature model |
| [TreeDivNet #57](https://github.com/zuizui0223/turnover/pull/57), 113 original plots/6 studies | Observed plot SLA+leafN two-trait FD increment to **absolute woody standing stock** prediction beyond richness+CWM: **−34.91%** held-out-study SSE gain (bootstrap **−70.78 to −1.56%**); 103 plots/5 studies without MataDIV: **−106.19%** | New specified FD predictor does **not** generalize positively; not a negative causal effect of FD |

**Do not pool these effects.** Guild category, one-dimensional height FD, two-dimensional measured in-plot FD, PD, standing crop, absolute woody stock, and published woody *net diversity effect* are different variables/estimands. Jena, BIODEPTH, Cedar and TreeDivNet differ in controls and data generation; reuse of the same experimental rows across source papers does not create independent replication. Positive published TreeDivNet monoculture-derived FDis → woody NDE findings are not contradicted by the alternate absolute-stock holdout result.

### E06 — Assignability of known-truth effects in simulations; **POSITIVE METHODOLOGICAL RESULT, NOT BIOLOGY**

- [PR #27](https://github.com/zuizui0223/turnover/pull/27): 722 prequalified geometries, 120 families/25 traits; successful target recovery **255/722** (continuously measured **249/443**, categorical **6/279**). Under one thresholded OU family, 220/276 nominal geometries failed to bracket the rho=0.15 target, although all 220 supported one-transition edge splits at or above target. An alternate Mk2 generator rescued 51/220; state-balance normalization rescued 50/167 among matched Mk2 no-bracket systems.
- General inference: distinguish **state-space feasibility**, **generator accessibility**, and **estimator recovery**; failure to impose target truth must not be mislabeled weak biological signal or mere low estimator power. Does not imply categorical traits are evolutionarily unconserved.

## Explicit non-claims / frozen source gates

1. **Do not assert** that `K` or `rho` causes FD, that FD causally raises/lowers standing biomass, or that `K -> FD -> biomass` mediation has been measured: no joint qualified original-species×plot phylogeny–trait–biomass design exists.
2. General time×space trait turnover programme closed **before real biological outcomes**: BIEN spatial informativeness bound and AusTraits joint structural bound. Mangal/GloBI interaction source programme likewise stopped on semantic/provenance gates before rewiring or time×space coupling was tested. Source HOLD is **not a biological null**.
3. Jena 2020 original 78 plots / 851 plot-years / 59 trait taxa [#58](https://github.com/zuizui0223/turnover/pull/58) passed source keys, but the signed-trait time-transport [#60](https://github.com/zuizui0223/turnover/pull/60) had only 55 eligible training plots and 47/48/51 heldout-year plot supports vs frozen 60 each: **no new FD→biomass coefficient estimated**.
4. Ali 2026 original forest source [#61](https://github.com/zuizui0223/turnover/pull/61) reported 157/200 **negative** purported physical AGB values and lacked direct species×plot source trait rows; this is **source HOLD**, not an ecological effect.
5. New **independent source-only** branches [NutNet/CoRRE #62](https://github.com/zuizui0223/turnover/pull/62) and [Africa/BEF-China #63](https://github.com/zuizui0223/turnover/pull/63) retain their *own already-frozen* original data, species coverage, site-count and year/unit acceptance gates. They have **no new qualified ecological effect** in this evidence cut.

## Publication split and next executable gate

**Paper A (primary comparative ecology):** BIEN family context and prospective held-out prediction. Keep main frozen results authoritative; cite PR #28 as a separate measurement-error and trait-redundancy sensitivity, not replacement of original CIs; mention scale dependence of PR #31 as additional exploratory boundary. Use K contrast to prevent sweeping conclusions across estimands; present AusTraits as *independent compilation*, not independent original-data replication.

**Paper B (exploratory functional morphology):** Reproductive versus vegetative K with matched species, tree, source and taxon-selection decomposition. Keep post-discovery classification, lack of primary source replication and actual paper Draft status prominent.

**Paper C (methodology):** Structural feasibility vs generator-accessible known truth vs recovery, using outcome-free simulations.

**Separate ecosystem-function research programme:** Judge only *new* source-qualified original studies under the already-fixed source rules in #62/#63. If eligible, test **within-study** and **leave-whole-independent-study-out** prediction under a fixed response definition with explicit richness/CWM baseline. Preserve all source HOLDs, never pool non-equivalent biomass endpoints, and **do not tune old TreeDivNet or BIODEPTH outcomes again**.

## Figure/communication contract

- Panel A: two-dimensional concept — mean lineage-level memory vs within-lineage trait allocation, marked “schematic, not new fit.”
- Panel B: same-source `rho` vs `K` held-out trait-rank gains on matched AusTraits systems; show S3 and prune distinctly and identify different estimands.
- Panel C: evidence-status grid (qualified biological support / exploratory observation / failed prospective prediction / pre-outcome source HOLD), **not a pooled effect forest plot**.
- Label every panel with dataset, genuine independent biological unit and response definition. No “universal law” or adaptive-process wording without independent validation.

## Change control

This is an **editorial cross-programme map**. Existing completed `main` BIEN analyses, their pre-frozen stop rule, all open paper branches, archived results, original scientific decisions and source-qualification thresholds are unchanged. Recheck linked PRs before any journal-facing claim; this snapshot does not automatically incorporate later commits.


## Same-day source-gate update (2026-11-19; no new biological effect)

The already-existing [PR #62](https://github.com/zuizui0223/turnover/pull/62) NutNet 2025 public species cover vs NutNet 2026 original biomass/CWM attempt yielded **zero** exact original shared site×calendar-year pairs despite **57** verbatim shared site codes, so no valid original species→plot biomass join or new FD effect was opened. CoRRE original EDI DOI metadata qualified, but its *observed-only* individual source trait records remain unverified (DO NOT use phylogenetically imputed K).

The independent [Africa/BEF-China PR #63](https://github.com/zuizui0223/turnover/pull/63) completed the source-only result (replayed after one original Zenodo HTTP 504). For Africa, country source counts **64/8/168/6/30** include two groups below the pre-frozen 12 plot threshold, and **all 104 young plots belong to Ethiopia**; leaving Ethiopia out makes the growth-stage covariate rank-deficient (**9/10 baseline; 10/11 with FD**). No five-country published-FDis→standardized-AGB effect was fitted. In BEF-China, actual released original H1H2 XLSX has **486** unique plot IDs / **1,927** plot-year records, compared with 482 plots in the published description; original exclusion rules are unresolved. Only two original experimental sites and no named species×plot local SLA/leaf N records were verified. All hold decisions are **source/design findings**, not biomass-effect null results.

A **new separate public candidate**, [FunDivEUROPE PR #65](https://github.com/zuizui0223/turnover/pull/65), was source-prequalified using the existing ≥80 plot / ≥5 forest group / ≥30 named species / original local trait coverage rules. Published catalogue metadata describe 209 mature forest plots in six regions and local crown-leaf measurements, but its official original Dryad workbook returned **HTTP 403** in the source-only CI ([verified source gate run](https://github.com/zuizui0223/turnover/actions/runs/44515506497)). Thus **SOURCE_ACCESS_HOLD**, not a proven absence of local trait rows. No K/FD/mass effect opened. Details and the nonraw source verdict are permanently recorded on PR #65.

**Publication implication:** do not add a speculative “FD mediates phylogenetic memory→biomass” claim. Paper A/B/C boundaries above remain unchanged. Future independent-source admission requires truly original named species, directly measured species traits, matching plot biomass, and sufficient independent forest groups; failed original-source plans are not retrospectively reclassified as biological nulls.

## 2026-11-19 original-source preflight: local trait × wood-stock TERRA-PNW

A new source-only [PR #66](https://github.com/zuizui0223/turnover/pull/66) frozen before raw rows uses original NASA/ORNL DAAC DOI `10.3334/ORNLDAAC/1292`. The authors' published descriptors report **1,296 individual leaf-trait records**, **266 stand-stock/composition rows**, **35 tree/shrub taxa** and **six collection projects** in Oregon/northern California. Unlike plot-CWM-only studies, the source *may* allow exact original local species×plot SLA and leaf-N joins to stand woody carbon; **actual matched direct-trait plot counts have NOT been verified**.

The prospective source gate checks exact original `PROJECT×PLOT_ID`, local SLA/leaf-N measured within two years, uniquely resolved six-letter overstory taxon codes, ≥2 dual-trait taxa per plot, ≥80% listed overstory basal-area support, ≥80 eligible original plots / ≥30 botanical taxa / ≥5 project groups with ≥8 plots, and repeated-site identity. Its original response candidate is `AG_BIOMASS_TREE_WOOD_AS_CARBON` (g C m−2), **not foliage or total carbon**, which could be algebraically derived in part from SLA. Original source may require NASA Earthdata permission: controlled access yields SOURCE_ACCESS_HOLD, not missing biological data.

**Source-only CI has now passed its 8 synthetic tests, but the original ORNL leaf CSV returned HTTP 401 (controlled access).** [Verified Actions #44518757061](https://github.com/zuizui0223/turnover/actions/runs/44518757061). No original CSV trait/biomass rows were admitted, no FD effect estimated, and no K mediation fit. This is SOURCE_ACCESS_HOLD, not an ecological null. A published total of only 35 tree/shrub taxa is far below the existing original 12 families×20 observed species K gate. Six projects sharing a regional archive are not six independent published ecological studies.
