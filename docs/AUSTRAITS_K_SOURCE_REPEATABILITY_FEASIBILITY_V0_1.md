# AusTraits K: source-replicate feasibility (2026-10-08)

**Status:** source-data audit completed, **not** an observation-error evolutionary null. [Successful audit workflow #37783083851](https://github.com/zuizui0223/turnover/actions/runs/37783083851), artifact `austraits-k-source-replicate-feasibility-v0-1`.

The eligibility rule was frozen before inspecting this coverage output in `data/austraits_k_source_repeatability_feasibility_v0_1.json` (but **after** empirical K and common-OU outcomes). This audit preserves the original 254 family×trait systems / 42 families / 13 traits, positive-numeric source-native units and species-level median eligibility. A repeated observation requires distinct `dataset_id` plus `observation_id`; across-dataset replication requires distinct `dataset_id` for the same species and trait. No observed K, family ICC or cross-family rank gain was analyzed in this source audit.

## Fixed outcome

**12 of 13 named traits qualify** under the frozen coverage rule: at least 30 species with records in multiple datasets, and at least three families each contributing at least five such species. Only `seed_height` fails the family-spread requirement. This is feasibility to calibrate source-associated variation, *not* proof of reliably measured instrument error.

| Trait | Matched species×system cells | ≥2 independent observation records | ≥2 datasets | Families with ≥5 multi-dataset species | Feasible |
|---|---:|---:|---:|---:|---|
| fruit_height | 855 | 302 | 296 | 4 | Yes |
| fruit_length | 7,215 | 3,092 | 3,071 | 29 | Yes |
| fruit_width | 3,708 | 1,501 | 1,492 | 16 | Yes |
| leaf_area | 1,712 | 692 | 493 | 6 | Yes |
| leaf_length | 12,495 | 7,019 | 6,940 | 40 | Yes |
| leaf_mass_per_area | 1,081 | 680 | 429 | 5 | Yes |
| leaf_width | 11,878 | 6,439 | 6,352 | 38 | Yes |
| petiole_length | 2,529 | 714 | 692 | 18 | Yes |
| plant_height | 13,053 | 8,666 | 8,612 | 35 | Yes |
| seed_dry_mass | 4,242 | 1,894 | 1,317 | 15 | Yes |
| seed_height | 455 | 74 | 56 | 2 | **No** |
| seed_length | 4,596 | 2,246 | 2,224 | 21 | Yes |
| seed_width | 2,511 | 645 | 623 | 17 | Yes |

Note: cell totals count each system's species, not unique species across traits. Dataset replication is not necessarily independently repeated measurements of a shared individual; same-species variation also contains environment, phenology, population heterogeneity, protocol and source effects.

## What this does and does not change

- **Unchanged:** original rho failure to replicate a portable trait hierarchy; empirical K portability; exact-tree Brownian and three shared-OU null outcomes.
- **Now feasible:** estimate source-replicate dispersion *without using observed K* as the target, and ask in a separate matched-tree simulation whether this variation alone could produce the portable K trait ranking.
- **Not licensed:** assign each same-species cross-source difference entirely to instrument measurement error; calibrate noise parameters to observed K; remove a trait post hoc based on its observed K; claim homogeneous OU has been universally excluded.
- **Critical design problem for the next step:** preserve exact matched family×trait graph when assessing 12 adequately replicated traits, and explicitly separately handle `seed_height`; use source-derived noise scenarios/uncertainty without tuning to K. A graph-specific observation-error null must be newly frozen **before its outcomes**, and is exploratory after original K/OU results.
- The highest-attraction shared-OU family ICC result was borderline (c=4, S3 observed 0.5306 vs null q97.5 0.5253 and p=0.0272), so the strongest stable claim remains the inability of *these independent homogeneous models* to explain trait-name K rank predictive gain. The family-ICC claim requires more caution.
