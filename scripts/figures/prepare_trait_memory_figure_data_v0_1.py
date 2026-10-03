#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
a=ap.parse_args()
a.out_dir.mkdir(parents=True,exist_ok=True)

rows=list(csv.DictReader(a.effects.open(newline="")))
if len(rows)!=201: raise SystemExit(f"expected 201 effects, got {len(rows)}")
families=sorted({r["family"] for r in rows})
traits=sorted({r["trait_name"] for r in rows})
if len(families)!=45 or len(traits)!=12: raise SystemExit("fixed core dimensions changed")

# Figure 1/2 matrix data: deterministic alphabetical ordering only.
with (a.out_dir/"memory_matrix.csv").open("w",newline="") as fh:
    fields=["family"]+traits
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
    lookup={(r["family"],r["trait_name"]):r for r in rows}
    for fam in families:
        rec={"family":fam}
        for tr in traits:
            x=lookup.get((fam,tr))
            rec[tr]="" if x is None else x["S3_rho"]
        w.writerow(rec)

# Figure 2/4 long data.
with (a.out_dir/"memory_effects.csv").open("w",newline="") as fh:
    fields=["family","trait_name","S3_rho","prune_only_rho","n_species_S3","n_species_prune"]
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
    for r in sorted(rows,key=lambda z:(z["family"],z["trait_name"])):
        w.writerow({k:r[k] for k in fields})

# Figure 3 summary from committed frozen result files.
root=Path(".")
rep=json.loads((root/"results/trait_memory_repeatability_v0_2/result.json").read_text())
port=json.loads((root/"results/trait_memory_portability_v0_2/result.json").read_text())
lin=json.loads((root/"results/lineage_memory_repeatability_v0_2/result.json").read_text())
summary=[
 {"panel":"repeatability","axis":"S3","quantity":"family","estimate":rep["primary_S3"]["R_family"],"lo":rep["bootstrap"]["ci95"]["R_family"][0],"hi":rep["bootstrap"]["ci95"]["R_family"][1]},
 {"panel":"repeatability","axis":"S3","quantity":"trait","estimate":rep["primary_S3"]["R_trait"],"lo":rep["bootstrap"]["ci95"]["R_trait"][0],"hi":rep["bootstrap"]["ci95"]["R_trait"][1]},
 {"panel":"repeatability","axis":"S3","quantity":"unresolved_system_residual","estimate":rep["primary_S3"]["R_residual"],"lo":rep["bootstrap"]["ci95"]["R_residual"][0],"hi":rep["bootstrap"]["ci95"]["R_residual"][1]},
 {"panel":"portability","axis":"S3","quantity":"gain","estimate":port["S3"]["gain"],"lo":port["S3"]["null_q025"],"hi":port["S3"]["null_q975"],"p":port["S3"]["p_value"]},
 {"panel":"portability","axis":"prune_only","quantity":"gain","estimate":port["prune_only"]["gain"],"lo":port["prune_only"]["null_q025"],"hi":port["prune_only"]["null_q975"],"p":port["prune_only"]["p_value"]},
 {"panel":"conditional_family","axis":"S3","quantity":"repeatability","estimate":lin["primary_S3"]["conditional_family_repeatability"],"lo":lin["bootstrap"]["ci95_conditional_family_repeatability"][0],"hi":lin["bootstrap"]["ci95_conditional_family_repeatability"][1]},
 {"panel":"conditional_family","axis":"prune_only","quantity":"repeatability","estimate":lin["prune_only_sensitivity"]["conditional_family_repeatability"],"lo":"","hi":""}
]
fields=sorted({k for r in summary for k in r})
with (a.out_dir/"figure3_summary.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(summary)

out={
 "version":"v0.1",
 "status":"TRAIT_MEMORY_FIGURE_DATA_PREPARED",
 "n_systems":len(rows),"n_families":len(families),"n_traits":len(traits),
 "ordering":"alphabetical only; no outcome-based clustering",
 "files":["memory_matrix.csv","memory_effects.csv","figure3_summary.csv"]
}
(a.out_dir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
