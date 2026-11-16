# BIODEPTH: 999 within-guild height-label permutations do not establish a special source species-height allocation

**Executed:** 2026-11-16, frozen prior to this *new* permutation result in `docs/BIODEPTH_HEIGHT_TRAIT_LABEL_RANDOMIZATION_DESIGN_V0_1.md`. Retrospective/exploratory because original biomass outcome and the Origanum correction were already known.

## Source + analysis QA: PASS

- Original Hector2010 (not Spehn2005 Shoots): SHA256 verified 2010 Species, Codes, Community, and original 2005 planted Design; the original source reference/GIFT live API fingerprints replay exactly.
- **174 original planted plots; 521 plot×year Community aboveground biomass responses; seven European source field sites; 88 height-covered original species**. Original GIFT *Origanum vulgare* 13m anomaly corrected to independent Kew 0.9m *for both observed and permuted mappings*, keeping the original 13m historical archive unchanged.
- Guild inference from intersections of original all-480-plot planted treatment flags: **51 species** uniquely assigned (**21 grass, 9 legume, 21 forb**), **37** original GIFT height species not uniquely identifiable held at their observed heights; **0** contradictory sources. All **174/174** eligible plots contain ≥2 within-guild-shufflable height species. The three pre-result structural eligibility gates **PASS**, but the unreassigned 37/88 species limit the scope of the conditional null.
- Replayed Kew-corrected original seven-site heldout effect: exactly **+3.829987%** equal-site mean FD predictive SSE improvement over a mean-height-adjusted model; **4/7** sites positive. Historical independent-site bootstrap 95% interval **−10.923% to +18.286%**. These are unchanged historical results, not new confirmation.

## New guild-conditioned species–trait mapping null: 999 fixed permutations

The same 51 unambiguously classified species undergo one globally consistent GIFT maximum-height reassignment **within each original functional guild** (999 independent permutations, seed 20261116). 37 ambiguous source species retain their height. Every permutation preserves the exact originally planted species incidence, individual-species occurrence frequencies, original seven sites, original 521 responses, height-missingness, three marginal within-guild height distributions and all M0 original covariates. M1 includes mean height; M2 adds mean log-height pairwise dispersion; BOTH are retrained in each of seven leave-whole-site-out folds.

| Metric | Observed original species-height mapping | Guild-conditioned label-shuffle null |
| --- | ---: | ---: |
| Equal-site mean heldout gain of adding FD beyond CWM | **+3.830%** | null median **−3.028%** |
| Null-reference 2.5–97.5% | (old site-bootstrap 95% **−10.92 to +18.29%**, a different quantity) | **−13.677% to +7.421%** |
| Observed − null median | **+6.858 percentage points** | — |
| One-sided label-null Monte Carlo tail p | **0.063** (62 of 999 null draws ≥ observed; add-one p=63/1000) | — |
| Frozen decision | **NOT above the 97.5th percentile** | therefore **NO LABEL-NULL PASS** |

The observed mapping is better than the null median, but not in the rarest 2.5% of the *predeclared conditional null*. It is not even below a conventional 0.05 one-sided cutoff. That result should not be rephrased as an established positive association or ecological evidence for species-specific complementary height allocation.

### Original historical corrected seven heldout site scores (unchanged)

| Heldout site | FD over CWM heldout SSE gain |
| --- | ---: |
| Germany | +18.56% |
| Ireland | +17.13% |
| Portugal | +30.37% |
| Sheffield | −27.05% |
| Silwood | −11.73% |
| Sweden | +15.04% |
| Switzerland | −15.50% |

These are original-site results from the botanical-height correction, not independent replications of this null test. The former one-site leave-out diagnostic showed that excluding Portugal alone makes the corrected seven-site average negative, and the main 95% site-bootstrap CI remains broad and includes 0. **A positive FD→biomass transport law is not established.**

## Scientific conclusion and boundaries

The source-corrected observed arrangement yields **numerically better** cross-field FD prediction than the typical within-guild alternative. However, the null overlap is substantial and the seven-site response itself remains heterogeneous. Inferences are therefore limited:

1. These results are compatible with **species composition/trait assignment mattering** for transport, but do not verify a general biological driver or a positive cross-site FD effect.
2. This label randomization asks a narrow predictive question; guild assignment is not a randomized intervention, 37 heights remain fixed, site-specific source pools and plot designs differ, and a trait-label null alone is not a general causal trait–environment interaction test.
3. Only one-axis species maximum **height** was measured from original GIFT source (not same-site realized height). The guilds, GIFT provenance, year-specific standing biomass, and planted/realized distinction matter.
4. No BIEN or AusTraits phylogenetic rho / Blomberg K is matched to these 174 community plots. Therefore **K→FD→biomass mediation is still untested**, and no phylogenetic constraint, selection, or mass mechanism follows.
5. Original >=6 strong exact-richness BIODEPTH site-gate, global 201-family BIEN/sPlotOpen GIFT source and NEON authorization remain **HOLD**.

## Reproducibility and preservation

- **Source + 999 analyses PASS:** https://github.com/zuizui0223/turnover/actions/runs/43805372379
- Full aggregate artifact `biodepth-2010-guild-conditioned-height-label-null-aggregate`, ID **14198695474**, digest `sha256:79b789e39679cd412e9d8a4e72b7c1347c8a43c6564a9e0e2880b627028f250e`; includes exact seven-site null summaries but expires according to GitHub retention. No raw copyrighted study rows exported.
- Permanent source-run stdout aggregate, incl. null quantiles, source IDs, calculated decisions and nonclaims: `results/biodepth_2010_species_source_v0_1/guild_height_trait_label_null_verified_summary_v0_1.json`.
- Implementation: `scripts/analysis/test_biodepth_height_label_guild_null_v0_1.py`, GitHub Actions `.github/workflows/biodepth-guild-conditioned-height-label-null-v0-1.yml`.
- This result and its null contract live only in a **separate Draft PR (#48)** stacked above Draft #47 and original BIODEPTH #46. Nothing merged to `main`.
