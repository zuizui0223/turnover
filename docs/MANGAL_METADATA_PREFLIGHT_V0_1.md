# Mangal metadata preflight v0.1

## Decision

**MANGAL_METADATA_SPATIAL_SUPPORT_PASS**

The first interaction-arm gate used only Mangal dataset/network metadata. No node identity, taxon identity, interaction edge, interaction type/value, trait value or environmental value was opened.

Current API snapshot:

- public datasets: **175**
- public networks: **1,487**
- georeferenced public networks: **1,307**
- georeferenced + dated public networks: **1,283**
- datasets with at least five georeferenced networks: **17**
- frozen requirement: **12**

The gate therefore passes.

## Eligible dataset programmes

The 17 programmes are recorded machine-readably in:

`results/mangal_metadata_preflight_v0_1/result.json`

They include large repeated-network sources such as `kolpelke_et_al_2017`, `RMBL_pollination`, `havens_1992`, `kaiser-bunbury_et_al_2010` and `kaiser-bunbury_et_al_2014`, plus 12 additional programmes meeting the same frozen five-network support rule.

## Interpretation

This establishes **sampling geometry only**.

It does not establish that:

- interaction taxa repeat across those networks;
- enough focal taxa exist for a phylogenetic partner-profile analysis;
- interaction types are comparable;
- rewiring is estimable after conditioning on species turnover;
- any time–space coupling exists.

The next gate may open taxon/node identity only. Interaction edges remain sealed.

## Provenance

- workflow run: `36546918783`
- job: `109335413553`
- frozen design: `data/mangal_metadata_preflight_design_v0_1.json`
- runner: `scripts/analysis/audit_mangal_metadata_preflight_v0_1.py`
