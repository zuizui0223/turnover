# Source-first independent mechanism analogue: maize cultivar root-trait mixing (2026-11-24)

**Source ID:** Su, Ye et al. (2026), [Zenodo DOI 10.5281/zenodo.22655228](https://doi.org/10.5281/zenodo.22655228), version 1.0.0 (2026-09-08). Original file \`experimental data.xlsx\`, Zenodo manifest MD5 \`26308df4b66c10527749ccb8bfa50bc9\`, approximately 65 KB.

## Why it is considered, and why it does NOT replicate the main question

The source description reports **two distinct Chinese field locations (Zhangye, Lishu)**, original pure stands and mixtures of up to **eight *maize cultivars***, original aboveground biomass/grain yield, cultivar-specific root weight density/root depth, and published relative complementarity and selection estimates. This is a potentially useful **within-species mechanistic analogue** for the separation of (a) intrinsic root-trait dissimilarity prior to mixture and (b) neighbor-induced root trait plasticity. It has no independent phylogenetic **family** or plant **species** variation, so it is NOT a direct test of BIEN/AusTraits K/rho→plant-community FD→biomass. Never combine its cultivar observations with cross-species FD or call the two locations independent global BEF experiments.

The article/dataset explicitly already describes associations between root responses and overyielding; do not represent a replication of the authors' primary conclusions as a new finding. Any new model would be retrospective, and requires a separately frozen **original-observation admission gate** after original source rows and source semantics are verified.

## This commit: predeclared no-outcome source-only gate

- Record ID, DOI and exact published file identity pinned to official Zenodo public API and exact source MD5; no authentication, third-party mirror, credential use or license assumption.
- Max 1.5 MB original file read anonymously on ephemeral CI runner. CSV/spreadsheet **raw files not committed or redistributed**.
- A stdlib XLSX package metadata reader scans only first 8 rows of *string* cells for structural labels (site/plot/cultivar/treatments/traits/biomass/CE–SE). **No numeric response cells opened, summarized or fitted.** It exports only sheet names, counts and a predefined token vocabulary. Original source numeric values, plot names and cultivar identities are not written to artifacts.
- Synthetic parser tests must pass before any source request. CI **SUCCESS does not mean ecological source PASS**: the result explicitly returns ACCESS_HOLD, SCHEMA_HOLD or MD5-validated-with-grain-unverified.
- The source original data are **ineligible for biological-effect modeling** until original site, subplot, block, year, planned cultivar composition, monoculture yields, physical biomass units, *pre-mixture* root trait values and any originally derived CE/SE definitions are all demonstrated on the same source grain. Original relative complementarity/selection cannot be assumed equal to signed Loreau–Hector CE/SE or \`NDE = CE + SE\`.
- Match original experimental design, not two independent measurement years or two independent publications. If each site has insufficient within-richness cultivar combinations or complete baseline rank, stop. In a two-site leave-one-site-out test there are only **two** folds and no honest global generalization CI. Likewise, retrospective post-mixture root response cannot be used as though it were preplant assigned FD.

**Conservative decision at freeze:** source candidate, not a positive effect. Do not change RC4, Jena TBE, BIODEPTH, TreeDivNet, Chen, Cadotte or any HOLD statuses.

## Source-screen alternatives already filtered without additional outcomes

- **Saito et al. 2026** [Functional Ecology](https://doi.org/10.1111/1365-2435.70325): IDENT-Freiburg experimental trees are within **TreeDivNet** (paper Methods 2.3), which overlaps existing original research programmes; **not** new independent network replication merely because it is a 2026 article.
- **Ceballos-Núñez et al. 2025** [Oikos](https://doi.org/10.1002/oik.11251): virtual biodiversity experiment (six simulations); useful theory, **not field experimental biomass replication**.
- **Ndayambaje et al. 2026** [Dryad](https://doi.org/10.5061/dryad.v15dv42c0): green-roof original mix/mono and traits, but primary ecosystem responses are **cover/temperature/assimilation**, not the required measured physical annual dry biomass. Do not substitute cover for biomass.
- **Pan et al. 2026** [Journal of Ecology](https://doi.org/10.1111/1365-2745.70306), [Zenodo](https://doi.org/10.5281/zenodo.18483939): BioCliVE grassland experiment reports productivity **temporal stability/asynchrony** and measured leaves in 2022 after 2018 establishment. Not a source-qualified original *premixing* FD→signed NDE→biomass design without further source evidence.

**Future qualified mechanism test only (not run here):** within each source site and planned cultivar richness, does directly observed pre-mixing depth dissimilarity predict absolute biomass and **source-defined** mixture excess equally well after composition baselines, and is the *incremental* out-of-site gain direction concordant? No causal FD-only claim without a design that varies FD independently of cultivar identities. Keep a separate within-cultivar evidence tier and never merge it into the 21-entry original species-level evidence registry automatically.

**Audit program:** \`python scripts/source/audit_maize_cultivar_zenodo22655228_source_v0_1.py --selftest\` and \`--source\`.
