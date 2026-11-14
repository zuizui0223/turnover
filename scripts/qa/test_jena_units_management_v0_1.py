import importlib,sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
try:
    m=importlib.import_module('audit_jena_units_management_v0_1')
except ModuleNotFoundError:
    m=None

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(m, 'audit module must exist before validation is usable')
    def test_zero_missing(self):
        a=m.clean_mass(pd.Series([0,2,-9999,np.nan]))
        self.assertEqual(a.iloc[0],0)
        self.assertTrue(a.iloc[2:].isna().all())
    def test_bad_negative_rejected(self):
        with self.assertRaises(ValueError):m.clean_mass(pd.Series([-2]))
    def test_duplicate_source_rejected(self):
        d=pd.DataFrame({'plot':['A','A'],'year':[2003,2003],'season':['spring']*2,'rep':[1,1],'mass':[1,1]})
        with self.assertRaises(ValueError):m.join_exact(d,d)
    def test_exact_join_uses_keys(self):
        d=pd.DataFrame({'plot':['A','B'],'year':[2003]*2,'season':['spring']*2,'rep':[1,1],'mass':[1,10]})
        r=d.iloc[::-1].copy();r['mass']=[20,2]
        q=m.join_exact(d,r)
        self.assertTrue(np.allclose(q.mass_compiled/q.mass_official,2))
    def test_unit_factor_not_fitted(self):
        r=m.unit_diagnostics(np.array([0,1,7]),np.array([0,10,70]))
        self.assertEqual(r['factors_to_multiply_compiled']['10']['n_within_tolerance'],3)
        self.assertEqual(r['factors_to_multiply_compiled']['1']['n_within_tolerance'],1)
    def test_no_random_rescaling(self):
        r=m.unit_diagnostics(np.array([1,2,3]),np.array([7,14,21]))
        self.assertFalse(any(x['n_within_tolerance']==3 for x in r['factors_to_multiply_compiled'].values()))
    def test_ordinary_excludes_fourth(self):
        d=pd.DataFrame({'plot':['A']*4,'season':['spring']*4,'rep':[1,2,3,4],'mass':[1.,2.,3.,10.]})
        q=m.sample_summaries(d)
        self.assertEqual(q.loc[('A','spring'),'ordinary_1to3'],2)
        self.assertEqual(q.loc[('A','spring'),'all_1to4'],4)
        self.assertEqual(q.loc[('A','spring'),'special_4'],10)
    def test_missing_subsample_not_zero(self):
        d=pd.DataFrame({'plot':['A']*3,'season':['spring']*3,'rep':[1,2,4],'mass':[1.,2.,10.]})
        with self.assertRaises(ValueError):m.sample_summaries(d)
    def test_paired_difference_algebra(self):
        rng=np.random.default_rng(27);x=np.column_stack([np.ones(25),rng.normal(size=(25,3))]);a=rng.normal(size=25);b=rng.normal(size=25)
        q=m.fit_response(x,b-a,2)
        expected=(np.linalg.lstsq(x,b,rcond=None)[0]-np.linalg.lstsq(x,a,rcond=None)[0])[2]
        self.assertAlmostEqual(q['beta'],expected,12)
    def test_parser_retains_units_and_sentinel(self):
        raw=('/* metadata */\nExperimental plot\tDate/time start\tRepl\tSown plant biom dw [g/m**2]\nA\t2003-05-24\t1\t0\nA\t2003-08-24\t1\t-9999\n').encode()
        d,meta=m.parse_official(raw,2003)
        self.assertEqual(d.season.tolist(),['spring','summer'])
        self.assertEqual(d.mass.iloc[0],0)
        self.assertTrue(pd.isna(d.mass.iloc[1]))
        self.assertEqual(meta['unit'],'g/m2')

if __name__=='__main__':unittest.main()
