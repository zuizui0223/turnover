#!/usr/bin/env python3
"""Exploratory paired Jena sown/non-sown aboveground biomass endpoint analysis.

Original official four-quadrat means only: a weed mean is not available by quadrat.
No interpretation as randomized weeding effects, total ecosystem mass, or NPP.
"""
from __future__ import annotations
import argparse
import json
import math
import platform
from pathlib import Path
from typing import Any
import numpy as np
from weeding_sensitivity import (MASS, MONTHS, SOURCES, COLUMNS, read_sources,
                                hc3_fit, paired_indices)

WEEDS = 'Weeds biom dw [g/m**2]'

def _mass(value: Any) -> float | None:
    """A blank or -9999 is missing; true zero is retained, not imputed."""
    if value is None or not str(value).strip():
        return None
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('non-numeric community biomass') from exc
    if x == -9999:
        return None
    if not math.isfinite(x) or x < 0:
        raise ValueError('nonfinite or unexpected negative biomass')
    return x

def partition_panel(records: list[dict], allocations: list[dict]) -> dict:
    meta = {}
    for row in allocations:
        p = row['plotcode'].strip()
        if not p or p in meta:
            raise ValueError('duplicate or blank plot allocation')
        meta[p] = row
    means = {}
    for row in records:
        if row['Repl'].strip() != 'mean':
            continue
        p = row['Experimental plot'].strip()
        month = row['Date/time start'].strip()[:7]
        key = (p, month)
        if p not in meta or month not in MONTHS or key in means:
            raise ValueError('unknown or duplicate plot campaign mean')
        means[key] = (_mass(row.get(MASS)), _mass(row.get(WEEDS)))
    required = {(p, m) for p in meta for m in MONTHS}
    if set(means) != required:
        raise ValueError('missing plot campaign mean row')
    keep, excluded = [], []
    for p in sorted(meta):
        missing = [{'month':m, 'endpoint':ep}
                   for m in MONTHS
                   for ep, val in zip(('sown', 'weeds'), means[(p,m)]) if val is None]
        if missing:
            excluded.append({'plot':p, 'missing':missing})
        else:
            keep.append(p)
    if not keep:
        raise ValueError('no complete paired plots')
    blocks = [meta[p]['block'].strip() for p in keep]
    if sorted(set(blocks)) != ['B1','B2','B3','B4']:
        raise ValueError('expected original four blocks')
    x = []
    for p, block in zip(keep, blocks):
        richness = int(meta[p]['NumberSownSpecies'])
        fg = int(meta[p]['NumberFunctionalGroups'])
        if richness not in (1,2,4,8,16,60) or not 1 <= fg <= min(4,richness):
            raise ValueError('invalid sowing treatment metadata')
        x.append([1., math.log2(richness), float(fg)] +
                 [float(block == b) for b in ('B2','B3','B4')])
    sown = np.array([[means[(p,m)][0] for m in MONTHS] for p in keep], dtype=float)
    weeds = np.array([[means[(p,m)][1] for m in MONTHS] for p in keep], dtype=float)
    return {'plot_ids':keep, 'blocks':blocks, 'X':np.asarray(x),
            'mass':{'sown':sown, 'weeds':weeds, 'combined':sown+weeds},
            'excluded':excluded, 'original_n_plots':len(meta)}

def outcome_matrix(panel: dict) -> tuple[list[str], np.ndarray]:
    columns = {}
    for j, season in enumerate(('May','August')):
        for endpoint in ('sown','weeds','combined'):
            raw = panel['mass'][endpoint][:,j]
            columns[f'raw_{endpoint}_{season}'] = raw
            columns[f'log_{endpoint}_{season}'] = np.log1p(raw)
        columns[f'log_combined_minus_sown_{season}'] = (
            columns[f'log_combined_{season}'] - columns[f'log_sown_{season}'])
    return list(columns), np.column_stack(list(columns.values()))

def holm(pvalues: list[float]) -> list[float]:
    p = np.asarray(pvalues, dtype=float)
    if p.ndim != 1 or not len(p) or not np.isfinite(p).all() or np.any((p<0)|(p>1)):
        raise ValueError('invalid p-values for Holm correction')
    order = np.argsort(p)
    adj = np.minimum(1.,np.maximum.accumulate(p[order] * np.arange(len(p),0,-1)))
    result = np.zeros(len(p)); result[order] = adj
    return result.tolist()

def fit_partition(panel: dict, repetitions: int = 4000, seed: int = 20261118) -> dict:
    if repetitions <= 0:
        raise ValueError('positive number of bootstrap replicates required')
    names, ys = outcome_matrix(panel)
    x = panel['X']
    fits = [hc3_fit(x,ys[:,i]) for i in range(len(names))]
    additivity = []
    for season in ('May','August'):
        coefs = {ep: fits[names.index(f'raw_{ep}_{season}')]['beta']
                 for ep in ('sown','weeds','combined')}
        additivity.append(float(np.max(np.abs(coefs['combined']-coefs['sown']-coefs['weeds']))))
    if max(additivity) > 1e-8:
        raise ValueError('raw endpoint coefficient additivity failed')
    rng = np.random.default_rng(seed)
    draws, failures = [], 0
    for _ in range(repetitions):
        idx = paired_indices(panel['blocks'],rng)
        if np.linalg.matrix_rank(x[idx]) != x.shape[1]:
            failures += 1
            continue
        draws.append(np.linalg.lstsq(x[idx],ys[idx],rcond=None)[0][2])
    if len(draws) < .95 * repetitions:
        raise ValueError('too many rank-deficient bootstrap draws')
    bounds = np.quantile(np.asarray(draws),[.025,.975],axis=0)
    estimates = {}
    for i,name in enumerate(names):
        f = fits[i]
        estimates[name] = {
            'FG_beta':float(f['beta'][2]), 'HC3_se':float(f['se'][2]),
            'HC3_p_nominal':float(f['p'][2]), 'HC3_ci95':f['ci95'][2].tolist(),
            'paired_plot_bootstrap_ci95':bounds[:,i].tolist(),
            'all_coefficients':dict(zip(COLUMNS,map(float,f['beta'])))}
    family = [f'log_{ep}_{ss}' for ss in ('May','August') for ep in ('weeds','combined')]
    adj = holm([estimates[n]['HC3_p_nominal'] for n in family])
    for n,p in zip(family,adj):
        estimates[n]['HC3_p_Holm_four_new_endpoints'] = p
    return {
        'status':'JENA_2003_PAIRED_BIOMASS_ENDPOINT_PARTITION_COMPLETED',
        'post_result_exploratory':True,
        'original_n_plots':panel['original_n_plots'],
        'n_complete_paired_plots':len(panel['plot_ids']),
        'excluded_plot_records':panel['excluded'],
        'n_complete_plot_seasons':2*len(panel['plot_ids']),
        'model':'intercept + log2(sown richness) + FG richness + original field blocks',
        'raw_response_units':'g/m^2 of source-specified harvested aboveground dry mass',
        'combined_definition':'official sown mean + official non-sown weed mean; excludes roots/dead/unidentified material',
        'official_four_quadrat_means_only':True,
        'raw_additivity_max_abs_error':max(additivity),
        'primary_holm_family':family,
        'estimates':estimates,
        'bootstrap':{'planned':repetitions,'valid':len(draws),'rank_failures':failures,'seed':seed,
                     'paired_both_seasons_all_endpoints':True,'stratification':'original field block'},
        'source_sha256':{k:v[1] for k,v in SOURCES.items()},
        'limitations':[
            'Exploratory endpoint extension after previous results; no independent confirmation.',
            'Planned functional-group count is not continuous trait FD or phylogenetic memory.',
            'Single site/year with repeated seasons; weed means are not available per quadrat.',
            'No randomized test of ordinary vs specially careful weeding or weed competition mediation.',
            'Intervals are marginal; Holm correction applies only to four new log endpoint tests.',
            'Combined recognized living biomass is not total ecosystem biomass or annual NPP.',
            'Complete-case analysis can be affected by the excluded record; blank is not assumed zero.'],
        'versions':{'python':platform.python_version(),'numpy':np.__version__}}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir',type=Path,default=Path('data'))
    p.add_argument('--out',type=Path,default=Path('results/response_partition.json'))
    args = p.parse_args()
    records, alloc = read_sources(args.data_dir)
    panel = partition_panel(records,alloc)
    result = fit_partition(panel)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,ensure_ascii=False,allow_nan=False))

if __name__=='__main__':
    main()
