# Manuscript skeleton — Plant trait phylogenetic memory spectrum

Status: **pre-outcome narrative freeze**. No real family × trait memory-loss rho has been opened.

## Working title

**Is evolutionary memory a property of traits or lineages? A crossed decomposition across vascular plant families**

Alternative descriptive title:

**Crossed trait and lineage effects structure phylogenetic memory across vascular plants**

No title may claim trait-dominant, lineage-dominant, or mixed architecture until the frozen variance-partition result is opened.

## Core gap

Comparative studies often ask whether a particular trait is phylogenetically conserved, or compare phylogenetic signal among traits. Those approaches leave a crossed question unresolved: when the same trait is measured in many independent plant families and each family contributes multiple traits, does the persistence of trait similarity through evolutionary divergence travel mainly with the **trait identity** or with the **lineage context**?

The distinction matters because the two architectures imply different generalizations.

- Under a trait-dominant architecture, a trait has a characteristic evolutionary memory gradient that transfers across lineages.
- Under a lineage-dominant architecture, families impose broadly conservative or labile evolutionary regimes across multiple traits.
- Under a mixed architecture, neither axis can be treated as a portable predictor by itself.

## Primary question

Across a crossed matrix of vascular-plant families and traits, how much variation in phylogenetic memory loss is attributable to trait identity versus family identity?

## Response

For each admitted family × trait system:

`memory_loss_rho = Spearman(patristic separation, trait-state dissimilarity)`

with all unordered species pairs.

- Continuous traits: species state = median; dissimilarity = absolute difference.
- Nominal categorical traits: species state = unique mode; dissimilarity = 0/1 mismatch.
- Larger positive rho means faster loss of trait-state information with increasing phylogenetic separation.
- The exact whole-state permutation-null mean is zero, so rho is already the null-centered effect.

## Prospective qualification

Admission is determined without real memory-loss rho:

1. >=20 species.
2. Semantic validity.
3. S3 resolvable >=20 and backbone-native prune-only >=20.
4. Known-truth recovery of benchmark rho=0.15 on both S3 and prune-only geometry.
5. Final crossed graph: family degree >=2, trait degree >=5, >=12 families, >=4 traits, one connected component.

The previous generalized time-space programme is not used to choose systems and remains terminal pre-outcome HOLD.

## Primary analysis

Crossed random-intercept REML:

`rho ~ 1 + (1 | family) + (1 | trait_name)`

Primary variance components:

- `sigma²_family`
- `sigma²_trait`
- `sigma²_residual`

Primary contrast:

`log(sigma²_trait / sigma²_family)`

with 2,000 fixed-seed parametric bootstrap replicates.

Decision language is frozen:

- CI entirely > 0: **trait-dominant architecture**
- CI entirely < 0: **lineage-dominant architecture**
- CI overlaps 0: **mixed architecture**
- both crossed variances at zero: **unstructured at the family/trait level**

These labels describe the variance architecture only; they do not imply a universal mechanism.

## Mandatory sensitivity

Repeat the identical crossed model using prune-only rho on the identical admitted family × trait set.

The prune-only result is a robustness analysis for taxonomy-inserted tips, not a second opportunity to select systems.

## Secondary analyses

Semantic-class fixed effect is estimated only if both continuous and categorical classes satisfy the predeclared representation rule.

Pre-annotated biological modules (leaf, stem/xylem, root, reproductive, whole-plant) are descriptive. They cannot change the primary admission set or primary trait-vs-family variance conclusion.

## Results template

### Qualification

Report, in order:

- structural systems / families / traits;
- semantic-valid systems / families / traits;
- phylogeny crosswalk systems / families / traits;
- pre-informativeness necessary core;
- informativeness-PASS systems;
- final crossed-core systems / families / traits.

Do not describe a gate failure as a biological null.

### Memory-effect distribution

Report the distribution of admitted system rho values without ranking families or traits as a primary result.

### Crossed variance architecture

Report all three variance components, variance shares, log variance ratio, and bootstrap interval.

Insert only the one frozen architecture label implied by the interval.

### Prune-only sensitivity

Report whether the variance architecture classification changes under backbone-native tips only.

## Discussion template

1. **What carries evolutionary memory?** Interpret the frozen variance decomposition.
2. **Portability across clades.** State what the family variance implies for transferring trait-level expectations among lineages.
3. **Portability across traits.** State what the trait variance implies for using trait identity as a general predictor.
4. **Why crossed replication matters.** Contrast the design with one-trait-across-tree or one-clade-many-traits studies.
5. **Measurement frontier.** Distinguish temporal evolutionary memory from the separately failed geographic joint programme.
6. **Limits.** BIEN coverage, S3 taxonomy-inserted tips, family-level scale, observational trait aggregation, and the benchmark-recovery gate.

## Hard language constraints

Never write that the failed spatial programme demonstrated weak spatial turnover. It demonstrated insufficient predeclared informativeness across enough independent families.

Never reinterpret excluded systems after observing their real rho.

Never promote module-level patterns to primary hypotheses in this version.

Never change the trait/family degree requirements, benchmark rho, recovery thresholds, or source after real memory effects are opened.
