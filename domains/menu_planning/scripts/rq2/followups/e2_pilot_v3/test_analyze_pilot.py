import copy
import unittest

import numpy as np

from analyze_pilot import exact_auc,loo_e2_interactions


class PilotAnalysisTests(unittest.TestCase):
    def fixture(self):
        data={}
        for i in range(7):
            g={}
            for label in (0,1):
                g[(label,'welfare')]=np.array([float(label*2),float(i)])
                g[(label,'value')]=np.array([0.,float(i)])
                g[(label,'silent')]=np.array([float(label),float(i)])
            data[str(i)]=g
        return data

    def test_loo_direction_uses_training_question_states_only(self):
        data=self.fixture();before=loo_e2_interactions(data)
        data['0'][(1,'welfare')]=np.array([-1000.,2000.])
        data['0'][(0,'value')]=np.array([3000.,-4000.])
        data['1'][(1,'silent')]=np.array([-999.,99.])
        after=loo_e2_interactions(data)
        # Held-out questioned states and training silent states cannot change fold 0.
        np.testing.assert_array_equal(before['folds'][0]['direction'],after['folds'][0]['direction'])
        self.assertEqual(before['folds'][0]['silent_pair_shift'],after['folds'][0]['silent_pair_shift'])

    def test_negative_transfer_does_not_flip_sign(self):
        data=self.fixture()
        for g in data.values():g[(1,'silent')]=np.array([-1.,0.])
        out=loo_e2_interactions(data)
        self.assertEqual(out['positive_pairs'],0)
        self.assertTrue(all(r['silent_pair_shift']<0 for r in out['folds']))

    def test_zero_direction_unresolved(self):
        data=self.fixture()
        for g in data.values():g[(1,'welfare')]=g[(0,'welfare')].copy()
        out=loo_e2_interactions(data)
        self.assertEqual(out['undefined_folds'],7)
        self.assertIsNone(out['pooled_auroc'])

    def test_missing_condition_rejected(self):
        data=self.fixture();del data['2'][(0,'value')]
        with self.assertRaises(ValueError):loo_e2_interactions(data)

    def test_auc_ties(self):
        self.assertEqual(exact_auc([1,0],[1.,1.]),.5)


if __name__=='__main__':unittest.main()
