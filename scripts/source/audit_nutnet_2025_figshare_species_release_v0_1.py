#!/usr/bin/env python3
"""2025 NutNet original public Figshare source metadata/optional small-file schema.

Only official Figshare API article 26412295 v4 and advertised original file
IDs; source MD5 + file sizes checked, no original plant cover rows exported.
No site alias, trait K, FD, biomass model, regression, or biology inferred.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ID=26412295
DOI="10.6084/m9.figshare.26412295"
API="https://api.figshare.com/v2/articles/"+str(ID)
MAX_META=2_000_000
MAX_FILE=10_000_000
MAX_UNPACKED=15_000_000
UA="turnover-NutNet-2025-2026-species-by-plot-original-Figshare-source-20261118/0.1"
KEY_TOKENS=("species","taxon","scientific","cover","plot","site","year","treatment","control",
           "richness","biomass","abundance","sample","duration")


def req(url,limit):
    try:
        request=Request(url,headers={"User-Agent":UA,"Accept":"application/json,application/octet-stream,text/plain,*/*"})
        with urlopen(request,timeout=90) as r:
            final=urlsplit(r.geturl())
            blob=r.read(limit+1)
            if len(blob)>limit:return "SOURCE_SIZE_LIMIT_HOLD",b"",final.hostname
            return r.status,blob,final.hostname
    except HTTPError as e:
        return e.code,b"",None
    except (OSError,TimeoutError):
        return "NETWORK_HOLD",b"",None


def csv_schema(blob):
    try:
        text=blob.decode("utf-8-sig")
        first=next(csv.reader(io.StringIO(text)),[])
        if not first:return {"status":"CSV_HEADER_EMPTY_HOLD"}
        return {"status":"CSV_HEADER_FOUND",
                "first_original_header_columns":first[:100],
                "header_token_presence":{k:any(k in str(x).casefold() for x in first) for k in KEY_TOKENS},
                "original_rows_read_or_exported":False}
    except Exception as e:
        return {"status":"CSV_SCHEMA_ERROR_HOLD","error":type(e).__name__}


def safe_files(obj):
    out={"version":"v0.1","status":"ORIGINAL_PUBLIC_FIGSHARE_IDENTITY_HOLD",
         "source_article_id":ID,"source_public_DOI_expected":DOI,
         "source_API":API,"only_source_metadata_and_file_checks":True,
         "ecological_effect_estimated":False,"source_original_species_cover_rows_exported":False,
         "source_file_catalogue":[]}
    if obj.get("id")!=ID:
        out["reason"]="API original Figshare article ID mismatch";return out
    found=str(obj.get("doi") or "").lower().strip().rstrip("/")
    found_v=obj.get("version")
    if not re.fullmatch(re.escape(DOI)+r"(?:\.v[1-9][0-9]*)?",found):
        out.update({"reason":"Different Figshare source DOI","source_returned_doi":found});return out
    # The published provenance cites version 4. Stop rather than silently using
    # any newer data revision from the current article endpoint.
    if found_v is not None and int(found_v)!=4:
        out.update({"status":"ORIGINAL_PUBLIC_FIGSHARE_VERSION_HOLD",
            "source_returned_version":found_v,
            "source_returned_doi":found,
            "reason":"Original source article v4 required; API most-current version differs, no silently revised dataset."})
        return out
    lic=obj.get("license") or {}
    out.update({"source_reported_version":found_v,
      "source_returned_doi":found,"published_date":obj.get("published_date"),
      "source_article_title":str(obj.get("title") or "")[:250],
      "source_licence":str(lic.get("name") if isinstance(lic,dict) else lic)[:150]})
    files=obj.get("files") or []
    if len(files)>35 or not isinstance(files,list):
        out["status"]="ORIGINAL_SOURCE_FILE_MANIFEST_LIMIT_HOLD";return out
    for f in files:
        n=str(f.get("name") or "")
        ident=f.get("id")
        size=int(f.get("size") or 0)
        md5=str(f.get("computed_md5") or f.get("supplied_md5") or "").lower()
        url=str(f.get("download_url") or "")
        record={"name":n,"source_figshare_file_id":ident,"advertised_file_bytes":size,
           "advertised_MD5":md5 or None,
           "file_extension":n.rsplit(".",1)[-1].casefold() if "." in n else "unknown",
           "source_file_access":"UNTESTED",
           "original_plant_species_cover_file_source_metadata_only":True}
        if not isinstance(ident,int) or ident<=0 or not n or size<0 or not re.fullmatch(r"[0-9a-f]{32}",md5):
            record["source_file_access"]="SOURCE_META_INCOMPLETE_HOLD"
            out["source_file_catalogue"].append(record);continue
        canonical="https://ndownloader.figshare.com/files/"+str(ident)
        if urlsplit(url).scheme!="https" or urlsplit(url).hostname!="ndownloader.figshare.com" or            urlsplit(url).path!="/files/"+str(ident):
            record["source_file_access"]="UNTRUSTED_ORIGINAL_SOURCE_URL_HOLD"
            out["source_file_catalogue"].append(record);continue
        if size>MAX_FILE:
            record["source_file_access"]="SOURCE_FILE_SIZE_LIMIT_HOLD"
            out["source_file_catalogue"].append(record);continue
        status,raw,host=req(canonical,MAX_FILE)
        record["source_download_http"]=status
        if status==200 and host in ("ndownloader.figshare.com","figshare.com","files.figshare.com") and len(raw)==size and hashlib.md5(raw).hexdigest()==md5:
            record["source_file_access"]="PUBLIC_ORIGINAL_BYTES_MD5_PASS"
            record["source_file_bytes_verified"]=len(raw)
            extension=record["file_extension"]
            if extension in ("csv","tsv","txt") and size<=2_000_000:
                if extension=="txt" and not any(k in n.casefold() for k in ("cover","species","plot","community","data","trait")):
                    record["original_text_schema"]="PUBLISHED_README_TEXT_NOT_RAW_BIOLOGY"
                else:
                    record["header_only"]=csv_schema(raw)
            elif extension in ("zip","xlsx"):
                try:
                    with zipfile.ZipFile(io.BytesIO(raw)) as z:
                        entries=[q for q in z.infolist() if not q.is_dir()]
                        if len(entries)>100 or sum(e.file_size for e in entries)>MAX_UNPACKED or any(".." in e.filename or e.filename.startswith("/") for e in entries):
                            record["archive_manifest_status"]="UNSAFE_OR_EXPANDED_SIZE_HOLD"
                        else:
                            record["archive_manifest_status"]="SOURCE_ARCHIVE_LISTED_NO_ROWS"
                            record["archive_original_filenames"]=[q.filename[:170] for q in entries[:70]]
                            record["original_uncompressed_total_bytes"]=sum(q.file_size for q in entries)
                except zipfile.BadZipFile:
                    record["archive_manifest_status"]="BAD_SOURCE_ZIP_HOLD"
        else:
            record["source_file_access"]="SOURCE_FILE_ACCESS_OR_CHECKSUM_HOLD"
        out["source_file_catalogue"].append(record)
    out["source_n_files"]=len(files)
    out["source_n_original_file_MD5_verified"]=sum(x["source_file_access"]=="PUBLIC_ORIGINAL_BYTES_MD5_PASS" for x in out["source_file_catalogue"])
    out["source_n_catalogued_csv_or_excel_or_zip"]=sum(x["file_extension"] in ("csv","tsv","xlsx","zip") for x in out["source_file_catalogue"])
    out["status"]="ORIGINAL_PUBLIC_SPECIES_SOURCE_FILE_MANIFEST_VERIFIED" if out["source_n_original_file_MD5_verified"] else "ORIGINAL_FIGSHARE_DATA_FILE_ACCESS_HOLD"
    out["original_2026_nutnet_1108_130_site_crosswalk_executed"]=False
    out["inference_limit"]="Manifest and headers only. Species×plot×year key overlap and original measured vs imputed trait lineage not yet established. NutNet raw network data policy remains binding."
    return out


def fixture():
    assert ID==26412295
    assert re.fullmatch(re.escape(DOI)+r"(?:\.v[1-9][0-9]*)?",DOI+".v4")
    assert csv_schema(b"site,plot,year,species,cover\n")["header_token_presence"]["species"]
    return {"status":"NUTNET_PUBLIC_SPECIES_FIGSHARE_API_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not args.out:p.error("--out required")
        status,body,host=req(API,MAX_META)
        result={"status":"SOURCE_API_ACCESS_HOLD","source_API":API,"source_API_http":status,
                "only_source_metadata_and_file_checks":True,"ecological_effect_estimated":False}
        if status==200 and host=="api.figshare.com":
            try:
                value=json.loads(body)
                result=safe_files(value)
                result["source_api_original_meta_sha256"]=hashlib.sha256(body).hexdigest()
                result["source_API_http"]=status
            except (ValueError,TypeError) as e:
                result["status"]="SOURCE_META_PARSE_HOLD"
                result["error_type"]=type(e).__name__
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf8")
        print("NUTNET_FIGSHARE_2025_SPECIES_PLOT_SOURCE_MANIFEST",json.dumps(result,sort_keys=True),flush=True)
