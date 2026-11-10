"""Regression checks for the analysis bugs repaired after the RQ2 audit."""
import unittest
import numpy as np
from repair_analysis import auc_summary, first_reads

class AnalysisTests(unittest.TestCase):
    def test_tied_auc_matches_direct_pairs(self):
        rows = [dict(scenario_id=s,option_label=label,score=value) for s,label,value in [('a','harmful',1),('a','safe',1),('b','harmful',3),('b','safe',2),('c','safe',0)]]
        positive = np.array([1,3]); negative = np.array([1,2,0])
        expected = np.mean((positive[:,None]>negative)+.5*(positive[:,None]==negative))
        self.assertAlmostEqual(auc_summary(rows,'score',200)['auroc'], expected)

    def test_one_class_is_explicitly_undefined(self):
        self.assertIsNone(auc_summary([dict(scenario_id='a',option_label='safe',score=1)],'score')['auroc'])

    def test_first_read_uses_token_order_and_preserves_other_runs(self):
        rows = [dict(run_id=run,option_id='x',tok_idx=token,sub_idx=i) for i,(run,token) in enumerate([('a',20),('b',8),('a',10)])]
        result = first_reads(rows)
        self.assertEqual({r['run_id']:r['tok_idx'] for r in result},{'a':10,'b':8})

if __name__=='__main__':
    unittest.main()
