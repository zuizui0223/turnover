#!/usr/bin/env python3
"""Post-HOLD source-grain diagnosis: NutNet original Figshare 2025 vs Zenodo 2026.

Only distinct counts and taxon syntax classes, never original species names,
site codes, plot identifiers, original cover or biomass values; no FD/K effects.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import unicodedata
from pathlib import Path

from audit_nutnet_figshare2025_vs_zenodo2026_original_coverage_join_v0_1 import (
    original_figshare, original_zenodo, parse_csv, stable_id, numeric,
    FIG_ID, FIG_MD5, ZEN_DATA_MD5
)

CONTROL={"control","ctrl","ambient"}


def classify_taxon(value):
    s=" ".join(str(value or "").split())
    if not s:return "blank"
    if not s.isascii():return "non_ascii_taxon_label"
    if re.fullmatch(r"[A-Z][a-z-]+ [a-z][a-z-]+",s):
        return "capitalized_genus_species_binomial"
    if re.fullmatch(r"[a-z][a-z-]+ [a-z][a-z-]+",s):
        return "lowercase_genus_species_binomial"
    if re.fullmatch(r"[A-Za-z][A-Za-z-]+ [a-z][a-z-]+",s):
        return "other_case_genus_species_binomial"
    if re.fullmatch(r"[a-zA-Z-]+",s):
        return "single_alpha_word"
    if re.search(r"\b(?:sp|spp|cf|agg)\b",s,flags=re.I):
        return "indeterminate_sp_cf_agg"
    if len(s.split())>2:
        return "three_plus_words"
    if any(ch.isdigit() for ch in s):
        return "contains_digit"
    return "other_source_taxon_format"


def audit():
    zen,zh=parse_csv(original_zenodo())
    fig,fh=parse_csv(original_figshare())
    if len(zen)!=1108 or len(fig)!=5668:
        raise ValueError("SOURCE_HOLD: original source row counts changed")
    print("POST_HOLD_SOURCE_MD5_PLOT_TAXON_PASS: Zenodo",len(zen),"Figshare",len(fig),flush=True)
    Zsite=set()
    Zsy=set()
    Zsp=set()
    Zspy=set()
    Zy=collections.Counter()
    for r in zen:
        a=stable_id(r["siteID"]);p=stable_id(r["plotID"]);y=stable_id(r["year"])
        if not a or not p or not y:raise ValueError("SOURCE_HOLD: original Zenodo ID invalid")
        Zsite.add(a);Zsy.add((a,y));Zsp.add((a,p));Zspy.add((a,p,y));Zy[y]+=1
    fsite=set();fsy=set();fsp=set();fspy=set()
    csite=set();csy=set();csp=set();cspy=set()
    nsite=set();nsy=set();nsp=set();nspy=set()
    format_counts=collections.Counter()
    site_by_year=collections.defaultdict(set)
    control_years=collections.Counter()
    npk_years=collections.Counter()
    Fy=collections.Counter()
    trty=collections.Counter()
    treatments=collections.Counter()
    taxa=set()
    bad_year=0
    for r in fig:
        s=stable_id(r["site_code"]);p=stable_id(r["plot"]);y=stable_id(r["year"])
        ty=stable_id(r["year_trt"]);trt=str(r["trt"] or "").strip().casefold()
        if not s or not p or not y:bad_year+=1;continue
        fsite.add(s);fsy.add((s,y));fsp.add((s,p));fspy.add((s,p,y))
        Fy[y]+=1;trty[ty]+=1;treatments[trt]+=1
        sp=" ".join(str(r["standard_taxon"] or "").split())
        taxa.add(sp);format_counts[classify_taxon(sp)]+=1
        site_by_year[s].add(y)
        if trt in CONTROL:
            csite.add(s);csy.add((s,y));csp.add((s,p));cspy.add((s,p,y))
            control_years[y]+=1
        elif trt=="npk":
            nsite.add(s);nsy.add((s,y));nsp.add((s,p));nspy.add((s,p,y))
            npk_years[y]+=1
    if bad_year>0:
        raise ValueError("SOURCE_HOLD: missing 2025 Figshare source site/plot/year, no correction")
    # One plot may represent multiple original species; only unique site IDs
    # are compared; original join uses zero alias/fuzzy matches.
    year_n_shared=len(fsy&Zsy)
    matched_sites=Zsite&fsite
    common_site_years={s: len(set(y for a,y in Zsy if a==s)&site_by_year[s]) for s in matched_sites}
    out={
      "version":"v0.2",
      "status":"POST_HOLD_NUTNET_2025_2026_SOURCE_YEAR_TAXON_FORMAT_DIAGNOSIS_COMPLETED",
      "previous_frozen_source_gate_result":"ORIGINAL_FIGSHARE_ZENODO_EXACT_SOURCE_COMPOSITION_JOIN_HOLD",
      "original_2025_Figshare_article_id":26412295,
      "original_2025_Figshare_file_id":FIG_ID,
      "original_2025_Figshare_MD5":FIG_MD5,
      "original_2026_Zenodo_biomass_MD5":ZEN_DATA_MD5,
      "original_2025_cover_rows":len(fig),
      "original_2026_biomass_CWM_rows":len(zen),
      "distinct_original_2025_taxon_string_labels":len(taxa),
      "original_taxon_syntax_label_rows":dict(sorted(format_counts.items())),
      "original_Zenodo_2026_original_calendar_year_histogram":dict(sorted(Zy.items())),
      "original_Figshare_2025_source_year_field_histogram":dict(sorted(Fy.items())),
      "original_Figshare_2025_source_treatment_relative_year_histogram":dict(sorted(trty.items())),
      "original_Figshare_2025_source_control_year_histogram":dict(sorted(control_years.items())),
      "original_Figshare_2025_source_NPK_year_histogram":dict(sorted(npk_years.items())),
      "2025_figshare_original_treatment_labels":dict(sorted(treatments.items())),
      "source_strict_overlap":{
          "n_unique_2025_figshare_site_names":len(fsite),
          "n_unique_2026_zenodo_site_names":len(Zsite),
          "n_common_site_names":len(matched_sites),
          "n_common_site_and_original_year":year_n_shared,
          "n_common_site_plot_disregarding_year":len(fsp&Zsp),
          "n_common_site_plot_year_all_treatments":len(fspy&Zspy),
          "n_common_site_plot_year_original_control":len(cspy&Zspy),
          "n_common_site_plot_original_control_disregarding_year":len(csp&Zsp),
          "n_common_site_year_original_control":len(csy&Zsy),
          "n_common_site_year_NPK":len(nsy&Zsy),
          "n_original_sites_with_atleast_one_exact_shared_year":sum(n>0 for n in common_site_years.values())
      },
      "source_semantics":{
          "2025_year_calendar_assumption":"NOT VERIFIED; source field values reported as is without renaming",
          "2025_year_trt_0_exists":any(y=="0" for y in trty),
          "2026_original_pretreatment_baseline_identity":"Published Zenodo original source documentation only, cross-release year mapping not certified",
          "original_2025_cover_trt_column_not_reclassified":True,
          "species_name_accepted_synonym_mapping":"NONE; source syntax classified without taxonomic renaming",
      },
      "nonclaims":[
         "Zero direct site+year overlap does not rule out same biological years if different indexing conventions exist, but no authorized conversion is known.",
         "Source syntax class mismatch does not prove these taxon strings are not scientifically identifiable.",
         "No original NutNet shared site/plot/year crosswalk was inferred by guessing block-plot mapping.",
         "No K, FD, PD, aboveground biomass model or causal effect was estimated.",
         "No raw species names, site or plot identifiers, cover or biomass values were exported."
      ],
      "safe_next_step":"Source-original data dictionaries and the published Figshare species-label semantics are necessary before a different temporal/plot crosswalk; do not revise the frozen strict join to force a positive result."
    }
    if out["source_strict_overlap"]["n_common_site_names"]!=57:
        raise ValueError("SOURCE_HOLD: historical 57 shared source site code count changed")
    if out["source_strict_overlap"]["n_common_site_and_original_year"]!=0:
        raise ValueError("SOURCE_DRIFT: original cross-release year coincidence changed; do NOT silently accept as temporal match")
    return out


def fixture():
    assert classify_taxon("Poa pratensis")=="capitalized_genus_species_binomial"
    assert classify_taxon("poa pratensis")=="lowercase_genus_species_binomial"
    assert classify_taxon("Carex sp.")=="indeterminate_sp_cf_agg"
    return {"status":"POST_HOLD_NUTNET_SOURCE_SEMANTIC_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.out:p.error("--out required")
        o=audit()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("POST_HOLD_NUTNET_YEAR_AND_TAXON_SYNTAX_SOURCE_DIAGNOSIS",json.dumps(o,sort_keys=True),flush=True)
