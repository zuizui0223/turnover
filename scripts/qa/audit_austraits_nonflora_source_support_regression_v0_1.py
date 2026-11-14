#!/usr/bin/env python3
"""Verify five-electronic-flora and shared nonflora DatasetID eligibility from public v7.

Source-only family×trait support; no original K magnitudes, raw species names
or new ecological hypotheses are calculated or published by this audit.
"""
import argparse,copy,hashlib,json,math
from pathlib import Path

STATUS="PASS_PUBLIC_AUSTRAITS_V7_REBUILT_NONFLORA_283_142_K_BLIND_SUPPORT"
EXPECTED="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_SOURCE_SUPPORT_AUDITED"

def need(x,msg):
    if not x:raise AssertionError(msg)

def same(a,b,path="root"):
    if isinstance(a,dict):
        need(isinstance(b,dict) and set(a)==set(b),
             "Source-only support keys differ: "+path)
        for k in a:same(a[k],b[k],path+"."+k)
    elif isinstance(a,list):
        need(isinstance(b,list) and len(a)==len(b),
             "Source-only support list differs: "+path)
        for i,(x,y) in enumerate(zip(a,b)):same(x,y,path+"["+str(i)+"]")
    elif isinstance(a,(int,float)) and not isinstance(a,bool):
        need(isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=0,abs_tol=1e-12),
             "Source-only eligibility count differs: "+path)
    else:
        need(a==b,"Source-only eligibility identity changed: "+path)

def audit(old,new):
    need(old["status"]==new["status"]==EXPECTED,"Not source-only old/new nonflora results")
    need(old["original_pairs"]==new["original_pairs"]==760,
         "Original 760 K-blind source pair population lost")
    need(old["original_cross_organ_pairs"]==new["original_cross_organ_pairs"]==406,
         "Original 406 cross-organ pair family cohort drift")
    need(new["no_K_effect_values_accessed_or_recomputed"] is True
         and new["no_species_measurement_values_or_original_record_ids_exported"] is True,
         "Recomputed K outcomes or raw measurements leaked into source-only audit")
    need(new["subsets"]["cross_organ"]["qualifying_20_same_nonflora_dataset_pairs"]==142,
         "Source-only strict 142 same-DatasetID graph changed")
    same(old,new)
    return {"status":STATUS,"original_eligible_K_blind_pairs":760,
            "full_source_only_support_data_exactly_reproduced":True,
            "strict_same_nonflora_dataset_K_blind_pairs":142,
            "raw_trait_species_or_study_values_exported":False,
            "new_K_estimates_fitted":False,
            "independent_primary_measurement_replication":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--fresh",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    old=json.loads(a.original.read_text())
    new=json.loads(a.fresh.read_text())
    v=audit(old,new)
    if a.self_test:
        bad=copy.deepcopy(new)
        bad["subsets"]["cross_organ"]["qualifying_20_same_nonflora_dataset_pairs"]+=1
        try:audit(old,bad)
        except AssertionError:pass
        else:raise AssertionError("Corrupted nonflora K-blind cohort not rejected")
    v["original_source_support_sha256"]=hashlib.sha256(a.original.read_bytes()).hexdigest()
    v["fresh_source_support_sha256"]=hashlib.sha256(a.fresh.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
    print(json.dumps(v,sort_keys=True))
if __name__=="__main__":main()
