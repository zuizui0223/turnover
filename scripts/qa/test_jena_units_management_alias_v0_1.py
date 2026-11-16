import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
import audit_jena_units_management_v0_1 as m
class SourceAliasRegression(unittest.TestCase):
 def test_global_plotcode_does_not_collide_with_local_plot(self):
  raw=pd.DataFrame({'plotcode':['B1A01'],'plot':['A01'],'year':[2003],'month':['May'],'subsample':[1],'target.biomass':[2.]})
  canonical=pd.DataFrame({'plot':['B1A01'],'year':[2003],'season':['spring'],'rep':['1'],'mass':[2.]})
  info=pd.DataFrame(index=['B1A01'])
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'biomass2003.tab').write_bytes(b'fixture')
   with patch.object(m,'csv_zip',return_value=raw),patch.object(m,'parse_official',return_value=(canonical,{'year':2003})),patch.object(m,'ANNUAL',{2003:846317}):
    reports,_=m.annual_reconcile(root,info)
  self.assertEqual(reports[0]['n_exact_key_pairs'],1)
  self.assertEqual(reports[0]['comparison']['factors_to_multiply_compiled']['1']['n_within_tolerance'],1)
if __name__=='__main__':unittest.main()
