import unittest,copy
from pathlib import Path
import numpy as np
from analyze_factual import fit_direction,summarize,PROBES,ValidationBlocked,verify_instruction_pair,analyze,read

class FactualAnalysisTests(unittest.TestCase):
    def states(self):
        return {(str(i),g,o,l):np.array([float(l*(2 if g=='welfare' else 0)),10.*l,float(g=='welfare'),float(o=='target_last')]) for i in range(6) for g in ('welfare','facts') for o in ('target_first','target_last') for l in (0,1)}
    def rows(self):
        return [dict(item_id=f'i{i}',label=l,condition=c,position=p,**{k:float(l) for k in PROBES}) for i in range(8) for l in (0,1) for c in ('base','price','rating','order') for p in ('pos_b','pos_a')]
    def test_interaction_removes_additive_content_and_goal(self):
        w,c,r=fit_direction(self.states());np.testing.assert_array_equal(w,[1.,0.,0.,0.]);self.assertEqual(r['development_states_used'],0)
    def test_missing_factor_and_zero_interaction_stop(self):
        d=self.states();d.pop(next(iter(d)))
        with self.assertRaises(ValueError):fit_direction(d)
        with self.assertRaises(ValueError):fit_direction({k:np.zeros(4) for k in self.states()})
    def test_primary_failure_not_rescued_by_order_or_old_probe(self):
        rows=self.rows()
        for r in rows:
            if r['condition']=='base' and r['position']=='pos_b':r['candidate_v6_l26']=-r['candidate_v6_l26']
        a=summarize(rows);self.assertFalse(a['development_flags']['primary_at_least_7_of_8']);self.assertTrue(a['development_flags']['control_at_least_7_of_8']['order'])
    def test_common_offsets_distinguished_from_pair_changes(self):
        rows=self.rows()
        for r in rows:
            if r['condition']=='price':r['candidate_v6_l26']+=10
        c=summarize(rows)['matched_controls']['pos_b|candidate_v6_l26']['price']
        self.assertEqual(c['mean_absolute_common_offset'],10);self.assertEqual(c['mean_absolute_interaction'],0);self.assertEqual(c['pair_sign_changes'],0)
    def test_duplicate_and_missing_rows_stop(self):
        for rows in [self.rows()[:-1],self.rows()+[self.rows()[0]]]:
            with self.assertRaises(ValidationBlocked):summarize(rows)
    def test_unexecuted_run_rejected(self):
        root=Path(__file__).resolve().parent/'_nonexistent_v6'
        with self.assertRaises(ValidationBlocked):analyze(root,root,root,root/'none.npz')
    def test_actual_pairs_and_modified_tool_content(self):
        root=Path(__file__).resolve().parents[2]/'Sentient-Futures-Project-git/results/rq2'
        jobs=read(root/'e2_factual_v6/jobs.json');old={j['job_id']:j for j in read(root/'e2_redesign_v5/jobs.json')}
        for j in jobs:verify_instruction_pair(j,old[j['source_v5_job_id']])
        j=copy.deepcopy(jobs[0]);j['request']['messages'][-1]['content']+=' extra'
        with self.assertRaises(ValidationBlocked):verify_instruction_pair(j,old[j['source_v5_job_id']])

if __name__=='__main__':unittest.main()
