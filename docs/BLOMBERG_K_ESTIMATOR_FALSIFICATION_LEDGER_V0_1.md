# Blomberg's K sensitivity: pre-outcome interpretation ledger v0.1

Status: interpretation protocol frozen 2026-10-08, after all rho outcomes and exploratory analyses, but before opening any AusTraits Blomberg K effect. This is NOT a prospective replication of the entire BIEN programme. It is an independent-estimator sensitivity.

## Population and ordering

Fixed 254 matched positive-numeric AusTraits family x trait systems (42 families, 13 traits). No missing-K-system selection based on the K outcome is permitted.

Blomberg K uses source-native log species values on the same S3/prune trees as the rho analysis. log(K) is an estimation scale; comparisons of pairwise K rank are unaffected by monotone log.

Prune-only K is the preferred conventional-signal axis because the tree does not require inserted tips; S3 K must be reported.

## Questions and decision boundaries

1. **Estimator coherence**: report pooled Spearman correlation of K and rho across all matched systems, plus mean within-family rank Spearman among families with >=3 common traits. High agreement is necessary to interpret rho rankings as rankings of conventional phylogenetic signal. Zero or negative agreement refutes straightforward equivalence.
2. **Lineage-wide signal**: calculate family conditional repeatability of log(K) after trait fixed effects, on prune and S3 separately. Nonzero family repeatability would support some family-dependent signal architecture but is not proof of a causal lineage trait. There is no K bootstrap CI in the initial workflow; avoid inferential claims about whether its magnitude exceeds 0.10 without such uncertainty.
3. **Trait-average prior**: use the pre-specified held-out-family absolute K predictor against the out-of-family global baseline and blocked permutation p-value. Explicitly report both tree axes; a positive result on one axis only is sensitivity, not tree-robust generality.
4. **Portable rank hierarchy**: use held-out-family normalized K rank with permutation test. If this succeeds on both trees while rho rank portability fails, reject the claim that absence of portable hierarchy is shared across estimators.
5. **Pairwise re-ordering**: compute pair order reversal among two random families for trait pairs with >=10 shared families. If a value remains >=0.40 on both tree axes, report extensive rank re-ordering under K; if it is materially less or is tree-axis sensitive, restrict the central conclusion to the original rho statistic. The 0.40 threshold is a descriptive reuse of an earlier threshold, not a hypothesis-test p-value.

## Falsifying outcomes

- Strong rho-specific re-ordering but portable K trait ranks: hierarchy failure is estimator-specific. Do not write 'evolutionary memory allocation is generally unstable.'
- Family shifts under rho but no family shifts under K: the family component may primarily reflect distance-dissimilarity geometry rather than conventional signal.
- Concordant family-level K/rho effects but discordant within-family ranks: only lineage-wide patterns transfer across signal metrics, not trait allocation.
- Consistent K re-ordering and L>A under the crossed K model: the architecture is supported by two distinct signal-related summaries. Do not infer evolutionary rate or mechanism.

## Interpretation boundary

For continuous traits under Brownian evolution, phylogenetic distance and trait dissimilarity have a positive expectation, while Blomberg K is standardized against a Brownian signal benchmark. No universal algebraic relation requires rho and K to rank traits identically.

Even if both estimators agree, the paper is about phylogenetic structure, not evolutionary tempo. Trait-change rates, selective constraints, or adaptive modules require distinct data/models.

## Decision integrity

Do not alter:
- the 254-system matched core,
- tree axes,
- positivity and support rules,
- the rho results or their original prospective classification.

Report all K outcomes whether agreement is positive, null, reversed, incomplete or computationally unavailable.
