#!/usr/bin/env python3
"""Source/geometry-only QA for published Jena decade-long FD and measured biomass.

Does not export numeric biomass values, FD values, cross-correlations, regression,
or new biological tests. Does not treat the Jena site as global replication.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,zipfile
from pathlib import Path
from collections import Counter,defaultdict

PINNED={
 "predictors_raw.zip":"4af2ccca7b85b7a15b47ace87acfe0386feab79da51d3d5f67b3cf6034442e4b",
 "biomass02_12.zip":"aa4e4904c200e4a7d35cfd713a47969b3c08f014bccfe245ee1e875db",
 "traits.st.zip":"5ae74c473ff2e36861f137f4fc8a28740725a90dda9e265350fd45bcb38996c5",
}
PLOT_HASH="7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70"
FROZEN_TRAITS=["h1","sla","leafN","SeedsTCW"]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def nonempty_number(x):
    try:
        val=float(x)
        return math.isfinite(val) and val != -9999
    except (TypeError,ValueError):return False
def load_zip(path,name):
    raw=Path(path).read_bytes()
    if sha(raw)!=PINNED[name]:raise ValueError(f"SHA256 changed {name}")
    with zipfile.ZipFile(io.BytesIO(raw)) as zip:
        names=[n for n in zip.namelist() if not n.endswith("/") and n.lower().endswith(".csv")]
        if len(names)!=1:raise ValueError(f"expected single source csv in {name}: {names}")
        with zip.open(names[0]) as f:
            txt=io.TextIOWrapper(f,encoding="utf-8-sig",errors="replace",newline="")
            reader=csv.DictReader(txt)
            cols=list(reader.fieldnames or [])
            rows=list(reader)
    if not cols or len(cols)!=len(set(cols)):raise ValueError("invalid source column headers")
    return cols,rows,{"name":name,"sha256":sha(raw),"zip_csv_name":names[0],
                       "csv_rows":len(rows),"csv_columns":len(cols)}

def plot_map(path):
    raw=Path(path).read_bytes()
    if sha(raw)!=PLOT_HASH:raise ValueError("plot information exact source checksum mismatch")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig")),delimiter="\t"))
    if len(rows)!=82:raise ValueError("Original plot info not 82")
    lookup={}
    for r in rows:
        for key in ("number","plotcode","plot"):
            candidate=(key,str(r[key]).strip())
            if candidate in lookup and lookup[candidate]!=r["plotcode"]:
                raise ValueError("Ambiguous plot alias: "+str(candidate))
            lookup[candidate]=r["plotcode"]
    return rows,lookup

def normalize_key(k,row,plot_alias):
    original=str(row.get(k,"")).strip()
    if not original:return None
    if original in plot_alias:return plot_alias[original]
    return None

def key_maps(p_rows,b_rows,info):
    # Plot-alias modes are *separate*, not auto-selected from outcome.
    aliases={n:{str(r[n]).strip():str(r["plotcode"]).strip()
                for r in info if str(r.get(n,"")).strip()}
             for n in ("plotcode","plot","number")}
    stats={}
    for label,rows,col in (("predictors",p_rows,"plot"),("biomass",b_rows,"plotcode")):
        vals={str(r.get(col) or "").strip() for r in rows if str(r.get(col) or "").strip()}
        stats[label]={
          "field":col,"n_unique_keys":len(vals),
          "exact_plotcode_overlap":len(vals & set(aliases["plotcode"])),
          "plot_local_field_overlap":len(vals & set(aliases["plot"])),
          "plot_number_field_overlap":len(vals & set(aliases["number"])),
        }
    return stats

def inspect(pfile,bfile,tfile,infofile):
    pcols,p_rows,pdoc=load_zip(pfile,"predictors_raw.zip")
    bcols,b_rows,bdoc=load_zip(bfile,"biomass02_12.zip")
    tcols,t_rows,tdoc=load_zip(tfile,"traits.st.zip")
    info,lookup=plot_map(infofile)
    neededp=["plot","year","season"]+["FD_"+trait for trait in FROZEN_TRAITS]
    neededb=["plotcode","year","month","subsample","target.biomass"]
    if any(k not in pcols for k in neededp) or any(k not in bcols for k in neededb):
        raise ValueError("Missing required original predictors or biomass source fields")
    if "sp" not in tcols:raise ValueError("Traits file lacks species key")
    file_names,diagnostic=key_maps(p_rows,b_rows,info),{}
    sample_count=Counter()
    key_counts_p=Counter()
    keys_b=Counter()
    species_trait_counts={}
    for trait in FROZEN_TRAITS:
        col="FD_"+trait
        present=sum(nonempty_number(r.get(col)) for r in p_rows)
        species_values=sum(nonempty_number(r.get(trait)) for r in t_rows) if trait in tcols else 0
        species_trait_counts[trait]={"predictor_nonmissing":present,
                                     "predictor_fraction":present/len(p_rows) if p_rows else 0,
                                     "trait_table_species_nonmissing":species_values,
                                     "trait_column_in_original":trait in tcols}
    for r in p_rows:
        sample_count["predictor_season_"+str(r.get("season"))]+=1
        sample_count["predictor_year_"+str(r.get("year"))]+=1
        key_counts_p[(str(r.get("plot","")).strip(),str(r.get("year","")).strip(),str(r.get("season","")).strip())]+=1
    for r in b_rows:
        sample_count["biomass_month_"+str(r.get("month"))]+=1
        sample_count["biomass_year_"+str(r.get("year"))]+=1
        sample_count["biomass_subsample_"+str(r.get("subsample"))]+=1
        if nonempty_number(r.get("target.biomass")):
            sample_count["biomass_finite_response_rows"]+=1
        keys_b[(str(r.get("plotcode","")).strip(),str(r.get("year","")).strip(),str(r.get("month","")).strip())]+=1
    doc={
      "status":"SOURCE_ONLY_CROSSWALK_PROFILE",
      "source":"PANGAEA.923591 source attachments 2024; excludes full/raw model outcomes",
      "files":[pdoc,bdoc,tdoc],
      "plot_original_info_sha256":PLOT_HASH,
      "n_original_plots":len(info),
      "key_candidate_mode_support":file_names,
      "expected_field_coverage":species_trait_counts,
      "season_year_month_and_replicate_counts":dict(sorted(sample_count.items())),
      "distinct_plot_year_season_predictor_combinations":len(key_counts_p),
      "predictor_keys_with_duplicate_rows":sum(n>1 for n in key_counts_p.values()),
      "distinct_biomass_plot_year_month_combinations":len(keys_b),
      "biomass_keys_with_duplicate_subsample_rows":sum(n>1 for n in keys_b.values()),
      "n_trait_species_rows":len(t_rows),
      "status_inference":"NO_BIOMASS_FD_EFFECT_OPENED",
      "hard_nonclaims":["No independent site replication", "PANGAEA traits overlap published analyses; not novel independent data",
        "FD predictors may reflect same-year realized composition; not ex-ante forecast",
        "File-header matches and monthly availability do not prove valid same-plot measured join",
        "No observed biomass numerical values exported, no effect or R² estimated"],
    }
    return doc

def self_test():
    assert nonempty_number("0")
    assert not nonempty_number("-9999")
    assert not nonempty_number("")
    assert not nonempty_number("NaN")
    return {"status":"SELF_TEST_PASS","checks":4}

if __name__=="__main__":
    a=argparse.ArgumentParser(description=__doc__)
    for name in ("predictors","biomass","traits","plotinfo","out"):
        a.add_argument("--"+name)
    a.add_argument("--self-test",action="store_true")
    args=a.parse_args()
    if args.self_test:
        print(json.dumps(self_test()))
    else:
        if not all(getattr(args,x,None) for x in ("predictors","biomass","traits","plotinfo","out")):
            a.error("All 5 paths required")
        doc=inspect(args.predictors,args.biomass,args.traits,args.plotinfo)
        out=Path(args.out)
        out.parent.mkdir(exist_ok=True,parents=True)
        out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("JENA_LONGITUDINAL_SOURCE_QA",json.dumps(doc,sort_keys=True))
