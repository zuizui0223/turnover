#!/usr/bin/env python3
"""Post-outcome evaluation uncertainty; frozen Jena fits and source population unchanged.
All three FI-focused contrasts are exploratory. Resampling is conditional on fits.
"""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import numpy as np
KEYS=('M0','M1_FD','M2_FI','M3_FD_FI')

def compare(y,predictions,plot_ids,reps=2000,seed=20261114):
    y=np.asarray(y,dtype=float);ids=np.asarray(plot_ids,dtype=str)
    if y.ndim!=1 or ids.shape!=y.shape or len(set(ids))<2 or reps<2:
        raise ValueError('At least two clusters and aligned vectors are required')
    if any(k not in predictions for k in KEYS):raise ValueError('All four fixed models required')
    p=[np.asarray(predictions[k],dtype=float) for k in KEYS]
    if not np.isfinite(y).all() or any(a.shape!=y.shape or not np.isfinite(a).all() for a in p):
        raise ValueError('Predictions must align and be finite')
    err=np.stack([(y-a)**2 for a in p],axis=1)
    unique=sorted(set(ids));indices={i:np.flatnonzero(ids==i) for i in unique}
    names=('FD_over_baseline','FI_over_baseline','FI_minus_FD_common_baseline','FD_added_to_FI')
    def effect(sse):
        if sse[0]<=0 or sse[2]<=0:raise ValueError('Degenerate error denominators')
        return np.array([1-sse[1]/sse[0],1-sse[2]/sse[0],(sse[1]-sse[2])/sse[0],1-sse[3]/sse[2]])
    point=effect(err.sum(axis=0));rng=np.random.default_rng(seed);draws=[]
    for _ in range(reps):
        sampled=rng.choice(unique,size=len(unique),replace=True)
        rows=np.concatenate([indices[i] for i in sampled])
        draws.append(effect(err[rows].sum(axis=0)))
    draws=np.asarray(draws)
    return {'repetitions':reps,'seed':seed,'n_plot_clusters':len(unique),'n_test_rows':len(y),
            'uncertainty':'paired holdout-plot resampling conditional on fixed fitted models; no training uncertainty',
            'contrasts':{k:{'point':float(point[i]),'ci95':np.quantile(draws[:,i],[.025,.975]).tolist(),
                'ci_secondary_family_98_333':np.quantile(draws[:,i],[.05/6,1-.05/6]).tolist() if i else None}
                for i,k in enumerate(names)}}

def selftest():
    p={k:np.ones(4) for k in KEYS};r=compare(np.zeros(4),p,['a','a','b','b'],100)
    assert all(x['point']==0 and x['ci95']==[0,0] for x in r['contrasts'].values())
    p={'M0':np.full(6,2.),'M1_FD':np.full(6,1.5),'M2_FI':np.full(6,1.),'M3_FD_FI':np.full(6,.5)}
    r=compare(np.zeros(6),p,['a','a','b','b','c','c'],100)
    assert math.isclose(r['contrasts']['FI_over_baseline']['point'],.75)
    assert math.isclose(r['contrasts']['FI_minus_FD_common_baseline']['point'],.3125)
    assert math.isclose(r['contrasts']['FD_added_to_FI']['point'],.75)
    try:compare([0,0],{k:[1] for k in KEYS},['a','b'])
    except ValueError:pass
    else:raise AssertionError('Misaligned vectors accepted')
    return {'status':'PAIRED_UNCERTAINTY_TESTS_PASS','tests':3}

def run(args):
    from fit_jena_923591_fd_biomass_time_transport_v0_1 import table_rows,fit_predict,TRAITS
    directory=Path('results/biomass_jena_2003_source_v0_1')
    reference=json.loads((directory/'longitudinal_fd_biomass_time_transport_v0_1.json').read_text())
    train,test,blocks,exclusions=table_rows(args.predictors,args.biomass,args.plotinfo,
        directory/'longitudinal_fd_biomass_join_qa_v0_1.json')
    specs={'M0':[],'M1_FD':['FD_'+t for t in TRAITS],'M2_FI':['FI_'+t for t in TRAITS],
           'M3_FD_FI':['FD_'+t for t in TRAITS]+['FI_'+t for t in TRAITS]}
    predictions={};checks={}
    for name,cols in specs.items():
        fit=fit_predict(train,test,blocks,cols)
        old=reference['models'][name]
        delta=abs(fit['sse']-old['sse'])
        if delta>1e-8:raise ValueError('Locked SSE changed for '+name)
        if set(fit['coefficients'])!=set(old['coefficients']):raise ValueError('Model specification changed')
        coefdelta=max(abs(fit['coefficients'][k]-old['coefficients'][k]) for k in old['coefficients'])
        if coefdelta>1e-8:raise ValueError('Locked coefficients changed')
        predictions[name]=fit['prediction'];checks[name]={'SSE_abs_difference':delta,'max_coefficient_abs_difference':coefdelta}
    if len(train)!=774 or len(test)!=767:raise ValueError('Frozen population changed')
    report=compare([r['y'] for r in test],predictions,[r['plot'] for r in test])
    oldci=reference['plot_bootstrap']['gain_FD_percentile_CI95']
    if not np.allclose(oldci,report['contrasts']['FD_over_baseline']['ci95'],atol=1e-10,rtol=0):
        raise ValueError('Original FD evaluation CI not reproduced')
    report.update(status='JENA_FIXED_MODEL_PAIRED_UNCERTAINTY_COMPLETE',post_outcome_extension=True,
        original_results_reproduced=True,model_replay_checks=checks,train_rows=len(train),
        source='PANGAEA 923591; same 78 Jena plots, 2003–2007 train and 2008–2012 evaluation',
        scope='Exploratory uncertainty of fixed heldout comparisons; no feature/model tuning; no independent spatial validation',
        caution=['Same plots in train and test.','PCA-imputed source traits and concurrent cover-weighted indices.',
                 'The three FI-focused contrasts were added after observing point gains.',
                 '98.333% marginal percentile intervals are a Bonferroni-style three-comparison sensitivity, not exact simultaneous guarantees.',
                 'No causal ecosystem mechanism inferred.'])
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for k in ('predictors','biomass','plotinfo','out'):p.add_argument('--'+k)
    p.add_argument('--self-test',action='store_true');a=p.parse_args()
    if a.self_test:print(json.dumps(selftest()))
    else:
        if not all((a.predictors,a.biomass,a.plotinfo,a.out)):p.error('all four paths required')
        result=run(a);out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print('PAIRED_FD_FI_RESULT',json.dumps(result,sort_keys=True))
