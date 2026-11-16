#!/usr/bin/env python3
"""Access/source-only qualification of two independent field trait×biomass datasets.

Frozen design: docs/INDEPENDENT_PLOT_TRAIT_BIOMASS_SOURCE_ROUTE_20261116.md.
This is NOT a biological outcome model. The NASA original leaf/biomass data
remain external. Only source metadata and aggregate original-plot coverage
may be exported; never print original rows, credentials, or signed data links.
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
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT="https://datadryad.org"
DOI_DRYAD="10.5061/dryad.kprr4xh8v"
DOI_NASA="10.3334/ORNLDAAC/1292"
UA="turnover-independent-original-field-traits-source-audit/0.1 (citation: NASA ORNL DAAC/1292, Dryad/kprr4xh8v)"
MAX_FILE=1_000_000
TIMEOUT=45
DELAY=1.5
SENTINELS={"","-9999","-9999.0","NaN","NA","N/A","None","NULL","null"}


def request(url:str, maxbytes:int=MAX_FILE, method:str="GET"):
    last=None
    for attempt in range(2):
        try:
            r=Request(url,headers={"User-Agent":UA,"Accept":"application/json, text/csv, */*"},method=method)
            with urlopen(r,timeout=TIMEOUT) as res:
                status=getattr(res,"status",200)
                if method=="HEAD":
                    return status,b"",res.headers.get("Content-Type","")
                blob=res.read(maxbytes+1)
                if len(blob)>maxbytes: raise ValueError("SOURCE_HOLD: source request exceeded max bytes")
                return status,blob,res.headers.get("Content-Type","")
        except (HTTPError,URLError,TimeoutError,ConnectionError,ValueError) as e:
            last=e
            if isinstance(e,HTTPError) and e.code in (400,401,403,404,405,410,429):break
            if attempt==0:time.sleep(DELAY)
    if isinstance(last,HTTPError):
        return int(last.code),b"",str(last.headers.get("Content-Type","")) if last.headers else ""
    return "NETWORK_HOLD",b"",""


def asjson(url:str):
    status,raw,mimetype=request(url,maxbytes=2_500_000)
    if status!=200:return status,None
    try:
        return 200,json.loads(raw.decode("utf-8-sig"))
    except Exception:
        return "INVALID_JSON_HOLD",None


def normalize(s)->str:
    return " ".join(str(s or "").strip().casefold().replace("_"," ").split())


def key(s)->str:
    val=str(s or "").strip()
    if not val:return ""
    if re.fullmatch(r"0*[0-9]+(?:\\.0+)?",val):
        return str(int(float(val)))
    return val.casefold()


def number(s,allow_zero=True):
    if s is None or str(s).strip() in SENTINELS:return None
    try:
        v=float(s)
        if not math.isfinite(v) or v<0 or (not allow_zero and v==0):return None
        return v
    except Exception:return None


def parse_csv(raw:bytes):
    text=raw.decode("utf-8-sig")
    data=list(csv.DictReader(io.StringIO(text)))
    if not data:return [],[]
    cols=list(data[0])
    if any(None in row for row in data):
        raise ValueError("SOURCE_HOLD: malformed delimited original data rows")
    if len(cols)!=len(set(cols)):raise ValueError("SOURCE_HOLD: duplicate original source fields")
    return data,cols


def api_link(root:str,href:str)->str:
    from urllib.parse import urljoin,urlsplit
    if not isinstance(href,str) or not href.strip():
        raise ValueError("Invalid source link")
    dest=urljoin(root,href)
    p=urlsplit(dest)
    if p.scheme!="https" or p.hostname not in {"datadryad.org","www.datadryad.org"}:
        raise ValueError("SOURCE_HOLD: non-Dryad data URL in official metadata")
    return dest


def nasa_probe() -> dict:
    out={
        "dataset":"NASA NACP TERRA-PNW, ORNLDAAC/1292",
        "DOI":DOI_NASA,
        "catalogue_reference":"https://daac.ornl.gov/NACP/guides/NACP_TERRA-PNW.html",
        "source_published_leaf_individuals":1296,
        "source_published_biomass_site_records":266,
        "source_published_species":35,
        "source_published_projects":6,
        "source_measurement":"original measured leaf traits; aboveground tree wood+foliage carbon and production estimates, not destructive biomass dry-weight",
        "status":"METADATA_ONLY",
        "source_BIOMASS_gC_m2_field":"AG_BIOMASS_TREE_TOTAL_AS_CARBON",
        "source_PROD_gC_m2_yr_field":"AG_PROD_TREE_TOTAL_AS_CARBON",
        "bio_data_downloaded":False,
        "ecological_effect_estimated":False
    }
    url="https://cmr.earthdata.nasa.gov/search/collections.json?"+urlencode({"doi":DOI_NASA,"page_size":3})
    code,data=asjson(url)
    out["NASA_CMR_DOI_lookup_status"]=code
    entries=(data.get("feed",{}).get("entry",[]) if isinstance(data,dict) else [])
    if not entries:
        url2="https://cmr.earthdata.nasa.gov/search/collections.json?"+urlencode(
            {"short_name":"NACP_TERRA-PNW","page_size":5})
        code2,data2=asjson(url2)
        out["NASA_CMR_short_name_lookup_status"]=code2
        entries=data2.get("feed",{}).get("entry",[]) if isinstance(data2,dict) else []
    selected=[r for r in entries if ("TERRA" in str(r.get("title","")).upper()
              or "TERRA" in str(r.get("short_name","")).upper())]
    out["cmr_published_collections_matched"]=len(selected)
    if not selected:
        out["status"]="METADATA_ONLY"
        out["reason"]="Public NASA ORNL original-data catalog confirmed in published documentation, but exact CMR dataset granule access not established."
        return out
    original=selected[0]
    out["cmr_collection_concept_id"]=original.get("id")
    out["cmr_short_name"]=original.get("short_name")
    out["cmr_version_id"]=original.get("version_id")
    collection_id=str(original.get("id") or "")
    if not collection_id:
        out["status"]="METADATA_ONLY"
        return out
    granule_url="https://cmr.earthdata.nasa.gov/search/granules.json?"+urlencode(
        {"collection_concept_id":collection_id,"page_size":50})
    code3,granules=asjson(granule_url)
    out["cmr_granule_lookup_status"]=code3
    gr=granules.get("feed",{}).get("entry",[]) if isinstance(granules,dict) else []
    out["cmr_granule_count_returned"]=len(gr)
    candidates=[]
    for g in gr:
        for l in g.get("links",[]):
            link=l.get("href","")
            if not isinstance(link,str):continue
            if (l.get("inherited") is True or l.get("rel","").endswith("metadata#")):continue
            lower=link.lower()
            if ("leaf_trait" in lower or "biomass_productivity" in lower) and (".csv" in lower or "/data/" in lower):
                candidates.append((link,"leaf" if "leaf_trait" in lower else "biomass"))
    # URL contents never logged or stored because signed URLs are ephemeral.
    out["cmr_original_csv_links_discovered"]=len(candidates)
    checked={}
    for u,typ in candidates[:8]:
        if typ in checked:continue
        status,blob,mime=request(u,method="HEAD")
        if status==405:
            status,blob,mime=request(u,maxbytes=2048,method="GET")
        checked[typ]=status
    out["official_original_data_link_access_status"]=checked
    if checked and all(s==200 for s in checked.values()) and set(checked)=={"leaf","biomass"}:
        out["status"]="PUBLIC_FILE_LINKS_HEAD_PASS_ONLY"
        out["reason"]="Two original files respond to HEAD; numeric source rows not downloaded or joined here. Independent full file SHA+source join remains required."
    elif any(s in (401,403) for s in checked.values()):
        out["status"]="AUTH_HOLD"
        out["reason"]="NASA CMR names original file references but actual data access requires credentials; do not seek bypass."
    elif checked:
        out["status"]="DATA_ACCESS_HOLD"
        out["reason"]="Official file endpoint was not successfully accessible for both required original CSVs."
    else:
        out["status"]="METADATA_ONLY"
        out["reason"]="CMR collection exists, but no source-authorized explicit leaf and biomass CSV download links were discovered."
    return out


def dryad_probe() -> dict:
    out={
      "dataset":"2026 MA Continuous Forest Inventory original local trait / allometric AGB",
      "DOI":DOI_DRYAD,
      "source_expected_inventory_plots":304,
      "source_expected_inventory_plot_years":626,
      "source_expected_local_trait_tree_records":142,
      "source_expected_local_trait_plots":26,
      "source_expected_original_forests":7,
      "status":"METADATA_ONLY",
      "original_files_retrieved":[],
      "biomass_effect_estimated":False,
      "source_grain":"local treeID trait observations vs original 2000–2021 inventory plot-year response"
    }
    doi=quote("doi:"+DOI_DRYAD,safe="")
    code,data=asjson(ROOT+"/api/v2/datasets/"+doi)
    out["dryad_dataset_meta_api_status"]=code
    if code!=200 or not isinstance(data,dict):
        out["status"]="DATA_ACCESS_HOLD"
        out["reason"]="Original public Dryad dataset API unavailable or blocked; do not infer source row coverage from abstract."
        return out
    out["dryad_dataset_id"]=data.get("id")
    out["dryad_version_number"]=data.get("versionNumber")
    out["dryad_visibility"]=data.get("visibility")
    out["dryad_license"]=data.get("license")
    version_href=((data.get("_links") or {}).get("stash:version") or {}).get("href")
    if not version_href:
        out["status"]="METADATA_ONLY";out["reason"]="Dryad metadata has no resolvable version link";return out
    version_url=api_link(ROOT,version_href)
    vcode,vdata=asjson(version_url)
    out["dryad_version_meta_api_status"]=vcode
    if vcode!=200 or not isinstance(vdata,dict):
        out["status"]="DATA_ACCESS_HOLD";return out
    files_href=((vdata.get("_links") or {}).get("stash:files") or {}).get("href")
    if not files_href:
        vi=vdata.get("id")
        if vi is None:
            out["status"]="METADATA_ONLY";return out
        files_href="/api/v2/versions/"+str(vi)+"/files"
    files_url=api_link(ROOT,files_href)
    fcode,fmeta=asjson(files_url)
    out["dryad_files_api_status"]=fcode
    if fcode!=200 or not isinstance(fmeta,dict):
        out["status"]="DATA_ACCESS_HOLD";return out
    embedded=fmeta.get("_embedded") or {}
    files=(embedded.get("stash:files") or embedded.get("files") or fmeta.get("files") or [])
    if not isinstance(files,list):files=[]
    out["dryad_files_in_version"]=len(files)
    required=("trait_obs.csv","cfi_ba.csv","CFI_AGB_covars_092026.csv")
    matches={}
    for item in files:
        name=str(item.get("path") or item.get("filename") or item.get("name") or "")
        short=name.split("/")[-1].lower()
        for wanted in required:
            if short==wanted.lower():
                if wanted in matches:
                    raise ValueError("SOURCE_HOLD: duplicate expected source file labels")
                matches[wanted]=item
    out["required_Dryad_files_present"]=sorted(matches)
    if len(matches)!=3:
        out["status"]="DATA_ACCESS_HOLD"
        out["reason"]="All three original local traits, species composition, and biomass files are not advertised in one Dryad version."
        return out
    original={}
    for name in required:
        item=matches[name]
        file_id=item.get("id")
        size=item.get("size")
        if file_id is None or size is not None and int(size)>MAX_FILE:
            out["status"]="DATA_ACCESS_HOLD";out["reason"]="Expected file ID missing or unexpectedly large";return out
        url=ROOT+"/api/v2/files/"+str(file_id)+"/download"
        status,raw,mime=request(url,maxbytes=MAX_FILE)
        if status!=200:
            out["status"]="AUTH_HOLD" if status in (401,403) else "DATA_ACCESS_HOLD"
            out["reason"]="Dryad public original file download request not accessible; HTTP status logged without original rows"
            out["file_download_status_for_"+name]=status
            return out
        rows,cols=parse_csv(raw)
        if not rows:
            out["status"]="INSUFFICIENT_SUPPORT_HOLD";out["reason"]="Original downloaded source empty";return out
        original[name]=(rows,cols)
        out["original_files_retrieved"].append({
            "filename":name,"source_file_id":file_id,"number_rows":len(rows),
            "number_columns":len(cols),"sha256":hashlib.sha256(raw).hexdigest(),
            "source_checksum":item.get("digest"),
            "source_checksum_type":item.get("digestType")
        })
    return audit_dryad_source(original,out)


def first_col(cols,options):
    for n in options:
        if n in cols:return n
    low={c.casefold():c for c in cols}
    for n in options:
        if n.casefold() in low:return low[n.casefold()]
    return None


def audit_dryad_source(original:dict,out:dict)->dict:
    trait,tcols=original["trait_obs.csv"]
    inv,icols=original["CFI_AGB_covars_092026.csv"]
    base,bcols=original["cfi_ba.csv"]
    trplot=first_col(tcols,["plot"])
    trsp=first_col(tcols,["Species"])
    irplot=first_col(icols,["PLOT","plot"])
    iryear=first_col(icols,["INVYR","year"])
    irbm=first_col(icols,["agb.plot","agb.ha","agb.plot.ha"])
    baplot=first_col(bcols,["PLOT","plot"])
    if not all((trplot,trsp,irplot,iryear,irbm,baplot)):
        out["status"]="SCHEMA_HOLD"
        out["reason"]="Missing required original PLOT/Species/INVYR/AGB or wide composition keys"
        out["available_original_columns"]={k:v[1][:55] for k,v in original.items()}
        return out
    t_trait=[c for c in ("sla","wd","leaf_n","leaf_p","cn_ratio") if first_col(tcols,[c])]
    if not t_trait:
        out["status"]="SCHEMA_HOLD";out["reason"]="No genuine locally observed trait measurement fields";return out
    t_species=collections.defaultdict(set)
    t_individuals=collections.Counter()
    for row in trait:
        p=key(row[trplot]);sp=normalize(row[trsp])
        if not p or not sp:continue
        if any(number(row[first_col(tcols,[col])],allow_zero=False) is not None for col in t_trait):
            t_species[p].add(sp);t_individuals[p]+=1
    i_year=collections.defaultdict(set)
    biomass_positive_plots=set()
    for row in inv:
        p=key(row[irplot]);yr=key(row[iryear])
        if not p or not yr:continue
        i_year[p].add(yr)
        if number(row[irbm]) is not None:
            biomass_positive_plots.add(p)
    core=[c for c in bcols if c.casefold() not in {"plot","plotyr","invyr","year"}]
    names={normalize(c):c for c in core}
    cover_plots=collections.defaultdict(set)
    for row in base:
        p=key(row[baplot])
        if not p:continue
        for norm,col in names.items():
            if number(row[col],allow_zero=False) is not None:
                cover_plots[p].add(norm)
    overlap=set(t_species)&biomass_positive_plots&set(cover_plots)
    actual={p:len(t_species[p]&cover_plots[p]) for p in overlap}
    two=[p for p,n in actual.items() if n>=2]
    forestcol=first_col(icols,["FOREST","forest","StateForest","state_forest","SITE","site"])
    forests=collections.defaultdict(set)
    if forestcol:
        for row in inv:
            p=key(row[irplot])
            if p in two:
                label=normalize(row[forestcol])
                if label:forests[label].add(p)
    n_supported=sum(len(x)>=3 for x in forests.values())
    out.update({
        "source_local_trait_individuals_with_numeric_measurement":sum(t_individuals.values()),
        "source_local_trait_unique_plot_keys":len(t_species),
        "source_inventory_unique_plot_keys":len(i_year),
        "source_inventory_plot_year_keys":sum(len(y) for y in i_year.values()),
        "source_community_composition_plot_keys":len(cover_plots),
        "source_plot_overlap_trait_inventory_composition":len(overlap),
        "source_plots_local_2plus_original_species_present_in_positive_basal_area":len(two),
        "source_plots_local_1plus_species_present_in_positive_basal_area":sum(v>=1 for v in actual.values()),
        "source_positive_original_response_plot_keys":len(biomass_positive_plots),
        "source_original_forest_id_available":bool(forestcol),
        "source_forests_with_at_least_three_local_2species_plots":n_supported,
        "traits_source_locally_measured_fields":t_trait,
        "source_biomass_field":irbm,
        "source_CFI_responses_are_allometry_derived":True,
        "ecological_effect_estimated":False,
    })
    if len(two)>=15 and forestcol and n_supported>=3:
        out["status"]="SOURCE_GATE_PASS"
        out["reason"]="Original local trait, positive species relative basal area, original plot-year carbon biomass and multi-forest identity source support sufficient for a separately frozen test"
    elif len(overlap)<15:
        out["status"]="INSUFFICIENT_SUPPORT_HOLD"
        out["reason"]="Fewer than 15 source local-trait plots can be exactly paired to positive original biomass and original plot-specific composition"
    elif len(two)<15:
        out["status"]="TAXON_CROSSWALK_HOLD"
        out["reason"]="Fewer than 15 original plots have >=2 exact common-name-matched locally measured species with positive original relative basal area"
    elif not forestcol or n_supported<3:
        out["status"]="SITE_IDENTITY_HOLD"
        out["reason"]="Cannot verify at least three independent forests with >=3 fully supported original plots; do not invent field locations"
    return out


def fixture():
    assert normalize("  Red_Oak ")=="red oak"
    assert key("000012.00")=="12"
    assert number("-9999") is None and number("0")==0
    assert number("NaN") is None and number("1.23",allow_zero=False)==1.23
    demo=b"PLOT,Species,sla\n001,A,2.5\n002,B,\n"
    rows,col=parse_csv(demo)
    assert len(rows)==2 and col==["PLOT","Species","sla"]
    assert len([x for x in ("trait_obs.csv","cfi_ba.csv","CFI_AGB_covars_092026.csv")])==3
    return {"status":"SOURCE_SCHEMA_FIXTURE_PASS","checks":6}


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        print(json.dumps(fixture(),sort_keys=True));return
    if not a.out:p.error("--out is required")
    results={"version":"v0.1","study":"independent source-only (no new ecology)",
       "contract":"docs/INDEPENDENT_PLOT_TRAIT_BIOMASS_SOURCE_ROUTE_20261116.md",
       "data_fetched_at_UTC":None,"candidates":[]}
    from datetime import datetime,timezone
    results["data_fetched_at_UTC"]=datetime.now(timezone.utc).isoformat()
    for tag,func in [("NASA_ORNL",nasa_probe),("Dryad_2026_local",dryad_probe)]:
        try:
            candidate=func()
        except Exception as exc:
            candidate={"dataset":tag,"status":"TECHNICAL_HOLD",
                       "exception_class":type(exc).__name__,
                       "error_summary":str(exc)[:300],
                       "ecological_effect_estimated":False}
        results["candidates"].append(candidate)
        print("SOURCE_ONLY_CANDIDATE",json.dumps({
           k:v for k,v in candidate.items()
           if k not in ("available_original_columns",)
        },sort_keys=True),flush=True)
    results["main_result"]="SOURCE_ONLY_NO_BIOLOGICAL_EFFECT"
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(results,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("INDEPENDENT_FIELD_SOURCE_GATE_COMPLETE",
          json.dumps({d["dataset"]:d["status"] for d in results["candidates"]},sort_keys=True))


if __name__=="__main__":
    main()
