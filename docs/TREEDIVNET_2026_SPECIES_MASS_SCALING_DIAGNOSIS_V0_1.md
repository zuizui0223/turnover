# TreeDivNet 2026 species×plot biomass apparent nonadditivity: source-scale diagnosis

**Post-source-surprise source-only diagnostic, fixed 2026-11-16** after the strict initial source mass hierarchy gate failed (135/328 total = 41.2% direct-sum matches despite 322/328 DS2 species counts equalling the original planted richness). Do not retroactively mark original strict sum gate PASS or call the original dataset erroneous. No ecological FD/biomass relationship is tested.

## Competing source representations (fixed before ratios reviewed)

On the same exact original `site×block×plot` keys for DS1 and DS2, evaluate three **source accounting identities** without fitting an outcome:

- **A: direct conservation** `stand_woody_mass = sum(species_per_plot_mass)`.
- **B: species-level equal-area normalization** `stand_woody_mass = sum(species_per_plot_mass)/observed_DS2_species_count`.
- **C: design richness normalization** `stand_woody_mass = sum(species_per_plot_mass)/DS1_reported_species_richness`.

Evaluate each candidate with identical original-source fixed tolerance `abs(stand−candidate) <= max(0.001 Mg dry ha−1, 0.01*abs(stand))`. No model fitting or source definition selection to rescue a desired correlation. Report all three across **all 328** joined original source plot keys, including original nonnegative zero values, and by original planted species richness (1,2,3,4,>4) and by 11 original experiments. If original DS1 richness does not match DS2 distinct species count, keep that plot in all source comparisons, report mismatch separately.

Diagnostics: ratio `sum_species/stand` for positive stand and positive sum, reported only as site/richness aggregate medians and interquartile ranges, never original plot values. Record source data row and signed file MD5 identities. Report if normalization ratios are near planted richness; do not call that a verified physical measurement unit, as the authors' original README labels both as woody biomass Mg ha−1 and no plot-area/numerator derivation is given.

- The original A original strict gate stays **HOLD**.
- A new accounting interpretation might be **SOURCE_SCALE_PATTERN_FOUND** if B or C reaches ≥90% of 328 original joined plot matches (and same or higher reconciliation fraction than A in ≥9/11 original sites), but is only a statistical source formatting pattern pending confirmation from the source authors, **not** a revision of original data or a source gate PASS.
- Otherwise status `UNRESOLVED_SOURCE_SCALE_HOLD`.
- Keep log/citation provenance, aggregate output only, no species/plot raw measures, no associations, regressions, or phylogenetic K→FD claims.

Do not convert the original source ecological response based on this diagnosis unless original author/source metadata establishes the numeric representation and repeated-environment units. The original published woody stand mass in DS1 remains the designated response.
