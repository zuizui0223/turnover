# AusTraits replication — authoritative downstream rebuild after exact crosswalk

Status: frozen while the exact pinned V.PhyloMaker2 v0.4.3 crosswalk is running. No AusTraits memory rho has been opened.

## Why this rebuild is mandatory

The first vectorized crosswalk was superseded after actual pinned V.PhyloMaker2 status counts disagreed for some systems. Consequently, every downstream object derived from that vectorized crosswalk is non-authoritative for the final replication, including the earlier pre-core, geometry preparation, informativeness run, provenance core and model-informativeness inputs.

No biological threshold changes.

## Authoritative order

After exact v0.4.3 crosswalk completes:

1. **Aggregate exact crosswalk**
   - require all 3,593 semantic-valid family × trait systems;
   - use only actual V.PhyloMaker2 `species.list$status`;
   - apply unchanged primary-resolvable >=20 and prune-only >=20.

2. **Rebuild necessary crossed core**
   - simultaneous iterative family degree >=2;
   - trait degree >=5;
   - no outcome use.

3. **Rebuild exact species-geometry signatures**
   - from exact-crosswalk admitted species sets;
   - deduplicate identical phylogenetic geometries only by exact hash;
   - retain a deterministic canonical representative and full system map.

4. **Run known-truth temporal informativeness**
   - benchmark rho=0.15;
   - MAE <=0.10;
   - directional >=0.80;
   - valid fraction >=0.90;
   - both S3 and prune-only;
   - no pair subsampling.

5. **Build final crossed core**
   - family degree >=2;
   - trait degree >=5;
   - >=12 families;
   - >=4 traits;
   - one connected component.

6. **Run provenance-overlap audit**
   - label replication as independent-source, low-overlap, or independent-compilation validation;
   - overlap cannot select systems.

7. **Run graph-specific conditional-family-repeatability model-informativeness**
   - before any real AusTraits memory rho.

8. **Only if all gates pass, open real AusTraits rho**
   - test the pre-frozen replication target;
   - do not tune to BIEN estimates.

## Explicitly superseded

Do not use for final inference:
- vectorized crosswalk run 37113852461;
- geometry-prep run 37128923077;
- final core/informativeness run 37129060487 or descendants;
- any provenance or model-informativeness result based on those objects.

## Failure interpretation

A failure at any pre-outcome gate is a **replication qualification failure**, not evidence that the BIEN biological result failed to replicate.

Only a qualified AusTraits core with opened real rho can yield biological replication/concordance/discordance language.
