import copy
import numpy as np
import pytest
import statsmodels.api as sm
from weeding_sensitivity import numeric_mass, prepare_panel, hc3_fit, paired_indices

COL = 'Sown plant biom dw [g/m**2]'

def fixture():
    records, allocations = [], []
    for i in range(32):
        b = i // 8
        richness = 2 ** ((i + b) % 5)
        fg = 1 + ((i // 2 + b) % min(richness, 4))
        plot = f'B{b+1}A{i%8+1:02}'
        allocations.append(dict(plotcode=plot, block=f'B{b+1}',
            NumberSownSpecies=str(richness), NumberFunctionalGroups=str(fg)))
        for month in ('05', '08'):
            y = 4 + .15*np.log2(richness) + .12*fg + .03*b + .08*np.sin(i)
            if month == '08': y += .25 - .05*fg
            ordinary = np.expm1(y)
            careful = np.expm1(y + .25 + .03*fg)
            vals = [ordinary*.8, ordinary, ordinary*1.2, careful]
            for rep, val in list(zip(('1','2','3','4'), vals)) + [('mean', np.mean(vals))]:
                records.append({'Experimental plot':plot, 'Date/time start':f'2003-{month}-27',
                                'Repl':rep, COL:str(val)})
    return records, allocations

def test_missing_and_invalid_are_not_zero():
    assert numeric_mass('0') == 0
    assert numeric_mass('2.5') == 2.5
    for v in ('', None, '-9999', 'NaN', 'inf', '-0.1', 'not-a-number'):
        with pytest.raises(ValueError): numeric_mass(v)

def test_ordinary_mean_before_log_and_independent_plot_count():
    r, m = fixture(); p = prepare_panel(r, m)
    assert p['X'].shape == (32, 6)
    assert len(p['plot_ids']) == len(set(p['plot_ids'])) == 32
    direct = [float(x[COL]) for x in r if x['Experimental plot']==p['plot_ids'][0]
              and x['Date/time start'].startswith('2003-05') and x['Repl'] in ('1','2','3')]
    assert p['biomass']['ordinary'][0,0] == pytest.approx(np.mean(direct))
    assert np.log1p(np.mean(direct)) != pytest.approx(np.log1p(direct).mean())
    assert p['biomass']['official'].shape == (32, 2)

def test_duplicate_record_is_rejected():
    r, m = fixture(); r.append(copy.deepcopy(r[0]))
    with pytest.raises(ValueError, match='duplicate'): prepare_panel(r,m)

def test_missing_quadrat_is_rejected_not_reweighted():
    r,m=fixture(); r.pop(0)
    with pytest.raises(ValueError, match='replicate'): prepare_panel(r,m)

def test_wrong_plot_count_is_rejected():
    r,m=fixture()
    with pytest.raises(ValueError, match='plot count'): prepare_panel(r,m,expected_plots=82)

def test_official_mean_discrepancy_is_not_ignored():
    r,m=fixture(); next(x for x in r if x['Repl']=='mean')[COL]='0'
    with pytest.raises(ValueError, match='official mean'): prepare_panel(r,m)

def test_hc3_matches_independent_statsmodels():
    r,m=fixture(); p=prepare_panel(r,m); x=p['X'];y=np.log1p(p['biomass']['ordinary'][:,0])
    got=hc3_fit(x,y); ref=sm.OLS(y,x).fit(cov_type='HC3')
    np.testing.assert_allclose(got['beta'],ref.params,atol=1e-10)
    np.testing.assert_allclose(got['se'],ref.bse,atol=1e-10)
    np.testing.assert_allclose(got['ci95'],ref.conf_int(),atol=1e-10)
    np.testing.assert_allclose(got['p'],ref.pvalues,atol=1e-10)

def test_direct_contrast_matches_difference_of_coefficients():
    r,m=fixture();p=prepare_panel(r,m);x=p['X']
    a=np.log1p(p['biomass']['careful'][:,0]);b=np.log1p(p['biomass']['ordinary'][:,0])
    direct=hc3_fit(x,a-b)['beta']
    np.testing.assert_allclose(direct,hc3_fit(x,a)['beta']-hc3_fit(x,b)['beta'],atol=1e-10)
    assert direct[2] == pytest.approx(.03)

def test_stratified_indices_preserve_block_sizes_and_pairs():
    r,m=fixture();p=prepare_panel(r,m);rng=np.random.default_rng(20261117)
    idx=paired_indices(p['blocks'],rng)
    assert len(idx)==32
    for b in set(p['blocks']):
        assert sum(p['blocks'][i]==b for i in idx)==p['blocks'].count(b)
    panel=p['biomass']['ordinary'][idx]
    assert panel.shape==(32,2)
    np.testing.assert_array_equal(panel[:,1],p['biomass']['ordinary'][idx,1])

def test_rank_deficiency_is_rejected():
    with pytest.raises(ValueError, match='rank'):
        hc3_fit(np.ones((20,3)),np.arange(20,dtype=float))

def test_full_synthetic_contrasts_keep_paired_identities():
    from weeding_sensitivity import analyse
    r,m=fixture();panel=prepare_panel(r,m)
    out=analyse(panel,repetitions=120,require_original_replay=False)
    assert out['original_official_mean_coefficients_reproduced'] is False
    assert out['bootstrap']['valid']==120
    assert out['estimates']['May_careful_minus_ordinary']['FG_beta']==pytest.approx(.03)
    assert out['estimates']['August_careful_minus_ordinary']['FG_beta']==pytest.approx(.03)
    assert out['estimates']['ordinary_August_minus_May']['FG_beta']==pytest.approx(-.05)

def test_source_identity_rejects_wrong_bytes(tmp_path):
    from weeding_sensitivity import read_sources
    (tmp_path/'biomass2003.tab').write_text('not original source')
    with pytest.raises(ValueError,match='SHA256'): read_sources(tmp_path)

def test_missing_raw_input_cannot_create_empirical_result(tmp_path):
    import subprocess,sys
    from pathlib import Path
    out=tmp_path/'result.json'
    code=Path(__file__).resolve().parents[1]/'weeding_sensitivity.py'
    p=subprocess.run([sys.executable,str(code),'--data-dir',str(tmp_path),'--out',str(out)],
                     capture_output=True,text=True)
    assert p.returncode != 0
    assert not out.exists()
    assert 'missing original source' in p.stderr
