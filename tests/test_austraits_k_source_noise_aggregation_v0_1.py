#!/usr/bin/env python3
"""Synthetic integration of complete 249-system OU+source K aggregation.

B=4 is ONLY for testing wiring. Scientific production always requires B=256.
This test does not retrieve actual observed trait values or process-null outcomes.
"""
from __future__ import annotations
import copy, json, math, sys, tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
import aggregate_austraits_k_source_noise_ou_v0_1 as agg

def expect_reject(message, call):
    try: call()
    except (ValueError,KeyError) as e:
        assert message in str(e),str(e)
    else: raise AssertionError("Corrupt source-model input should be rejected: "+message)

def run(arguments):
    old=sys.argv
    try:
        sys.argv=["synthetic"]+arguments
        agg.main()
    finally:
        sys.argv=old

rng=np.random.default_rng(20261008)
with tempfile.TemporaryDirectory(prefix="source_ou_complete_") as tmp:
    wd=Path(tmp); (wd/"sim").mkdir()
    design={"status":"POST_OBSERVED_K_AND_SHARED_OU_PRE_SOURCE_DISPERSION_OUTCOMES_FROZEN"}
    reference={"status":"AUSTRAITS_REAL_TREE_OU_TIME_REFERENCE_FROZEN",
               "T_ref":47.5820775,
               "absolute_alpha_grid":{"c0p25":.25/47.5820775,
                                      "c1":1/47.5820775,
                                      "c4":4/47.5820775}}
    source={"status":"AUSTRAITS_K_CROSS_SOURCE_DISPERSION_ESTIMATED",
            "eligible_traits":12,"traits":{},"systems":[]}
    for t in range(12):
        source["traits"][f"T{t:02d}"]={
            "source_log_variance_ratio_median":float(.01+.015*t),
            "calibratable_for_followon_process_null":True
        }
    source["traits"]["seed_height"]={
        "source_log_variance_ratio_median":.15,
        "calibratable_for_followon_process_null":False
    }
    obs=[]
    # 42 families x 5 traits plus 39 one-more trait => 249.
    for family in range(42):
        for k in range(5+(family<39)):
            trait=f"T{(family*7+k)%12:02d}"
            obs.append({"system_id":f"A{len(obs)+1:04d}",
                        "family":f"F{family:02d}","trait_name":trait})
    assert len(obs)==249
    # Exactly five source-ineligible seed_height cases, excluded in both axes.
    for family in range(5):
        obs.append({"system_id":f"A{len(obs)+1:04d}",
                    "family":f"F{family:02d}","trait_name":"seed_height"})
    for row in obs:
        sid,fam,trait=row["system_id"],row["family"],row["trait_name"]
        K3=float(np.exp(rng.normal(-1,.3)))
        Kp=float(np.exp(rng.normal(-.9,.3)))
        row.update({"S3_K":K3,"prune_K":Kp,
                    "S3_logK":math.log(K3),"prune_logK":math.log(Kp)})
        # Full 254-system source graph, with five fallback cells.
        qualified=(int(sid[1:])%17!=0)
        local=float(.02+.003*(int(sid[1:])%13)) if qualified else None
        source["systems"].append({
            "system_id":sid,"trait_name":trait,"family":fam,
            "calibratable":qualified,
            "relative_source_dispersion":local
        })
        if trait=="seed_height":continue
        global_eta=source["traits"][trait]["source_log_variance_ratio_median"]
        eta=local if qualified else global_eta
        axes={}
        for axis,kval in (("S3",K3),("prune_only",Kp)):
            scenarios={}
            for label,alpha in reference["absolute_alpha_grid"].items():
                # Model-specific null values with exact fixed dimensions;
                # a global trait effect gives meaningful rank gain.
                y=float(np.log(kval))
                scenarios[label]={"alpha":alpha,"models":{
                    "trait_global":{"logK":(rng.normal(.03*int(trait[1:]),.2,size=4)).tolist()},
                    "system_local":{"logK":(rng.normal(.04*int(trait[1:]),.2,size=4)).tolist()}}}
            axes[axis]={"observed_logK":math.log(kval),
                        "observed_fast_K_error":0,"scenarios":scenarios}
        entry={"status":"AUSTRAITS_K_SOURCE_NOISE_OU_SYSTEM_ESTIMATED",
               "system_id":sid,"family":fam,"trait_name":trait,
               "eta_global":global_eta,"eta_local":eta,
               "eta_local_fallback":not qualified,
               "T_ref":reference["T_ref"],"axes":axes}
        (wd/"sim"/(sid+".json")).write_text(json.dumps(entry))
    pd.DataFrame(obs).to_csv(wd/"K.csv",index=False)
    (wd/"source.json").write_text(json.dumps(source))
    (wd/"time.json").write_text(json.dumps(reference))
    (wd/"design.json").write_text(json.dumps(design))
    opts=["--input-dir",str(wd/"sim"),"--observed-K",str(wd/"K.csv"),
          "--source-calibration",str(wd/"source.json"),
          "--time-reference",str(wd/"time.json"),"--design",str(wd/"design.json"),
          "--out",str(wd/"results.json"),"--tables-dir",str(wd/"tables")]
    original=agg.B
    agg.B=4
    try:
        run(opts)
        output=json.loads((wd/"results.json").read_text())
        assert output["status"]=="AUSTRAITS_K_SOURCE_NOISE_OU_METRIC_NULL_ESTIMATED"
        assert output["observed_graph"]=={"systems":249,"families":42,"traits":12}
        assert output["replicates"]==4
        assert set(output["models"])=={"trait_global","system_local"}
        for model in output["models"]:
            for scen in output["models"][model]:
                table=pd.read_csv(wd/"tables"/f"null_effects_{model}_{scen}.csv")
                assert len(table)==4*249
                assert "seed_height" not in set(table.trait_name)
                for axis in ("S3","prune_only"):
                    z=output["models"][model][scen]["axes"][axis]
                    assert math.isfinite(z["observed"]["rank_gain"])
                    assert math.isfinite(z["null"]["rank_gain"]["q975"])
        # Adversarial source-ratio corruption must fail *before* inference.
        p=wd/"sim"/"A0001.json"
        valid=json.loads(p.read_text())
        mutated=copy.deepcopy(valid)
        mutated["eta_global"]*=2
        p.write_text(json.dumps(mutated))
        expect_reject("eta no longer matches",lambda:run(opts))
        p.write_text(json.dumps(valid))
        # Incomplete frozen graph must fail rather than silently infer.
        p.unlink()
        expect_reject("missing K source-noise systems",lambda:run(opts))
    finally:
        agg.B=original
print("PASS: synthetic complete 249-system source-OU aggregation, 12 model-axis outcomes and source guards")
