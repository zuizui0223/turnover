#!/usr/bin/env python3
"""Freeze shared OU time scale from all 254 exact AusTraits system trees.

T_ref is median over 508 per-tree max root-to-tip depths (S3+prune).
No observed K value, trait difference or outcome enters this calculation.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--metadata-dir",type=Path,required=True)
ap.add_argument("--reference-effects",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()
ref=pd.read_csv(a.reference_effects)
assert (len(ref),ref.family.nunique(),ref.trait_name.nunique())==(254,42,13)
d={x.system_id:(x.family,x.trait_name) for x in ref.itertuples(index=False)}
seen={}
for path in sorted(a.metadata_dir.glob("*.json")):
    x=json.loads(path.read_text())
    sid=x.get('system_id')
    if x.get('status')!='AUSTRAITS_REAL_TREE_OU_DEPTH_REFERENCE_ESTIMATED':
        raise ValueError(f"invalid reference file {path}")
    if sid in seen or sid not in d:
        raise ValueError(f"duplicate/unknown system {sid}")
    if (x['family'],x['trait_name'])!=d[sid]:
        raise ValueError(f"system identity mismatch {sid}")
    for axis in ['S3','prune_only']:
        z=x['axes'][axis]
        if z['n_tips']<20 or not np.isfinite(z['maximum_root_to_tip_depth']) or z['maximum_root_to_tip_depth']<=0:
            raise ValueError(f"invalid tree depth {sid} {axis}")
    seen[sid]=x
if set(seen)!=set(d):
    raise ValueError(f"incomplete metadata: missing {len(set(d)-set(seen))}")
depths=np.array([seen[sid]['axes'][axis]['maximum_root_to_tip_depth']
                 for sid in sorted(seen) for axis in ['S3','prune_only']],float)
refdepth=float(np.median(depths))
out={
  'version':'v0.1',
  'status':'AUSTRAITS_REAL_TREE_OU_TIME_REFERENCE_FROZEN',
  'n_systems':254,
  'n_families':42,
  'n_traits':13,
  'n_axis_tree_samples':508,
  'T_ref':refdepth,
  'tree_depth_summary':{
    'minimum':float(depths.min()),
    'median':refdepth,
    'maximum':float(depths.max()),
    'q025':float(np.quantile(depths,.025)),
    'q975':float(np.quantile(depths,.975))
  },
  'dimensionless_alpha_grid':[.25,1,4],
  'absolute_alpha_grid':{
    'c0p25':.25/refdepth,
    'c1':1/refdepth,
    'c4':4/refdepth
  },
  'parameter_freeze_rule':'T_ref = median of maximum tip depth of each fixed source-native exact S3/prune system tree, independent of observed K values.',
  'post_outcome_design':True,
  'OU_outcomes_opened':False
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':out['status'],'T_ref':refdepth,
                  'alpha_grid':out['absolute_alpha_grid'],'trees':len(depths)},indent=2))
