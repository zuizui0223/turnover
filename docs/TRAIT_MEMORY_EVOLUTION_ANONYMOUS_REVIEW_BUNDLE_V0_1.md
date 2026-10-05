# Anonymous peer-review bundle — Evolution RC1

Status: **submission packaging; scientific content frozen upstream**

This bundle supports double-anonymized review of the trait-memory manuscript.

## Included evidence

- frozen 201-system family × trait effect table;
- v0.3 species-bootstrap SE / log-applicability effect table;
- measurement-aware crossed meta-analysis outputs and cluster-bootstrap table;
- training-only BLUP portability predictions;
- correlated-trait zero-family-effect null outputs;
- canonical result JSON files used by the manuscript;
- analysis and figure-generation scripts;
- prospective design / robustness contracts.

## Excluded

- Git history and pull-request metadata;
- author names, affiliations, ORCID identifiers and acknowledgements;
- public development-repository URLs;
- raw species-level BIEN trait records and species-level states, which were not persisted by the frozen analysis routes;
- title page and cover letter.

## Third-party data

The analyses draw species-level trait records from BIEN under the frozen extraction contract and use the frozen phylogenetic backbone / V.PhyloMaker2 workflow described in the Methods. The anonymous bundle contains the derived 201-system effect tables and all downstream data needed to reproduce the manuscript-level robustness analyses and figures.

## Identity firewall

The generated archive must:
- contain no `.git` directory;
- contain no repository-owner identifier;
- contain no email address;
- contain no `github.com` URL;
- use neutral file and directory names;
- retain the AI-assisted-development disclosure in analysis scripts.

## Publication archive

The review bundle is not the final public archive. Upon acceptance, the accepted data/code package should be deposited in an appropriate public repository with a persistent identifier and cited in the final Data Availability statement.
