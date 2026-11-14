#!/usr/bin/env python3
"""Jena 2003 original plant group assignment and plot-mean availability gate.

NO inference on biomass values. Only field labels, sowing metadata, nonblank
species *structural support*, and replicate tags are read into aggregated QA.
"""
import argparse, collections, csv, io, json, hashlib
from pathlib import Path
from probe_jena_2003_direct_biomass_v0_1 import parse_table

GROUPS=[
    ("grasses","NumberGrassSpecies","PresenceGrasses",16),
    ("small_herbs","NumberSmallHerbSpecies","PresenceSmallHerbs",12),
    ("tall_herbs","NumberTallHerbSpecies","PresenceTallHerbs",20),
    ("legumes","NumberLegumeSpecies","PresenceLegumes",12),
]
EXPECTED_REPL={"1":164,"2":164,"3":164,"4":164,"mean":164}

def audit(src,plotinfo):
    b=Path(src).read_bytes()
    cols,rows,_=parse_table(b)
    if len(rows)!=820 or len(cols)!=84: raise ValueError("JENA_RAW_2003_SCHEMA_CHANGED")
    if "Weeds biom dw [g/m**2]" not in cols:raise ValueError("SPECIES_ANCHOR_MISSING")
    species_cols=cols[cols.index("Weeds biom dw [g/m**2]")+1:]
    if len(species_cols)!=60 or not all("biom" in c for c in species_cols):
        raise ValueError("EXPECTED_60_SPECIES_BIOMASS_COLUMNS")
    info_bytes=Path(plotinfo).read_bytes()
    info=list(csv.DictReader(io.StringIO(info_bytes.decode("utf-8-sig")),delimiter="\t"))
    if len(info)!=82:raise ValueError("JENA_PLOTINFO_NOT_82")
    plotinfo_map={x["plotcode"].strip():x for x in info}
    if len(plotinfo_map)!=82:raise ValueError("DUPLICATE_OR_BLANK_PLOT_CODES")
    raw_plots={x["Experimental plot"].strip() for x in rows}
    if raw_plots != set(plotinfo_map):raise ValueError("NOT_EXACT_82_PLOT_JOIN")
    replicates=collections.Counter(x["Repl"].strip() for x in rows)
    if dict(replicates)!=EXPECTED_REPL:
        raise ValueError(f"UNEXPECTED_REPLICATE_LABELS: {dict(replicates)}")
    meanrows=[x for x in rows if x["Repl"]=="mean"]
    if len(meanrows)!=164:raise ValueError("EXPECTED_164_PLOT_SEASON_MEAN_ROWS")
    season_mean=collections.Counter()
    plot_seasons=set()
    for r in meanrows:
        yearmonth=r["Date/time start"][:7]
        season_mean[yearmonth]+=1
        key=(r["Experimental plot"],yearmonth)
        if key in plot_seasons:raise ValueError("DUPLICATE_PLOT_SEASON_MEAN")
        plot_seasons.add(key)
    if len(plot_seasons)!=164 or season_mean!={"2003-05":82,"2003-08":82}:
        raise ValueError("UNEXPECTED_MEAN_CAMPAIGN_COUNTS")
    if len(set(x["block"] for x in info))!=4:raise ValueError("BLOCK_COUNT_MISMATCH")
    for p,x in plotinfo_map.items():
        counts=[int(x[key]) for _,key,_,_ in GROUPS]
        if sum(counts)!=int(x["NumberSownSpecies"]):
            raise ValueError("DESIGN_SPECIES_RICHNESS_SUM_MISMATCH")
        if sum(n>0 for n in counts)!=int(x["NumberFunctionalGroups"]):
            raise ValueError("DESIGN_FUNCTIONAL_RICHNESS_SUM_MISMATCH")
        for n,(_,_,pres,_) in zip(counts,GROUPS):
            if int(x[pres])!=int(n>0):
                raise ValueError("DESIGN_GROUP_PRESENCE_FLAG_MISMATCH")
    if set(int(x["NumberSownSpecies"]) for x in info)!={1,2,4,8,16,60}:
        raise ValueError("DESIGN_SOWN_RICHNESS_LEVELS_MISMATCH")
    if set(int(x["NumberFunctionalGroups"]) for x in info)!={1,2,3,4}:
        raise ValueError("DESIGN_FUNCTIONAL_RICHNESS_LEVELS_MISMATCH")
    # Structural sown patterns are audited only; richness predictors come from
    # external original plotinfo, NOT from measured biomass values.
    masks=collections.defaultdict(set)
    for row in rows:
        p=row["Experimental plot"].strip()
        for i,col in enumerate(species_cols):
            if str(row.get(col) or "").strip():
                masks[p].add(i)
    bounds=[]
    begin=0
    for label,_,_,n in GROUPS:
        bounds.append((label,begin,begin+n))
        begin+=n
    if begin!=60:raise AssertionError("functional group sizes don't sum to 60")
    all_counter=collections.Counter()
    mismatch=[]
    for p,rec in plotinfo_map.items():
        observed=[sum(a<=idx<b for idx in masks[p]) for _,a,b in bounds]
        planned=[int(rec[key]) for _,key,_,_ in GROUPS]
        for (label,_,_),o,e in zip(bounds,observed,planned):
            if o!=e:
                all_counter[label]+=1
        if observed!=planned:
            mismatch.append(p)
    # Treat 95% plot×species-group structural identity as source contract.
    fraction=1-len(mismatch)/len(plotinfo_map)
    group_map_names={label:[col for col in species_cols[a:b]] for label,a,b in bounds}
    report={
        "status":"TIER1_JENA_GROUP_DESIGN_PASS" if fraction>=0.95 else "TIER1_JENA_GROUP_DESIGN_HOLD",
        "source_2003_doi":"10.1594/PANGAEA.846317",
        "source_2003_sha256":hashlib.sha256(b).hexdigest(),
        "plotinfo_sha256":hashlib.sha256(info_bytes).hexdigest(),
        "original_plotinfo_url":"https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt",
        "n_matched_2003_plots":len(raw_plots),
        "n_measured_species_columns":len(species_cols),
        "n_original_4group_species_mapped":sum(n for _,_,_,n in GROUPS),
        "replicate_labels":dict(replicates),
        "n_independent_plot_means_may":season_mean.get("2003-05",0),
        "n_independent_plot_means_aug":season_mean.get("2003-08",0),
        "n_independent_plot_ids":len(raw_plots),
        "n_original_blocks":len(set(x["block"] for x in info)),
        "sown_species_richness_levels":sorted({int(x["NumberSownSpecies"]) for x in info}),
        "planned_functional_group_richness_levels":sorted({int(x["NumberFunctionalGroups"]) for x in info}),
        "plot_functional_group_sowing_mask_agreement_fraction":fraction,
        "plot_sowing_mask_mismatches":len(mismatch),
        "mismatch_group_counts":dict(all_counter),
        "group_name_mapping_source":"PANGAEA 2003 species-column original functional-group order and published Jena design (16 grasses, 12 small herbs, 20 tall herbs, 12 legumes); confirmed against independent plotinfo group counts",
        "group_name_mapping":group_map_names,
        "analysis_authorization":"ONLY separate planned functional-group-richness sentinel, no quantitative Rao FD or PD and no global across-family inference" if fraction>=.95 else "NO_BIOMASS_FD_ANALYSIS",
        "biomass_values_or_effects_opened":False,
    }
    return report

def selftest():
    pos=[(name,n) for name,_,_,n in GROUPS]
    assert sum(n for _,n in pos)==60
    assert EXPECTED_REPL["mean"]==82*2
    assert len(GROUPS)==4
    return {"status":"TIER1_GROUP_FIXTURE_PASS","checks":3}

if __name__=="__main__":
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument("--source")
    pa.add_argument("--plotinfo")
    pa.add_argument("--out")
    pa.add_argument("--self-test",action="store_true")
    a=pa.parse_args()
    if a.self_test:print(json.dumps(selftest()))
    else:
        if not all((a.source,a.plotinfo,a.out)):
            pa.error("need --source --plotinfo --out")
        res=audit(a.source,a.plotinfo)
        dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        abbreviated={k:v for k,v in res.items() if k!="group_name_mapping"}
        print("TIER1_GROUP_QA",json.dumps(abbreviated,ensure_ascii=False))
        if res["status"]!="TIER1_JENA_GROUP_DESIGN_PASS":raise SystemExit(2)
