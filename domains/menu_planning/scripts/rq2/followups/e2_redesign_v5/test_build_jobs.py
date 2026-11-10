import copy,unittest
import build_jobs as b

class PreparedJobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs=b.read(b.OUT/'jobs.json')
        payload=b.read(b.CODE/'candidate_pairs.json')
        cls.pairs=payload['pairs'] if isinstance(payload,dict) else payload

    def test_frozen_preparation_has_expected_counts(self):
        result=b.validate(self.jobs,self.pairs)
        self.assertEqual(result['new_training_forwards_required'],48)
        self.assertEqual(result['existing_development_jobs_reused'],64)
        self.assertEqual(result['independent_fresh_holdout_items'],0)

    def test_post_tool_instruction_is_rejected(self):
        jobs=copy.deepcopy(self.jobs)
        jobs[0]['request']['messages'].append({'role':'user','content':b.INSTRUCTIONS['welfare']})
        with self.assertRaises(AssertionError):b.validate(jobs,self.pairs)

    def test_complete_label_reversal_is_rejected(self):
        jobs=copy.deepcopy(self.jobs)
        for j in jobs:
            if j['split']=='train':j['label']=1-j['label']
        with self.assertRaises(AssertionError):b.validate(jobs,self.pairs)

    def test_missing_order_cell_is_rejected(self):
        jobs=copy.deepcopy(self.jobs)
        jobs[0]['detail_order']='target_last'
        with self.assertRaises(AssertionError):b.validate(jobs,self.pairs)

    def test_reuse_input_change_is_rejected(self):
        jobs=copy.deepcopy(self.jobs)
        next(j for j in jobs if j['split']=='development')['input_ids'][0]+=1
        with self.assertRaises(AssertionError):b.validate(jobs,self.pairs)

    def test_training_development_item_overlap_is_rejected(self):
        pairs=copy.deepcopy(self.pairs)
        first=next(p['item_id'] for p in pairs if p['split']=='train')
        next(p for p in pairs if p['split']=='development')['item_id']=first
        with self.assertRaises(AssertionError):b.validate(self.jobs,pairs)

if __name__=='__main__':unittest.main()
