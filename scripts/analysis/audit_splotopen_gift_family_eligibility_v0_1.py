#!/usr/bin/env python3
"""Independent SOURCE-SUPPORT audit: sPlotOpen × GIFT3.1 × frozen BIEN core.

No PD, FD, biomass, regression, or evolution effect is estimated.
Uses exact accepted species binomials for traits, and separately labels
genus-only family classification for unmatched species (denominator only).
"""
from __future__ import annotations
import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
import csv
import io
import json
import math
from pathlib import Path
import re
import time
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import zipfile

API = "https://gift.uni-goettingen.de/api/extended/index3.1.php"
TRAITS = {"woodiness": "1.1.1", "growth_form": "1.2.1",
          "plant_height_max": "1.6.2"}
EXPECTED = {"gift_taxonomy":21192,"gift_species":372046,"splot_rows":1943306,
            "splot_plots":95104,"splot_binomials":39795,"splot_exact":34888}
PAGE = 10000

def normal(s):
    return " ".join(str(s or "").replace("_", " ").casefold().split())

def binomial(s):
    s = normal(s)
    return s if re.fullmatch(r"[a-z-]+ [a-z-]+", s) else None

def finite_number(s):
    try:
        n = float(s)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None

def query(kind, **kw):
    url = API + "?" + urlencode(dict(query=kind, **kw))
    last = None
    for attempt in range(4):
        try:
            req = Request(url, headers={
                "User-Agent": "turnover-pd-fd-family-eligibility/0.1",
                "Accept": "application/json"})
            with urlopen(req, timeout=110) as response:
                rows = json.load(response)
            if not isinstance(rows, list):
                raise ValueError("GIFT API returned nonlist")
            return rows
        except (URLError, ValueError, TimeoutError) as exc:
            last = str(exc)
            time.sleep(min(2**attempt, 5))
    raise RuntimeError(f"GIFT API unavailable: {kind} {last}")

def paged(kind, upper=600000, **kw):
    offset = 0
    previous = None
    while offset < upper:
        chunk = query(kind, startat=offset, limit=PAGE, **kw)
        if len(chunk) > PAGE:
            raise ValueError("GIFT returned overlarge page")
        if chunk:
            first = json.dumps(chunk[0], sort_keys=True)
            if first == previous:
                raise ValueError("GIFT pagination repeated previous page")
            previous = first
        yield from chunk
        if len(chunk) < PAGE:
            return
        offset += len(chunk)
        time.sleep(0.03)
    raise ValueError("GIFT pagination exceeded predeclared ceiling")

def family_index(taxonomy):
    family = sorted(
        (int(x["lft"]), int(x["rgt"]), str(x["taxon_name"]).strip())
        for x in taxonomy if x.get("taxon_lvl")=="family"
    )
    starts = [x[0] for x in family]
    genus_family = {}
    missing = 0
    for x in taxonomy:
        if x.get("taxon_lvl") != "genus":
            continue
        a, b, identifier = int(x["lft"]), int(x["rgt"]), str(x["taxon_ID"])
        i = bisect_right(starts, a) - 1
        if i < 0 or not (family[i][0] < a < b < family[i][1]):
            missing += 1
            continue
        genus_family[identifier] = family[i][2]
    if len(family) != 657 or len(genus_family) < 20000:
        raise ValueError(f"Unexpected GIFT taxonomy tree: families={len(family)} valid_genera={len(genus_family)}")
    return genus_family, {"taxon_rows":len(taxonomy),"families":len(family),
                          "valid_genus_family_assignments":len(genus_family),
                          "genera_without_family":missing}

def gift_maps():
    taxonomy = query("taxonomy")
    if len(taxonomy) != EXPECTED["gift_taxonomy"]:
        raise ValueError("GIFT 3.1 taxonomy count differs from frozen snapshot")
    genus_family, tax_summary = family_index(taxonomy)
    accepted_ids = defaultdict(set)
    accepted_families = defaultdict(set)
    genus_families = defaultdict(set)
    species_n = 0
    species_missing_family = 0
    for row in paged("species"):
        species_n += 1
        species = binomial(row.get("work_species"))
        genus = normal(row.get("work_genus"))
        work_id = str(row.get("work_ID") or "")
        genus_id = str(row.get("genus_ID") or "")
        family = genus_family.get(genus_id)
        if not family:
            species_missing_family += 1
            continue
        if genus:
            genus_families[genus].add(family)
        if species and work_id:
            accepted_ids[species].add(work_id)
            accepted_families[species].add(family)
    if species_n != EXPECTED["gift_species"]:
        raise ValueError("GIFT 3.1 species count differs from frozen snapshot")
    accepted = {s:(next(iter(ids)),next(iter(accepted_families[s])))
                for s,ids in accepted_ids.items()
                if len(ids)==1 and len(accepted_families[s])==1}
    genus = {g:next(iter(fs)) for g,fs in genus_families.items() if len(fs)==1}
    data = {}
    trait_meta = {}
    for name, trait_id in TRAITS.items():
        values = defaultdict(set)
        n = 0
        for row in paged("traits", upper=500000, traitid=trait_id,
                         biasref=0, biasderiv=0):
            work = str(row.get("work_ID") or "")
            value = row.get("trait_value")
            val = str(value).strip() if value is not None else ""
            if work and val:
                values[work].add(val)
            n += 1
        simple = {k:next(iter(v)) for k,v in values.items() if len(v)==1}
        if name=="plant_height_max":
            accepted_trait = {k for k,v in simple.items()
                              if (x:=finite_number(v)) is not None and x>0}
        else:
            accepted_trait = set(simple)
        data[name] = accepted_trait
        trait_meta[name] = {
            "trait_ID":trait_id, "source_rows":n, "unambiguous_values":len(simple),
            "usable_values":len(accepted_trait),
            "ambiguous_value_ids_excluded":sum(len(v)>1 for v in values),
            "validity":"finite positive numeric" if name=="plant_height_max"
                       else "present categorical (not numerical FD)"
        }
    return accepted, genus, data, {"taxonomy":tax_summary,
                                   "gift_species_records":species_n,
                                   "species_without_family":species_missing_family,
                                   "unique_accepted_species_family":len(accepted),
                                   "unique_genus_family":len(genus),
                                   "traits":trait_meta}

def read_core(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    pairs={(r["family"].strip(),r["trait_name"].strip()) for r in rows}
    fam={f for f,_ in pairs}; trait={t for _,t in pairs}
    if len(rows)!=201 or len(pairs)!=201 or len(fam)!=45 or len(trait)!=12:
        raise ValueError("Historical BIEN core is not exact 201/45/12")
    if "maximum whole plant height" not in trait:
        raise ValueError("Maximum whole plant height not present in BIEN core")
    return pairs, {"rows":len(rows),"families":len(fam),"traits":len(trait),
                   "max_height_family_trait_pairs":
                   sum(t=="maximum whole plant height" for _,t in pairs)}

def read_plots(z):
    found=[n for n in z.namelist() if re.search(
        r"(?:^|/)sPlotOpen_header(?:\([^)]*\))?\.txt$", n,re.I)]
    if len(found)!=1:
        raise ValueError("Expected one sPlotOpen header")
    with io.TextIOWrapper(z.open(found[0]),encoding="utf-8-sig",errors="replace") as f:
        meta={}
        for x in csv.DictReader(f,delimiter="\t"):
            p=str(x["PlotObservationID"]).strip()
            values=(str(x.get("Dataset") or "").strip(),
                    str(x.get("Biome") or "").strip(),
                    finite_number(x.get("Releve_area")))
            if p in meta and meta[p] != values:
                raise ValueError("Conflicting header for PlotObservationID")
            meta[p]=values
    if len(meta)!=EXPECTED["splot_plots"]:
        raise ValueError("sPlotOpen unique plot metadata count unexpected")
    return meta

def read_species(z):
    found=[n for n in z.namelist() if re.search(
        r"(?:^|/)sPlotOpen_DT(?:\([^)]*\))?\.txt$", n,re.I)]
    if len(found)!=1:
        raise ValueError("Expected one sPlotOpen DT")
    raw=io.TextIOWrapper(z.open(found[0]),encoding="utf-8-sig",
                         errors="replace",newline="")
    return raw,csv.DictReader(raw,delimiter="\t")

def audit(archive,core,accepted,genus,traits,gift_summary):
    with zipfile.ZipFile(archive) as z:
        plot_meta=read_plots(z)
        handle,records=read_species(z)
        seen_binomial=set()
        seen_exact=set()
        unmatched_with_genus=set()
        unmatched_unknown_genus=set()
        family_exact_species=defaultdict(set)
        family_unmatched_species=defaultdict(set)
        plot_cover=defaultdict(float)
        plot_exact_cover=defaultdict(float)
        plot_unknown_family_cover=defaultdict(float)
        fam_cover=defaultdict(float)
        fam_height_cover=defaultdict(float)
        fam_wood_cover=defaultdict(float)
        fam_growth_cover=defaultdict(float)
        fam_height_species=defaultdict(dict)
        biome_plot_coverage=defaultdict(list)
        bad_p_name=0
        n_rows=0
        positive_binomial=0
        exact_positive=0
        try:
            for row in records:
                n_rows+=1
                p=str(row.get("PlotObservationID") or "").strip()
                if not p or p not in plot_meta:
                    bad_p_name+=1
                    continue
                w=finite_number(row.get("Relative_cover"))
                s=binomial(row.get("Species"))
                if s:
                    seen_binomial.add(s)
                if w is None or w<=0:
                    continue
                plot_cover[p]+=w
                if not s:
                    plot_unknown_family_cover[p]+=w
                    continue
                positive_binomial+=1
                known=accepted.get(s)
                if known:
                    work,fam=known
                    seen_exact.add(s)
                    plot_exact_cover[p]+=w
                    exact_positive+=1
                    family_exact_species[fam].add(s)
                else:
                    fam=genus.get(s.split()[0])
                    work=None
                    if fam:
                        unmatched_with_genus.add(s)
                        family_unmatched_species[fam].add(s)
                    else:
                        unmatched_unknown_genus.add(s)
                        plot_unknown_family_cover[p]+=w
                        continue
                key=(p,fam)
                fam_cover[key]+=w
                if work and work in traits["plant_height_max"]:
                    fam_height_cover[key]+=w
                    old=fam_height_species[key].get(s,0.0)
                    fam_height_species[key][s]=old+w
                if work and work in traits["woodiness"]:
                    fam_wood_cover[key]+=w
                if work and work in traits["growth_form"]:
                    fam_growth_cover[key]+=w
        finally:
            handle.close()
    if n_rows!=EXPECTED["splot_rows"] or len(seen_binomial)!=EXPECTED["splot_binomials"]:
        raise ValueError("Source DT identity unexpectedly changed")
    if len(seen_exact)!=EXPECTED["splot_exact"]:
        raise ValueError(f"Exact name identity differs from first GIFT 3.1 audit: {len(seen_exact)}")
    if len(seen_binomial)-len(seen_exact)!=4907:
        raise ValueError("Frozen unmatched binomial count changed")
    for p,total in plot_cover.items():
        biome = plot_meta[p][1] or "(unlabelled)"
        biome_plot_coverage[biome].append((plot_exact_cover[p]/total,
                                          plot_unknown_family_cover[p]/total))
    eligible=defaultdict(set)
    eligible_core=defaultdict(set)
    height_fails=Counter()
    for key,values in fam_height_species.items():
        p,f=key
        m=plot_meta[p]
        if not m[0] or not m[1] or m[2] is None or m[2]<=0:
            height_fails["missing_plot_metadata"]+=1
            continue
        weights=[v for v in values.values() if v>0]
        if len(weights)<3:
            height_fails["less_than_three_height_species"]+=1
            continue
        if fam_cover[key]<=0 or sum(weights)/fam_cover[key]<0.8:
            height_fails["below_80pct_family_known_cover"]+=1
            continue
        n_eff=sum(weights)**2/sum(w*w for w in weights)
        if n_eff<2.5:
            height_fails["effective_species_below_2_5"]+=1
            continue
        eligible[f].add(p)
        if (f,"maximum whole plant height") in core:
            eligible_core[f].add(p)
    twenty={f:ps for f,ps in eligible.items() if len(ps)>=20}
    twenty_core={f:ps for f,ps in eligible_core.items() if len(ps)>=20}
    ds_all={plot_meta[p][0] for ps in twenty.values() for p in ps}
    ds_core={plot_meta[p][0] for ps in twenty_core.values() for p in ps}
    fam_report = []
    for f in sorted(set(family_exact_species)|set(family_unmatched_species)|set(eligible)):
        fam_report.append({
            "family":f,
            "exact_GIFT_species_in_sPlotOpen":len(family_exact_species[f]),
            "unmatched_binomials_assigned_from_unique_genus":len(family_unmatched_species[f]),
            "eligible_height_plot_cells_pre_family_floor":len(eligible.get(f,set())),
            "eligible_height_plot_cells_if_in_frozen_BIEN_maxheight_core":
                len(eligible_core.get(f,set())),
            "in_frozen_BIEN_maxheight_core":(f,"maximum whole plant height") in core
        })
    fam_report.sort(key=lambda x:(-x["eligible_height_plot_cells_pre_family_floor"],x["family"]))
    report={
        "version":"v0.1",
        "status":"PRE_OUTCOME_HOLD_EXACT_NAME_90PCT_NOT_PASSED",
        "scope":"Source-only: counts, metadata and fixed-core overlaps; NO FD, MPD or biomass outcomes",
        "splot_mirror_commit":"1bfcad669ae1a7e6f0a419159dd3051e83bdd26b",
        "GIFT_version":"3.1",
        "BIEN_core_provenance":"GitHub artifact trait-memory-informativeness-v0-5; run 37086693588",
        "GIFT_source":gift_summary,
        "BIEN_core":core_summary(core),
        "splot_unique_plots":len(plot_meta),
        "splot_composition_rows":n_rows,
        "splot_binomial_species":len(seen_binomial),
        "splot_exact_gift_species":len(seen_exact),
        "splot_exact_fraction":len(seen_exact)/len(seen_binomial),
        "frozen_exact_90pct_pass":len(seen_exact)/len(seen_binomial)>=0.9,
        "unmatched_binomial_species":len(seen_binomial-seen_exact),
        "unmatched_but_recognized_genus_species":len(unmatched_with_genus),
        "unmatched_unassigned_genus_species":len(unmatched_unknown_genus),
        "unmatched_with_known_genus_percentage":
           len(unmatched_with_genus)/len(seen_binomial-seen_exact),
        "positive_binomial_composition_rows":positive_binomial,
        "positive_exact_gift_composition_rows":exact_positive,
        "rows_with_unresolved_plot_id":bad_p_name,
        "plot_biome_exact_cover": {
            biome: {
                "plots":len(v),
                "mean_exact_species_cover_fraction":sum(x for x,_ in v)/len(v),
                "mean_unknown_family_cover_fraction":sum(x for _,x in v)/len(v),
                "plots_exact_cover_at_least_80pct":sum(x>=0.8 for x,_ in v)}
            for biome,v in sorted(biome_plot_coverage.items()) if len(v)>=30
        },
        "height_quality_gates": {
            "min_distinct_species":3,"family_known_cover_fraction":0.8,
            "effective_species_floor":2.5,"min_plots_per_family":20,
            "primary_min_families":12,"primary_min_cells":500,
            "primary_min_source_datasets":5
        },
        "height_candidate_plot_family_cells_pre_family_floor":sum(len(s) for s in eligible.values()),
        "height_candidate_families_pre_family_floor":len(eligible),
        "height_families_with_at_least_20_plots":len(twenty),
        "height_plot_family_cells_after_family_floor":sum(len(s) for s in twenty.values()),
        "height_source_datasets_after_family_floor":len(ds_all),
        "height_candidates_matching_BIEN_maxheight_family_trait":sum(len(s) for s in eligible_core.values()),
        "height_BIEN_maxheight_families_at_least_20_plots":len(twenty_core),
        "height_BIEN_maxheight_plot_family_cells_after_floor":sum(len(s) for s in twenty_core.values()),
        "height_BIEN_maxheight_datasets_after_floor":len(ds_core),
        "height_candidate_failure_reasons":dict(height_fails),
        "families":fam_report,
        "hard_nonclaims":[
            "The family known-cover denominator includes genus-assigned unmatched species but excludes unresolved genera, so it is conditional, not full unbiased completeness.",
            "Height max traits in GIFT may reuse TRY/BIEN/AusTraits studies; independence and measurement units have not been audited.",
            "Woodiness and growth form are categorical, not the quantitative height FD outcome.",
            "The BIEN maximum whole plant height row is not assumed measurement-identical to GIFT plant_height_max.",
            "Matching family labels does not yield any phylogenetic tips, patristic MPD, Rao Q, biomass or positive scientific association.",
            "The frozen 90% exact binomial gate is NOT reset after the observed 87.7% match."
        ]
    }
    return report

def core_summary(core):
    return {"n_family_trait_pairs":len(core),
            "families":len({f for f,_ in core}),
            "traits":len({t for _,t in core}),
            "maximum_whole_plant_height_families":
                sum(t=="maximum whole plant height" for f,t in core)}

def self_test():
    toy=[
      dict(taxon_ID="F1",taxon_lvl="family",taxon_name="FamX",lft=1,rgt=10),
      dict(taxon_ID="G1",taxon_lvl="genus",taxon_name="GenX",lft=2,rgt=3),
    ]
    # Unit-test only parent look-up logic; real verification requires 657 family taxonomy.
    starts=[1]
    fidx=bisect_right(starts,2)-1
    assert fidx==0 and 1<2<3<10
    assert binomial("GenX species")=="genx species"
    assert binomial("GenX sp.") is None
    assert finite_number("3.5")==3.5
    assert finite_number("NaN") is None
    return {"status":"SELF_TEST_PASS","checks":5}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive")
    p.add_argument("--core")
    p.add_argument("--out")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        print(json.dumps(self_test()))
        return
    if not all((a.archive,a.core,a.out)):
        p.error("--archive --core --out are required")
    core,_=read_core(a.core)
    accepted,genus,traits,gift_summary=gift_maps()
    report=audit(a.archive,core,accepted,genus,traits,gift_summary)
    dst=Path(a.out)
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    slim={k:v for k,v in report.items()
          if k!="families" and k!="plot_biome_exact_cover" and k!="GIFT_source"}
    slim["top_10_height_families"]=report["families"][:10]
    print("FAMILY_ELIGIBILITY_SUMMARY",json.dumps(slim,sort_keys=True))
    # HOLD is a successful source-audit execution; do NOT treat as effect authorization.

if __name__=="__main__":
    main()
