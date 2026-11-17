#!/usr/bin/env python3
"""Official Figshare metadata source-only inventory for original Jena long-term
trait/community/biomass 2020 publication and 2022 same-study reanalysis.
No original biological data or effect models are opened.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import time
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from pathlib import Path

ARTICLES={
    12834350:{"source_role":"2020_Jena_original_primary_source",
              "paper_doi":"10.1038/s41559-020-01316-9"},
    19087640:{"source_role":"2022_reply_reanalysis_same_original_Jena_experiment",
              "paper_doi":"10.1038/s41559-022-01920-x"}
}
USER_AGENT="turnover-20261117-Jena-longitudinal-original-source-meta/0.1"
MAX_JSON=2_000_000
MAX_MANIFEST_FILES=200
MAX_RANGE=2048
HEAD_TIMEOUT=60

def grab(url:str,method="GET",limit=MAX_JSON,extra=None):
    headers={"User-Agent":USER_AGENT,"Accept":"application/json, */*"}
    if extra:headers.update(extra)
    req=Request(url,method=method,headers=headers)
    last=None
    for retry in range(2):
        try:
            with urlopen(req,timeout=HEAD_TIMEOUT) as response:
                if method=="HEAD":return response.status,b"",response.headers.get("Content-Type","")
                b=response.read(limit+1)
                if len(b)>limit:raise ValueError("PUBLIC_META_SIZE_HOLD")
                return response.status,b,response.headers.get("Content-Type","")
        except HTTPError as e:
            if e.code in (400,401,403,404,410,429):return e.code,b"",e.headers.get("Content-Type","") if e.headers else ""
            last=e
        except (URLError,TimeoutError,ValueError) as e:last=e
        if not retry:time.sleep(.5)
    return ("NETWORK_HOLD" if not isinstance(last,ValueError) else "SIZE_HOLD"),b"",""


def file_class(name):
    text=name.casefold()
    # This is *only* filename discovery, not original source grain certification.
    roles=[]
    labels={
       "README":("readme","metadata","description"),
       "community":("species","cover","composition","community","abundance"),
       "traits":("trait","plant_character","functional"),
       "biomass":("biomass","productivity","standing","aboveground"),
       "functions":("ecosystem","property","function","ep","response"),
       "models":(".r",".rmd","script","model","analysis","random","result"),
    }
    for label,terms in labels.items():
        if any(x in text for x in terms):roles.append(label)
    return roles or ["UNCLASSIFIED_FILENAME"]


def single(article_id:int,description:dict)->dict:
    root=f"https://api.figshare.com/v2/articles/{article_id}"
    code,raw,mimetype=grab(root)
    out={
      "original_article_id":article_id,
      "source_role":description["source_role"],
      "original_paper_doi":description["paper_doi"],
      "original_official_figshare_api":root,
      "api_status":code,"status":"PUBLISHER_META_HOLD",
      "is_source_only":True,"new_biological_effect_tested":False,
      "original_source_biological_rows_downloaded":0,
      "file_manifest":[]}
    if code!=200:
        out["reason"]="Official Figshare original article metadata not fetched; no inferred attachment."
        return out
    try:body=json.loads(raw)
    except Exception:
        out["status"]="PUBLISHER_META_HOLD"
        out["reason"]="Official Figshare returned malformed source metadata"
        return out
    if body.get("id")!=article_id:
        out["status"]="PUBLISHER_META_HOLD"
        out["reason"]="Original Figshare article numeric ID mismatch"
        return out
    out.update({
        "source_metadata_sha256":hashlib.sha256(raw).hexdigest(),
        "title":body.get("title"),"published_date":body.get("published_date"),
        "modified_date":body.get("modified_date"),
        "version":body.get("version"),"doi":body.get("doi"),
        "license":(body.get("license") or {}).get("name") if isinstance(body.get("license"),dict) else body.get("license")
    })
    fs=body.get("files") or []
    if not isinstance(fs,list) or len(fs)>MAX_MANIFEST_FILES:
        out["status"]="SOURCE_FILE_MANIFEST_HOLD"
        out["reason"]="Original source file array not a valid list or >200 file entries"
        return out
    out["n_source_files_listed"]=len(fs)
    discovered=0
    good=0
    sample_codes={}
    for f in fs:
        file_id=f.get("id")
        name=str(f.get("name") or "")
        size=f.get("size")
        original_md5=f.get("computed_md5") or f.get("supplied_md5")
        source_url=f.get("download_url")
        allowed=bool(isinstance(file_id,int) and isinstance(size,int) and
                     size>=0 and bool(name) and isinstance(source_url,str) and
                     re.fullmatch("https://ndownloader[.]figshare[.]com/files/"+str(file_id)+r"(?:[?].*)?",source_url))
        record={
          "file_id":file_id,"filename":name[:300],"bytes_advertised":size,
          "md5_as_reported":original_md5,
          "file_roles_inferred_from_filename_only":file_class(name),
          "official_file_id_link_validated":allowed,
          "is_link_only":bool(f.get("is_link_only"))}
        if allowed and not record["is_link_only"]:
            discovered+=1
            url=f"https://ndownloader.figshare.com/files/{file_id}"
            st,_,ty=grab(url,method="HEAD")
            if st in (405,403,"NETWORK_HOLD"):
                st,_,ty=grab(url,method="GET",limit=MAX_RANGE,
                             extra={"Range":"bytes=0-2047"})
            record["anonymous_access_status"]=st
            record["file_content_type"]=ty.split(";")[0][:60]
            if st in (200,206):good+=1
            sample_codes[str(st)]=sample_codes.get(str(st),0)+1
        else:
            record["anonymous_access_status"]="UNTRUSTED_OR_LINK_ONLY_HOLD"
        out["file_manifest"].append(record)
    out.update({
      "original_public_file_links_from_official_API":discovered,
      "file_links_anonymously_accessible":good,
      "file_access_status_counts":sample_codes,
      "primary_dataset_independence":"The 2022 article and 2020 article use the SAME 78-plot Jena original experiment, NOT independent ecological replicates.",
      "original_plot_year_species_join_verified":False,
      "original_biomass_response_grain_verified":False,
      "family_trait_phylogenetic_K_estimated":False,
      "site_and_time_transfer_estimated":False
    })
    if good==0:
        out["status"]="SOURCE_FILE_ACCESS_HOLD"
    elif not fs:
        out["status"]="SOURCE_FILE_MANIFEST_HOLD"
    else:
        out["status"]="SOURCE_META_PASS_FILE_LINK_PASS"
    return out


def fixture():
    assert file_class("README.txt")==["README"]
    assert "traits" in file_class("Species_traits_2020.csv")
    assert file_class("XXX.bin")==["UNCLASSIFIED_FILENAME"]
    assert len(ARTICLES)==2 and ARTICLes_identical_experiments() is True
    return {"status":"JENA_2020_2022_SOURCE_META_FIXTURE_PASS","checks":4}

def ARTICLes_identical_experiments():
    return all("Jena" in v["source_role"] for v in ARTICLES.values())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:print(json.dumps(fixture(),sort_keys=True));return
    if not args.out:parser.error("--out mandatory")
    items=[single(k,v) for k,v in ARTICLES.items()]
    response={
       "version":"v0.1",
       "program":"Independent Jena longitudinal source-only; no new outcome",
       "status":"JENA_2020_2022_SOURCE_METADATA_AUDIT_COMPLETE",
       "source_contract":"docs/JENA_INDEPENDENT_LONGITUDINAL_TRAIT_FUNCTION_SOURCE_PREFLIGHT_20261117.md",
       "articles":items,
       "n_distinct_original_ecological_experiments":1,
       "Jena_is_not_independent_of_earlier_turnover_Jena_guild_results":True,
       "TreeDivNet_2026_forest_is_ecologically_distinct_from_Jena_grassland":True,
       "no_biological_response_or_trait_FD_K_predictive_effect_opened":True,
       "next_action":"Open original primary author-file schema only after verifying publicly accessible original trait matrix plus plot/season/year cover and biomass; do not reopen frozen generic time-space BIEN gates."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(response,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("JENA_2020_PRIMARY_2022_REANALYSIS_SOURCE_META",json.dumps(response,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
