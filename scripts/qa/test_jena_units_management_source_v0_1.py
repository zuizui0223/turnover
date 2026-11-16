import unittest,importlib,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
try:m=importlib.import_module('audit_jena_response_source_sensitivity_v0_1')
except ModuleNotFoundError:m=None
class ResponseSourceTests(unittest.TestCase):
 def test_missing_original_not_zero(self):
  self.assertIsNotNone(m)
  ys,keep=m.source_responses(np.array([2007,2010,2012]),np.array([2.,3.,4.]),np.array([8.,np.nan,np.nan]))
  self.assertEqual(keep.tolist(),[True,False,True])
  self.assertAlmostEqual(ys[0,1],np.log1p(8.))
  self.assertEqual(ys[1,1],4.)
 def test_future_year_source_unchanged(self):
  self.assertIsNotNone(m)
  ys,keep=m.source_responses(np.array([2011,2012]),np.array([3.,4.]),np.array([np.nan,np.nan]))
  np.testing.assert_allclose(ys[:,0],ys[:,1]);self.assertTrue(keep.all())
if __name__=='__main__':unittest.main()
