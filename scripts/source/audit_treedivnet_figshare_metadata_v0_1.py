#!/usr/bin/env python3
"""Source-only official Figshare article metadata and public file-access audit.

No biological values, raw species rows, biomass endpoints, plot prediction,
phylogenetic K/PD or functional diversity are read or estimated.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

ID=31026004
DOI="10.6084/m9.figshare.31026004"
API=f"https://api.figshare.com/v2/articles/{ID}"
MAX_META=1_500_000
SOURCE_READ_LIMIT=2048
TIMEOUT=65
UA="turnover-20261116-tree-divnet-original-data-source-preflight/0.1"


def fetch(url:str, method="GET", ceiling=MAX_META, header=None):
    h={"User-Agent":UA,"Accept":"application/json, */*"}
    if header:h.update(header)
    req=Request(url,headers=h,method=method)
    try:
        with urlopen(req,timeout=TIMEOUT) as response:
            data=response.read(ceiling+1) if method!="HEAD" else b""
            if len(data)>ceiling:
                raise ValueError("SOURCE_ACCESS_HOLD_TOO_LARGE_RESPONSE")
            return response.status,data,response.headers.get("Content-Type","")
    except HTTPError as e:
        return int(e.code),b"",e.headers.get("Content-Type","") if e.headers else ""
    except (OSError,TimeoutError):
        return "NETWORK_HOLD",b"",""


def verify_file(item:dict)->dict:
    name=str(item.get("name") or "")
    ident=item.get("id")
    size=item.get("size")
    checksum=str(item.get("computed_md5") or item.get("supplied_md5") or "").lower()
    is_link=bool(item.get("is_link_only"))
    url=str(item.get("download_url") or "")
    if not name or not isinstance(ident,int) or ident<=0 or size is None or int(size)<0:
        raise ValueError("SOURCE_HOLD: incomplete article file metadata")
    # Only accept a direct Figshare file ID URI; no untrusted arbitrary host.
    pattern=rf"^https://ndownloader\.figshare\.com/files/{ident}(?:[?].*)?$"
    file={"name":name,"file_id":ident,"bytes":int(size),
          "computed_md5":checksum or None,
          "link_only":is_link,"format":name.rsplit(".",1)[-1].lower() if "." in name else "unknown",
          "figshare_download_url_matches_advertised_id":bool(re.fullmatch(pattern,url))}
    if is_link or not file["figshare_download_url_matches_advertised_id"]:
        file["anonymous_access"]="UNTRUSTED_OR_LINK_ONLY_HOLD"
        return file
    status,blob,typ=fetch(url,method="HEAD")
    if status in (403,405,501,"NETWORK_HOLD"):
        # The exact source advertized URL with an original 2KB bounded read
        # is used ONLY if HEAD did not prove file availability.
        status,blob,typ=fetch(url,method="GET",ceiling=SOURCE_READ_LIMIT,
                              header={"Range":f"bytes=0-{SOURCE_READ_LIMIT-1}"})
    file["anonymous_access_http"]=status
    file["anonymous_access"]="ACCESSIBLE" if status in (200,206) else "ACCESS_HOLD"
    file["content_type"]=typ.split(";")[0].lower()[:65]
    file["sample_body_or_rows_persisted"]=False
    return file


def run()->dict:
    status,blob,mime=fetch(API)
    record={"status":"ARTICLE_NOT_PUBLIC_HOLD","version":"v0.1",
            "contract":"docs/TREEDIVNET_2026_FIGSHARE_SOURCE_GATE_V0_1.md",
            "source":"Figshare official API v2",
            "doi_expected":DOI,"article_id_expected":ID,
            "metadata_http":status,
            "api_article_url":API,
            "no_original_biomass_or_trait_values_opened":True,
            "no_ecological_effect_estimated":True,"article_file_table":[]}
    if status!=200:
        record["reason"]="Exact publicly cited Figshare article metadata unavailable; do not invent data."
        return record
    try:
        body=json.loads(blob)
    except Exception:
        record["status"]="ARTICLE_NOT_PUBLIC_HOLD"
        record["reason"]="Public metadata malformed or not JSON"
        return record
    found_doi=str(body.get("doi") or "").strip().lower().rstrip("/")
    # Figshare public article may return DOI with immutable version .v1 etc.,
    # while the published Data Availability Statement cites the root DOI.
    # Validate an exact root+numeric version only; never a different DOI.
    accepted=bool(re.fullmatch(re.escape(DOI)+r"(?:\.v[1-9][0-9]*)?",found_doi))
    if body.get("id")!=ID or not accepted:
        record["status"]="ARTICLE_NOT_PUBLIC_HOLD"
        record["reason"]="Figshare article identity or DOI mismatch"
        record["returned_article_id"]=body.get("id")
        record["returned_doi"]=body.get("doi")
        return record
    record.update({"article_title":body.get("title"),
        "doi":body.get("doi"),"version":body.get("version"),
        "published_date":body.get("published_date"),
        "modified_date":body.get("modified_date"),
        "license":(body.get("license") or {}).get("name") if isinstance(body.get("license"),dict) else str(body.get("license")),
        "public":bool(body.get("published_date")),"resource_doi":body.get("references")[:2] if isinstance(body.get("references"),list) else None,
        "source_article_metadata_sha256":hashlib.sha256(blob).hexdigest()
    })
    files=body.get("files") or []
    if not isinstance(files,list) or len(files)>30:
        record["status"]="METADATA_PASS_DATA_GRAIN_HOLD"
        record["reason"]="More than 30 original files or invalid file manifest; list only via manual audit"
        record["article_file_count"]=len(files) if isinstance(files,list) else None
        return record
    record["article_file_count"]=len(files)
    table=[]
    for item in files:
        try:table.append(verify_file(item))
        except Exception as exc:
            table.append({"name":str(item.get("name") or ""),"status":"SOURCE_METADATA_HOLD",
                          "error_type":type(exc).__name__})
    record["article_file_table"]=table
    n_public=sum(x.get("anonymous_access")=="ACCESSIBLE" for x in table)
    record["n_original_file_links_verified_anonymous"]=n_public
    if not files:
        record["status"]="METADATA_PASS_DATA_GRAIN_HOLD"
        record["reason"]="Published article metadata has no downloadable primary data files"
    elif n_public==0:
        record["status"]="PUBLIC_DATA_ACCESS_HOLD"
        record["reason"]="No Figshare original file link anonymously accessible"
    else:
        record["status"]="FILE_LIST_PASS_HEAD_ONLY"
        record["reason"]="At least one original file publicly accessible, but original plot×species trait and plot biomass join NOT checked. A subsequent original-row grain qualification is required before ecological effects."
    return record


def fixture():
    f={"id":123,"name":"original_trait_table.csv","size":2400,
       "download_url":"https://ndownloader.figshare.com/files/123",
       "is_link_only":False,"computed_md5":"0"*32}
    assert ID==31026004
    assert re.fullmatch(r"https://ndownloader\.figshare\.com/files/123",
                        f["download_url"])
    assert DOI.endswith("31026004")
    return {"status":"FIGSHARE_METADATA_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(fixture(),sort_keys=True))
    else:
        if not args.out:p.error("--out required")
        d=run()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("TREEDIVNET_FIGSHARE_SOURCE_METADATA",json.dumps({
            k:v for k,v in d.items() if k not in ("source_article_metadata_sha256",)},sort_keys=True),flush=True)
