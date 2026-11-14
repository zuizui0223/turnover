#!/usr/bin/env python3
"""Read original Jena PANGAEA dataset *schema and coverage only*.

Never export species-level biomass, response moments, correlations, FD, or models.
The outcome remains unopened for scientific inference until pre-registered Tier 1.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, re
from pathlib import Path
from collections import Counter, defaultdict

EXPECTED_SOURCE = "10.1594/PANGAEA.846317"

def parse_table(raw):
    text = raw.decode("utf-8-sig")
    if "<!doctype" in text[:1000].lower() or "<html" in text[:1000].lower():
        raise ValueError("HTML_LANDING_PAGE_NOT_TABULAR_DATA")
    lines = text.splitlines()
    if not lines:
        raise ValueError("EMPTY_SOURCE_FILE")
    close = [i for i,l in enumerate(lines) if l.strip() == "*/"]
    if close:
        idx=close[0]+1
    else:
        idx=next((i for i,line in enumerate(lines) if
                  "Experimental plot" in line and "\t" in line),None)
        if idx is None: raise ValueError("PANGAEA_TABLE_HEADER_NOT_IDENTIFIED")
    while idx<len(lines) and not lines[idx].strip(): idx+=1
    if idx>=len(lines):raise ValueError("NO_DATA_AFTER_METADATA")
    reader=csv.DictReader(io.StringIO("\n".join(lines[idx:])),delimiter="\t")
    if not reader.fieldnames or len(reader.fieldnames)<20:
        raise ValueError("TOO_FEW_SOURCE_COLUMNS_FOR_JENA_MAIN_DATA")
    if len(reader.fieldnames)!=len(set(reader.fieldnames)):
        raise ValueError("DUPLICATED_SOURCE_COLUMN_LABELS")
    rows=list(reader)
    if any(None in row for row in rows):
        raise ValueError("JENA_ROW_WIDTH_CONFLICT")
    return reader.fieldnames, rows,idx

def source_probe(path):
    path=Path(path)
    blob=path.read_bytes()
    if len(blob)<5000:raise ValueError("JENA_RAW_SOURCE_TOO_SMALL")
    sha=hashlib.sha256(blob).hexdigest()
    columns, rows, start=parse_table(blob)
    plot_col=next((s for s in columns if "experimental plot" in s.casefold()),None)
    response_col=next((s for s in columns if
                       "sown plant" in s.casefold() and "biom" in s.casefold()),None)
    date_candidates=[s for s in columns if "date/time" in s.casefold()]
    species_biom=[s for s in columns if "biom" in s.casefold()
                  and s!=response_col
                  and not any(x in s.casefold() for x in
                              ("weed","dead plant","unid","unidentified"))]
    if not plot_col or not response_col or not date_candidates:
        raise ValueError("ORIGINAL_PLOT_BIOMASS_OR_CAMPAIGN_FIELDS_NOT_IDENTIFIED")
    counts=Counter()
    plot_ids=set()
    valid_plots=set()
    months=Counter()
    plot_rows=defaultdict(int)
    for row in rows:
        pid=str(row.get(plot_col) or "").strip()
        if not pid:counts["plot_id_blank"]+=1;continue
        plot_ids.add(pid)
        plot_rows[pid]+=1
        for dc in date_candidates[:2]:
            date=str(row.get(dc) or "")
            m=re.search(r"2003[-/](0[1-9]|1[012])",date)
            if m:
                months[m.group(1)]+=1
                break
        val=str(row.get(response_col) or "").strip()
        if not val:
            counts["community_biomass_blank"]+=1
            continue
        try:
            f=float(val)
        except ValueError:
            counts["community_biomass_nonnumeric"]+=1;continue
        if f==-9999:
            counts["community_biomass_failure_sentinel"]+=1
        elif f<0:
            counts["community_biomass_other_negative"]+=1
        else:
            counts["community_biomass_finite_nonnegative"]+=1
            valid_plots.add(pid)
    for col in species_biom:
        values=[str(x.get(col) or "").strip() for x in rows]
        counts["species_specific_biomass_cells_nonempty"]+=sum(bool(x) for x in values)
        counts["species_specific_failure_sentinel"]+=sum(x=="-9999" for x in values)
    report={
      "source":"PANGAEA", "doi":EXPECTED_SOURCE,
      "license_source":"Read the original PANGAEA DOI for rights and citation",
      "file_name":path.name,"raw_file_sha256":sha,
      "raw_file_bytes":len(blob),
      "raw_header_start_one_based":start+1,
      "rows":len(rows),"columns":len(columns),
      "columns_names":columns,
      "plot_id_column":plot_col,
      "measured_dry_biomass_column":response_col,
      "date_columns":date_candidates,
      "candidate_species_biomass_columns":len(species_biom),
      "number_unique_plots":len(plot_ids),
      "plots_with_valid_measured_biomass":len(valid_plots),
      "plots_with_multiple_rows":sum(n>1 for n in plot_rows.values()),
      "source_row_counts_by_2003_month":dict(months),
      "raw_value_integrity_counts":dict(counts),
      "scope":"SOURCE-ONLY no FD, PD, biomass association, prediction, p-values or ecological inference",
      "interpretation":"Source presence and schema only; scheduled species and trait provenance remain unverified",
    }
    enough=(len(plot_ids)>=70 and len(valid_plots)>=70
            and counts["community_biomass_finite_nonnegative"]>=70
            and len(species_biom)>=50 and not counts["community_biomass_other_negative"]
            and months.get("05",0)>0 and months.get("08",0)>0)
    report["status"]="TIER0_JENA_SOURCE_DATA_SCHEMA_PASS" if enough else "TIER0_JENA_SOURCE_HOLD"
    report["tier1_not_opened"]=True
    return report

def test():
    fields=["Experimental plot","Date/time start","Sown plant biom [g/m**2]"]+[f"Species {i} biom" for i in range(60)]
    rows=[]
    for i in range(82):
        for month in ("05","08"):
            rows.append([f"B{i:03}",f"2003-{month}-27","21"]+["1"]*60)
    tmp="/* DATA DESCRIPTION:\nCitation:\t"+EXPECTED_SOURCE+"\n*/\n"
    tmp+="\t".join(fields)+"\n"+"\n".join("\t".join(r) for r in rows)
    names,records,_=parse_table(tmp.encode())
    assert len(names)==63 and len(records)==164
    assert len({x["Experimental plot"] for x in records})==82
    assert all(float(x["Sown plant biom [g/m**2]"])>=0 for x in records)
    return {"status":"JENA_SCHEMA_FIXTURE_PASS","checks":3}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source")
    p.add_argument("--out")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        print(json.dumps(test()))
    else:
        if not a.source or not a.out:p.error("--source and --out required")
        report=source_probe(a.source)
        out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps({k:v for k,v in report.items() if k!="columns_names"},ensure_ascii=False))
        if report["status"]!="TIER0_JENA_SOURCE_DATA_SCHEMA_PASS":raise SystemExit(2)
