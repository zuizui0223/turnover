#!/usr/bin/env python3
"""Technical raw-AusTraits-v7 to matched-tip K smoke, not new biological inference."""
import argparse,hashlib,json,math
from pathlib import Path

BASE=Path("results/austraits_organ_paper_frozen_rebuild_inputs_v0_1")
SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
PAIRS=[("Casuarinaceae","fruit_length","leaf_length",47),
       ("Asteraceae","fruit_width","leaf_length",177)]
STATUS="PASS_PUBLIC_AUSTRAITS_V7_RAW_TO_K_TECHNICAL_SMOKE"

def need(x,label):
    if not x:raise AssertionError(label)

def source_check(base):
    m=json.loads((base/"frozen_rebuild_manifest.json").read_text())
    need(m["status"]=="PASS_FROZEN_ORIGINAL_AGGREGATE_REBUILD_REFERENCES_V0_1",
         "Original reference manifest invalid")
    need(m["source_parquet_sha256"]==SHA and m["original_systems"]==254
         and m["matched_supported_pairs"]==760,"Original cohort or source drift")
    for name,sha in m["source_byte_sha256"].items():
        need(hashlib.sha256((base/name).read_bytes()).hexdigest()==sha,
             "Archived reference mutated: "+name)
    s=json.loads((base/"shared_taxon_pair_support.json").read_text())
    need(s["status"]=="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"
         and s["qualifying_family_trait_pairs"]==760,
         "Source-only eligibility graph changed")
    return s

def prepare(base,out):
    s=source_check(base)
    rows=[]
    for f,a,b,n in PAIRS:
        matches=[r for r in s["family_trait_pair_support"]
                 if (r["family"],r["trait_A"],r["trait_B"])==(f,a,b)]
        need(len(matches)==1,"No unique prior source-only pair")
        row=matches[0]
        need(row["qualifies_20_common_species"] and
             row["n_common_species_same_genus"]==n,
             "Source-only original tip count drift")
        rows.append(row)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n")
    return {"status":"PASS_FROZEN_K_BLIND_PAIR_IDENTITIES",
            "pairs":[{"family":x["family"],"n_original_common_species":
                      x["n_common_species_same_genus"]} for x in rows]}

def historical_matched_K(base):
    "Check SHA-pinned original 24 R-batch outputs and return original per-pair values."
    prior=Path("results/austraits_organ_paper_original_pair_K_v0_1")
    manifest=json.loads((prior/"original_pair_k_reference_manifest.json").read_text())
    need(manifest["status"]=="PASS_PRESERVED_760_ORIGINAL_MATCHED_TIP_K_REGRESSION_REFERENCES"
         and manifest["n_original_matched_pairs"]==760,
         "Historical per-pair matched R K archive missing")
    need(manifest["parent_rebuild_manifest_sha256"]==
         hashlib.sha256((base/"frozen_rebuild_manifest.json").read_bytes()).hexdigest(),
         "Historical per-pair outcomes do not share the exact source cohort")
    found={}
    for filename,sha in manifest["files"].items():
        data=(prior/filename).read_bytes()
        need(hashlib.sha256(data).hexdigest()==sha,
             "Historical raw R pair outcome archive tampered: "+filename)
        b=json.loads(data)
        for p in b["pairs"]:
            key=(p["family"],p["trait_A"],p["trait_B"])
            need(key not in found, "Duplicate historical pair identity")
            found[key]=p
    need(len(found)==760,"Historical matched K reference incomplete")
    return found


def finish(base,batch,raw,parquet,out):
    source_check(base)
    historical=historical_matched_K(base)
    need(hashlib.sha256(parquet.read_bytes()).hexdigest()==SHA,
         "Downloaded public Parquet differs from original SHA256")
    items=json.loads(batch.read_text())
    z=json.loads(raw.read_text())
    need(z["status"]=="AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED"
         and z["n_family_trait_pairs"]==len(z["pairs"])==2,
         "Original R K estimator did not produce both results")
    need(z["no_species_names_or_raw_values_persisted"] is True,
         "Raw species values leaked into K report")
    indexed={(v["family"],v["trait_A"],v["trait_B"]):v for v in z["pairs"]}
    summary=[]
    for orig in items:
        key=(orig["family"],orig["trait_A"],orig["trait_B"])
        need(key in indexed,"Source-qualified pair dropped from R results")
        v=indexed[key]
        need(key in historical,"No historical matched K reference for original case")
        earlier=historical[key]
        need(v["n_shared_species"]==orig["n_common_species_same_genus"]==
             earlier["n_shared_species"],
             "Original vs reconstructed source-tip cohort differs")
        tree={}
        for t in ("S3","prune_only"):
            x=v["axes"][t]
            previous=earlier["axes"][t]
            need(x["status"]=="PASS" and x["n_tips"]>=20,
                 "Original comparison missing native K tree support: "+t)
            a,b=float(x["K_A"]),float(x["K_B"])
            need(math.isfinite(a) and math.isfinite(b) and a>0 and b>0,
                 "Invalid raw-derived K")
            need(abs((math.log(a)-math.log(b))-float(x["delta_shared_logK"]))<2e-9,
                 "K values mismatch logged original contrast")
            need(abs((float(x["delta_shared_logK"])-float(x["delta_original_logK"]))
                     -float(x["delta_support_shift"]))<2e-9,
                 "Support-versus-original comparison arithmetic mismatch")
            need(previous["status"]=="PASS" and
                 previous["n_tips"]==x["n_tips"],
                 "Exact original tree tip geometry differs in fresh reconstruction")
            max_difference=max(abs(float(x[k])-float(previous[k]))
                               for k in ("K_A","K_B","delta_shared_logK",
                                         "delta_original_logK","delta_support_shift"))
            need(all(math.isclose(float(x[k]),float(previous[k]),
                     rel_tol=1e-7,abs_tol=2e-8) for k in
                     ("K_A","K_B","delta_shared_logK",
                      "delta_original_logK","delta_support_shift")),
                 "Recomputed exact original matched K values do not agree")
            tree[t]={"status":"PASS","n_tips":x["n_tips"],
                     "K_log_contrast_identity_pass":True,
                     "historical_numeric_K_regression_pass":True,
                     "max_abs_K_or_log_contrast_difference":max_difference}
        summary.append({"family":v["family"],"trait_A":v["trait_A"],
                        "trait_B":v["trait_B"],
                        "original_matched_species_count":v["n_shared_species"],
                        "axes":tree})
    result={"status":STATUS,"dataset":"AusTraits v7.0.0",
            "exact_original_source_parquet_sha256":SHA,
            "frozen_original_reference_integrity":True,
            "source_native_species_states_and_matched_tree_K_recomputed":True,
            "n_technical_smoke_pairs":2,
            "original_full_source_supported_comparisons":760,
            "all_760_original_pairs_recomputed":False,
            "exact_original_matched_pair_numeric_parity_verified":True,
            "original_matched_K_reference_batch_count":24,
            "independent_primary_measurement_replication":False,
            "new_biological_support_claim":False,"original_raw_values_saved":False,
            "pairs":summary}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=["prepare","finish"])
    p.add_argument("--references",type=Path,default=BASE)
    p.add_argument("--batch",required=True,type=Path)
    p.add_argument("--raw-result",type=Path)
    p.add_argument("--parquet",type=Path)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    if a.mode=="prepare":
        z=prepare(a.references,a.batch)
    else:
        need(a.raw_result and a.parquet and a.report,"Finish requires R result and raw source")
        z=finish(a.references,a.batch,a.raw_result,a.parquet,a.report)
    print(json.dumps(z,sort_keys=True))
if __name__=="__main__":main()
