#!/usr/bin/env python3
"""NHM plant-traits source-only data dictionary check on pinned public source commit.

No numeric trait cell is interpreted, no phenotype is compared, and no K or
phylogenetic inference can occur. Inspect only header/metadata keys and row
counts before authorizing a pre-specified matched-taxon support extractor.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

SOURCE_SHA = "4843c22bb2fc91018d9828dcddebf067c83b1097"
FILES = {
    "herbarium_leaf": "output/raw/cv-traits/all_leaf_measurements.csv",
    "description_traits": "output/raw/ocr-traits/combined.csv",
    "taxonomy": "input/wfo-angiosperms.csv",
}
META_WORDS = ("species","taxon","scientific","family","genus","name","barcode",
              "source","site","specimen","accession","gbif","wfo","trait","id","file")


def checksum(path):
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda:handle.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def meta_column(name):
    n = re.sub(r"[^a-z0-9]","",str(name or "").lower())
    if n in {"length","width","area","value","measurement","height","perimeter"}:
        return False
    return any(key in n for key in META_WORDS)


def audit_file(path):
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as handle:
        reader=csv.DictReader(handle)
        header=reader.fieldnames
        if not header:
            raise ValueError("Empty header: "+str(path))
        metadata_fields=[f for f in header if f and meta_column(f)]
        count=0
        examples=[]
        for row in reader:
            count+=1
            if len(examples)<3:
                examples.append({
                    k:str(row.get(k) or "").strip()[:120]
                    for k in metadata_fields[:15]
                })
    return {
        "filename":path.name,
        "sha256":checksum(path),
        "size_bytes":path.stat().st_size,
        "header":header,
        "metadata_fields":metadata_fields,
        "first_3_metadata_rows_only":examples,
        "row_count":count
    }


def main():
    p=argparse.ArgumentParser()
    for name in FILES:
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report={
        "status":"SOURCE_SCHEMA_PREFLIGHT_ONLY",
        "third_party_repo":"NaturalHistoryMuseum/plant-traits",
        "pinned_commit":SOURCE_SHA,
        "license":"CC-BY 4.0 as published by repository README",
        "no_trait_magnitudes_compared":True,
        "no_K_or_ancestral_process_estimated":True,
        "files":{}
    }
    for name in FILES:
        report["files"][name]=audit_file(getattr(a,name))
    a.out.parent.mkdir(exist_ok=True,parents=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("NHM_METADATA_PREFLIGHT="+json.dumps(report,ensure_ascii=False))


if __name__=="__main__":
    main()
