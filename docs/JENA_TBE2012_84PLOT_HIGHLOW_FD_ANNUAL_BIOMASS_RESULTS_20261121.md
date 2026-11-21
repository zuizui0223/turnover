# Jena TBE 2012: Trait-designed high-versus-low FD mixture and annual dry biomass

**Executed retrospective single-site descriptive contrast**, not a randomized independent FD-only intervention. Original PANGAEA [Wagg et al. 2017 DOI 10.1594/PANGAEA.876725](https://doi.org/10.1594/PANGAEA.876725), licensed CC BY 3.0. The original Wagg et al. 2017 *Functional Ecology* publication had already examined trait composition, complementarity and productivity; these are not independent field experiments or a new universal discovery.

## Original source and error correction

- Verified original source SHA256 `458f61307df217d285c972f894ca5cf23709c3524dc6e13bb4d9dd3c26c2ab56`, exactly **138 original plots**, **276 2012 source plot×month harvests** (May, August), 20 sown species mass columns; no missing sown-species biomass, no roster/metadata mismatches.
- **114** complete planted mixture plots (richness≥2), of which **84** in **6 predeclared original pool×planted-richness strata** had ≥4 high-FD and ≥4 low-FD source plots (stratum plot counts 12,12,12,16,16,16).
- Important source conflict: the literal PANGAEA `Block` field has **one** source category; original article says three spatial randomized blocks. All 138 source Plot IDs have **three distinct balanced A/B/C prefix classes of 46** and each source prefix covers all three trait pools. University JEXIS design dataset #739 export timed out: **there is no certified mapping from prefix series to actual randomized field blocks**. The original 3-literal-block v0.1 admission **stays HOLD**; v0.2 adjusts for three source prefix classes only as an **unverified spatial proxy**.
- This analysis branch uses a second **separately frozen**, outcome-independent new descriptively framed protocol `docs/JENA_TBE2012_ASSIGNED_HIGHLOW_FD_ANNUAL_BIOMASS_RETROSPECTIVE_V0_2.md` and reports the original source constraint rather than retroactively passing a failed causal gate.

## Analysis fixed before seeing high/low results

Treatment `HighFD=1[wFDc=3/4]` vs `LowFD=1[wFDc=1/2]`, same source pool and planted species richness, excluding 1-species monocultures. Annual response = original source same-plot **May+August sown-species total dry mass g/m²**, excluding weeds, dead/unidentified tissue. Fixed conditional WLS `log1p(Y) ~ C(pool×richness)+C(source-Plot-prefix)+HighFD`, equal weight per eligible pool×richness stratum. Source-plot units, NOT monthly harvests, independently resampled 2000 times stratified by pool×richness×HighFD, with unchanged WLS refitted each draw. Original all 2000/2000 bootstrap refits full rank.

| Descriptive association | Estimate (HighFD−LowFD) | 95% plot bootstrap interval |
|---|---:|---:|
| Original annual sown-species `log1p(g dry mass/m²)` | **+0.06034** | **−0.17094 to +0.28389** |
| `100(exp(beta)−1)` ratio approximation | **+6.22%** | **−15.72% to +32.83%** |
| Same model, untransformed g dry mass/m² | **+35.34 g/m²** | **−76.28 to +146.73 g/m²** |

**Conclusion:** high designed trait dissimilarity produces a positive **point** contrast in annual biomass when original source richness, trait-pool and source prefix class are adjusted, but **both original prespecified intervals span zero**. This does not establish a reliable biomass increase and does not independently identify the mechanism for Wagg's earlier published complementarity and competitive disparity. Even if the CI had excluded zero, species identity/assemblage is simultaneously manipulated with wFDc, so it would not establish a pure scalar FD intervention. Source A/B/C proxy remains physically uncertified.

The paper Wagg et al. 2017 already directly addressed much of this experiment's complementarity/composition relationship. New finding here is a **bounded, reproducible estimator with explicit original-source strata and a verified null-compatible interval**, not a new causal experiment or a law holding across plant lineages.

## Provenance

- [Original source and eligibility CI #44847711261](https://github.com/zuizui0223/turnover/actions/runs/44847711261), no ecological effect.
- [Plot-prefix structural CI #44847964061](https://github.com/zuizui0223/turnover/actions/runs/44847964061), university JEXIS timeout and old gate HOLD.
- [Original WLS effect + 2000 plot-level bootstrap CI #44848307503](https://github.com/zuizui0223/turnover/actions/runs/44848307503), SUCCESS, artifact #14684067248 digest `sha256:40c45be6246e34c4c1b0618a85ced45c4bb21a105520ad98ff9b2ed3e44d12fa`.
- Permanent nonraw derived numeric summary `results/jena_tbe2012_84plot_highlow_fd_annual_biomass_v0_2.json`; original species×plot rows and biomass outcomes **not committed**.
- Main BIEN 201-system, original Jena Main/BIODEPTH/TreeDivNet results and all their source HOLDs unchanged. The TBE is **one original field experiment** at Jena, not 3 independent studies and not a direct test of the global K/rho→FD→biomass chain.
