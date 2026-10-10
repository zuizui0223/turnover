#!/usr/bin/env python3
"""Metadata-only external source triage for five frozen named-trait predictions.

No K, observed trait states, phylogenetic distances, source error ratios or
recalculated hypotheses are accessed. A 5-trait trait-index listing is NOT
proof of family-species support, provenance independence or trait semantics.
Only blocks obviously impossible small datasets or marks larger compilations
for strict *future* primary dataset and semantic audits.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

STATUS="EXTERNAL_NAMED_RANK_SOURCE_METADATA_TRIAGE_ONLY"
EXPECTED_TARGETS=("seed_width","leaf_area","seed_dry_mass","leaf_width","petiole_length")


def audit(d:dict)->dict:
    if d.get("status")!="EXTERNAL_NAMED_RANK_SOURCE_CANDIDATES_METADATA_ONLY_PRE_VALIDATION_HOLD":
        raise ValueError("candidate inventory is not metadata-only")
    gate=d["frozen_primary_minimums"]
    required=gate["family_min_species_per_trait"]*gate["min_families_per_trait"]
    if (gate["family_min_species_per_trait"],gate["min_families_per_trait"],
        gate["min_families_with_two_traits"],gate["min_signed_traits_supported"])!=(20,10,10,4):
        raise ValueError("changed frozen external validation gate")
    terms=d["discovery_only_targets"]
    if len(terms)!=5 or {t["name"] for t in terms}!=set(EXPECTED_TARGETS):
        raise ValueError("five signed discovery traits not fixed")
    seen=set()
    outputs={}
    for source in d["sources"]:
        sid=source["id"]
        if sid in seen:raise ValueError("duplicate candidate")
        seen.add(sid)
        traits=source["listed_target_traits"]
        if len(traits)!=len(set(traits)) or not set(traits)<=set(EXPECTED_TARGETS):
            raise ValueError("invalid source candidate trait names")
        ceiling=source["maximum_possible_species_count"]
        not_enough=ceiling is not None and int(ceiling)<required
        trait_shortage=len(traits)<gate["min_signed_traits_supported"]
        if not_enough:
            verdict="FAIL_HARD_TOTAL_SPECIES_UPPER_BOUND"
        elif trait_shortage:
            verdict="HOLD_FEWER_THAN_FOUR_TARGET_TRAITS"
        else:
            verdict="HOLD_PRIMARY_PROVENANCE_TRAIT_SEMANTICS_AND_FAMILY_SUPPORT"
        # None of the public sources is certified for independent validation.
        # Even a claimed boolean is not sufficient without recorded source IDs,
        # raw-measurement audit, primary DOI overlap and frozen tree graph.
        out={
          "candidate_id":sid,"verdict":verdict,
          "n_listed_target_traits":len(traits),
          "minimum_distinct_species_per_trait_to_meet_frozen_gate":required,
          "source_total_species_upper_bound":ceiling,
          "total_species_necessary_condition_met":False if not_enough else None,
          "primary_measurement_independence_established":False,
          "semantic_match_established":False,
          "tip_family_graph_support_established":False,
          "K_outcome_accessed":False,
          "permission_to_claim_independent_validation":False
        }
        outputs[sid]=out
    if len(outputs)!=3:raise ValueError("expected complete three-source first-stage registry")
    return {
      "version":"v0.1","status":STATUS,
      "original_external_protocol":d["parent_protocol"],
      "qualified_independent_validation_sources":0,
      "candidate_count":len(outputs),
      "hard_total_species_ineligible":sum(z["verdict"]=="FAIL_HARD_TOTAL_SPECIES_UPPER_BOUND" for z in outputs.values()),
      "holds_require_new_source_metadata_or_qualified_raw_input":sum(z["verdict"].startswith("HOLD_") for z in outputs.values()),
      "candidates":outputs,
      "scientific_boundary":"A release, trait registry and total species counts do not establish independently sampled observations or adequate matched family graphs. No target K/trait measurements opened."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidates",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(json.loads(a.candidates.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"qualified_independent_validation_sources":0,
         "hard_total_species_ineligible":result["hard_total_species_ineligible"],
         "holds":result["holds_require_new_source_metadata_or_qualified_raw_input"]}))

if __name__=="__main__":
    main()
