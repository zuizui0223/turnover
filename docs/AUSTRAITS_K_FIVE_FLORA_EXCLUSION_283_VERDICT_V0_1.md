# Removing five dominant electronic floras preserves the broad reproductive-organ phylogenetic K advantage

**Verified 2026-10-17 from successfully completed CI #38922133371 and its frozen 283-pair output.** This is a **post-discovery AusTraits v7.0.0 source-robustness sensitivity**, not independent primary-source replication, prospective confirmation or mechanistic inference. Source exclusions were fixed by original public study provenance and their K-blind support tested [before this K re-estimation](https://github.com/zuizui0223/turnover/actions/runs/38920414545).

## Scientific question

Can the previously described reproductive (seed/fruit) > vegetative (leaf/petiole/height) contrast in Blomberg's K be explained entirely by **five electronic Floras** that contribute the majority of the matched-source organ dataset links? The excluded AusTraits DatasetIDs were `ABRS_2023` (*Flora of Australia*), `NHNSW_2023` (PlantNet), `RBGV_2023` (VicFlora), `NTH_2023` (Northern Territory flora) and `SAH_2023` (South Australian eFlora). They contributed **49,746/65,043 (76.48%) source-to-species×pair links** in an earlier, differently restricted 279-pair source intersection. These links are **not independent measured individuals**.

The study reconstructed the same original K-positive species median values from the fixed AusTraits 7.0.0 parquet SHA256 `5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99` and its pinned unit definition. For each original K-blind eligible reproductive–vegetative pair, we retained only species with positive numerical medians **after removing all five DatasetIDs**. Within that **unchanged common species and tree**, both organs' K were re-evaluated from (1) all original AusTraits contributing measurements of the retained species, (2) non-flora source measurements only. Thus the difference *within that pair* changes measurements, not species/taxonomic support or tree geometry. It **does not** require the two non-flora traits to have been collected by the same remaining DatasetID; this joint restriction is an outstanding further source-availability diagnostic.

The resulting same-tip source contrast is descriptive, not a comparison of the original (larger) taxon cohort's K to the trimmed cohort as a pure observation-source effect. Source eligibility and the 20-common-species cutoff were set before the resulting post-exclusion K estimates were opened. The organ-class hypothesis itself was already discovered after the original K results.

## Verified 283 original source-qualified pair results

[Complete 18-job source and phylogeny CI #38922133371](https://github.com/zuizui0223/turnover/actions/runs/38922133371), final artifact `austraits-k-five-flora-exclusion-283-final-v0-1`; 16 immutable native-tree K batches and full 5,000 whole-family bootstrap, no missing 283 source-eligible pairs.

| Original source-matched-tip cohort, excluding five electronic Floras in measurement arm | Native V.PhyloMaker2 S3 | Original GBOTB prune-only |
|---|---:|---:|
| K-blind qualified cross-organ pairs | 283 | 283 |
| Native supported paired K results | **283** | **233** |
| Pair-by-tree holds (<20 native prune tips etc.) | **0** | **50** |
| Families with supported same-tree comparisons | **29** | **25** |
| All original source medians, **on these identical reduced tips**: reproductive K higher | **222/283 = 78.45%** | **182/233 = 78.11%** |
| **Five electronic Floras excluded**: reproductive K higher | **221/283 = 78.09%** | **180/233 = 77.25%** |
| 5,000-family bootstrap 95% CI, pair-weighted five-flora-excluded reproductive win rate | **68.48–86.67%** | **67.02–87.12%** |
| **Equal-family-mean five-flora-excluded reproductive win rate** | **75.60%** | **73.96%** |
| Equal-family 5,000-bootstrap 95% CI | **64.55–85.36%** | **60.97–85.42%** |
| **K sign reversal due ONLY to changing source values on the SAME tips/tree** | **21/283 = 7.42%** | **16/233 = 6.87%** |
| Median paired shift in reproductive−vegetative logK from flora source removal | **0.0000** | **−0.00195** |
| Mean paired shift in reproductive−vegetative logK from flora source removal | −0.03186 | −0.03532 |

All 283 original source-based candidate pairs were assessed; the prune-only 50 holds cannot be interpreted as a phylogenetic signal tie or negative result. Their missingness could still affect prune-axis generalization.

### Biological trait classes survive separately

| K reproductive higher AFTER removing five Flora DatasetIDs | S3 | prune |
|---|---:|---:|
| Fruits (three length/width/height traits) vs vegetative | **82/106 = 77.36%** | **57/76 = 75.00%** |
| Seeds (width/length/dry mass) vs vegetative | **139/177 = 78.53%** | **123/157 = 78.34%** |
| All comparisons EXCLUDING `seed_dry_mass` (source Kew SID concern) | **178/229 = 77.73%** | **140/183 = 76.50%** |

No one single seed-mass-rich source or the five electronic floras suffices to explain the descriptive cross-organ K ordering in the source-eligible original AusTraits subset. However, the remaining **non-flora datasets may include descriptive taxonomic monographs, herbarium scores, source compilations and correlated measurements**; they are not a randomly sampled independent primary-observation control.

### Same-source membership and individual families need careful separation

For the **233** supported pairs on BOTH S3 and prune trees, the non-flora reproductive-versus-vegetative winner is **reproductive on both in 168**, **vegetative on both in 41**, and **tree-dependent in 24**. Thus exactly **72.1%** show a reproductive advantage on both trees (168/233), and 10.3% exhibit tree-axis disagreement.

Within the non-flora-only pair universe:

| Family | S3 reproductive K higher | prune reproductive K higher | Difference from earlier source-matched 279-pair subset |
|---|---:|---:|---|
| Fabaceae | **23/25** | **25/25** | Positive class contrast remains |
| Poaceae | **20/20** | **18/19** | Positive class contrast remains |
| Cyperaceae | **10/10** | 2/2 | prune support too sparse for lineage claim |
| **Casuarinaceae** | **4/9** | **4/9** | Previously 0/3, 1/3 among different original **same-DatasetID** pair cohort |
| **Rubiaceae** | **4/6** | 1/4 | Previously 0/6, 0/6 among different original **same-DatasetID** pair cohort |
| Proteaceae | 16/25 | 16/25 | Reproductive advantage weaker than families like Poaceae |

**Caution:** Different source/phylogeny eligibility implies **different species and trait-pair sets** across the earlier 279-cohort and this new 283-cohort, even though each *within-cohort measurement-arm comparison* fixes its own species/tips/tree. The changed Casuarinaceae and Rubiaceae fraction therefore **does not establish that Flora values caused the family exceptions**. It does show that calling those entire lineages intrinsically “opposite” is premature and heavily source/sample conditioned.

## Paired source-only effect and boundary on biological mechanism

On unchanged 283/233 supported family×pairs, source removal alone produces **21/16 sign reversals**. Exploratory family-bootstrap of the *paired difference* in win rates gives **−0.35 percentage points (95% family bootstrap −5.2 to +3.3 pp) S3** and **−0.86 pp (−3.4 to +2.0 pp) prune** (10,000 whole-family resamples, fixed seed 20261017, calculated on archived per-pair output). These CIs are broad and include non-negligible negative values; **do not interpret small point estimates as an equivalence or non-inferiority test**. The 5,000-bootstrap family-CIs in the main table are original pipeline estimates. The paired-difference analysis is a separately added exploratory QA descriptive sensitivity.

**What this falsifies within this particular database:** the strong hypothesis that the broad organ K contrast is only an artifact of the FIVE NAMED electronic Flora DatasetIDs. The result does **not** falsify the broader possibility of floristic/secondary-source biases, because e.g. `Kooyman_2011` also obtained leaf/fruit data from published floras and `Maslin_2012` is a taxonomic treatment; both can remain after electronic Flora removal. Nor does this identify developmental constraints, natural selection, evolutionary rates, OU alpha, true common ancestor signal or environmental plasticity.

**Next independent evidential gate:** a fully source-qualified independent primary measurement cohort meeting the existing new-data protocol, or else a final, clearly exploratory *joint* non-flora and identical surviving DatasetID support diagnostic on the **142 source-feasible pairs across 24 families** (source support already counted before any new K values). After either, stop new AusTraits biological subgroup scanning and finish the manuscript.

## Reproducible source provenance

- [K-blind five-flora removal support #38920414545](https://github.com/zuizui0223/turnover/actions/runs/38920414545)
- [Full 283 matched-tree K result #38922133371](https://github.com/zuizui0223/turnover/actions/runs/38922133371)
- [Pinned exact-source original cohort and reproductive organ family rules](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/austraits_k_exclude_five_electronic_floras_support_v0_1.json)
- [Previous 279-pair same-original-DatasetID K study](https://github.com/zuizui0223/turnover/actions/runs/38698215216)
- [Previously verified 760 same-tip K results](https://github.com/zuizui0223/turnover/actions/runs/38674635870)
- No raw species identities, trait records or underlying original dataset IDs were exported by the 283 K result; all inferences are original-source, exploratory and fully within AusTraits.
