#!/usr/bin/env python3
"""Original PANGAEA Jena TBE 2012 source-gate: NO biomass effects, nonraw diagnostics.

Source public CC BY 3.0; harvest columns are sown species dry biomass
(g/m²). This audit does not release source rows or fit any ecological model.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,urllib.error,urllib.request
from collections import Counter,defaultdict
from pathlib import Path

URL="https://doi.pangaea.de/10.1594/PANGAEA.876725?format=textfile"
DOI="10.1594/PANGAEA.876725"
BYTES_LIMIT=900_000
MISSING={"-9999","-9999.0","na","nan","n/a","null"}

def invalid(reason):
    raise ValueError(reason)

def public_bytes():
    req=urllib.request.Request(URL,headers={"User-Agent":"turnover-jena-TBE-original-source-audit/0.1",
       "Accept":"text/plain,text/tab-separated-values"})
    with urllib.request.urlopen(req,timeout=55) as r:
        if r.status!=200:invalid("SOURCE_HTTP_NOT_200")
        raw=r.read(BYTES_LIMIT+1)
        if len(raw)>BYTES_LIMIT:invalid("SOURCE_FIXED_BYTE_LIMIT")
        final=r.geturl().lower()
        if any(x in final for x in ("login","captcha","auth.")):
            invalid("OFFICIAL_DATA_ACCESS_AUTH_HOLD")
        return raw

def parse_source(b, synthetic_fixture=False):
    try: s=b.decode("utf-8-sig")
    except UnicodeDecodeError:s=b.decode("cp1252")
    lines=s.splitlines()
    # PANGAEA text files are written with /* DATA DESCRIPTION: ... */ metadata.
    end=next((i for i,x in enumerate(lines) if x.strip()=="*/"),None)
    if end is None:invalid("OFFICIAL_PANGAEA_METADATA_DELIMITER_MISSING")
    source_meta="\n".join(lines[:end+1])
    if "876725" not in source_meta:invalid("OFFICIAL_SOURCE_DOI_IDENTITY_MISSING")
    body="\n".join(lines[end+1:]).strip()+"\n"
    rd=csv.DictReader(io.StringIO(body,newline=""),delimiter="\t")
    h=rd.fieldnames or []
    if len(h)<(8 if synthetic_fixture else 20) or len(h)!=len(set(h)):invalid("ORIGINAL_HEADER_NOT_SOWN_SPECIES_GRID")
    rows=list(rd)
    if any(None in row for row in rows):invalid("PANGAEA_SOURCE_TABULAR_FIELD_COUNT_MISMATCH")
    return h,rows

def find_col(headers,needles,exclude=()):
    possible=[h for h in headers if any(n in h.lower() for n in needles) and
              not any(n in h.lower() for n in exclude)]
    if len(possible)!=1:invalid("AMBIGUOUS_OFFICIAL_COLUMN_ROLE_"+"/".join(needles))
    return possible[0]

def parsed_number(s,integer=False):
    s=(s or "").strip()
    if not s or s.lower() in MISSING:return None
    try:
        x=float(s)
        if not math.isfinite(x):return None
        if integer and int(x)!=x:return None
        return int(x) if integer else x
    except ValueError:return None

def inspect(h,rows):
    roles={
      "plot":find_col(h,("plot",)),
      "month":find_col(h,("month",)),
      "FD_assigned":find_col(h,("wfdc","functional diversity")),
      "richness_sown":find_col(h,("spec no","number of species")),
      "pool":find_col(h,("species pool",)),
      "block":find_col(h,("block",)),
    }
    if len(set(roles.values()))!=6:invalid("OFFICIAL_METADATA_ROLES_COLLIDE")
    candidates=[x for x in h if "biom" in x.lower() and "dw" in x.lower()]
    nontarget=["weed","unid","dead"]
    species=[x for x in candidates if not any(t in x.lower() for t in nontarget)]
    if len(species)<15:invalid("SOWN_SPECIES_BIOMASS_HEADERS_LT_15")
    if len(rows)<200:invalid("PANGAEA_HARVEST_ROW_COUNT_LT_200")
    byplot=defaultdict(list)
    keys=set()
    months=Counter();pools=Counter();blocks=Counter()
    metadata_missing=0;invalid_sown_counts=0;missing_species_harvest=0
    for row in rows:
        plot=(row.get(roles["plot"]) or "").strip()
        month=(row.get(roles["month"]) or "").strip()
        pool=(row.get(roles["pool"]) or "").strip()
        block=(row.get(roles["block"]) or "").strip()
        fd=parsed_number(row.get(roles["FD_assigned"]),True)
        richness=parsed_number(row.get(roles["richness_sown"]),True)
        if not all((plot,month,pool,block)) or fd is None or richness is None:
            metadata_missing+=1;continue
        if (plot,month) in keys:invalid("DUPLICATE_ORIGINAL_PLOT_MONTH")
        keys.add((plot,month))
        months[month]+=1
        pools[pool]+=1;blocks[block]+=1
        # Blank species biomass cells refer to species not sown (PANGAEA metadata).
        original_sown=[v for v in species if (row.get(v) or "").strip()!=""]
        if len(original_sown)!=richness:invalid_sown_counts+=1
        bad=0
        for col in original_sown:
            x=parsed_number(row.get(col))
            if x is None or x<0:bad+=1
        if bad:missing_species_harvest+=1
        byplot[plot].append({
          "month":month,"pool":pool,"block":block,"fd":fd,
          "richness":richness,"sown_cells":frozenset(original_sown),
          "n_missing_numeric":bad,"n_sown_cells":len(original_sown)})
    expectedmonths=set(months)
    qualified=[]
    inconsistent=0;incomplete=0
    for plot,rs in byplot.items():
        if len(rs)!=2 or len({r["month"] for r in rs})!=2 or set(r["month"] for r in rs)!=expectedmonths:
            incomplete+=1;continue
        group={(r["pool"],r["block"],r["fd"],r["richness"],r["sown_cells"]) for r in rs}
        if len(group)!=1:
            inconsistent+=1;continue
        r=rs[0]
        if r["richness"]<2 or any(x["n_missing_numeric"] for x in rs) or any(x["n_sown_cells"]!=x["richness"] for x in rs):
            continue
        qualified.append(r)
    groupmat=defaultdict(lambda:Counter())
    for r in qualified:
        groupmat[(r["pool"],r["richness"])][r["fd"]]+=1
    eligible_strata=[]
    for key,c in groupmat.items():
        low=sum(n for fd,n in c.items() if fd<=2)
        high=sum(n for fd,n in c.items() if fd>=3)
        if low>=4 and high>=4:
            eligible_strata.append({"richness":key[1],"low":low,"high":high,"n":low+high})
    qualify_pool_counts=Counter(r["pool"] for r in qualified)
    eligible_by_pool=defaultdict(set)
    for key,c in groupmat.items():
        if sum(n for fd,n in c.items() if fd<=2)>=4 and sum(n for fd,n in c.items() if fd>=3)>=4:
            eligible_by_pool[key[0]].add(key[1])
    n_strata=len(eligible_strata)
    n_plots=sum(x["n"] for x in eligible_strata)
    # Source-level pool names (S/P/SP) are categorical; do not export original site/plot/species identities.
    admitted=(len(byplot)>=120 and len(expectedmonths)==2
        and len(pools)==3 and len(blocks)==3 and len(qualified)>=80
        and len(qualify_pool_counts)==3 and min(qualify_pool_counts.values())>=20
        and n_strata>=4 and len(eligible_by_pool)>=2 and n_plots>=40
        and invalid_sown_counts==0)
    return {
      "status":"PREOUTCOME_TBE_TREATMENT_DESIGN_ELIGIBLE" if admitted else "ORIGINAL_TBE_SOURCE_OR_DESIGN_HOLD",
      "source_header_fields":len(h),"source_species_mass_columns":len(species),
      "source_harvest_rows":len(rows),"source_unique_plot_IDs":len(byplot),
      "source_months_distinct":len(months),"source_month_row_counts_sorted":sorted(months.values()),
      "source_species_pools_distinct":len(pools),"source_field_blocks_distinct":len(blocks),
      "source_plots_with_both_months_and_matching_treatment":sum(len(v)==2 for v in byplot.values())-inconsistent,
      "source_unique_eligible_multispecies_plots":len(qualified),
      "eligible_pools_plot_counts_anonymized":sorted(qualify_pool_counts.values()),
      "source_inconsistent_original_metadata_or_sown_roster_plot_count":inconsistent,
      "source_plots_missing_one_month":incomplete,
      "source_rows_invalid_sown_roster":invalid_sown_counts,
      "source_rows_nonpositive_or_missing_required_species_mass":missing_species_harvest,
      "source_rows_missing_source_design_fields":metadata_missing,
      "richness_by_FD_original_source_eligible_strata":sorted([{"richness":k[1],"fd_level_counts_sorted":sorted(c.values())} for k,c in groupmat.items()],key=lambda x:(x["richness"],x["fd_level_counts_sorted"])),
      "source_matched_high_vs_low_FD_strata_n":n_strata,
      "source_matched_high_vs_low_FD_plot_count":n_plots,
      "source_matched_high_vs_low_FD_strata_sizes":sorted([x["n"] for x in eligible_strata]),
      "source_matched_strata_distinct_pools":len(eligible_by_pool),
      "original_biomass_values_exported":0,
      "biological_effect_fitted":False,
      "source_gate_pass":admitted}

def test():
    toy=("/* DATA DESCRIPTION:\nCitation: 10.1594/PANGAEA.876725\n*/\n"
         "Plot\tMonth\tFunctional diversity (wFDc)\tNumber of species (Spec No)\tSpecies Pool\tBlock\tA. odoratum biom dw\tB. crop biom dw\n"
         "T1\t5\t3\t2\tS\tA\t12\t0\n")
    h,d=parse_source(toy.encode(),synthetic_fixture=True)
    assert len(d)==1 and len(h)==8
    assert parsed_number("-9999") is None
    assert parsed_number("1",True)==1
    assert parsed_number("2.3",True) is None
    assert len({k for k in ("S","P","SP")})==3
    print(json.dumps({"status":"JENA_TBE_ORIGINAL_SOURCE_FIXTURE_PASS","checks":5}))

def main(path):
    out={
      "dataset_doi":DOI,
      "official_public_download":URL,
      "status":"ORIGINAL_TBE_SOURCE_ACCESS_HOLD",
      "no_original_plot_or_species_ID_values_exported":True,
      "no_original_biomass_values_exported":True,
      "no_ecological_effects_estimated":True,
      "freeze_file":"docs/JENA_TBE_2012_ASSIGNED_FD_BIOMASS_SOURCE_GATE_20261121.md"
    }
    try:
        b=public_bytes()
        out["original_source_sha256"]=hashlib.sha256(b).hexdigest()
        out["original_source_bytes"]=len(b)
        h,rows=parse_source(b)
        out.update(inspect(h,rows))
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,KeyError,UnicodeError) as e:
        out["status"]="ORIGINAL_TBE_SOURCE_ACCESS_OR_STRUCTURE_HOLD"
        out["failure_class"]=type(e).__name__
        if isinstance(e,urllib.error.HTTPError):out["http_status"]=e.code
        elif isinstance(e,ValueError):out["source_gate_failure"]=str(e)[:120]
    assert out["no_ecological_effects_estimated"] and out["no_original_biomass_values_exported"]
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("JENA_TBE_2012_SOURCE_ONLY",json.dumps({
      "status":out["status"],"plots":out.get("source_unique_plot_IDs"),
      "eligible":out.get("source_unique_eligible_multispecies_plots"),
      "matched_strata":out.get("source_matched_high_vs_low_FD_strata_n"),
      "matched_plots":out.get("source_matched_high_vs_low_FD_plot_count"),
      "http":out.get("http_status"),"no_biological_effects":True}))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.self_test:test()
    elif a.out:main(a.out)
    else:p.error("Select --self-test or --out")
