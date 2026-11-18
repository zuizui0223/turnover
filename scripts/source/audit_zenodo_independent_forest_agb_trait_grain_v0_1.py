#!/usr/bin/env python3
"""Source-only original Zenodo 19609795 forest AGB + traits grain / provenance.

Contract fixed before ANY downloaded original source row/effect:
docs/INDEPENDENT_K_FD_AGB_NEW_SOURCE_PILOT_20261118.md.
No biomass/trait correlations, no ecology fit. Exact Zenodo-hosted
manifest, MD5 bytes; report only source nonraw column names/counts.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path
from urllib.parse import urlsplit,unquote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

RECORD=19609795
DOI="10.5281/zenodo.19609795"
API=f"https://zenodo.org/api/records/{RECORD}"
HEADERS={"User-Agent":"turnover-source-first-independent-forest-AGB-trait-20261118/0.1",
         "Accept":"application/json, text/csv, */*"}
TARGET={
 "Forest_AGB_Data. Final.csv":"c3ffed15932611dca604dcd9e67d9bb8",
 "README Dataset Description.txt":"6f0e782ec7968d35f5ee5f5539124b24",
}
MAX_SOURCE_BYTES=1_000_000
MAX_SOURCE_ROWS=50000
SENTINELS={"","-9999","-9999.0","NA","N/A","nan","NaN","null","None","NULL"}
EFFECT_COL=re.compile(r"agb|biomass|above.?ground.?bio|aboveground",re.I)
ORIGINAL_TRAIT_COL=re.compile(r"(^sla$|wood.?density|(^wd$)|(^lncm$)|leaf.?nitrogen|specific.?leaf|root.?length|leaf.?area)",re.I)
AGGREGATE_MARK=re.compile(r"^cwm|community.?weighted|^fd(?:is|iv|iv)?$|functional.?divers|rao|^fric|^feve|^fdiv|^fdis",re.I)


def bounded(url:str,cap:int):
    t=urlsplit(url)
    if t.scheme!="https" or t.hostname!="zenodo.org":
        raise ValueError("SOURCE_IDENTITY_HOLD: original URL not official zenodo.org")
    req=Request(url,headers=HEADERS)
    with urlopen(req,timeout=100) as r:
        final=urlsplit(r.url)
        # A trusted official endpoint may redirect to Zenodo-managed object
        # storage; do not follow arbitrary non-Zenodo file hosts.
        allowed=(final.hostname=="zenodo.org" or
                 final.hostname in ("zenodo-records.s3.amazonaws.com",
                                    "zenodo-prod-files.s3.amazonaws.com"))
        if not allowed:
            raise ValueError("SOURCE_IDENTITY_HOLD: unexpected original data redirect")
        data=r.read(cap+1)
        if len(data)>cap:raise ValueError("SOURCE_ACCESS_HOLD: original file size cap exceeded")
        return data


def source_csv_profile(blob:bytes)->dict:
    source=blob.decode("utf-8-sig")
    first=source[:8000]
    dialect=csv.Sniffer().sniff(first,delimiters=",;\t")
    reader=csv.DictReader(io.StringIO(source),dialect=dialect)
    heads=reader.fieldnames
    if not heads or len(heads)!=len(set(heads)) or len(heads)>250:
        raise ValueError("SOURCE_SCHEMA_HOLD: no unique valid source header")
    if any(not x or x.strip()!=x for x in heads):
        raise ValueError("SOURCE_SCHEMA_HOLD: missing/malformed original headers")
    rows=[]
    for r in reader:
        if len(rows)>=MAX_SOURCE_ROWS:raise ValueError("SOURCE_SCHEMA_HOLD: too many records")
        if None in r:raise ValueError("SOURCE_SCHEMA_HOLD: extra field in original record")
        rows.append(r)
    if not rows:raise ValueError("SOURCE_SCHEMA_HOLD: source csv empty")
    missing={h:sum(1 for row in rows if row[h] is None or row[h].strip() in SENTINELS) for h in heads}
    numeric={}
    for h in heads:
        good=0
        neg=0
        for r in rows:
            v=r.get(h)
            if v is None or v.strip() in SENTINELS:continue
            try:
                x=float(v)
            except (ValueError,OverflowError):continue
            if math.isfinite(x):
                good+=1;neg+=int(x<0)
        numeric[h]={"finite_numeric_values":good,"negative_numeric_values":neg}
    def candidate(pattern):
        return [h for h in heads if pattern.search(h)]
    plot=re.compile(r"^(plot|plot_id|plotid|quadrat|quadrat_id|sample_plot|plot_no|plot_no\.)$",re.I)
    site=re.compile(r"^(site|site_id|siteid|forest|forest_id|forest_type|location|region|reserve|forest_name)$",re.I)
    species=re.compile(r"^(species|species_name|species_id|sp_name|scientific_name|taxon|taxon_name|species_code)$",re.I)
    plot_keys=candidate(plot)
    site_keys=candidate(site)
    spp=candidate(species)
    precomputed=candidate(AGGREGATE_MARK)
    direct_trait=candidate(ORIGINAL_TRAIT_COL)
    biomass=candidate(EFFECT_COL)
    distinct=lambda col:len({r[col].strip() for r in rows if r.get(col) and r[col].strip() not in SENTINELS})
    source_sites={h:distinct(h) for h in site_keys}
    source_plots={h:distinct(h) for h in plot_keys}
    grouping={}
    if plot_keys:
        keys=[site_keys[0]] if site_keys else []
        keys+=plot_keys[:1]
        counts={}
        for r in rows:
            k=tuple(r.get(q,"").strip() for q in keys)
            if any(not v for v in k):continue
            counts[k]=counts.get(k,0)+1
        grouping={
           "source_plot_key_parts":keys,"n_unique_named_composite_plot_keys":len(counts),
           "n_composite_plot_keys_with_duplicate_source_rows":sum(n>1 for n in counts.values()),
           "max_source_rows_per_composite_plot_key":max(counts.values(),default=0),
           "n_rows_with_nonmissing_composite_plot_key":sum(counts.values())
        }
    return {
      "source_columns":heads,
      "n_original_source_rows":len(rows),
      "n_original_source_columns":len(heads),
      "source_field_missing_counts":missing,
      "source_numeric_field_profile":numeric,
      "original_candidate_plot_ID_columns":plot_keys,
      "original_candidate_site_type_columns":site_keys,
      "original_candidate_species_taxon_columns":spp,
      "source_site_or_forest_type_cardinality":source_sites,
      "source_plot_ID_cardinality":source_plots,
      "source_derived_FD_CWM_composition_index_columns":precomputed,
      "source_original_direct_species_trait_candidates":direct_trait,
      "source_biomass_field_candidates":biomass,
      "source_original_plot_grain_check":grouping,
      "species_trait_community_join_proven":False,
    }


def main():
    audit={
      "version":"v0.1","dataset_doi":DOI,"original_zenodo_record_id":RECORD,
      "status":"SOURCE_IDENTITY_HOLD","no_ecological_effect_estimated":True,
      "no_original_data_rows_committed":True,
      "frozen_protocol":"docs/INDEPENDENT_K_FD_AGB_NEW_SOURCE_PILOT_20261118.md",
      "prior_BIEN_sPlotOpen_BIODEPTH_NEON_gates_unchanged":True,
    }
    meta=json.loads(bounded(API,3_000_000))
    if int(meta.get("id",0))!=RECORD or meta.get("doi","").casefold()!=DOI.casefold():
        raise ValueError("SOURCE_IDENTITY_HOLD: original Zenodo record DOI/id did not match")
    public=meta.get("access",{}).get("record","public")=="public"
    files=meta.get("files") or []
    found={f.get("key") or f.get("filename"):f for f in files}
    audit["original_catalogue"]={
       "source_record_id":meta["id"],"DOI":meta["doi"],
       "published":meta.get("created"),"modified":meta.get("updated"),
       "original_source_license":(meta.get("metadata") or {}).get("rights",[])[:1],
       "original_record_access_public":public,
       "n_original_files":len(files),
       "source_file_inventory":[{"name":q,"size":f.get("size"),
                                  "checksum":f.get("checksum")} for q,f in sorted(found.items())],
    }
    if not public: audit["status"]="AUTH_HOLD";return audit
    verified={}
    for name,md5 in TARGET.items():
        entry=found.get(name)
        if entry is None:
            audit["status"]="SOURCE_IDENTITY_HOLD"
            audit["reason"]="Exact original public source filename not listed in current original Zenodo record"
            return audit
        targetsize=entry.get("size")
        if not isinstance(targetsize,int) or targetsize<=0 or targetsize>MAX_SOURCE_BYTES:
            audit["status"]="DATA_ACCESS_HOLD"
            audit["reason"]="Missing source size or exceeds 1 MB bound"
            return audit
        original_checksum=str(entry.get("checksum") or "").lower().removeprefix("md5:")
        if original_checksum!=md5:
            audit["status"]="SOURCE_IDENTITY_HOLD"
            audit["reason"]="Original official Zenodo expected file MD5 differs from published source catalogue"
            return audit
        url=((entry.get("links") or {}).get("self") or
             (entry.get("links") or {}).get("content"))
        if not url:
            audit["status"]="DATA_ACCESS_HOLD"
            audit["reason"]="Official file metadata does not provide source URL"
            return audit
        data=bounded(url,MAX_SOURCE_BYTES)
        if len(data)!=targetsize or hashlib.md5(data).hexdigest()!=md5:
            audit["status"]="SOURCE_IDENTITY_HOLD"
            audit["reason"]="Original source file bytes did not replay official length and checksum"
            return audit
        verified[name]={"name":name,"bytes":len(data),"md5":md5,
                        "original_source_record_id":RECORD}
        if name.endswith(".csv"):
            audit["source_csv_nonraw_profile"]=source_csv_profile(data)
        else:
            raw=data.decode("utf-8-sig",errors="replace")
            rlines=raw.splitlines()
            verified[name]["n_original_document_lines"]=len(rlines)
            verified[name]["mentions_species_level_traits"]=bool(re.search(r"species.level|species.?wise|species.?trait",raw,re.I))
            verified[name]["mentions_original_measured_biomass"]=bool(re.search(r"measur.{0,50}(?:AGB|above.?ground.?biomass)",raw,re.I|re.S))
    audit["verified_original_files"]=list(verified.values())
    c=audit["source_csv_nonraw_profile"]
    has_bio=bool(c["source_biomass_field_candidates"])
    has_plot=bool(c["original_candidate_plot_ID_columns"])
    has_spp=bool(c["original_candidate_species_taxon_columns"])
    has_traits=bool(c["source_original_direct_species_trait_candidates"])
    if not has_bio:
        audit["status"]="SOURCE_BIOMASS_MISSING_HOLD"
    elif not has_plot:
        audit["status"]="SOURCE_SITE_SUPPORT_HOLD"
        audit["reason"]="No explicit source plot ID column. Stand plot/source type cannot be conflated."
    elif not has_spp or not has_traits:
        audit["status"]="PLOT_SUMMARY_ONLY_HOLD"
        audit["reason"]="Original plot AGB present, but source lacks complete per-species original taxon and trait fields for a same-plot K/FD bridge."
    else:
        audit["status"]="SOURCE_GRANULARITY_REVIEW_REQUIRED"
        audit["reason"]="Original biomass/plot/species/trait fields present; require separate exact-plot species roster and original multi-site/source measurement provenance audit before any effect."
    audit["original_biomass_response_coefficients_estimated"]=0
    audit["family_specific_phylogenetic_K_estimated"]=0
    return audit


def fixture():
    raw=b"site,plot,AGB,CWM_SLA,FD,soil_pH\nA,p1,20.0,6.0,0.2,7\nA,p2,21.0,5.0,0.5,6\n"
    x=source_csv_profile(raw)
    assert x["n_original_source_rows"]==2
    assert x["original_candidate_plot_ID_columns"]==["plot"]
    assert x["original_candidate_site_type_columns"]==["site"]
    assert x["original_candidate_species_taxon_columns"]==[]
    assert x["source_biomass_field_candidates"]==["AGB"]
    assert "FD" in x["source_derived_FD_CWM_composition_index_columns"]
    assert not x["species_trait_community_join_proven"]
    return {"status":"INDEPENDENT_ZENODO_ORIGINAL_SOURCE_SCHEMA_FIXTURE_PASS","checks":7}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(fixture(),sort_keys=True))
    else:
        if not args.out:p.error("--out required")
        try:
            data=main()
        except (ValueError,URLError,HTTPError,OSError,TimeoutError,UnicodeError,
                json.JSONDecodeError,csv.Error) as e:
            data={"version":"v0.1","dataset_doi":DOI,"status":"DATA_ACCESS_HOLD" if isinstance(e,(URLError,HTTPError,TimeoutError,OSError)) else "SOURCE_IDENTITY_HOLD",
                  "source_error_class":type(e).__name__,
                  "reason":"Source original file/API unavailable, malformed or not safely interpretable: "+str(e)[:220],
                  "no_ecological_effect_estimated":True,
                  "no_original_data_rows_committed":True}
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("ZENODO_INDEPENDENT_FOREST_SOURCE_GATE",json.dumps(data,sort_keys=True),flush=True)
