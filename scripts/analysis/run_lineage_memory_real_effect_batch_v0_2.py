#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--batch-json",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
ap.add_argument("--r-script",type=Path,required=True)
a=ap.parse_args()
systems=json.loads(a.batch_json.read_text())
a.out_dir.mkdir(parents=True,exist_ok=True)
for s in systems:
    out=a.out_dir/f"{s['id']}.json"
    cmd=[
      "Rscript",str(a.r_script),
      "--family",s["family"],"--trait",s["trait_name"],"--class",s["semantic_class"],
      "--id",s["id"],"--out",str(out)
    ]
    subprocess.run(cmd,check=True)
print(json.dumps({"status":"LINEAGE_MEMORY_REAL_BATCH_COMPLETE","n_systems":len(systems)},indent=2))
