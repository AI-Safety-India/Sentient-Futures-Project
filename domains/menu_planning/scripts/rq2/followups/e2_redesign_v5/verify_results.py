from pathlib import Path
import json,hashlib,base64,zipfile,io
import numpy as np
from fit_direction import fit_direction
ROOT=Path(__file__).resolve().parents[2];CODE=Path(__file__).resolve().parent
DATA=ROOT/'Sentient-Futures-Project-git/results/rq2/e2_redesign_v5'
OLD=DATA.parent/'e2_benchmark_v4'
log=(CODE/'export_transfer.log').read_text(encoding='utf-8');assert 'EXPORT_COMPLETE' in log
lines=log.splitlines();expected=next(x.split(' ',1)[1] for x in lines if x.startswith('EXPORT_SHA256 '))
b=base64.b64decode(''.join(x[9:] for x in lines if x.startswith('V5EXPORT:')))
assert hashlib.sha256(b).hexdigest()==expected
with zipfile.ZipFile(io.BytesIO(b)) as z:
    assert set(z.namelist())=={'training_pos_b_l26.npz','selected_training_manifest.json','candidate_v5_direction.npz'}
    z.extractall(DATA)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=read(DATA/'development_analysis.json');manifest=read(DATA/'selected_training_manifest.json');jobs=read(DATA/'jobs.json');execution=read(DATA/'execution_manifest.json')
assert sha(DATA/'jobs.json')==report['jobs_sha256']==manifest['jobs_sha256']==execution['jobs_sha256']
assert sha(DATA/'training_pos_b_l26.npz')==manifest['selected_npz_sha256']
records={r['job_id']:r for r in manifest['records']};payloads={r['job_id']:r['payload_sha256'] for r in report['training_cache_evidence']}
states={}
with np.load(DATA/'training_pos_b_l26.npz',allow_pickle=False) as z:
    assert len(z.files)==48
    for j in jobs:
        if j['split']!='train':continue
        h=z[j['job_id']];m=records[j['job_id']]
        assert h.shape==(4096,) and h.dtype==np.float16 and np.isfinite(h).all()
        assert hashlib.sha256(h.tobytes()).hexdigest()==m['selected_array_sha256'] and m['original_npz_sha256']==payloads[j['job_id']]
        states[j['item_id'],j['objective'],j['detail_order'],j['label']]=h.astype(float)
w,center,fit=fit_direction(states)
with np.load(DATA/'candidate_v5_direction.npz',allow_pickle=False) as z:
    weight_error=float(np.max(np.abs(w-z['direction'])));center_error=float(np.max(np.abs(center-z['center'])))
    assert weight_error<1e-12 and center_error<1e-12
rows={(r['job_id'],r['position']):r for r in report['rows']};error=0.;count=0
with np.load(OLD/'selected_layers_1_26.npz',allow_pickle=False) as z:
    for j in jobs:
        if j['split']!='development':continue
        for n,pos in enumerate(['pos_b','pos_a']):
            actual=float(np.dot(z[j['job_id']][n,1].astype(float)-center,w))
            error=max(error,abs(actual-rows[j['job_id'],pos]['candidate_v5_l26']));count+=1
assert error<1e-10
assert all(sha(CODE/n)==h for n,h in execution['code_and_input_sha256'].items())
prep=read(DATA/'preparation_manifest.json')
assert all(sha(ROOT/n)==h for n,h in prep['source_sha256'].items())
result=dict(training_arrays_verified=48,cached_development_arrays_reused=64,candidate_scores_reproduced=count,max_weight_error=weight_error,max_center_error=center_error,max_score_error=error,frozen_code_and_original_source_hashes_unchanged=True,full_training_cache_archive='/marimo/e2_redesign_v5/full_v5_results.zip',full_training_cache_archive_local=False)
(DATA/'local_reproduction.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
