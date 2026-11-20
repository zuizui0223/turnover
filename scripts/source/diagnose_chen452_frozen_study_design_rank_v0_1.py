#!/usr/bin/env python3
"""Source-only matrix rank diagnostics. Zero CE/SE fits, no original IDs exported."""
import collections,json
from pathlib import Path
import numpy as np
import sys
sys.path.insert(0,"scripts/analysis")
import chen452_fixed_leafn_fd_ce_se_study_holdout_v0_1 as m

def diagnose():
    out={"status":"SOURCE_ONLY_FROZEN_DESIGN_RANK_DIAGNOSIS",
         "biological_effect_fitted":False,"source_study_names_exported":False,
         "original_frozen_HOLD_unchanged":True,"cohorts":{}}
    for typ in ("leafN","SLA"):
        rows,groups,src=m.assemble(typ)
        rankhist=collections.Counter(); redundant=collections.Counter(); failures=0
        for key in sorted(groups):
            excluded=set(groups[key])
            ix=[i for i in range(len(rows)) if i not in excluded]
            tr=[rows[i] for i in ix]
            w=m.weights_for_train(rows,ix)
            values=np.array([m.numeric(r) for r in tr])
            mean=np.average(values,axis=0,weights=w)
            std=np.sqrt(np.average((values-mean)**2,axis=0,weights=w))
            if any(std<=1e-10):
                redundant["numeric_zero_sd"]+=1;failures+=1;continue
            n=(values-mean)/std
            columns=[np.ones(len(tr)),*[n[:,j] for j in range(6)],
                     np.array([r["nfix"] for r in tr])]
            names=["intercept","richness","age","PD","CWM","MAT","AI","NFix"]
            for k,label in (("eco","Eco1"),("plant","PlantType")):
                levels=sorted({r[k] for r in tr})
                for lev in levels[1:]:
                    columns.append(np.array([float(r[k]==lev) for r in tr]))
                    names.append(label+"_dummy")
            fd=np.array([r["FD"] for r in tr])
            fsd=np.sqrt(np.average((fd-np.average(fd,weights=w))**2,weights=w))
            if fsd<=1e-10:
                redundant["FD_zero_sd"]+=1;failures+=1;continue
            columns.append((fd-np.average(fd,weights=w))/fsd);names.append("RaoQ_FD")
            X=np.column_stack(columns)
            rank=int(np.linalg.matrix_rank(X))
            rankhist[str(X.shape[1])+"cols_"+str(rank)+"rank"]+=1
            if rank<X.shape[1]:
                failures+=1
                for col in range(1,X.shape[1]):
                    if np.linalg.matrix_rank(X[:,:col+1])==np.linalg.matrix_rank(X[:,:col]):
                        redundant[names[col]]+=1
        out["cohorts"][typ]={"study_folds":len(groups),
            "original_complete_rows":len(rows),"fullrank_study_folds":len(groups)-failures,
            "original_rank_deficient_folds":failures,
            "source_variable_redundancy":dict(redundant),
            "rank_histogram":dict(rankhist)}
    return out

if __name__=="__main__":
    out=diagnose()
    path=Path("build/chen452_holdout/original_rank_diagnosis_v0_1.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("CHEN452_FROZEN_SOURCE_PREDICTOR_RANK",json.dumps(out,sort_keys=True))
