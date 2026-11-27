#!/usr/bin/env python3
"""Post-result strict species-disjoint support and fixed transfer sensitivity."""
from __future__ import annotations
import collections, importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/jena_tbe2012_species_disjoint_sensitivity_20261127_v0_1.json"
def run():
    spec=importlib.util.spec_from_file_location("primary",ROOT/"scripts/analysis/jena_tbe2012_pool_fox_transfer_20261127.py")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    rows,info=m.source()
    primary=json.loads((ROOT/"results/jena_tbe2012_84plot_pool_fox_transfer_20261127_v0_1.json").read_text())
    replay=m.evaluate(rows)
    for k,v in primary["analysis"]["combined_equal_pool_richness_gain"].items():
        if abs(v-replay["combined_equal_pool_richness_gain"][k])>1e-10:raise ValueError("primary replay changed")
    pools=sorted({r["pool"] for r in rows});rich=sorted({r["rich"] for r in rows})
    support=[]
    for p in pools:
        te=[r for r in rows if r["pool"]==p]
        test_taxa=set(s for r in te for s in r["species"])
        pre=[r for r in rows if r["pool"]!=p];tr=[r for r in pre if not set(r["species"])&test_taxa]
        tr_taxa=set(s for r in tr for s in r["species"])
        ct=[{"pool":q,"richness":r,"n":sum(z["pool"]==q and z["rich"]==r for z in tr),
             "n_low":sum(z["pool"]==q and z["rich"]==r and not z["high"] for z in tr),
             "n_high":sum(z["pool"]==q and z["rich"]==r and z["high"] for z in tr)}
            for q in pools if q!=p for r in rich]
        support.append({"heldout_pool":p,"n_original_test":len(te),"n_train_before":len(pre),
           "n_train_after":len(tr),"n_shared_taxa_after":len(tr_taxa&test_taxa),
           "prefix_levels":len({r["prefix"] for r in tr}),"training_cells":ct,
           "support_gate_pass":len(tr)>20 and all(c["n_low"]>0 and c["n_high"]>0 for c in ct)
                    and len({r["prefix"] for r in tr})==3 and not (tr_taxa&test_taxa)})
    result={"status":"SPECIES_DISJOINT_SOURCE_SUPPORT_HOLD","post_result_sensitivity":True,
       "primary_replay":True,"original_source_audit":info,"fold_support":support,
       "original_primary_result_changed":False,"n_field_experiments":1,"original_raw_rows_exported":False}
    if not all(f["support_gate_pass"] for f in support):return result
    try:
        result["analysis"]=m.evaluate(rows,purge_shared_species=True)
        assert all(f["n_shared_train_test_taxa"]==0 for f in result["analysis"]["folds"])
        result["status"]="SPECIES_DISJOINT_SENSITIVITY_COMPLETE"
    except ValueError as e:
        result["model_gate_stop"]=str(e)[:150]
    return result
if __name__=="__main__":
    try:j=run()
    except Exception as e:j={"status":"SOURCE_OR_REPLAY_HOLD","failure_class":type(e).__name__,"reason":str(e)[:150] if isinstance(e,ValueError) else "source access or calculation"}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(j,indent=2)+"\n")
    print(json.dumps(j))
    if j["status"]=="SOURCE_OR_REPLAY_HOLD":raise SystemExit(1)
