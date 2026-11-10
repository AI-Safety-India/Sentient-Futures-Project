import unittest,json
import numpy as np
from project_nuisance import learn_nuisance_span,project_direction,score,summaries,CONDITIONS

class ProjectionTests(unittest.TestCase):
    def states(self):
        return {str(i):{(c,l):np.array([float(l),float(c=='price'),float(c=='rating'),float(c=='order'),float(i)]) for c in CONDITIONS for l in (0,1)} for i in range(8)}
    def test_known_nuisance_removed_and_signal_preserved(self):
        basis,_,meta=learn_nuisance_span(self.states(),list(self.states()))
        raw,unit,report=project_direction(np.array([1.,2.,3.,4.,0.]),basis)
        np.testing.assert_allclose(raw,[1.,0.,0.,0.,0.],atol=1e-12)
        self.assertEqual(meta['rank'],3);self.assertAlmostEqual(np.linalg.norm(unit),1.)
    def test_rank_deficiency_handled(self):
        states=self.states()
        for g in states.values():
            for l in (0,1):g['order',l]=g['price',l].copy()
        _,_,meta=learn_nuisance_span(states,list(states));self.assertEqual(meta['rank'],2)
    def test_heldout_item_cannot_change_fold_basis(self):
        states=self.states();items=[i for i in states if i!='0'];a=learn_nuisance_span(states,items)[0]
        states['0']['price',1]+=1e6;b=learn_nuisance_span(states,items)[0]
        np.testing.assert_array_equal(a@a.T,b@b.T)
    def test_common_offset_not_welfare_interaction(self):
        states=self.states();s=score(states,states,np.ones(5),np.zeros(5));r=summaries(s)
        self.assertEqual(r['nuisance_effects']['price']['mean_absolute_interaction'],0)
        self.assertEqual(r['nuisance_effects']['price']['mean_absolute_common_offset'],1)
        self.assertEqual(r['pair_summaries']['base']['positive_pairs'],8)
    def test_annihilated_direction_not_fabricated(self):
        basis,_,_=learn_nuisance_span(self.states(),list(self.states()))
        _,unit,_=project_direction(np.array([0.,1.,0.,0.,0.]),basis);self.assertIsNone(unit)
    def test_no_cross_fold_pooled_auc(self):
        r=summaries(score(self.states(),self.states(),np.ones(5),np.zeros(5)),False)
        self.assertIsNone(r['pair_summaries']['base']['auroc'])
    def test_missing_condition_rejected(self):
        s=self.states();del s['0']['price',0]
        with self.assertRaises(ValueError):learn_nuisance_span(s,list(s))
    def test_summary_is_serializable_and_raw_unit_signs_match(self):
        states=self.states();basis,_,_=learn_nuisance_span(states,list(states))
        raw,unit,meta=project_direction(np.array([1.,2.,3.,4.,0.]),basis)
        a=summaries(score(states,states,raw,np.zeros(5)))
        b=summaries(score(states,states,unit,np.zeros(5)))
        json.dumps(dict(raw=a,normalized=b,projection=meta))
        self.assertEqual(a['pair_summaries']['base']['positive_pairs'],b['pair_summaries']['base']['positive_pairs'])

if __name__=='__main__':unittest.main()
