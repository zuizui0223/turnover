import copy
import numpy as np
import pytest
import response_partition as m
from weeding_sensitivity import MASS, MONTHS
WEEDS='Weeds biom dw [g/m**2]'

def fixture():
    rng=np.random.default_rng(7); records=[]; allocations=[]
    for i in range(40):
        p=f'P{i:02d}'; block=f'B{(i%4)+1}'; richness=[1,2,4,8,16][(i//4)%5]
        fg=1 if richness==1 else (1+(i//2)%min(4,richness))
        allocations.append(dict(plotcode=p, block=block, NumberSownSpecies=str(richness),NumberFunctionalGroups=str(fg)))
        for month in MONTHS:
            records.append({'Experimental plot':p,'Date/time start':month+'-20','Repl':'mean',MASS:str(float(rng.uniform(10,500))),WEEDS:str(float(rng.uniform(0,90)))})
    return records,allocations

def test_balanced_panel_and_additive_mass():
    r,a=fixture();p=m.partition_panel(r,a)
    assert len(p['plot_ids'])==40
    np.testing.assert_allclose(p['mass']['combined'],p['mass']['sown']+p['mass']['weeds'])
    assert p['X'].shape==(40,6)

def test_missing_weed_excludes_same_plot_both_dates_without_zero_imputation():
    r,a=fixture(); r[0][WEEDS]='';p=m.partition_panel(r,a)
    assert len(p['plot_ids'])==39 and 'P00' not in p['plot_ids']
    assert p['excluded'][0]['plot']=='P00'

def test_failure_sentinel_excluded_and_true_zero_kept():
    r,a=fixture();r[0][WEEDS]='-9999';r[2][WEEDS]='0'
    p=m.partition_panel(r,a)
    assert 'P00' not in p['plot_ids'] and 'P01' in p['plot_ids']
    idx=p['plot_ids'].index('P01'); assert p['mass']['weeds'][idx,0]==0

def test_negative_mass_and_duplicate_rows_rejected():
    r,a=fixture();r[0][WEEDS]='-1'
    with pytest.raises(ValueError):m.partition_panel(r,a)
    r,a=fixture();r.append(copy.deepcopy(r[0]))
    with pytest.raises(ValueError):m.partition_panel(r,a)

def test_missing_campaign_rejected():
    r,a=fixture();r.pop()
    with pytest.raises(ValueError):m.partition_panel(r,a)

def test_source_groups_are_not_merged_across_dates_or_replicates():
    r,a=fixture();other=copy.deepcopy(r[0]);other['Repl']='1';other[WEEDS]=''
    r.append(other);p=m.partition_panel(r,a)
    assert len(p['plot_ids'])==40

def test_sum_precedes_log_transform():
    r,a=fixture();r[0][MASS]='3';r[0][WEEDS]='5'
    p=m.partition_panel(r,a);names,y=m.outcome_matrix(p)
    i=names.index('log_combined_May');j=p['plot_ids'].index('P00')
    assert y[j,i]==pytest.approx(np.log1p(8))
    assert y[j,i]!=pytest.approx(np.log1p(3)+np.log1p(5))

def test_holm_adjustment_and_order():
    np.testing.assert_allclose(m.holm([.04,.01,.2,.03]),[.09,.04,.2,.09])
    np.testing.assert_allclose(m.holm([1.,0.,.5,.5]),[1.,0.,1.,1.])
    with pytest.raises(ValueError):m.holm([np.nan])

def test_additive_coefficient_identity_and_reproducible_paired_bootstrap():
    r,a=fixture();p=m.partition_panel(r,a)
    z=m.fit_partition(p,40,42);other=m.fit_partition(p,40,42)
    assert z==other
    assert z['raw_additivity_max_abs_error']<1e-9
    assert z['bootstrap']['valid']==40
    assert len(z['primary_holm_family'])==4
