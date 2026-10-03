# Cross-lineage prediction reveals limited portability of phylogenetic trait memory across plant families

## Abstract

Phylogenetic signal is often summarized as a property of a trait, yet evolutionary dynamics can vary among clades and phylogenetic scales. We asked a predictive question: does a phylogenetic-memory estimate learned for the same plant trait in other families transfer to a completely held-out family? Using BIEN 4.2.8 and a prospectively qualified matrix of 201 family x trait systems spanning 45 vascular-plant families and 12 continuous traits, we quantified memory-loss strength as the Spearman association between within-family patristic separation and trait-state dissimilarity. The final system set was fixed before real memory effects were opened, and all systems passed support, semantic, phylogenetic-crosswalk and known-truth informativeness gates. Family-blocked prediction showed no robust portability advantage for trait identity over a training-set global mean (S3 gain = -0.024, blocked-permutation p = 0.091; prune-only gain = -0.032, p = 0.193). In a crossed REML decomposition, family identity accounted for an estimated 0.150 of total variance (95% parametric-bootstrap CI 0.020-0.286), trait identity 0.043 (0-0.134), and 0.806 remained in the residual/system-level component. A prospectively failed model-precision gate precluded a formal family-versus-trait dominance comparison. In a separate qualified model that removed trait-specific means, conditional family repeatability was 0.183 (0.029-0.337; prune-only 0.168), although its interval spanned a predeclared 0.10 practical reference. Thus within-family phylogenetic memory does not imply a robustly portable trait-specific memory signature across plant families. Instead, memory strength is context-dependent, with a modest recurring family-level lineage component and substantial unresolved system-level variation.

## Introduction

Phylogenetic comparative biology often treats trait resemblance among relatives as an interpretable feature of a trait or evolutionary process. Metrics such as Blomberg's K and Pagel's lambda summarize phylogenetic dependence, while evolutionary-rate models describe the tempo of phenotypic change. Yet both signal and rate can vary with the set of taxa being analysed. Ackerly (2009), for example, showed that evolutionary rates for the same plant functional traits differed by orders of magnitude among woody clades, and Graham, Storch & Machac (2018) formalized the broader concept of phylogenetic scale dependence: a pattern measured at one phylogenetic extent need not extrapolate to another.

This scale dependence creates a predictive problem that is distinct from detecting phylogenetic signal itself. A trait can show a real within-clade phylogenetic pattern while the strength of that pattern varies enough among clades that a value learned in one clade provides little information about another. Predictive evaluation is not new to phylogenetic comparative methods. Guénard, Legendre & Peres-Neto (2013) explicitly argued that the presence of phylogenetic signal does not guarantee useful prediction, Brown & Thomson (2018) emphasized predictive model checks in evolutionary biology, and recent work shows that explicit phylogenetic models can perform well for single-trait prediction (Richard-Bollans & Silvestro 2026). Those studies primarily predict missing trait values or compare model performance at the species level.

Here we ask a second-order question. Rather than predicting a species trait value, we first estimate a within-family macroevolutionary summary for each family x trait system: a phylogenetic memory gradient, defined as the monotonic increase in trait-state dissimilarity with patristic separation. We then ask whether that estimated memory gradient is portable across lineages. Specifically, if a named trait has a particular memory gradient in several plant families, does that information improve prediction of the same trait's memory gradient in a completely held-out family?

A crossed family x trait design also allows the complementary question. After trait-specific mean memory gradients are removed, does family identity recur across multiple traits? This separates three quantities that are often conflated: within-clade phylogenetic memory, cross-clade portability of trait identity, and cross-trait repeatability of lineage context.

We addressed these questions using BIEN trait data and a prospectively qualified crossed matrix of 201 family x trait systems. The analysis was deliberately fail-closed. System inclusion was determined before real memory effects were opened, using support, semantic validity, phylogenetic crosswalk and known-truth geometry-informativeness gates. Three separately frozen analyses were then applied to the identical system set: a repeatability decomposition, family-blocked trait portability, and conditional family repeatability. We expected that if phylogenetic memory were an intrinsic and transferable property of trait identity, same-trait information from other families would improve held-out-family prediction. Conversely, if memory depended strongly on lineage context, trait portability would be weak and family identity could retain a recurring cross-trait component.

## Methods

### Study structure and prospective qualification

The present study is a temporal-only follow-up to a broader turnover programme. The earlier programme jointly targeted temporal and geographic turnover but closed before generalized trait outcomes were opened because the predeclared spatial informativeness requirement could not be met across enough independent families. The present analyses did not relax that programme. Instead, they used an independently frozen temporal-only design.

Trait data came from BIEN 4.2.8 (Enquist et al. 2026). Phylogenetic placement used V.PhyloMaker2 at commit 7af3fb5152f691af2e4ec9d5e2e467d1b50505e9 with GBOTB.extended.TPL and scenario S3 (Jin & Qian 2022). A mandatory prune-only sensitivity retained only backbone-native tips.

The final empirical core was selected entirely before real memory-loss effects were opened. Starting from the preclassified BIEN trait universe, systems were required to pass temporal support, trait-state semantic validity, S3 and prune-only phylogeny crosswalk, and a known-truth geometry-informativeness test. The final core contained 201 family x trait systems, 45 families and 12 continuous traits (Fig. 1). The family x trait graph was connected; each family was represented by at least two traits and each trait by at least five families.

A separate pre-outcome model-informativeness study attempted to classify the relative dominance of trait and family variance, but the realized graph could not recover a twofold variance ratio with the predeclared precision. That question was therefore closed before real effects were opened. The present repeatability, portability and conditional-lineage analyses were separately frozen and each passed its own known-truth model-informativeness gate before using real memory effects.

### Phylogenetic memory gradient

For each family x trait system, species state was the median valid BIEN measurement for that trait. All 12 traits in the final core were continuous.

Within each system, we calculated all unordered pairwise patristic distances from the S3 tree and all corresponding absolute differences in species trait state. The memory-loss statistic was

rho = Spearman(patristic separation, trait-state dissimilarity).

Larger positive rho indicates a stronger monotonic loss of trait similarity with phylogenetic separation. The statistic is not a time-calibrated decay rate, Blomberg's K, Pagel's lambda or a Brownian evolutionary-rate parameter.

Before outcomes were opened, we proved and independently verified that under complete whole-state label permutation over all unordered pairs, the exact expected Spearman correlation is zero. Thus rho itself is the null-centered effect; permutations are not needed to estimate the null mean.

For every system we calculated both S3 rho and a prune-only rho on backbone-native tips. Three independently implemented execution routes later reproduced all 201 S3 and prune-only effects exactly.

### Repeatability decomposition

The first analysis asked how much variation in memory-loss rho was repeatable by family identity and by trait identity separately, without comparing the two components.

We fitted the crossed REML model

rho ~ 1 + (1 | family) + (1 | trait_name),

with one unweighted observation per family x trait system.

Let sigma²_family, sigma²_trait and sigma²_residual denote the three fitted variance components. Repeatability shares were defined as each component divided by their sum:

R_family = sigma²_family / total,

R_trait = sigma²_trait / total,

R_residual = sigma²_residual / total.

Uncertainty was estimated using 2,000 parametric-bootstrap replicates under fixed seed 20261003. The model and bootstrap were qualified prospectively on known-truth simulations of the exact 201-edge graph. A hard rule prohibited using these components to classify one axis as dominant over the other because the earlier variance-ratio model had failed its precision gate.

We repeated the model on prune-only rho for the identical system set. Leave-one-trait-out and leave-one-family-out refits were predeclared descriptive robustness checks.

### Cross-lineage portability of trait identity

The second analysis asked whether trait identity improves prediction of memory rho for a completely held-out family.

For each family f, all systems belonging to f were excluded from training. For each held-out system (f,t), the trait-based predictor was the arithmetic mean rho for trait t among all remaining families. The baseline predictor was the arithmetic mean rho across all training systems. Each held-out family x trait system was predicted exactly once.

Prediction performance was summarized as

portability gain = 1 - SSE_trait / SSE_global.

Positive gain means that knowing trait identity reduces out-of-family prediction error relative to a training-set global mean.

We tested the directional hypothesis using 999 blocked permutations under seed 20261003. Within each family independently, observed rho values were permuted among that family's fixed trait labels. This preserves each family's response distribution and the exact family x trait incidence graph while destroying cross-family correspondence of trait identity. The one-sided p-value was

(1 + number of null gains >= observed gain) / (1 + 999).

A positive portability result required observed gain > 0 and p <= 0.05. The identical procedure was required to pass on both S3 and prune-only rho. The graph, statistic, alpha level and permutation scheme had all passed a pre-outcome known-truth power/false-positive gate.

### Conditional family repeatability

The third analysis asked whether family identity retains a recurring component across traits after trait-specific mean memory gradients are removed.

We fitted

rho ~ 0 + trait_name + (1 | family)

by REML. Trait identity was treated as a fixed nuisance factor, giving each admitted trait its own mean. Family identity was a random intercept representing a grouping-level shift shared across multiple traits.

Conditional family repeatability was

R_family|trait = sigma²_family / (sigma²_family + sigma²_residual).

A 0.10 practical reference was frozen before real outcomes were opened. Classification was predeclared as: lower 95% bootstrap bound > 0.10, repeatable lineage regime; upper bound < 0.10, weak lineage repeatability; otherwise uncertain. Uncertainty used 2,000 parametric-bootstrap replicates under seed 20261003.

The identical model was repeated on prune-only rho. Leave-one-trait-out and leave-one-family-out refits were mandatory descriptive robustness checks.

### Interpretation boundaries

The family random effect treats families as grouping levels. It does not model phylogenetic covariance among the families themselves. Therefore the estimated family component is interpreted as family-level lineage context, not as a uniquely family-specific causal mechanism.

Likewise, the residual component in the crossed model is not identifiable as pure family x trait biological interaction. It can contain genuine family x trait specificity, effect-estimation error, heterogeneous trait measurements and other model residual.

## Results

### Memory gradients were common but heterogeneous

Across the 201 qualified systems, S3 rho averaged 0.093 (median 0.053, SD 0.143), ranged from -0.183 to 0.709, and was positive in 74.6% of systems (Fig. 2). Prune-only rho averaged 0.114 and was positive in 71.6% of systems.

S3 and prune-only estimates were strongly concordant across systems (Spearman rho = 0.832; Pearson r = 0.848; Fig. 4), indicating that the broad pattern was not generated solely by S3 taxonomic insertion.

### Most variation was not repeatable as family or trait main effects

In the crossed REML decomposition, R_family was 0.150 (95% bootstrap CI 0.020-0.286), R_trait was 0.043 (0-0.134), and R_residual was 0.806 (0.660-0.952).

Prune-only estimates were similar: family 0.148, trait 0.021 and residual 0.831.

Leave-one-out estimates were stable. Across omission analyses, R_family ranged from 0.094 to 0.190 and R_trait from 0.024 to 0.061.

These components were not compared in a formal dominance test. The main inference is that most among-system heterogeneity was not repeatable as a family main effect or trait main effect and remained in the unresolved system-level/residual component.

### Trait identity did not provide robust cross-family prediction

For S3 rho, the same-trait predictor had SSE = 4.251 compared with 4.151 for the global training-mean baseline, yielding portability gain = -0.0242. The blocked-permutation p-value was 0.091.

For prune-only rho, the same-trait predictor had SSE = 6.184 compared with 5.990 for the global baseline, yielding gain = -0.0324 and p = 0.193.

Thus the predeclared positive criterion failed on both tree treatments. Trait identity did not provide a robust incremental prediction advantage for a new family.

This negative portability result did not arise because memory gradients were universally absent: many systems had positive rho. Instead, the strength of that memory did not transport reliably by trait label across families.

### Family-level lineage context recurred across traits

After fitting separate means for all 12 traits, conditional family repeatability was 0.183 (95% bootstrap CI 0.029-0.337). The prune-only estimate was 0.168.

Leave-one-trait and leave-one-family refits ranged from 0.121 to 0.227, showing that the estimated family component was not driven by one trait or one family.

The bootstrap interval spanned the predeclared 0.10 practical reference, so the frozen classification was uncertain relative to 10% (Fig. 3).

## Discussion

### Within-clade memory is not the same as cross-clade portability

The central result is a distinction between detecting phylogenetic memory and transferring a memory estimate among clades. A named trait can show a positive association between phylogenetic separation and trait dissimilarity within many families while the magnitude of that association remains poorly transportable by trait identity alone.

This distinction parallels a broader principle in predictive comparative biology: a detectable phylogenetic pattern does not automatically imply useful out-of-sample prediction. Guénard et al. (2013) made this point for predicting species trait values. Here the prediction target is different. We ask whether a family-specific macroevolutionary statistic learned repeatedly across other families is portable to a held-out lineage.

### The result is an empirical test of phylogenetic scale dependence, not the discovery of it

Clade dependence of trait evolution is well established. Ackerly (2009) showed large differences in evolutionary rate for the same plant traits among clades, and Graham et al. (2018) formalized how evolutionary attributes can depend on phylogenetic grain and extent.

Our contribution is to turn that context dependence into a blocked prediction problem. Rather than only comparing fitted values among clades, we ask whether same-trait memory measured elsewhere is good enough to improve prediction in a new family. On the qualified graph, it was not.

### Trait identity was a weak portable summary of memory strength

Trait repeatability was small and uncertain, and same-trait information from other families did not outperform a global mean in held-out-family prediction. These results argue against treating a trait-specific phylogenetic-memory estimate as a portable constant.

This does not imply that named traits have no evolutionary regularities. It means that trait identity alone was insufficient to carry the memory-gradient magnitude across the family boundary tested here. The relevant predictive state may require additional information about lineage history, ecological context, life form, developmental constraints, environmental regime or other factors not modelled here.

### Family identity retained a modest recurring component

After trait means were removed, family identity retained an estimated repeatability of 0.183, with a lower bootstrap bound above zero but an interval spanning the predeclared 0.10 practical reference.

This component should be interpreted carefully. Families are grouping levels, not independent causal units, and the model does not account for deeper covariance among plant families. The family term can therefore reflect any lineage-associated structure shared by multiple traits within a family, including deeper phylogenetic history, correlated ecology, architecture or measurement composition.

The appropriate conclusion is that family-level lineage context recurs across traits at a modest estimated level, not that a family-specific mechanism has been identified.

### The large residual is unresolved, not a measured interaction

The crossed model assigned 0.806 of variance to the residual component. It is tempting to label this as family x trait interaction, but that would overstate what the model identifies.

The residual includes any true idiosyncratic family x trait biology, but also uncertainty in system-level rho, heterogeneous BIEN measurement sources, unmodelled within-species variation and other model residual. The stronger and defensible conclusion is simply that most variation was not repeatable as either family or trait main effects.

Future work with replicated within-species measurement error, standardized trait protocols and explicit family-level phylogenetic covariance could separate these components more cleanly.

### Implications for comparative ecology

Trait databases and large phylogenies increasingly support prediction of missing species traits and extrapolation of trait relationships across taxa. Model-based phylogenetic approaches can perform well for such tasks, including under evolutionary-model misspecification (Richard-Bollans & Silvestro 2026).

Our result does not challenge that literature. It instead identifies a different extrapolation problem: exporting a macroevolutionary memory summary from one set of lineages to another. For that task, a trait label by itself was not a robust predictor on this family-blocked design.

Accordingly, trait-specific phylogenetic priors or expectations learned in one clade should not automatically be treated as portable to another without direct blocked validation at the scale of intended transfer.

### Limitations

First, BIEN aggregates measurements collected under heterogeneous protocols. Outcome-blind semantic and informativeness gates reduce obvious incompatibilities, but they do not eliminate measurement error.

Second, the family grain was chosen because it provided repeated species and repeated traits across a broad matrix. It is not necessarily the biologically privileged scale. Different results could emerge at genus, order or continuous phylogenetic scales.

Third, S3 includes taxonomically inserted tips. The prune-only analysis substantially reduces this concern, but backbone uncertainty remains.

Fourth, memory-loss rho is a monotonic distance-dissimilarity gradient. It is not an explicit stochastic evolutionary-rate parameter and should not be interpreted as one.

Finally, the family random effect does not model deeper phylogenetic covariance among families. A future analysis could replace independent family effects with a family-level phylogenetic covariance structure, but that is outside the present prospectively qualified design.

## Conclusion

Phylogenetic memory of plant traits is real in many individual lineages, but its magnitude is not a robustly portable intrinsic property of trait identity across families. The same named trait can carry different memory gradients in different lineages, while family identity contributes a modest recurring cross-trait context. Most remaining heterogeneity is unresolved at the system level. The broader implication is predictive: within-clade phylogenetic memory should not be assumed to transfer across clades without explicit validation at the phylogenetic scale of application.

## Data and code availability

The analyses use BIEN 4.2.8 through a pinned RBIEN implementation (commit 531cb221bd44cf43419e89b2354f6424e718cd53) and a pinned V.PhyloMaker2 implementation (commit 7af3fb5152f691af2e4ec9d5e2e467d1b50505e9) with GBOTB.extended.TPL. Raw BIEN measurements are not redistributed by this repository and remain available through the BIEN source under its data-access terms.

All analysis code, prospective gate contracts, machine-readable result summaries and manuscript figure scripts are versioned in the turnover repository. The canonical manuscript-level effect table contains the 201 qualified family × trait systems and is stored at results/trait_memory_context_synthesis_v0_1/effects.csv (SHA256: 5fffdfbc9ab50ff7bf568e80537a290e11c2bfde02f1d5484c7e896ed5f9415b). Three independently authorized real-effect execution routes reproduce the S3 and prune-only rho values in this table exactly.

A machine-readable submission manifest is provided at data/trait_memory_context_submission_manifest_v0_1.json. The prospective gate chronology, including questions that were stopped before real effects were opened, is documented in docs/TRAIT_MEMORY_GATE_CHRONOLOGY_SI_V0_1.md.

## Figure captions

**Figure 1. Prospectively qualified crossed family × trait design.** Incidence matrix for the fixed empirical core of 201 family × trait systems spanning 45 vascular-plant families and 12 continuous traits. Cells indicate qualified systems only; family and trait ordering is graphical and is not used to define inferential clusters.

**Figure 2. Phylogenetic memory gradients across the fixed 201 systems.** Dot matrix of S3 memory-loss rho for every qualified family × trait system. Positive values indicate a monotonic increase in trait-state dissimilarity with patristic separation; negative values indicate the opposite pattern. The figure is descriptive and the ordering is not used for system selection or clustering.

**Figure 3. Triangulation of repeatability, portability and family-level lineage context.** (A) Crossed REML family, trait and residual/system-level shares on S3, with 95% parametric-bootstrap intervals and prune-only point estimates. The components are reported separately; no family-versus-trait dominance test is made. (B) Observed leave-one-family-out portability gain for S3 and prune-only rho, shown against the 2.5–97.5% interval of the predeclared within-family blocked-permutation null; zero denotes no incremental advantage over the global training mean. (C) Conditional family repeatability after trait-specific means are fitted, with the S3 95% bootstrap interval, prune-only point estimate and predeclared 0.10 practical reference.

**Figure 4. Backbone sensitivity of system-level memory gradients.** S3 versus prune-only memory-loss rho for the identical 201 qualified systems. The dashed line is the 1:1 reference. The descriptive cross-system Spearman correspondence is 0.832.

## References

Ackerly, D.D. 2009. Conservatism and diversification of plant functional traits: evolutionary rates versus phylogenetic signal. Proceedings of the National Academy of Sciences USA 106:19699-19706. doi:10.1073/pnas.0901635106.

Brown, J.M. & Thomson, R.C. 2018. Evaluating model performance in evolutionary biology. Annual Review of Ecology, Evolution, and Systematics. doi:10.1146/annurev-ecolsys-110617-062249.

Enquist, B.J. et al. 2026. BIEN: A biodiversity informatics ecosystem advancing open and reproducible workflows for plant observation, plot and trait data. Methods in Ecology and Evolution 17:1556–1584. doi:10.1111/2041-210X.70274.

Graham, C.H., Storch, D. & Machac, A. 2018. Phylogenetic scale in ecology and evolution. Global Ecology and Biogeography 27:175-187. doi:10.1111/geb.12686.

Guénard, G., Legendre, P. & Peres-Neto, P. 2013. Phylogenetic eigenvector maps: a framework to model and predict species traits. Methods in Ecology and Evolution 4:1120-1131. doi:10.1111/2041-210X.12111.

Jin, Y. & Qian, H. 2022. V.PhyloMaker2: an updated and enlarged R package that can generate very large phylogenies for vascular plants. Plant Diversity. doi:10.1016/j.pld.2022.05.005.

Münkemüller, T. et al. 2012. How to measure and test phylogenetic signal. Methods in Ecology and Evolution 3:743-756. doi:10.1111/j.2041-210X.2012.00196.x.

Revell, L.J. 2018. Comparing evolutionary rates between trees, clades and traits. Methods in Ecology and Evolution 9:994-1005. doi:10.1111/2041-210X.12977.

Richard-Bollans, A. & Silvestro, D. 2026. The persistent advantage of model-based phylogenetic methods for single-trait prediction. Methods in Ecology and Evolution 17:1032-1041. doi:10.1111/2041-210X.70258.
