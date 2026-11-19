# Nonpositive BIEN trait-value audit — Stage A interpretation

Status: **Stage A complete; no memory effect recomputed**

## Why this audit was necessary

The v0.3 robustness programme could not execute its mandatory all-201 natural-log sensitivity because 25 primary-tree systems and 18 prune-only systems contained at least one species median <=0.

For plant height, diameter, leaf area, dry mass and seed mass, a nonpositive realized measurement is not merely a logarithm inconvenience: it can indicate invalid raw coding and can therefore contaminate the raw-scale memory gradient itself.

Stage A re-queried all 201 frozen family x trait systems under the exact BIEN 4.2.8 extraction contract without recalculating rho.

## Identity gate

The audit exactly reproduced the original v0.3 blocker:

- S3 systems with a nonpositive species median: **25**
- prune-only systems with a nonpositive species median: **18**

The per-system counts match the v0.3 robustness artifact exactly.

## What the raw data contain

Across 26,112 audited species states:

- 206 species have median <=0;
- all 206 medians are **exactly zero**;
- 141 species are zero because every admitted raw record is zero;
- 65 have mixed positive/zero raw records but a zero median;
- no species has a negative median;
- 443 species contain at least one raw value <=0, including 237 whose median remains positive.

Raw nonpositive records occur only in the five traits declared positive-only before Stage A outcomes were opened:

| Trait | Species median <=0 | Species with any raw <=0 | Raw zeros | Raw negatives |
|---|---:|---:|---:|---:|
| whole plant height | 197 | 229 | 8,858 | 1 |
| diameter at breast height (1.3 m) | 1 | 188 | 2,786 | 0 |
| leaf area | 4 | 17 | 23 | 0 |
| leaf dry mass | 1 | 4 | 109 | 0 |
| seed mass | 3 | 5 | 61 | 0 |

The only negative raw value is **whole plant height = -3 m**.

The other seven continuous traits contain **zero** raw nonpositive records in the frozen 201-system population.

## Unit and provenance pattern

No contaminated species has mixed units.

Nonpositive records use the ordinary expected units:
- height: m;
- DBH: cm;
- leaf area: mm2;
- leaf dry mass: g;
- seed mass: mg.

Thus the blocker is not explained by within-species unit mixing.

Provenance patterns differ by trait:

- 99.73% of nonpositive whole-plant-height records have missing BIEN source metadata;
- 99.57% of nonpositive DBH records have missing source metadata;
- all 23 zero leaf-area records come from the LEDA database;
- all 109 zero leaf-dry-mass records come from published-paper imports;
- all 61 zero seed-mass records come from published-paper imports.

Examples include 0 g leaf dry mass, 0 mg seed mass and 0 mm2 leaf area, which are outside the admissible physical measurement domain.

## Data-validity conclusion

The v0.3 log blocker is a **raw-data validity problem**, not only a transformation problem.

The contamination is overwhelmingly exact zero coding in strictly positive size/mass traits. Because these same values entered the frozen raw species medians and 49 systems contain at least one raw nonpositive record, the raw-scale rho values must be impact-audited before submission.

## Stage B

Stage B is frozen in `data/trait_memory_positive_only_cleaning_impact_design_v0_2.json`.

Cleaning rule:
- only the five Stage-A predeclared positive-only traits are affected;
- raw numeric values <=0 are excluded before species medians are calculated;
- no source/citation is deleted;
- no offset, replacement, winsorization or trait-specific threshold is allowed;
- 49 contaminated systems are re-extracted;
- the other 152 systems inherit the immutable v0.3 effects exactly.

If all 201 systems retain >=20 species on both tree treatments, the positive-only extraction becomes the scientifically valid primary data contract **regardless of whether it strengthens or weakens the current manuscript conclusion**.

If any system loses support, submission is HOLD and the population must be re-scoped before any replacement primary analysis.

## Editorial consequence already accepted

The current title phrase **“rather than trait-intrinsic”** is stronger than necessary given the broad family/trait heterogeneity intervals.

The next manuscript RC should use a non-dichotomous title such as:

**Phylogenetic trait memory is lineage-contingent, with little transferable trait-level signal across plant families**

This wording change does not depend on the Stage B outcome.
