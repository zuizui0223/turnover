#!/usr/bin/env python3
"""Source-only eligibility of Noulekoun et al. GEB original Zenodo 276 plots.

No biomass/functional diversity ecological regression. Verify five country
fold covariate matrix rank, original std AGB/FDis numerical presence and
source grain before opening a NEW exploratory country-transfer model.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,io,json,math,urllib.parse,urllib.request
from pathlib import Path

import numpy as np

ZENODO_ID=10045492
SOURCE_MD5="60fc555c8e2942af432b09d3aeb84d57"
SOURCE_NAME="dataall_Noulekoun_GEB.csv"
REQUIRED_CONT=("sd_richness","sd_cwmwd","sd_cwmsla","sd_cwmlnc","sd_cwmhm","sd_prec","sd_temp","sd_plots")
SOURCE_TARGET="sd_agb.mg.ha"
SOURCE_FDIS="sd_fdis"
N_COUNTRIES=5
MIN_PLOTS_PER_COUNTRY=12
MIN_TOTAL_COMPLETE=200
UA="turnover-source-only-African-forest-original-FDis-domain-qualification-v0.1"


def fetch_source():
    req=urllib.request.Request(f"https://zenodo.org/api/records/{ZENODO_ID}",headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=95) as response:
        info=json.load(response)
    if int(info.get("id",-1))!=ZENODO_ID:raise ValueError("SOURCE_IDENTITY_HOLD: Zenodo record changed")
    matches=[r for r in info.get("files",[]) if r.get("key")==SOURCE_NAME]
    if len(matches)!=1:raise ValueError("SOURCE_MANIFEST_HOLD: original archived file missing or duplicated")
    f=matches[0]
    url=str((f.get("links") or {}).get("content") or "")
    parsed=urllib.parse.urlparse(url)
    if parsed.hostname!="zenodo.org" or parsed.scheme!="https" or int(f.get("size",0))>1_000_000:
        raise ValueError("SOURCE_LINK_HOLD: unpublished or oversized original source")
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=95) as response:
        raw=response.read(1_000_001)
    if len(raw)!=int(f.get("size")) or hashlib.md5(raw).hexdigest()!=SOURCE_MD5:
        raise ValueError("SOURCE_MD5_HOLD: immutable original data changed")
    return raw


def source_numeric(row,k):
    raw=str(row.get(k) or "").strip()
    if raw.lower() in ("","n/a","na","nan","none","null","-9999"):
        return None
    try:
        x=float(raw)
        return x if math.isfinite(x) else None
    except (ValueError,TypeError):
        return None


def inspect(raw:bytes)->dict:
    reader=csv.DictReader(io.StringIO(raw.decode("utf8-sig")))
    cols=reader.fieldnames or []
    required={"plot_uniq_ID","country","growth","plot_size_ha",SOURCE_TARGET,SOURCE_FDIS,*REQUIRED_CONT}
    if not required.issubset(cols):
        raise ValueError("SOURCE_SCHEMA_HOLD: missing original source columns "+repr(sorted(required-set(cols))))
    rows=list(reader)
    if len(rows)!=276 or len(set(r["plot_uniq_ID"] for r in rows))!=276:
        raise ValueError("SOURCE_GRAIN_HOLD: original 276 distinct plots not reproduced")
    percountry=collections.Counter()
    per_growth=collections.Counter()
    percountry_growth=collections.defaultdict(collections.Counter)
    invalid=collections.Counter()
    distinct_country=set()
    expected=["plot_size_ha",SOURCE_TARGET,SOURCE_FDIS,*REQUIRED_CONT]
    good=[]
    for r in rows:
        country=str(r.get("country") or "").strip()
        growth=str(r.get("growth") or "").strip().lower()
        if not country or not growth:raise ValueError("SOURCE_GRAIN_HOLD: original country/growth missing")
        distinct_country.add(country)
        percountry[country]+=1
        per_growth[growth]+=1
        percountry_growth[country][growth]+=1
        values={k:source_numeric(r,k) for k in expected}
        for k,x in values.items():
            if x is None:invalid[k]+=1
        if any(x is None for x in values.values()) or values["plot_size_ha"]<=0:
            continue
        good.append({**values,"plot_uniq_ID":r["plot_uniq_ID"],"country":country,"growth":growth})
    if len(distinct_country)!=N_COUNTRIES:
        raise ValueError("SOURCE_GRAIN_HOLD: original five countries not reproduced")
    complete_country=collections.Counter(r["country"] for r in good)
    growth_classes=sorted(per_growth)
    if len(growth_classes)!=2:raise ValueError("SOURCE_GRAIN_HOLD: original growth stage class not two")
    rank_by_country={}
    for hold in sorted(complete_country):
        train=[r for r in good if r["country"]!=hold]
        # Only non-target/source covariates are allowed in source model rank
        # preflight; the original AGB and FDis values are not used here.
        full=np.array([[1., *[r[k] for k in REQUIRED_CONT],float(r["growth"]==growth_classes[-1]),r[SOURCE_FDIS]] for r in train],float)
        if not np.isfinite(full).all():
            raise ValueError("SOURCE_MODEL_HOLD: nonfinite original source design")
        scale=np.std(full[:,1:-1],axis=0)
        norm=np.std(full[:,-1])
        r0=int(np.linalg.matrix_rank(full[:,:-1]))
        r1=int(np.linalg.matrix_rank(full))
        rank_by_country[hold]={
           "n_source_train_plots":len(train),"n_source_test_plots":complete_country[hold],
           "rank_baseline":r0,"n_covariates_baseline":full.shape[1]-1,
           "rank_with_FDis":r1,"n_covariates_with_FDis":full.shape[1],
           "nonconstant_original_source_predictors":bool(min(scale)>1e-10 and norm>1e-10),
           "source_rank_full":r0==full.shape[1]-1 and r1==full.shape[1],
        }
    qualified=(len(good)>=MIN_TOTAL_COMPLETE and len(complete_country)==N_COUNTRIES and
       all(n>=MIN_PLOTS_PER_COUNTRY for n in complete_country.values())
       and all(q["source_rank_full"] and q["nonconstant_original_source_predictors"] for q in rank_by_country.values()))
    return {
      "version":"v0.1",
      "status":"AFRICAN_DERIVED_FDIS_AGB_COUNTRY_SOURCE_SUPPORT_PASS" if qualified else "AFRICAN_DERIVED_FDIS_AGB_COUNTRY_SOURCE_SUPPORT_HOLD",
      "source":"Noulekoun et al GEB 2023, Zenodo original record 10045492",
      "original_source_md5":SOURCE_MD5,
      "original_source_total_plot_rows":len(rows),
      "original_plot_ID_unique":True,
      "source_countries":dict(sorted(percountry.items())),
      "source_growth_class_counts":dict(sorted(per_growth.items())),
      "source_growth_class_counts_by_country":{k:dict(sorted(v.items())) for k,v in sorted(percountry_growth.items())},
      "original_complete_response_and_predictor_source_plots":len(good),
      "source_complete_original_plots_by_country":dict(sorted(complete_country.items())),
      "source_nonfinite_or_missing_col_counts":dict(sorted(invalid.items())),
      "source_rank_preflight_by_heldout_country":rank_by_country,
      "source_derived_FDis_original_field":SOURCE_FDIS,
      "source_standardized_AGB_original_field":SOURCE_TARGET,
      "source_original_species_trait_rows_available":False,
      "source_original_species_name_columns_available":False,
      "source_original_biomass_Mg_ha_raw_unstandardized_in_csv":False,
      "source_original_biomass_response_units":"Original authors globally standardized aboveground biomass, not original raw Mg ha−1",
      "source_plot_year_by_record_available":False,
      "data_grain":"One source author-derived aggregate per forest plot, not species or individual tree observations",
      "source_tested_no_FD_AGB_regression_or_effect":True,
      "source_qualifying_limits":{"min_all_complete":MIN_TOTAL_COMPLETE,"min_countries":N_COUNTRIES,"min_per_country":MIN_PLOTS_PER_COUNTRY},
      "outcome_analysis_authorization":"SEPARATE_DERIVED_PLOT_INDEX_COUNTRY_HOLDOUT_ONLY" if qualified else "SOURCE_HOLD",
      "no_biological_trait_evolutionary_K_or_plant_community_local_FD_claim":True,
    }


def fixture():
    r={k:"1.0" for k in [*REQUIRED_CONT,"plot_size_ha",SOURCE_FDIS,SOURCE_TARGET]}
    assert all(source_numeric(r,k)==1 for k in REQUIRED_CONT)
    assert source_numeric({"sd_fdis":"-0.5"},"sd_fdis")==-.5
    assert source_numeric({"sd_agb.mg.ha":"NA"},SOURCE_TARGET) is None
    assert MIN_PLOTS_PER_COUNTRY==12 and N_COUNTRIES==5
    return {"status":"AFRICA_COUNTRY_SOURCE_GEOMETRY_FIXTURE_PASS","checks":4}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.out:p.error("--out required")
        audit=inspect(fetch_source())
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(audit,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf8")
        print("AFRICAN_ORIGINAL_DERIVED_FDIS_COUNTRY_SOURCE_GATE",json.dumps(audit,sort_keys=True),flush=True)
