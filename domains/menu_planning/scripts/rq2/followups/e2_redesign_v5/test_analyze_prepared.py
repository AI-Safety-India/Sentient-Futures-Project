import unittest
from pathlib import Path
import numpy as np
from analyze_prepared import analyze,summarize,sign_flip_diagnostic,ValidationBlocked,PROBES
from fit_direction import fit_direction

class AnalysisTests(unittest.TestCase):
    def rows(self):
        return [dict(item_id=f'i{i}',label=l,condition=c,position=p,**{k:float(l) for k in PROBES}) for i in range(8) for l in (0,1) for c in ('base','price','rating','order') for p in ('pos_b','pos_a')]
    def test_missing_run_fails_without_output(self):
        d=Path(__file__).resolve().parent/'_nonexistent_v5_run_for_test'
        self.assertFalse(d.exists())
        with self.assertRaises(ValidationBlocked):analyze(d,d,d/'none.npz')
        self.assertFalse((d/'candidate_v5_direction.npz').exists())
    def test_perfect_matched_pairs(self):
        r=summarize(self.rows());self.assertTrue(r['development_flags']['primary_at_least_7_of_8'])
        self.assertEqual(r['matched_controls']['pos_b|candidate_v5_l26']['price']['mean_absolute_variant_shift'],0)
    def test_missing_and_duplicate_rows_rejected(self):
        for rows in [self.rows()[:-1],self.rows()+[self.rows()[0]]]:
            with self.assertRaises(ValidationBlocked):summarize(rows)
    def test_order_cannot_rescue_primary(self):
        rows=self.rows()
        for r in rows:
            if r['condition']=='base' and r['position']=='pos_b':r['candidate_v5_l26']=-r['candidate_v5_l26']
        out=summarize(rows)['development_flags'];self.assertFalse(out['primary_at_least_7_of_8']);self.assertTrue(out['control_at_least_7_of_8']['order'])
    def test_null_is_diagnostic_only(self):
        states={(str(i),g,o,l):np.array([float(l*(2 if g=='welfare' else 0)),float(i)]) for i in range(6) for g in ('welfare','commercial') for o in ('target_first','target_last') for l in (0,1)}
        direction,center,_=fit_direction(states);before=direction.copy()
        out=sign_flip_diagnostic(states,np.tile([1.,0.],(8,1)),direction)
        self.assertEqual(out['label_flip_patterns'],64);self.assertFalse(out['selection_performed'])
        np.testing.assert_array_equal(direction,before)
        self.assertEqual(out['defined_patterns']+out['undefined_patterns'],64)
    def test_predeclared_exclusion_never_changes_primary(self):
        rows=self.rows()
        for r in rows:
            if r['item_id']=='i7':r['item_id']='fresh_v4_07'
        out=summarize(rows)
        self.assertEqual(out['pair_summaries']['pos_b|base|candidate_v5_l26']['items'],8)
        self.assertEqual(out['predeclared_novelty_sensitivity']['summaries']['pos_b|base|candidate_v5_l26']['items'],7)

if __name__=='__main__':unittest.main()
