#!/usr/bin/env python3
"""Official original DivResource 2013 supplement schema. No biological response fitted."""
import argparse, collections, hashlib, io, json, re, urllib.request, urllib.error, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BASE="https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371%2Fjournal.pone.0158110."
OUT=Path("results/divresource_2013_source_schema_v0_1.json")

def get(suffix):
    req=urllib.request.Request(BASE+suffix,headers={"User-Agent":"turnover-divresource-original-source/0.1"})
    with urllib.request.urlopen(req,timeout=25) as res:
        data=res.read(4_000_001)
    if len(data)>4_000_000:raise ValueError("file too large")
    if not zipfile.is_zipfile(io.BytesIO(data)):raise ValueError("official response not a DOCX archive")
    return data

def tables(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        x=ET.fromstring(z.read("word/document.xml"))
    tt=[]
    for table in x.iter(W+"tbl"):
        rr=[]
        for row in table.findall(W+"tr"):
            rr.append([" ".join("".join(t.text or "" for t in p.iter(W+"t")) for p in c.findall(W+"p")).strip()
                       for c in row.findall(W+"tc")])
        tt.append(rr)
    return tt

def schema(data):
    t=tables(data)
    out=[]
    for rows in t:
        if not rows:continue
        widths=collections.Counter(len(row) for row in rows)
        def isnum(v):
            return bool(re.fullmatch(r"[-+]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[Ee][-+]?\d+)?",v.strip()))
        # Actual header text only; for body, counts and string-domain candidates,
        # not individual row values or numeric outcomes.
        width=max(widths)
        domains=[]
        for i in range(width):
            vs=[r[i] for r in rows[1:] if len(r)>i]
            nonnum=sorted({v for v in vs if v and not isnum(v)})
            domains.append({"column":i,"nonempty":sum(bool(v) for v in vs),
                "numeric_strings":sum(isnum(v) for v in vs),
                "distinct_strings":len(set(vs)),
                "non_numeric_labels":nonnum[:16] if len(nonnum)<=16 else None})
        out.append({"rows":len(rows),"column_width_counts":dict(widths),"first_row_header":rows[0],
                    "column_domains":domains})
    return {"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),"tables":out}

def main():
    result={"doi":"10.1371/journal.pone.0158110","source_programme":"DivResource Bad Lauchstadt 2013",
            "source_mode":"official PLOS S5 S6 DOCX only","biological_models_fit":0,"files":{}}
    for label,suffix in [("S5","s008"),("S6","s009")]:
        try:result["files"][label]={"status":"ORIGINAL_DOCX_SCHEMA_PASS",**schema(get(suffix))}
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,KeyError,zipfile.BadZipFile,ET.ParseError) as exc:
            result["files"][label]={"status":"SOURCE_HOLD","exception":type(exc).__name__,"http_status":getattr(exc,"code",None)}
    OUT.parent.mkdir(exist_ok=True,parents=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":main()
