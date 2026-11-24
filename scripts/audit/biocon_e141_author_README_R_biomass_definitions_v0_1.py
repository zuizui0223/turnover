#!/usr/bin/env python3
"""Read ONLY original author README/R script field definitions for BioCON E141.

Identify the semantic distinction between two differently named biomass
columns in an already completed original-source audit. No raw source CSV,
numeric source yields, new ecological outcome fits or model modifications.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

FILES={
 "README":{"id":56055623,"md5":"9ce824a94a0ad0ab455a9cfcc1589670"},
 "R_derive":{"id":54890864,"md5":"3166d7b1f8ee36e974812b3c7ac2cb48"},
 "R_figures":{"id":54890867,"md5":"92b07f0cc41cca51ecb589d6e450eca8"},
}
OUT=Path("results/biocon_e141_original_author_biomass_field_semantics_v0_1.json")
PATTERNS={
 "source_AbovegroundTotal":r"AbovegroundTotal[. _]*Biomass",
 "source_alternate_Total_Biomass":r"(?<!Aboveground)Total[. _]*Biomass",
 "source_Misc_Litter":r"Miscellaneous[. _]*Litter",
 "source_seed_or_planting":r"sown|planted|monocult|seed",
 "source_sorting":r"unsorted|sorted|cover.?based|estimate.?species|predict.?biomass",
 "source_sum":r"\browSums?\s*\(|\bsum\s*\(|\baggregate\s*\(",
 "source_outcome_year":r"\b(?:year|season|june|august)\b",
}
def load_author(name):
    x=FILES[name]
    url=f"https://ndownloader.figshare.com/files/{x['id']}"
    req=urllib.request.Request(url,headers={"User-Agent":"turnover-original-author-codebook-audit/0.1"})
    with urllib.request.urlopen(req,timeout=30) as response:
        b=response.read(200000)
    if len(b)>199999 or hashlib.md5(b).hexdigest()!=x["md5"]:
        raise ValueError("Original author file MD5 or source byte cap mismatch")
    return b.decode("utf-8-sig",errors="replace")

def assignments(line):
    stripped=line.strip()
    if stripped.startswith("#"): return []
    return re.findall(r"([A-Za-z_.][\w.]*)(?:\$\s*[A-Za-z_.][\w.]*)?\s*(?:<-|=)",stripped)[:8]

def inspect():
    out={"as_of_jst":"2026-11-24",
         "purpose":"Original author source-code semantics of distinct named biomass fields; prior 174-row source identity audit unchanged",
         "no_original_biomass_CSV_download":True,
         "no_original_numeric_outcome_values_opened":True,
         "no_original_FD_or_NDE_model_refit":True,
         "source_MD5_pass":{},"file_semantic_line_classifications":{}}
    for name in FILES:
        src=load_author(name)
        out["source_MD5_pass"][name]=True
        lines=src.splitlines()
        matches=[]
        for i,line in enumerate(lines,1):
            flags=[name for name,pattern in PATTERNS.items() if re.search(pattern,line,re.I)]
            if flags:
                matches.append({"source_line":i,"semantic_tags":flags,
                                "noncomment_assignment_lhs":assignments(line),
                                "contains_arithmetic_operator":bool(re.search(r"[+*/]|\\-\\b",line)),
                                "is_comment":line.lstrip().startswith("#")})
        out["file_semantic_line_classifications"][name]={
            "original_author_line_count":len(lines),
            "num_lines_with_source_biomass_column_tags":sum(
                any(k in v["semantic_tags"] for k in
                    ("source_AbovegroundTotal","source_alternate_Total_Biomass","source_Misc_Litter"))
                for v in matches),
            "source_line_tags":matches[:120],
        }
        # Print only bounded author field-dictionary excerpts for human review,
        # never archive excerpt in the aggregate artifact.
        if name=="README":
            for i,line in enumerate(lines,1):
                if re.search(r"(?:AbovegroundTotal|(?:^|\\b)Total Biomass|Miscellaneous Litter|clipstrip|Litter:)",line,re.I):
                    print("AUTHOR_README_SOURCE_DESCRIPTOR",i,line.strip()[:200])
        elif name=="R_derive":
            for i,line in enumerate(lines,1):
                if re.search(r"(?:AbovegroundTotal|Total[. _]*Biomass|Miscellaneous[. _]*Litter)",line,re.I):
                    print("AUTHOR_R_SOURCE_FIELD",i,line.strip()[:180])
    all_references=[
        (source,key) for source,item in out["file_semantic_line_classifications"].items()
        for x in item["source_line_tags"] for key in x["semantic_tags"]]
    out["author_separate_field_uses"]={
        name:sum(key==name for _,key in all_references)
        for name in ("source_AbovegroundTotal","source_alternate_Total_Biomass","source_Misc_Litter")}
    out["source_semantic_verdict"]="AUTHOR_FIELD_CODE_REFERENCES_EXTRACTED_NOT_YET_A_CERTIFIED_FORMULA"
    return out

def test():
    assert "source_AbovegroundTotal" in [
        k for k,p in PATTERNS.items() if re.search(p,"AbovegroundTotal Biomass")]
    assert "source_alternate_Total_Biomass" in [
        k for k,p in PATTERNS.items() if re.search(p,"Total Biomass")]
    assert assignments("df$Total.Biomass <- someValue")
    print("SYNTHETIC_SOURCE_FIELD_PATTERN_PASS")

def main():
    out={"status":"ORIGINAL_CODEBOOK_ACCESS_OR_PARSER_HOLD",
         "original_FD_NDE_model_refit":False}
    try:
        out["source_author_semantics"]=inspect()
        out["status"]="ORIGINAL_AUTHOR_README_R_FIELD_REFERENCES_PASS_FORMULA_NOT_ASSERTED"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,UnicodeError,TypeError) as exc:
        out["failure_class"]=type(exc).__name__
        if isinstance(exc,ValueError):out["source_reason"]=str(exc)[:160]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],
           "summaries":{k:{"line_count":v["original_author_line_count"],
                   "biomass_field_line_mentions":v["num_lines_with_source_biomass_column_tags"]}
             for k,v in out.get("source_author_semantics",{}).get("file_semantic_line_classifications",{}).items()}}))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    a=p.parse_args()
    if a.selftest:test()
    elif a.source:main()
    else:p.error("Choose --selftest or --source")
