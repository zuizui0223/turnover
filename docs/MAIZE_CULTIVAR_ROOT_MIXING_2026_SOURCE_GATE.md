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


## Executed original 6-sheet/identifier audit — 2026-11-24

Official Zenodo original bytes **MD5 PASS** (no original source rows published). Original workbook has six worksheets with physical XML row-element counts **223/49/49/97/193/193**, and original headers were read as *string-only first row*:

- Sheet1 (candidate biomass): \`Site, Cul, T, sys, Cs, Block, Grain yield, Biomass\`.
- Sheet2 (published relative CE/SE): \`Site, sys, T, Block, rCE-GY, rSE-GY, rCE-AB, rSE-AB\`.
- Sheet3: \`Site, Row, Block, Comp, RRD_RWD, RRD_MRD, rCE_GY, rSE_GY, rCE_AB, rSE_AB\`.
- Sheet4: \`Site, Row, MoMi, T, Block, ΔMRD_D, rCE_GY, rSE_GY, rCE_AB, rSE_AB\`.
- Sheet5: \`Site, Sys, Row, Block, RSA, SRL, RLD, RWD\`.
- Sheet6: \`Row, Cul, T, Cs, Block, RWD, MRD\` (no same-name Site field).

**Pre-outcome original key qualification:**
- Sheet1 has **222 rows**, 96 distinct fully populated source \`Site×sys×T×Block\` candidate keys, two original Site values, and repeats consistent with multiple cultivar rows (but original \`Cul\` semantics not independently certified).
- Sheet2 has **48 rows**, 48 distinct full same-name keys, two Site values.
- The two tables share **2 Site codes, 4 sys codes, 3 block codes, 21 distinct Site×sys×Block combinations**.
- Critically, original \`T\` has **30 distinct codes in Sheet1, 9 in Sheet2, ZERO exact values shared**. Thus **0 of Sheet2's 48 full keys** match Sheet1 by exact same-name four-column tuple. This mismatch is an original **source-encoding / dictionary** obstacle, **not** a negative ecological finding.
- The apparent original Sheet1 cultivar-code multiplicity per candidate key is {1:48, 2:24, 4:15, 6:3, 8:6}; do **not** infer true planted richness (or fix unexpected 6) without author documentation.

Source-only explicit STOP: **\`SOURCE_BYTES_MD5_PASS_T_SOURCE_CODE_DICTIONARY_HOLD\`**. The original manuscript/data dictionary must independently establish whether and how \`T\` identifiers correspond; **do not** join on the weaker shared \`Site×sys×Block\`, guess \`T\` recoding or inspect original biomass/CE outcomes to choose a mapping. No numeric biomass, root trait, CE/SE response or modeling was opened.

Sources and reproducibility:
- Final original [Actions #45309532853](https://github.com/zuizui0223/turnover/actions/runs/45309532853) **SUCCESS** as a fail-closed source-only audit.
- Source-only artifact #14882471711, SHA256 \`c67ee37f3fc578144b2b81bb51523d4aa77d63f63e4f17224eaf67728f20e57e\`.
- [Persistent nonraw original source-only verdict JSON](../results/maize_cultivar_zenodo22655228_source_gate_20261124_v0_1.json).
- This programme remains **one cultivar experiment network** and must not enter the independent plant species-level 21-claim evidence registry or alter Evolution RC4.
