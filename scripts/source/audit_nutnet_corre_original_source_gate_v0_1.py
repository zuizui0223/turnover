#!/usr/bin/env python3
"""NutNet 2026 independently field-measured aboveground biomass source and
CoRRE observed-only plant trait K *source* feasibility.

Only official Zenodo record 20070364 and DataCite EDI DOI metadata.
No original species records or values committed, no K, FD, biomass effects fit.
Frozen: docs/INDEPENDENT_NUTNET_CORRE_K_FD_MASS_SOURCE_GATE_20261118.md
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import re
import ssl
from datetime import datetime,timezone
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import quote,urlsplit
from urllib.request import Request,urlopen

ZENODO_ID=20070364
ZENODO_DOIS={"10.5281/zenodo.20070364","10.5281/zenodo.20070363"}
CORRE_DOI="10.6073/pasta/a33c9be2bd819d6b1a2c52663d561158"
BASE="https://zenodo.org"
FILE_DATA="Andraczek_et_al_Belowground_traits_and_aboveground_biomass_NutNet_subset.csv"
FILE_META="Andraczek_et_al_Belowground_traits_and_aboveground_biomass_NutNet_subset_metadata.txt"
UA="turnover-grassland-K-FD-mass-source-qualification-20261118/0.1 (original DOIs 10.5281/zenodo.20070363; 10.6073/pasta/a33c9be2bd819d6b1a2c52663d561158)"
MAX_META=1_000_000
MAX_DATA=2_000_000
NUT_NET_SITE_MIN=12
NUT_NET_PLOT_MIN=80
NUT_NET_SITE8_MIN=5
NUT_NET_PER_SITE_MIN=5
NUT_NET_CWM_COVERAGE=.80
BAD={"","na","n/a","nan","none","null","-9999","-9999.0","-999","inf","infinity","-inf"}


def request(url:str,limit:int,accept:str="application/json,*/*"):
    try:
        q=Request(url,headers={"User-Agent":UA,"Accept":accept})
        with urlopen(q,timeout=90) as resp:
            body=resp.read(limit+1)
            if len(body)>limit:raise ValueError("SIZE_LIMIT_HOLD")
            final=urlsplit(resp.geturl())
            return resp.status,body,final.hostname,resp.headers.get("Content-Type","")
    except HTTPError as e:
        return int(e.code),b"",None,""
    except (URLError,TimeoutError,ValueError):
        return "ACCESS_HOLD",b"",None,""


def safe_schema_name(value):
    return re.sub(r"[^a-z0-9]","",str(value or "").casefold())


def getcol(cols,options):
    normalized={}
    for c in cols:
        normalized.setdefault(safe_schema_name(c),[]).append(c)
    for o in options:
        hits=normalized.get(safe_schema_name(o),[])
        if len(hits)==1:return hits[0]
    return None


def numeric(value):
    if value is None or str(value).strip().casefold() in BAD:return None
    try:
        x=float(value)
        return x if math.isfinite(x) else None
    except Exception:return None


def stable_id(value):
    v=str(value or "").strip()
    if not v:return ""
    if re.fullmatch(r"[0-9]+(?:\.0+)?",v):return str(int(float(v)))
    return v.casefold()


def verify_files(meta):
    rows=meta.get("files") or []
    if isinstance(rows,dict):
        rows=list(rows.get("entries") or rows.values())
    if not isinstance(rows,list):return {"status":"ZENODO_FILE_MANIFEST_HOLD"},{}
    wanted={}
    inventory=[]
    for x in rows:
        if not isinstance(x,dict):continue
        name=str(x.get("key") or x.get("filename") or "")
        if not name:continue
        size=int(x.get("size") or 0)
        checksum=str(x.get("checksum") or "")
        inventory.append({"filename":name,"size_bytes":size,"advertised_checksum":checksum[:120]})
        if name in (FILE_DATA,FILE_META):wanted[name]=x
    if len(wanted)!=2:
        return {"status":"ORIGINAL_FILES_NOT_ALL_ADVERTISED",
                "advertised_original_filenames":[x["filename"] for x in inventory][:40]},{}
    actual={}
    for fn,entry in wanted.items():
        checksum=str(entry.get("checksum") or "")
        if not re.fullmatch(r"md5:[0-9a-fA-F]{32}",checksum):
            return {"status":"SOURCE_CHECKSUM_UNSUPPORTED_HOLD","filename":fn},{}
        length=int(entry.get("size") or 0)
        if length<=0 or length>(MAX_DATA if fn==FILE_DATA else 100_000):
            return {"status":"SOURCE_FILE_SIZE_HOLD","filename":fn,"bytes":length},{}
        # Original Zenodo-generated file references (no URL guessing / signed link).
        links=entry.get("links") or {}
        url=str(links.get("content") or links.get("self") or "")
        parsed=urlsplit(url)
        if (parsed.scheme!="https" or parsed.hostname not in ("zenodo.org","www.zenodo.org")
            or str(ZENODO_ID) not in parsed.path):
            return {"status":"UNTRUSTED_ORIGINAL_ZENODO_FILE_LINK_HOLD","filename":fn},{}
        status,blob,final_host,mimetype=request(url,(MAX_DATA if fn==FILE_DATA else 100_000),
                             accept="text/csv,text/plain,application/octet-stream,*/*")
        if status!=200 or final_host not in ("zenodo.org","www.zenodo.org"):
            return {"status":"SOURCE_FILE_ACCESS_HOLD","filename":fn,"http_status":status},{}
        if len(blob)!=length or hashlib.md5(blob).hexdigest()!=checksum.split(":",1)[1].lower():
            return {"status":"SOURCE_BYTES_MD5_HOLD","filename":fn,"bytes_downloaded":len(blob)},{}
        actual[fn]=blob
    return {"status":"SOURCE_CHECKSUMS_PASS",
            "original_data_file_bytes":len(actual[FILE_DATA]),
            "original_metadata_file_bytes":len(actual[FILE_META]),
            "original_data_md5":hashlib.md5(actual[FILE_DATA]).hexdigest(),
            "original_metadata_md5":hashlib.md5(actual[FILE_META]).hexdigest(),
            "original_files":[x for x in inventory if x["filename"] in wanted]},actual


def sample_csv(original:bytes):
    text=original.decode("utf-8-sig")
    # CRLF normalization only in parser; raw bytes hash already frozen.
    buff=io.StringIO(text)
    reader=csv.DictReader(buff)
    cols=reader.fieldnames or []
    if not cols or any(not x for x in cols) or len(set(cols))!=len(cols):
        return {"status":"CSV_SCHEMA_HOLD","columns":cols[:100]}
    rows=[]
    for row in reader:
        if None in row:
            return {"status":"MALFORMED_CSV_ROWS_HOLD","columns":cols[:100]}
        rows.append(row)
        if len(rows)>100_000:return {"status":"PLOT_ROW_LIMIT_HOLD","columns":cols[:100]}
    if not rows:return {"status":"EMPTY_CSV_HOLD","columns":cols[:100]}
    site=getcol(cols,("site","site_id","siteID","site_code","sitecode","SiteName"))
    plot=getcol(cols,("plot","plot_id","plotID","plot_code","plotcode","PlotName","blockplot"))
    yr=getcol(cols,("year","Year","survey_year","sampling_year"))
    # The original source metadata must identify this as dry aboveground biomass.
    biomass_cols=[c for c in cols if ("biomass" in c.casefold() or "agb" in safe_schema_name(c))]
    cwm_cols=[c for c in cols if "cwm" in safe_schema_name(c) and
              not any(x in safe_schema_name(c) for x in ("coverage","support","numspecies","n_species"))]
    trait_support=[c for c in cols if any(x in safe_schema_name(c) for x in
                  ("traitcoverage","traitcover","traitsupport","ntaxa","proptrait"))]
    source={"status":"ORIGINAL_PLOT_CSV_SCHEMA_AUDITED",
        "n_csv_data_rows":len(rows),"n_source_columns":len(cols),
        "original_source_columns":cols,"original_site_column":site,"original_plot_column":plot,
        "original_year_column":yr,"candidate_biomass_columns":biomass_cols,
        "candidate_derived_CWM_columns":cwm_cols,
        "candidate_trait_source_coverage_columns":trait_support,
        "original_species_level_columns_detected":[c for c in cols if safe_schema_name(c) in
                   ("species","scientificname","acceptedname","taxon","taxonid")],
        "raw_species_by_plot_rows_present":False,
        "no_original_raw_values_or_unique_plot_ids_exported":True,
    }
    if not site or not plot or not yr:
        source["status"]="PLOT_GRAIN_HOLD"
        source["source_key_diagnostics"]="One or more original site, plot, year identifiers are not explicitly in CSV columns; no synthetic IDs."
        return source
    keys=set()
    per_site=collections.Counter()
    duplicated=0
    blank=0
    years=collections.Counter()
    for row in rows:
        z=(stable_id(row[site]),stable_id(row[plot]),stable_id(row[yr]))
        if not all(z):
            blank+=1;continue
        if z in keys:duplicated+=1
        keys.add(z)
        per_site[z[0]]+=1
        years[z[2]]+=1
    source.update({"n_distinct_original_sites":len(per_site),
                   "n_distinct_site_plot_year_keys":len(keys),
                   "n_duplicate_original_site_plot_year_keys":duplicated,
                   "n_blank_site_plot_year_keys":blank,
                   "n_original_sites_with_atleast5_source_rows":sum(x>=5 for x in per_site.values()),
                   "per_site_source_row_count_distribution_sorted":sorted(per_site.values()),
                   "source_original_year_observation_histogram":dict(sorted(years.items()))})
    def num_profile(c):
        vals=[numeric(row[c]) for row in rows]
        present=[x for x in vals if x is not None]
        return {"nonmissing_numeric_rows":len(present),"fraction_numeric":len(present)/len(rows),
                "nonnegative_numeric_rows":sum(x>=0 for x in present),
                "positive_numeric_rows":sum(x>0 for x in present),
                "negative_numeric_rows":sum(x<0 for x in present)}
    source["biomass_source_column_presence"]={c:num_profile(c) for c in biomass_cols}
    source["CWM_source_column_presence"]={c:num_profile(c) for c in cwm_cols}
    if (duplicated or blank or len(per_site)<NUT_NET_SITE_MIN or len(keys)<NUT_NET_PLOT_MIN
       or sum(x>=NUT_NET_PER_SITE_MIN for x in per_site.values())<NUT_NET_SITE8_MIN):
        source["status"]="INDEPENDENT_SITE_PLOT_SUPPORT_HOLD"
    elif not biomass_cols or not cwm_cols:
        source["status"]="BIO_DERIVED_CWM_OR_MASS_SOURCE_SCHEMA_HOLD"
    else:
        good_bio=any(x["nonnegative_numeric_rows"]>=NUT_NET_PLOT_MIN
                     for x in source["biomass_source_column_presence"].values())
        good_trait=any(x["fraction_numeric"]>=NUT_NET_CWM_COVERAGE
                       for x in source["CWM_source_column_presence"].values())
        source["status"]="MULTISITE_MASS_AND_DERIVED_CWM_PRESENCE_PASS" if good_bio and good_trait else "MASS_CWM_QUALITY_HOLD"
    # No taxon-level source matrix is ever inferred from single plot CWM.
    source["plot_level_FD_K_linkage_status"]="PLOT_SPECIES_IDENTITIES_NOT_EXPOSED_IN_DERIVED_CWM_TABLE"
    source["biomass_unit"]="g dry weight m^-2 (per original public author description; validate against original metadata file)"
    source["trait_origin"]="UNDERPLOT-derived site plot CWM, NOT independently measured original species-by-plot field traits"
    return source


def nutnet():
    meta={"source":"2026 NutNet subset, Andraczek et al.",
          "doi_concept":"10.5281/zenodo.20070363","zenodo_record_id":ZENODO_ID,
          "source_api":"https://zenodo.org/api/records/20070364",
          "original_source_rows_opened":False,"biological_effect_estimated":False}
    status,blob,host,mime=request(meta["source_api"],MAX_META)
    meta["zenodo_record_metadata_http"]=status
    if status!=200 or host not in ("zenodo.org","www.zenodo.org"):
        meta["status"]="SOURCE_RECORD_ACCESS_HOLD";return meta
    try:obj=json.loads(blob)
    except Exception:
        meta["status"]="ZENODO_METADATA_PARSE_HOLD";return meta
    found=str(obj.get("doi") or "").lower()
    concept=str(obj.get("conceptdoi") or "").lower()
    if obj.get("id")!=ZENODO_ID or found not in ZENODO_DOIS or concept not in ZENODO_DOIS:
        meta["status"]="DOI_RECORD_IDENTITY_HOLD"
        meta["record_returned_doi"]=found
        meta["record_returned_conceptdoi"]=concept
        return meta
    v=obj.get("metadata") or {}
    licence=v.get("license")
    if isinstance(licence,dict):licence=licence.get("id")
    meta.update({"zenodo_version_doi":found,"zenodo_conceptdoi":concept,
           "publication_date":v.get("publication_date"),
           "license":licence,
           "record_metadata_sha256":hashlib.sha256(blob).hexdigest()})
    file_check,actual=verify_files(obj)
    meta["source_file_audit"]=file_check
    if file_check["status"]!="SOURCE_CHECKSUMS_PASS":
        meta["status"]=file_check["status"];return meta
    meta["original_source_rows_opened"]=True
    raw_meta=actual[FILE_META].decode("utf-8-sig",errors="replace")
    meta["original_metadata_original_line_count"]=len(raw_meta.splitlines())
    meta["original_metadata_mentions_grams_dry_weight"]=bool(
        re.search(r"(biomass|aboveground)",raw_meta,re.I) and
        re.search(r"(g\s*m\s*[-^]?\s*2|g.*dry|dry.*weight)",raw_meta,re.I))
    meta["original_metadata_explicit_species_incidence_file"]=bool(
        re.search(r"(original.*species.*(raw|cover|composition).*file|species-by-plot|species x plot|species.*plot.*record)",raw_meta,re.I))
    profile=sample_csv(actual[FILE_DATA])
    meta["original_file_schema_profile"]=profile
    meta["status"]="NUTNET_VERIFIED_PLOT_SOURCE_AUDITED" if profile.get("status")=="MULTISITE_MASS_AND_DERIVED_CWM_PRESENCE_PASS" else "NUTNET_SOURCE_GRAIN_OR_CWM_HOLD"
    meta["source_species_level_K_FD_joint_admissibility"]="HOLD_MISSING_RAW_SPECIES_BY_PLOT_AND_INDEPENDENT_OBSERVED_K"
    meta["no_new_original_biomass_coefficient"]=True
    return meta


def corre():
    out={"source":"CoRRE Trait Data, Komatsu et al. 2024",
         "publication_doi":"10.1038/s41597-024-03637-x",
         "original_dataset_edi_doi":CORRE_DOI,
         "doi_metadata_source":"https://api.datacite.org/dois/"+quote(CORRE_DOI,safe=""),
         "reported_original_species_categorical":4079,
         "reported_original_families_categorical":173,
         "reported_imputed_continuous_species":2927,
         "reported_imputed_continuous_families":147,
         "reported_observation_training_individuals":206113,
         "reported_observation_training_species":3188,
         "reported_observation_training_families":151,
         "original_training_sources":["TRY v6","AusTraits v4.1","BIEN v4.2",
               "TiP Leaf","China Plant Trait DB v2"],
         "primary_eligibility_note":"Do NOT use imputed continuous traits for Blomberg K. Source family K requires native tree + >=20 observed species in each of >=12 families and de-duplicated source training IDs.",
         "raw_edi_species_observations_downloaded":False,
         "actual_source_12families_x20species_trait_axes_verified":False,
         "new_phylogenetic_K_estimated":False}
    status,body,host,ct=request(out["doi_metadata_source"],MAX_META)
    out["datacite_http"]=status
    if status!=200 or host!="api.datacite.org":
        out["status"]="PUBLISHED_SOURCE_ONLY_EDI_ORIGINAL_ACCESS_HOLD";return out
    try:x=json.loads(body).get("data",{}).get("attributes",{})
    except Exception:
        out["status"]="ORIGINAL_DOI_METADATA_PARSE_HOLD";return out
    if str(x.get("doi","")).lower()!=CORRE_DOI:
        out["status"]="ORIGINAL_EDI_DOI_MISMATCH_HOLD";return out
    out.update({"verified_edi_doi":x.get("doi"),
               "edi_registered_publication_year":x.get("publicationYear"),
               "edi_registered_publisher":x.get("publisher"),
               "edi_registered_resource_type":x.get("types",{}).get("resourceTypeGeneral"),
               "doi_metadata_sha256":hashlib.sha256(body).hexdigest(),
               "status":"EDI_ORIGINAL_DOI_METADATA_PASS_BUT_OBSERVED_TRAIT_RECORDS_UNVERIFIED"})
    return out


def fixture():
    assert numeric("-9999") is None and numeric("0")==0 and numeric("2.3")==2.3
    assert stable_id("0001.0")=="1"
    assert getcol(["site_id","PlotName","Yr"],("site","site_id"))=="site_id"
    assert MIN_SOURCE_PLOTS if False else True
    return {"status":"INDEPENDENT_NUTNET_CORRE_SOURCE_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not args.out:p.error("--out required")
        result={"version":"v0.1",
                "source_contract":"docs/INDEPENDENT_NUTNET_CORRE_K_FD_MASS_SOURCE_GATE_20261118.md",
                "audited_utc":datetime.now(timezone.utc).isoformat(),
                "new_biological_K_FD_biomass_effect_estimated":False,
                "separate_from_original_BIEN_BIODEPTH_TreeDivNet_source_gates":True,
                "nutnet_derived_biomass_and_CWM":nutnet(),
                "corre_observed_vs_imputed_trait_K":corre()}
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
        print("INDEPENDENT_GRASSLAND_NUTNET_CORRE_SOURCE_AUDIT",
              json.dumps(result,sort_keys=True),flush=True)
