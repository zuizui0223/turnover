#!/usr/bin/env python3
"""Post-result Jena 2003 sensitivity to specially weeded quadrat 4.

Source-verified real analysis only; synthetic tests are not empirical findings.
Raw source data are downloaded only on explicit --download, never committed.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import platform
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import numpy as np
from scipy.stats import norm

MASS = 'Sown plant biom dw [g/m**2]'
MONTHS = ('2003-05', '2003-08')
REPS = ('1', '2', '3', '4', 'mean')
COLUMNS = ['intercept', 'log2_sown_species', 'functional_group_richness',
           'block_B2', 'block_B3', 'block_B4']
SOURCES = {
    'biomass2003.tab': (
        'https://doi.org/10.1594/PANGAEA.846317',
        '70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079',
        {'Accept': 'text/tab-separated-values'}),
    'plotinfo.txt': (
        'https://store.pangaea.de/Publications/Jena_Experiment/PlotInformationMainExperiment.txt',
        '7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70', {}),
}


def numeric_mass(value: Any) -> float:
    """Missing/failed observations are NOT structural zeros."""
    try:
        x = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError('missing or nonnumeric community biomass') from exc
    if not math.isfinite(x) or x < 0:
        raise ValueError('missing sentinel, nonfinite or negative community biomass')
    return x


def prepare_panel(records: list[dict], allocations: list[dict],
                  expected_plots: int | None = None) -> dict:
    meta = {}
    for row in allocations:
        p = row['plotcode'].strip()
        if not p or p in meta:
            raise ValueError('duplicate/blank allocation plot identifier')
        meta[p] = row
    if expected_plots is not None and len(meta) != expected_plots:
        raise ValueError('original plot count differs from expected value')
    observed = {}
    for row in records:
        p = row['Experimental plot'].strip()
        month = row['Date/time start'].strip()[:7]
        rep = row['Repl'].strip()
        if p not in meta or month not in MONTHS or rep not in REPS:
            raise ValueError('unexpected plot, campaign or replicate label')
        key = (p, month, rep)
        if key in observed:
            raise ValueError('duplicate plot/campaign/replicate')
        observed[key] = numeric_mass(row.get(MASS))
    required = {(p, month, rep) for p in meta for month in MONTHS for rep in REPS}
    if set(observed) != required:
        raise ValueError('missing replicate or campaign; no silent reweighting allowed')
    ids = sorted(meta)
    blocks = [meta[p]['block'].strip() for p in ids]
    if sorted(set(blocks)) != ['B1', 'B2', 'B3', 'B4']:
        raise ValueError('expected exactly four original blocks B1 through B4')
    arrays = {k: np.zeros((len(ids), 2)) for k in ('official','ordinary','careful','all_reconstructed')}
    x = []
    for i, p in enumerate(ids):
        r = meta[p]
        richness, fg = int(r['NumberSownSpecies']), int(r['NumberFunctionalGroups'])
        if richness not in (1, 2, 4, 8, 16, 60) or not 1 <= fg <= min(4, richness):
            raise ValueError('invalid original sowing allocation')
        x.append([1., math.log2(richness), float(fg),
                  *[float(blocks[i] == b) for b in ('B2','B3','B4')]])
        for j, month in enumerate(MONTHS):
            v = [observed[(p,month,rep)] for rep in ('1','2','3','4')]
            arrays['official'][i,j] = observed[(p,month,'mean')]
            arrays['ordinary'][i,j] = np.mean(v[:3])
            arrays['careful'][i,j] = v[3]
            arrays['all_reconstructed'][i,j] = np.mean(v)
    maxdiff = float(np.max(np.abs(arrays['official'] - arrays['all_reconstructed'])))
    if maxdiff > .02:
        raise ValueError(f'official mean does not match four quadrats: max difference={maxdiff}')
    return {'plot_ids':ids, 'blocks':blocks, 'X':np.asarray(x,dtype=float),
            'biomass':arrays, 'official_mean_max_abs_difference_g_m2':maxdiff}


def hc3_fit(x: np.ndarray, y: np.ndarray) -> dict:
    """Independent HC3 sandwich implementation; checked against statsmodels."""
    x = np.asarray(x,dtype=float); y = np.asarray(y,dtype=float)
    if x.ndim != 2 or y.shape != (len(x),) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('invalid regression arrays')
    if len(x) <= x.shape[1] or np.linalg.matrix_rank(x) != x.shape[1]:
        raise ValueError('rank-deficient or undersupported regression')
    beta = np.linalg.lstsq(x,y,rcond=None)[0]
    bread = np.linalg.inv(x.T@x)
    leverage = np.sum((x@bread)*x,axis=1)
    if np.any(leverage >= 1-1e-10):
        raise ValueError('HC3 leverage denominator invalid')
    adjusted_residual = (y-x@beta)/(1-leverage)
    meat = (x*adjusted_residual[:,None]).T@(x*adjusted_residual[:,None])
    variance = bread@meat@bread
    se = np.sqrt(np.maximum(np.diag(variance),0))
    with np.errstate(divide='ignore',invalid='ignore'):
        z = np.divide(beta,se,out=np.zeros_like(beta),where=se>0)
    p = 2*norm.sf(np.abs(z))
    ci = np.column_stack((beta-norm.ppf(.975)*se, beta+norm.ppf(.975)*se))
    return {'beta':beta,'se':se,'p':p,'ci95':ci}


def paired_indices(blocks: list[str], rng: np.random.Generator) -> np.ndarray:
    """A single draw is reused for both seasons and all quadrat summaries."""
    b = np.asarray(blocks)
    return np.concatenate([rng.choice(np.flatnonzero(b==k), size=int(np.sum(b==k)),replace=True)
                           for k in sorted(set(blocks))])


def read_sources(directory: Path) -> tuple[list[dict],list[dict]]:
    raw = {}
    for name, (_,digest,_) in SOURCES.items():
        path = directory/name
        if not path.exists(): raise FileNotFoundError(f'missing original source: {path}')
        raw[name] = path.read_bytes()
        if hashlib.sha256(raw[name]).hexdigest() != digest:
            raise ValueError(f'source SHA256 mismatch: {name}; do not relax identity check')
    lines = raw['biomass2003.tab'].decode('utf-8-sig').splitlines()
    start = lines.index('*/') + 1
    reader = csv.DictReader(io.StringIO('\n'.join(lines[start:])),delimiter='\t')
    if len(reader.fieldnames or []) != 84: raise ValueError('expected 84 source columns')
    records = list(reader)
    if len(records) != 820 or any(None in r for r in records):
        raise ValueError('unexpected source row count or malformed row')
    allocations = list(csv.DictReader(io.StringIO(raw['plotinfo.txt'].decode('utf-8-sig')),delimiter='\t'))
    return records,allocations


def download_sources(directory: Path) -> None:
    directory.mkdir(parents=True,exist_ok=True)
    for name, (url,digest,headers) in SOURCES.items():
        path=directory/name
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==digest: continue
        request=Request(url,headers={**headers,'User-Agent':'turnover-jena-weeding-sensitivity/1.0'})
        with urlopen(request,timeout=90) as response: data=response.read(2_000_001)
        if len(data)>2_000_000 or hashlib.sha256(data).hexdigest()!=digest:
            raise ValueError(f'download/source identity failed for {name}')
        temporary=path.with_suffix(path.suffix+'.part')
        temporary.write_bytes(data);temporary.replace(path)


def analyse(panel: dict, repetitions: int = 4000, seed: int = 20261117,
            require_original_replay: bool = True) -> dict:
    x=panel['X']; mass=panel['biomass']; responses={}
    for version in ('official','ordinary','careful'):
        for j,label in enumerate(('May','August')):
            responses[f'{version}_{label}']=np.log1p(mass[version][:,j])
    # The same full-rank X makes a fitted paired difference exactly a slope difference.
    responses['May_ordinary_minus_official']=responses['ordinary_May']-responses['official_May']
    responses['May_careful_minus_ordinary']=responses['careful_May']-responses['ordinary_May']
    responses['August_careful_minus_ordinary']=responses['careful_August']-responses['ordinary_August']
    responses['ordinary_August_minus_May']=responses['ordinary_August']-responses['ordinary_May']
    fits={key:hc3_fit(x,y) for key,y in responses.items()}
    if require_original_replay:
        for label,expected in (('May',.1678907779139575),('August',.0016810095627732557)):
            if abs(fits['official_'+label]['beta'][2]-expected)>1e-9:
                raise ValueError(f'original official-mean {label} effect not reproduced')
    names=list(responses);ys=np.column_stack([responses[k] for k in names])
    rng=np.random.default_rng(seed); draws=[];rank_fail=0
    for _ in range(repetitions):
        ix=paired_indices(panel['blocks'],rng)
        if np.linalg.matrix_rank(x[ix])!=x.shape[1]: rank_fail+=1;continue
        draws.append(np.linalg.lstsq(x[ix],ys[ix],rcond=None)[0][2,:])
    if len(draws)<.95*repetitions: raise ValueError('more than 5% bootstrap rank failures')
    limits=np.quantile(np.asarray(draws),[.025,.975],axis=0)
    summary={}
    for j,name in enumerate(names):
        f=fits[name]
        summary[name]={
            'FG_beta':float(f['beta'][2]), 'HC3_se':float(f['se'][2]),
            'HC3_p_two_sided':float(f['p'][2]),'HC3_ci95':f['ci95'][2].tolist(),
            'paired_block_stratified_plot_bootstrap_ci95':limits[:,j].tolist(),
            'all_model_coefficients':dict(zip(COLUMNS,map(float,f['beta'])))}
    return {
        'status':'JENA_2003_WEEDING_SAMPLING_SENSITIVITY_COMPLETED',
        'post_result_exploratory_analysis':True,'n_paired_plots':len(panel['plot_ids']),
        'response_units':'sown-species aboveground dry standing biomass g/m^2; log1p after raw arithmetic means',
        'original_model':'intercept + log2(sown richness) + functional-group richness + 3 original block indicators',
        'original_official_mean_coefficients_reproduced':require_original_replay,
        'official_mean_max_abs_difference_g_m2':panel['official_mean_max_abs_difference_g_m2'],
        'estimates':summary,
        'bootstrap':{'planned':repetitions,'valid':len(draws),'rank_failures':rank_fail,'seed':seed,
                     'paired_across_seasons_and_quadrat_versions':True},
        'source_sha256':{k:v[1] for k,v in SOURCES.items()},
        'limitations':[
            'Quadrats 1–3 were ordinarily weeded, not unweeded controls.',
            'Quadrat 4 differs in handling and spatial position; this is not a randomized weeding-effect test.',
            'Weed biomass is available only as a four-quadrat plot mean, preventing quadrat-level weed mediation tests.',
            'All confidence intervals are post-result exploratory marginal intervals, not multiplicity adjusted.',
            'Same 82 plots in one site/year; no new independent validation of continuous FD or phylogenetic memory.',
            'Response excludes weed biomass, roots and detached dead material; it is not annual NPP.'],
        'versions':{'python':platform.python_version(),'numpy':np.__version__}}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=Path('data'))
    parser.add_argument('--out',type=Path,default=Path('results/weeding_sensitivity.json'))
    parser.add_argument('--download',action='store_true',help='Explicitly retrieve the two pinned public source files')
    args=parser.parse_args()
    if args.download: download_sources(args.data_dir)
    records,allocations=read_sources(args.data_dir)
    panel=prepare_panel(records,allocations,expected_plots=82)
    result=analyse(panel)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'n_paired_plots':result['n_paired_plots'],
                      'estimates':result['estimates']},ensure_ascii=False))

if __name__=='__main__': main()
