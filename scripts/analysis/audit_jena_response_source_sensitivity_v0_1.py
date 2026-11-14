#!/usr/bin/env python3
"""Retrospective response-source robustness, unchanged original FD/FI models."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from audit_jena_units_management_v0_1 import ANNUAL,parse_official
from validate_jena_direct_contrasts_v0_1 import load_panel,base_matrix,scale_train_only,draw_weights,metrics,METRICS,TRAITS

def source_responses(year,compiled_log,annual_mass):
    year=np.asarray(year);old=np.asarray(compiled_log,float);annual=np.asarray(annual_mass,float)
    keep=(year>2010)|np.isfinite(annual)
    if np.any(annual[np.isfinite(annual)]<0):raise ValueError('Negative official response')
    yy=np.column_stack([old,np.where(year<=2010,np.log1p(annual),old)])
    return yy[keep],keep

def source_panel(root):
    info=pd.read_csv(root/'plotinfo.txt',sep='\t').set_index('plotcode');panel=load_panel(root,info)
    frames=[]
    for year in ANNUAL:
        path=root/('biomass2003.tab' if year==2003 else f'biomass{year}.tab')
        d,_=parse_official(path.read_bytes(),year)
        d=d[d.rep.isin(['1','2','3','4'])&d['plot'].isin(info.index)]
        frames.append(d.groupby(['plot','year','season'],as_index=False).mass.median())
    med=pd.concat(frames).rename(columns={'plot':'plotcode','mass':'annual_mass'})
    merged=panel.merge(med,on=['plotcode','year','season'],how='left',validate='one_to_one')
    if len(merged)!=1541:raise ValueError('Original cohort expanded or changed')
    return merged

def scope_fit(frame,max_year):
    d=frame[frame.year<=max_year].copy();original_n=len(d)
    y,keep=source_responses(d.year.to_numpy(),d.y.to_numpy(),d.annual_mass.to_numpy())
    d=d.loc[keep].reset_index(drop=True)
    train=(d.year<=2007).to_numpy();test=~train;tr=d[train];te=d[test]
    if tr.plotcode.nunique()<50 or te.plotcode.nunique()<50:raise ValueError('Too few original plot clusters')
    designs=[]
    for feat in ([],['FD_'+t for t in TRAITS],['FI_'+t for t in TRAITS],['FD_'+t for t in TRAITS]+['FI_'+t for t in TRAITS]):
        x=base_matrix(tr);xt=base_matrix(te)
        if feat:
            z,zt=scale_train_only(tr[feat].to_numpy(),te[feat].to_numpy());x=np.column_stack([x,z]);xt=np.column_stack([xt,zt])
        designs.append((x,xt))
    ids=sorted(d.plotcode.unique());mapping={p:i for i,p in enumerate(ids)}
    ti=tr.plotcode.map(mapping).to_numpy();vi=te.plotcode.map(mapping).to_numpy()
    blocks=d.drop_duplicates('plotcode').set_index('plotcode').loc[ids,'block'].to_numpy()
    def score(w):
        pred=[]
        for x,xt in designs:
            a=x*np.sqrt(w[ti])[:,None];b=y[train]*np.sqrt(w[ti])[:,None]
            coeff,_,rank,_=np.linalg.lstsq(a,b,rcond=None)
            if rank!=x.shape[1]:raise ValueError('Rank-deficient source bootstrap')
            pred.append(xt@coeff)
        loss=(np.stack(pred,axis=1)-y[test,None,:])**2
        sse=(loss*w[vi,None,None]).sum(axis=0)
        return np.stack([metrics(sse[:,j]) for j in range(2)]),sse
    point,sse=score(np.ones(len(ids)));rng=np.random.default_rng(20261118);draws=[];failed=0
    for _ in range(2000):
        try:v,_=score(draw_weights(blocks,rng))
        except ValueError:failed+=1;continue
        draws.append(v)
    if len(draws)<1900:raise ValueError('Insufficient full-rank source-bootstrap draws')
    arr=np.array(draws);worlds={}
    for j,name in enumerate(('compiled','annual_2003_2010_then_compiled')):
        worlds[name]={'sse_models_order_M0_FD_FI_both':sse[:,j].tolist(),'metrics':{key:{'estimate':float(point[j,i]),'paired_refit_ci95':np.quantile(arr[:,j,i],[.025,.975]).tolist()} for i,key in enumerate(METRICS)}}
    delta=arr[:,1]-arr[:,0]
    change={key:{'estimate':float(point[1,i]-point[0,i]),'paired_refit_ci95':np.quantile(delta[:,i],[.025,.975]).tolist()} for i,key in enumerate(METRICS)}
    return {'max_year':max_year,'original_cells':original_n,'common_cells':len(d),'jointly_excluded_missing_annual':original_n-len(d),
      'train_cells':int(train.sum()),'test_cells':int(test.sum()),'n_plot_clusters':len(ids),'train_years':sorted(tr.year.unique().tolist()),'test_years':sorted(te.year.unique().tolist()),
      'replicates':len(draws),'failed_rank':failed,'seed':20261118,'worlds':worlds,'gain_change_annual_minus_compiled':change,
      'boundary':'Paired source sensitivity only; both worlds have identical rows and predictors. Conditions on one site and observed years.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    d=source_panel(a.source_dir)
    out={'status':'RETROSPECTIVE_JENA_RESPONSE_SOURCE_SENSITIVITY_COMPLETE','scopes':{'full_panel_partial_source_replacement':scope_fit(d,2012),'all_response_years_source_verified':scope_fit(d,2010)},
      'constraints':['Original results preserved. No source chosen by a favorable gain or p-value.','2011–2012 remain compiled in the full-panel scope; the shortened scope ends in 2010.','No new independent experiment, no causal FD or weeding mechanism, no source-error verdict.']}
    a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print('RESPONSE_SOURCE_SENSITIVITY',json.dumps(out,allow_nan=False))
if __name__=='__main__':main()
