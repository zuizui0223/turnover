#!/usr/bin/env python3
"""Source-only height-trait support for 103 original BIODEPTH taxa via GIFT v3.1.

Original 2010 Species roster defines SOWN community, regardless of harvested
biomass. Never use same-year species biomass to weight explanatory traits.
Do not fit biomass effects or infer evolutionary rho in this source gate.
"""
from __future__ import annotations
import argparse,collections,csv,datetime,hashlib,io,json,math,re,time
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path

API="https://gift.uni-goettingen.de/api/extended/index3.1.php"
SOURCE_SHA={
"species":"ebe677c639ef4603bc1ed50d49e7440588683e7696be230c0cbfff7d6b22b816",
"codes":"02ad483f727d4d10c10be7e7fe83e9e66c42803d6d08956d9397001dbf32f11b",
}
PAGE=10000
HEIGHT_ID="1.6.2"
def normal(s):return " ".join(str(s or "").replace("_"," ").casefold().strip().split())
def binomial(s):
    v=normal(s)
    return v if re.fullmatch(r"[a-z-]+ [a-z-]+",v) else None
def num(s):
    try:
        v=float(s)
        return v if math.isfinite(v) and v>0 else None
    except (TypeError,ValueError):return None
def source(path,label):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA[label]:
        raise ValueError("Original BIODEPTH 2010 SHA256 changed "+label)
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")),delimiter="\t")
    rows=list(reader)
    if any(None in r for r in rows):raise ValueError("Original source malformed columns")
    return rows
def get(kind,**params):
    uri=API+"?"+urlencode({"query":kind,**params})
    for attempt in range(3):
        try:
            req=Request(uri,headers={"User-Agent":"turnover-BIODEPTH-GIFT-trait-eligibility/0.1",
                                    "Accept":"application/json"})
            with urlopen(req,timeout=110) as r:
                j=json.load(r)
            if not isinstance(j,list):raise ValueError("GIFT response not list")
            if len(j)>PAGE:raise ValueError("GIFT page length above pinned cap")
            return j
        except (OSError,ValueError) as exc:
            if attempt==2:raise RuntimeError("GIFT SOURCE ACCESS HOLD "+str(exc)) from exc
            time.sleep(2**attempt)
def paged(kind,cap=600000,**params):
    at=0
    seen=set()
    for idx in range(90):
        rows=get(kind,startat=at,limit=PAGE,**params)
        if rows:
            head=hashlib.sha256(json.dumps(rows[0],sort_keys=True).encode()).hexdigest()
            if head in seen:raise ValueError("GIFT source repeated page")
            seen.add(head)
        yield from rows
        if len(rows)<PAGE:return
        at+=len(rows)
        if at>=cap:raise ValueError("GIFT source too large for pinned paging cap")
        time.sleep(.05)
    raise ValueError("GIFT source >90 pages")
def geometry(s_rows,c_rows):
    original_name={}
    for r in c_rows:
        k=str(r["speciescode"]).strip()
        name=binomial(r["genus"]+" "+r["species"])
        if not name:raise ValueError("Nonbinomial author Linnaean label in original 2010 source")
        if k in original_name:raise ValueError("Original 2010 ecotype code duplicate")
        original_name[k]=name
    if len(original_name)!=186 or len(set(original_name.values()))!=103:
        raise ValueError("Original 2010 186 ecotype/103 taxa source geometry changed")
    site_plot=collections.defaultdict(set)
    year2=collections.Counter()
    plot_site={}
    for r in s_rows:
        code=str(r["species"]).strip()
        p=str(r["plot"]).strip()
        year=int(r["year"])
        site=str(r["site"]).strip()
        if code not in original_name or year not in (1,2,3):raise ValueError("Original 2010 species code or year invalid")
        year2[year]+=1
        if year!=1:continue
        site_plot[(site,p)].add(original_name[code])
        if p in plot_site and plot_site[p]!=site:raise ValueError("Original plot key crosses field sites")
        plot_site[p]=site
    if len(s_rows)!=5802 or len(site_plot)!=480 or len(plot_site)!=480 or len({s for s,p in site_plot})!=8 or year2!={1:1934,2:1934,3:1934}:
        raise ValueError("Original planted species source population is not 1934×3 across 480 plots")
    if sum(map(len,site_plot.values()))!=1934:
        raise ValueError("Original 2010 sown species occurrence population changed")
    return set(original_name.values()),site_plot,{"n_original_ecotypes":len(original_name),
      "n_original_sown_plant_species_names":len(set(original_name.values())),
      "n_original_plots":len(site_plot),"n_orig_plant_occurrences":1934,
      "source_rows_each_year":dict(year2)}
def audit(s_rows,c_rows):
    names,site_plot,geometry_meta=geometry(s_rows,c_rows)
    workIDs=collections.defaultdict(set)
    gift_rows=0
    for r in paged("species",cap=600000):
        gift_rows+=1
        name=binomial(r.get("work_species"))
        if name in names:
            id=str(r.get("work_ID") or "").strip()
            if id:workIDs[name].add(id)
    if gift_rows<300000:
        raise ValueError("GIFT accepted species source unexpectedly incomplete")
    name_to_id={k:next(iter(v)) for k,v in workIDs.items() if len(v)==1}
    target_ids=set(name_to_id.values())
    values=collections.defaultdict(set)
    ntrait=0
    all_valid=collections.defaultdict(set)
    relevant=0
    for r in paged("traits",cap=500000,traitid=HEIGHT_ID,biasref=0,biasderiv=0):
        ntrait+=1
        workID=str(r.get("work_ID") or "").strip()
        if workID not in target_ids:continue
        val=num(r.get("trait_value"))
        if val is not None:
            values[workID].add(val);all_valid[workID].add(val)
            relevant+=1
    height={w for w,v in values.items() if len(v)==1}
    anyheight={w for w,v in values.items() if len(v)>=1}
    trait_names={n for n,w in name_to_id.items() if w in height}
    alltrait_names={n for n,w in name_to_id.items() if w in anyheight}
    siteinfo={}
    nqual=0
    for site in sorted({s for s,p in site_plot}):
        plots={p:species for (ss,p),species in site_plot.items() if ss==site}
        eligible=[]
        site_sown={x for s in plots.values() for x in s}
        counts=collections.Counter()
        for p,s in plots.items():
            n=sum(x in trait_names for x in s)
            fraction=n/len(s)
            counts[len(s)]+=1
            if n>=3 and fraction>=.8:
                eligible.append(p)
        if len(eligible)>=8:nqual+=1
        siteinfo[site]={
          "n_original_plots":len(plots),
          "n_unique_original_sown_species":len(site_sown),
          "n_species_exact_GIFT_accepted_name":len(site_sown & set(name_to_id)),
          "n_species_unambiguous_GIFT_height":len(site_sown & trait_names),
          "n_original_plots_3plus_covered_species_atleast80pct":len(eligible),
          "planted_richness_plot_distribution":dict(sorted(counts.items()))
        }
    nplots=sum(v["n_original_plots_3plus_covered_species_atleast80pct"] for v in siteinfo.values())
    ispass=(len(name_to_id)>=80 and len(trait_names)>=55 and nqual>=4 and nplots>=60)
    result={
      "version":"v0.1",
      "status":"BIODEPTH_GIFT_HEIGHT_SOURCE_FEASIBILITY_PASS" if ispass else "BIODEPTH_GIFT_HEIGHT_SOURCE_FEASIBILITY_HOLD",
      "original_biodepth_species_source":geometry_meta,
      "GIFT_v3_1_versioned_API":API,
      "GIFT_accepted_species_source_records":gift_rows,
      "GIFT_trait_ID":HEIGHT_ID,
      "GIFT_original_trait_source_rows":ntrait,
      "n_original_taxa":len(names),
      "n_exact_accepted_GIFT_taxa_with_unique_work_ID":len(name_to_id),
      "n_original_taxa_unambiguous_finite_positive_max_height":len(trait_names),
      "n_original_taxa_any_positive_max_height_even_multisource":len(alltrait_names),
      "n_GIFT_workIDs_with_multiple_different_positive_height_values":sum(len(v)>1 for v in values.values()),
      "n_original_taxa_ambiguous_GIFT_work_ID":sum(len(x)>1 for x in workIDs.values()),
      "n_original_taxa_without_exact_unique_GIFT_match":len(names-set(name_to_id)),
      "n_original_taxa_without_valid_unambiguous_GIFT_height":len(names-trait_names),
      "original_taxa_exact_match_missing_names":sorted(names-set(name_to_id)),
      "original_taxa_height_unavailable_names":sorted(names-trait_names),
      "n_original_plots_height_eligible":nplots,
      "n_sites_with_8plus_height_eligible_plots":nqual,
      "source_eligibility_frozen_thresholds":{
        "min_exact_GIFT_accepted_names":80,
        "min_original_taxa_with_unambiguous_max_height":55,
        "min_sites_with_8_height_eligible_plots":4,
        "min_original_height_eligible_plots_total":60,
        "per_plot_min_original_sown_trait_species":3,
        "per_plot_min_fraction_sown_trait_covered":0.8},
      "site_coverage":siteinfo,
      "GIFT_source_queried_at_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "biology":"No functional diversity, biomass association, phylogenetic rho, site environmental moderation or quantitative trait effects calculated.",
      "hard_nonclaims":[
        "GIFT v3.1 source is live and only versioned, not content-immutable",
        "Accepted-name exact match excludes synonyms and unresolved original ecotype taxa",
        "Multiple legitimate height measurements conservatively excluded for lower bound",
        "External GIFT trait data source/work provenance and units are not independently audited",
        "One-axis height coverage is not multi-axis plant functional diversity",
        "Source 2010 species roster is SOWN plant community, not observed biomass-weighted realized composition",
        "Original 6-site BIODEPTH main support gate remains HOLD; BIEN/sPlotOpen original source gate remains HOLD"]
    }
    return result
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--species");ap.add_argument("--codes");ap.add_argument("--out");ap.add_argument("--self-test",action="store_true")
    a=ap.parse_args()
    if a.self_test:
        # Only local scalar normalization fixture; raw study geometry requires actual 5802 source rows.
        assert binomial("Poa_pratensis")=="poa pratensis"
        assert binomial("Bromus hordeaceus subsp.") is None
        assert num("0") is None and num("10.4")==10.4
        print(json.dumps({"status":"TRAIT_SOURCE_NORMALIZER_PASS","checks":3}))
    else:
        if not all((a.species,a.codes,a.out)):ap.error("--species --codes --out required")
        r=audit(source(a.species,"species"),source(a.codes,"codes"))
        f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
        print("BIODEPTH_103TAXA_GIFT_HEIGHT_COVERAGE",json.dumps(
          {k:v for k,v in r.items() if k not in ("site_coverage","original_taxa_exact_match_missing_names","original_taxa_height_unavailable_names")},sort_keys=True))
        print("BIODEPTH_103TAXA_GIFT_SITE",json.dumps(r["site_coverage"],sort_keys=True))
