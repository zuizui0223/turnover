# turnover

General comparative programme on **how biological information is lost with separation**.

The repository asks:

> **Do the same biological properties predict how rapidly organismal traits and biotic interactions turn over across evolutionary time and geographic space?**

## Core design

| Biological state | Evolutionary separation | Geographic separation |
|---|---|---|
| organismal trait | trait memory loss | within-species trait spatial turnover |
| biotic interaction | partner-profile evolutionary turnover | interaction rewiring across space |

All four cells use one common effect convention: **null-centered distance–dissimilarity correlation**.

The programme is explicitly not flower-colour-specific. CHUN and FCP are motivating temporal/spatial proofs of concept only; their existing outcomes are not used to choose generalized traits, networks, predictors or thresholds.

## Frozen biological predictors

1. **Context heterogeneity** — candidate common driver of faster turnover on both axes.
2. **Ecological specialization** — candidate decoupler; opposite time/space effects are predeclared as biologically meaningful.
3. **Dispersal / mobility** — secondary decoupler expected to affect geographic turnover more strongly than evolutionary memory.

Biotic interaction type is an explicit moderator. Interaction turnover is decomposed into **species turnover** and **rewiring among shared/available species**; only rewiring enters the primary cross-axis interaction test.

## Start here

- Programme design: data/spatiotemporal_memory_turnover_design_v0_1.json
- Scientific programme: docs/SPATIOTEMPORAL_MEMORY_TURNOVER_PROGRAM_V0_1.md
- Source-first eligibility matrix: data/spatiotemporal_memory_turnover_source_matrix_v0_1.csv

## Source order

Trait arm:
1. BIEN 4.2 — generalized joint time-space route closed at spatial informativeness; later independent temporal-only studies use the already-qualified BIEN core
2. AusTraits independent transport — terminal structural HOLD under matched thresholds

TRY is not a third rescue source for the closed prospective programme; it remains only a future source-access possibility for a separately designed study.

Interaction arm:
1. Mangal curated networks — joint time/space route closed at species-rank support gate; retained only as non-primary spatial validation candidate
2. GloBI stable versioned archive — second and final primary source; terminal pre-outcome HOLD at source-semantic gate

No biological response is opened until source identity, schema/support eligibility and observed-geometry informativeness are frozen.

## Project boundary

This repository is independent of current submission claims in CHUN, FCP and IWE. Those repositories remain external anchors and are not silently modified by this programme.

## Current source-gate state

### Interaction arm — terminal pre-outcome HOLD

Mangal passed spatial-network and taxonomy-ID gates but failed the frozen species-rank joint gate: 7 programmes qualified versus 12 required. No interaction edge was opened. The finite-family contract therefore authorized one pre-outcome switch to GloBI.

GloBI then passed several increasingly strict gates:

1. Stable Zenodo archive identity (record 22691479, version 0.11): **PASS**.
2. Archive schema / aliases: **PASS** without row opening.
3. Structural support v0.4: **PASS** — 815 candidate systems -> 92 structural systems -> 62 sourceNamespace clusters.
4. Correct-grain support v0.5.2: **PASS** — 58 provenance-resolved programme blocks in 20 namespaces independently satisfy the same frozen 20-focal / 5-site-year / 10-repeated-focal thresholds.
5. Source-semantic / provenance gate v0.5: **HOLD**.

The terminal HOLD is fail-closed. Nine of the 20 remaining namespaces are definitively ineligible under rules frozen before any turnover outcome: occurrence/specimen/collection aggregators, a citizen-science aggregation, an IPT occurrence archive, or the GloBI mirror of the already-failed first source Mangal. Therefore at most 11 independent namespaces can remain, below the frozen requirement of 12.

No turnover, rewiring, distance-dissimilarity, phylogenetic, predictor-response or time-space coupling outcome was opened. The threshold is not lowered and a third primary interaction source is not introduced.

See: `docs/GLOBI_SOURCE_SEMANTIC_V0_5.md`.

### Trait arm — terminal pre-outcome HOLD

The trait arm also closes **before any generalized biological turnover effect is opened**.

BIEN source/schema qualification passed at exact patch **4.2.8**: 25,932,628 rows, required `agg_traits` fields present, and 54/54 expected trait names. It then passed three increasingly strict prospective gates under the frozen >=20 temporal species / >=8 spatial species / >=20 georeferenced records / >=5 25-km cells / >=12-family design:

1. **Structural support PASS** — 8,215 family × trait systems -> 1,705 temporal candidates -> **73 joint-support systems in 37 independent families**.
2. **State-validity PASS** — 73 -> **43 semantic-valid systems in 34 families**.
3. **Phylogeny crosswalk PASS** — 43 -> **39 systems in 31 families** under pinned V.PhyloMaker2 S3 plus the mandatory prune-only >=20 native-tip sensitivity.

The geometry-only informativeness gate then selected much more strongly:

4. **Temporal informativeness PASS** — 39 -> **24 systems in 21 independent families**, requiring both S3 and prune-only recovery of benchmark delta_rho=0.15 with median absolute recovery error <=0.10, directional recovery >=0.80, and valid-replicate fraction >=0.90.
5. **Spatial informativeness HOLD** — among those 21 temporal-PASS families, **11 independent families are already confirmed spatial HOLD** under the identical benchmark/recovery rules. Even if every unresolved family passed, at most **10 families** could remain, below the frozen requirement of 12.

That upper bound makes exhaustive completion unnecessary. The BIEN route is therefore **terminal pre-outcome HOLD** at spatial informativeness. The first spatial implementation attempts exposed two technical-only matrix/indexing bugs before any spatial scientific result; both are retained in the audit trail and fixed without changing generator, benchmark, pair set, thresholds, seeds, or coordinates. The terminal HOLD uses only corrected-run scientific results.

The predeclared independent transport, **AusTraits v7.0.0**, is independently terminal structural HOLD: after correcting its non-global `observation_id` to the source-faithful composite `dataset_id + observation_id`, the unchanged matched gate still produced only **10 joint-support systems in 3 independent families (Fabaceae, Myrtaceae, Proteaceae)** versus 12 required.

The finite source family is exhausted: BIEN + AusTraits were the two predeclared primary trait sources. **No third primary source is introduced, no threshold is lowered, and the frozen real-effect design is not executed.** TRY v7 remains a future source-access HOLD rather than a rescue route for this prospective programme.

For trait-time and trait-space, the complete label-permutation null has also been simplified analytically before outcomes: with all unordered pairs and whole-state label permutations, the exact expected Spearman correlation is zero. Thus the canonical trait `delta_rho` equals observed Spearman `rho`; permutations are retained only for null dispersion and implementation diagnostics, not to Monte-Carlo-estimate the null mean.


## Independent temporal follow-up

The generalized time-space programme above remains terminal pre-outcome HOLD and was not relaxed. A separate prospective temporal-only follow-up asked whether **phylogenetic trait-memory loss is primarily trait-specific or lineage-specific**.

This follow-up remained outcome-blind through all system-selection gates:

- temporal structural support: **1,455 systems / 240 families / 49 traits**;
- semantic validity: **1,219 systems / 219 families / 47 traits**;
- S3 + prune-only phylogeny crosswalk: **802 systems / 160 families / 47 traits**;
- necessary pre-informativeness crossed core: **722 systems / 120 families / 25 traits**;
- temporal known-truth informativeness: **255 systems / 70 families / 22 traits**;
- final crossed degree/connectivity core: **201 systems / 45 families / 12 traits**, one connected bipartite graph.

The final pre-outcome gate tested whether that realized 201-edge graph could recover a predeclared twofold trait-vs-family variance architecture before any real family × trait memory-loss rho was opened. Directional recovery was adequate (trait-dominant 0.833; lineage-dominant 0.886), but the median absolute error of the log variance ratio was **0.442–0.452**, above the frozen maximum **0.35**.

Therefore the trait-dominant versus lineage-dominant variance-ratio question is **terminal pre-outcome HOLD**. Real memory-loss rho was not opened, the precision threshold was not relaxed, and no outcome-driven family/trait deletion was performed.

The qualification trail is retained because it identifies a broad and well-connected temporal trait matrix while also showing that the crossed graph is not precise enough for the predeclared twofold variance-ratio classification.


## Independent temporal repeatability and portability follow-ups — completed

The earlier temporal trait-vs-lineage **variance-ratio** follow-up remains terminal pre-outcome HOLD: the 201-system crossed graph could recover direction but not the predeclared precision of a twofold variance-ratio contrast. That result was not relaxed.

Three separately prequalified analyses were then completed on the exact same fixed core (**201 systems / 45 families / 12 continuous traits**). Three independent real-effect pipelines reproduce the S3 and prune-only rho values exactly.

### Repeatability decomposition

Crossed REML without a dominance comparison:

- **R_family = 0.1504** (95% bootstrap CI 0.0204–0.2861)
- **R_trait = 0.0433** (0–0.1335)
- **R_residual = 0.8063** (0.6600–0.9522)

Prune-only sensitivity is similar: family 0.1482, trait 0.0207, residual 0.8312.

These are separate repeatability shares only; the repository does **not** infer that family effects are statistically larger than trait effects.

### Cross-lineage portability of trait identity

Leave-one-family-out prediction asks whether the same trait in other families improves prediction over a global training mean.

- S3 portability gain = **−0.0242**, blocked-permutation p = **0.091**
- prune-only gain = **−0.0324**, p = **0.193**

The frozen robust portability criterion fails on both trees. Trait identity therefore does not robustly transport the memory estimate to a held-out family on this graph.

### Conditional lineage repeatability

After giving every trait its own fixed mean, family identity retains:

- S3 conditional family repeatability = **0.1825**
- 95% bootstrap CI = **0.0285–0.3369**
- prune-only = **0.168**
- leave-one-trait / leave-one-family estimates = **0.1205–0.2268**

The interval spans the predeclared 0.10 practical reference, so the frozen classification is **uncertain relative to 10%**.

## Integrated temporal synthesis

The completed temporal follow-ups now support one coherent ecological result on a prospectively qualified core of **201 family × trait systems, 45 vascular-plant families and 12 continuous traits**.

Across systems, the phylogenetic memory gradient — Spearman association between patristic separation and trait-state dissimilarity — is usually positive but highly heterogeneous (S3 mean **0.093**, median **0.053**, positive in **74.6%** of systems). S3 and backbone-native prune-only estimates are strongly concordant (Spearman **0.832**).

Three independently qualified analyses then separate different meanings of “generalization”:

1. **Crossed repeatability:** family identity accounts for an estimated **15.0%** of variation in memory strength (95% bootstrap CI 2.0–28.6%), trait identity **4.3%** (0–13.4%), and **80.6%** remains family × trait-specific/residual. These shares are not used for a family>trait dominance test.
2. **Cross-lineage portability:** knowing how the same trait behaves in other families does **not** robustly improve prediction for a held-out family (S3 gain **−0.024**, p=0.091; prune-only **−0.032**, p=0.193).
3. **Conditional lineage repeatability:** after every trait receives its own mean, family identity still carries an estimated cross-trait repeatability of **0.183** (95% CI 0.029–0.337; prune-only 0.168; leave-one-out range 0.121–0.227), although uncertainty spans the predeclared 0.10 practical reference.

The resulting biological conclusion is deliberately narrower than “lineages dominate traits”:

> **A trait can show real phylogenetic memory within a plant family without carrying a portable memory strength to another family. The relevant unit of generalization is therefore closer to a trait-in-lineage context than to the trait label alone.**

This places the result beyond a generic statement that phylogenetic signal varies among clades. The predictive result is that a memory estimate learned for trait X in one set of families is not automatically a useful prior for trait X in a new family, while lineage context retains a modest recurring signature across different traits.

The response is called a **phylogenetic memory gradient** rather than a decay rate: it measures the monotonic erosion of pairwise trait similarity with patristic separation and is not an OU alpha, evolutionary rate, half-life, or universal replacement for K or Pagel's lambda.

Mechanisms are not identified here. Prospectively testable candidates include whole-organism life-history context, lineage-specific developmental/genetic constraint, clade-specific environmental occupancy, and residual measurement/taxon-composition heterogeneity. Those require new held-out-family tests rather than post-hoc explanation of the present 201 systems.

The full synthesis and claim boundaries are in:

- `docs/TRAIT_MEMORY_CONTEXT_SYNTHESIS_V0_1.md`
- `docs/TRAIT_MEMORY_CONTEXT_MANUSCRIPT_V0_1.md`
- `results/trait_memory_context_synthesis_v0_1/result.json`
- `results/trait_memory_context_synthesis_v0_1/effect_identity.json`
