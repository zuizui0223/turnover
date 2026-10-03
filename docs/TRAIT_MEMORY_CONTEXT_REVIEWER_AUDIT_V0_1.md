# Reviewer audit v0.1 — phylogenetic trait-memory context manuscript

Status: post-outcome robustness and wording audit only. No new empirical inference.

## 1. This is just another phylogenetic-signal paper

Risk: high if rho is sold as a new signal metric.

Response: do not sell rho as a replacement for K or lambda. The contribution is the second-order portability test: whether a within-family memory statistic for a named trait transfers to a held-out family.

## 2. Cross-validation in phylogenetics is not new

Risk: high. Guénard et al. (2013) already advocated predictive evaluation.

Response: agree. Novelty is not prediction itself. The prediction target is a family-specific macroevolutionary summary, not a missing trait value.

## 3. Clade dependence is already known

Risk: high. Ackerly (2009) and the phylogenetic-scale literature already establish clade heterogeneity.

Response: agree. Do not claim discovery of clade heterogeneity. Claim an explicit portability test and paired family-level recurrence analysis across one crossed matrix.

## 4. Residual 80.6% is not family x trait interaction

Risk: very high.

Response: correct. Residual contains true interaction, estimation error, BIEN measurement heterogeneity and model residual. Call it residual/system-level or unexplained system-level component.

Forbidden: 80.6% is family x trait interaction.

## 5. Families are not independent

Risk: moderate to high.

Response: the analysis estimates repeatability by family labels; it does not model covariance among families induced by deeper angiosperm phylogeny. Interpret the random effect as family-level lineage context, not a uniquely family-specific mechanism.

## 6. Portability p > 0.05 does not prove absence

Risk: high if phrased as trait memory does not transfer.

Response: the frozen positive result required gain > 0 and p <= 0.05 on S3 and prune-only. That criterion failed. Say no robust portability advantage or limited/non-robust portability.

## 7. Why use a global-mean baseline?

Risk: moderate.

Response: it asks a clean incremental question: does knowing trait identity improve prediction beyond knowing only the training response distribution? The permutation null destroys trait correspondence within families while preserving family distributions and incidence.

Frame this as incremental portability of trait identity, not the best possible predictive model.

## 8. Why family as the grain?

Risk: moderate.

Response: family is a repeated grain with enough within-family species and repeated traits to create a large crossed design. It is not claimed to be uniquely correct. Graham et al. (2018) motivates explicit attention to phylogenetic scale.

## 9. BIEN measurement heterogeneity may attenuate repeatability

Risk: real.

Response: acknowledge directly. Species states aggregate heterogeneous source measurements, and effect precision differs among systems. The residual therefore cannot be given a purely biological interpretation. Outcome-blind support, semantic and informativeness gates reduce but do not eliminate this limitation.

Do not add an outcome-selected precision weighting as a new primary model.

## 10. Taxonomically inserted S3 tips drive the effect

Risk: reduced by existing analysis.

Response: mandatory prune-only effects are strongly concordant with S3 (Spearman 0.832), and the portability/repeatability picture remains similar.

## 11. Three analyses on the same outcome are multiple fishing

Risk: moderate.

Response: each question was separately frozen and passed its own known-truth model-informativeness gate before its real rho was opened. All use the same outcome-blind 201-system core. The synthesis adds no new inferential test and preserves failed prior questions.

## Recommended primary claim

Trait identity provides no robust incremental cross-lineage prediction of phylogenetic-memory strength on the qualified family x trait matrix.

## Recommended supporting claim

Family-level lineage context is repeatable across traits at a modest estimated level, while most variation remains unresolved at the system/residual level.

## Claim to avoid

Phylogenetic memory is mainly a family property.

The pre-outcome dominance comparison failed its precision gate and remains unavailable.
