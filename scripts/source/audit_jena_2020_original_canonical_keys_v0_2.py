#!/usr/bin/env python3
"""Source-only exact key and species source-identity audit Jena 2020.

No ecological effects, FD or biomass associations opened. Author script:
fonsvanderplas/traits-and-ecosystem-properties/main analysis.r
Source file original Figshare IDs & bytes/MD5 pinned v0.1.
"""
from __future__ import annotations
import argparse,collections,csv,io,json,math,re
from pathlib import Path
from audit_jena_2020_original_csv_grain_v0_1 import FILES,get_orig

BIO="biomass02_12.csv"
COVER="CoverMain-JenaExp2003-2015all.csv"
TRAIT="traits.st.csv"
FUNCTION="functions raw values.csv"
PRECOMPUTED="predictors_raw.csv"
MIN_PLOTS=60
MIN_YEARS=7
MIN_SPECIES=20

def csv_rows(name):
    blob=get_orig(name)
    try:s=blob.decode("utf-8-sig")
    except UnicodeDecodeError:s=blob.decode("cp1252")
    x=csv.DictReader(io.StringIO(s,newline=""))
    if not x.fieldnames or len(x.fieldnames)<3:raise ValueError("SOURCE_HOLD: original header")
    rows=list(x)
    if any(None in r for r in rows):raise ValueError("SOURCE_HOLD: malformed CSV row "+name)
    return x.fieldnames,rows

def canonical(s):
    s=str(s or "").strip()
    return s if s and s.casefold() not in {"null","na","nan","-9999"} else None

def code(s):
    """Author source uses '.' vs '_' for same two-part source taxon abbreviations."""
    s=canonical(s)
    if s is None:return None
    return re.sub(r"[._]","",s.casefold())

def original_keys(rows,plot,year):
    plot_ids=set();year_ids=set();pairs=set();missing=0;sites=collections.Counter()
    for r in rows:
        p=canonical(r.get(plot))
        y=canonical(r.get(year))
        if not p or not y:
            missing+=1
            continue
        plot_ids.add(p)
        year_ids.add(y)
        pairs.add((p,y))
        sites[y]+=1
    return {"plots":plot_ids,"years":year_ids,"plotyear":pairs,"year_rows":sites,"missing":missing}

def float_presence(v):
    s=canonical(v)
    if s is None:return "SOURCE_MISSING_OR_SENTINEL"
    try:
        x=float(s)
        if not math.isfinite(x):return "SOURCE_MISSING_OR_SENTINEL"
        if x<0:return "SOURCE_NEGATIVE"
        return "SOURCE_POSITIVE" if x>0 else "SOURCE_ZERO"
    except Exception:return "SOURCE_NONTYPE"

def audit():
    h_b,b=csv_rows(BIO)
    h_c,c=csv_rows(COVER)
    h_t,t=csv_rows(TRAIT)
    h_f,f=csv_rows(FUNCTION)
    h_p,p=csv_rows(PRECOMPUTED)
    must={
        BIO:({"plotcode","block","plot","subsample","year","month","target.biomass"},h_b),
        COVER:({"Plot","Year","Month"},h_c),
        TRAIT:({"sp"},h_t),
        FUNCTION:({"plot","year","target_biomass_average"},h_f),
        PRECOMPUTED:({"plot","year","season"},h_p)
    }
    for name,(cols,header) in must.items():
        if not cols.issubset(header):
            raise ValueError("ORIGINAL_SCHEMA_HOLD: required source columns absent "+name+" "+str(sorted(cols-set(header))))
    if [len(z) for z in (b,c,t,f,p)] != [5544,2214,59,851,1619]:
        raise ValueError("ORIGINAL_SOURCE_HOLD: source fixed 2020 rows changed")
    bk=original_keys(b,"plotcode","year")
    ck=original_keys(c,"Plot","Year")
    fk=original_keys(f,"plot","year")
    pk=original_keys(p,"plot","year")
    if len(fk["plots"])!=78 or len(ck["plots"])!=82:
        raise ValueError("ORIGINAL_SOURCE_HOLD: original 78 main and 82 cover source plots")
    numeric_plotcodes={canonical(x["plot"]) for x in b if canonical(x["plot"]) is not None}
    plot_composites={(canonical(x["block"]),canonical(x["plot"])) for x in b if canonical(x["block"]) and canonical(x["plot"])}
    cross={
      "original_2020_main_function_plots":len(fk["plots"]),
      "original_biomass_complete_plotcodes":len(bk["plots"]),
      "original_plant_cover_plots":len(ck["plots"]),
      "original_species_trait_reference_rows":len(t),
      "original_biomass_numeric_plot_values_only":len(numeric_plotcodes),
      "original_biomass_composite_block_plot_ids":len(plot_composites),
      "original_author_source_code_field_to_use_for_biomass":"plotcode",
      "original_author_source_cover_Plot_to_use":"Plot",
      "original_author_source_functions_plot_to_use":"plot",
      "original_publication_2020_figshare_years_function":sorted(fk["years"]),
      "original_publication_2020_figshare_years_cover":sorted(ck["years"]),
      "original_publication_2020_figshare_years_biomass":sorted(bk["years"]),
      "n_exact_original_main_plotcodes_present_in_biomass":len(fk["plots"]&bk["plots"]),
      "n_exact_original_main_plotcodes_present_in_cover":len(fk["plots"]&ck["plots"]),
      "n_exact_main_plotcodes_present_in_both_original_cover_and_biomass":len(fk["plots"]&ck["plots"]&bk["plots"]),
      "n_original_functions_plotyears":len(fk["plotyear"]),
      "n_original_cover_plotyears":len(ck["plotyear"]),
      "n_original_biomass_plotyears":len(bk["plotyear"]),
      "n_exact_original_function_biomass_plotyear_overlap":len(fk["plotyear"]&bk["plotyear"]),
      "n_exact_original_function_cover_plotyear_overlap":len(fk["plotyear"]&ck["plotyear"]),
      "n_exact_original_function_cover_biomass_plotyear_overlap":len(fk["plotyear"]&ck["plotyear"]&bk["plotyear"]),
      "n_main_plotcodes_missing_in_biomass":len(fk["plots"]-bk["plots"]),
      "n_main_plotcodes_missing_in_cover":len(fk["plots"]-ck["plots"]),
      "n_canonical_plotyear_missing_original_fields":{
        "functions":fk["missing"],"cover":ck["missing"],"biomass":bk["missing"],"derived_predictors":pk["missing"]},
      "n_derived_predictor_plotyears":len(pk["plotyear"]),
      "n_main_plotcodes_in_authors_derived_predictors":len(fk["plots"]&pk["plots"]),
    }
    # Exact published abbreviated source 2-part species codes, ONLY punctuation
    # differences allowed. Do not fuzzy-match taxonomy or synonym rescue.
    spec_traits={code(z["sp"]) for z in t if code(z["sp"]) is not None}
    spec_cover={code(x) for x in h_c[3:] if code(x) is not None}
    spec_bio={code(x) for x in h_b[h_b.index("Alo.pra"):] if code(x) is not None}
    spec_common=spec_traits&spec_cover&spec_bio
    source_species={
      "n_unique_source_trait_species_codes":len(spec_traits),
      "n_cover_source_species_columns":len(spec_cover),
      "n_biomass_source_species_columns":len(spec_bio),
      "n_trait_species_exact_authors_abbreviated_code_in_biomass_and_cover":len(spec_common),
      "n_trait_species_missing_in_cover":len(spec_traits-spec_cover),
      "n_trait_species_missing_in_biomass":len(spec_traits-spec_bio),
      "n_cover_species_without_original_trait_table":len(spec_cover-spec_traits),
      "no_species_codes_or_original_taxon_labels_exported":True
    }
    response=collections.Counter(float_presence(row["target_biomass_average"]) for row in f)
    response_year=collections.defaultdict(lambda:collections.Counter())
    for row in f:
        year=canonical(row["year"]) or "SOURCE_MISSING"
        response_year[year][float_presence(row["target_biomass_average"])]+=1
    # Source only: response numeric existence by source year. Does not
    # calculate per-plot/year values, mean response, traits or effects.
    qualify_years=sorted(int(y) for y,s in response_year.items()
         if y.isdigit() and 2003<=int(y)<=2012 and s["SOURCE_POSITIVE"]+s["SOURCE_ZERO"]>0)
    structure=(
        len(fk["plots"]&bk["plots"]&ck["plots"])>=MIN_PLOTS
        and len(qualify_years)>=MIN_YEARS
        and len(spec_common)>=MIN_SPECIES
        and cross["n_exact_original_function_cover_biomass_plotyear_overlap"]>=MIN_PLOTS*MIN_YEARS*.6
    )
    return {
        "version":"v0.2",
        "status":"JENA_ORIGINAL_AUTHOR_CODE_CANONICAL_KEY_SOURCE_GEOMETRY_PASS" if structure else "JENA_ORIGINAL_CROSSFILE_KEY_SOURCE_HOLD",
        "source_only":True,"no_biomass_FD_or_K_predictor_response_effect_estimated":True,
        "original_author_script":"fonsvanderplas/traits-and-ecosystem-properties/main analysis.r",
        "original_author_script_uses_cover_minus9999_as_zero_and_codes_1_to_0point5_2_to_3":True,
        "original_author_script_uses_target_biomass_positive_row_selection_when_building_derived_community":True,
        "derived_full_panel_predictors_not_independently_future_year_fold_safe":True,
        "original_author_script_calculates_RaoQ_FD_and_biomass_weighted_CWM":True,
        "original_author_script_uses_PCA_imputation_of_trait_table":True,
        "original_2020_authors_Figshare_MD5_six_source_files_reverified":True,
        "original_source_keys_and_cardinality":cross,
        "original_trait_species_abbreviation_identity":source_species,
        "original_functions_raw_target_biomass_presence_not_effect":dict(response),
        "original_functions_raw_target_biomass_presence_by_year_not_effect":{k:dict(v) for k,v in sorted(response_year.items())},
        "n_source_years_2003to2012_with_numeric_original_function_biomass":len(qualify_years),
        "source_years_2003to2012_with_numeric_original_function_biomass":qualify_years,
        "source_thresholds":{"min_matched_canonical_original_plots":MIN_PLOTS,"min_years_numeric_2003to2012":MIN_YEARS,"min_original_trait_species":MIN_SPECIES,"min_matched_plotyears_fraction_of_theoretical_min":.6},
        "next_step":"If original exact plotcode and year source geometry qualifies, separately freeze source-only all-original plot-year feature construction from cover and traits, never conditioned on future heldout biomass. Any future original time-transport test must be a separately outcome-frozen exploratory analysis.",
        "independence_limits":["Same Jena study as authors' 2020 and 2022 reply; and overlaps earlier turnover Jena original guild source.","Different ecosystem from TreeDivNet forestry, but original source only one Jena field experiment.","Original authors used PCA-imputed traits and a Rao's Q FD, not plot-measured 2D Euclidean FD; do not call them directly equivalent."],
    }

def fixture():
    assert code("Alo_pra")==code("Alo.pra")
    assert code("Med.var")==code("Med_var")
    assert code("Random genus")!=code("Alo.pra")
    assert float_presence("-9999")=="SOURCE_MISSING_OR_SENTINEL"
    assert float_presence("0")=="SOURCE_ZERO"
    return {"status":"ORIGINAL_AUTHOR_PLOTCODE_AND_TRAIT_CODE_SOURCE_FIXTURE_PASS","checks":5}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:
       print(json.dumps(fixture(),sort_keys=True))
    else:
       if not args.out:parser.error("--out mandatory")
       v=audit()
       args.out.parent.mkdir(parents=True,exist_ok=True)
       args.out.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
       print("JENA_2020_ORIGINAL_COMPLETE_PLOTCODE_SPECIES_YEAR_SOURCE",
             json.dumps(v,sort_keys=True),flush=True)
