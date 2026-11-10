"""Regression checks for the prospective factorial input contract, no inference."""
import copy
import unittest
from build_jobs_v8 import HERE, PAIRS, RESULTS, read, validate, canonical


class InputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = read(HERE / 'training_jobs_draft.json')
        cls.pairs = read(PAIRS)

    def test_complete_factorial_and_old_reuse_exclusion(self):
        report = validate(self.jobs, self.pairs)
        self.assertEqual(report['new_forwards_required'], 192)
        self.assertEqual(report['old_exact_prefix_matches'], 0)
        self.assertEqual(report['admin_style_item_counts'], {'billing_pdf_searchability': 3, 'receipt_page_sequence': 3})

    def test_missing_cell_rejected(self):
        with self.assertRaises(ValueError):
            validate(self.jobs[:-1], self.pairs)

    def test_duplicate_factor_cell_rejected(self):
        jobs = copy.deepcopy(self.jobs)
        jobs[1] = copy.deepcopy(jobs[0])
        with self.assertRaises(ValueError):
            validate(jobs, self.pairs)

    def test_old_no_note_prefix_cannot_be_counted_as_new(self):
        jobs = copy.deepcopy(self.jobs)
        old = read(RESULTS / 'e2_factual_v6/jobs.json')[0]
        jobs[0]['primary_prefix_sha256'] = canonical(old['input_ids'])
        with self.assertRaises(ValueError):
            validate(jobs, self.pairs)

    def test_post_tool_nudge_rejected(self):
        jobs = copy.deepcopy(self.jobs)
        jobs[0]['request']['messages'].append({'role': 'user', 'content': 'Please continue.'})
        with self.assertRaises(ValueError):
            validate(jobs, self.pairs)

    def test_price_must_match_search_and_details(self):
        jobs = copy.deepcopy(self.jobs)
        job = next(j for j in jobs if j['price_condition'] == 'double')
        current = f"  Price: {job['target_metadata']['price']:,.2f}"
        job['request']['messages'][3]['content'] = job['request']['messages'][3]['content'].replace(current, '  Price: 0.01', 1)
        with self.assertRaises(ValueError):
            validate(jobs, self.pairs)

    def test_runtime_verification_cannot_be_invented(self):
        jobs = copy.deepcopy(self.jobs)
        jobs[0]['input_check']['exact_input_verified'] = True
        with self.assertRaises(ValueError):
            validate(jobs, self.pairs)

    def test_factorial_is_balanced_within_each_pair(self):
        for pair in self.pairs:
            group = [j for j in self.jobs if j['item_id'] == pair['item_id']]
            self.assertEqual(len(group), 32)
            for field, values in [('label', (0, 1)), ('objective', ('welfare', 'facts')),
                                  ('detail_order', ('target_first', 'target_last')),
                                  ('service_condition', ('positive', 'negative')),
                                  ('price_condition', ('base', 'double'))]:
                self.assertEqual([sum(j[field] == value for j in group) for value in values], [16, 16])


if __name__ == '__main__':
    unittest.main()
