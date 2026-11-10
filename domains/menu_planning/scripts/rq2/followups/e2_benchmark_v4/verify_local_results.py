from pathlib import Path
import json,base64,hashlib,zipfile,io
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
CODE=Path(__file__).resolve().parent
DATA=ROOT/'Sentient-Futures-Project-git/results/rq2/e2_benchmark_v4'
log=(CODE/'export_transfer.log').read_text(encoding='utf-8')
assert 'EXPORT_COMPLETE' in log
lines=log.splitlines()
expected=next(x.split(' ',1)[1] for x in lines if x.startswith('EXPORT_SHA256 '))
b=base64.b64decode(''.join(x[9:] for x in lines if x.startswith('V4EXPORT:')))
assert hashlib.sha256(b).hexdigest()==expected
with zipfile.ZipFile(io.BytesIO(b)) as z:
    assert set(z.namelist())=={'selected_layers_1_26.npz','selected_layer_manifest.json'}
    z.extractall(DATA)
manifest=json.loads((DATA/'selected_layer_manifest.json').read_text())
assert hashlib.sha256((DATA/'selected_layers_1_26.npz').read_bytes()).hexdigest()==manifest['selected_npz_sha256']
report=json.loads((DATA/'benchmark_validation.json').read_text())
jobs=json.loads((DATA/'jobs.json').read_text(encoding='utf-8'))
assert hashlib.sha256((DATA/'jobs.json').read_bytes()).hexdigest()==report['core_jobs_sha256']==manifest['jobs_sha256']
assert hashlib.sha256((DATA.parent/'probe_directions.npz').read_bytes()).hexdigest()==report['baseline_weights_sha256']
expected_rows={(r['job_id'],r['position']):r for r in report['rows']}
expected_payloads={r['job_id']:r['payload_sha256'] for r in report['cache_evidence']}
max_error=0.0;max_float32_score_difference=0.0;float32_scores={}
with np.load(DATA/'selected_layers_1_26.npz',allow_pickle=False) as z,np.load(DATA.parent/'probe_directions.npz',allow_pickle=False) as w:
    assert len(z.files)==78
    for entry in manifest['records']:
        h=z[entry['job_id']]
        assert h.shape==(2,2,4096) and h.dtype==np.float16 and np.isfinite(h).all()
        assert hashlib.sha256(h.tobytes()).hexdigest()==entry['selected_array_sha256']
        assert expected_payloads[entry['job_id']]==entry['original_npz_sha256']
        for n,position in enumerate(['pos_b','pos_a']):
            h1=h[n,0].astype(float);h26=h[n,1].astype(float)
            actual=dict(saved_e2_l26=float(np.dot(h26-w['e2_mid_mm'],w['e2_w_mm'])),content_lr_l26=float(np.dot(h26,w['content_w_lr'])+float(w['content_b_lr'])),e1_l1=float(np.dot(h1-w['e1_mid_mm'],w['e1_w_mm'])))
            for key,value in actual.items():max_error=max(max_error,abs(value-expected_rows[entry['job_id'],position][key]))
            f32=float(np.dot(h[n,1].astype(np.float32)-w['e2_mid_mm'],w['e2_w_mm']))
            float32_scores[entry['job_id'],position]=f32
            max_float32_score_difference=max(max_float32_score_difference,abs(f32-actual['saved_e2_l26']))
assert max_error<1e-10
execution=json.loads((DATA/'execution_manifest.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in execution['source_sha256'].items())
assert all(hashlib.sha256((CODE/p).read_bytes()).hexdigest()==sha for p,sha in execution['code_sha256'].items())
groups={}
for j in jobs:groups.setdefault((j['cohort'],j['item_id'],j['condition']),{})[j['label']]=j['job_id']
for g in groups.values():
    for position in ['pos_b','pos_a']:
        a=float32_scores[g[1],position]-float32_scores[g[0],position]
        b=expected_rows[g[1],position]['saved_e2_l26']-expected_rows[g[0],position]['saved_e2_l26']
        assert np.sign(a)==np.sign(b)
result=dict(verified_selected_arrays=78,reproduced_positions=156,reproduced_probe_scores=468,max_score_error=max_error,max_float32_e2_difference=max_float32_score_difference,float32_pair_signs_identical=True,original_source_hashes_unchanged=True,frozen_code_hashes_unchanged=True,full_archive_location='/marimo/e2_benchmark_v4/full_v4_results.zip',full_archive_local=False)
(DATA/'local_reproduction.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
