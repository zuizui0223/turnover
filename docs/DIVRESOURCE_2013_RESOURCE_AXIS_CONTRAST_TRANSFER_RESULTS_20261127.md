# DivResource 2013 resource-axis transfer and descriptive shade-dependent ranking reversal
2026-11-27, exploratory reanalysis of the same one original field experiment, not a new independent field replication.

## Source and fixed test
Siebenkäs, Schumacher & Roscher (2016), *Resource Availability Alters Biodiversity Effects in Experimental Grass-Forb Mixtures*, PLOS ONE 11:e0158110, DOI 10.1371/journal.pone.0158110. Original S5/S6 SHA-256 pinned; all 64 published Fox component partitions agree within printed precision. Prior B/NDE/CE/SE/TDCE/DE scores replayed. Forty-eight two-species plots retained, two disjoint species pools, four fertilizer×shade contexts each. Three perfect matchings of the four assigned functional types: H-only (different stature, same functional group), G-only (different functional group, same stature), HG (different both). Each category contains two mixtures covering every species once. C_H=mean(HG)−mean(G-only); C_G=mean(HG)−mean(H-only). Additive mono expectation cancels within each context (max |C(E)| 1.14e-13 g/m²). C(B)=C(NDE) up to 1.14e-13; not independent endpoints. This balancing does not eliminate physical block effects or all composition interactions. No actual root acquisition trait measured in the new analysis.

Reconstructed coherent S5 outcomes, fixed contrast-space transfer. M0 separate constant per axis; Mmatch shade→C_H, fertilization→C_G; Mcross swapped; Mfull both resource terms per axis, additive (no fertilizer×shade term). Train A predict B and reverse. Gain=1−SSE(model)/SSE(M0), raw original g dry mass/m² contrasts. No population CI or p-value with two pools in one field. No axis/endpoint selected post-score to redefine criterion.

## Predeclared outcome: matched transfer criterion not supported
| Endpoint | Mmatch | Mcross | Mfull | Matched A→B | Matched B→A | Fixed criterion |
|---|---:|---:|---:|---:|---:|---|
| B | -0.46% | -9.44% | -9.90% | -1.58% | +0.38% | FAIL |
| NDE | -0.46% | -9.44% | -9.90% | -1.58% | +0.38% | FAIL |
| CE | -13.98% | -16.56% | -30.54% | -14.26% | -13.76% | FAIL |
| SE | -21.61% | -17.44% | -39.05% | -67.70% | -1.20% | FAIL |
| TDCE | -90.26% | -68.70% | -158.96% | -84.01% | -97.69% | FAIL |
| DE | +8.26% | +7.49% | +15.75% | -8.96% | +17.00% | FAIL |

All six fixed endpoint criteria fail. DE has a positive combined matched gain +8.26% and full-model gain +15.75%, but the matched model worsens A→B prediction and improves B→A, and the full model is secondary rather than a replacement. NDE height-axis shade gain +2.75% combined (+4.03%,+1.81% by direction); functional group-axis fertilization gain −22.14% combined. Thus the preassigned one-resource-per-axis generalization hypothesis does not pass. Original study had already reported effects of nutrient/light supply; no claim to rediscover those effects.

## Post-result diagnostic: which mixture type gains relative to the other?
C_G−C_H = mean(G-only)−mean(H-only). The marginal shade change averaged across fertilizer conditions is +192.725 g/m² in A and +212.75 g/m² in B. This follows from the predeclared contrast output, but the following fertilizer-stratified comparison is explicitly **post-result descriptive**, not a confirmatory interaction test.

| Pool | Fertilizer 0/1 | Unshaded G−H NDE | Shaded G−H NDE | Shade change | CE contribution | SE contribution |
|---|---:|---:|---:|---:|---:|---:|
| A | 0 | 154.65 | 40.65 | -114.00 | -36.68 | -77.32 |
| A | 1 | -219.05 | 280.40 | 499.45 | 280.96 | 218.49 |
| B | 0 | -198.95 | -87.35 | 111.60 | 107.15 | 4.45 |
| B | 1 | -238.10 | 75.80 | 313.90 | 245.01 | 68.89 |

Units g dry aboveground mass/m². Under fertilization both pools show negative G−H NDE in unshaded contexts and positive G−H in shaded contexts. Without fertilization the direction of the shade change differs across pools. The difference-in-differences of the shade response between F+ and F− equals +613.45 and +202.30 g/m² in A and B. Under F+, the shift decomposes into CE +280.96/+245.01 and SE +218.49/+68.89; each CE exceeds the corresponding SE, but no inferential intervals or causal mediation. Differences are computed from exact source contrasts, all component identities pass. This observation is a hypothesis about *relative pair-composition performance in joint resource contexts*, not evidence that any trait diversity generally increases absolute production or proof of nutrient or light partitioning. In particular the normalized tall-minus-short yield difference responds to shading in opposite directions (A −0.882, B +0.272). Do not infer a consistent tall species competitive advantage. Grass-minus-forb yield differences respond positively to shade in both pools (+0.521/+0.440), but grass/forb is not a direct root physiology proxy, and normalized allocations do not identify competition/uptake mechanisms.

## Decision and next evidence requirement
Do not claim universal matching of shade with stature and fertilization with functional-group dissimilarity. The observed fertilized ranking reversal motivates a separate prospectively fixed factorial interaction test in other independent experiments with source verified sown trait axes and whole-block design. This is not a successful external validation: each group mean has only two mixture plots per context, four shared resource contexts, one source mono per species/context, eight shade blocks and only one field. Resource moderation may reflect plot/block and species composition effects. No new causal FD-only inference, phylogenetic memory mediation, or changed earlier results. The source paper's existing positive resource effects remain attributed to original authors.

## Provenance
Original run #45951957874, SUCCESS, artifact 15177356172, digest sha256:6a34b6c955800d838365c210605a720054bd17ea1c06a8cc8052f914df8203f1. [Fixed protocol](DIVRESOURCE_2013_RESOURCE_AXIS_CONTRAST_TRANSFER_FROZEN_20261127.md). [Source run](https://github.com/zuizui0223/turnover/actions/runs/45951957874). [Aggregate JSON](../results/divresource_2013_resource_axis_contrast_transfer_20261127_v0_1.json). Raw original source records not redistributed.
