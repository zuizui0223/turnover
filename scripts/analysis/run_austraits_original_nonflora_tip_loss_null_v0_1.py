#!/usr/bin/env python3
"""Original AusTraits 142-pair fixed-broad-tree taxon-loss null: plan and audit.

Post-discovery sensitivity, NOT an independent primary-study hypothesis.
The null has fixed original broad nonflora phenotype medians, fixed original
broad V.PhyloMaker2 native trees, and matches ACTUAL strict surviving tree
tip count. Compare actual strict-survivor subset to size-matched random draws.

Input species/trait states and original observation IDs are EPHEMERAL.
Only derived pair-level K null summaries are durably reported.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys
from collections import defaultdict
from pathlib import Path
import duckdb
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qa"))
from audit_austraits_organ_contributing_sources_v0_1 import source_graph,compile_states,make_pairs

ORIGINAL=Path("results/austraits_organ_paper_public_v7_nonflora_3stage_replay_v0_1")
SOURCE_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
STATUS_PLAN="PASS_K_BLIND_ORIGINAL_142_PAIRS_TIP_LOSS_NULL_FIXED_BATCHES"
STATUS_PREP="PASS_ORIGINAL_142_TIP_LOSS_EPHEMERAL_SOURCE_MEDIANS"
STATUS_BATCH="PASS_ORIGINAL_142_TIP_LOSS_FROZEN_BROAD_TREE_NULL_BATCH"
STATUS_FULL="PASS_ORIGINAL_142_101_BROAD_TREE_FIXED_SIZE_MATCHED_TIP_LOSS_NULL"
NUM_BATCH=12
DRAW_COUNT=128
SEED=20261114
REPRO={"fruit_height","fruit_length","fruit_width","seed_dry_mass","seed_length","seed_width"}
AXES=("S3","prune_only")

def need(test,msg):
    if not test:raise AssertionError(msg)

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def records(arm,ax):
    data=json.loads((ORIGINAL/(arm+"_aggregate.json")).read_text()) if False else None
    p="broad_283_aggregate.json" if arm=="broad" else "strict_142_aggregate.json"
    data=json.loads((ORIGINAL/p).read_text())
    rows=data["axes"][ax]["pair_level_K_decisions_no_species_names"]
    return {(z["family"],z["trait_A"],z["trait_B"]):z for z in rows}

def selected():
    _,_,fixed=source_graph()
    need(len(fixed)==142,"Original 142 common DatasetID K-blind source cohort changed")
    broad={ax:records("broad",ax) for ax in AXES}
    strict={ax:records("strict",ax) for ax in AXES}
    res=[]
    for z in fixed:
        key=(z["family"],z["trait_A"],z["trait_B"])
        need(key in broad["S3"] and key in strict["S3"],
             "Original strict pair not in original broad K source archive")
        ref=bro= broad["S3"][key]
        rn=strict["S3"][key]
        need(rn["n_same_source_species"]>=20
             and bro["n_nonflora_species"]>=rn["n_same_source_species"],
             "Original strict/broad species source graph not nested")
        need((z["trait_A"] in REPRO)!=(z["trait_B"] in REPRO),
             "Original post-selected cross-organ classification changed")
        ax={}
        for a in AXES:
            if key in strict[a]:
                need(key in broad[a],"Strict native K pair absent from broad native K")
                bb=broad[a][key];ss=strict[a][key]
                ax[a]={"broad_delta":bb["delta_five_flora_removed"],
                       "strict_original_rebuilt_delta":ss["delta_all_nonflora_sources"],
                       "broad_native_tips":bb["n_native_tree_tips"],
                       "strict_original_native_tips":ss["n_native_tree_tips"],
                       "status":"PASS"}
            else:
                need(a=="prune_only","Original S3 strict K pairs should all pass")
                ax[a]={"status":"HOLD_ORIGINAL_NATIVE_PRUNE"}
        res.append({"family":z["family"],"trait_A":z["trait_A"],
            "trait_B":z["trait_B"],"system_A":z["system_A"],
            "system_B":z["system_B"],
            "original_all_positive_species":z["n_original_shared_positive_species"],
            "original_broad_nonflora_species":bro["n_nonflora_species"],
            "original_strict_source_species":rn["n_same_source_species"],
            "original_K_axes":ax})
    need(len(res)==142 and len({x["family"] for x in res})==24,
         "Original 142 K pairs or 24 family clusters missing")
    need(sum(x["original_K_axes"]["prune_only"]["status"]=="PASS" for x in res)==101,
         "Original 101 native prune supported strict pair identities changed")
    return sorted(res,key=lambda x:(x["family"],x["trait_A"],x["trait_B"]))

def plan(out_dir,out):
    from copy import deepcopy
    items=selected()
    fam=defaultdict(list)
    for z in items:fam[z["family"]].append(z)
    groups=[{"work":0,"families":[],"pairs":[]} for _ in range(NUM_BATCH)]
    for family,rows in sorted(fam.items(),
          key=lambda v:-sum(x["original_broad_nonflora_species"]**1.4 for x in v[1])):
        idx=min(range(NUM_BATCH),key=lambda i:(groups[i]["work"],i))
        g=groups[idx]
        g["families"].append(family)
        g["pairs"]+=deepcopy(rows)
        g["work"]+=sum(x["original_broad_nonflora_species"]**1.4 for x in rows)
    out_dir.mkdir(parents=True,exist_ok=True)
    summary={}
    for i,g in enumerate(groups,1):
        label=f"P{i:02d}"
        need(g["pairs"],"Fixed source K-batch would be empty")
        for j,z in enumerate(g["pairs"],1):z["null_pair_id"]=f"{label}_Q{j:03d}"
        (out_dir/(label+".json")).write_text(json.dumps(g["pairs"],sort_keys=True,indent=2)+"\n")
        summary[label]={"n_original_pairs":len(g["pairs"]),"n_families":len(g["families"]),
                        "family_labels":g["families"]}
    need(sum(v["n_original_pairs"] for v in summary.values())==142,
         "Original 142 pair-ID source-only null plan incomplete")
    answer={"status":STATUS_PLAN,"source":"original public AusTraits v7 142-pair K-blind source cohort",
      "number_of_batches":NUM_BATCH,"null_draws_per_family_replicate":DRAW_COUNT,
      "shared_family_species_priority_seed":SEED,
      "original_qualified_pairs":142,"original_prune_native_supported_pairs":101,
      "families":24,"all_family_pairs_in_one_batch":True,
      "source_K_outcomes_not_used_to_select_pairs":True,
      "no_original_data_downloaded_for_plan":True,
      "batch_profiles":summary}
    out.write_text(json.dumps(answer,sort_keys=True,indent=2)+"\n")
    return answer

def prepare(batch,parquet,traits_yml,out_dir,out):
    need(digest(parquet)==SOURCE_SHA,"Original public source AusTraits v7 SHA mismatch")
    items=json.loads(batch.read_text())
    fixed={(z["family"],z["trait_A"],z["trait_B"]):z for z in selected()}
    need(items and len({(z["family"],z["trait_A"],z["trait_B"]) for z in items})==len(items),
         "Fixed original source-only batch has duplicate K identities")
    need(all((z["family"],z["trait_A"],z["trait_B"]) in fixed for z in items),
         "Attempt to add a source-unqualified original K pair")
    families={z["family"] for z in items}
    c=duckdb.connect(":memory:")
    try:
        refs,pairs,strict=source_graph()
        compile_states(c,parquet,traits_yml,refs)
        make_pairs(c,pairs,strict)
        c.execute("""CREATE TEMP TABLE nonflora_medians AS
            SELECT r.sid,r.species,r.genus,median(r.val) AS val
            FROM nonflora_records r
            JOIN nonflora_states s ON r.sid=s.sid AND r.species=s.species AND r.genus=s.genus
            GROUP BY r.sid,r.species,r.genus""")
        c.execute("""CREATE TEMP TABLE source_medians AS
            SELECT s.family,s.trait_A,s.trait_B,s.species,s.genus,
                   median(r.val) FILTER(WHERE r.sid=s.system_A) AS source_A,
                   median(r.val) FILTER(WHERE r.sid=s.system_B) AS source_B
            FROM same_dataset s JOIN nonflora_records r
                 ON r.species=s.species AND r.genus=s.genus AND r.ds=s.ds
                 AND r.sid IN (s.system_A,s.system_B)
            GROUP BY s.family,s.trait_A,s.trait_B,s.species,s.genus""")
        c.execute("CREATE TEMP TABLE target_null(family VARCHAR,trait_A VARCHAR,trait_B VARCHAR,system_A VARCHAR,system_B VARCHAR)")
        c.executemany("INSERT INTO target_null VALUES (?,?,?,?,?)",[
          (z["family"],z["trait_A"],z["trait_B"],z["system_A"],z["system_B"]) for z in items])
        rows=c.execute("""SELECT p.family,p.trait_A,p.trait_B,
                 a.species,a.genus,a.val,b.val,
                 CASE WHEN s.source_A>0 AND s.source_B>0 THEN 1 ELSE 0 END AS strict_survivor
            FROM target_null p
            JOIN nonflora_medians a ON a.sid=p.system_A
            JOIN nonflora_medians b ON b.sid=p.system_B
                 AND a.species=b.species AND a.genus=b.genus
            LEFT JOIN source_medians s
                 ON s.family=p.family AND s.trait_A=p.trait_A AND s.trait_B=p.trait_B
                 AND s.species=a.species AND s.genus=a.genus
            ORDER BY p.family,p.trait_A,p.trait_B,a.species""").fetchall()
    finally:c.close()
    by=defaultdict(list)
    for x in rows:by[(x[0],x[1],x[2])].append(x)
    out_dir.mkdir(parents=True,exist_ok=True)
    full=[]
    for z in items:
        key=(z["family"],z["trait_A"],z["trait_B"])
        vals=by.get(key,[])
        nstrict=sum(int(x[7]) for x in vals)
        need(len(vals)==z["original_broad_nonflora_species"]
             and nstrict==z["original_strict_source_species"],
             "Same original public-v7 species selected for broad/strict K pair differs")
        need(all(math.isfinite(float(x[5])) and math.isfinite(float(x[6]))
                 and float(x[5])>0 and float(x[6])>0 for x in vals),
             "Nonpositive original nonflora trait state after qualifying source cohort")
        fn=out_dir/(z["null_pair_id"]+".csv")
        with fn.open("w",newline="",encoding="utf-8") as f:
            writer=csv.writer(f)
            writer.writerow(("family","genus","species","state_A","state_B","strict_survivor"))
            for row in vals:writer.writerow((row[0],row[4],row[3],row[5],row[6],row[7]))
        full.append({**z,"ephemeral_original_state_csv":str(fn)})
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(full,sort_keys=True,indent=2)+"\n")
    return {"status":STATUS_PREP,"n_original_pairs":len(full),
       "n_original_species_state_rows_temp":sum(x["original_broad_nonflora_species"] for x in full),
       "n_actual_strict_source_species_state_rows_temp":sum(x["original_strict_source_species"] for x in full),
       "all_original_broad_and_strict_species_support_exact":True,
       "species_trait_values_never_written_to_committed_results":True}

def validate(batch,result):
    cases=json.loads(batch.read_text())
    data=json.loads(result.read_text())
    need(data["status"]==STATUS_BATCH and len(data["pairs"])==len(cases)
         and data["null_replicates"]==DRAW_COUNT
         and data["same_family_random_rank_shared_across_original_trait_pairs"] is True,
         "Original 142-pair family-structured fixed-tree null output malformed")
    families={z["family"] for z in cases}
    accepted_draws=DRAW_COUNT*len(families)
    need(data["null_inference_conditioned_on_phylogenetic_K_estimable_in_every_family_pair"] is True
         and data["no_per_pair_independent_resampling_after_K_variance_hold"] is True
         and data["n_total_candidate_family_priorities_evaluated"]>=accepted_draws
         and data["n_rejected_family_priorities_due_to_undefined_K"]==
             data["n_total_candidate_family_priorities_evaluated"]-accepted_draws
         and set(data["rejected_K_undefined_draws_by_family"])==families
         and sum(data["rejected_K_undefined_draws_by_family"].values())==
             data["n_rejected_family_priorities_due_to_undefined_K"],
         "Family-priority K validity conditioning and null rejection accounting incomplete")
    ref={x["null_pair_id"]:x for x in cases}
    for z in data["pairs"]:
        p=ref[z["null_pair_id"]]
        need((z["family"],z["trait_A"],z["trait_B"])==
             (p["family"],p["trait_A"],p["trait_B"]),
             "Fixed original family/trait K null identity modified")
        for ax in AXES:
            x=z["axes"][ax];prior=p["original_K_axes"][ax]
            if prior["status"]!="PASS":
                need(x["status"]=="HOLD_ORIGINAL_NATIVE_PRUNE","Unexpected original native prune K")
                continue
            need(x["status"]=="PASS" and x["n_baseline_tips"]==prior["broad_native_tips"]
                 and x["n_actual_strict_tips"]==prior["strict_original_native_tips"]
                 and math.isclose(x["baseline_logK_contrast"],prior["broad_delta"],
                                  rel_tol=1e-7,abs_tol=2e-8),
                 "Original public-v7 baseline K or actual source survivor native tip count drift")
            need(math.isclose(x["historical_stage2_rebuilt_logK_contrast"],
                              prior["strict_original_rebuilt_delta"],abs_tol=1e-12),
                 "Original stage2 native re-insertion K contrast changed")
            bits=x["null_flip_bits"]
            need(len(bits)==DRAW_COUNT and set(bits)<=set("01")
                 and 0<=x["empirical_null_tail_prob_abs_delta_shift"]<=1
                 and 0<=x["null_K_sign_flip_probability"]<=1,
                 "Random taxon-loss null incomplete or nonfinite")
    return {"status":"PASS_ORIGINAL_TAXON_LOSS_K_BATCH_REGRESSION",
            "batch":batch.stem,"n_cases":len(cases),
            "native_tips_and_original_broad_K_pinned":True,
            "null_draws_per_original_pair":DRAW_COUNT,
            "original_biological_conclusions_unchanged":True}

def combine(input_dir,plan_dir,out):
    plan=json.loads((plan_dir/"original_null_plan.json").read_text())
    need(plan["status"]==STATUS_PLAN and plan["original_qualified_pairs"]==142,
         "Unverified null source-only plan")
    pairs=[]; audits=[]
    rejected_total=0; attempts_total=0
    for k in range(1,NUM_BATCH+1):
        tag=f"P{k:02d}"
        p=input_dir/(tag+"_null.json")
        qa=input_dir/(tag+"_audit.json")
        need(p.is_file() and qa.is_file(),"Original K null batch missing "+tag)
        chk=validate(plan_dir/(tag+".json"),p)
        old=json.loads(qa.read_text())
        need(chk==old,"Null per-batch deterministic QA changed "+tag)
        item=json.loads(p.read_text())
        pairs.extend(item["pairs"])
        rejected_total+=item["n_rejected_family_priorities_due_to_undefined_K"]
        attempts_total+=item["n_total_candidate_family_priorities_evaluated"]
        audits.append(tag)
    need(len(pairs)==142 and len(set((x["family"],x["trait_A"],x["trait_B"]) for x in pairs))==142,
         "Original full 142 native K pair identities missing from null")
    need(attempts_total==24*DRAW_COUNT+rejected_total,
         "Full 24-family K-valid random-priority accounting did not match 128 draws")
    axes={};source_only={}
    for ax in AXES:
        data=[z for z in pairs if z["axes"][ax]["status"]=="PASS"]
        expected=142 if ax=="S3" else 101
        need(len(data)==expected,"Original native 142/101 K axis missing")
        observed=sum(z["axes"][ax]["actual_strict_survivor_flip_on_fixed_broad_tree"] for z in data)
        original_stage2=sum((z["axes"][ax]["baseline_logK_contrast"]>0)!=(z["axes"][ax]["historical_stage2_rebuilt_logK_contrast"]>0) for z in data)
        expected_historical=23 if ax=="S3" else 13
        need(original_stage2==expected_historical,
             "Original observed full source/taxon stage flips no longer match frozen")
        sim=[sum(z["axes"][ax]["null_flip_bits"][r]=="1" for z in data)
             for r in range(DRAW_COUNT)]
        need(all(0<=x<=expected for x in sim),"Invalid family-correlated draw count")
        from statistics import median
        expected_num=sum(z["axes"][ax]["null_K_sign_flip_probability"] for z in data)
        p_hi=(1+sum(v>=observed for v in sim))/(1+DRAW_COUNT)
        p_lo=(1+sum(v<=observed for v in sim))/(1+DRAW_COUNT)
        axes[ax]={
          "original_frozen_strict_K_pairs":expected,
          "original_historical_broad_to_strict_tree_rebuilt_K_flips":original_stage2,
          "actual_strict_survivors_on_fixed_broad_tree_K_flips":observed,
          "null_draws":DRAW_COUNT,
          "mean_family_correlated_random_taxon_loss_K_flips":sum(sim)/DRAW_COUNT,
          "sum_individual_pair_null_flip_probability":expected_num,
          "median_family_correlated_random_K_flips":median(sim),
          "range_random_K_flip_counts":[min(sim),max(sim)],
          "empirical_upper_tail_p_actual_fixed_tree_flips":p_hi,
          "empirical_lower_tail_p_actual_fixed_tree_flips":p_lo,
          "median_null_flip_probability_of_historically_reversed_pairs":
             median([z["axes"][ax]["null_K_sign_flip_probability"] for z in data if
                     (z["axes"][ax]["baseline_logK_contrast"]>0)!=(z["axes"][ax]["historical_stage2_rebuilt_logK_contrast"]>0)]),
          "family_correlated_null_sampling_same_species_priorities_within_family":True,
          "original_same_source_phenotype_values_and_broad_tree_kept_fixed":True,
          "stage2_rebuilt_tree_not_equated_to_broad_tree_pruning":True}
    result={"status":STATUS_FULL,"axes":axes,
      "number_original_family_trait_pairs":142,
      "original_prune_supported_pair_ids":101,
      "original_K_original_native_phylogeny_reconstructed_from_public_v7":True,
      "public_source_release":"AusTraits v7.0.0","original_source_parquet_SHA256":SOURCE_SHA,
      "n_null_draws":DRAW_COUNT,"null_seed":SEED,"n_original_fixed_batches":NUM_BATCH,
      "family_clustered_random_priority_across_overlapping_original_pairs":True,
      "null_distribution_conditioned_on_K_estimable_across_each_original_family":True,
      "n_original_family_clusters":24,
      "n_total_candidate_family_rank_draws":attempts_total,
      "n_rejected_candidate_family_rank_draws_due_to_undefined_K":rejected_total,
      "no_independent_per_pair_redraws_that_break_family_dependence":True,
      "randomization_tests_conditional_on_fixed_taxa_numbers_not_independent_empirical_validation":True,
      "original_post_K_organ_grouping_and_selection_bias_unchanged":True,
      "no_K_source_data_or_GIFT_or_TRY_raw_trait_measurements_exported":True,
      "not_a_plant_biomass_or_natural_selection_causal_test":True,
      "null_null_sampling_contingent_on_original_broad_phylogenetic_tree":True}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=("plan","prepare","audit","combine"))
    p.add_argument("--batch",type=Path)
    p.add_argument("--parquet",type=Path)
    p.add_argument("--traits-yml",type=Path)
    p.add_argument("--states-dir",type=Path)
    p.add_argument("--results-dir",type=Path)
    p.add_argument("--plan-dir",type=Path)
    p.add_argument("--input",type=Path)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.mode=="plan":
        need(a.plan_dir,"Null K plan batch output path required")
        r=plan(a.plan_dir,a.out)
    elif a.mode=="prepare":
        need(a.batch and a.parquet and a.traits_yml and a.states_dir,
             "Original raw-source null K batch input missing")
        r=prepare(a.batch,a.parquet,a.traits_yml,a.states_dir,a.out)
    elif a.mode=="audit":
        need(a.batch and a.input,"Original K null per-batch evidence missing")
        r=validate(a.batch,a.input)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    else:
        need(a.results_dir and a.plan_dir,"Missing complete 12-batch fixed K null results")
        r=combine(a.results_dir,a.plan_dir,a.out)
    print(json.dumps({"status":r["status"],
          "original_pairs":r.get("original_qualified_pairs",r.get("number_original_family_trait_pairs",r.get("n_cases"))),
          "axes":r.get("axes")},sort_keys=True))

if __name__=="__main__":main()
