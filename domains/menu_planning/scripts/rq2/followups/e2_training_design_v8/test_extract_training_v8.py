"""Pure local runner contract tests: no torch/model/inference/network needed."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import extract_training_v8 as e


HERE = Path(__file__).resolve().parent


class RunnerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = e.read_json(HERE/'training_jobs_draft.json')
        cls.versions = dict(torch='test', transformers='test', numpy='test')

    def make_protocol(self, label_sha='a'*64):
        return e.make_execution_manifest(HERE/'training_jobs_draft.json',
            label_review_sha256=label_sha,
            free_runtime_evidence=dict(explicitly_free=True, evidence='synthetic test only',
                                       verified_at_utc='synthetic'),
            expected_backend_versions=self.versions)

    def test_frozen_file_192_unique_prefixes(self):
        report = e.preflight_package(HERE)
        self.assertEqual(report['jobs'], 192)
        self.assertEqual(report['unique_input_prefixes'], 192)
        self.assertEqual(report['model_runs_started'], 0)

    def test_lock_requires_explicit_free_evidence(self):
        with self.assertRaisesRegex(ValueError, 'free-runtime'):
            e.make_execution_manifest(HERE/'training_jobs_draft.json',
                label_review_sha256='a'*64, free_runtime_evidence=dict(explicitly_free=False),
                expected_backend_versions=self.versions)

    def test_lock_binds_review_content_and_all_job_hashes(self):
        with tempfile.TemporaryDirectory(dir=HERE, prefix='_runner_test_') as d:
            self.assertEqual(Path(d).resolve().parent, HERE)
            label = Path(d)/'review.json'
            label.write_text('{"synthetic":true}', encoding='utf-8')
            protocol = self.make_protocol(e.file_sha(label))
            e.validate_lock(HERE/'training_jobs_draft.json', protocol, label)
            tampered = copy.deepcopy(protocol)
            tampered['job_sha256'][self.jobs[0]['job_id']] = 'b'*64
            with self.assertRaisesRegex(ValueError, 'lock schema'):
                e.validate_lock(HERE/'training_jobs_draft.json', tampered, label)
            label.write_text('{"synthetic":false}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'label-review'):
                e.validate_lock(HERE/'training_jobs_draft.json', protocol, label)

    def test_duplicate_factorial_and_wrong_positions_rejected(self):
        jobs = copy.deepcopy(self.jobs)
        jobs[1] = copy.deepcopy(jobs[0])
        with self.assertRaises(ValueError):
            e.validate_jobs(jobs)
        jobs = copy.deepcopy(self.jobs)
        jobs[0]['positions']['pos_b'] -= 1
        with self.assertRaisesRegex(ValueError, 'positions'):
            e.validate_jobs(jobs)

    def test_resume_never_repeats_an_ambiguous_forward(self):
        j = self.jobs[0]
        ledger = {j['job_id']: dict(state='forward_started', attempts=1, job_sha256=e.canonical(j))}
        with self.assertRaisesRegex(ValueError, 'no automatic retry'):
            e.reconcile_resume(self.jobs, ledger, set())
        pending = e.reconcile_resume(self.jobs, ledger, {j['job_id']})
        self.assertEqual(len(pending), 191)
        self.assertNotIn(j, pending)

    def test_resume_requires_producer_ledger(self):
        with self.assertRaisesRegex(ValueError, 'producer'):
            e.reconcile_resume(self.jobs, {}, {self.jobs[0]['job_id']})

    def test_cache_requires_runtime_input_evidence_and_payload_hash(self):
        j = self.jobs[0]
        identity = e.cache_identity(j, self.versions, dict(synthetic=True))
        with tempfile.TemporaryDirectory(dir=HERE, prefix='_runner_test_') as d:
            self.assertEqual(Path(d).resolve().parent, HERE)
            dest = Path(d)/(j['job_id']+'.npz')
            np.savez_compressed(dest, hidden_states=np.zeros((2,32,4096), dtype=np.float16),
                input_ids=np.asarray(j['input_ids']),
                indices=np.asarray([j['positions']['pos_b'], j['positions']['pos_a']]))
            manifest = dict(identity, payload_sha256=e.file_sha(dest), input_check=dict(
                exact_input_verified=True, token_ids_match=True,
                actual_backend_count=len(j['input_ids']), expected_ids_sha256=e.canonical(j['input_ids'])))
            e.atomic_json(dest.with_suffix('.json'), manifest)
            _, vector = e.verify_cache(dest, j, identity, np)
            self.assertEqual(vector.shape, (4096,))
            self.assertEqual(vector.dtype, np.float16)
            manifest['input_check']['exact_input_verified'] = False
            e.atomic_json(dest.with_suffix('.json'), manifest)
            with self.assertRaisesRegex(ValueError, 'runtime exact-input'):
                e.verify_cache(dest, j, identity, np)
            manifest['input_check']['exact_input_verified'] = True
            manifest['payload_sha256'] = 'a'*64
            e.atomic_json(dest.with_suffix('.json'), manifest)
            with self.assertRaisesRegex(ValueError, 'payload hash'):
                e.verify_cache(dest, j, identity, np)

    def test_unsafe_job_name_rejected(self):
        jobs = copy.deepcopy(self.jobs)
        jobs[0]['job_id'] = '../original_cache'
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            e.validate_jobs(jobs)

    def test_all_target_boundaries_using_cached_tokenizer_without_model(self):
        from build_jobs_v8 import load_tokenizer
        cached, _ = load_tokenizer()

        class Adapter:
            chat_template = cached.chat_template

            def encode(self, text, add_special_tokens=False):
                return cached.backend.encode(text, add_special_tokens=add_special_tokens).ids

            def decode(self, ids, skip_special_tokens=False):
                return cached.backend.decode(ids, skip_special_tokens=skip_special_tokens)

            def apply_chat_template(self, messages, **kwargs):
                return cached.apply_chat_template(messages, **kwargs)

        e.verify_tokenizer(self.jobs, Adapter())


if __name__ == '__main__':
    unittest.main()
