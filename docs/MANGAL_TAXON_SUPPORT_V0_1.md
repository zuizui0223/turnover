# Mangal taxonomy-ID support prefilter v0.1

## Decision

**MANGAL_TAXON_SUPPORT_PREFILTER_PASS**

After the spatial metadata gate passed, the second gate opened only Mangal `taxonomy_id` values on taxon-level nodes. Taxon names, interaction edges, interaction types, trait values and environmental values remained sealed.

Frozen necessary-support rule:

- >= 5 georeferenced networks;
- >= 20 unique taxonomy IDs;
- >= 10 taxonomy IDs repeated in at least two networks;
- >= 12 qualifying dataset programmes.

Observed:

- metadata-qualified programmes: **17**
- programmes passing taxonomic support: **13**
- required: **12**
- node rows retrieved: **39,939**
- taxon-level node rows in scope: **8,566**

The gate passes.

## Important negative cases

Two very large network collections did **not** pass merely because they contain many networks:

- `kolpelke_et_al_2017`: 783 georeferenced networks, but 0 usable taxonomy IDs under this gate;
- `RMBL_pollination`: 86 georeferenced networks, but 0 usable taxonomy IDs.

`ricciardi_2010` fails the >=20 unique-taxon requirement and `beaver_1985` fails the >=10 repeated-taxon requirement.

This shows that the support gate is not a network-count proxy.

## Passing programmes

Thirteen programmes pass the necessary taxonomic-support prefilter:

`havens_1992`, `closs_1994`, `dexter_1947`, `hadfield_2014`, `baeta_2011`, `ruzicka_2012`, `hawkins_goeden_1984`, `mckinnerney_1978`, `thompson_townsend_2004`, `tavares-cromar_williams_1996`, `kaiser-bunbury_et_al_2010`, `kaiser-bunbury_et_al_2014`, and `bartomeus_2005`.

This remains a **necessary, not sufficient** gate because focal and partner guilds are not yet distinguished.

## Next gate

Before any interaction edge is opened:

1. recover dataset/reference metadata only;
2. freeze one source-faithful interaction family and focal guild per programme where possible;
3. stop programmes whose interaction semantics cannot be determined without inspecting outcome edges;
4. only then run the observed-support informativeness simulation.

No edge/type/value is authorized by this result alone.
