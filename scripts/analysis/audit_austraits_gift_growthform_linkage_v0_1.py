#!/usr/bin/env python3
"""Public GIFT 3.1 macroecological context feasibility on original AusTraits K species.

Preserves the original 254/760/142 K systems, native phylogenetic K results,
species/source filters and numerical results unchanged. Matches accepted GIFT
names EXACTLY, reports coverage and descriptive trait strata. No species,
specimens, raw measurements, independent-source or DOI claims are exported.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,time,urllib.parse,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
from statistics import median

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qa"))
from audit_austraits_organ_contributing_sources_v0_1 import source_graph,compile_states,make_pairs
import duckdb

API="https://gift.uni-goettingen.de/api/extended/index3.1.php"
GIFT_VERSION="3.1"
RAW_PARQUET_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
STATUS="PASS_PUBLIC_GIFT_3_1_AUSTRAITS_ORIGINAL_K_EXACT_NAME_MATCH_COVERAGE_ONLY"
TRAITS={"growth_form":"1.2.1","woodiness":"1.1.1","plant_height_max":"1.6.2"}
BATCH=10000

def need(ok,msg):
    if not ok:raise AssertionError(msg)

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def request(query,opts):
    u=API+"?"+urllib.parse.urlencode({"query":query,**opts})
    last=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(u,headers={
                "User-Agent":"turnover-GIFT-source-overlap-audit/0.1 (research",
                "Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=100) as r:
                need(r.status==200,"GIFT API non-200 response")
                payload=json.load(r)
            need(isinstance(payload,list),"GIFT API expected list response")
            return payload
        except (ValueError,TimeoutError,urllib.error.URLError) as e:
            last=e
            time.sleep(min(2**attempt,5))
    raise RuntimeError("Unreachable original GIFT v3.1 public API: "+str(last))

def pages(query,opts={},max_rows=600000):
    offset=0
    seen_start=None
    all_rows=[]
    for page in range(100):
        current=request(query,{**opts,"startat":offset,"limit":BATCH})
        need(len(current)<=BATCH,"GIFT API chunk ignored requested limit")
        if current:
            sign=json.dumps(current[0],sort_keys=True)
            need(sign!=seen_start,"GIFT pagination repeated first item")
            seen_start=sign
        all_rows.extend(current)
        if len(current)<BATCH:return all_rows
        offset+=len(current)
        need(offset<max_rows,"GIFT public records exceed freeze maximum")
        time.sleep(0.05)
    raise RuntimeError("Public GIFT pagination exceeded maximum page count")

def normalize(name):
    return " ".join(str(name or "").replace("_"," ").strip().casefold().split())

def collect_original_species(c):
    def species(sql):return {x[0] for x in c.execute(sql).fetchall()}
    base={
       "original_254_single_K":species("SELECT DISTINCT species FROM states"),
       "original_760_matched_K":species("SELECT DISTINCT species FROM matched_active"),
       "strict_142_same_DatasetID":species("SELECT DISTINCT species FROM strict_active")
    }
    need(base["strict_142_same_DatasetID"].issubset(base["original_254_single_K"]),
         "Original fixed source species set not nested in 254 graph")
    need(base["original_760_matched_K"].issubset(base["original_254_single_K"]),
         "Original same-tip K species not nested in eligible 254 states")
    broad=c.execute("""SELECT DISTINCT t.family,t.trait_A,t.trait_B,a.species
       FROM strict_targets t
       JOIN nonflora_states a ON a.sid=t.system_A
       JOIN nonflora_states b ON b.sid=t.system_B
          AND a.species=b.species AND a.genus=b.genus""").fetchall()
    strict=c.execute("""SELECT DISTINCT family,trait_A,trait_B,species
       FROM same_dataset""").fetchall()
    broad_d=defaultdict(set);strict_d=defaultdict(set)
    for fam,tr1,tr2,sp in broad:broad_d[(fam,tr1,tr2)].add(sp)
    for fam,tr1,tr2,sp in strict:strict_d[(fam,tr1,tr2)].add(sp)
    need(len(broad_d)==len(strict_d)==142,"Original strict K pair identities not restored")
    need(all(strict_d[k].issubset(broad_d[k]) and len(strict_d[k])>=20 for k in strict_d),
         "Original source-taxon nested cohort changed")
    return base,broad_d,strict_d

def map_gift_taxa(original_set):
    all_sp=pages("species",{},max_rows=600000)
    need(len(all_sp)>100000,"GIFT unexpectedly missing global species records")
    ref=defaultdict(set)
    for r in all_sp:
        name=normalize(r.get("work_species",""))
        wid=str(r.get("work_ID") or "")
        if name and wid:ref[name].add(wid)
    names={sp:next(iter(ids)) for sp in original_set
           if len(ids:=ref.get(normalize(sp),set()))==1}
    ambiguous=sum(len(ref.get(normalize(sp),set()))>1 for sp in original_set)
    return names,{"gift_species_rows":len(all_sp),
                  "unique_standardized_gift_names":len(ref),
                  "ambiguous_original_exact_name_matches":ambiguous,
                  "original_unique_species_exact_matched":len(names),
                  "no_synonym_matching_performed":True}

def trait_values():
    meta=request("traits_meta",{})
    need(len(meta)>50,"GIFT 3.1 trait metadata unexpectedly incomplete")
    ids={str(z["Lvl3"]):str(z.get("Trait2","")) for z in meta}
    need(all(t in ids for t in TRAITS.values()),
         "GIFT fixed growth-form/woodiness/height trait IDs changed")
    data={};metadata={}
    for name,tid in TRAITS.items():
        rows=pages("traits",{"traitid":tid,"biasref":0,"biasderiv":0},max_rows=500000)
        mapping=defaultdict(set)
        for row in rows:
            wid=str(row.get("work_ID") or "")
            val=str(row.get("trait_value") if row.get("trait_value") is not None else "").strip()
            if wid and val:mapping[wid].add(val)
        data[name]={k:next(iter(v)) for k,v in mapping.items() if len(v)==1}
        metadata[name]={"gift_trait_ID":tid,"GIFT_trait_name":ids[tid],
                        "records_fetched":len(rows),"work_IDs_with_one_unambiguous_value":len(data[name]),
                        "work_IDs_with_conflicting_values":sum(len(v)>1 for v in mapping.values()),
                        "bias_ref_excluded":True,"bias_deriv_excluded":True}
    return data,metadata

def categories(map_species,tdata,original,strict,broad,flip):
    matching={}
    for name,sp in original.items():
        matched={s for s in sp if s in map_species}
        z={"n_original_unique_species":len(sp),"n_exact_GIFT_species_matches":len(matched),
           "fraction_exact_GIFT_species_match":len(matched)/len(sp)}
        for tr,values in tdata.items():
            covered=sum(map_species[s] in values for s in matched)
            z["n_GIFT_"+tr+"_available_exact_species"]=covered
            z["fraction_GIFT_"+tr+"_available_of_original_species"]=covered/len(sp)
        matching[name]=z
    by_axis={}
    for axis in ("S3","prune_only"):
        subset=[p for p in flip if p["axis"]==axis]
        totals=Counter();pairs=[]
        for x in subset:
            fam=x["family"];rep=x["trait_reproductive"];veg=x["trait_vegetative"]
            keys=[(fam,veg,rep),(fam,rep,veg)]
            k=next((p for p in keys if p in broad),None)
            need(k is not None,"K sign-reversal original pair ID absent in source species graph")
            retained=strict[k];lost=broad[k]-retained
            n_ret=sum(s in map_species for s in retained)
            n_lost=sum(s in map_species for s in lost)
            known_ret=[tdata["woodiness"][map_species[s]] for s in retained
                       if s in map_species and map_species[s] in tdata["woodiness"]]
            known_lost=[tdata["woodiness"][map_species[s]] for s in lost
                        if s in map_species and map_species[s] in tdata["woodiness"]]
            # Raw original GIFT categories vary among sources; do not silently
            # treat ambiguous classes as woody/non-woody.
            def iswoody(x):
                v=normalize(x).replace("-","_").replace(" ","_")
                return 1 if v in ("woody","yes") else 0 if v in ("herbaceous","non_woody","no") else None
            bins_ret=[v for x in known_ret if (v:=iswoody(x)) is not None]
            bins_lost=[v for x in known_lost if (v:=iswoody(x)) is not None]
            row={"axis":axis,"family":fam,"organ_subtype":x["organ_subtype"],
                 "trait_reproductive":rep,"trait_vegetative":veg,
                 "original_taxon_plus_tree_K_reversed":int(x["reversal_taxon_plus_tree"]),
                 "original_same_tips_measurement_K_reversed":int(x["reversal_measurement_same_tips"]),
                 "n_original_nonflora_species":len(broad[k]),
                 "n_retained_same_DatasetID_species":len(retained),
                 "n_lost_after_source_restriction":len(lost),
                 "n_retained_exact_GIFT_name_matches":n_ret,
                 "n_lost_exact_GIFT_name_matches":n_lost,
                 "n_retained_known_GIFT_woodiness":len(bins_ret),
                 "n_lost_known_GIFT_woodiness":len(bins_lost),
                 "fraction_woody_retained_if_classified":sum(bins_ret)/len(bins_ret) if bins_ret else None,
                 "fraction_woody_lost_if_classified":sum(bins_lost)/len(bins_lost) if bins_lost else None}
            pairs.append(row)
            totals["retained_original_pair_weighted_species"]+=len(retained)
            totals["lost_original_pair_weighted_species"]+=len(lost)
            totals["retained_GIFT_exact_matched_pair_weighted"]+=n_ret
            totals["lost_GIFT_exact_matched_pair_weighted"]+=n_lost
        reversed_pairs=[x for x in pairs if x["original_taxon_plus_tree_K_reversed"]]
        other=[x for x in pairs if not x["original_taxon_plus_tree_K_reversed"]]
        def med(field,subset):
            values=[x[field] for x in subset if x[field] is not None]
            return median(values) if values else None
        by_axis[axis]={
           "original_matched_family_trait_pairs":len(pairs),
           "original_K_sign_reversals":len(reversed_pairs),
           "pair_weighted_exact_name_exposure_counts":dict(totals),
           "median_fraction_lost_species_with_exact_GIFT_match_reversed":
             med("n_lost_exact_GIFT_name_matches",reversed_pairs),
           "median_fraction_lost_species_with_exact_GIFT_match_not_reversed":
             med("n_lost_exact_GIFT_name_matches",other),
           "median_GIFT_classified_woody_fraction_lost_reversed":
             med("fraction_woody_lost_if_classified",reversed_pairs),
           "median_GIFT_classified_woody_fraction_retained_reversed":
             med("fraction_woody_retained_if_classified",reversed_pairs),
           "median_GIFT_classified_woody_fraction_lost_not_reversed":
             med("fraction_woody_lost_if_classified",other),
           "median_GIFT_classified_woody_fraction_retained_not_reversed":
             med("fraction_woody_retained_if_classified",other),
           "n_reversed_pairs_with_known_woody_both_lost_and_retained":
             sum(x["n_retained_known_GIFT_woodiness"]>0 and
                 x["n_lost_known_GIFT_woodiness"]>0 for x in reversed_pairs),
           "woodiness_raw_trait_labels_need_manual_semantic_check":True,
           "not_independent_pair_level_biological_replicates":True}
    return matching,by_axis

def main():
    p=argparse.ArgumentParser()
    for name in ("parquet","traits-yml","flip-csv","out"):
        p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args()
    need(sha(args.parquet)==RAW_PARQUET_SHA,"Original public AusTraits data SHA changed")
    c=duckdb.connect(":memory:")
    try:
        refs,pairs,strict=source_graph()
        compile_states(c,args.parquet,args.traits_yml,refs)
        make_pairs(c,pairs,strict)
        original,broad_d,strict_d=collect_original_species(c)
    finally:c.close()
    all_species=set().union(*original.values())
    known,gift_taxa=map_gift_taxa(all_species)
    tdata,trait_metadata=trait_values()
    with args.flip_csv.open(newline="",encoding="utf-8") as f:
        flip=list(csv.DictReader(f))
    need(len(flip)==243,"Original S3/Prune K reversal context missing")
    # Original parsed CSV boolean flag fields may be "0"/"1": coerce
    for x in flip:
        x["reversal_taxon_plus_tree"]=int(x["reversal_taxon_plus_tree"])
        x["reversal_measurement_same_tips"]=int(x["reversal_measurement_same_tips"])
    coverage,context=categories(known,tdata,original,strict_d,broad_d,flip)
    need(coverage["original_254_single_K"]["n_original_unique_species"]>3000,
         "AusTraits original eligible 254 species unusually few")
    result={
       "status":STATUS,
       "original_public_AusTraits_v7_parquet_sha256":RAW_PARQUET_SHA,
       "original_K_254_family_trait_systems":254,
       "original_K_760_matched_pair_ids":760,
       "original_K_strict_142_same_source_pair_ids":142,
       "GIFT_version":"3.1",
       "GIFT_API":API,
       "GIFT_accepted_names_only_exact_match_coverage":coverage,
       "GIFT_taxonomy_download":gift_taxa,
       "GIFT_public_trait_coverage":trait_metadata,
       "GIFT_woodiness_pair_context":context,
       "growth_form_woodiness_and_height_are_context_not_measured_biomass":True,
       "no_plant_total_biomass_allometry_or_allocation_measured":True,
       "GIFT_may_reuse_TRY_AusTraits_underlying_trait_studies":True,
       "GIFT_traits_not_used_to_refit_original_K":True,
       "no_independence_or_causal_recruitment_inferred":True,
       "no_original_species_names_record_ids_or_trait_values_exported":True,
       "original_organ_grouping_retrospective":True,
       "TRY_v7_raw_data_not_downloaded_or_joined":True,
       "external_taxonomy_synonym_resolution_not_yet_applied":True}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":STATUS,
          "covered":coverage,
          "woodiness_pair_context":context,
          "GIFT_taxonomy":gift_taxa,
          "GIFT_trait_records":trait_metadata},sort_keys=True))

if __name__=="__main__":
    main()
