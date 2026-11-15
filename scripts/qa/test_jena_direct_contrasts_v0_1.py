import importlib.util
from pathlib import Path
import numpy as np
import pytest

PATH = Path(__file__).parents[1] / 'analysis' / 'validate_jena_direct_contrasts_v0_1.py'

def impl():
    assert PATH.exists(), 'direct-contrast implementation has not been created'
    spec=importlib.util.spec_from_file_location('contrast',PATH)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def test_direct_gain_algebra():
    out=impl().metrics(np.array([100.,90.,80.,79.]))
    np.testing.assert_allclose(out,[.1,.2,.21,.1,.0125])

def test_identity_contrast_is_zero():
    assert np.all(impl().metrics(np.array([10.,10.,10.,10.]))==0)

def test_invalid_baseline_rejected():
    with pytest.raises(ValueError): impl().metrics(np.array([0.,1.,2.,3.]))

def test_fit_weights_match_explicit_repeated_rows():
    m=impl();x=np.array([[1,0],[1,1],[1,2.],[1,3.]])
    y=np.array([0.,1.,4.,8.]);w=np.array([2.,0.,1.,3.]);ix=np.repeat(np.arange(4),w.astype(int))
    actual=m.predict(x,y,x,w)
    expected=x@np.linalg.lstsq(x[ix],y[ix],rcond=None)[0]
    np.testing.assert_allclose(actual,expected)

def test_block_draws_preserve_each_block_size():
    m=impl();blocks=np.array(['A','A','B','B','B']);rng=np.random.default_rng(1)
    for _ in range(20):
        w=m.draw_weights(blocks,rng)
        assert w[:2].sum()==2 and w[2:].sum()==3
        assert (w>=0).all()

def test_training_scales_not_changed_by_test_values():
    m=impl();train=np.array([[0.,10.],[2.,20.],[4.,30.]])
    test=np.array([[1e10,-1e10]])
    a,b=m.scale_train_only(train,test)
    np.testing.assert_allclose(a.mean(0),[0.,0.],atol=1e-8)
    np.testing.assert_allclose(b,(test-train.mean(0))/train.std(0))

def test_source_hash_lengths():
    for _,digest,_ in impl().SOURCES.values(): assert len(digest)==64

def test_paired_slope_equals_difference_of_separate_slopes():
    m=impl();rng=np.random.default_rng(52)
    x=np.column_stack([np.ones(30),rng.normal(size=(30,3))])
    spring=x@np.array([2.,3.,.2,-.4])+rng.normal(size=30)
    summer=x@np.array([4.,2.,.5,.8])+rng.normal(size=30)
    slope=m.paired_coefficient(x,spring,summer,2)
    expected=np.linalg.lstsq(x,summer,rcond=None)[0][2]-np.linalg.lstsq(x,spring,rcond=None)[0][2]
    assert np.isclose(slope,expected)
