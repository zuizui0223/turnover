#!/usr/bin/env python3
"""Retrospective direct-contrast audit; original Jena models remain unchanged.

Public original source hashes are required. No token, private file or raw data
is exported. Plot bootstrap conditions on the observed years at one field site.
"""
from __future__ import annotations
import argparse, hashlib, io, json, platform, urllib.request, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
import statsmodels.api as sm
import statsmodels

SOURCES = {
 'predictors_raw.zip': ('https://download.pangaea.de/dataset/923591/files/predictors_raw.zip','4af2ccca7b85b7a15b47ace87acfe0386feab79da51d3d5f67b3cf6034442e4b',None),
 'biomass02_12.zip': ('https://download.pangaea.de/dataset/923591/files/biomass02_12.zip','aa4e4904c200e4a7d35cfd713a47969b3c08f014bccfe330cefe245ee1e875db',None),
 'plotinfo.txt': ('https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt','7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70',None),
 'biomass2003.tab': ('https://doi.org/10.1594/PANGAEA.846317','70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079','text/tab-separated-values'),
}
TRAITS = ('h1','sla','leafN','SeedsTCW')
METRICS = ('FD_vs_M0','FI_vs_M0','FD_FI_vs_M0','FI_minus_FD','FD_added_to_FI')
EXPECTED_SSE = np.array([828.3085900803643,824.4758853475671,803.6540715981432,804.5931741927857])


def metrics(sse: np.ndarray) -> np.ndarray:
    sse=np.asarray(sse,dtype=float)
    if sse.shape!=(4,) or not np.isfinite(sse).all() or (sse<0).any() or sse[0]<=0 or sse[2]<=0:
        raise ValueError('Expected four finite nonnegative SSEs, with positive M0 and FI')
    return np.array([1-sse[1]/sse[0],1-sse[2]/sse[0],1-sse[3]/sse[0],
                     (sse[1]-sse[2])/sse[0],1-sse[3]/sse[2]])


def predict(x: np.ndarray,y: np.ndarray,xt: np.ndarray,w=None) -> np.ndarray:
    if w is None: w=np.ones(len(y))
    w=np.asarray(w,dtype=float)
    if w.shape!=(len(y),) or not np.isfinite(w).all() or (w<0).any():
        raise ValueError('Invalid bootstrap multiplicities')
    sx=x*np.sqrt(w)[:,None];sy=y*np.sqrt(w)
    coeff,_,rank,_=np.linalg.lstsq(sx,sy,rcond=None)
    if rank!=x.shape[1]: raise ValueError('Rank-deficient resampled design')
    return xt@coeff


def draw_weights(blocks: np.ndarray,rng: np.random.Generator) -> np.ndarray:
    blocks=np.asarray(blocks);out=np.zeros(len(blocks),dtype=int)
    for block in sorted(set(blocks)):
        ids=np.flatnonzero(blocks==block)
        out+=np.bincount(rng.choice(ids,len(ids),replace=True),minlength=len(blocks))
    return out


def scale_train_only(x,xt):
    mu=x.mean(axis=0);sd=x.std(axis=0)
    if not np.isfinite(x).all() or not np.isfinite(xt).all() or (sd<=1e-10).any():
        raise ValueError('Invalid training trait scale')
    return (x-mu)/sd,(xt-mu)/sd


def paired_coefficient(x,spring,summer,index):
    return float(np.linalg.lstsq(x,summer-spring,rcond=None)[0][index])


def acquire(root: Path) -> list[dict]:
    root.mkdir(parents=True,exist_ok=True);manifest=[]
    for name,(url,digest,accept) in SOURCES.items():
        path=root/name
        if path.exists(): raw=path.read_bytes()
        else:
            headers={'User-Agent':'turnover-direct-contrast-validation/0.1'}
            if accept: headers['Accept']=accept
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=90) as response: raw=response.read(10_000_001)
        actual=hashlib.sha256(raw).hexdigest()
        if len(raw)>10_000_000 or actual!=digest:
            raise ValueError(f'Source integrity failure: {name}, {actual}')
        path.write_bytes(raw)
        manifest.append({'name':name,'sha256':actual,'bytes':len(raw),'source':url})
    return manifest


def csv_zip(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        names=[x for x in z.namelist() if x.lower().endswith('.csv')]
        if len(names)!=1: raise ValueError('Expected one CSV in source archive')
        return pd.read_csv(z.open(names[0]))


def load_panel(root: Path,info: pd.DataFrame) -> pd.DataFrame:
    p=csv_zip(root/'predictors_raw.zip');b=csv_zip(root/'biomass02_12.zip')
    if p.shape!=(1619,87) or b.shape!=(5544,144): raise ValueError('Source schema changed')
    p=p[p.year.between(2003,2012)].copy().rename(columns={'plot':'plotcode'})
    b=b[b.year.between(2003,2012)&b.plotcode.isin(info.index)].copy()
    b['season']=b.month.map({'May':'spring','Jun':'spring','Aug':'summer','Sept':'summer'})
    if b.season.isna().any(): raise ValueError('Unmapped original biomass month')
    keys=['plotcode','year','season']
    if p.duplicated(keys).any() or b.groupby(keys).month.nunique().gt(1).any():
        raise ValueError('Ambiguous plot/year/season keys')
    v=pd.to_numeric(b['target.biomass'],errors='coerce')
    if ((v<0)&(v!=-9999)).any(): raise ValueError('Unexpected negative biomass')
    b['target.biomass']=v.mask((v==-9999)|~np.isfinite(v))
    mass=b.groupby(keys,as_index=False)['target.biomass'].median().dropna()
    panel=p.merge(mass,on=keys,validate='one_to_one').merge(info.reset_index(),on='plotcode',validate='many_to_one')
    f=[prefix+t for prefix in ('FD_','FI_') for t in TRAITS]
    if panel[f].isna().any().any() or len(panel)!=1541 or panel.plotcode.nunique()!=78:
        raise ValueError('Frozen common-case cohort changed')
    panel['y']=np.log1p(panel['target.biomass'])
    return panel.sort_values(keys).reset_index(drop=True)


def base_matrix(d: pd.DataFrame,temporal=True) -> np.ndarray:
    cols=[np.ones(len(d)),np.log2(d.NumberSownSpecies.to_numpy()),d.NumberFunctionalGroups.to_numpy()]
    if temporal: cols.extend([(d.season=='summer').astype(float).to_numpy(),(d.year-2003).to_numpy()])
    cols.extend([(d.block==b).astype(float).to_numpy() for b in ('B2','B3','B4')])
    return np.column_stack(cols).astype(float)


def intervals(point,draws):
    arr=np.asarray(draws)
    if len(arr)<1900: raise ValueError('Too few full-rank bootstrap replicates')
    return {name:{'estimate':float(v),'ci95_percentile':[float(x) for x in np.quantile(arr[:,i],[.025,.975])]}
            for i,(name,v) in enumerate(zip(METRICS,point))}


def longitudinal(panel: pd.DataFrame,B=2000) -> dict:
    train=panel[panel.year<=2007].copy();test=panel[panel.year>=2008].copy()
    if (len(train),len(test))!=(774,767): raise ValueError('Frozen year split changed')
    x0=base_matrix(train);t0=base_matrix(test);y=train.y.to_numpy();yt=test.y.to_numpy()
    fd=['FD_'+t for t in TRAITS];fi=['FI_'+t for t in TRAITS]
    designs=[]
    for features in ([],fd,fi,fd+fi):
        x=x0;t=t0
        if features:
            z,zt=scale_train_only(train[features].to_numpy(),test[features].to_numpy())
            x=np.column_stack([x0,z]);t=np.column_stack([t0,zt])
        designs.append((x,t))
    predictions=np.column_stack([predict(x,y,t) for x,t in designs])
    err=(predictions-yt[:,None])**2;sse=err.sum(axis=0)
    if not np.allclose(sse,EXPECTED_SSE,rtol=1e-10,atol=1e-8):
        raise ValueError(f'Independent original SSE reproduction failed: {sse}')
    point=metrics(sse)
    ids=sorted(panel.plotcode.unique());map_id={p:i for i,p in enumerate(ids)}
    tri=train.plotcode.map(map_id).to_numpy();tei=test.plotcode.map(map_id).to_numpy()
    loss_by_plot=np.zeros((len(ids),4));np.add.at(loss_by_plot,tei,err)
    rng=np.random.default_rng(20261114);fixed=[]
    for _ in range(B):
        draws=rng.choice(len(ids),size=len(ids),replace=True)
        w=np.bincount(draws,minlength=len(ids));fixed.append(metrics(w@loss_by_plot))
    fixed=intervals(point,fixed)
    expected_ci=[-.01580870375869039,.02178334386032681]
    if B==2000 and not np.allclose(fixed['FD_vs_M0']['ci95_percentile'],expected_ci,atol=1e-10):
        raise ValueError('Original conditional FD bootstrap not reproduced')
    blocks=panel.drop_duplicates('plotcode').set_index('plotcode').loc[ids,'block'].to_numpy()
    rng=np.random.default_rng(20261115);refit=[];failed=0
    for _ in range(B):
        w=draw_weights(blocks,rng)
        try: pred=np.column_stack([predict(x,y,t,w[tri]) for x,t in designs])
        except ValueError: failed+=1;continue
        errors=(pred-yt[:,None])**2
        refit.append(metrics((errors*w[tei,None]).sum(axis=0)))
    return {'n_plots':78,'train_cells':774,'test_cells':767,'original_SSE_reproduced':sse.tolist(),
      'conditional_paired_plot_bootstrap':{'replicates':B,'seed':20261114,'intervals':fixed},
      'same_plot_train_test_refit_bootstrap':{'replicates':len(refit),'failed_rank':failed,'seed':20261115,
        'stratification':'original field block; same plot multiplicity in train and test','intervals':intervals(point,refit)},
      'OLS_scaling_note':'Intercept and full-rank OLS make fixed training-affine scaling equivalent to recomputing scaling in each resample.',
      'uncertainty_scope':'Conditions on these observed years and one site; not independent year or site replication.'}


def seasonal(root: Path,info: pd.DataFrame,B=2000) -> dict:
    raw=(root/'biomass2003.tab').read_text(encoding='utf-8-sig')
    parts=raw.split('*/',1)
    if len(parts)!=2: raise ValueError('Missing PANGAEA metadata terminator')
    d=pd.read_csv(io.StringIO(parts[1].strip()),sep='\t')
    if d.shape!=(820,84): raise ValueError('2003 source schema mismatch')
    d=d[d.Repl.astype(str)=='mean'].copy()
    d['season']=d['Date/time start'].str[5:7].map({'05':'spring','08':'summer'})
    ycol='Sown plant biom dw [g/m**2]'
    if len(d)!=164 or d.season.isna().any() or (d[ycol]<0).any(): raise ValueError('Invalid 2003 means')
    wide=d.pivot(index='Experimental plot',columns='season',values=ycol).join(info,validate='one_to_one').sort_index()
    if len(wide)!=82 or wide[['spring','summer']].isna().any().any(): raise ValueError('Unpaired 2003 plots')
    x=base_matrix(wide,temporal=False);sp=np.log1p(wide.spring.to_numpy());su=np.log1p(wide.summer.to_numpy())
    a=sm.OLS(sp,x).fit(cov_type='HC3');b=sm.OLS(su,x).fit(cov_type='HC3')
    if not np.allclose([a.params[2],b.params[2]],[.1678907779139575,.0016810095627732557],atol=1e-10):
        raise ValueError('Original seasonal slopes not reproduced')
    delta=su-sp;m=sm.OLS(delta,x).fit(cov_type='HC3');beta=paired_coefficient(x,sp,su,2)
    assert np.isclose(beta,b.params[2]-a.params[2])
    rng=np.random.default_rng(20261116);boot=[]
    for _ in range(B):
        w=draw_weights(wide.block.to_numpy(),rng);sx=x*np.sqrt(w)[:,None];sy=delta*np.sqrt(w)
        coeff,_,rank,_=np.linalg.lstsq(sx,sy,rcond=None)
        if rank==x.shape[1]: boot.append(coeff[2])
    if len(boot)<1900: raise ValueError('Too few seasonal bootstrap draws')
    return {'n_paired_plots':82,'response':'log1p(August g/m2)-log1p(May g/m2)',
      'original_May_FG_beta':float(a.params[2]),'original_August_FG_beta':float(b.params[2]),
      'August_minus_May_FG_beta':beta,'HC3_SE':float(m.bse[2]),'HC3_p_two_sided':float(m.pvalues[2]),
      'HC3_ci95':m.conf_int()[2].tolist(),'block_stratified_paired_bootstrap_ci95':np.quantile(boot,[.025,.975]).tolist(),
      'bootstrap_replicates':len(boot),'bootstrap_seed':20261116,
      'source_caveat':'Original official plot means include subsample 4 with special careful weeding; original estimand is unchanged.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();manifest=acquire(args.source_dir)
    info=pd.read_csv(args.source_dir/'plotinfo.txt',sep='\t').set_index('plotcode')
    if len(info)!=82 or not info.index.is_unique: raise ValueError('Invalid plot allocation')
    panel=load_panel(args.source_dir,info)
    result={'status':'RETROSPECTIVE_DIRECT_CONTRAST_VALIDATION_COMPLETED','version':'v0.1',
      'source_manifest':manifest,'longitudinal':longitudinal(panel),'seasonal':seasonal(args.source_dir,info),
      'interpretation_boundary':['Post-result validation, not preregistered confirmation.',
        'No change to original four-trait models, years, cohorts or original published result files.',
        'A confidence interval including zero is not evidence of zero or equivalence.',
        'Repeated plots in one experiment; imputed concurrent cover-based traits; no causal or phylogenetic-memory test.'],
      'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'statsmodels':statsmodels.__version__}}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('DIRECT_CONTRAST_RESULT',json.dumps(result,ensure_ascii=False))

if __name__=='__main__': main()
