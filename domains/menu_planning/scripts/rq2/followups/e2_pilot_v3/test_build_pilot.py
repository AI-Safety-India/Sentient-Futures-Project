import copy,unittest
from build_pilot import build_jobs,validate_jobs


class PilotBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.jobs,cls.pairs,cls.checks=build_jobs()

    def test_core_structure_and_no_fake_backend_pass(self):
        self.assertEqual(len(self.jobs),42)
        self.assertTrue(all(j['input_check']['token_ids_match'] is None for j in self.jobs))
        self.assertTrue(all(j['whole_option_binary_label'] is None for j in self.jobs))
        for j in self.jobs:
            if j['condition'] in ('welfare','value'):
                self.assertTrue(j['request']['messages'][-1]['content'].endswith('Answer yes, no, or uncertain.'))

    def test_added_condition_cue_fails_pair_check(self):
        jobs=copy.deepcopy(self.jobs);jobs[0]['prompt_text']+=' condition-specific cue'
        with self.assertRaises(AssertionError):validate_jobs(jobs)

    def test_changed_prefix_ids_fail_causal_prefix_check(self):
        jobs=copy.deepcopy(self.jobs);jobs[1]['input_ids'][0]+=1
        with self.assertRaises(AssertionError):validate_jobs(jobs)

    def test_original_scope_and_only_common_tags(self):
        for j in self.jobs:
            self.assertIn('search_options',j['prompt_text'])
            self.assertIn('get_option_details',j['prompt_text'])
            self.assertIn('OrderHub Fulfilment Agent',j['prompt_text'])
            self.assertFalse(j['approved_for_execution'])
            self.assertFalse(j['generation'])


if __name__=='__main__':unittest.main()
