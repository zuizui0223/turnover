# BioCON 2021 August: retrospective secondary-SLA candidate FD vs absolute biomass and signed net diversity effect

2026-11-24, one study only; new analysis based on previously published data, not a new independent field experiment. See [original pre-outcome freeze](BIOCON_E141_2021_SECONDARY_SLA_FD_NDE_PREDICTION_FROZEN_20261124.md) and [nonraw numeric result](../results/biocon_e141_2021_secondary_sla_fd_B_NDE_composition_holdout_v0_1.json).

## Executed original-source results

Exact original author [Huang et al. Figshare v3](https://doi.org/10.6084/m9.figshare.26841637.v3), original MD5 8185b8effca37c8740ad065c53eb75d2; 2021 **August** same-site matched source aboveground total dry mass g/m². Original sources provide 16 planted species flags, 46 qualified independent physical *mixture plots* with 46 unique original sown compositions (4 species=36, 9 species=10), six original CO2 whole rings and exact same-year/season/CO2/N single-species control baselines, 2 physical mono replicates per plant species×treatment. Seed mass originally equal across sown species. Extra water/warming subexperiment excluded. Underlying native-source-candidate leaf trait data from [Ohlert et al. 2024](https://doi.org/10.1371/journal.pone.0306342) pooled 1998–2020 **monoculture** observations and supplied processed treatment-specific SLA means; two taxa substituted with neighboring Big Bio E120 are **excluded**. Direct EDI 538 original observation-year file remains **HTTP403 HOLD**: this is a distinct **secondary-data, single-year retrospective** sensitivity, not an upgrade of the primary E141 direct trait-source programme.

Within the **same 46 original plots and composition-heldout folds**, model M0 uses sown richness, treatment N, Ring fixed effects and original-secondary 14-candidate species CWM log SLA. M1 adds equal-weighted, one-axis Rao-type absolute pairwise difference in log SLA, using only source-candidate native E141 species; 46/46 source geometry rank tests passed **before biomass effects**. Predict held-out original sown species **composition**, not repeated measurements. Six CO2 ring total weights are equal and original CWM/FD standardization is training-fold only.

### Out-of-original-sown-composition SSE improvement

| Original outcome | Additional FD predictive gain | Approximate 95% 6-ring bootstrap interval |
|---|---:|---:|
| Absolute 2021 August aboveground biomass B | **−3.89%** | **−35.72% to +12.15%** |
| Signed mono-relative NDE = B−E | **−9.09%** | **−64.49% to +15.85%** |
| Difference in gain, NDE minus B | **−5.20 percentage points** | **−30.85 to +3.71 pp** |

Both endpoint model improvements are **negative point estimates** and all three uncertainty intervals contain 0. Thus neither a beneficial heldout FD increment nor hypothesized NDE-specific transport advantage is supported **in this exact limited comparison**. No negative causal biological effect of FD is established. The single-mono-reference sensitivity gave NDE predictive gains of **−9.05%** using the first mono reference and **−8.85%** using the second. These are NOT confidence intervals or a substitute for full monoculture variance propagation.

Uncertainty: the documented 2,000-draw bootstrap resamples **original CO2 whole rings** 3 ambient + 3 elevated, based on **fixed out-of-fold errors** and without full model refits or full mono/leaf-trait uncertainty. Six rings cannot justify broad statistical precision, and 46 physical plots/46 planted composition units are not independent experiments.

Actual original source run [GitHub Actions #45318673580 PASS](https://github.com/zuizui0223/turnover/actions/runs/45318673580), PR replay [#45318678169 PASS](https://github.com/zuizui0223/turnover/actions/runs/45318678169). Nonraw workflow artifact #14886832240 SHA256 6af478af87b45f65b6e5f0ace92e268bc5f793a272dbcf03bf3781727a91a30e. No individual source biomass observations, original trait values, taxon values, plot IDs, or raw rows were published in this analysis branch.

## Scientific boundary

1. **No universal FD effect:** adding an extra FD predictor to a previously selected, source-qualified 2021 sample can worsen held-out SSE even while FD has biological relevance to resource partitioning. The original source used only *one* trait axis and 14/16 native candidate measured taxa and is a same-site 2021 temporal subset.
2. **No FD-specific causal intervention:** original species composition determines candidate FD; assigning richness and species combinations does not isolate a continuous FD-only manipulation. Treatment effects were previously published by Huang et al. 2025, and this retrospective analysis is not a second independent experiment.
3. **No family K/ρ mediation:** 16 source species within this field are not a qualifying original multi-family evolutionary memory design and cannot be joined to BIEN/AusTraits trait memory to claim K→FD→NDE→biomass.
4. **No negative ecological null:** negative prediction gains and intervals overlapping zero do not demonstrate that a biodiversity mechanism is absent, nor do they contradict other experimental mixture richness total effects.
5. **Original parent 24-year EDI trait-source gate remains HOLD** after a verified official EDI 538 v9 HTTP403 request, and original direct observation-year records were not recovered. Post-result tuning of richness, SLA metrics, outcome transforms, thresholds or split groups is prohibited for this programme. The hypothesis that FD generalizes better to NDE than absolute mass **does not gain affirmative support**.

### Exact interpretation to carry forward

Source-credible established statement: *The 2021 within-site native-source-candidate SLA-FD increment did not improve planted-composition held-out prediction of either absolute aboveground mass or signed mixing gains, and NDE-over-absolute advantage was not supported.* 

Strong biological / journal claim not established: *Family-specific evolutionary memory changes functional diversity, thereby causally changing complementary resource use and biomass across ecological systems.*

Maintain the verified Evolution RC4 trait-memory study as scientifically separate from this secondary same-field FD/B negative predictive increment. No main branch or prior results should be rewritten or auto-merged as new independent replication.
