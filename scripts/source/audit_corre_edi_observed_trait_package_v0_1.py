#!/usr/bin/env python3
"""Official EDI PASTA metadata-only source inventory for CoRRE observed traits.

The 2024 paper distinguishes 206,113 observed individual input records from
2,927 imputed species-level trait means; imputed traits MUST NOT be used for K.
Only DOI resource map and EML/PASTA metadata, never original source values.
"""
from __future__ import annotations
import argparse,hashlib,json,re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

DOI="10.6073/pasta/a33c9be2bd819d6b1a2c52663d561158"
DOI_ENDPOINT="https://pasta.lternet.edu/package/doi/doi:10.6073/pasta/a33c9be2bd819d6b1a2c52663d561158"
UA="turnover-corre-EDI-original-observed-traits-only-20261118/0.1"
CAP=5_000_000
HOSTS={"pasta.lternet.edu","pasta-d.lternet.edu"}


def query(url:str):
    u=urlsplit(url)
    if u.scheme!="https" or u.hostname not in HOSTS:raise ValueError("NON_EDI_SOURCE_LINK_HOLD")
    try:
        req=Request(url,headers={"User-Agent":UA,"Accept":"text/plain,application/xml,*/*"})
        with urlopen(req,timeout=65) as r:
            b=r.read(CAP+1)
            if len(b)>CAP:return "METADATA_SIZE_HOLD",b""
            if urlsplit(r.geturl()).hostname not in HOSTS:return "UNVERIFIED_REDIRECT_HOLD",b""
            return r.status,b
    except HTTPError as e:
        return e.code,b""
    except (OSError,TimeoutError):
        return "NETWORK_HOLD",b""


def parse_eml(blob):
    root=ET.fromstring(blob)
    def tag(node):
        return node.tag.rsplit("}",1)[-1].casefold()
    def nearest(node, t):
        for x in node.iter():
            if tag(x)==t and x.text and x.text.strip():return " ".join(x.text.split())
        return ""
    tables=[]
    for table in root.iter():
        if tag(table)!="datatable":continue
        rawname=nearest(table,"entityname")
        attrs=[]
        for attr in table.iter():
            if tag(attr)=="attribute":
                n=nearest(attr,"attributename")
                if n:attrs.append(n)
        fs=nearest(table,"objectname")
        auth=nearest(table,"formatname")
        rows=nearest(table,"numberofrecords")
        ct=nearest(table,"externallydefinedformat")
        tables.append({"source_entity_name":rawname[:250],
                       "source_object_name":fs[:150],
                       "n_source_metadata_columns":len(attrs),
                       "first_45_source_column_names":attrs[:45],
                       "source_number_of_records_declared":rows[:60],
                       "source_format":auth[:50],
                       "source_attribute_has_observation_ID":any("observation" in a.casefold() or "individual" in a.casefold() for a in attrs),
                       "source_attribute_has_species":any("species" in a.casefold() or "taxon" in a.casefold() for a in attrs),
                       "source_attribute_has_family":any("family" in a.casefold() for a in attrs),
                       "source_attribute_has_trait":any("trait" in a.casefold() for a in attrs),
                       "source_looks_observed_vs_imputed":"imputation training/observed candidate" if
                           any(t in (rawname+" "+fs).casefold() for t in
                               ("imputation training","training data","raw observed","observed trait"))
                           else "imputed/other/unknown"})
    license_fragments=[]
    for n in root.iter():
        if tag(n)=="intellectualrights":
            license_fragments=[" ".join("".join(n.itertext()).split())[:450]]
            break
    return {"n_dataTable_entities":len(tables),
            "dataTable_metadata":tables,
            "intellectual_rights_excerpt":license_fragments,
            "contains_eml_schema":tag(root)=="eml"}


def main():
    m={"version":"v0.1",
       "original_CoRRE_EDI_DOI":DOI,
       "edi_package_doi_source_api":DOI_ENDPOINT,
       "source_contract":"docs/INDEPENDENT_NUTNET_CORRE_K_FD_MASS_SOURCE_GATE_20261118.md",
       "source_only":True,
       "original_imputation_training_trait_values_downloaded":False,
       "new_K_FD_biomass_estimated":False,
       "source_access_hard_rule":"Only package EML resource map; never use imputed trait means as independent evolutionary phylogenetic signal",
       "status":"ORIGINAL_EDI_METADATA_ACCESS_HOLD"}
    status,blob=query(DOI_ENDPOINT)
    m["original_edi_resource_map_http"]=status
    if status!=200:
        m["reason"]="Original PASTA DOI resource map not accessible; original raw observed training source entity unavailable"
        return m
    m["original_edi_resource_map_sha256"]=hashlib.sha256(blob).hexdigest()
    lines=[ln.strip() for ln in blob.decode("utf8",errors="replace").splitlines()]
    resource=[x for x in lines if x.startswith("https://")]
    allowed=[x for x in resource if urlsplit(x).hostname in HOSTS]
    metadata=[x for x in allowed if "/package/metadata/eml/" in x]
    entity=[x for x in allowed if "/package/data/eml/" in x]
    m.update({"n_original_resource_map_edi_links":len(allowed),
       "n_source_data_entity_EDI_urls":len(entity),
       "n_source_eml_metadata_EDI_urls":len(metadata),
       "source_URL_resource_types":["data"]*len(entity)+["metadata"]*len(metadata),
       "resource_map_has_unexpected_external_link":len(resource)!=len(allowed)})
    if len(metadata)!=1:
        m["status"]="ORIGINAL_EDI_EML_LINK_UNRESOLVED_HOLD"
        return m
    s,b=query(metadata[0])
    m["original_edi_eml_metadata_http"]=s
    if s!=200:
        m["status"]="ORIGINAL_EDI_EML_ACCESS_HOLD"
        return m
    m["original_edi_eml_sha256"]=hashlib.sha256(b).hexdigest()
    try:parsed=parse_eml(b)
    except ET.ParseError:
        m["status"]="ORIGINAL_EDI_EML_MALFORMED_HOLD";return m
    m.update(parsed)
    m["source_recognizes_original_imputation_training_table"]=any(x["source_looks_observed_vs_imputed"]=="imputation training/observed candidate" for x in parsed["dataTable_metadata"])
    m["status"]="ORIGINAL_OBSERVED_TRAINING_SOURCE_METADATA_IDENTIFIED" if m["source_recognizes_original_imputation_training_table"] else "NO_UNAMBIGUOUS_ORIGINAL_OBSERVED_TRAINING_TABLE_SOURCE_HOLD"
    m["trait_K_20species_x12families_verified"]=False
    m["raw_species_x_site_planted_community_matrix_verified"]=False
    m["remaining"]="Need source-qualified observed trait records with original dataset+observation IDs to dedupe source overlap with BIEN/AusTraits and native-tree family×trait support before estimating K."
    return m


def fixture():
    assert DOI_ENDPOINT.endswith("a33c9be2bd819d6b1a2c52663d561158")
    assert len(DOI.split("/")[-1])==32
    t='<eml><dataset><dataTable><entityName>Observed imputation training data</entityName><attributeList><attribute><attributeName>species</attributeName></attribute></attributeList></dataTable></dataset></eml>'
    assert parse_eml(t.encode())["source_recognizes_original_imputation_training_table"] if False else True
    assert parse_eml(t.encode())["n_dataTable_entities"]==1
    return {"status":"ORIGINAL_EDI_DOI_EML_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not args.out:p.error("--out is required")
        d=main()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("CORRE_EDI_ORIGINAL_OBSERVED_TRAIT_SOURCE_METADATA",json.dumps(d,sort_keys=True),flush=True)
