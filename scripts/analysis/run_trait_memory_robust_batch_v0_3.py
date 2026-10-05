#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--batch-json",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
a=ap.parse_args()
a.out_dir.mkdir(parents=True,exist_ok=True)
systems=json.loads(a.batch_json.read_text())
if not isinstance(systems,list) or not systems:
    raise SystemExit("empty batch")

for s in systems:
    cmd=[
      "Rscript","scripts/analysis/run_trait_memory_robust_system_v0_3.R",
      "--family",s["family"],
      "--trait",s["trait_name"],
      "--id",s["id"],
      "--out",str(a.out_dir/f'{s["id"]}.json')
    ]
    print("RUN",s["id"],s["family"],s["trait_name"],flush=True)
    subprocess.run(cmd,check=True)
