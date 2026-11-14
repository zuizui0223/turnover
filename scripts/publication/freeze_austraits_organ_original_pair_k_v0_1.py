#!/usr/bin/env python3
"""Preserve 24 original matched-tip R K batches for later exact numeric regression.

No new fitting; no species values, source records or names are written.
All data here are ORIGINAL already-opened derived family × trait-pair K outputs.
"""
import argparse,hashlib,json,math,shutil
from pathlib import Path

RUN=38674635870
ST="AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED"
OUTPUT="PASS_PRESERVED_760_ORIGINAL_MATCHED_TIP_K_REGRESSION_REFERENCES"

def need(ok,label):
    if not ok:raise AssertionError(label)

def freeze(source,ref,dest):
    s=json.loads((ref/"shared_taxon_pair_support.json").read_text())
    m=json.loads((ref/"frozen_rebuild_manifest.json").read_text())
    for name,sha in m["source_byte_sha256"].items():
        need(hashlib.sha256((ref/name).read_bytes()).hexdigest()==sha,
             "Source cohort archive corrupted: "+name)
    original={(x["family"],x["trait_A"],x["trait_B"]):x
              for x in s["family_trait_pair_support"]
              if x["qualifies_20_common_species"]}
    need(len(original)==760,"Missing original source-only graph")
    files=[source/("B%02d.json"%i) for i in range(1,25)]
    need(all(f.is_file() for f in files),"24 historical K batches incomplete")
    all_seen={}
    axis_pass={"S3":0,"prune_only":0}
    cross={"S3":0,"prune_only":0}
    reproductive={"fruit_height","fruit_length","fruit_width",
                  "seed_dry_mass","seed_length","seed_width"}
    hashes={}
    for f in files:
        d=json.loads(f.read_text())
        need(d["status"]==ST and d["post_original_K_outcome_exploratory"],
             "Incorrect original analysis status")
        need(d["n_family_trait_pairs"]==len(d["pairs"]),
             "Missing paired R K outcomes in original batch")
        need(d["no_species_names_or_raw_values_persisted"] is True,
             "Original source leaked species-level observations")
        for p in d["pairs"]:
            key=(p["family"],p["trait_A"],p["trait_B"])
            need(key in original and key not in all_seen,
                 "Unknown or repeated original K comparison")
            q=original[key]
            for col in ("system_A","system_B"):
                need(p[col]==q[col],"Original system identity changed: "+col)
            need(p["n_shared_species"]==q["n_common_species_same_genus"],
                 "Original K vs source-only support changed")
            need(not any(x in p for x in ("species","binomial","genus",
                                         "raw_value","value","observation_id")),
                 "Raw trait/source values in aggregated K pair")
            for axis in ("S3","prune_only"):
                a=p["axes"][axis]
                if a["status"]=="PASS":
                    axis_pass[axis]+=1
                    need(a["n_tips"]>=20 and a["n_tips"]<=p["n_shared_species"],
                         "Original native tips invalid")
                    vals=[float(a[x]) for x in ("K_A","K_B","delta_shared_logK",
                              "delta_original_logK","delta_support_shift")]
                    need(all(math.isfinite(z) for z in vals)
                         and vals[0]>0 and vals[1]>0,"Nonfinite original K values")
                    need(abs(math.log(vals[0]/vals[1])-vals[2])<2e-8,
                         "Original K ratio algebra failed")
                    if reproductive.__contains__(p["trait_A"]) != reproductive.__contains__(p["trait_B"]):
                        cross[axis]+=1
                else:
                    need(a["status"].startswith("HOLD_"),"Unrecognized original native tree hold")
            all_seen[key]=p
        hashes[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
    need(len(all_seen)==760 and axis_pass=={"S3":760,"prune_only":747},
         "Original 760/747 tree pass counts drift")
    need(cross=={"S3":406,"prune_only":397},
         "Original 406/397 cross-organ source counts drift")
    dest.mkdir(parents=True,exist_ok=True)
    for f in files:
        target=dest/f.name
        if target.exists():
            need(target.read_bytes()==f.read_bytes(),
                 "Pinned historical R K reference file drift: "+f.name)
        else:shutil.copyfile(f,target)
    summary={"status":OUTPUT,"original_run_id":RUN,
             "parent_rebuild_manifest_sha256":hashlib.sha256(
                 (ref/"frozen_rebuild_manifest.json").read_bytes()).hexdigest(),
             "files":hashes,"n_original_matched_pairs":760,
             "axis_original_pass_counts":axis_pass,
             "axis_original_cross_organ_counts":cross,
             "source_species_values_saved":False,
             "new_K_models_fitted":0,"independent_replication":False,
             "use":"Regression reference for fresh raw-to-K execution, not a biological third result."}
    path=dest/"original_pair_k_reference_manifest.json"
    data=json.dumps(summary,indent=2,sort_keys=True)+"\n"
    if path.exists():need(path.read_text()==data,"Historical match manifest changed")
    else:path.write_text(data)
    return summary

def main():
    p=argparse.ArgumentParser()
    for x in ("source","references","out-dir"):
        p.add_argument("--"+x,type=Path,required=True)
    a=p.parse_args()
    z=freeze(a.source,a.references,a.__dict__["out_dir"])
    print(json.dumps({"status":z["status"],
                      "n_original_matched_pairs":z["n_original_matched_pairs"],
                      "pass":z["axis_original_pass_counts"],
                      "sha256_file_count":len(z["files"])}))
if __name__=="__main__":main()
