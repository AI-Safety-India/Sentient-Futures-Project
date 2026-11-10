from pathlib import Path
import json,hashlib,base64,zipfile,io
import numpy as np
from analyze_factual import fit_direction,cosine
ROOT=Path(__file__).resolve().parents[2];CODE=Path(__file__).resolve().parent
DATA=ROOT/'Sentient-Futures-Project-git/results/rq2/e2_factual_v6'
V5=DATA.parent/'e2_redesign_v5';V4=DATA.parent/'e2_benchmark_v4'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
log=(CODE/'export_transfer.log').read_text(encoding='utf-8');assert 'EXPORT_COMPLETE' in log
lines=log.splitlines();digest=next(x.split(' ',1)[1] for x in lines if x.startswith('EXPORT_SHA256 '))
b=base64.b64decode(''.join(x[9:] for x in lines if x.startswith('V6EXPORT:')))
assert hashlib.sha256(b).hexdigest()==digest
with zipfile.ZipFile(io.BytesIO(b)) as z:
    assert set(z.namelist())=={'training_pos_b_l26.npz','selected_training_manifest.json','candidate_v6_direction.npz'}
    z.extractall(DATA)
report=read(DATA/'factual_analysis.json');jobs=read(DATA/'jobs.json');m=read(DATA/'selected_training_manifest.json');execution=read(DATA/'execution_manifest.json')
assert sha(DATA/'jobs.json')==report['jobs_sha256']==m['jobs_sha256']==execution['jobs_sha256']
assert sha(DATA/'training_pos_b_l26.npz')==m['selected_npz_sha256']
oldm=read(V5/'selected_training_manifest.json');assert sha(V5/'training_pos_b_l26.npz')==oldm['selected_npz_sha256']
oldrecords={r['job_id']:r for r in oldm['records']};records={r['job_id']:r for r in m['records']}
evidence={r['job_id']:r['payload_sha256'] for r in report['new_cache_evidence']};oldevidence={r['job_id']:r['payload_sha256'] for r in report['welfare_cache_evidence']}
states={};oldstates={}
with np.load(DATA/'training_pos_b_l26.npz',allow_pickle=False) as z,np.load(V5/'training_pos_b_l26.npz',allow_pickle=False) as old:
    assert len(z.files)==24
    for j in jobs:
        h=z[j['job_id']];sid=j['source_v5_job_id'];w=old[sid]
        assert h.shape==w.shape==(4096,) and h.dtype==w.dtype==np.float16
        assert np.isfinite(h).all() and np.isfinite(w).all()
        for arr,rec,expected in [(h,records[j['job_id']],evidence[j['job_id']]),(w,oldrecords[sid],oldevidence[sid])]:
            assert hashlib.sha256(arr.tobytes()).hexdigest()==rec['selected_array_sha256'] and rec['original_npz_sha256']==expected
        states[j['item_id'],'facts',j['detail_order'],j['label']]=h.astype(float)
        states[j['item_id'],'welfare',j['detail_order'],j['label']]=w.astype(float)
    for j in read(V5/'jobs.json'):
        if j['split']=='train':oldstates[j['item_id'],j['objective'],j['detail_order'],j['label']]=old[j['job_id']].astype(float)
w,center,_=fit_direction(states)
with np.load(DATA/'candidate_v6_direction.npz',allow_pickle=False) as z:
    weight_error=float(np.max(abs(w-z['direction'])));center_error=float(np.max(abs(center-z['center'])))
    assert weight_error<1e-12 and center_error<1e-12
rows={(r['job_id'],r['position']):r for r in report['rows']};error=0.;count=0
with np.load(V4/'selected_layers_1_26.npz',allow_pickle=False) as z:
    for j in read(V5/'jobs.json'):
        if j['split']!='development':continue
        for n,pos in enumerate(['pos_b','pos_a']):
            value=float(np.dot(z[j['job_id']][n,1].astype(float)-center,w))
            error=max(error,abs(value-rows[j['job_id'],pos]['candidate_v6_l26']));count+=1
assert error<1e-10
assert all(sha(CODE/n)==h for n,h in execution['code_and_input_sha256'].items())
assert all(sha(Path(n))==h for n,h in execution['source_sha256'].items())
items=sorted({k[0] for k in states})
oldcontent=np.mean([((oldstates[i,'welfare',o,1]-oldstates[i,'welfare',o,0])+(oldstates[i,'commercial',o,1]-oldstates[i,'commercial',o,0]))/2 for i in items for o in ['target_first','target_last']],axis=0)
with np.load(V5/'candidate_v5_direction.npz',allow_pickle=False) as z:
    fixed=dict(status='post_run_descriptive_reference_comparison_not_selection',reference='Same frozen v5 training content main-effect vector for both candidates',v5_cosine=cosine(z['direction'],oldcontent),v6_cosine=cosine(w,oldcontent),interpretation='Geometric overlap only; not proof of content/evaluation separation.')
(DATA/'fixed_reference_content_diagnostic.json').write_text(json.dumps(fixed,indent=2),encoding='utf-8')
result=dict(new_factual_arrays_verified=24,reused_welfare_arrays_verified=24,cached_development_arrays_reused=64,candidate_scores_reproduced=count,max_weight_error=weight_error,max_center_error=center_error,max_score_error=error,frozen_code_and_original_source_hashes_unchanged=True,full_new_cache_archive='/marimo/e2_factual_v6/full_v6_results.zip',full_new_cache_archive_local=False)
(DATA/'local_reproduction.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2));print(json.dumps(fixed,indent=2))
