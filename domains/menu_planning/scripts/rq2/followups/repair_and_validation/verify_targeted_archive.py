import hashlib, io, json, zipfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent/'Sentient-Futures-Project-git/results/rq2'
p = ROOT/'rq2_targeted_repair_v1.zip'
remote = (ROOT/'remote_archive_hash.txt').read_text(encoding='utf-8')
expected_hash = next(s.split(':',1)[1] for s in remote.splitlines() if s.startswith('ARCHIVE_SHA256:'))
assert hashlib.sha256(p.read_bytes()).hexdigest() == expected_hash
projections = json.loads((ROOT/'corrected_projections.json').read_text())
score_lookup = {(r['run_id'],r['kind'],r['sub_idx']):r for r in projections['rows']}
errors = []
with np.load(DATA/'probe_directions.npz',allow_pickle=False) as probes, zipfile.ZipFile(p) as z:
    assert z.testzip() is None
    report = json.loads(z.read('report.json'))
    assert report == json.loads((ROOT/'gpu_repair_report.json').read_text())
    assert len(z.namelist()) == 25
    for job in report['completed_jobs']:
        with np.load(io.BytesIO(z.read(job['file'])),allow_pickle=False) as a:
            h=a['hidden_states']
            assert h.shape == (len(job['indices']),32,4096) and np.isfinite(h).all()
            assert np.array_equal(a['token_indices'],job['indices'])
            assert str(a['signature'].item()) == job['signature']
            assert hashlib.sha256(a['input_ids'].astype(np.int64).tobytes()).hexdigest() == job['input_ids_sha256']
            if job['kind']=='replacement':
                for i,meta in enumerate(job['positions']):
                    r=score_lookup[job['run_id'],meta['kind'],meta['sub_idx']]
                    for name in ('content','e1','e2'):
                        score=float(np.dot(h[i,int(probes[name+'_layer'])-1].astype(np.float32)-probes[name+'_mid_mm'],probes[name+'_w_mm']))
                        errors.append(abs(score-r['score_'+name]))
assert len(errors)==225 and max(errors)<1e-5
out=dict(passed=True,archive_sha256=expected_hash,jobs=24,score_comparisons=len(errors),maximum_projection_difference=max(errors))
(DATA/'repair_v2/archive_verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
