# Among-family heterogeneity of reproductive versus vegetative Blomberg K
**20 October 2026 · Post-discovery reporting audit, NOT a new biological or significance analysis.**

## Question and source boundary
Does the frozen AusTraits matched-tip reproductive-K advantage occur across families, or is it a consequence of a few high-coverage families? This is a **descriptive re-expression of the previously computed per-family counts**, not an additional independent hypothesis test. No additional AusTraits, TRY, or other data are retrieved. No K, OU, tree or source-outcome estimation is performed.

**Only source:** [permanent original aggregate](https://github.com/zuizui0223/turnover/blob/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_frozen_aggregate_inputs_v0_1/reproductive_vegetative_lofo.json) from original LOFO [run #38686389859](https://github.com/zuizui0223/turnover/actions/runs/38686389859). File bytes are authenticated against the [permanent source-SHA256 manifest](https://github.com/zuizui0223/turnover/blob/paper/austraits-organ-ecology-v0-2/results/austraits_organ_paper_frozen_aggregate_inputs_v0_1/frozen_input_manifest.json). Neither the traits nor original aggregate counts are altered.

## Results: both the prevalent direction and the exceptions are real descriptive features

| Descriptive quantity | S3 | Native prune |
| --- | ---: | ---: |
| Named family × trait-pair reproductive-K wins | **313/406 (77.09%)** | **314/397 (79.09%)** |
| Family-equal win-rate mean | **74.73%** | **75.84%** |
| Original whole-family bootstrap CI95, family-equal mean | 64.30–84.36% | 67.4–84.1% |
| Families with reproductive-majority comparisons | **27/34** | **30/34** |
| Families with vegetative-majority comparisons | **7/34** | **4/34** |
| Families with at least five cross-organ comparisons | 23/34 | 23/34 |
| Family-equal mean among those 23 families | **72.79%** | **76.97%** |
| Leave any one whole family out: remaining pair-weighted rate | **75.14–79.12%** | **77.13–80.78%** |
| Kish equivalent number for the *family count weights*, not effective biological replication | 21.26 | 21.56 |

The original bootstrap intervals are quoted **unaltered from the frozen result**. The family-wise means and single-family deletion diagnostics describe how the source graph is weighted; they are **not new phylogenetically independent observations**, not adjusted effect-size uncertainty and not an independent test of a universal organ hypothesis.

## Illustrative families, with denominators
| Plant family | S3 wins | Prune wins | Interpretation |
| --- | ---: | ---: | --- |
| Fabaceae | 35/36 (97.2%) | 34/34 (100%) | High reproductive K frequency in this source |
| Poaceae | 20/20 (100%) | 19/20 (95.0%) | High reproductive K frequency |
| **Asteraceae** | **16/30 (53.3%)** | **16/27 (59.3%)** | Much weaker directional asymmetry |
| **Casuarinaceae** | **2/12 (16.7%)** | **3/12 (25.0%)** | Observationally opposite majority in both trees |
| Rubiaceae | 1/6 (16.7%) | 2/6 (33.3%) | Opposite majority in both trees, with only six comparisons |

Two families (Casuarinaceae, Rubiaceae) have a vegetative-majority direction under **both** tree treatments and at least five pairs per treatment. This is an **after-the-fact reporting screen**, not a validated family-specific biological exception. Orchidaceae is 0/4 in both treatments, but its four comparisons do not meet even this descriptive support threshold.

Among the same 34 families, only **three** switch the side of 50% between tree treatments: **Elaeocarpaceae, Lauraceae and Phyllanthaceae**. Across the 397 original trait contrasts evaluable on both trees, **41/397 (10.33%)** had different signed K directions between tree treatments. The family-level reproductive-win fractions are correlated (Pearson r ≈ **0.859**), but this cannot count as cross-dataset replication because the underlying species and source compilation overlap.

## Interpretation and stop rules
The earlier global claim is refined from **“reproductive morphology is intrinsically more conserved”** to **“the available matched-tip reproductive-versus-vegetative K ranking is frequently reproductive-high across AusTraits families, but varies strongly by family, source eligibility and phylogenetic treatment.”**

There is no evidence here that Asteraceae, Casuarinaceae or any other family has a special evolutionary-rate regime, stronger developmental constraint, or a different OU selection parameter. K is not a direct evolutionary rate. Repeated pair comparisons share species, trait measurements and data providers, so a 27/34 count is not a binomial sample of independent evolutionary origins. S3 and prune are not independent biological replicates. The organ class itself was selected after the original results. Hence **no new p values or prospective family-specific predictions** are reported.

**Manuscript impact:** retain current exploratory paper structure (matched-tip direction + source/taxon ascertainment as the two main observations), but provide this audit for scientific coauthor review. Do not create a third main finding, claim cross-family independence, or amend the existing figure package before its human scientific review.

## Reproduce and detect source drift
Run `python scripts/qa/audit_austraits_organ_family_heterogeneity_v0_1.py --self-test --output results/austraits_organ_family_heterogeneity_v0_1/audit.json` at repository root. The audit checks the original file SHA256 against its committed manifest, validates every family's counts and reported rates, validates original K totals, and rejects simulated input corruption and impossible cross-tree totals. It emits a deterministic machine-readable result. The [audit workflow](https://github.com/zuizui0223/turnover/blob/paper/austraits-organ-ecology-v0-2/.github/workflows/austraits-organ-family-heterogeneity-qa-v0-1.yml) uploads that report as an Actions artifact.

**Status:** exploratory coauthor-review addendum; no journal submission, merge, or new database search authorized.
