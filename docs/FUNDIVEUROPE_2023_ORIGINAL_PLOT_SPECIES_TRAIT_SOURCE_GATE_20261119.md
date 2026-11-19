# Original source gate — FunDivEUROPE six-region plots (2026-11-19)

**STATUS: OUTCOME-BLIND SOURCE-ONLY CANDIDATE. No fitted ecological effect, K, FD or biomass coefficient may be opened in this lane.** This is a new candidate separate from the older BIODEPTH, Jena, TreeDivNet and previously failed Africa/BEF-China source audits.

## Verified external published catalogue (not yet file-content qualified)

- Source: Scherer-Lorenzen et al. (2023), *The functional significance of tree species diversity in European forests — the FunDivEUROPE dataset*, Dryad DOI **[10.5061/dryad.9ghx3ffpz](https://doi.org/10.5061/dryad.9ghx3ffpz)**, public version dated **2023-11-06**.
- Authors report **209 mature observational forest plots**, 30 × 30 m, in **six European countries** (Finland 28, Poland 43, Germany 38, Romania 28, Italy 36, Spain 36), **12,939 inventoried individual stems** assigned to species, **15 *target* tree species**, and an original plot-level aboveground tree biomass variable **Mg C ha−1**. These are **published descriptors**, not newly checked original file-row counts or proof of 30 original species or observed plot-specific trait coverage.
- Dryad landing page advertises exactly a small XLSX (`FunDivEUROPE_alldata_exploratory-platform_2023.xlsx`, ~162 kB) and README; workbook is described as **one plot per row** on worksheet `Data`, with variable definitions on `Metadata`. The paper reports *locally sampled dominant species leaves* but the public workbook may contain only **precomputed community-level summaries** rather than original tree×plot named leaf measurements.
- Official file direct link from the public landing page is `https://datadryad.org/downloads/file_stream/2691337`; its file identity must be checked against the public DOI/API metadata, its bytes capped, and original ZIP/XLSX headers inspected. If the source/API is inaccessible (including HTTP 403), **SOURCE_ACCESS_HOLD**, not invented coverage.

## Frozen source-qualification contract, BEFORE original file inspection

Reuse the original independent-forest study eligibility strictness specified in [PR #63](https://github.com/zuizui0223/turnover/pull/63), **without lowering it after source inspection**:

1. Original plot IDs: ≥**80** unique; ≥**5** genuinely distinct source forest groups with ≥**8** source-eligible plots each. The six countries are *candidate regions*, not independently published experiments; years or within-region plots are not independent studies.
2. ≥**30 named botanical species** source-verified, not merely 15 target taxa, and ≥**2 observed original species per eligible plot**; directly observed species×plot trait values for a common pair of traits (e.g. original SLA and leaf N) with ≥**80% source plant-species trait coverage** in the eligible plots, not derived CWM/FDis, TRY-imputed means or target-richness proxies.
3. Stand biomass and original trait date match within ≤**2 years**, with explicit original woody-stock units and no unnoticed C/NPP conversion; use one source plot once (not individual stems as independent stand outcomes). Verify measured local original traits vs species-wide literature values.
4. A direct new family-specific `K→FD→biomass` study requires, **in addition**, at least **12 non-overlapping families × 20 independently measured species** each, valid native phylogenetic tips, and source-level taxon/provenance mapping. The paper's **15 target species** cannot satisfy this by themselves, but the actual full raw source taxa count is not yet established.
5. **No biomass response fitting, FD coefficients or site-holdout prediction before source eligibility passes.** Existing source-derived FD vs standing stock may support a different explicitly pre-frozen *regional predictive* estimand in a later **new** lane, but neither direct species K/FD inference nor a universal law is authorized by this metadata audit.

## Bounded execution

The associated GitHub Action only requests the official public Dryad DOI/API and the page-advertised small XLSX. It checks original resource identity, byte limits, ZIP validity, worksheet header labels, approximate row grain, and whether an original species×plot observation table is actually included in the public file. It emits **nonraw source metadata** and an explicit HOLD/PREFLIGHT decision. It neither commits nor prints original biological rows, named original species, original plot IDs, trait values, or mass responses.

The external source page itself contains multiple ecological findings already published by the original authors; source and outcome reuse must not be labeled independent replication of those same findings.

## Stop conditions

- If source XLSX is plot summary only, record **PLOT_SUMMARY_ONLY_HOLD**, without reconstructing species measurements from derived indices.
- If initial source reveals no complete original taxonomic species×plot trait rows, stop before effects and do not retune variables or thresholds.
- If Dryad refuses unauthenticated original file access, record **SOURCE_ACCESS_HOLD** and stop rather than bypassing access controls.
- Do not alter the archived BIEN analyses, existing PR #62/#63 scientific source decisions, or PR #64 positive-evidence ledger.
