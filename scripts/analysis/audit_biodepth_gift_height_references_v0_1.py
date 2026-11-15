#!/usr/bin/env python3
"""Original GIFT3.1 references audit of 103 BIODEPTH original named species.
Only source metadata and bibliographic sources. No FD or biomass modeling.
"""
from __future__ import annotations
import argparse,collections,datetime,hashlib,json,math,re
from pathlib import Path
from audit_biodepth_103_taxa_gift_height_v0_1 import source,geometry,paged,get,num,binomial,API,HEIGHT_ID

N_SP=372046
N_HEIGHT=70231
DIRECT=re.compile(r"(?i)(?:\bBIODEPTH\b|\bSpehn\b|\bHector\b|European\s+grassland\s+biodiversity\s+experiment)")
INDIRECT=re.compile(r"(?i)(?:\bTRY\b|\bBIEN\b|\bJena Experiment\b|\bCedar Creek\b)")

def references(v):
    s=str(v or "").strip()
    return set(re.findall(r"\d+",s)),bool(s and re.fullmatch(r"[0-9,;|\s]+",s))

def coverage(plots,valid):
    sites={}
    for site in sorted({s for s,p in plots}):
        group=[sp for (s,p),sp in plots.items() if s==site]
        count=sum(sum(n in valid for n in sp)>=3 and
                  sum(n in valid for n in sp)/len(sp)>=.8 for sp in group)
        sites[site]={"original_plots":len(group),"provenance_eligible_plots":count,
                     "sown_taxa_unique":len(set().union(*group)) if group else 0,
                     "height_matched_taxa_unique":len(set().union(*group)&valid) if group else 0}
    return sites,sum(v["provenance_eligible_plots"] for v in sites.values()),sum(v["provenance_eligible_plots"]>=8 for v in sites.values())

def run(s_rows,c_rows):
    original,plots,source_meta=geometry(s_rows,c_rows)
    names=collections.defaultdict(set);nc=0
    for x in paged("species",cap=600000):
        nc+=1
        n=binomial(x.get("work_species"))
        if n in original and x.get("work_ID") is not None:
            names[n].add(str(x["work_ID"]))
    if nc!=N_SP:raise ValueError("Original GIFT 3.1 species source drift")
    unique={n:next(iter(ids)) for n,ids in names.items() if len(ids)==1}
    if len(unique)!=93:raise ValueError("Prior BIODEPTH 93 exact GIFT names changed")
    rev={work:n for n,work in unique.items()}
    if len(rev)!=len(unique):raise ValueError("Different original BIODEPTH species share a GIFT work ID")
    source_rows=0;traits=collections.defaultdict(list)
    for row in paged("traits",cap=500000,traitid=HEIGHT_ID,biasref=0,biasderiv=0):
        source_rows+=1
        work=str(row.get("work_ID") or "")
        if work in rev:traits[work].append(row)
    if source_rows!=N_HEIGHT:raise ValueError("Original GIFT 1.6.2 record count drift")
    ref_records=get("references",startat=0,limit=10000)
    ref_map={}
    repeat_ref_ids=collections.Counter()
    for r in ref_records:
        key=str(r.get("ref_ID") or "").strip()
        if not key:raise ValueError("Missing GIFT reference key")
        if key in ref_map:
            # Original reference table can repeat a bibliographic reference across
            # different taxon/region metadata rows. Only its identity string is
            # used for attribution; do not merge contradictory reference titles.
            if str(ref_map[key].get("ref_long") or "").strip()!=str(r.get("ref_long") or "").strip():
                raise ValueError("Conflicting bibliographic reference texts share ref_ID "+key)
            repeat_ref_ids[key]+=1
        else:
            ref_map[key]=r
    if len(ref_map)<700:raise ValueError("Original distinct reference bibliography truncated")
    source_fp=[]
    height=set();traceable=set();unresolved=set();direct=set();shared=set()
    by_reference=collections.Counter();nsource=collections.Counter();cv_data=[]
    extreme=collections.Counter()
    duplicate=[]
    for work,name in sorted(rev.items()):
        recs=traits.get(work,[])
        if len(recs)!=1:
            if len(recs)>1:duplicate.append(name)
            continue
        rec=recs[0];v=num(rec.get("trait_value"))
        if v is None:continue
        height.add(name)
        ids,wellformed=references(rec.get("references"))
        resolved=bool(wellformed and ids and all(k in ref_map for k in ids))
        if not resolved:unresolved.add(name)
        for k in ids:
            if k in ref_map:
                by_reference[k]+=1
                bib=str(ref_map[k].get("ref_long") or "")
                if DIRECT.search(bib):direct.add(name)
                if INDIRECT.search(bib):shared.add(name)
        try:
            n=int(float(rec.get("n")))
            nsource[str(n) if n<=8 else "9plus"]+=1
        except (ValueError,TypeError,OverflowError):nsource["missing_or_invalid"]+=1
        try:cv=float(rec.get("coeff_var"))
        except (ValueError,TypeError):cv=math.nan
        if math.isfinite(cv) and cv>=0:cv_data.append(cv)
        if v<.01:extreme["below_1cm"]+=1
        if v>10:extreme["above_10m"]+=1
        if v>50:extreme["above_50m"]+=1
        if resolved and name not in direct:traceable.add(name)
        source_fp.append([name,work,repr(v),str(rec.get("references")),str(rec.get("n")),str(rec.get("coeff_var"))])
    if len(height)!=88:raise ValueError("Original GIFT 88 height species no longer reproduced")
    sites0,plots0,nsite0=coverage(plots,height)
    if plots0!=174 or nsite0!=7:raise ValueError("Original 174 GIFT-available BIODEPTH plots changed")
    sites1,plots1,nsite1=coverage(plots,traceable)
    top=[]
    for ref,count in by_reference.most_common(20):
        long=str(ref_map[ref].get("ref_long") or "")
        top.append({"reference_id":ref,"original_BIODEPTH_species_cited":count,"citation":long[:250],
                    "potential_original_study_overlap":bool(DIRECT.search(long)),
                    "potential_database_overlap":bool(INDIRECT.search(long))})
    good=len(traceable)>=70 and plots1>=80 and nsite1>=4
    return {
      "version":"v0.1","status":"GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS" if good else "GIFT_HEIGHT_REFERENCE_PROVENANCE_HOLD",
      "original_BIODEPTH_species_roster":source_meta,
      "GIFT_original_species_rows":nc,"GIFT_original_height_aggregated_rows":source_rows,
      "GIFT_bibliography_source_rows":len(ref_records),
      "GIFT_bibliography_unique_ref_IDs":len(ref_map),
      "GIFT_ref_IDs_repeated_with_same_bibliography":dict(repeat_ref_ids),
      "GIFT_bibliography_content_sha256":hashlib.sha256(json.dumps(ref_records,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
      "GIFT_original_target_species_height_and_reference_fingerprint_sha256":hashlib.sha256(json.dumps(sorted(source_fp),separators=(",",":"),ensure_ascii=False).encode()).hexdigest(),
      "GIFT_metadata_trait_id":"1.6.2","height_unit":"m",
      "original_species_named":len(original),"original_taxa_exact_accepted_names":len(unique),
      "original_species_with_positive_aggregated_max_height":len(height),
      "original_species_with_full_references_and_no_explicit_original_BIODEPTH":len(traceable),
      "original_species_with_missing_or_invalid_reference_ids":len(unresolved),
      "original_species_with_explicit_original_BIODEPTH_citations":len(direct),
      "original_species_with_possible_other_trait_database_overlap":len(shared),
      "GIFT_source_n_number_distribution":dict(nsource),
      "GIFT_record_coefficient_variation_summary":{
         "n_finite":len(cv_data),"median":float(sorted(cv_data)[len(cv_data)//2]) if cv_data else None,
         "p90":float(sorted(cv_data)[min(int(len(cv_data)*.9),len(cv_data)-1)]) if cv_data else None},
      "GIFT_original_max_height_extremes":dict(extreme),
      "GIFT_target_aggregated_duplicate_workids_count":len(duplicate),
      "top_bibliographic_references":top,
      "all_height_eligible_original_plots":plots0,"all_height_eligible_original_sites":nsite0,
      "bibliography_eligible_original_plots":plots1,"bibliography_eligible_original_sites":nsite1,
      "site_coverage_unfiltered":sites0,"site_coverage_bibliography_qualified":sites1,
      "source_gate_thresholds":{"min_original_height_species_citations_traceable_and_no_explicit_BIODEPTH":70,
                  "min_original_plots_3_spp_and_80pct_coverage":80,
                  "min_sites_with_at_least_8_eligible_plots":4},
      "retrieval_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "no_biological_association_opened":True,
      "hard_nonclaims":["Citation traceability not independent biological measurement of site height",
          "Other TRY/BIEN trait-source overlap may remain","Source GIFT max species height aggregated from source maxima",
          "No within-site real measured height, FD or biomass association estimated",
          "Greece has no eligible plots in the prior 174-plot cohort",
          "Original BIODEPTH exact-richness high-support gate remains HOLD",
          "Original sPlotOpen GIFT BIEN family-by-trait rho source gate remains HOLD"]}
def fixture():
    assert references("123,456")[0]=={"123","456"}
    assert references("123")[1] and not references("bad ref")[1]
    assert binomial("Poa_pratensis")=="poa pratensis"
    return {"status":"GIFT_REFERENCE_FIXTURE_PASS","checks":3}
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species");parser.add_argument("--codes");parser.add_argument("--out")
    parser.add_argument("--self-test",action="store_true")
    a=parser.parse_args()
    if a.self_test:print(json.dumps(fixture()))
    else:
        if not all((a.species,a.codes,a.out)):parser.error("species codes out required")
        ans=run(source(a.species,"species"),source(a.codes,"codes"))
        path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(ans,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("GIFT_BIODEPTH_HEIGHT_PROVENANCE_AUDIT",json.dumps(
           {k:v for k,v in ans.items() if k not in ("top_bibliographic_references",
               "site_coverage_unfiltered","site_coverage_bibliography_qualified")},sort_keys=True))
        print("GIFT_BIODEPTH_HEIGHT_REFERENCE_SITES",json.dumps(ans["site_coverage_bibliography_qualified"],sort_keys=True))
        if ans["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS":raise SystemExit(2)
