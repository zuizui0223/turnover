#!/usr/bin/env python3
"""Read official Chen 2025 Figshare original CSVs for schema/cohort eligibility only.

Original *public column labels* and aggregate missingness are reported for audit.
No original study, plot, species identity or biological response values are exported.
No regression/association/hypothesis effect estimated.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,urllib.request
from collections import Counter
from pathlib import Path

ROOT="https://api.figshare.com/v2/articles/27316062"
FILES={
 "all_full":("Data_Mix_All_241019.csv",50036697,"6f4099e82c547c421f832aef057e52fa"),
 "all_primary":("Data_Mix_All_no outliers_241019.csv",50036694,"8803b0479267bf9650de15301bf37e96"),
 "field_primary":("Data_Mix_Field_no outliers_241019.csv",50036709,"39efaeb218704628b1c5da1b21735651"),
 "leafN_primary":("Data_Mix_LN_no outliers_241019.csv",50036712,"cbf1955398018ba892e52abe2ca8c315"),
 "SLA_primary":("Data_Mix_SLA_no outliers_241019.csv",50036718,"df6b948bd892c3a04595e0f8f83c0f8b")
}
SOURCE_LIMIT=1_800_000
EXPECTED={"all_full":4680,"all_primary":4598,"field_primary":3091,"leafN_primary":2273,"SLA_primary":2784}
BASIC_TERMS=("study","experiment","reference","paper","rich","ce","se","ne","nfix","age","ecosystem","fd","sla","ln","nitrogen","pd","biomass","cv")
MISSING={"","na","nan","none","null","-9999","n/a","."}

def request(url,limit):
    req=urllib.request.Request(url,headers={"User-Agent":"turnover-Chen452-original-source-cohort-gate/0.2",
                                             "Accept":"application/json,application/octet-stream"})
    with urllib.request.urlopen(req,timeout=40) as r:
        if r.status!=200:raise RuntimeError("OFFICIAL_FILE_ACCESS_HOLD")
        b=r.read(limit+1)
        if len(b)>limit:raise RuntimeError("ORIGINAL_FILE_SIZE_HOLD")
        return b

def clean(x):
    return re.sub(r"[^a-z0-9]+","_",str(x).lower()).strip("_")

def missing(x):
    return x is None or str(x).strip().lower() in MISSING

def number(x):
    if missing(x):return None
    try:
        n=float(str(x).strip())
        return n if math.isfinite(n) else None
    except ValueError:return None

def csv_bytes(b):
    s=b.decode("utf-8-sig")
    rd=csv.DictReader(io.StringIO(s,newline=""))
    if not rd.fieldnames:raise RuntimeError("SOURCE_CSV_MISSING_HEADER")
    cols=rd.fieldnames
    if len(set(cols))!=len(cols):raise RuntimeError("SOURCE_CSV_DUPLICATE_COLUMN")
    rows=[]
    for item in rd:
        if None in item:raise RuntimeError("CSV_SOURCE_FIELD_COUNT_MISMATCH")
        rows.append(item)
    return cols,rows

def column_audit(cols,rows):
    # Column labels are published schema, not biological values or private IDs.
    normalized={c:clean(c) for c in cols}
    stats={}
    for col in cols:
        if not any(t in normalized[col] for t in BASIC_TERMS):
            continue
        avail=[r.get(col) for r in rows if not missing(r.get(col))]
        numeric=sum(number(v) is not None for v in avail)
        unique_values=len({v for v in avail})
        stats[col]={"nonmissing_rows":len(avail),
                    "numeric_rows":numeric,
                    "distinct_values_count":unique_values}
    # These are structural indicators only, not differences/correlations.
    return {"original_header_labels":cols,"feature_structure":stats,
            "n_qualified_original_rows":len(rows)}

def run(path):
    article=json.loads(request(ROOT,1_500_000))
    assert re.search(r"10[.]6084/m9[.]figshare[.]27316062([.]v[0-9]+)?$", str(article.get("doi","")), re.I), "OFFICIAL_FIGSHARE_DOI_IDENTITY_HOLD"
    fm={f["id"]:f for f in article.get("files",[])}
    out={"status":"STRUCTURAL_SOURCE_ONLY_NO_EFFECTS",
         "original_article":27316062,
         "doi":"10.6084/m9.figshare.27316062",
         "original_figure_data_CC_BY_4_0":True,
         "no_original_experiment_or_species_ID_values_exported":True,
         "no_original_response_values_exported":True,
         "no_CE_SE_FD_model_or_hypothesis_fitted":True,
         "retrospective_original_study_outcomes_published":True,
         "datasets":{}}
    for alias,(name,source_id,expected_md5) in FILES.items():
        sf=fm[source_id]
        if sf["name"]!=name:raise RuntimeError("PUBLIC_ORIGINAL_FILE_NAME_DRIFT_"+alias)
        data=request(f"https://api.figshare.com/v2/file/download/{source_id}",SOURCE_LIMIT)
        if len(data)!=sf["size"] or hashlib.md5(data).hexdigest()!=expected_md5:
            raise RuntimeError("ORIGINAL_DATA_MD5_OR_SIZE_DRIFT_"+alias)
        cols,rows=csv_bytes(data)
        if len(rows)!=EXPECTED[alias]:
            raise RuntimeError("ORIGINAL_PUBLISHED_COHORT_ROWCOUNT_DRIFT_"+alias)
        out["datasets"][alias]={
            "source_file_id":source_id,"source_sha256":hashlib.sha256(data).hexdigest(),
            "original_data_count":len(rows),"source_schema":column_audit(cols,rows)}
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("CHEN452_ORIGINAL_SOURCE_COHORT_STRUCTURE",
       json.dumps({"status":out["status"],
                   "datasets":{k:{"rows":v["original_data_count"],
                                  "public_original_columns":v["source_schema"]["original_header_labels"],
                                  "selected_source_support_counts":v["source_schema"]["feature_structure"]}
                               for k,v in out["datasets"].items()},
                   "new_effects_opened":False},sort_keys=True))

def test():
    c=["Study","CE","SE","FD_N","species_richness"]
    r=[{"Study":"one","CE":"1","SE":"0","FD_N":"0.2","species_richness":"4"},
       {"Study":"two","CE":"","SE":"0","FD_N":"NA","species_richness":"8"}]
    x=column_audit(c,r)
    assert x["feature_structure"]["CE"]["numeric_rows"]==1
    assert x["feature_structure"]["SE"]["nonmissing_rows"]==2
    assert x["feature_structure"]["Study"]["distinct_values_count"]==2
    assert len(FILES)==5 and EXPECTED["all_primary"]==4598
    print('{"status":"CHEN452_ORIGINAL_SCHEMA_FIXTURE_PASS","checks":5}')

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.self_test:test()
    elif args.out:run(args.out)
    else:p.error("Choose --self-test or --out")
