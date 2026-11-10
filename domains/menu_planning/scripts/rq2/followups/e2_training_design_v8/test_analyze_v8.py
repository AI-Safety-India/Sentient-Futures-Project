"""Synthetic metric/provenance checks. No model, remote access, or real fitting."""
import copy
from itertools import product
from pathlib import Path
import tempfile
import unittest

import numpy as np

from analyze_v8 import (CONDITIONS, JOBS_SHA, PAIRS_SHA, MODEL, REVISION, TEMPLATE,
                        array_sha, canonical_sha, comparison_deltas,
                        independently_verify_fit, summarize_scores,
                        training_interaction_strata, validate_execution_evidence,
                        validate_selected_record, write_once_json)
from fit_direction import fit_direction


def score_fixture():
    # Eight distinct examples, each with the same +2 higher-minus-lower gap.
    return {f'item{i}': {(condition, label): float(2 * label)
                        for condition, label in product(CONDITIONS, (0, 1))}
            for i in range(8)}


def selected_fixture():
    ids = [11, 22, 33]
    job = {'job_id': 'synthetic', 'input_ids': ids,
           'primary_prefix_sha256': canonical_sha(ids), 'positions': {'pos_b': 2, 'pos_a': 0},
           'split': 'train', 'primary_layer_one_based': 26}
    state = np.zeros(4096, dtype=np.float16)
    record = {'job_id': job['job_id'], 'job_sha256': canonical_sha(job),
              'input_ids_sha256': canonical_sha(ids), 'primary_prefix_sha256': canonical_sha(ids),
              'positions': job['positions'], 'selected_array_sha256': array_sha(state),
              'cache_payload_sha256': 'a' * 64, 'cache_manifest_sha256': 'b' * 64,
              'input_check': {'exact_input_verified': True, 'token_ids_match': True,
                              'expected_ids_sha256': canonical_sha(ids), 'actual_backend_count': 3}}
    return job, record, state


class DevelopmentMetricTests(unittest.TestCase):
    def test_shared_offset_is_not_gap_change(self):
        scores = score_fixture()
        for cells in scores.values():
            for label in (0, 1):
                cells['price', label] += 10
        result = summarize_scores(scores, 8)
        effect = result['nuisance_effects']['price']
        self.assertEqual(effect['mean_absolute_variant_shift'], 10)
        self.assertEqual(effect['mean_absolute_common_offset'], 10)
        self.assertEqual(effect['mean_absolute_pair_gap_change'], 0)
        self.assertEqual(effect['pair_sign_changes'], 0)
        self.assertFalse(effect['positive_welfare_mean_exceeds_nuisance_magnitude'])
        self.assertEqual(result['pair_summaries']['price']['positive_pairs'], 8)

    def test_paired_reversal_separate_from_common_offset(self):
        scores = score_fixture()
        for cells in scores.values():
            cells['order', 1] -= 2
            cells['order', 0] += 2
        result = summarize_scores(scores, 8)
        self.assertEqual(result['nuisance_effects']['order']['mean_absolute_common_offset'], 0)
        self.assertEqual(result['nuisance_effects']['order']['mean_pair_gap_change'], -4)
        self.assertEqual(result['nuisance_effects']['order']['pair_sign_changes'], 8)
        self.assertEqual(result['pair_summaries']['order']['negative_pairs'], 8)
        self.assertEqual(result['pair_summaries']['order']['auroc'], 0)

    def test_auc_is_cross_item_and_half_credit_for_ties(self):
        # Gaps (0,1), but pooled positive-vs-negative AUROC is 5/8.
        scores = {i: {(c, l): v[l] for c in CONDITIONS for l in (0, 1)}
                  for i, v in {'a': (0., 0.), 'b': (1., 2.)}.items()}
        report = summarize_scores(scores)['pair_summaries']['base']
        self.assertEqual(report['positive_pairs'], 1)
        self.assertEqual(report['ties'], 1)
        self.assertEqual(report['auroc'], .625)
        self.assertEqual(report['median_pair_gap'], .5)

    def test_missing_pair_or_nonfinite_score_is_rejected(self):
        scores = score_fixture(); scores['item0'].pop(('base', 0))
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            summarize_scores(scores, 8)
        scores = score_fixture(); scores['item0']['base', 0] = np.nan
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            summarize_scores(scores, 8)

    def test_seven_item_sensitivity_has_no_seven_of_eight_flag(self):
        scores = score_fixture(); scores.pop('item0')
        report = summarize_scores(scores, 7)
        self.assertIsNone(report['descriptive_7_of_8_flags'])
        self.assertEqual(report['pair_summaries']['base']['items'], 7)

    def test_delta_signs_describe_new_minus_previous(self):
        old = summarize_scores(score_fixture(), 8)
        scores = score_fixture()
        for cells in scores.values():
            cells['base', 1] += 1
        new = summarize_scores(scores, 8)
        reports = {name: old for name in ('original_e2', 'v5', 'v6', 'v7_corrected_v6')}
        reports['v8'] = new
        delta = comparison_deltas(reports)
        self.assertEqual(delta['v6']['pairs']['base']['mean_pair_gap'], 1)


class ProvenanceAndFitTests(unittest.TestCase):
    def test_execution_binds_loaded_model_job_hashes_and_reviewed_inputs(self):
        jobs = [{'job_id': f'job{i}', 'item_id': f'item{i}'} for i in range(6)]
        model_identity = {'loaded_model_verified': True, 'model_revision': REVISION,
                          'model_dtype': 'bfloat16', 'attention': 'sdpa',
                          'model_class': 'Qwen3_5ForConditionalGeneration'}
        manifest = {'model_identity': model_identity}
        lock = {'job_sha256': {j['job_id']: canonical_sha(j) for j in jobs},
                'model_id': MODEL, 'model_revision': REVISION, 'template_sha256': TEMPLATE,
                'primary_position': 'pos_b', 'primary_layer_one_based': 26}
        release = {'schema': 'rq2_v8_review_release_v1',
                   'source_files': {'training_jobs_draft.json': JOBS_SHA, 'training_pairs_reviewed_draft.json': PAIRS_SHA},
                   'pilot_authorized_by_user': True, 'maximum_new_forwards': 192,
                   'paid_resources_authorized': False, 'remaining_label_reviews': 0,
                   'items': [{'item_id': f'item{i}', 'human_annotation': i < 2,
                              'decision': 'approved' if i < 2 else 'accepted_for_bounded_pilot_by_delegated_agent'} for i in range(6)]}
        validate_execution_evidence(manifest, lock, release, jobs)
        for field in model_identity:
            bad = copy.deepcopy(manifest); bad['model_identity'][field] = 'wrong'
            with self.subTest(model_field=field), self.assertRaisesRegex(ValueError, 'Loaded model identity differs'):
                validate_execution_evidence(bad, lock, release, jobs)
        bad = copy.deepcopy(lock); bad['job_sha256']['job0'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'per-job hashes'):
            validate_execution_evidence(manifest, bad, release, jobs)
        for field in ('training_jobs_draft.json', 'training_pairs_reviewed_draft.json'):
            bad = copy.deepcopy(release); bad['source_files'][field] = 'wrong'
            with self.subTest(reviewed_file=field), self.assertRaisesRegex(ValueError, 'reviewed jobs/pairs'):
                validate_execution_evidence(manifest, lock, bad, jobs)
        bad = copy.deepcopy(release); bad['items'][0]['human_annotation'] = False
        with self.assertRaisesRegex(ValueError, 'two human approvals'):
            validate_execution_evidence(manifest, lock, bad, jobs)

    def test_valid_selected_record_and_tamper_rejection(self):
        job, record, state = selected_fixture()
        validate_selected_record(job, record, state, canonical_sha(job), canonical_sha(job['input_ids']))
        for kind in ('value', 'job_hash', 'ids_hash', 'position', 'runtime_unverified', 'count'):
            damaged = copy.deepcopy(record); vector = state.copy()
            if kind == 'value': vector[7] = 1
            if kind == 'job_hash': damaged['job_sha256'] = 'x' * 64
            if kind == 'ids_hash': damaged['input_ids_sha256'] = 'x' * 64
            if kind == 'position': damaged['positions']['pos_b'] = 1
            if kind == 'runtime_unverified': damaged['input_check']['exact_input_verified'] = False
            if kind == 'count': damaged['input_check']['actual_backend_count'] = 4
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                validate_selected_record(job, damaged, vector, canonical_sha(job), canonical_sha(job['input_ids']))

    def test_wrong_dtype_and_nonfinite_cache_rejected_even_with_correct_hash(self):
        job, record, state = selected_fixture()
        for value in (state.astype(np.float32), np.full(4096, np.nan, dtype=np.float16)):
            damaged = copy.deepcopy(record); damaged['selected_array_sha256'] = array_sha(value)
            with self.assertRaisesRegex(ValueError, 'activation'):
                validate_selected_record(job, damaged, value, canonical_sha(job), canonical_sha(job['input_ids']))

    def test_signed_sum_independently_reproduces_matched_estimator(self):
        rng = np.random.default_rng(846)
        records = []
        for key in product([f'i{n}' for n in range(6)], ('welfare', 'facts'),
                           ('target_first', 'target_last'), ('base', 'double'), ('positive', 'negative'), (0, 1)):
            value = rng.normal(size=13)
            value[0] += (1 if key[1] == 'welfare' else -1) * (1 if key[5] else -1)
            records.append((key, value))
        direction, center, report = fit_direction(records)
        result = independently_verify_fit(list(reversed(records)), direction, center, report)
        self.assertTrue(result['passed'])
        strata = training_interaction_strata(records, direction)['groups']
        self.assertEqual(strata['order|target_first']['contrasts'], 24)
        self.assertEqual(strata['item_order|i0|target_first']['contrasts'], 4)
        with self.assertRaisesRegex(ValueError, 'direction differs'):
            independently_verify_fit(records, -direction, center, report)

    def test_different_output_never_overwrites_prior_result(self):
        workspace = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=workspace) as temporary:
            self.assertTrue(Path(temporary).resolve().is_relative_to(workspace))
            path = Path(temporary) / 'test.json'
            write_once_json(path, {'result': 1})
            before = path.read_bytes()
            write_once_json(path, {'result': 1})
            with self.assertRaisesRegex(ValueError, 'Refusing'):
                write_once_json(path, {'result': 2})
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
