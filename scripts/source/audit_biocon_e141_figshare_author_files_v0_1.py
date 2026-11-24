#!/usr/bin/env python3
"""BioCON E141 author-released Figshare v3 byte/source-schema audit.

Source-only. Original CSV is fetched and checksummed, but ONLY THE FIRST HEADER
ROW is parsed. Author README/R are inspected for codebook keyword presence.
No numeric source outcomes/plots/traits, regression or derived FD are opened.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

ARTICLE=26841637
VERSION=3
API=f"https://api.figshare.com/v2/articles/{ARTICLE}/versions/{VERSION}"
FILES={
    "BioCON_biomass_cover_data_Sep2022.csv":"8185b8effca37c8740ad065c53eb75d2",
    "01_data_clean_and_calculation.R":"3166d7b1f8ee36e974812b3c7ac2cb48",
    "02_figures.R":"92b07f0cc41cca51ecb589d6e450eca8",
    "README.txt":"9ce824a94a0ad0ab455a9cfcc1589670",
}
OUTPUT=Path("results/biocon_e141_figshare_author_four_files_schema_20261124_v0_1.json")
TOPICS={
    "plot_key":r"\bplot\b|plotid|plot_id",
    "ring_key":r"\bring\b|ringid|ring_id",
    "time_year":r"\byear\b|yr_|yr$",
    "species_identity":r"\bspecies\b|\bsp\b|species_name|spcode",
    "planted_identity":r"\bplanted\b|\bsown\b|\bseeded\b|species.?composition|composition.?code",
    "monoculture":r"monocult|\bmono\b|single.?species",
    "biomass":r"biomass|aboveground|above_ground",
    "cover":r"\bcover\b|percent.?cover",
    "complementarity":r"complementarity|\bce\b",
    "selection":r"selection|\bse\b",
    "species_trait":r"\bsla\b|specific.?leaf|height|leaf.?nitrogen|trait.?value",
    "CO2":r"\bco2\b|co_2|carbon.?dioxide",
    "nitrogen":r"\bnitrogen\b|^nadd$|fertiliz|\bnadd\b",
    "richness":r"\brichness\b|species.?richness",
}
def get(url: str, max_bytes: int=4_000_000) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"turnover-e141-figshare-source-only/1.0",
         "Accept":"application/octet-stream,application/json;q=0.8,*/*;q=0.5"})
    with urllib.request.urlopen(req,timeout=40) as res:
        blob=res.read(max_bytes+1)
    if len(blob)>max_bytes:
        raise ValueError("Original file exceeded fixed source bytes cap")
    return blob

def first_csv_header(raw: bytes) -> list[str]:
    # Slice at the first line-break BEFORE decoding: never parse numeric response rows.
    rawline=raw.split(b"\n",1)[0].rstrip(b"\r")
    text=rawline.decode("utf-8-sig")
    fields=next(csv.reader([text]))
    if len(fields)<2 or len(fields)>500:
        raise ValueError("Original CSV header field count outside safe bounds")
    if len(fields)!=len(set(fields)):
        raise ValueError("Original source has duplicate column names")
    return fields

def topic_flags(text: str) -> dict[str,bool]:
    return {topic:bool(re.search(pattern,text,re.I|re.M))
            for topic,pattern in TOPICS.items()}

def selftest():
    assert first_csv_header(b"\xef\xbb\xbfplot,ring,biomass\r\n1,1,100\r\n")==["plot","ring","biomass"]
    assert topic_flags("raw=read.csv('source.csv')\nrichness, complementarity, selection")["complementarity"]
    assert not topic_flags("foo bar")["monoculture"]
    print("SYNTHETIC_AUTHOR_SOURCE_SCHEMA_PARSER_PASS")

def main():
    out={"as_of_jst":"2026-11-24",
         "source_programme":"Cedar Creek BioCON E141; not E120 and not 24 independent experiments",
         "source_release":"10.6084/m9.figshare.26841637.v3",
         "paper_doi":"10.1038/s41467-025-62691-0",
         "required_file_md5":FILES,
         "source_access":"SOURCE_ACCESS_HOLD",
         "original_numeric_response_rows_opened":False,
         "original_species_trait_values_opened":False,
         "new_biological_models_fitted":0,
         "original_raw_files_committed":False,
         "e141_planting_crosswalk_certified":False,
         "trait_source_directly_measured_before_target_response":False,
         "original_site_eligible_effect":"NOT_TESTED",
         "original_release_file_schemas":{},
    }
    try:
        meta=json.loads(get(API,600_000).decode("utf-8"))
        if int(meta.get("id",-1))!=ARTICLE or int(meta.get("version") or -1)!=VERSION:
            raise ValueError("Wrong Figshare original immutable version")
        manifest={x.get("name"):x for x in meta.get("files",[])}
        if not set(FILES).issubset(manifest):
            raise ValueError("Missing required original author file")
        summaries={}
        for name,md5 in FILES.items():
            entry=manifest[name]
            announced=(entry.get("computed_md5") or entry.get("supplied_md5") or "").lower()
            if announced and announced!=md5:
                raise ValueError("Figshare immutable manifest MD5 mismatch")
            file_id=entry.get("id")
            url=entry.get("download_url") or f"https://ndownloader.figshare.com/files/{file_id}"
            if not str(url).startswith(("https://ndownloader.figshare.com/","https://figshare.com/","https://api.figshare.com/")):
                raise ValueError("Unexpected original author archive download URL")
            raw=get(url)
            actual=hashlib.md5(raw).hexdigest()
            if actual!=md5:
                raise ValueError(f"Original checksum failed for {name}")
            summary={"original_file_id":file_id,"md5_verified":True,"size_bytes":len(raw)}
            if name.lower().endswith(".csv"):
                fields=first_csv_header(raw)
                summary.update({"number_of_original_headers":len(fields),
                                "original_column_names_only":fields,
                                "original_header_class_flags":topic_flags(" ".join(fields)),
                                "numeric_response_rows_parsed":0})
            else:
                txt=raw.decode("utf-8-sig",errors="replace")
                summary.update({"author_source_text_keyword_flags":topic_flags(txt),
                                "original_authored_line_count":len(txt.splitlines()),
                                "data_row_values_parsed":0})
            summaries[name]=summary
        out["original_release_file_schemas"]=summaries
        out["source_access"]="SOURCE_AUTHOR_FOUR_ORIGINAL_FILES_MD5_PASS"
        out["source_verdict"]="AUTHOR_SOURCE_BYTES_AND_HEADER_PASS_PLANTING_TRAIT_CROSSWALK_HOLD"
        out["next_identifiability_gate"]="Qualify original author treatment table and sown-species plot IDs, source site/ring/year/N/CO2, and trait source from monocultures; no FD→NDE/CE/SE effect fitted."
    except (urllib.error.HTTPError,urllib.error.URLError,KeyError,ValueError,
            TimeoutError,UnicodeError,csv.Error,json.JSONDecodeError,TypeError) as exc:
        out["source_verdict"]="AUTHOR_SOURCE_ACCESS_OR_SCHEMA_HOLD"
        out["source_error_class"]=type(exc).__name__
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"source_verdict":out["source_verdict"],
                      "source_error_class":out.get("source_error_class"),
                      "original_file_schemas":out["original_release_file_schemas"],
                      "raw_response_rows_parsed":0,"ecological_model_fits":0},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    a=p.parse_args()
    if a.selftest:selftest()
    elif a.source:main()
    else:p.error("choose --selftest or --source")
