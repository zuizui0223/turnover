#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--batch-json",type=Path,required=True)
ap.add_argument("--crosswalk",type=Path,required=True)
ap.add_argument("--source-dir",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
ap.add_argument("--r-script",type=Path,required=True)
a=ap.parse_args()
systems=json.loads(a.batch_json.read_text())
a.out_dir.mkdir(parents=True,exist_ok=True)
for s in systems:
    source=a.source_dir/f"{s['id']}.json"
    if not source.exists():
        raise FileNotFoundError(source)
    out=a.out_dir/f"{s['id']}.json"
    cmd=[
      "Rscript",str(a.r_script),
      "--family",s["family"],
      "--trait",s["trait_name"],
      "--id",s["id"],
      "--crosswalk",str(a.crosswalk),
      "--source-json",str(source),
      "--out",str(out)
    ]
    subprocess.run(cmd,check=True)
print(json.dumps({"status":"BATCH_COMPLETE","n_systems":len(systems),"ids":[s["id"] for s in systems]},indent=2))
