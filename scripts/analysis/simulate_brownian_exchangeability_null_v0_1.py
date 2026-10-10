#!/usr/bin/env python3
"""Known-truth Brownian counterexample to interpreting rho rank reversals as evolutionary rewiring.

All traits in all families share a single Brownian evolutionary-rate parameter.
Families differ only in phylogenetic geometry and stochastic realized trajectories.
The resulting rho, K, and crossed components are descriptive counterexamples, not
a calibrated null for the observed BIEN or AusTraits family trees.

K follows the method='K', test=FALSE formula in phytools::phylosig.
"""
from __future__ import annotations
import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.stats import rankdata, spearmanr


def tree_covariance(n: int, rng: np.random.Generator, mode: str):
    """Construct an ultrametric binary coalescent tree and its Brownian tip covariance."""
    age = np.zeros((n, n), dtype=float)
    parts = [np.array([i], dtype=int) for i in range(n)]
    t = 0.0
    while len(parts) > 1:
        k = len(parts)
        t += rng.exponential(2.0 / (k * (k - 1)))
        a, b = rng.choice(k, size=2, replace=False)
        left, right = parts[a], parts[b]
        age[np.ix_(left, right)] = t
        age[np.ix_(right, left)] = t
        parts = [part for idx, part in enumerate(parts) if idx not in (a, b)]
        parts.append(np.r_[left, right])
    age /= t
    if mode == "deep":
        age **= 1.5
    elif mode == "starish":
        age = 1 - (1 - age) ** 1.5
        np.fill_diagonal(age, 0.0)
    elif mode != "standard":
        raise ValueError(mode)
    # Ensure short positive terminal edges for numerical stability of C^-1.
    mask = (age > 0) & (age < 1)
    age[mask] = np.maximum(.015, age[mask])
    covariance = 1.0 - age
    np.fill_diagonal(covariance, 1.0)
    return covariance, 2.0 * age


def phylogenetic_k(x, inv_c, norm):
    one = np.ones(len(x))
    gls_mean = (one @ inv_c @ x) / (one @ inv_c @ one)
    residual = x - gls_mean
    return float((residual @ residual) / (residual @ inv_c @ residual) / norm)


def crossed_moments(v):
    """Balanced two-way random-effects method of moments (NOT REML)."""
    f, t = v.shape
    grand = v.mean()
    fem = v.mean(axis=1, keepdims=True)
    tem = v.mean(axis=0, keepdims=True)
    error = v - fem - tem + grand
    ms_e = (error**2).sum() / ((f - 1) * (t - 1))
    ms_f = t * ((fem - grand)**2).sum() / (f - 1)
    ms_t = f * ((tem - grand)**2).sum() / (t - 1)
    vf = max(0., (ms_f - ms_e) / t)
    vt = max(0., (ms_t - ms_e) / f)
    ve = ms_e
    return {"L":float(vf/(vf+ve)), "A":float(vt/(vt+ve)),
            "var_family":float(vf), "var_trait":float(vt), "var_system":float(ve)}


def reversal(v):
    f, t = v.shape
    contrasts = []
    for i, j in combinations(range(t), 2):
        d = v[:, i] - v[:, j]
        pos = int(np.count_nonzero(d > 0))
        neg = int(np.count_nonzero(d < 0))
        n = pos + neg
        contrasts.append((pos*neg, n*(n-1)/2))
    return float(sum(z[0] for z in contrasts) / sum(z[1] for z in contrasts))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--families', type=int, default=24)
    p.add_argument('--traits', type=int, default=8)
    p.add_argument('--replicates', type=int, default=128)
    p.add_argument('--seed', type=int, default=20261008)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    rng = np.random.default_rng(a.seed)
    fam = []
    for f in range(a.families):
        n = [24, 30, 36, 44, 56, 72][f % 6]
        mode = ['deep', 'standard', 'starish'][f % 3]
        c, d = tree_covariance(n, rng, mode)
        chol = np.linalg.cholesky(c)
        inv = cho_solve(cho_factor(c, lower=True, check_finite=False),
                        np.eye(n), check_finite=False)
        norm = (np.trace(c)-n/(np.ones(n) @ inv @ np.ones(n))) / (n-1)
        tri = np.triu_indices(n, 1)
        rd = rankdata(d[tri], method='average')
        rd -= rd.mean()
        rd /= np.linalg.norm(rd)
        fam.append({'n':n, 'mode':mode, 'chol':chol, 'inv':inv, 'norm':norm,
                    'tri':tri, 'rank_dist':rd})

    records = []
    for rep in range(a.replicates):
        rs = np.zeros((a.families, a.traits))
        ks = np.zeros_like(rs)
        for f, z in enumerate(fam):
            n = z['n']
            x = z['chol'] @ rng.standard_normal((n, a.traits))
            for t in range(a.traits):
                state = x[:, t]
                deltas = np.abs(state[z['tri'][0]]-state[z['tri'][1]])
                ranks = rankdata(deltas, method='average')
                ranks -= ranks.mean()
                nr = np.linalg.norm(ranks)
                rs[f, t] = (z['rank_dist'] @ ranks)/nr if nr else 0
                ks[f, t] = phylogenetic_k(state, z['inv'], z['norm'])
        rm = crossed_moments(rs)
        km = crossed_moments(np.log(ks))
        row = {'replicate':rep, 'rho_reversal':reversal(rs),
               'K_reversal':reversal(ks),
               'rho_L':rm['L'], 'rho_A':rm['A'],
               'logK_L':km['L'], 'logK_A':km['A'],
               'mean_rho':float(rs.mean()), 'mean_K':float(ks.mean()),
               'cross_metric_spearman':float(spearmanr(rs.ravel(), ks.ravel()).statistic)}
        for mode in ['deep', 'standard', 'starish']:
            mask = np.array([z['mode']==mode for z in fam])
            row[f'mean_rho_{mode}'] = float(rs[mask].mean())
            row[f'mean_K_{mode}'] = float(ks[mask].mean())
        records.append(row)
    keys = records[0].keys()
    summary = {key:{'mean':float(np.mean([r[key] for r in records])),
                    'q025':float(np.quantile([r[key] for r in records], .025)),
                    'q975':float(np.quantile([r[key] for r in records], .975))}
               for key in keys if key!='replicate'}
    y = fam[0]['chol'] @ rng.standard_normal(fam[0]['n'])
    indices = fam[0]['tri']
    def rho_state(x):
        v = rankdata(np.abs(x[indices[0]]-x[indices[1]]))
        v -= v.mean()
        return float((fam[0]['rank_dist'] @ v)/np.linalg.norm(v))
    scale_test = {'rho_original':rho_state(y), 'rho_scaled_x10':rho_state(10*y),
                  'K_original':phylogenetic_k(y, fam[0]['inv'], fam[0]['norm']),
                  'K_scaled_x10':phylogenetic_k(10*y, fam[0]['inv'], fam[0]['norm'])}
    assert abs(scale_test['rho_original']-scale_test['rho_scaled_x10'])<1e-12
    assert abs(scale_test['K_original']-scale_test['K_scaled_x10'])<1e-8
    result = {'version':'v0.1','status':'BROWNIAN_IDENTICAL_PROCESS_NULL_ESTIMATED',
              'simulation':{'families':a.families, 'traits':a.traits,
                            'replicates':a.replicates, 'seed':a.seed,
                            'branch_geometry_modes':['deep','standard','starish'],
                            'species_sizes':[24,30,36,44,56,72],
                            'same_evolutionary_rate_for_every_trait_and_family':True,
                            'species_states_from_phylogenetic_brownian_mvn':True},
              'summary':summary, 'scale_invariance':scale_test,
              'theoretical_exchangeable_pair_reversal':.5,
              'hard_nonclaims':[
                  'Synthetic family trees are not observed BIEN or AusTraits trees; NOT an empirical-null p-value.',
                  'High reversal under equal-rate Brownian motion does not imply adaptive trait allocation rewiring.',
                  'Under exchangeable within-family trait processes, pair-order signs are symmetric, so two independent families disagree with probability 1/2.',
                  'The empirical L/A null must condition on observed trees, trait missingness and cross-system covariance.']}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],
                      'summary':{k:summary[k] for k in ['rho_reversal','K_reversal','rho_L','rho_A','logK_L','logK_A','mean_rho_deep','mean_rho_starish','mean_K_deep','mean_K_starish']}},
                     indent=2))
if __name__=='__main__':
    main()
