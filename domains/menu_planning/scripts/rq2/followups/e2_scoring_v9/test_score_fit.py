import unittest
from itertools import product
import numpy as np
import score_fit as s


def fixture(items=6):
    records=[]
    for item,goal,order,price,service,label in product(range(items),s.GOALS,s.ORDERS,s.PRICES,s.SERVICES,s.LABELS):
        vector=np.array([label*(2 if goal=='welfare' else .4),
                         label*(.5 if goal=='welfare' else .2)+2*(price=='double'),
                         3*(order=='target_last')+.2*label,
                         2*(service=='negative'),item*.03,(goal=='welfare')*.5],dtype=float)
        records.append(((str(item),goal,order,price,service,label),vector))
    return records


class ScoringTests(unittest.TestCase):
    def test_full_design_counts(self):
        _,_,d,n=s.matrices(fixture(),6)
        self.assertEqual(d.shape,(48,6))
        self.assertEqual({k:len(v) for k,v in n.items()},{'price':96,'order':96,'service':96})

    def test_primal_solution_matches_dual(self):
        records=fixture()
        direction,_,raw,_=s.fit(records)
        _,_,target,nuisance=s.matrices(records)
        scale2=np.mean(np.sum(target**2,axis=1))
        covariance=target.T@target/len(target)
        for values in nuisance.values():covariance+=values.T@values/(3*len(values))
        reference=np.linalg.solve(covariance+.01*scale2*np.eye(6),target.mean(0))
        np.testing.assert_allclose(raw,reference,rtol=1e-11,atol=1e-12)
        np.testing.assert_allclose(direction,reference/np.linalg.norm(reference),atol=1e-11)

    def test_penalty_reduces_known_price_component(self):
        records=fixture()
        fitted,_,_,_=s.fit(records)
        baseline,_=s.mean_baseline(records)
        self.assertLess(abs(fitted[1]),abs(baseline[1]))
        self.assertGreater(fitted[0],0)

    def test_scale_and_rotation_equivariance(self):
        records=fixture()
        direction,_,raw,_=s.fit(records)
        scaled,_,scaled_raw,_=s.fit([(k,7*v) for k,v in records])
        np.testing.assert_allclose(scaled,direction,atol=1e-11)
        np.testing.assert_allclose(scaled_raw,raw/7,atol=1e-11)
        q,_=np.linalg.qr(np.random.default_rng(41).normal(size=(6,6)))
        rotated,_,_,_=s.fit([(k,q@v) for k,v in records])
        np.testing.assert_allclose(rotated,q@direction,atol=1e-11)

    def test_duplicate_incomplete_and_nonfinite_rejected(self):
        records=fixture()
        for bad in [records+[records[0]],records[:-1],[(records[0][0],np.full(6,np.nan))]+records[1:]]:
            with self.assertRaises(ValueError):s.fit(bad)

    def test_held_out_item_never_enters_fit(self):
        records=fixture()
        train,test=s.item_split(records,'2')
        self.assertEqual((len(train),len(test)),(160,32))
        self.assertNotIn('2',{k[0] for k,_ in train})
        changed=[(k,v+1000 if k[0]=='2' else v) for k,v in records]
        changed_train,_=s.item_split(changed,'2')
        np.testing.assert_array_equal(s.fit(train)[0],s.fit(changed_train)[0])

    def test_row_order_invariance(self):
        records=fixture()
        np.testing.assert_allclose(s.fit(records)[0],s.fit(records[::-1])[0],atol=1e-12)

    def test_zero_interaction_rejected(self):
        with self.assertRaisesRegex(ValueError,'interaction energy'):
            s.fit([(k,np.zeros(6)) for k,v in fixture()])


if __name__=='__main__':unittest.main()
