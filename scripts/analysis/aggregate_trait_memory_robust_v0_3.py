#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
from __future__ import annotations
import argparse,csv,json,math,statistics
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--reference-effects",type=Path,required=True)
ap.add_argument("--core-table",type=Path,required=True)
ap.add_argument("--out-csv",type=Path,required=True)
ap.add_argument("--out-json",type=Path,required=True)
a=ap.parse_args()
a.out_csv.parent.mkdir(parents=True,exist_ok=True)
a.out_json.parent.mkdir(parents=True,exist_ok=True)

design=json.loads(Path("data/trait_memory_robustness_design_v0_3.json").read_text())
if design["status"]!="FROZEN_BEFORE_TRAIT_MEMORY_ROBUSTNESS_OUTCOMES":
    raise SystemExit("robustness design not frozen")

with a.core_table.open(newline="") as fh:
    core=list(csv.DictReader(fh))
with a.reference_effects.open(newline="") as fh:
    ref=list(csv.DictReader(fh))
if len(core)!=201 or len(ref)!=201:
    raise SystemExit("frozen 201-system population changed")
core_keys={(r["family"],r["trait_name"]) for r in core}
ref_map={(r["family"],r["trait_name"]):r for r in ref}
if set(ref_map)!=core_keys:
    raise SystemExit("reference effect keys differ from frozen core")

rows=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    k=(x["family"],x["trait_name"])
    if k not in core_keys:
        raise SystemExit(f"robust effect outside frozen core: {k}")
    def val(axis,key):
        z=x[axis].get(key)
        return "" if z is None else z
    rows.append({
      "system_id":x["system_id"],
      "family":x["family"],
      "trait_name":x["trait_name"],
      "status":x["status"],
      "n_species_S3":x["S3"]["n_species"],
      "n_species_prune":x["prune_only"]["n_species"],
      "S3_raw_rho":x["S3"]["raw_rho"],
      "S3_raw_se":val("S3","raw_bootstrap_se"),
      "S3_boot_valid":x["S3"]["raw_bootstrap_valid_fraction"],
      "S3_log_status":x["S3"]["log_status"],
      "S3_n_nonpositive":x["S3"]["n_nonpositive"],
      "S3_log_rho":val("S3","log_rho"),
      "S3_log_se":val("S3","log_bootstrap_se"),
      "S3_log_boot_valid":val("S3","log_bootstrap_valid_fraction"),
      "prune_raw_rho":x["prune_only"]["raw_rho"],
      "prune_raw_se":val("prune_only","raw_bootstrap_se"),
      "prune_boot_valid":x["prune_only"]["raw_bootstrap_valid_fraction"],
      "prune_log_status":x["prune_only"]["log_status"],
      "prune_n_nonpositive":x["prune_only"]["n_nonpositive"],
      "prune_log_rho":val("prune_only","log_rho"),
      "prune_log_se":val("prune_only","log_bootstrap_se"),
      "prune_log_boot_valid":val("prune_only","log_bootstrap_valid_fraction")
    })
if len(rows)!=201 or len({(r["family"],r["trait_name"]) for r in rows})!=201:
    raise SystemExit("robust system outputs incomplete or duplicated")

rows.sort(key=lambda r:(r["family"],r["trait_name"]))
mismatches=[]
deltas=[]
for r in rows:
    rr=ref_map[(r["family"],r["trait_name"])]
    for newk,oldk,axis in [
        ("S3_raw_rho","S3_rho","S3"),
        ("prune_raw_rho","prune_only_rho","prune_only"),
    ]:
        new=float(r[newk]); old=float(rr[oldk])
        delta=abs(new-old); deltas.append(delta)
        if f"{new:.4f}" != f"{old:.4f}" and delta>5e-5:
            mismatches.append({
              "family":r["family"],"trait_name":r["trait_name"],"axis":axis,
              "new":new,"reference":old,"abs_delta":delta
            })

identity_pass=len(mismatches)==0
all_raw_se=all(
    r["status"]=="TRAIT_MEMORY_ROBUST_SYSTEM_ESTIMATED"
    and r["S3_raw_se"]!="" and r["prune_raw_se"]!=""
    for r in rows
)
all_log=all(
    r["S3_log_status"]=="LOG_POSITIVE"
    and r["prune_log_status"]=="LOG_POSITIVE"
    and r["S3_log_rho"]!="" and r["prune_log_rho"]!=""
    for r in rows
)

fields=list(rows[0])
with a.out_csv.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=fields)
    w.writeheader(); w.writerows(rows)

def _pearson(x,y):
    if len(x)!=len(y) or len(x)<2:
        raise ValueError("invalid correlation vectors")
    mx=sum(x)/len(x); my=sum(y)/len(y)
    dx=[v-mx for v in x]; dy=[v-my for v in y]
    vx=sum(v*v for v in dx); vy=sum(v*v for v in dy)
    if vx<=0 or vy<=0:
        return float("nan")
    return sum(a*b for a,b in zip(dx,dy))/math.sqrt(vx*vy)

def _midranks(values):
    order=sorted(range(len(values)),key=lambda i:values[i])
    ranks=[0.0]*len(values)
    k=0
    while k<len(order):
        j=k+1
        while j<len(order) and values[order[j]]==values[order[k]]:
            j+=1
        mid=((k+1)+j)/2.0
        for z in range(k,j):
            ranks[order[z]]=mid
        k=j
    return ranks

def corr(a1,a2,kind="pearson"):
    x=[float(v) for v in a1]; y=[float(v) for v in a2]
    if kind=="pearson":
        return float(_pearson(x,y))
    return float(_pearson(_midranks(x),_midranks(y)))

log_summary=None
if all_log:
    raw=[float(r["S3_raw_rho"]) for r in rows]
    lg=[float(r["S3_log_rho"]) for r in rows]
    abs_change=[abs(a-b) for a,b in zip(lg,raw)]
    def sgn(v):
        return 1 if v>0 else (-1 if v<0 else 0)
    log_summary={
      "n_systems":len(rows),
      "raw_log_pearson":corr(raw,lg,"pearson"),
      "raw_log_spearman":corr(raw,lg,"spearman"),
      "sign_agreement":sum(sgn(a)==sgn(b) for a,b in zip(raw,lg))/len(raw),
      "median_abs_change":float(statistics.median(abs_change)),
      "max_abs_change":float(max(abs_change))
    }

status=(
  "HOLD_TRAIT_MEMORY_ROBUSTNESS_REFERENCE_DRIFT" if not identity_pass else
  "HOLD_TRAIT_MEMORY_ROBUSTNESS_BOOTSTRAP_VALIDITY" if not all_raw_se else
  "TRAIT_MEMORY_ROBUST_EFFECTS_AGGREGATED"
)
out={
  "version":"v0.3",
  "status":status,
  "n_systems":len(rows),
  "n_families":len({r["family"] for r in rows}),
  "n_traits":len({r["trait_name"] for r in rows}),
  "reference_identity":{
    "pass":identity_pass,
    "archive_precision_decimal_places":4,
    "max_abs_unrounded_delta":max(deltas) if deltas else None,
    "n_mismatches":len(mismatches),
    "first_mismatches":mismatches[:10]
  },
  "measurement_error":{
    "all_systems_have_valid_raw_se":all_raw_se,
    "median_S3_se":float(statistics.median([float(r["S3_raw_se"]) for r in rows if r["S3_raw_se"]!=""])),
    "median_prune_se":float(statistics.median([float(r["prune_raw_se"]) for r in rows if r["prune_raw_se"]!=""]))
  },
  "log_scale":{
    "all_201_positive_and_estimable":all_log,
    "n_S3_nonpositive_systems":sum(int(r["S3_n_nonpositive"])>0 for r in rows),
    "n_prune_nonpositive_systems":sum(int(r["prune_n_nonpositive"])>0 for r in rows),
    "summary_if_complete":log_summary
  }
}
a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
if not identity_pass:
    raise SystemExit("reference identity gate failed")
if not all_raw_se:
    raise SystemExit("bootstrap SE validity gate failed")
