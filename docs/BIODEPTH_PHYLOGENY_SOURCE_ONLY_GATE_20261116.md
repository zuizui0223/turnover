# BIODEPTH × GBOTB: source-only, outcome-blind phylogeny eligibility (2026-11-16)

**Scope:** New exploration derived from BIODEPTH 2010 botanical-source / height-FD results (PR #46–48). These effects are already known; the upcoming tree crosswalk is source-only **before any new phylogenetic-distance, biomass, or prediction effects are opened**. This does *not* reopen the old preregistered 201-family BIEN×sPlotOpen source gate.

## Fixed data sources and identity

1. Original 2010 Hector et al. BIODEPTH Species dataset (5802 rows, original 480 sowing plots × 3 years, 103 unique Linnaean taxa) and SpeciesCodes. Exact original SHA256 already frozen in `audit_biodepth_103_taxa_gift_height_v0_1.py`.
2. Source-pinned plant tree V.PhyloMaker2 commit `7af3fb5152f691af2e4ec9d5e2e467d1b50505e9`, `GBOTB.extended.TPL` with 74,529 tips, original `tips.info.TPL` and `nodes.info.1.TPL`; S3 grafting scenario fixed. Reference Jin & Qian 2022, doi:10.1016/j.pld.2022.05.005. Do not change to a more favorable tree based on outcomes.
3. Original planting incidence and species list define the source population. No GIFT trait numerical observations, no biomass, and no FD or PD are read for this gate.

## Taxonomy normalization and fail-closed family rule

- Species accepted original BIODEPTH genus + epithet as exact binomial; convert spaces to underscores only for original GBOTB tip matching.
- Assign family by **a unique original backbone metadata genus→family association** in `tips.info.TPL`. A missing or multiple-family genus remains unmapped; **no approximate name matching, synonym replacement, or hand-curated source additions**.
- Before opening any tree-derived predictors, ensure no duplicate species, complete stable source SHA, nonnegative finite dated branch lengths, and exact package commit, tree and species provenance.
- Use source-native `phylo.maker(..., scenarios="S3")` with `output.sp.list=TRUE` to count `prune`, `bind`, `fail to bind`. Native-tip count is checked separately from the S3 tree.
- All tree-building endpoints are source/taxon coverage only. No outcome-driven choice of family or taxa.

## Pre-result source qualification

Minimum eligible structure to allow a *subsequent separately frozen* PD→FD→biomass exploration:

1. ≥70 of the 103 originally named species have uniquely mapped backbone families;
2. ≥60 original taxa are resolved by native S3 grafting, drawn from **≥6 distinct families**;
3. ≥25 are exact backbone-native species (avoid inference relying exclusively on grafted taxa);
4. among the 480 original planted plots, ≥200 retain ≥3 S3-resolved original species, including ≥6 original field sites each with ≥8 such plots.

These are scientific coverage thresholds, not significance cutoffs; **a PASS only authorizes a separate outcome-frozen study**. Do not lower them after viewing. Tree distance coverage in the historical *174 GIFT height-eligible plots* must also be evaluated before an actual FD/mass test; that is a further source-only matched-support gate, not silently assumed.

## Intended follow-up if source coverage passes

- First match the **same GIFT height-covered source-eligible species and planted communities** against the S3 tree, without accessing biomass response; require taxonomically complete tree coverage for ≥100 of the historical 174 plots across ≥5 independent sites and ≥3 phylogenetically resolved height-bearing taxa per plot.
- Freeze models/prediction score **before** opening new PD-matched effects. Compare leave-whole-site-out incremental prediction from mean-pairwise patristic distance, exact planted richness, source guild identities, mean log height, and one-axis observed height dispersion; treat repeated plot-years within each source site as non-independent.
- Distinguish **phylogenetic breadth** from family-specific **Blomberg's K** (this study does not estimate K). Site-holdout prediction is an association, not evolutionary rate, natural selection, causal FD or biomass mediation.

**Branch/merging boundaries:** This new source-only check is stacked over Draft PR #48, and no previous historical result or `main` is modified. The original high-density six-site BIODEPTH, BIEN×sPlotOpen 201-system and NEON auth gates stay HOLD.
