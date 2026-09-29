# Mangal species-rank support gate v0.1

## Decision

**HOLD_MANGAL_SPECIES_RANK_SUPPORT**

The gate was frozen before taxon names/ranks were opened and before any interaction edge/type/value was opened.

Required per programme:

- >=5 georeferenced networks
- >=20 unique species-rank taxa
- >=10 species-rank taxa repeated in at least two networks

Required programme count: **12**.

Observed passing programmes: **7/13**.

Passing:

- havens_1992 — 104 species / 83 repeated
- hadfield_2014 — 297 / 220
- baeta_2011 — 31 / 25
- mckinnerney_1978 — 20 / 10
- thompson_townsend_2004 — 53 / 38
- kaiser-bunbury_et_al_2010 — 132 / 108
- kaiser-bunbury_et_al_2014 — 63 / 55

Six programmes fail species-rank support and are not rescued using genus/family/higher-rank nodes.

## Consequence

Mangal remains valuable for geographically replicated network structure, but it does not supply enough joint programmes for the frozen evolutionary-time × geographic-space interaction test.

No interaction edge was opened.

Under the already-frozen finite-family rule, this is a valid **support-geometry HOLD**, so the joint interaction route may switch to the second and final primary source family: the stable versioned GloBI archive.

Mangal can later serve as an external spatial/network validation source, but not as the response-selected replacement for its own failed joint gate.
