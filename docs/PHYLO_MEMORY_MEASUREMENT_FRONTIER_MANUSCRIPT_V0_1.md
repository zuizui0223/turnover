# Manuscript skeleton — The phylogenetic-memory measurement frontier

## Working title

**Known truth is not automatically assignable in simulation-based power studies**

Alternative:

**Equal phylogenetic memory signals are not equally assignable across trait representations**

## Question

If the true distance–dissimilarity association is held constant, which properties of a real comparative sampling design determine whether that signal can actually be recovered?

This is an outcome-free methods study. It uses only known-truth simulations on real family × trait phylogenetic geometries. No observed trait-memory rho enters any result.

**Central claim:** a requested simulation truth must be shown to be structurally realizable and generator-accessible before downstream failure can be interpreted as low statistical power (Fig. 1). A journal-neutral abstract is frozen in `docs/PHYLO_MEMORY_ABSTRACT_V0_1.md`.

## Data geometry

722 prequalified BIEN family × trait geometries:
- 120 plant families
- 25 traits
- S3 and prune-only tree treatments
- 443 continuous-scalar systems
- 279 nominal-categorical systems

Every system is challenged with the same benchmark Spearman rho = 0.15 and the same frozen recovery criteria.

## Main result 1 — recoverability is representation-dependent

Overall: 255/722 = 35.3% recover the common benchmark.

Continuous scalar:
- 249/443 = 56.2%