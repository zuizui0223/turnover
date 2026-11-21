#!/usr/bin/env python3
"""Outcome-blind original Jena TBE plot-prefix balance and JEXIS public crosswalk attempt."""
from __future__ import annotations
import collections,csv,hashlib,io,json,re,urllib.error,urllib.request,zipfile
from pathlib import Path
import audit_jena_tbe_2012_assigned_fd_biomass_v0_1 as a

EXPECTED_SHA="458f61307df217d285c972f894ca5cf23709c3524dc6e13bb4d9dd3c26c2ab56"
JEXIS="https://jexis.uni-jena.de/ddm/Data/DownloadZip/739?format=text%2Ftsv&version=3333&withFilter=False&withUnits=False"
JEXIS_BYTES=500_000
PATTERN=re.compile(r"^B0B([ABC])[0-9]{3}$")

def inspect():
    b=a.public_bytes()
    if hashlib.sha256(b).hexdigest()!=EXPECTED_SHA:
        raise RuntimeError("ORIGINAL_PANGAEA_SHA_CHANGED")
    h,rows=a.parse_source(b)
    roles={"plot":a.find_col(h,("plot",)),
           "rich":a.find_col(h,("spec no","number of species")),
           "fd":a.find_col(h,("wfdc","functional diversity")),
           "pool":a.find_col(h,("species pool",)),
           "block":a.find_col(h,("block",)),
           "month":a.find_col(h,("month",))}
    plotmap={}
    wrong_pattern=0;metadata_changes=0
    for row in rows:
        plot=row[roles["plot"]].strip()
        met=(row[roles["pool"]].strip(),row[roles["rich"]].strip(),
             row[roles["fd"]].strip(),row[roles["block"]].strip())
        if plot in plotmap:
            if plotmap[plot]!=met:metadata_changes+=1
        else:
            plotmap[plot]=met
        if not PATTERN.fullmatch(plot):wrong_pattern+=1
    prefix_counts=collections.Counter()
    block_fields=collections.Counter()
    prefix_pool=collections.defaultdict(set)
    rich_fd=collections.defaultdict(lambda:collections.Counter())
    for plot,(pool,rich,fd,block) in plotmap.items():
        match=PATTERN.fullmatch(plot)
        if not match:continue
        prefix=match.group(1)
        prefix_counts[prefix]+=1
        block_fields[block]+=1
        prefix_pool[prefix].add(pool)
        if int(float(rich))>=2:
            rich_fd[(prefix,pool,int(float(rich)))][int(float(fd))]+=1
    matched=collections.Counter()
    for (prefix,pool,rich),counts in rich_fd.items():
        if sum(v for k,v in counts.items() if k<=2)>0 and sum(v for k,v in counts.items() if k>=3)>0:
            matched[prefix]+=1
    ok=(len(plotmap)==138 and wrong_pattern==0 and metadata_changes==0
        and sorted(prefix_counts.values())==[46,46,46] and len(block_fields)==1
        and len(prefix_pool)==3 and sorted(map(len,prefix_pool.values()))==[3,3,3])
    return {
       "status":"ORIGINAL_PLOT_PREFIX_THREE_BALANCED_CLASSES_PROVISIONAL" if ok else "ORIGINAL_PLOT_CODE_BALANCE_HOLD",
       "source_original_DOI":"10.1594/PANGAEA.876725",
       "original_source_sha256":EXPECTED_SHA,
       "source_rows":len(rows),"source_distinct_plots":len(plotmap),
       "source_rows_plot_ids_not_matching_frozen_prefix_regex":wrong_pattern,
       "source_plots_with_month_metadata_disagreement":metadata_changes,
       "prefix_strata_count":len(prefix_counts),
       "prefix_plot_counts_anonymized":sorted(prefix_counts.values()),
       "literal_Block_field_distinct_category_count":len(block_fields),
       "pool_count_within_each_prefix_anonymized":sorted(map(len,prefix_pool.values())),
       "original_richness_within_prefix_eligible_strata_counts_anonymized":sorted(matched.values()),
       "original_physical_randomized_block_identity_certified":False,
       "original_biomass_effect_estimated":False,
       "original_plot_species_and_outcome_values_exported":False
    }

def jexis():
    result={"status":"JEXIS_PUBLIC_DESIGN_CROSSWALK_ACCESS_HOLD",
            "official_dataset_id":739,"original_plot_block_identity_crosswalk_verified":False}
    try:
        req=urllib.request.Request(JEXIS,headers={
            "User-Agent":"turnover-jena-TBE-design-original-source-probe/0.1",
            "Accept":"application/zip,text/tab-separated-values"})
        with urllib.request.urlopen(req,timeout=20) as response:
            if response.status!=200:raise ValueError("JEXIS_PUBLIC_NON_200")
            body=response.read(JEXIS_BYTES+1)
        if len(body)>JEXIS_BYTES:raise ValueError("JEXIS_SOURCE_SIZE_CAP")
        if body[:2]!=b"PK":
            raise ValueError("JEXIS_RESPONSE_NOT_PUBLIC_ZIP")
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            if z.testzip():raise ValueError("JEXIS_ZIP_CRC_HOLD")
            items=[p for p in z.infolist() if not p.is_dir()]
            if len(items)>20 or any(x.file_size>800_000 for x in items):
                raise ValueError("JEXIS_ZIP_PAYLOAD_NOT_SOURCE_QUALIFIED")
            result["file_count"]=len(items)
            result["size_bytes"]=len(body)
            result["sha256"]=hashlib.sha256(body).hexdigest()
            result["status"]="JEXIS_PUBLIC_ZIP_AVAILABLE__IDENTITY_CROSSWALK_NOT_YET_QUALIFIED"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,zipfile.BadZipFile) as e:
        result["status"]="JEXIS_PUBLIC_ACCESS_OR_SCHEMA_HOLD"
        result["error_class"]=type(e).__name__
        if isinstance(e,urllib.error.HTTPError):result["http_status"]=e.code
        if isinstance(e,ValueError):result["reason"]=str(e)[:80]
    return result

def selftest():
    assert PATTERN.fullmatch("B0BA001").group(1)=="A"
    assert PATTERN.fullmatch("B0BB047").group(1)=="B"
    assert PATTERN.fullmatch("B0BC093").group(1)=="C"
    assert PATTERN.fullmatch("B0BD999") is None
    print('{"status":"JENA_TBE_ORIGINAL_PREFIX_SOURCE_FIXTURE_PASS","checks":4}')

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    if args.self_test:selftest()
    else:
        x=inspect()
        x["JEXIS_design_source"]=jexis()
        x["causal_assignment_claim_authorized"]=False
        x["original_v01_3_literal_blocks_gate_HOLD"]=True
        assert x["original_biomass_effect_estimated"] is False
        assert x["original_plot_species_and_outcome_values_exported"] is False
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
        print("JENA_TBE_PLOT_PREFIX_SOURCE_ONLY",json.dumps({
          "status":x["status"],"plots":x["source_distinct_plots"],
          "prefix_counts":x["prefix_plot_counts_anonymized"],
          "literal_Block_categories":x["literal_Block_field_distinct_category_count"],
          "JEXIS":x["JEXIS_design_source"]["status"],
          "new_biological_effects":0}))
