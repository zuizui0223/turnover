#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before use.
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--reference",type=Path,required=True)
ap.add_argument("--stage-a-system-summary",type=Path,required=True)
ap.add_argument("--out-csv",type=Path,required=True)
ap.add_argument("--out-json",type=Path,required=True)
a=ap.parse_args()
a.out_csv.parent.mkdir(parents=True,exist_ok=True)
a.out_json.parent.mkdir(parents=True,exist_ok=True)

design=json.loads(Path("data/trait_memory_positive_only_cleaning_impact_design_v0_2.json").read_text())
if design["status"]!="FROZEN_BEFORE_POSITIVE_ONLY_CLEANING_IMPACT_OUTCOMES":
    raise SystemExit("Stage B design not frozen")

with a.reference.open(newline="") as fh:
    ref=list(csv.DictReader(fh))
with a.stage_a_system_summary.open(newline="") as fh:
    stagea=list(csv.DictReader(fh))
if len(ref)!=201 or len(stagea)!=201:
    raise SystemExit("expected frozen 201-system tables")
rmap={(r["family"],r["trait_name"]):r for r in ref}
amap={(r["family"],r["trait_name"]):r for r in stagea}
if set(rmap)!=set(amap):
    raise SystemExit("Stage A/reference graph mismatch")

contaminated={k for k,r in amap.items() if int(r["n_species_raw_nonpositive"])>0}
if len(contaminated)!=49:
    raise SystemExit(f"Stage A contaminated-system count drifted: {len(contaminated)}")

outputs={}
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    k=(x["family"],x["trait_name"])
    if k in outputs: raise SystemExit(f"duplicate Stage B output {k}")
    outputs[k]=x
if set(outputs)!=contaminated:
    missing=sorted(contaminated-set(outputs))
    extra=sorted(set(outputs)-contaminated)
    raise SystemExit(f"Stage B output keys mismatch missing={missing[:5]} extra={extra[:5]}")

rows=[]
identity_fail=[]
support_holds=[]
for k in sorted(rmap):
    rr=rmap[k]; aa=amap[k]
    fam,tr=k
    inherited=k not in contaminated
    if inherited:
        row={
          "system_id":rr["system_id"],"family":fam,"trait_name":tr,
          "cleaning_status":"CLEAN_UNCHANGED_STAGE_A",
          "original_n_species_S3":int(rr["n_species_S3"]),
          "cleaned_n_species_S3":int(rr["n_species_S3"]),
          "removed_species_S3":0,
          "original_n_species_prune":int(rr["n_species_prune"]),
          "cleaned_n_species_prune":int(rr["n_species_prune"]),
          "removed_species_prune":0,
          "original_S3_raw_rho":float(rr["S3_raw_rho"]),
          "original_prune_raw_rho":float(rr["prune_raw_rho"]),
          "S3_raw_rho":float(rr["S3_raw_rho"]),
          "S3_raw_se":float(rr["S3_raw_se"]),
          "S3_boot_valid":float(rr["S3_boot_valid"]),
          "S3_log_status":rr["S3_log_status"],
          "S3_n_nonpositive":0,
          "S3_log_rho":float(rr["S3_log_rho"]),
          "S3_log_se":float(rr["S3_log_se"]),
          "S3_log_boot_valid":float(rr["S3_log_boot_valid"]),
          "prune_raw_rho":float(rr["prune_raw_rho"]),
          "prune_raw_se":float(rr["prune_raw_se"]),
          "prune_boot_valid":float(rr["prune_boot_valid"]),
          "prune_log_status":rr["prune_log_status"],
          "prune_n_nonpositive":0,
          "prune_log_rho":float(rr["prune_log_rho"]),
          "prune_log_se":float(rr["prune_log_se"]),
          "prune_log_boot_valid":float(rr["prune_log_boot_valid"])
        }
    else:
        x=outputs[k]
        if x["status"]!="TRAIT_MEMORY_CLEANED_SYSTEM_ESTIMATED":
            support_holds.append({"family":fam,"trait_name":tr,"status":x["status"]})
            continue
        s=x["S3"]; p=x["prune_only"]
        # Identity gate: original rho at archived persistence precision and exact nonpositive counts.
        if f'{float(s["original_raw_rho"]):.4f}'!=f'{float(rr["S3_raw_rho"]):.4f}':
            identity_fail.append((fam,tr,"S3_rho",s["original_raw_rho"],rr["S3_raw_rho"]))
        if f'{float(p["original_raw_rho"]):.4f}'!=f'{float(rr["prune_raw_rho"]):.4f}':
            identity_fail.append((fam,tr,"prune_rho",p["original_raw_rho"],rr["prune_raw_rho"]))
        if int(s["original_nonpositive_species"])!=int(rr["S3_n_nonpositive"]):
            identity_fail.append((fam,tr,"S3_nonpositive",s["original_nonpositive_species"],rr["S3_n_nonpositive"]))
        if int(p["original_nonpositive_species"])!=int(rr["prune_n_nonpositive"]):
            identity_fail.append((fam,tr,"prune_nonpositive",p["original_nonpositive_species"],rr["prune_n_nonpositive"]))

        row={
          "system_id":rr["system_id"],"family":fam,"trait_name":tr,
          "cleaning_status":"CLEANED_STAGE_B",
          "original_n_species_S3":int(s["original_n_species"]),
          "cleaned_n_species_S3":int(s["cleaned_n_species"]),
          "removed_species_S3":int(s["n_species_removed_for_no_positive_state"]),
          "original_n_species_prune":int(p["original_n_species"]),
          "cleaned_n_species_prune":int(p["cleaned_n_species"]),
          "removed_species_prune":int(p["n_species_removed_for_no_positive_state"]),
          "original_S3_raw_rho":float(s["original_raw_rho"]),
          "original_prune_raw_rho":float(p["original_raw_rho"]),
          "S3_raw_rho":float(s["cleaned_raw_rho"]),
          "S3_raw_se":float(s["cleaned_raw_se"]),
          "S3_boot_valid":float(s["cleaned_raw_boot_valid_fraction"]),
          "S3_log_status":"LOG_POSITIVE",
          "S3_n_nonpositive":0,
          "S3_log_rho":float(s["cleaned_log_rho"]),
          "S3_log_se":float(s["cleaned_log_se"]),
          "S3_log_boot_valid":float(s["cleaned_log_boot_valid_fraction"]),
          "prune_raw_rho":float(p["cleaned_raw_rho"]),
          "prune_raw_se":float(p["cleaned_raw_se"]),
          "prune_boot_valid":float(p["cleaned_raw_boot_valid_fraction"]),
          "prune_log_status":"LOG_POSITIVE",
          "prune_n_nonpositive":0,
          "prune_log_rho":float(p["cleaned_log_rho"]),
          "prune_log_se":float(p["cleaned_log_se"]),
          "prune_log_boot_valid":float(p["cleaned_log_boot_valid_fraction"])
        }
    row["delta_S3_raw_rho"]=row["S3_raw_rho"]-row["original_S3_raw_rho"]
    row["delta_prune_raw_rho"]=row["prune_raw_rho"]-row["original_prune_raw_rho"]
    rows.append(row)

if support_holds:
    a.out_json.write_text(json.dumps({"version":"v0.2","status":"HOLD_CLEANED_SYSTEM_SUPPORT","holds":support_holds},indent=2)+"\n")
    raise SystemExit("HOLD_CLEANED_SYSTEM_SUPPORT")
if identity_fail:
    a.out_json.write_text(json.dumps({"version":"v0.2","status":"HOLD_CLEANING_IMPACT_REFERENCE_DRIFT","failures":identity_fail[:20]},indent=2)+"\n")
    raise SystemExit("HOLD_CLEANING_IMPACT_REFERENCE_DRIFT")
if len(rows)!=201 or len({(r["family"],r["trait_name"]) for r in rows})!=201:
    raise SystemExit("final cleaned 201-system table invalid")

# Hard inherited-row identity check.
for r in rows:
    if r["cleaning_status"]=="CLEAN_UNCHANGED_STAGE_A":
        rr=rmap[(r["family"],r["trait_name"])]
        for ck,rk in [
          ("S3_raw_rho","S3_raw_rho"),("S3_raw_se","S3_raw_se"),("S3_log_rho","S3_log_rho"),("S3_log_se","S3_log_se"),
          ("prune_raw_rho","prune_raw_rho"),("prune_raw_se","prune_raw_se"),("prune_log_rho","prune_log_rho"),("prune_log_se","prune_log_se")
        ]:
            if float(r[ck])!=float(rr[rk]):
                raise SystemExit(f"inherited row drift {r['family']} {r['trait_name']} {ck}")

fields=list(rows[0])
with a.out_csv.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)

def summarize(axis):
    old=np.array([r[f"original_{axis}_raw_rho"] for r in rows],float)
    new=np.array([r[f"{axis}_raw_rho"] for r in rows],float)
    d=new-old
    return {
      "pearson_original_cleaned":float(np.corrcoef(old,new)[0,1]),
      "spearman_original_cleaned":float(pd_spearman(old,new)),
      "median_abs_delta":float(np.median(np.abs(d))),
      "p90_abs_delta":float(np.quantile(np.abs(d),.90)),
      "max_abs_delta":float(np.max(np.abs(d))),
      "n_sign_changes":int(np.sum(np.sign(old)!=np.sign(new))),
      "n_abs_delta_ge_0_01":int(np.sum(np.abs(d)>=.01)),
      "n_abs_delta_ge_0_05":int(np.sum(np.abs(d)>=.05)),
      "n_abs_delta_ge_0_10":int(np.sum(np.abs(d)>=.10))
    }

def pd_spearman(x,y):
    # Average ranks with exact tie handling via pandas-free numpy implementation.
    def ranks(v):
        order=np.argsort(v,kind="mergesort")
        out=np.empty(len(v),float)
        i=0
        while i<len(v):
            j=i+1
            while j<len(v) and v[order[j]]==v[order[i]]: j+=1
            rank=(i+j-1)/2+1
            out[order[i:j]]=rank
            i=j
        return out
    return np.corrcoef(ranks(x),ranks(y))[0,1]

out={
  "version":"v0.2",
  "status":"TRAIT_MEMORY_POSITIVE_ONLY_CLEANED_EFFECTS_AGGREGATED",
  "n_systems":201,
  "n_recomputed_contaminated_systems":49,
  "n_inherited_clean_systems":152,
  "all_201_support_retained":True,
  "all_201_cleaned_log_available":all(r["S3_log_status"]=="LOG_POSITIVE" and r["prune_log_status"]=="LOG_POSITIVE" for r in rows),
  "species_removed":{
    "S3_total":int(sum(r["removed_species_S3"] for r in rows)),
    "prune_total":int(sum(r["removed_species_prune"] for r in rows)),
    "max_per_system_S3":int(max(r["removed_species_S3"] for r in rows)),
    "max_per_system_prune":int(max(r["removed_species_prune"] for r in rows))
  },
  "impact":{"S3":summarize("S3"),"prune":summarize("prune")},
  "hard_guard":"Cleaning membership was determined solely by Stage A raw-data validity; no rho or downstream result selected the cleaning rule."
}
a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
