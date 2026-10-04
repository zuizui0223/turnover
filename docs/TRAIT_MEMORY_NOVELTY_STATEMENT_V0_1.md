# Novelty statement — temporal plant trait memory

## What is not new

The paper does **not** claim novelty for any of the following:

- that plant traits can show phylogenetic signal;
- that different traits show different strengths of phylogenetic signal;
- that the same trait can evolve at different rates in different clades;
- that phylogenetic niche conservatism can vary among traits and lineages.

Those points are established in the comparative literature, including Blomberg et al. (2003), Ackerly (2009), Crisp & Cook (2012), Münkemüller et al. (2012), and Revell (2018).

## What is new

The study converts clade heterogeneity into a **prediction/transport question**.

Instead of fitting trait X in clade A and separately fitting trait X in clade B, it asks:

> If the phylogenetic memory of trait X has been learned from other plant families, does that information improve prediction of trait X in a family that was completely withheld?

On the prospectively qualified 201-system crossed design, the answer is no under the frozen family-blocked criterion. The same-trait predictor does not outperform the global training mean on either S3 or backbone-native prune-only trees.

The same crossed design then asks the converse contextual question:

> After trait-specific means are removed, does a family tend to show a recurring deviation across several different traits?

A modest family-level repeatable component remains.

The combination yields an asymmetric generalization result:

1. **trait -> unseen lineage is not robustly portable;**
2. **lineage context -> multiple traits leaves a recurring component;**
3. **that component is not detectably organized as a smooth function of deeper family phylogenetic distance;**
4. **most variation remains unresolved at the individual family x trait system level.**

The empirical implication is therefore not that “lineage dominates trait.” It is that the transferable unit is not well represented by the trait label alone. At this taxonomic scale, phylogenetic memory behaves more like a property of a **trait embedded in a lineage context**.

## Why this matters for comparative ecology

Phylogenetic-signal estimates are often interpreted as reusable properties of traits: if leaf area, height, or seed mass is strongly conserved in one analysis, that estimate can inform expectations elsewhere.

The present result tests that transfer explicitly and finds that it is unreliable across plant families under the predeclared criterion.

This matters for:

- comparative models that borrow trait-specific phylogenetic priors across clades;
- imputation or prediction of trait structure in poorly sampled lineages;
- interpretation of “conserved” versus “labile” traits as globally portable labels;
- macroecological analyses that combine clades while assuming one trait-level phylogenetic structure.

The recommendation is not to abandon trait-level phylogenetic information. It is to allow the phylogenetic structure associated with a trait to vary with lineage context unless cross-lineage portability has itself been demonstrated.

## Claim boundary

The family component is repeatable, not proven causal.

Pre-frozen adjustment for species coverage, backbone-native tip fraction and calibration geometry leaves it nearly unchanged. A separate post-outcome provenance sensitivity audits BIEN source composition. Even if that audit is stable, unmeasured study heterogeneity and lineage-correlated ecological/developmental factors remain possible explanations.

The deepest defensible claim is therefore about **predictive generalization**, not mechanism.
