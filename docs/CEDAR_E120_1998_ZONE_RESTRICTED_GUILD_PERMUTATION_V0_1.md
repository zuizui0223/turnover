# Cedar E120 1998 within-zone guild-vector exchangeability sensitivity v0.1

2026-11-15. **Explicitly retrospective**, added after Cedar's full-source 1998 guild identity heterogeneity p=7.63e−7 and Jena's guild-identity non-replication p=0.309 were known. All results retain exploratory status. This does not modify the frozen 1998 primary contrast or the original E120 >=4-year source HOLD.

## Source and design
Original public ESA TIEE 2004 `DataBonus-Student.xls` is a *secondary reproduction* of Cedar E120; its exact source SHA256 `a86755544d75fabb85f4979303efcada96683ae60c0bc3bdb60c5d4c739d7476`. No original EDI PASTA source was fetched (403); no new effects may be presented as authoritative original package inference.

Original source-supported 1998 population is unchanged: **94 plots** sown to 2,4,8 species; **39** originally Woody-positive. Four herbaceous guild flags C3 grass, C4 grass, forb and legume; FG4 is their exact sum.

## Key question
Do the *guild identity* differences remain detectable when original **species-richness × Woody-treatment × herbaceous guild count × field location** is conditioned more stringently? This specifically probes sensitivity to conditional treatment support, not an ecological mechanism.

## Design support measured before this new outcome test
- Under exact `NumSp,Woody,FG4` strata: 73/94 Cedar plots in 9 strata have >1 observed guild assignment; 14 strata overall.
- Add four original-field-row **zones** defined by plot position `floor((plotID-1)/19)+1` and then grouped rows 1–4 / 5–9 / 10–13 / 14–18: **60/94 plots** in 18 nontrivial strata. The zones are analytical, not randomized Cedar blocks.
- Add **18 individual field-row strata**: **33/94 plots** in 15 nontrivial strata. Exact field-row swaps provide limited geographic-local support.
- Jena's 62 plot same richness×original block×FG4 support includes only 8 two-plot pairs (16 plots), all 2-spp. The source designs are not fully equivalent; use these counts only to identify differences in source support and detection power.

## Locked sensitivity estimators (not a new primary)
- Same 94 plot 1998 response `y=log1p(ESA AbvBio 1998 g/m²)`.
- For zone-aware test: base `y~C(NumSp)+Woody+C(zone)+FG4`; alternative `y~C(NumSp)+Woody+C(zone)+C3+C4+Forb+Legume`. The latter contains no FG4 (it would be perfectly collinear). Report HC3 three-constraint Wald equality p for four guild coefficients and unadjusted SSE improvement of alternative over nested base.
- **9,999 restricted vector permutations**, RNG seed **20261115**, shuffle whole original four-guild binary vector only among source rows within identical `NumSp×Woody×FG4×zone` strata; re-fit alternative, source base SSE unchanged, report right-tail `p=(1+count(deltaSSE_perm>=deltaSSE_obs))/(10000)`.
- 18-fieldrow sensitivity: base/alternative add `C(fieldrow)` replacing zone term, shuffle whole guild vectors within `NumSp×Woody×FG4×fieldrow` (n=9,999, seed **20261116**). Stratum support is smaller: 33/94. Report corresponding HC3 Wald and conditional vector test. If model/source rank is deficient, STOP; no selective dropping.
- Count number of shuffled plots/strata and number of unique guild vectors in each. Do not interpret a low p as evidence of causal group identity separately from species mixtures or of transfer across sites.

## Interpretation rules
All results were chosen after observing the original Cedar and Jena effects and are **exploratory robustness checks**. Show both zoning levels even if one fails. A significant source-conditioned guild-vector test indicates heterogeneity compatible with the original biological assignment but cannot establish exact randomization, nitrogen fixation, complementary resource use, trait FD, or global generality.
