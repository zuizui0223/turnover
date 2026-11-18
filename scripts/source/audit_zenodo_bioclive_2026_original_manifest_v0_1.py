#!/usr/bin/env python3
"""Pan/de Bello 2026 UU BioCliVE original Zenodo 18483939 file-manifest audit.

Original paper: one grassland experiment, two blocks 88 original plots,
2018–22 species-sorted clipped biomass, SLA/LDMC measured in 2022.
No trait–biomass regression and no original family phylogenetic K.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlsplit
from urllib.error import HTTPError,URLError

RECORD=18483939
DOI=f"10.5281/zenodo.{RECORD}"
API=f"https://zenodo.org/api/records/{RECORD}"
UA="turnover-independent-Utrecht-BioCliVE-original-source-manifest-20261118/0.1"
HEADER={"User-Agent":UA,"Accept":"application/json, */*"}
MAX_META=2_000_000
MAX_SMALL=2_000_000
MAX_ZIP=20_000_000
MAX_UNZIP=60_000_000
MAX_MEMBERS=250
EXTS=(".csv",".tsv",".txt",".xlsx",".zip",".rds")

def fetch(url,cap):
    u=urlsplit(url)
    if u.scheme!="https" or u.hostname!="zenodo.org":
        raise ValueError("SOURCE_URL_HOLD: original Zenodo API/file target not official")
    with urlopen(Request(url,headers=HEADER),timeout=120) as r:
        final=urlsplit(r.url)
        if final.hostname not in ("zenodo.org","zenodo-records.s3.amazonaws.com","zenodo-prod-files.s3.amazonaws.com"):
            raise ValueError("SOURCE_URL_HOLD: unexpected redirected source blob hostname")
        b=r.read(cap+1)
        if len(b)>cap:raise ValueError("SOURCE_SIZE_HOLD")
        return b

def csv_info(blob,ext):
    txt=blob.decode("utf-8-sig")
    reader=csv.reader(io.StringIO(txt),delimiter="\t" if ext==".tsv" else ",")
    rows=iter(reader)
    header=next(rows,None)
    if not header:return {"status":"EMPTY_SOURCE_CSV_HOLD"}
    if any(not s.strip() for s in header) or len(set(header))!=len(header):
        return {"status":"DUPLICATED_OR_MISSING_SOURCE_HEADER_HOLD"}
    n=0
    invalid=0
    for row in rows:
        if not row or not any(str(x).strip() for x in row):continue
        n+=1
        invalid+=int(len(row)!=len(header))
        if n>100000:raise ValueError("SOURCE_ROW_LIMIT_HOLD")
    names=[str(h).strip()[:100] for h in header[:130]]
    rx={
      "species":r"species|sp(?:[_. ]?name|[_. ]?id)|taxon|speciescode",
      "plot":r"plot|subplot|block|quadrat|community",
      "year":r"year|date|time|harvest",
      "biomass":r"biomass|dry.?mass|productiv|above.?ground|yield",
      "traits":r"sla|ldmc|leaf.?dry|leaf.?area|trait",
    }
    return {"status":"ORIGINAL_TABLE_HEADER_INSPECTED",
       "row_count":n,"n_columns":len(header),"n_bad_row_length":invalid,
       "column_names":names,
       "candidate_roles":{k:[x for x in names if re.search(r,x,re.I)][:20] for k,r in rx.items()},
       "original_numeric_species_biomass_trait_values_never_exported":True,
    }

def zip_info(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        files=z.infolist()
        if len(files)>MAX_MEMBERS or sum(i.file_size for i in files)>MAX_UNZIP:
            raise ValueError("SOURCE_ZIP_BOMB_LIMIT_HOLD")
        names=[]
        for fi in files:
            n=fi.filename
            if n.startswith("/") or n.startswith("../") or "/../" in n:
                raise ValueError("SOURCE_ZIP_PATH_HOLD")
            if not fi.is_dir():
                names.append({"path":n[:180],"uncompressed_bytes":fi.file_size,
                              "name_suggests_trait":bool(re.search(r"trait|sla|ldmc|leaf",n,re.I)),
                              "name_suggests_species_biomass":bool(re.search(r"biomass|productivity|species.?abund|harvest|dry.?mass",n,re.I))})
        return {"status":"ZIP_SOURCE_MEMBERS_LISTED_ONLY","source_member_count":len(names),
                "source_members":names[:200],"no_member_data_rows_read":True}

def run():
    source=json.loads(fetch(API,MAX_META))
    if source.get("id")!=RECORD or source.get("doi")!=DOI:
        raise ValueError("SOURCE_IDENTITY_HOLD: exact Zenodo version DOI/ID not verified")
    files=source.get("files") or []
    report={
       "version":"v0.1","study":"Pan, de Bello et al. 2026 UU BioCliVE experiment",
       "doi":DOI,"official_zenodo_record_id":RECORD,
       "record_created":source.get("created"),"record_updated":source.get("updated"),
       "original_dataset_file_count":len(files),
       "dataset_status":"PUBLIC_RECORD" if source.get("access",{}).get("record","public")=="public" else "SOURCE_AUTH_HOLD",
       "original_experiment_published_design":{"one_original_Utrecht_experiment":True,
          "two_original_blocks":True,"published_original_plots":88,
          "biomass_original_annual_species_clipping_years":[2018,2019,2020,2021,2022],
          "original_leaf_SLA_LDMC_measurement_year":2022,
          "source_trait_sample_count_reported_by_article":"over 2000",
          "not_independent_cross_eco_region_site_transport":True,
          "family_specific_12_families_20_species_K_not_supported":True},
       "file_manifest":[],"original_file_content_header_profiles":[],
       "no_source_outcome_numeric_values_exported":True,
       "no_ecological_model_estimated":True,
    }
    if report["dataset_status"]!="PUBLIC_RECORD":
        report["status"]="AUTH_HOLD";return report
    if len(files)>100:
        report["status"]="SOURCE_MANIFEST_SIZE_HOLD";return report
    for f in files:
        name=f.get("key") or ""
        md5=str(f.get("checksum") or "").removeprefix("md5:").lower()
        size=f.get("size")
        item={"name":name,"original_file_size":size,"MD5":md5,
              "download_status":"NOT_ACCESSED"}
        report["file_manifest"].append(item)
        if not name or not isinstance(size,int) or not re.fullmatch(r"[0-9a-f]{32}",md5):
            item["download_status"]="ORIGINAL_MANIFEST_INCOMPLETE_HOLD"
            continue
        ext="."+name.rsplit(".",1)[-1].lower() if "." in name else ""
        if ext not in EXTS:
            item["download_status"]="NON_TABLE_SOURCE_TYPE_NOT_OPENED"
            continue
        if size>MAX_SMALL and (ext!=".zip" or size>MAX_ZIP):
            item["download_status"]="SOURCE_SIZE_LIMIT_NOT_OPENED"
            continue
        url=(f.get("links") or {}).get("self") or ""
        if not url:
            item["download_status"]="NO_OFFICIAL_DOWNLOAD_LINK"
            continue
        try:
            blob=fetch(url,MAX_ZIP if ext==".zip" else MAX_SMALL)
            if len(blob)!=size or hashlib.md5(blob).hexdigest()!=md5:
                item["download_status"]="SOURCE_MD5_MISMATCH_HOLD"
                continue
            item["download_status"]="ORIGINAL_MD5_PASS"
            if ext in (".csv",".tsv"):
                extra=csv_info(blob,ext)
            elif ext==".zip":
                extra=zip_info(blob)
            elif ext==".txt":
                extra={"status":"ORIGINAL_TEXT_SOURCE_ACCESS_VERIFIED",
                       "n_lines":len(blob.decode("utf8",errors="replace").splitlines()),
                       "no_raw_original_text_exported":True}
            else:
                extra={"status":"BINARY_SOURCE_MD5_PASS_NO_ORIGINAL_ROWS_READ"}
            report["original_file_content_header_profiles"].append({
                  "original_file_name":name,"original_byte_MD5_verified":True,
                  "source_inspection":extra})
        except (ValueError,HTTPError,URLError,TimeoutError,OSError,zipfile.BadZipFile,UnicodeError) as e:
            item["download_status"]="ORIGINAL_FILE_ACCESS_OR_FORMAT_HOLD"
            item["exception_type"]=type(e).__name__
    nverified=sum(x["download_status"]=="ORIGINAL_MD5_PASS" for x in report["file_manifest"])
    report["n_source_files_MD5_accessible_and_verified"]=nverified
    report["status"]="PUBLIC_SOURCE_MANIFEST_VERIFIED" if nverified>0 else "ORIGINAL_SOURCE_FILES_ACCESS_HOLD"
    report["source_join_qualification"]="SOURCE_ONLY_INSPECTED__ORIGINAL_PLOT_YEAR_TRAIT_BIOMASS_JOIN_NOT_YET_CONFIRMED"
    return report

def fixture():
    x=b"plot,year,species,biomass_g,leaf_SLA\n1,2022,A,20,10\n"
    y=csv_info(x,".csv")
    assert y["row_count"]==1
    assert y["candidate_roles"]["species"]==["species"]
    assert y["candidate_roles"]["biomass"]==["biomass_g"]
    assert y["candidate_roles"]["traits"]==["leaf_SLA"]
    return {"status":"BIOCLIVE_ORIGINAL_SOURCE_MANIFEST_FIXTURE_PASS","checks":4}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not args.out:p.error("--out needed")
        try:obj=run()
        except Exception as e:
            obj={"version":"v0.1","doi":DOI,"status":"SOURCE_ACCESS_OR_MANIFEST_HOLD",
                 "error_class":type(e).__name__,"error_message":str(e)[:240],
                 "no_ecological_model_estimated":True}
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("PAN_BIOCLIVE_2026_ZENODO_ORIGINAL_SOURCE_MANIFEST",json.dumps(obj,sort_keys=True),flush=True)
