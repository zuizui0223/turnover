#!/usr/bin/env python3
"""Check full 760-pair eligibility reproducibility using exact public AusTraits v7.

Only counts/common-species source qualification. It does not estimate trait K,
test an organ hypothesis, or record source species/measurements.
"""
import argparse,copy,hashlib,json
from pathlib import Path

STATUS="PASS_PUBLIC_AUSTRAITS_V7_ALL_760_SOURCE_OVERLAP_REBUILT"

def need(x,msg):
    if not x:raise AssertionError(msg)

def verify(original,new):
    expected={
        "original_graph":{"systems":254,"families":42,"traits":13},
        "named_graph":{"systems":249,"families":42,"traits":12},
        "minimum_common_species":20,
        "qualifying_family_trait_pairs":760,
    }
    for item,val in expected.items():
        need(original[item]==val and new[item]==val,
             "Original and regenerated support contract drift: "+item)
    need(new["status"]==original["status"]==
         "AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED",
         "Original source-only audit status changed")
    for field in ("family_trait_pair_support","trait_pairs","original_graph",
                  "named_graph","total_family_trait_pairs_present",
                  "qualifying_pair_types","pair_types_with_at_least_5_qualified_families",
                  "no_species_or_trait_values_persisted"):
        need(new[field]==original[field],
             "Public v7 raw rebuild disagrees with archived support: "+field)
    pairs=original["family_trait_pair_support"]
    need(len(pairs)==770 and sum(x["qualifies_20_common_species"] for x in pairs)==760,
         "Original full source-only support graph is not 770/760")
    need(new["no_species_or_trait_values_persisted"] is True,
         "Regeneration leaked species or raw measurements")
    return {"status":STATUS,
            "original_systems":254,"named_systems":249,"original_families":42,
            "source_only_family_named_trait_pairs":770,
            "qualifying_matched_species_pairs":760,
            "trait_pair_types":66,
            "all_pair_support_rows_identical":True,
            "all_family_trait_pair_counts_identical":True,
            "original_trait_K_recalculated":False,
            "original_species_values_exported":False,
            "new_biological_support":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--recomputed",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    old=json.loads(args.original.read_text())
    new=json.loads(args.recomputed.read_text())
    result=verify(old,new)
    if args.self_test:
        bad=copy.deepcopy(new)
        bad["family_trait_pair_support"][0]["n_common_species_same_genus"]+=1
        try:verify(old,bad)
        except AssertionError:pass
        else:raise AssertionError("Source support mutation not detected")
    result["original_source_support_sha256"]=hashlib.sha256(args.original.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
