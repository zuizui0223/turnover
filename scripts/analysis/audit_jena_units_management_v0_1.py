#!/usr/bin/env python3
"""Post-outcome validation of Jena biomass units and fourth-subsample management.

Preserves original result files. Outputs aggregates only, not raw records.
Exact source-key matches are independent of observed biomass values.
"""
from __future__ import annotations
import argparse,hashlib,io,json,platform,urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from validate_jena_direct_contrasts_v0_1 import acquire,csv_zip,base_matrix,draw_weights

ANNUAL={2003:846317,2004:846319,2005:846348,2006:846582,2007:846583,2008:846532,2009:866304,2010:866305}
KEYS=['plot','year','season','rep']
B=2000

def clean_mass(values):
    a=pd.to_numeric(values,errors='coerce').astype(float)
    a=a.mask((a==-9999)|~np.isfinite(a))
    if (a<0).any():raise ValueError('Unexpected negative dry mass')
    return a

def parse_official(raw:bytes,year:int):
    text=raw.decode('utf-8-sig');parts=text.split('*/',1)
    if len(parts)!=2:raise ValueError('PANGAEA metadata terminator missing')
    d=pd.read_csv(io.StringIO(parts[1].strip()),sep='\t',dtype={'Repl':str})
    masscols=[c for c in d if c.lower().startswith('sown plant') and 'biom' in c.lower()]
    if len(masscols)!=1:raise ValueError('Ambiguous sown-community biomass column')
    col=masscols[0]
    if '[g/m**2]' not in col and '[g/m^2]' not in col:raise ValueError('Source unit not explicit g/m2')
    datecol='Date/time start' if 'Date/time start' in d else 'Date/time'
    date=pd.to_datetime(d[datecol],errors='raise')
    if not date.dt.year.eq(year).all():raise ValueError('Official year mismatch')
    season=date.dt.month.map({5:'spring',6:'spring',8:'summer',9:'summer'})
    if season.isna().any():raise ValueError('Unexpected sampling season')
    out=pd.DataFrame({'plot':d['Experimental plot'].astype(str).str.strip(),'year':year,
          'season':season,'rep':d['Repl'].astype(str).str.strip(),'mass':clean_mass(d[col])})
    return out,{'doi':f'10.1594/PANGAEA.{ANNUAL.get(year,"unknown")}',
         'year':year,'rows':len(d),'unit':'g/m2','response_column':col,
         'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
         'metadata_careful_weeding_note':('extra carefully weeded' in parts[0].lower())}

def join_exact(official,compiled):
    for d in (official,compiled):
        if d.duplicated(KEYS).any():raise ValueError('Duplicate exact sampling keys')
    return official.merge(compiled,on=KEYS,how='inner',validate='one_to_one',suffixes=('_official','_compiled'))

def unit_diagnostics(compiled,official):
    x=np.asarray(compiled,float);y=np.asarray(official,float)
    if x.shape!=y.shape:raise ValueError('Paired values must have same shape')
    keep=np.isfinite(x)&np.isfinite(y);x=x[keep];y=y[keep]
    if not len(x):raise ValueError('No finite paired measurements')
    detail={}
    for c in (1,10,.1,100,.01):
        diff=x*c-y;match=np.isclose(x*c,y,atol=.051,rtol=1e-6)
        detail[f'{c:g}']={'n_within_tolerance':int(match.sum()),
          'fraction_within_tolerance':float(match.mean()),'max_absolute_difference':float(np.abs(diff).max()),
          'median_absolute_difference':float(np.median(np.abs(diff)))}
    pos=(x>0)&(y>0)
    return {'n_finite_pairs':len(x),'absolute_tolerance_g_m2':.051,'relative_tolerance':1e-6,
       'n_positive_pairs':int(pos.sum()),'median_official_over_compiled_positive':float(np.median(y[pos]/x[pos])) if pos.any() else None,
       'factors_to_multiply_compiled':detail}

def sample_summaries(d):
    z=d.copy();z['rep']=pd.to_numeric(z.rep,errors='coerce');z=z[z.rep.isin([1,2,3,4])]
    if z.duplicated(['plot','season','rep']).any():raise ValueError('Duplicate 2003 subsample')
    wide=z.pivot(index=['plot','season'],columns='rep',values='mass')
    if not set([1,2,3,4]).issubset(wide.columns) or wide[[1,2,3,4]].isna().any().any():
        raise ValueError('All four positive-or-zero subsamples required; missing is not zero')
    return pd.DataFrame({'all_1to4':wide[[1,2,3,4]].mean(axis=1),
                         'ordinary_1to3':wide[[1,2,3]].mean(axis=1),'special_4':wide[4]})

def fit_response(x,y,index=2):
    if not np.isfinite(x).all() or not np.isfinite(y).all() or np.linalg.matrix_rank(x)!=x.shape[1]:
        raise ValueError('Invalid response or design rank')
    model=sm.OLS(y,x).fit(cov_type='HC3')
    return {'beta':float(model.params[index]),'HC3_SE':float(model.bse[index]),
            'HC3_p_two_sided':float(model.pvalues[index]),'HC3_ci95':model.conf_int()[index].tolist()}

def management_analysis(d,info):
    summaries=sample_summaries(d);ids=sorted(info.index)
    if len(ids)!=82 or len(summaries)!=164:raise ValueError('Expected 82 paired original plots')
    x=base_matrix(info.loc[ids],temporal=False)
    original=d[d.rep.eq('mean')].pivot(index='plot',columns='season',values='mass').loc[ids]
    responses={};results={}
    for label in ('official_mean','all_1to4','ordinary_1to3','special_4'):
        values=original if label=='official_mean' else summaries[label].unstack('season').loc[ids]
        sp=np.log1p(values.spring.to_numpy());su=np.log1p(values.summer.to_numpy())
        for season,y in [('spring',sp),('summer',su),('summer_minus_spring',su-sp)]:
            key=f'{label}:{season}';responses[key]=y;results[key]=fit_response(x,y)
    if not np.allclose([results['official_mean:spring']['beta'],results['official_mean:summer']['beta']],
                       [.1678907779139575,.0016810095627732557],atol=1e-10):
        raise ValueError('Original May/August slope reproduction failed')
    for season in ('spring','summer','summer_minus_spring'):
        for a,b,label in [('ordinary_1to3','all_1to4','exclude4_minus_all'),('special_4','ordinary_1to3','special4_minus_ordinary')]:
            key=f'{label}:{season}';responses[key]=responses[f'{a}:{season}']-responses[f'{b}:{season}']
            results[key]=fit_response(x,responses[key])
    names=list(responses);Y=np.column_stack([responses[k] for k in names]);draws=[];rng=np.random.default_rng(20261117)
    for _ in range(B):
        w=draw_weights(info.loc[ids].block.to_numpy(),rng);sx=x*np.sqrt(w)[:,None];sy=Y*np.sqrt(w)[:,None]
        beta,_,rank,_=np.linalg.lstsq(sx,sy,rcond=None)
        if rank!=x.shape[1]:continue
        draws.append(beta[2])
    if len(draws)<1900:raise ValueError('Too few paired bootstrap fits')
    for i,k in enumerate(names):results[k]['paired_plot_bootstrap_ci95']=np.quantile(np.array(draws)[:,i],[.025,.975]).tolist()
    mean_dif=(summaries.all_1to4.unstack('season').loc[ids]-original).to_numpy()
    return {'n_plots':82,'unit':'g/m2','response_transform':'log1p','model':'log2(sown richness)+FG richness+original block',
      'replicates':len(draws),'seed':20261117,'resampling':'within-block paired original plots; common weights for all variants',
      'max_abs_reconstructed_mean_minus_official_mean':float(np.max(np.abs(mean_dif))),
      'results':results,'boundary':'All variants are post-result sensitivity analyses, not randomized causal weeding comparisons; intervals are marginal, not multiplicity-adjusted.'}

def annual_reconcile(root,info):
    comp=csv_zip(root/'biomass02_12.zip');comp=comp[comp.plotcode.isin(info.index)].copy()
    comp['season']=comp.month.map({'May':'spring','Jun':'spring','Aug':'summer','Sept':'summer'})
    comp=comp.rename(columns={'plotcode':'plot','subsample':'rep','target.biomass':'mass'})
    comp.rep=pd.to_numeric(comp.rep,errors='raise').astype(int).astype(str);comp.mass=clean_mass(comp.mass)
    reports=[];official2003=None
    for year,doi in ANNUAL.items():
        path=root/('biomass2003.tab' if year==2003 else f'biomass{year}.tab')
        try:
            if not path.exists():
                req=urllib.request.Request(f'https://doi.org/10.1594/PANGAEA.{doi}',headers={'Accept':'text/tab-separated-values','User-Agent':'turnover-units-management-audit/0.1'})
                with urllib.request.urlopen(req,timeout=75) as res:raw=res.read(10_000_001)
                if len(raw)>10_000_000:raise ValueError('Official source unexpectedly large')
                path.write_bytes(raw)
            raw=path.read_bytes();official,meta=parse_official(raw,year)
            if year==2003:official2003=official
            one=official[official.rep.isin(['1','2','3','4']) & official['plot'].isin(info.index)].copy()
            two=comp[comp.year.eq(year)][KEYS+['mass']].copy()
            joined=join_exact(one,two)
            report={'status':'EXACT_KEY_COMPARISON_COMPLETED','source':meta,'n_official_individual_rows':len(one),
               'n_compiled_individual_rows':len(two),'n_exact_key_pairs':len(joined),
               'n_both_missing':int((joined.mass_official.isna()&joined.mass_compiled.isna()).sum()),
               'n_missing_only_one_source':int((joined.mass_official.isna()^joined.mass_compiled.isna()).sum()),
               'comparison':unit_diagnostics(joined.mass_compiled,joined.mass_official)}
            reports.append(report)
        except Exception as exc:
            reports.append({'year':year,'doi':f'10.1594/PANGAEA.{doi}','status':'SOURCE_RECONCILIATION_UNRESOLVED',
                            'error_type':type(exc).__name__,'error':str(exc)[:300]})
            if year==2003:raise
    if official2003 is None:raise ValueError('No verified 2003 original')
    return reports,official2003

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    manifest=acquire(a.source_dir);info=pd.read_csv(a.source_dir/'plotinfo.txt',sep='\t').set_index('plotcode').sort_index()
    annual,official=annual_reconcile(a.source_dir,info)
    result={'status':'RETROSPECTIVE_JENA_UNIT_AND_MANAGEMENT_AUDIT_COMPLETED','version':'v0.1',
      'original_input_manifest':manifest,'annual_source_reconciliation':annual,'management_2003':management_analysis(official,info),
      'scope':['Post-outcome data validation and sensitivity, one Jena experimental site.',
       'No original result overwrite; no selected significant variant replaces the original estimand.',
       'No inferred whole-plant or annual NPP; no cross-site or evolutionary-memory mechanism tested.',
       '2011–2012 original year datasets not verified in this audit; no extension of unit validation to those years.'],
      'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__}}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('JENA_UNITS_MANAGEMENT_RESULT',json.dumps(result,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()
