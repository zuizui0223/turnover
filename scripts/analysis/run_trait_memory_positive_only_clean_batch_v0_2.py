#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before use.
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--batch-json",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
a=ap.parse_args()
a.out_dir.mkdir(parents=True,exist_ok=True)
systems=json.loads(a.batch_json.read_text())
if not systems:
    raise SystemExit("empty Stage B batch")
for s in systems:
    out=a.out_dir/f'{s["id"]}.json'
    cmd=[
      "Rscript","scripts/analysis/run_trait_memory_positive_only_clean_system_v0_2.R",
      "--family",s["family"],"--trait",s["trait_name"],"--id",s["id"],"--out",str(out)
    ]
    print("RUN",s["id"],s["family"],s["trait_name"],flush=True)
    subprocess.run(cmd,check=True)
