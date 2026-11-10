import unittest
import numpy as np
from fit_direction import fit_direction,score_pairs,GOALS,ORDERS

class FitTests(unittest.TestCase):
    def fixture(self):
        return {(str(i),g,o,l):np.array([float(l*(g=='welfare')),10.*l,100.*(g=='welfare'),float(o=='target_last')]) for i in range(6) for g in GOALS for o in ORDERS for l in (0,1)}
    def test_common_content_goal_order_effects_cancel(self):
        w,_,r=fit_direction(self.fixture());np.testing.assert_array_equal(w,[1.,0.,0.,0.]);self.assertEqual(r['development_states_used'],0)
    def test_factor_order_does_not_change_fit(self):
        d=self.fixture();a=fit_direction(d)[0];b=fit_direction(dict(reversed(list(d.items()))))[0];np.testing.assert_array_equal(a,b)
    def test_no_posthoc_sign_flip_on_bad_transfer(self):
        w,c,_=fit_direction(self.fixture());original=w.copy()
        result=score_pairs(w,c,{'unseen':{0:np.zeros(4),1:np.array([-1.,0.,0.,0.])}})
        self.assertLess(result['unseen']['higher_minus_lower'],0);np.testing.assert_array_equal(w,original)
    def test_zero_interaction_stops(self):
        d={k:np.zeros(4) for k in self.fixture()}
        with self.assertRaises(ValueError):fit_direction(d)
    def test_missing_or_neutral_training_factors_stop(self):
        d=self.fixture();d.pop(next(iter(d)))
        with self.assertRaises(ValueError):fit_direction(d)
        d=self.fixture();d['new','neutral','target_first',0]=np.zeros(4)
        with self.assertRaises(ValueError):fit_direction(d)

if __name__=='__main__':unittest.main()
