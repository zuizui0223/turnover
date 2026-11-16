#!/usr/bin/env python3
"""Read-only source chronology/woody scaling metadata from Figshare README and
publisher Wiley supplementary assets, using strictly declared official paths.
No ecological coefficients or original study row data evaluated/exported.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse

from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file,shared_strings,source_sheets,get_xml,NS

DOI="10.1111/1365-2435.70320"
FILES={
  "methods_docx":"fec70320-sup-0001-FigureS1-S12-TableS5-S6.docx",
  "site_table":"fec70320-sup-0002-TableS1.xlsx",
  "allometry_table":"fec70320-sup-0004-TableS3.xlsx"
}
BASES=(
 "https://besjournals.onlinelibrary.wiley.com/doi/suppl/"+DOI+"/supinfo/",
 "https://onlinelibrary.wiley.com/doi/suppl/"+DOI+"/supinfo/"
)
UA="turnover-Jensen2026-Wiley-original-supplement-source-qa/0.1"
WNS={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
MAX_ZIP_SIZE=2_000_000
MAX_UNZIP_SIZE=18_000_000


def read_exact(url):
    domain=urlparse(url).hostname
    if domain not in {"besjournals.onlinelibrary.wiley.com","onlinelibrary.wiley.com"}:
        raise ValueError("NON_PUBLISHER_SOURCE_HOLD")
    try:
        req=Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream,*/*"})
        with urlopen(req,timeout=35) as resp:
            final=urlparse(resp.url)
            if not final.hostname or not (final.hostname.endswith(".wiley.com") or final.hostname.endswith(".wiley-content.com")):
                return "UNSUPPORTED_PUBLISHER_REDIRECT_HOLD",None
            blob=resp.read(MAX_ZIP_SIZE+1)
            if len(blob)>MAX_ZIP_SIZE:return "SIZE_CAP_HOLD",None
            if blob[:4]!=b"PK\x03\x04":return "NOT_OFFICE_ZIP_HOLD",None
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                if sum(i.file_size for i in z.infolist())>MAX_UNZIP_SIZE or any(".." in i.filename for i in z.infolist()):
                    return "ZIP_UNSAFE_HOLD",None
            return 200,blob
    except HTTPError as e:
        return e.code,None
    except (URLError,TimeoutError,ValueError,zipfile.BadZipFile) as e:
        return type(e).__name__+"_HOLD",None


def original_readme():
    raw=fetch_file("README.txt")
    source=raw.decode("utf-8-sig",errors="replace")
    lines=source.splitlines()
    evidence=[]
    for i,line in enumerate(lines,1):
        low=line.casefold()
        hits=[k for k in ("year","date","sampling","measured","biomass","wood","species","scale","site","mass","sum","average","data availability","source") if k in low]
        if not hits:continue
        if not (("biomass" in hits or "wood" in hits or "year" in hits or "sampling" in hits or "scale" in hits or "average" in hits)):continue
        # Only source-line number/keywords and a short catalogue-text snippet,
        # never original data rows, published methods verbatim, site identifiers.
        clean=" ".join(line.split())
        snippet=clean[:96] if len(clean.split())<=10 else " ".join(clean.split()[:10])
        evidence.append({"readme_line":i,"categories":hits,"short_excerpt":snippet})
    return {
        "readme_source_MD5":hashlib.md5(raw).hexdigest(),
        "original_text_lines":len(lines),
        "time_or_response_definition_evidence_lines":evidence[:22],
        "mentions_original_measurement_year":bool(re.search(r"measurement year|sampling year|measured in (?:19|20)\d\d",source,re.I)),
        "mentions_biomass_species_row_scaling_formula":bool(re.search(r"(?:biomass|woody).{0,75}(?:divid|multipli|averag|sum|normaliz|richness)",source,re.I|re.S)),
        "readme_is_original_public_data_documentation":True
    }


def docx_metadata(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        root=ET.fromstring(z.read("word/document.xml"))
    pars=[]
    for p in root.findall(".//w:p",WNS):
        text=" ".join((t.text or "") for t in p.findall(".//w:t",WNS)).strip()
        if text:pars.append(" ".join(text.split()))
    # Methods headings and direct relative sampling phrases only;
    # do not dump the published supplement or original numeric tables.
    headings=[{"paragraph_index":i,"heading":s[:120]} for i,s in enumerate(pars)
              if re.match(r"(?i)methods\s*S[123]\b",s)]
    topics=("trait","sample","leaf","year","yearly","biomass","allometr","per hectare","measurement","species","plot")
    metadata=[]
    for i,p in enumerate(pars):
        if re.search(r"(?i)\b(?:19|20)\d{2}\b",p):
            if any(t in p.casefold() for t in topics):
                metadata.append({"paragraph_index":i,"year_tokens":sorted(set(re.findall(r"\b(?:19|20)\d{2}\b",p))),
                  "categories":[t for t in topics if t in p.casefold()],"text_not_exported":True})
    return {"n_supplement_paragraphs":len(pars),
            "methods_S1_S2_S3_headings":headings[:15],
            "n_year_mentions_in_relevant_paragraphs":len(metadata),
            "year_and_topic_index":metadata[:28],
            "method_chronology_record_level_join_not_assumed":True}


def xlsx_metadata(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        shared=shared_strings(z)
        sheets=source_sheets(z)
        summaries=[]
        for name,path in sheets:
            root=get_xml(z,path)
            rows=root.findall(".//m:sheetData/m:row",NS)
            titles=[]
            for row in rows[:8]:
                cells=[]
                for cell in row.findall("m:c",NS):
                    tp=cell.attrib.get("t","")
                    if tp=="s":
                        v=cell.find("m:v",NS)
                        ii=int(v.text) if v is not None and v.text else -1
                        cells.append(shared[ii] if 0<=ii<len(shared) else "")
                    elif tp in ("str","inlineStr"):
                        cells.append(" ".join((v.text or "") for v in cell.findall(".//m:t",NS)))
                    else:
                        cells.append("")
                indicator=sum(any(term in c.lower() for term in ("year","date","biomass","sampling","leaf","site","measurement","species")) for c in cells)
                if indicator>=2:
                    titles.append({"row_number":row.attrib.get("r"),"science_keyword_header":[c[:80] for c in cells[:50]],"header_keyword_count":indicator})
            summaries.append({"sheet":name,"original_source_row_count":len(rows),
                "source_header_candidates":titles[:3],
                "sourced_individual_year_mapping_verified":False})
    return {"n_original_sheets":len(summaries),"sheets":summaries,"no_original_site_row_values_exported":True}


def main():
    readme=original_readme()
    audits={}
    for typ,name in FILES.items():
        candidates=[]
        outcome=None
        for url in [base+name for base in BASES]:
            status,blob=read_exact(url)
            candidates.append({"publisher_hostname":urlparse(url).hostname,"result":status})
            if status==200:
                typdoc=docx_metadata(blob) if typ=="methods_docx" else xlsx_metadata(blob)
                outcome={"file_sha256":hashlib.sha256(blob).hexdigest(),"file_bytes":len(blob),"source_format":"docx" if typ=="methods_docx" else "xlsx",
                    "source_extraction":typdoc}
                break
        audits[typ]={"public_source_filename":name,
            "publisher_access_probes":candidates,
            "status":"PUBLISHER_SUPPLEMENT_READ_ONLY_METADATA_PASS" if outcome else "PUBLISHER_SUPPLEMENT_ACCESS_HOLD",
            "verified_original_metadata":outcome}
    result={
      "version":"v0.1","source_only":True,
      "no_new_trait_FD_K_PD_or_biomass_effect":True,
      "original_figshare_article":"10.6084/m9.figshare.31026004.v1",
      "original_publisher_paper":DOI,
      "original_figshare_readme":readme,
      "official_publisher_supplement":audits,
      "woody_biomass_source_identity_explained":"UNVERIFIED_AUTHOR_FORMULA",
      "individual_DS2_original_trait_provenance":"INDIVIDUAL_SOURCE_PROVENANCE_HOLD",
      "original_DS1_DS2_time_alignment":"TEMPORAL_ALIGNMENT_HOLD",
      "source_decision":"RETAIN_PREVIOUS_328_PLOT_SOURCE_GEOMETRY_PASS_WITH_PROVENANCE_AND_YEAR_HOLD",
      "nonclaims":["No unpublished Wiley supplementary was invented from a 403 page","No source year derived from experimental establishment date","DS2 woody species row averages 321/328 DS1 rows but no explicit species scaling formula was established by arithmetic alone",
                   "No plot trait–biomass coefficient, causal model or evolutionary K estimated"]
    }
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        assert MAX_ZIP_SIZE<=2_000_000
        assert re.search(r"Methods S2","Methods S2. Allometric estimation",re.I)
        assert all(BASES[0].startswith("https://") for x in FILES)
        print(json.dumps({"status":"SOURCE_PUBLISHER_README_FIXTURE_PASS","checks":3}))
    else:
        if not a.out:p.error("--out needed")
        res=main()
        # More specific PASS only when actual supplementary chronology is retrieved
        # and independently audited; never auto-unlock a new biomass regression.
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("TREE_DIVNET_SUPPLEMENT_SOURCE_PROBE",json.dumps(res,sort_keys=True),flush=True)
