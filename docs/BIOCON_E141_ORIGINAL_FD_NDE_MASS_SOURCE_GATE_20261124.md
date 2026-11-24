# Independent BioCON E141 site experiment: original FD→mixing effect→biomass source gate

**Source selected without seeing any new outcome scores: 2026-11-24.**

## Original provenance and previously published results

- The **Cedar Creek BioCON E141** grassland experiment in Minnesota is **not E120**, the Cedar Creek teaching-source experiment already audited in turnover PR #44. Its original design contains **296 main plots** with randomly assembled communities of **1/4/9/16** of 16 sown species in **six whole-plot CO₂ rings**, plus **63 functional-group design subplots** and **12 bare plots**, totaling **371 plots**. CO₂ is whole-ring, not plot-randomized; N and planted diversity are subplot factors. 1997 sowing, with multiple biomass survey years.
- Original source: https://cedarcreek.umn.edu/research/experiments/e141 and EDI **knb-lter-cdr.302** (original aboveground biomass), **.301** (species cover). Original experiment treatment table is separately linked on the original E141 site; a plot×species sown-composition crosswalk has **not yet** been source-verified.
- Already published *Nature Communications* 2025 original study Huang et al. DOI **10.1038/s41467-025-62691-0**, original Figshare **10.6084/m9.figshare.26841637.v3**, reports a 24-year E141 data analysis with known positive richness→production/complementarity effects and N×CO₂ interactions on CE/SE. This is **previously published evidence**, not a new finding or a prospective first-look independent replication. Do not re-report those effects as ours.

## Pre-outcome question and research scope

Only after original grain and traits pass: within E141's **one study**, can species-dispersed monoculture-derived trait FD add *out-of-assigned-species-composition* incremental predictive information to **signed NDE/CE/SE** and to **absolute annual aboveground biomass**, beyond richness, CWM and known treatments? Does this comparison change under nutrient enrichment or elevated CO₂? This is an **exploratory within-experiment** generalization test; original conditions are not independent experiment sites, and CO₂ has **six whole-ring experimental units**, not hundreds of independent randomized plots. There is **no** direct K→FD mediation with 16 species, and a single experiment can **never** establish cross-biome transport.

## Outcome-blind source gates

1. **Official original source access:** require exact Figshare article ID, version **3** and official original file inventory, and two EDI package EML manifests .301/.302. Extract only original metadata and **column names** at this stage. No raw numeric response/species/trait values or copyrighted source rows exported.
2. **Original identity:** source-authorized E141 rather than E120; unique **physical ring×plot ID×calendar year×CO₂/N treatment**, original sown species rather than observed-only cover, exact planted richness (1,4,9,16), and distinguish main randomly assembled **296** from the nonrandom species composition of **63** functional diversity additions, **12** bare plots, and later TeRaCON subsample.
3. **Expected monoculture biomass and CE/SE:** For each mixture/year/CO₂/N, original species monoculture responses must exist at matching context with sufficient original replicates. The accepted CE and SE formula must be audited, including whether any published CE/SE columns already derive from the source response (to avoid an algebraic predictor leak). Never use the same mixture in training and held-out validation through repeated years.
4. **Trait eligibility:** from **actually observed** per-species measurements outside mixtures, not post-treatment plasticity/imputation/functional-group labels. Original 2001 SLA is **after 1997 sowing** and cannot silently be called preplant; source/year measurement ordering and treatment alignment need explicit validation. Without source-direct species trait data, cannot compute a legitimate new FD effect.
5. **Evaluation and causal scope:** Only if the above are qualified, freeze a fixed target (equal-plot/whole-composition heldout SSE comparing baseline richness,CWM,CO₂/N,ring/year to plus-FD). Treat treatment assignments as randomized total effects subject to ring/block structure, but FD is a derived property of assigned species composition, not independently randomized. No FD-only causal mediation without additional design/identification assumptions. Distinct published 2025 CE/SE results are **not independent biological confirmations**.

## Hard stop

Do not alter original E120, TreeDivNet, BIODEPTH, Jena TBE, Chen, Cadotte, original BIEN 201 systems or Evolution RC4. Do not mine 24 years as 24 independent field experiments. If official download/auth fails, original sown-composition unavailable, original source plot/year joins differ, or trait measurements not eligible, record **SOURCE_HOLD**, do not lower thresholds and do not fit any new biological outcome.

Original official-source metadata preflight: `python scripts/source/audit_biocon_e141_figshare_edi_v0_1.py --selftest` and `--source`.
