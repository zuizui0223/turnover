# Evolution reviewer prebuttal — trait-memory RC2

Status: **submission-stage editorial risk audit; no new scientific analysis authorized**

## 1. “Your response is essentially a Mantel correlation. Why not use K or lambda?”

### Likely reviewer concern
The memory gradient is a pairwise distance association and therefore inherits known limitations of Mantel-type statistics. A reviewer may argue that the paper is built on a weak or nonstandard measure of phylogenetic signal.

### Current response
Do not defend rho as a generally superior signal estimator.

The manuscript now states that the statistical performance of Mantel-type signal tests depends on the chosen phylogenetic and phenotypic distance definitions and on measurement error. Harmon & Glor (2010) identified poor performance in some comparative settings, while Hardy & Pavoine (2012) showed that relative performance can reverse under alternative distance definitions and measurement error. Pavoine & Ricotta (2013) further showed that Mantel, Moran, Abouheif and Blomberg-type procedures are related through a common cross-product framework; much of their performance difference comes from the chosen similarity/dissimilarity matrices.

The inferential target is therefore deliberately narrower:

> **Does this prospectively fixed distance-decay descriptor carry portable information across lineages?**

The response was fixed before outcomes, qualified on each admitted geometry, and given species-cluster bootstrap SEs rather than treating species pairs as independent observations.

### Do not do
Do not add K, lambda or another signal estimator now. That would change the estimator family after observing the portability and repeatability results.

## 2. “The family component could still be unmeasured confounding.”

### Likely reviewer concern
Family is not a randomized biological treatment. A ~15% random-intercept share could summarize shared life history, study design, taxonomic structure, geography, data provenance or many unmeasured features.

### Current response
Agree.

The manuscript calls this **repeatable lineage context**, not a causal family mechanism.

The family point share remains near 0.15 after:
- species-level sampling-error correction;
- species-count adjustment;
- prune-fraction and calibration-geometry adjustment;
- BIEN source- and citation-composition adjustment;
- five-domain trait collapse;
- leave-one-trait / leave-one-family checks;
- a predeclared correlated-trait zero-family-effect null.

This establishes robustness to several specific artifacts, not causality.

### Do not do
Do not mine additional BIEN fields, environmental covariates, life-history predictors or taxonomic subgroups on the observed effects. Mechanism is future work.

## 3. “The log-scale sensitivity failed, so how much should we trust absolute differences?”

### Likely reviewer concern
Several plant traits are multiplicative and often log-transformed. Raw absolute differences can rank pairwise dissimilarities differently from log differences.

### Current response
This is the clearest unresolved limitation.

The all-201 log sensitivity was prospectively required to use the identical population with no offset or signed-log rescue. It stopped because 25 primary-tree systems and 18 prune-only systems contain at least one nonpositive species median.

The manuscript therefore scopes the result to the predefined **raw-scale distance-decay descriptor** and explicitly does not claim multiplicative-scale invariance.

### Do not do
Do not add an offset, delete nonpositive systems, or choose trait-specific transformations after seeing the outcome.

## 4. “Your family and system variance shares are too uncertain to compare.”

### Likely reviewer concern
The measurement-aware two-way cluster-bootstrap intervals are wide and overlap strongly.

### Current response
Agree.

The original claim that most variation was “system-specific” has been removed. Species-level sampling error accounts for roughly one quarter of typical total variance. System heterogeneity is the largest point component, but family and system heterogeneity are not cleanly ordered under bootstrap uncertainty.

The paper does **not** make a family-versus-system dominance claim.

## 5. “Negative portability may simply reflect a poor predictor.”

### Likely reviewer concern
The original same-trait arithmetic mean is unshrunk and can amplify noise when trait variance is small.

### Current response
This criticism is directly addressed.

Training-only BLUP shrinkage changes portability gain from −0.024 to +0.006 on the primary tree and from −0.032 to −0.0048 on the prune-only sensitivity. Thus the apparent negative penalty largely disappears.

The revised conclusion is not anti-portability. It is:

> **There is little stable trait-level information to borrow across families.**

This is reinforced by the small training trait variance relative to residual variance.

## 6. “Could correlated/redundant traits mechanically inflate family repeatability?”

### Likely reviewer concern
Height versus maximum height, leaf area versus leaf dry mass, and nitrogen-per-mass versus nitrogen-per-area are non-independent.

### Current response
This was prospectively tested.

A zero-family-effect null preserved predeclared trait-block covariance and the exact sparse family × trait incidence graph. Observed family repeatability exceeded the null on both tree treatments (p = 0.017 and 0.009). Collapsing the 12 labels into five biological domains also leaves the family share essentially unchanged.

This weakens the specific redundancy artifact without implying that every source of trait dependence has been modeled.

## 7. “Is ‘lineage-contingent’ too strong when the mechanism is unknown?”

### Likely reviewer concern
The title may be read as a causal evolutionary-process statement.

### Current response
Use “lineage-contingent” in the predictive/repeatability sense only.

The paper defines the result operationally:
- family identity carries repeatable cross-trait structure;
- trait identity provides almost no held-out-family predictive gain;
- the family component is not given a causal label.

Discussion explicitly lists possible biological and sampling processes summarized by family identity.

## 8. “The deep-family result was designed after outcome inspection.”

### Likely reviewer concern
The near-zero family-context versus deeper phylogenetic distance result could be overinterpreted as a tested third hypothesis.

### Current response
It is labeled **complementary post-outcome / exploratory** everywhere in RC2.

It is not part of the primary two-hypothesis design and is used only to motivate a future nested-taxonomic replication.

## 9. “Why should this be in Evolution rather than a methods or data journal?”

### Current response
The contribution is not a new estimator.

The evolutionary question is the scale at which trait evolutionary structure generalizes:
- trait identity does not transport memory strength to an unseen family;
- lineage context repeats modestly across traits.

Prior work already establishes that phylogenetic signal varies among traits and clades. The new result converts that heterogeneity into an explicit out-of-lineage prediction problem and demonstrates an asymmetry between **trait portability** and **lineage repeatability**.

## Submission rule

If peer review requests one of the frozen-prohibited analyses above, it may be considered as a reviewer-mandated revision. It must not be added before review merely to strengthen RC2.
