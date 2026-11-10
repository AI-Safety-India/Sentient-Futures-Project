import unittest
from analyze import summarize, sign_p, auc

class AnalysisTests(unittest.TestCase):
    def rows(self):
        rows=[]
        for cohort,n,conditions in [('fresh',8,['base','price','rating','order']),('legacy_bridge',7,['base'])]:
            for i in range(n):
                for condition in conditions:
                    for label in (0,1):
                        for position in ('pos_b','pos_a'):
                            value=label+(0 if condition=='base' else .1)
                            rows.append(dict(cohort=cohort,item_id=str(i),condition=condition,label=label,position=position,saved_e2_l26=value,content_lr_l26=value,e1_l1=value))
        return rows
    def test_primary_and_control_flags(self):
        r=summarize(self.rows())
        self.assertTrue(r['development_screen']['all_prespecified_development_flags_pass'])
        self.assertFalse(r['development_screen']['rq3_ready'])
        self.assertAlmostEqual(r['matched_control_contrasts']['pos_b|saved_e2_l26']['price']['mean_absolute_variant_shift'],.1)
    def test_secondary_never_rescues_primary(self):
        rows=self.rows()
        for r in rows:
            if r['cohort']=='fresh' and r['position']=='pos_b':r['saved_e2_l26']=-r['saved_e2_l26']
        self.assertFalse(summarize(rows)['development_screen']['primary_pair_screen_pass'])
    def test_nuisance_shift_flag(self):
        rows=self.rows()
        for r in rows:
            if r['condition']=='price':r['saved_e2_l26']+=3
        report=summarize(rows)
        self.assertTrue(report['development_screen']['control_pair_screen_pass']['price'])
        self.assertFalse(report['development_screen']['nuisance_dominance_flags']['price'])
    def test_missing_pair_rejected(self):
        rows=self.rows();rows.pop()
        with self.assertRaises(ValueError):summarize(rows)
    def test_duplicate_rejected(self):
        rows=self.rows();rows.append(rows[0])
        with self.assertRaises(ValueError):summarize(rows)
    def test_sign_and_auc(self):
        self.assertEqual(sign_p(7,1),9/256)
        self.assertEqual(auc([0,1],[0,0]),.5)

if __name__=='__main__':unittest.main()
