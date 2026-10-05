# Known truth is not automatically assignable in simulation-based power studies

## Abstract

1. Simulation-based power studies usually treat a requested effect size as an input. That assumption can fail when the effect is a summary of constrained data rather than a freely assignable parameter of the generator. We distinguish three logically ordered events: **structural realizability**, **generator accessibility**, and **recovery**.

2. We tested these gates across 722 real plant family × trait sampling geometries under a common phylogenetic-memory target (Spearman rho = 0.15), with observed trait values kept hidden. Structural realizability was audited explicitly; generator accessibility was challenged by a controlled latent-OU-to-Mk2 substitution; downstream recovery was evaluated only after successful assignment.

3. Among 683 systems with complete calibration diagnostics, generator no-bracket failure differed by 65.0 percentage points between continuous-scalar and nominal-categorical representations (14.7% versus 79.7%), whereas assigned-but-S3-recovery-failed systems occupied nearly identical shares of the full diagnostic populations (13.3% versus 13.8%). All 276 categorical trees could structurally express the target. Replacing only the generator with symmetric Mk2 reduced categorical no-bracket frequency to 61.6%, and removing the exact binary state-balance attenuation term reduced it further to 42.4–43.8%. Even after successful Mk2 assignment, 34.9% failed downstream recovery.

4. A failed known-truth simulation can therefore represent different inferential events. Structural feasibility does not guarantee generator accessibility, and generator accessibility does not guarantee recovery. Power studies for constrained representations should establish target assignability before interpreting failure as low statistical power.

## Data and code for peer review

An anonymized review bundle containing the frozen design contracts, canonical result summaries, verification scripts, figure-data preparation and figure-rendering code will be supplied with the submission or through a private-for-review archive. The review bundle will exclude Git history and author-identifying repository metadata. Observed trait values are not required to reproduce the methodological results reported here. A permanent public archive with a persistent identifier will replace the review bundle at acceptance.

## Keywords

simulation study; power analysis; data-generating mechanism; constrained outcomes; calibration; phylogenetic signal

## Introduction

Simulation-based power studies usually begin by choosing an effect size that is treated as known truth, generating data intended to contain that effect, and asking whether an estimator recovers it. This ordering hides a logically prior question whenever the requested effect is a summary of simulated data rather than a free parameter of the generator: **can the requested truth actually be assigned on the realized design?** General simulation guidance separates data-generating mechanisms, estimands, methods and performance measures (Morris et al. 2019; Williams 2024), but usually assumes that the generative mechanism can supply the declared target.

That assumption is innocuous when the target is itself a direct parameter of an unconstrained generative model. It becomes less obvious for constrained outcomes. Binary and other discrete representations collapse many possible continuous configurations into a small state space. Their pairwise dissimilarities contain ties, attainable state balances depend on the realized sample, and increasing phylogenetic structure can change not only the magnitude of a statistic but whether both states remain represented at all. Under these conditions, a simulation may be described as “known truth” even when the requested summary statistic is not reachable by the generator over the declared parameter family.

The underlying feasibility problem has precedents in synthetic-data generation. Methods for simulating correlated binary, ordinal and mixed variables explicitly calculate feasible correlation bounds and check requested dependence structures before generation (Fialkowski & Tiwari 2019). **Structural feasibility is therefore not itself our novelty.** The unresolved step is generator-specific accessibility: a target may exist within the representation's attainable state space yet remain unreachable, or reachable only through invalid states, along the stochastic path defined by the chosen generator. If that failure is folded into a final power estimate, a generator limitation can be attributed to the estimator.

Phylogenetic signal provides a useful stress test because the literature already shows that signal metrics respond differently to sample size, tree topology, evolutionary model and trait representation (Fritz & Purvis 2010; Münkemüller et al. 2012; Borges et al. 2019; Yao & Yuan 2025). Binary-specific and categorical signal statistics have been developed precisely because discrete outcomes do not behave like continuous traits, and recent unified approaches likewise report lower power for low-state categorical traits. Our question is not whether binary traits can be harder to analyse. Instead, we ask where a failed known-truth simulation fails.

We distinguish three gates. **Structural realizability** asks whether the representation on the realized design contains any state configuration capable of expressing the requested target. **Generator accessibility** asks whether the declared stochastic generator can reach and bracket that target while satisfying its own validity rules. **Recovery** asks whether the target, once successfully assigned, can be recovered under finite simulation and the frozen estimator. These gates are logically ordered: a failure of realizability or generator accessibility occurs before estimator power can be evaluated.

We evaluate this distinction in a frozen comparative-ecology simulation programme spanning 722 real plant family × trait sampling geometries. All mechanism analyses are outcome-free: observed trait values and observed phylogenetic-memory effects remain excluded. We first quantify the representation-dependent recovery frontier, then localize categorical failure to calibration versus recovery. We next test whether the target is absent from the binary state space or merely inaccessible to the original latent-OU threshold generator, substitute a representation-appropriate two-state Markov generator while holding the target and estimator fixed, and finally isolate an exact state-balance attenuation term. A pre-frozen stop rule prevents further mechanism search after this sequence.

## Materials and Methods

### General assignability audit

The proposed audit applies when the requested simulation target is a summary of generated data rather than a free parameter of the data-generating mechanism. It is deliberately ordered so that downstream estimator performance is evaluated only after upstream assignment has been established.

**Step 1 — Declare the target and validity contract.** Specify the target statistic, target value, tolerance, realized design on which it is defined, and any conditions that make a simulated replicate valid.

**Step 2 — Audit structural realizability.** Construct an attainable witness, exact bound, optimization result or exhaustive check showing whether the representation × realized design can express the target at all. If the target is structurally impossible, stop: the requested power scenario is undefined for that design and target.

**Step 3 — Audit generator accessibility.** Holding the target statistic and realized design fixed, ask whether the declared generator can bracket or otherwise assign the target over a prospectively specified parameter family while satisfying the validity contract. Distinguish failure to approach the target from failure caused by invalid generated states.

**Step 4 — Diagnose generator dependence without redefining success.** If a mechanism diagnostic is scientifically justified, change one generative component at a time while preserving the target, estimator and success thresholds. Such substitutions diagnose accessibility; they should not be searched adaptively until a favourable result appears.

**Step 5 — Evaluate recovery conditional on assignment.** Only systems in which the target was successfully assigned contribute to conventional recovery, bias or power statements for that target. Report upstream assignment failures separately rather than pooling them with estimator failures.

The audit therefore produces three possible scientific conclusions: target not structurally realizable; target realizable but inaccessible to the declared generator; or target assigned but not recovered. These outcomes should not be collapsed into one low-power category.

### Study population and outcome firewall

The study uses 722 prequalified BIEN family × trait sampling geometries spanning 120 plant families and 25 traits. Of these, 443 are continuous-scalar systems and 279 are nominal-categorical systems. Each system has a realized S3 phylogeny and a prune-only comparison geometry inherited from the frozen trait-memory qualification programme.

The mechanism study is deliberately separated from the biological trait-memory analysis. No observed trait value and no observed phylogenetic-memory rho enters the present results. System selection, simulation targets, calibration rules and recovery thresholds were frozen before the corresponding known-truth outcomes were opened. The closed biological trait-memory paper is therefore not evidence for the methodological claims made here.

### Common target and recovery gate

The common declared target was Spearman rho = 0.15 between pairwise patristic-distance ranks and pairwise trait dissimilarity. The original qualification programme used 200 pilot replicates per candidate generator value and 1,000 independent evaluation replicates after calibration.

A system passed the frozen recovery gate only if the S3 geometry and the prune-only geometry both passed. Within a geometry, valid-replicate fraction had to be at least 0.90, directional recovery at least 0.80, and median absolute recovery error at most 0.10. These thresholds were inherited unchanged throughout the present analysis.

For continuous traits, pairwise dissimilarity was the absolute continuous difference. For nominal-categorical traits, pairwise dissimilarity was binary mismatch. The latter makes Spearman rho equivalent to a point-biserial association between patristic-distance ranks and a match/mismatch indicator.

### Representation-dependent recoverability

We first analysed the full 722-system known-truth qualification result using the pre-frozen logistic model

`PASS ~ semantic_class × z(log n_species) + z(prune_fraction)`.

Uncertainty was estimated by a two-way cluster bootstrap resampling family and trait labels independently for 2,000 replicates. This stage asks whether the same target is equally recoverable across representations and sampling geometries; it does not diagnose the mechanism.

### Calibration versus recovery

For the 683 newly simulated systems with stored calibration diagnostics, we decomposed failure into two stages. A **calibration no-bracket** occurred when the frozen generator, realized tree and estimator failed to bracket rho = 0.15 on the predeclared parameter grid with adequate pilot validity. A **recovery failure** occurred when calibration succeeded but the subsequent 1,000-replicate evaluation failed one or more frozen recovery thresholds.

The artifact-correct novel population contains 407 continuous systems and 276 categorical systems. We modelled no-bracket status as a function of semantic class, standardized log species count and standardized prune fraction. Trait- and family-level summaries were used only to establish the breadth of the categorical bottleneck.

### Structural realizability of the categorical target

Calibration failure does not by itself imply that the binary state space cannot express rho = 0.15. We therefore constructed an explicit realizable state family on every categorical S3 tree.

Every tree edge defines a one-transition binary state: all descendant tips take one state and all remaining tips take the other. For each edge we computed the exact binary-mismatch Spearman rho between the resulting mismatch indicator and patristic-distance ranks. The maximum positive edge-split rho is not a global upper bound over all possible multi-transition binary patterns. It is a biologically interpretable attainable witness. If at least one edge split exceeds rho = 0.15, a hard binary-state-space ceiling below the target is ruled out for that tree.

### Accessibility within latent-OU thresholding

The original categorical generator simulated a latent Gaussian OU process and thresholded tip values at zero. We used the stored pilot calibration grids to determine why the 220 categorical no-bracket systems failed.

For binary mismatch, a replicate is invalid when all tips receive the same state. We therefore distinguished systems whose finite OU grid never reached rho = 0.15 even if low-validity points were allowed (**effect ceiling**) from systems that reached rho >= 0.15 only after valid-replicate fraction fell below 0.90 (**validity collapse**). Within each system we also summarized the rank association of log generator parameter with pilot rho and with valid fraction.

### Generator substitution with symmetric Mk2

The edge-split analysis showed that the target was structurally realizable, so the next prospectively frozen test changed only the categorical generator while retaining the same trees, rho target and binary-mismatch Spearman estimator.

The alternative generator was a symmetric two-state continuous-time Markov chain (Mk2/ER). Root state was Bernoulli(0.5). Along a branch of length t, the probability of a state flip was

`P(flip) = (1 - exp(-2 q t))/2`.

To make the grid comparable across trees, q was parameterized through a dimensionless eta equal to q times the median positive pairwise patristic distance. The frozen eta grid was 0.01 to 100 in half-log10 steps. Common random numbers were used across eta candidates within a system, with independent deterministic randomness for evaluation. Calibration and recovery thresholds were unchanged.

Primary quantities were the Mk2 no-bracket rate, paired rescue among the 220 original OU no-bracket systems, and new Mk2 failures among the 56 systems that had calibrated under OU thresholding.

### Exact state-balance attenuation

For binary mismatch Y and patristic-distance rank X, the ordinary correlation has the exact factorization

`rho = Delta_rank × sqrt(p(1-p))`,

where p is the prevalence of mismatch pairs and

`Delta_rank = (mean rank_mismatch - mean rank_match) / SD(rank)`.

Because `sqrt(p(1-p)) <= 0.5`, a necessary balance-normalized separation capable of supporting rho = 0.15 is `Delta_rank = 0.30` at p = 0.5. We therefore froze a final mechanism test that reproduced the same Mk2 pilot states and same distance ranks but calibrated Delta_rank instead of rho. The corresponding tolerance was 0.02, obtained by mapping the original rho tolerance of 0.01 at p = 0.5.

During the first execution, live BIEN reconstruction failed an exact geometry-identity assertion for at least one system before its balance-normalized statistic was computed. A retry protocol was therefore frozen before the full result was available. All 276 system identities remained in the population; systems whose reconstructed S3 geometry no longer matched the frozen Mk2 artifact were assigned an outcome-free geometry HOLD and received no balance-normalized outcome. Full-population bounds were computed by assigning all HOLD systems to calibration success versus failure, without imputing intermediate outcomes.

### Stop rule

Before the full balance-normalized aggregate was opened, an unconditional stop rule was frozen. After v0.5, no additional generator, estimator, target, parameter-grid extension or outcome-based subgroup search on these 276 categorical systems could be used to strengthen the primary mechanism claim. Remaining unexplained failure was to be retained as a result.

## Results

### Equal targets were not equally recoverable

Across all 722 systems, 255 (35.3%) passed the full known-truth recovery gate. Continuous-scalar recovery was 249/443 (56.2%), whereas nominal-categorical recovery was 6/279 (2.15%; Fig. 1B).

In the pre-frozen logistic model, the categorical coefficient was -4.74, corresponding to an odds ratio of 0.0087 at mean sampling. Its two-way family/trait cluster-bootstrap 95% interval on the logit scale was -26.58 to -3.61. Increasing log species count was strongly associated with improved recoverability (odds ratio 5.79 per SD), and higher native prune-tip fraction was also favourable (odds ratio 1.75). Representation nevertheless dominated the recovery surface.

### Most categorical loss occurred before evaluation

Among the 683 novel systems with calibration diagnostics, 60/407 continuous systems (14.7%) failed to bracket the target, compared with 220/276 categorical systems (79.7%). The complementary population partition sharpened this localization (Fig. 1B). Continuous systems comprised 14.7% generator no-bracket, 13.3% successfully assigned but S3-recovery-failed, and 72.0% S3-recovery-passed systems. Categorical systems comprised 79.7%, 13.8%, and 6.52%, respectively. Thus the representation contrast at the final S3 endpoint was dominated by a 65.0-percentage-point difference in generator accessibility; assigned-but-recovery-failed systems contributed almost the same share of each full diagnostic population.

Conditioning only on systems that could be assigned gives a different and complementary view: recovery failed in 54/347 continuous systems (15.6%) and 38/56 categorical systems (67.9%). Categorical systems were therefore disadvantaged after assignment as well, but this downstream conditional penalty acted on a much smaller accessible subset. The adjusted odds ratio for categorical no-bracket status was 18.4.

The categorical bottleneck was broad but heterogeneous. Across seven categorical traits represented in the novel population, no-bracket rates ranged from 50.0% to 86.9%, with three traits above 80%. Across 100 families represented by at least two categorical systems, the median family no-bracket rate was 100% with an interquartile range of 66.7–100%.

### The binary state space could express the target in every tree

The structural-realizability test rejected the simplest explanation for categorical no-bracket failure. All 276 categorical S3 trees contained at least one one-transition edge split with rho >= 0.15. Among the 220 original OU no-bracket systems, none had a maximum edge-split rho below the target.

The median maximum edge-split rho among these 220 systems was 0.7733 (IQR 0.7422–0.8114), whereas the median maximum rho reached on the frozen OU grid was 0.09785. The median gap between an explicit realizable one-transition state and the maximum OU-grid pilot rho was 0.67665 (IQR 0.62935–0.7283; Fig. 2A). The target therefore existed in the realized binary state space but was usually inaccessible along the chosen generative path.

### OU thresholding failed mainly before complete validity collapse

Stored OU grids further localized the accessibility problem. Of the 220 categorical no-bracket systems, 195 (88.6%) never reached rho = 0.15 anywhere on the finite grid even after ignoring the valid-fraction threshold. The remaining 25 (11.4%) reached rho >= 0.15 only at grid points whose valid fraction was below 0.90. No no-bracket system reached the target at an admissible grid point (Fig. 2B).

Across categorical no-bracket systems, increasing the OU parameter tended to increase the measured effect (median within-system Spearman = +0.767) while strongly decreasing the valid fraction (median = -0.957). Median valid fraction at the largest grid value was 0.20. In the 60 continuous no-bracket systems, valid fraction remained 1.00. Thus monomorphism was one part of the binary accessibility trade-off, but it did not explain the 88.6% of failures whose finite OU grids remained below target even without the validity constraint.

### A representation-appropriate generator rescued accessibility asymmetrically

Replacing latent-OU thresholding with symmetric Mk2 reduced categorical no-bracket frequency from 220/276 (79.7%) to 170/276 (61.6%; Fig. 3A). Of the 220 original OU no-bracket systems, 51 (23.2%) became calibratable under Mk2. Only one of the 56 originally OU-calibrated systems became a new Mk2 no-bracket failure. The 51-versus-1 paired asymmetry identifies generator choice as a material source of truth-accessibility loss (Fig. 3B).

Mk2 calibration succeeded in 106 systems. Of these, 69 passed the subsequent S3 recovery gate and 37 failed, giving a recovery-failure rate of 34.9% conditional on assignment (Fig. 3C). Assignment and recovery were therefore empirically separable even after using a generator matched to the binary representation.

### State balance explained another independent share of accessibility loss

The balance-normalized factorization was reproduced to a maximum absolute numerical error of 8.88 × 10^-16. Four of the 276 systems encountered outcome-free geometry drift under exact reconstruction and were placed in HOLD before their v0.5 statistic was computed. Of the remaining 272 exact geometry matches, 167 had been Mk2-rho no-bracket and 105 had been Mk2-rho calibrated.

Calibrating Delta_rank rather than rho produced 155 calibrated systems and 117 no-bracket systems in the matched subset. Fifty of the 167 matched Mk2-rho no-bracket systems (29.9%) were rescued, while none of the 105 previously calibrated matched systems became a new failure. Median pilot valid fraction at Delta_rank calibration was 1.00, median mismatch-pair prevalence was 0.4037, and median ordinary rho at the same calibration point was 0.1398.

The four geometry-HOLD systems comprised three original Mk2-rho no-bracket systems and one calibrated system. Without imputing their outcomes, the full-population balance-normalized no-bracket rate was bounded at 42.4–43.8%, and the rescue fraction among the original 170 Mk2-rho no-bracket systems was bounded at 29.4–31.2%. Generator choice and state balance therefore explained substantial, separable portions of accessibility failure, but a large remainder persisted (Fig. 3A).

## Discussion

### A known target can fail before power is defined

The main result is conceptual but empirically sharp: a declared known truth is not automatically an assignable truth. In this study the same rho = 0.15 target passed through three different bottlenecks. It was structurally realizable on every categorical tree. It was frequently inaccessible to the original latent-OU threshold generator. A representation-appropriate Mk2 generator rescued a substantial subset, and removing an exact state-balance attenuation term rescued another subset. Even after successful assignment, a further set of systems failed recovery.

These are not interchangeable forms of “low power.” Structural non-realizability would mean that the requested truth is absent from the allowed state space on the realized design. Generator inaccessibility means that the state space contains suitable configurations but the chosen stochastic path does not place sufficient probability near them under the frozen parameter family. Recovery failure is downstream: the target has been assigned, but finite data and the estimator do not recover it under the declared criteria. Only the third of these is conventional estimator-power failure.

### The categorical penalty was not a hard binary ceiling

A generic statement that binary or low-state categorical traits can have lower power is not new. Our result refines where that loss occurs. Every categorical tree had a one-transition witness far above the target, including every OU no-bracket tree. The binary state space itself therefore did not impose the observed ceiling at rho = 0.15.

This matters because a no-bracket result could otherwise be interpreted as an intrinsic informational limitation of the representation. Here the median realizable one-edge signal among failed systems was roughly eight times the median maximum reached along the OU grid. The relevant limitation was access to the state space, not absence of informative states within it.

### Generator choice is part of truth assignment

The Mk2 substitution provides the strongest paired evidence for generator dependence. Nothing about the realized trees, target statistic or estimator changed, yet 51 previously inaccessible systems became calibratable while only one moved in the opposite direction. The generator is therefore not merely a neutral device for producing data around an externally specified truth. For a constrained representation, it partly determines whether that truth can be assigned.

This does not imply that Mk2 is the biologically correct evolutionary model for every categorical plant trait. The purpose of the substitution is diagnostic. It demonstrates that accessibility is contingent on the generative family and should therefore be checked rather than assumed.

### State balance is a distinct attenuation mechanism

The exact identity `rho = Delta_rank sqrt(p(1-p))` separates alignment of mismatch pairs with phylogenetic distance from the prevalence of mismatch pairs itself. Removing only this balance term, while retaining the same Mk2 states and distance ranks, rescued about 30% of the remaining matched no-bracket systems and produced no new failures. State balance is therefore not just a descriptive correlate of binary power; it is an algebraically identified attenuation mechanism in this distance-based statistic.

At the same time, approximately 42–44% of the full categorical population remained no-bracket after both generator substitution and balance normalization. Under the pre-frozen stop rule we do not search for a better estimator, broader parameter grid or favourable subgroup to remove this remainder. It is retained as unresolved generator–partition–geometry alignment.

### Implications for simulation-based power studies

The structural-realizability gate generalizes a familiar requirement from constrained-data simulation: requested dependence structures should lie within attainable bounds. Our additional claim is that **feasibility does not imply accessibility by the declared generator**. The practical implication is therefore a change in ordering. For constrained representations, a simulation study should not move directly from “choose a target effect” to “estimate power.” It should first ask:

1. **Can the target exist on the realized design?** Supply a realizability witness or bound appropriate to the representation.
2. **Can the proposed generator reach it?** Demonstrate calibration accessibility over a prospectively declared parameter family while enforcing validity rules.
3. **Only then ask whether the estimator recovers it.**

This sequence complements, rather than replaces, existing guidance on data-generating mechanisms, estimands and Monte Carlo error. Simulation-based calibration similarly evaluates inferential calibration conditional on data generated from a specified model (Säilynoja et al. 2026); assignability concerns the prior logical step of whether a requested target summary can be generated in the first place.

The requirement is especially relevant when the outcome representation is discrete, compositional, bounded, zero-inflated or otherwise constrained, because the requested effect may not be a free parameter of the generative family. Realized sample geometry can make this a system-specific property even under a common target.

### Scope and limitations

Our empirical demonstration is intentionally narrow. It uses one distance-based phylogenetic-memory target, one target magnitude (rho = 0.15), real plant phylogenetic geometries, binary mismatch for the categorical representation and two categorical generator families. The one-edge construction proves only that a simple realizable binary pattern exceeds the target; it is not a global characterization of all possible binary states. The balance-normalized statistic is used as a mechanism diagnostic, not proposed as a universally preferable estimator.

The four v0.5 geometry HOLD systems also illustrate a reproducibility issue independent of the statistical mechanism. Live source reconstruction can drift even when code and package versions are pinned. We therefore report bounds rather than silently redefining the population or imputing outcomes.

These limitations restrict the numerical generality of the observed percentages. They do not weaken the logical distinction among realizability, accessibility and recovery. That distinction applies whenever an analyst declares a target summary that is not itself a freely assignable parameter of the generator.

## Conclusion

Known-truth simulations can fail before statistical power is meaningfully evaluated. In our phylogenetic-memory example, categorical target failure was not caused by an absence of informative binary states: the target was explicitly realizable on every tree. Instead, generator accessibility, state-balance attenuation and downstream recovery each removed different systems. A power study that collapses these stages can therefore attribute failure to the estimator when the requested truth was never successfully assigned.

For constrained representations, “known truth” should be treated as a claim to verify, not an input to assume.

## Figure mapping

- **Figure 1:** assignability gates and the representation-dependent recovery contrast.
- **Figure 2:** structural witness versus latent-OU accessibility, plus effect-ceiling versus validity-collapse failure.
- **Figure 3:** sequential OU → Mk2 → balance-normalized accessibility and recovery after assignment.

Primary figure captions are in `docs/PHYLO_MEMORY_FIGURE_CAPTIONS_V0_1.md`. The frozen figure plan is `data/phylo_memory_figure_plan_v0_1.json`.

## Analysis closure

The primary mechanism programme is closed under `data/phylo_memory_mechanism_stop_v0_5_2.json` and `data/phylo_memory_mechanism_close_v0_5_3.json`. No additional generator, estimator, target, grid extension or outcome-based subgroup search on these 276 categorical systems may strengthen the primary claim. The unresolved remainder is part of the result.


## References

Borges, R., Machado, J. P., Gomes, C., Rocha, A. P. & Antunes, A. (2019). Measuring phylogenetic signal between categorical traits and phylogenies. *Bioinformatics*, 35, 1862–1869. https://doi.org/10.1093/bioinformatics/bty800

Fialkowski, A. & Tiwari, H. (2019). SimCorrMix: Simulation of correlated data with multiple variable types including continuous and count mixture distributions. *The R Journal*, 11(1), 250–286. https://doi.org/10.32614/RJ-2019-022

Fritz, S. A. & Purvis, A. (2010). Selectivity in mammalian extinction risk and threat types: a new measure of phylogenetic signal strength in binary traits. *Conservation Biology*, 24, 1042–1051. https://doi.org/10.1111/j.1523-1739.2010.01455.x

Morris, T. P., White, I. R. & Crowther, M. J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine*, 38, 2074–2102. https://doi.org/10.1002/sim.8086

Münkemüller, T., Lavergne, S., Bzeznik, B., Dray, S., Jombart, T., Schiffers, K. & Thuiller, W. (2012). How to measure and test phylogenetic signal. *Methods in Ecology and Evolution*, 3, 743–756. https://doi.org/10.1111/j.2041-210X.2012.00196.x

Säilynoja, T., Schmitt, M., Bürkner, P.-C. & Vehtari, A. (2026). Posterior SBC: simulation-based calibration checking conditional on data. *Statistics and Computing*, 36, 78. https://doi.org/10.1007/s11222-026-10825-9

Williams, C., Yang, Y., Lagisz, M., Morrison, K., Ricolfi, L., Nakagawa, S. & Warton, D. (2024). Transparent reporting items for simulation studies evaluating statistical methods: Foundations for reproducibility and reliability. *Methods in Ecology and Evolution*, 15, 1926–1939. https://doi.org/10.1111/2041-210X.14415

Yao, L. & Yuan, Y. (2025). A unified method for detecting phylogenetic signals in continuous, discrete, and multiple trait combinations. *Ecology and Evolution*, 15, e71106. https://doi.org/10.1002/ece3.71106
