from pathlib import Path
import json,hashlib,copy
from build_jobs import validate,ROOT,CODE,OUT
jobs=json.loads((OUT/'jobs.json').read_text(encoding='utf-8'));validate(jobs)
for kind in ['price_confound','wrong_order','wrong_boundary']:
    bad=copy.deepcopy(jobs)
    if kind=='price_confound':
        next(j for j in bad if j['cohort']=='fresh' and j['condition']=='price')['target_metadata']['rating']=1.0
    elif kind=='wrong_order':
        j=next(j for j in bad if j['cohort']=='fresh' and j['condition']=='order');j['request']['messages'][-2:]=j['request']['messages'][-2:][::-1]
    else:bad[0]['positions']['pos_b']-=1
    try:validate(bad)
    except AssertionError:pass
    else:raise AssertionError('Negative test not rejected: '+kind)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=dict(jobs_sha256=sha(OUT/'jobs.json'),development_only=True,paid_resources_authorized=False,execution_authority='User requested tests on existing confirmed-free runtime; no new resources permitted.',expected_jobs=78,primary='Original saved E2 L26 at original pos_b definition',screen_minimum_positive_pairs=7,screen_total_pairs=8,secondary_cannot_rescue_primary=True,predeclared_novelty_sensitivity_exclude='fresh_v4_07',independent_human_labels=False,original_probe_sha256=sha(OUT.parent/'probe_directions.npz'),code_sha256={n:sha(CODE/n) for n in ['run_checks.py','analyze.py','build_jobs.py','fresh_pairs.json','novelty_review.json','boundary_review.json','protocolproposal.txt']},source_sha256=json.loads((OUT.parent/'e2_pilot_v3/core_42_manifest.json').read_text(encoding='utf-8'))['source_sha256'],structural_negative_tests_passed=3,analysis_tests_passed=6)
(OUT/'execution_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Frozen:',manifest['jobs_sha256']);print('Job token lengths',min(len(j['input_ids']) for j in jobs),max(len(j['input_ids']) for j in jobs));print('3 negative structural checks rejected correctly')
