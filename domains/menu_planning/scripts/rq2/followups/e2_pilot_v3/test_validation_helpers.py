import hashlib
from pathlib import Path
import tempfile
import unittest

from validation_helpers import (ValidationBlocked, measured_input_check,
    select_layer_on_validation, make_cache_identity, verify_cache,
    REQUIRED_MEASUREMENT_GATES, require_measurement_gates)


class ValidationTests(unittest.TestCase):
    def test_equal_counts_cannot_mask_changed_ids(self):
        report=measured_input_check([1,2,3],3,[1,9,3])
        self.assertTrue(report['count_matches'])
        self.assertFalse(report['exact_input_verified'])
        self.assertEqual(report['first_mismatch'],1)

    def test_missing_ids_and_counts_remain_unknown(self):
        report=measured_input_check([1,2])
        self.assertIsNone(report['count_matches'])
        self.assertIsNone(report['token_ids_match'])
        self.assertFalse(report['exact_input_verified'])

    def test_truncation_reports_boundary(self):
        self.assertEqual(measured_input_check([1,2,3],actual_backend_ids=[1,2])['first_mismatch'],2)

    def test_documented_layer_tie_and_no_test_selection(self):
        rows=[dict(layer=1,val_auroc=.9,val_accuracy=.8,test_auroc=1),
              dict(layer=19,val_auroc=.9,val_accuracy=.8,test_auroc=0),
              dict(layer=21,val_auroc=.9,val_accuracy=.8,test_auroc=.99)]
        self.assertEqual(select_layer_on_validation(rows)['layer'],19)
        rows[0]['val_accuracy']=.81
        self.assertEqual(select_layer_on_validation(rows)['layer'],1)
        with self.assertRaises(ValidationBlocked):select_layer_on_validation([dict(layer=1,val_auroc=.9)])

    def test_cache_rejects_changed_prompt_layer_and_payload(self):
        identity=make_cache_identity(model_id='test',model_revision='pinned',
            template_sha256='template',prompt_text='hello',input_ids=[1,2],positions=[1],
            layers_one_based=[26],dtype='float16',backend='test',backend_versions={'test':'1'})
        with tempfile.NamedTemporaryFile(dir=Path(__file__).resolve().parent, suffix='.testcache', delete=False) as f:
            path=Path(f.name)
        try:
            path.write_bytes(b'payload')
            manifest={**identity,'payload_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            self.assertTrue(verify_cache(path,manifest,identity)['verified'])
            for change in ({'layers_one_based':[25]}, {'prompt_sha256':'different'}, {'model_revision':'other'}):
                with self.assertRaises(ValidationBlocked):verify_cache(path,manifest,{**identity,**change})
            path.write_bytes(b'changed')
            with self.assertRaises(ValidationBlocked):verify_cache(path,manifest,identity)
            with self.assertRaises(ValidationBlocked):verify_cache(path,{},identity)
        finally:
            path.unlink()

    def test_failed_or_unproven_gate_cannot_continue(self):
        evidence={k:{'status':'pass','evidence':'artifact.json'} for k in REQUIRED_MEASUREMENT_GATES}
        self.assertTrue(require_measurement_gates(evidence)['measurement_validated'])
        evidence['silent_context_transfer']['status']='fail'
        with self.assertRaises(ValidationBlocked):require_measurement_gates(evidence)
        evidence['silent_context_transfer']={'status':'pass'}
        with self.assertRaises(ValidationBlocked):require_measurement_gates(evidence)
        with self.assertRaises(ValidationBlocked):require_measurement_gates({})


if __name__=='__main__':unittest.main()
