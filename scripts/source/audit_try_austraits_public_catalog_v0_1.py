#!/usr/bin/env python3
"""Conservative public TRY-directory vs AusTraits source-lineage metadata check.

The publicly indexed TRY Data Explorer advertises database v6; this audit
MUST NOT promote it to TRY v7 trait availability, family support or source
independence. No TRY measurements or biological K outcomes are opened.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote
import requests
import bs4
import duckdb
import pandas as pd
import yaml

STATUS="TRY_PUBLIC_DIRECTORY_VERSUS_AUSTRAITS_CORE_METADATA_AUDITED"
DOI_RE=re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+",re.I)

def normalized_doi(s):
    if not s:return None
    t=str(s).strip().lower()
    t=re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)","",t)
    m=DOI_RE.search(t)
    return m.group(0).rstrip(".,;") if m else None

def key(s):
    return set(re.findall(r"[a-z0-9]+",str(s).lower().replace("_"," "))) - {
        "data","dataset","traits","trait","plant","plants","the","for",
        "and","of","from","a","an","with","2018","2019","2020","2021","2022"}

def name_overlap(a,b):
    x,y=key(a),key(b)
    return float(len(x&y)/len(x|y)) if x and y else 0.

def parse_try_catalog(html):
    soup=bs4.BeautifulSoup(html,"html.parser")
    tables=soup.find_all("table")
    possible=[]
    for table in tables:
        name=" ".join(table.stripped_strings)
        if "DatasetID" not in name[:1000] or "Dataset" not in name[:1000]:
            continue
        for tr in table.find_all("tr"):
            cells=tr.find_all("td",recursive=False)
            if len(cells)<2:continue
            fields=[c.get_text(" ",strip=True) for c in cells]
            if not re.fullmatch(r"\d{1,6}",fields[0]):continue
            if not fields[1]:continue
            access=next((p for p in fields[2:] if p.lower().startswith(
                ("public","restricted","cur. na"))), "UNVERIFIED")
            # Hyperlinks in the public TRY directory sometimes resolve to
            # the original published source. Collect DOI strings from *links
            # only*, not from any trait/value table.
            linked_dois=sorted({d for cell in cells[1:]
                                for link in cell.find_all("a",href=True)
                                if (d:=normalized_doi(link.get("href")))})
            # TRY wraps linked citations with a literal '(link)' anchor in
            # its visible dataset title; this is not part of the study name.
            dataset_title=re.sub(r"\\s*\\(?link\\)?\\s*$","",fields[1],flags=re.I).strip()
            if not dataset_title:continue
            possible.append({"try_dataset_id":int(fields[0]),
                             "try_dataset_title":dataset_title,
                             "public_explorer_access_status":access,
                             "try_source_link_dois":";".join(linked_dois)})
    if not possible:
        # Fail closed rather than interpreting a login/maintenance page as
        # an empty data-custodian registry.
        raise ValueError("TRY public catalogue HTML has no DatasetID table")
    # TRY's HTML can nest its actual dataset table in a surrounding layout
    # table; recursive scans then encounter the exact same <tr> twice.
    # Accept only identical duplicate representations. Conflicting public
    # entries for the same ID are a genuine metadata inconsistency and HOLD.
    unique={}
    for row in possible:
        identifier=row["try_dataset_id"]
        if identifier in unique:
            if unique[identifier]!=row:
                raise ValueError("TRY directory contains conflicting dataset ID rows")
            continue
        unique[identifier]=row
    return sorted(unique.values(),key=lambda r:r["try_dataset_id"])

def extract_source_ids(parquet, core, traits_yml):
    k=pd.read_csv(core)
    if (len(k),k.family.nunique(),k.trait_name.nunique()) != (254,42,13):
        raise ValueError("wrong K core family/trait graph")
    cfg=yaml.safe_load(Path(traits_yml).read_text())["traits"]["elements"]
    units=[]
    for r in k.itertuples(index=False):
        unit=cfg[r.trait_name].get("units")
        if unit is None or not str(unit).strip():raise ValueError("missing source-native unit")
        units.append((r.family,r.trait_name,str(unit).strip()))
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE cand(family VARCHAR,trait VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO cand VALUES (?,?,?)",units)
    sql=r"""
      SELECT DISTINCT trim(CAST(a.dataset_id AS VARCHAR)) AS dataset_id
      FROM read_parquet(?) a JOIN cand c
       ON trim(CAST(a.family AS VARCHAR))=c.family
      AND trim(CAST(a.trait_name AS VARCHAR))=c.trait
      WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
        AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
        AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
        AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
        AND coalesce(trim(CAST(a.unit AS VARCHAR)),'')=c.unit
        AND try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE)>0
      ORDER BY dataset_id
    """
    try:result=[str(x[0]) for x in con.execute(sql,[str(parquet)]).fetchall()]
    finally:con.close()
    if not result:raise ValueError("no original AusTraits contributing dataset IDs")
    return result

def get_primary_metadata(dataset_id,commit):
    u=("https://raw.githubusercontent.com/traitecoevo/austraits.build/"+
       quote(commit,safe="")+"/data/"+quote(dataset_id,safe="")+"/metadata.yml")
    try:
        q=requests.get(u,timeout=22,headers={"User-Agent":"turnover-public-source-audit/0.1"})
        q.raise_for_status()
        src=yaml.safe_load(q.text)
        if not isinstance(src,dict):raise ValueError("metadata is not dict")
        pri=(src.get("source") or {}).get("primary") or {}
        if not isinstance(pri,dict):pri={}
        return {"austraits_dataset_id":dataset_id,
                "austraits_primary_doi":normalized_doi(pri.get("doi")),
                "austraits_primary_reference":str(pri.get("citation") or pri.get("reference") or "")[:500],
                "source_metadata_status":"READABLE"}
    except Exception:
        return {"austraits_dataset_id":dataset_id,
                "austraits_primary_doi":None,
                "austraits_primary_reference":"",
                "source_metadata_status":"UNKNOWN_METADATA_UNREADABLE"}

def audit(catalog,aus,contract):
    if contract.get("status")!="PRE_PUBLIC_METADATA_CATALOG_AUDIT_PROTOCOL_FIXED":
        raise ValueError("catalogue design missing or changed")
    mintry=contract["minimum_operational_checks"]["try_catalog_min_rows"]
    if len(catalog)<mintry:raise ValueError("partial TRY public directory, refuse snapshot")
    if len({r["try_dataset_id"] for r in catalog})!=len(catalog):
        raise ValueError("duplicate TRY dataset IDs")
    if not aus:raise ValueError("AusTraits source list empty")
    # Use names only to nominate possible overlaps; NEVER make a claim
    # that a nonmatching pair of names implies independent observations.
    hits=[]
    for a in aus:
        for t in catalog:
            sim=name_overlap(a["austraits_dataset_id"],t["try_dataset_title"])
            if sim>=.83 and len(key(a["austraits_dataset_id"]) & key(t["try_dataset_title"]))>=2:
                hits.append({
                    "austraits_dataset_id":a["austraits_dataset_id"],
                    "try_public_directory_dataset_id":t["try_dataset_id"],
                    "try_dataset_title":t["try_dataset_title"],
                    "lexical_jaccard":round(sim,4),
                    "classification":"POTENTIAL_NAME_OVERLAP_NOT_RECORD_LINKAGE"})
    by_doi={}
    for a in aus:
        if a["austraits_primary_doi"]:
            by_doi.setdefault(a["austraits_primary_doi"],[]).append(a["austraits_dataset_id"])
    doi_hits=[]
    for t in catalog:
        for doi in filter(None,str(t.get("try_source_link_dois","")).split(";")):
            for ds in by_doi.get(doi,[]):
                doi_hits.append({
                    "shared_primary_publication_doi":doi,
                    "austraits_dataset_id":ds,
                    "try_public_directory_dataset_id":t["try_dataset_id"],
                    "try_dataset_title":t["try_dataset_title"],
                    "classification":"SAME_DOI_PUBLIC_SOURCE_REFERENCE_NOT_MEASUREMENT_MATCH"})
    summary={
      "version":"v0.1","status":STATUS,
      "try_index_advertised_version":"6.0 (public Data Explorer; NOT current main TRY v7 release)",
      "try_public_directory_dataset_rows":len(catalog),
      "austraits_source_candidate_dataset_ids":len(aus),
      "austraits_source_metadata_readable":sum(r["source_metadata_status"]=="READABLE" for r in aus),
      "austraits_primary_doi_covered":sum(bool(r["austraits_primary_doi"]) for r in aus),
      "potential_lexical_name_overlap_pairs":len(hits),
      "try_directory_doi_linked_dataset_rows":sum(bool(t.get("try_source_link_dois")) for t in catalog),
      "direct_public_doi_overlap_pairs":len(doi_hits),
      "external_independent_validation_sources_qualified":0,
      "final_status":"HOLD_TRY_V7_SOURCE_LINEAGE_AND_TRAIT_FAMILY_SUPPORT_UNVERIFIED",
      "hard_boundaries":[
        "Historical TRY directory is not a current TRY7 per-trait family support table",
        "No TRY original observations, measurements, or trait values opened",
        "No inference of independence from unmatched dataset titles or DOIs",
        "Missing AusTraits DOI is unknown provenance, not a distinct measurement",
        "Name similarities are screening leads, not proven shared original observations",
        "New external raw data requires TRY request and use/access authorization",
        "Frozen 10-family x 20-species gate and five named trait predictions unchanged"]
    }
    return summary,hits,doi_hits

def write_csv(path,rows,fields):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,"w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    for v in ("design","try-url","austraits-parquet","core","traits-yml","out-dir"):
        p.add_argument("--"+v,required=True)
    a=p.parse_args()
    design=json.load(open(a.design))
    if design.get("status")!="PRE_PUBLIC_METADATA_CATALOG_AUDIT_PROTOCOL_FIXED":
        raise ValueError("unfrozen design")
    u=str(a.__dict__["try_url"])
    if u!=design["sources"]["try_directory"]:
        raise ValueError("TRY directory endpoint changed")
    payload=requests.get(u,timeout=40,headers={"User-Agent":"turnover-metadata-preflight/0.1"})
    payload.raise_for_status()
    catalog=parse_try_catalog(payload.text)
    src=extract_source_ids(a.__dict__["austraits_parquet"],a.core,a.__dict__["traits_yml"])
    commit=design["sources"]["austraits_source_commit"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        aus=list(pool.map(lambda ds:get_primary_metadata(ds,commit),src))
    summary,hits,doi_hits=audit(catalog,aus,design)
    summary["try_directory_html_sha256"]=hashlib.sha256(payload.content).hexdigest()
    out=Path(a.__dict__["out_dir"])
    out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"try_public_directory.csv",catalog,
        ["try_dataset_id","try_dataset_title","public_explorer_access_status","try_source_link_dois"])
    write_csv(out/"austraits_fixed_core_source_metadata.csv",aus,
        ["austraits_dataset_id","austraits_primary_doi","austraits_primary_reference","source_metadata_status"])
    write_csv(out/"lexical_overlap_candidates.csv",hits,
        ["austraits_dataset_id","try_public_directory_dataset_id","try_dataset_title","lexical_jaccard","classification"])
    write_csv(out/"doi_overlap_candidates.csv",doi_hits,
        ["shared_primary_publication_doi","austraits_dataset_id","try_public_directory_dataset_id","try_dataset_title","classification"])
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":main()
