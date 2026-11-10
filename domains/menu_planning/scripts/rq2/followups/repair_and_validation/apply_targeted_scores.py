"""Build a versioned exploratory score set; preserve all original research files."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'Sentient-Futures-Project-git/results/rq2'
OUT = DATA / 'repair_v2'
INPUT = OUT / 'inputs'
INPUT.mkdir(parents=True, exist_ok=True)
(INPUT/'t2').mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT/'Sentient-Futures-Project-git/domains/menu_planning/scripts/rq2'))
from repair_analysis import run

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source_paths = ['benchmark_probe_scores_1200.csv', 't2/qwen35_positions_1200.jsonl', 'qwen35_rq1_scores_1200.csv', 'probe_directions.npz']
before = {name: sha(DATA/name) for name in source_paths}
report = json.loads((ROOT/'rq2_repair/gpu_repair_report.json').read_text())
projection = json.loads((ROOT/'rq2_repair/corrected_projections.json').read_text())
manifest = json.loads((ROOT/'rq2_repair/targeted_repair_manifest.json').read_text())
assert projection['probe_sha256'] == before['probe_directions.npz']
assert report['environment']['audit_sha256'] == manifest['audit_sha256']
assert report['summary']['completed_jobs'] == 24
expected = {(r['run_id'], p['kind'], p['sub_idx']) for r in manifest['prefix_repairs'] for p in r['positions']}
assert len(expected) == 75
with (DATA/source_paths[0]).open(newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fields = list(reader.fieldnames)
    rows = list(reader)
lookup = {(r['run_id'], r['pos_type'], int(r['sub_idx'])): r for r in rows}
assert len(lookup) == len(rows) == 6064
original_scores = {k: {p: r['score_'+p] for p in ('content', 'e1', 'e2')} for k,r in lookup.items()}
records = [json.loads(x) for x in (DATA/source_paths[1]).read_text().splitlines()]
record_lookup = {r['run_id']:r for r in records}
changes = []
seen = set()
for p in projection['rows']:
    key = (p['run_id'], p['kind'], p['sub_idx'])
    assert key in expected and key not in seen
    seen.add(key)
    row = lookup[key]
    if p['kind'] == 'pos_a':
        assert row['option_id'] == p['option_id']
    for name in ('content', 'e1', 'e2'):
        changes.append(dict(run_id=key[0], pos_type=key[1], sub_idx=key[2], probe=name, old_score=float(row['score_'+name]), new_score=p['score_'+name]))
        row['score_'+name] = repr(p['score_'+name])
    # Keep final-replay tok_idx for chronology; original-call coordinates are separate.
    row.update(activation_source='repaired_original_call', activation_call_index=p['call_index'], activation_token_index=p['new_token_index'], activation_file=p['file'])
assert seen == expected
metadata_changes = []
for job in report['completed_jobs']:
    if job['kind'] != 'diagnostic':
        continue
    rec = record_lookup[job['run_id']]
    ordered = [('pos_a',x) for x in rec['pos_a']] + [('pos_b',x) for x in rec['pos_b']]
    if rec['pos_c'] is not None:
        ordered.append(('pos_c',rec['pos_c']))
    for change in job['changes']:
        kind, pos = ordered[change['old_cache_row']]
        sub = int(pos.get('sub_idx',0)) if kind != 'pos_c' else 0
        key = (job['run_id'],kind,sub)
        assert key not in expected and pos['tok_idx'] == change['stored_index']
        row = lookup[key]
        assert int(row['tok_idx']) == change['stored_index']
        pos['tok_idx'] = change['corrected_index']
        row['tok_idx'] = str(change['corrected_index'])
        metadata_changes.append(dict(run_id=key[0],pos_type=kind,sub_idx=sub,old_index=change['stored_index'],corrected_index=change['corrected_index']))
assert len(metadata_changes) == 12
for key,row in lookup.items():
    if key not in expected:
        assert all(row['score_'+p] == original_scores[key][p] for p in ('content','e1','e2'))
    if 'activation_source' not in row:
        row.update(activation_source='original_cache',activation_call_index='',activation_token_index=row['tok_idx'],activation_file=key[0]+'.npz')
fields += ['activation_source','activation_call_index','activation_token_index','activation_file']
with (INPUT/source_paths[0]).open('w', newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
(INPUT/source_paths[1]).write_text(''.join(json.dumps(r)+'\n' for r in records),encoding='utf-8')
for name in source_paths[2:]:
    shutil.copy2(DATA/name,INPUT/name)
result = run(INPUT, output_dir=OUT)
assert before == {name: sha(DATA/name) for name in source_paths}
audit = dict(status='Exploratory targeted repair; not construct or historical backend validation',original_input_sha256=before,environment=report['environment'],replacement_runs=len({k[0] for k in seen}),replacement_rows=len(seen),unchanged_score_rows=len(rows)-len(seen),metadata_only_runs=len(report['diagnostic_runs']),metadata_only_positions=metadata_changes,score_changes=changes,diagnostic_comparisons=report['diagnostic_comparisons'],notes=['Original caches and score files unchanged.','Diagnostic caches retained: corrected positions agree much more closely than stale indices. Numerical differences remain; no universal tolerance or historical fidelity pass is asserted.','tok_idx is the final-replay chronological coordinate; activation_token_index is the coordinate within activation_call_index for repaired rows.','Only primary tok_idx metadata corrected. Auxiliary old positions and historical length fields remain historical and are not validated for new extraction.'])
(OUT/'repair_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
with (OUT/'score_changes.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(changes[0])); w.writeheader(); w.writerows(changes)
old = json.loads((DATA/'repair_v1/analysis.json').read_text())
for condition in ('neutral','ethical'):
    print(condition,'E1 first read',old['auroc'][condition]['first_read']['e1']['auroc'],'->',result['auroc'][condition]['first_read']['e1'])
for entry in result['thresholds']:
    if entry['unit']=='option' and entry['target_safe_exceedance']==.05:
        print(entry['condition'],entry['counts'])
print('Preserved originals; wrote',OUT)
