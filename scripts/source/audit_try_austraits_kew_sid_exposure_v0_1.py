#!/usr/bin/env python3
"""Audit same-named Kew Seed Information Database provenance exposure on
exact original AusTraits K cohorts. Does NOT match TRY records or recalculate K.

The public historical TRY SID title is evidence of a named *source-family*
collision, while the AusTraits Kew_2019_1 archive itself compiles original
references. This counts source-native exposed species, never shared records.
"""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
import yaml

from audit_try_austraits_shared_source_exposure_v0_1 import (
    build_candidates,query_source,read_csv
)

STATUS="TRY_AUSTRAITS_KEW_SID_NAMED_SOURCE_FAMILY_EXPOSURE_AUDITED"
DESIGN="POST_PUBLIC_KEW_SOURCE_IDENTITY_PRE_KEW_SOURCE_EXPOSURE_COUNT_FROZEN"

def certify_public_metadata(design,try_catalog,kew_metadata):
    if design.get("status")!=DESIGN:raise ValueError("Kew source exposure contract not frozen")
    target=design["source_identity"]
    if (target["aus_dataset_id"]!="Kew_2019_1"
        or set(target["try_historical_candidate_ids"])!={21,565}):
        raise ValueError("Kew/TRY public lineage IDs changed")
    index={int(r["try_dataset_id"]):r for r in try_catalog}
    if len(index)!=len(try_catalog) or len(index)<100:
        raise ValueError("historical TRY public directory invalid")
    for id_,name in zip(target["try_historical_candidate_ids"],
                        target["try_historical_candidate_titles"]):
        if id_ not in index or index[id_]["try_dataset_title"].strip()!=name:
            raise ValueError(f"TRY public historical Kew dataset {id_} mismatch")
    meta=yaml.safe_load(Path(kew_metadata).read_text())
    if meta["source"]["primary"]["key"]!="Kew_2019_1":
        raise ValueError("wrong AusTraits original Kew reference")
    title=meta["source"]["primary"]["title"]
    if "Seed Information Database" not in title or "Seed Bank Database" not in title:
        raise ValueError("incorrect original Kew data source family")
    source_id=meta["dataset"]["source_id"]
    if source_id!="original_dataset_id":
        raise ValueError("original Kew dataset/source lineage field changed")
    traits={t["trait_name"] for t in meta["traits"] if t.get("trait_name")}
    if traits!={"seed_dry_mass"}:
        raise ValueError("Kew source-native phenotype label unexpectedly differs")
    if not meta["dataset"].get("custom_R_code"):
        raise ValueError("original Kew record lineage code missing")
    return {
      "austraits_source_id":"Kew_2019_1",
      "austraits_original_nested_source_field":"original_dataset_id",
      "austraits_record_trait":"seed_dry_mass",
      "try_public_historical_ids":[21,565],
      "try_v7_measurement_identity_verified":False
    }

def summarize_kew(rows,expected,meta):
    by_trait=defaultdict(lambda:{"original_species_system_cells":0,
                                 "kew_sid_source_species_system_cells":0,
                                 "kew_sid_positive_observation_keys":0,
                                 "all_systems":0,"kew_exposed_systems":0,
                                 "families":set(),"kew_exposed_families":set()})
    if len(rows)!=254:raise ValueError("changed original 254 K system cohort")
    seen=set()
    total=0
    for row in rows:
        sid,fam,trait,nsp,npos,nkew,nweak,nboth,kew_records,weak_records=row
        sid=str(sid)
        if sid in seen:raise ValueError("duplicate original K system")
        seen.add(sid)
        ref=expected.get(sid)
        if ref is None or (fam,trait)!=(ref["family"],ref["trait_name"]):
            raise ValueError("original family-trait identity changed")
        if int(nsp)!=ref["n_input_species"]:
            raise ValueError(f"original native species support changed: {sid}")
        if not (0<=int(nkew)<=int(nsp)) or int(nweak)!=0 or int(nboth)!=0 or int(weak_records)!=0:
            raise ValueError("unexpected source-class assignment")
        if int(kew_records)<int(nkew):raise ValueError("positive Kew record count too small")
        total+=int(nsp)
        v=by_trait[trait]
        v["original_species_system_cells"]+=int(nsp)
        v["kew_sid_source_species_system_cells"]+=int(nkew)
        v["kew_sid_positive_observation_keys"]+=int(kew_records)
        v["all_systems"]+=1
        v["families"].add(fam)
        if int(nkew)>0:
            v["kew_exposed_systems"]+=1
            v["kew_exposed_families"].add(fam)
    if set(seen)!=set(expected) or len(by_trait)!=13 or len({v for d in by_trait.values() for v in d["families"]})!=42:
        raise ValueError("K original graph was not fully preserved")
    summarized={
      trait:{
        "original_species_system_cells":v["original_species_system_cells"],
        "kew_sid_source_species_system_cells":v["kew_sid_source_species_system_cells"],
        "kew_sid_positive_observation_keys":v["kew_sid_positive_observation_keys"],
        "all_family_trait_systems":v["all_systems"],
        "kew_exposed_systems":v["kew_exposed_systems"],
        "kew_exposed_families":len(v["kew_exposed_families"]),
        "source_exposure_fraction":(
          v["kew_sid_source_species_system_cells"]/v["original_species_system_cells"])
      } for trait,v in sorted(by_trait.items())
    }
    return {
      "version":"v0.1","status":STATUS,
      "graph":{"systems":254,"families":42,"traits":13},
      "source_identity":meta,
      "original_species_system_cells":total,
      "kew_source_exposed_species_system_cells":sum(v["kew_sid_source_species_system_cells"] for v in summarized.values()),
      "kew_source_positive_observation_keys":sum(v["kew_sid_positive_observation_keys"] for v in summarized.values()),
      "traits":summarized,
      "external_try_v7_independent_validation_qualified":False,
      "K_effects_or_trait_values_exported":False,
      "interpretation":"Kew SID dataset lineage appears in both database families, but these AusTraits Kew_2019_1 exposures do not establish shared original individual measurements or TRY v7 membership."
    }

def main():
    p=argparse.ArgumentParser()
    for arg in ("parquet","core","observed-K","traits-yml","strong-links",
                "weak-leads","design","try-directory","kew-metadata","out"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    design=json.loads(a.design.read_text())
    meta=certify_public_metadata(design,read_csv(a.__dict__["try_directory"]),
                                 a.__dict__["kew_metadata"])
    original_source_contract=json.loads(
      Path("data/try_austraits_shared_source_exposure_contract_v0_1.json").read_text())
    cand,expected,_,_=build_candidates(
      a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],
      original_source_contract,read_csv(a.__dict__["strong_links"]),
      read_csv(a.__dict__["weak_leads"]))
    # The previous call validates original K source metadata and historical
    # Tng matching. No historical TRY data is used as a Kew measurement.
    rows=query_source(a.parquet,cand,{"Kew_2019_1"},set())
    r=summarize_kew(rows,expected,meta)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,
      "kew_cells":r["kew_source_exposed_species_system_cells"],
      "seed_dry_mass":r["traits"]["seed_dry_mass"]},sort_keys=True))

if __name__=="__main__":main()
