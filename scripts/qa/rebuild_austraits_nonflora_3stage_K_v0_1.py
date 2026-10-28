#!/usr/bin/env python3
"""Technical replay of ORIGINAL AusTraits 283/142 nonflora K source arms.

All family x named-trait identities and original reference batch assignments
are immutable. Historical K values are used ONLY for numeric regression and
original job partition, not for eligibility or additional discovery.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from pathlib import Path

ROOT=Path(".")
ARCHIVE=Path("results/austraits_organ_paper_original_nonflora_K_references_v0_1")
SOURCE=Path("results/austraits_organ_paper_frozen_rebuild_inputs_v0_1/shared_taxon_pair_support.json")
BROAD_DESIGN=Path("data/austraits_k_exclude_five_electronic_floras_support_v0_1.json")
STRICT_DESIGN=Path("data/austraits_joint_nonflora_shared_dataset_K_design_v0_1.json")
REPRO={"fruit_height","fruit_length","fruit_width","seed_dry_mass","seed_length","seed_width"}
NUMERIC=("K_full_A","K_full_B","K_source_A","K_source_B",
         "delta_full","delta_source","delta_source_measurements")
ARMS={"broad":{"batches":16,"pairs":283,"status":"AUSTRAITS_K_FIVE_FLORA_EXCLUSION_PAIR_BATCH_COMPLETE",
               "pass":{"S3":283,"prune_only":233}},
      "strict":{"batches":12,"pairs":142,"status":"AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_BATCH_COMPLETE",
                "pass":{"S3":142,"prune_only":101}}}
PARQUET_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"

def need(yes,why):
    if not yes:raise AssertionError(why)

def ident(z):
    return z["family"],z["trait_A"],z["trait_B"]

def ref():
    m=json.loads((ARCHIVE/"original_nonflora_reference_manifest.json").read_text())
    need(m["status"]=="PASS_PERMANENT_AUSTRAITS_ORIGINAL_NONFLORA_SOURCE_K_REFERENCE"
         and m["file_count"]==32 and m["original_public_v7_sha256"]==PARQUET_SHA,
         "Original 283/142 source archive not validated")
    for f,sha in m["file_sha256"].items():
        need(hashlib.sha256((ARCHIVE/f).read_bytes()).hexdigest()==sha,
             "Pinned original source/K file hash changed: "+f)
    s=json.loads((ARCHIVE/"source_support_excluding_five_floras.json").read_text())
    o=json.loads(SOURCE.read_text())
    need(s["status"]=="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_SOURCE_SUPPORT_AUDITED"
         and o["qualifying_family_trait_pairs"]==760,
         "Original K-blind source cohort missing")
    return s,o

def eligible(arm,s,o):
    sys.path.insert(0,"scripts/analysis")
    if arm=="strict":
        from run_austraits_k_joint_nonflora_dataset_batch_v0_1 import cohort
        design=json.loads(STRICT_DESIGN.read_text())
    else:
        from run_austraits_k_five_flora_exclusion_batch_v0_1 import cohort
        design=json.loads(BROAD_DESIGN.read_text())
    rows=cohort(s,o,design)
    need(len(rows)==ARMS[arm]["pairs"],"Original eligible source IDs differ for "+arm)
    d={ident(v):v for v in rows}
    need(len(d)==len(rows),"Duplicated original source-only pair")
    return d

def plan(outdir,report):
    s,o=ref()
    outdir.mkdir(parents=True,exist_ok=True)
    sizes={}
    for arm in ARMS:
        allowed=eligible(arm,s,o)
        covered=set()
        for i in range(1,ARMS[arm]["batches"]+1):
            b=f"B{i:02d}"
            original=json.loads((ARCHIVE/f"{arm}_{b}.json").read_text())
            selection=[]
            for v in original["pairs"]:
                k=ident(v)
                need(k in allowed and k not in covered,
                     "Historical partition not original eligible pair "+str(k))
                covered.add(k)
                selection.append(allowed[k])
            need(selection,"Empty historical batch")
            (outdir/f"{arm}_{b}.json").write_text(
                json.dumps(selection,sort_keys=True,indent=2)+"\n")
            sizes[f"{arm}_{b}"]=len(selection)
        need(set(allowed)==covered,"Missing original source-eligible pairs "+arm)
    result={"status":"PASS_RESTORED_ORIGINAL_283_142_K_BLIND_SOURCE_BATCHES",
            "n_historical_batches":len(sizes),"n_source_eligible_pairs":sum(sizes.values()),
            "batch_sizes":sizes,"new_hypothesis_selection":False,
            "raw_original_species_measurements_exported":False}
    need(result["n_historical_batches"]==28
         and result["n_source_eligible_pairs"]==425,"Nonflora original workflow size drift")
    save(report,result)
    return result

def win(row,value):
    ra,rb=row["trait_A"] in REPRO,row["trait_B"] in REPRO
    need(ra!=rb,"Original nonflora K pair not reproductive-versus-vegetative")
    x=float(value)
    need(x!=0 and math.isfinite(x),"Original K direction became null/nonfinite")
    return int((ra and x>0) or (rb and x<0))

def compare(arm,batch,freshfile,output):
    need(arm in ARMS and batch.startswith("B") and
         1<=int(batch[1:])<=ARMS[arm]["batches"],
         "Not an original nonflora source-K batch")
    ref()
    original=json.loads((ARCHIVE/f"{arm}_{batch}.json").read_text())
    fresh=json.loads(freshfile.read_text())
    require_status=ARMS[arm]["status"]
    need(original["status"]==fresh["status"]==require_status,
         "Wrong original source-arm K estimator")
    need(fresh["no_species_observation_IDs_or_raw_trait_measurements_persisted"] is True,
         "Raw source species/measurements persisted")
    if arm=="strict":
        need(fresh["joint_nonflora_and_identical_source_post_outcome_exploratory"] is True
             and fresh["not_independent_primary_measurement_validation"] is True,
             "Source-arm semantics claim changed")
    else:
        need(fresh["NOT_independent_primary_measurement_validation"] is True,
             "Nonflora source independence mislabelled")
    expected={ident(v):v for v in original["pairs"]}
    observed={ident(v):v for v in fresh["pairs"]}
    need(len(expected)==len(original["pairs"]) and
         len(observed)==len(fresh["pairs"]) and set(observed)==set(expected),
         "Missing or newly included nonflora pair under original cohort")
    counts={axis:{"pass":0,"hold":0,"all_nonflora_wins":0,"common_dataset_wins":0}
            for axis in ("S3","prune_only")}
    max_abs=0.0
    for k,z in observed.items():
        old=expected[k]
        for field in ("system_A","system_B"):
            need(z[field]==old[field],"Changed original source/taxon system ID "+str(k))
        for field in (("n_same_source_positive_species" if arm=="strict" else
                       "n_nonflora_positive_species"),):
            need(z[field]==old[field],"Changed common-source positive species "+str(k))
        for axis in counts:
            x,y=z["axes"][axis],old["axes"][axis]
            need(x["status"]==y["status"] and x["n_tips"]==y["n_tips"],
                 "Original source-stage tree or tip support differs "+str((k,axis)))
            if x["status"]=="PASS":
                counts[axis]["pass"]+=1
                for field in NUMERIC:
                    a,b=float(x[field]),float(y[field])
                    need(math.isfinite(a) and math.isfinite(b),
                         "K numeric source-arm value nonfinite")
                    delta=abs(a-b)
                    max_abs=max(max_abs,delta)
                    need(math.isclose(a,b,rel_tol=1e-7,abs_tol=2e-8),
                         "Source-stage old/new K discrepancy "+str((k,axis,field,a,b)))
                counts[axis]["all_nonflora_wins"]+=win(z,x["delta_full"])
                counts[axis]["common_dataset_wins"]+=win(z,x["delta_source"])
            else:
                need(x["status"].startswith("HOLD_"),"Invalid original source-stage tree hold")
                counts[axis]["hold"]+=1
    result={"status":"PASS_ORIGINAL_NONFLORA_SOURCE_K_BATCH_NUMERIC_REGRESSION",
            "arm":arm,"batch":batch,"n_pairs":len(observed),"axes":counts,
            "max_absolute_K_or_logK_difference":max_abs,
            "new_biological_effects":0,"independent_primary_study_replication":False}
    save(output,result)
    return result

def combine(fresh_dir,audit_dir,outfile):
    ref()
    summary={}
    fresh={}
    max_abs=0.0
    for arm in ARMS:
        ax={name:{"pass":0,"hold":0,"all_nonflora_wins":0,"common_dataset_wins":0}
            for name in ("S3","prune_only")}
        pairs={}
        n=0
        for i in range(1,ARMS[arm]["batches"]+1):
            b=f"B{i:02d}"
            fp=fresh_dir/f"{arm}_{b}_fresh.json"
            ap=audit_dir/f"{arm}_{b}_audit.json"
            need(fp.is_file() and ap.is_file(),"Original strict or broad fresh batch missing "+arm+b)
            oldaudit=json.loads(ap.read_text())
            checked=compare(arm,b,fp,audit_dir/f"{arm}_{b}_aggregation_recheck.json")
            need(oldaudit==checked,"Batch K QA differs from independently checked result")
            max_abs=max(max_abs,checked["max_absolute_K_or_logK_difference"])
            n+=checked["n_pairs"]
            for axis in ax:
                for k in ax[axis]:ax[axis][k]+=checked["axes"][axis][k]
            for row in json.loads(fp.read_text())["pairs"]:
                k=ident(row)
                need(k not in pairs,"Repeated source-qualified pair")
                pairs[k]=row
        need(n==ARMS[arm]["pairs"] and len(pairs)==n and
             all(ax[t]["pass"]==ARMS[arm]["pass"][t] for t in ax),
             "Incomplete original source restriction K pair graph")
        summary[arm]={"n_qualified":n,"axes":ax}
        fresh[arm]=pairs
    need(summary["broad"]["axes"]["S3"]["common_dataset_wins"]==221
         and summary["broad"]["axes"]["prune_only"]["common_dataset_wins"]==180,
         "Original 283 broad nonflora K winner counts changed")
    need(summary["strict"]["axes"]["S3"]["common_dataset_wins"]==120
         and summary["strict"]["axes"]["prune_only"]["common_dataset_wins"]==81,
         "Original strict same-source 142/101 K winner counts changed")
    stage={}
    for ax,n,original in (("S3",142,[110,121,120]),
                          ("prune_only",101,[82,83,81])):
        strict={k:v for k,v in fresh["strict"].items() if v["axes"][ax]["status"]=="PASS"}
        wide={k:v for k,v in fresh["broad"].items() if v["axes"][ax]["status"]=="PASS"}
        need(len(strict)==n and set(strict).issubset(wide),
             "Nonflora three-stage pair identity source tip graph changed")
        rates=[0,0,0]
        flips=[0,0]
        for k,v in strict.items():
            st1=win(wide[k],wide[k]["axes"][ax]["delta_source"])
            st2=win(v,v["axes"][ax]["delta_full"])
            st3=win(v,v["axes"][ax]["delta_source"])
            rates[0]+=st1;rates[1]+=st2;rates[2]+=st3
            flips[0]+=int(st1!=st2);flips[1]+=int(st2!=st3)
        need(rates==original and flips==([23,9] if ax=="S3" else [13,12]),
             "Three-stage source/tip K decomposition cannot be numerically reproduced")
        stage[ax]={"same_original_pair_identities":n,
                   "reproductive_K_wins":rates,"source_tip_then_value_sign_flips":flips}
    result={
       "status":"PASS_ALL_283_142_NONFLORA_K_AND_THREE_STAGE_TRANSITIONS_REPRODUCED",
       "source_release":"AusTraits v7.0.0",
       "original_public_parquet_sha256":PARQUET_SHA,
       "source_arms":summary,"three_stage_identical_pair_contrasts":stage,
       "maximum_absolute_source_K_or_logK_discrepancy":max_abs,
       "strict_nonflora_K_recomputed_from_public_source":True,
       "broad_nonflora_K_recomputed_from_public_source":True,
       "independent_original_measurement_replication":False,
       "original_postdiscovery_organ_grouping":True,
       "new_evolutionary_process_parameter_tests":0}
    save(outfile,result)
    return result

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("plan","compare","combine"),required=True)
    p.add_argument("--arm",choices=tuple(ARMS))
    p.add_argument("--batch")
    p.add_argument("--batch-dir",type=Path)
    p.add_argument("--fresh",type=Path)
    p.add_argument("--fresh-dir",type=Path)
    p.add_argument("--audit-dir",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.mode=="plan":
        need(a.batch_dir,"Batch plan output missing")
        x=plan(a.batch_dir,a.output)
    elif a.mode=="compare":
        need(a.arm and a.batch and a.fresh,"Source K batch arguments missing")
        x=compare(a.arm,a.batch,a.fresh,a.output)
    else:
        need(a.fresh_dir and a.audit_dir,"Source K full re-aggregation requires all 28 batches")
        x=combine(a.fresh_dir,a.audit_dir,a.output)
    print(json.dumps({"status":x["status"],
                      "arm":x.get("arm"),
                      "n_pairs":x.get("n_pairs"),
                      "stages":x.get("three_stage_identical_pair_contrasts")},sort_keys=True))
if __name__=="__main__":main()
