#!/usr/bin/env python3
"""Summarize source-key and missingness discrepancies, never repair by value."""
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
from audit_jena_units_management_v0_1 import ANNUAL,KEYS,parse_official,clean_mass
from validate_jena_direct_contrasts_v0_1 import csv_zip

def inventory(d):
 return {f'{s}/rep{r}':int(n) for (s,r),n in d.groupby(['season','rep']).size().items()}

def main(root):
 info=pd.read_csv(root/'plotinfo.txt',sep='\t');allowed=set(info.plotcode)
 raw=csv_zip(root/'biomass02_12.zip')
 raw=raw[raw.plotcode.isin(allowed)].copy();raw['season']=raw.month.map({'May':'spring','Jun':'spring','Aug':'summer','Sept':'summer'})
 b=raw[['plotcode','year','season','subsample','target.biomass']].rename(columns={'plotcode':'plot','subsample':'rep','target.biomass':'mass'})
 b.rep=pd.to_numeric(b.rep).astype(int).astype(str);b.mass=clean_mass(b.mass)
 out=[]
 for year in ANNUAL:
  f=root/('biomass2003.tab' if year==2003 else f'biomass{year}.tab')
  if not f.exists():continue
  a,meta=parse_official(f.read_bytes(),year);a=a[a['plot'].isin(allowed)&a.rep.isin(['1','2','3','4'])]
  c=b[b.year.eq(year)];j=a.merge(c,on=KEYS,how='outer',suffixes=('_official','_compiled'),indicator=True,validate='one_to_one')
  left=j[j['_merge']=='left_only'];right=j[j['_merge']=='right_only'];both=j[j['_merge']=='both']
  misses=both[both.mass_official.isna()^both.mass_compiled.isna()]
  entry={'year':year,'official_inventory':inventory(a),'compiled_inventory':inventory(c),
   'official_only_inventory':inventory(left),'compiled_only_inventory':inventory(right),
   'official_missing_compiled_present':int((both.mass_official.isna()&both.mass_compiled.notna()).sum()),
   'compiled_missing_official_present':int((both.mass_compiled.isna()&both.mass_official.notna()).sum()),
   'missingness_disagreement_inventory':inventory(misses)}
  if len(left) and len(right) and not left.duplicated(['plot','year','rep']).any() and not right.duplicated(['plot','year','rep']).any():
   shift=left[['plot','year','rep','season','mass_official']].merge(right[['plot','year','rep','season','mass_compiled']],on=['plot','year','rep'],suffixes=('_official','_compiled'),validate='one_to_one')
   finite=shift.dropna(subset=['mass_official','mass_compiled'])
   entry['unmatched_same_plot_rep_different_season_diagnostic']={'n_pairs':len(shift),'n_finite':len(finite),'n_equal_within_0051':int(np.isclose(finite.mass_official,finite.mass_compiled,atol=.051,rtol=1e-6).sum()),'n_different_season':int((shift.season_official!=shift.season_compiled).sum()),'repaired_or_relabelled':False}
  groupkeys=['plot','year','season']
  ma=a.groupby(groupkeys,as_index=False).mass.median().rename(columns={'mass':'official_median'})
  mc=c.groupby(groupkeys,as_index=False).mass.median().rename(columns={'mass':'compiled_median'})
  med=ma.merge(mc,on=groupkeys,how='outer',validate='one_to_one')
  finite=med.dropna(subset=['official_median','compiled_median'])
  entry['plot_season_median_comparison']={'n_keys':len(med),'n_finite_pairs':len(finite),'n_equal_within_0051':int(np.isclose(finite.official_median,finite.compiled_median,atol=.051,rtol=1e-6).sum()),'max_abs_difference':float(np.abs(finite.official_median-finite.compiled_median).max()),'missing_only_one':int((med.official_median.isna()^med.compiled_median.isna()).sum())}
  if len(left) and len(right) and not left.duplicated(groupkeys).any() and not right.duplicated(groupkeys).any():
   renumber=left[groupkeys+['rep','mass_official']].merge(right[groupkeys+['rep','mass_compiled']],on=groupkeys,suffixes=('_official','_compiled'),validate='one_to_one')
   finite=renumber.dropna(subset=['mass_official','mass_compiled'])
   entry['same_plot_season_different_replicate_diagnostic']={'n_pairs':len(renumber),'n_finite':len(finite),'n_equal_within_0051':int(np.isclose(finite.mass_official,finite.mass_compiled,atol=.051,rtol=1e-6).sum()),'replicate_label_pairs':sorted(set(renumber.rep_official+'->'+renumber.rep_compiled)),'repaired_or_relabelled':False}
  out.append(entry)
 return {'status':'SOURCE_CALENDAR_AND_MISSINGNESS_DIAGNOSTIC_COMPLETE','comparisons':out,'scope':'Descriptive exact-key source reconciliation; no source row relabelled or any inference refitted.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 result=main(a.source_dir);a.out.write_text(json.dumps(result,indent=2)+'\n');print('SAMPLE_SOURCE_DIAGNOSTIC',json.dumps(result))
