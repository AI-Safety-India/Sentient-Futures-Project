"""Rescore exact cached diagnostic states at L26; no inference or network."""
from pathlib import Path
import io,json,zipfile,hashlib
from collections import defaultdict
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'Sentient-Futures-Project-git/results/rq2'
OUT=DATA/'e2_pilot_v3';OUT.mkdir(exist_ok=True)
archive=ROOT/'rq2_repair/validation_download/validation_artifacts.zip'
weights=DATA/'probe_directions.npz'

def auroc(rows,key):
    a=np.array([r[key] for r in rows if r['label']==1]);b=np.array([r[key] for r in rows if r['label']==0])
    return float(((a[:,None]>b).sum()+.5*(a[:,None]==b).sum())/(len(a)*len(b)))

def summary(rows):
    items=defaultdict(dict)
    for r in rows:
        assert r['label'] not in items[r['item_id']]
        items[r['item_id']][r['label']]=r
    assert all(set(g)=={0,1} for g in items.values())
    out={'observations':len(rows),'independent_items':len(items)}
    for key in ('score_e2','score_content_lr'):
        shifts=[g[1][key]-g[0][key] for g in items.values()]
        out[key]={'auroc':auroc(rows,key),'mean_paired_label1_minus_label0':float(np.mean(shifts)),
            'positive_pairs':sum(v>0 for v in shifts),'ties':sum(v==0 for v in shifts)}
    return out

with np.load(weights,allow_pickle=False) as p:
    assert int(p['e2_layer'])==int(p['content_lr_layer'])==26
    ew=p['e2_w_mm'].copy();em=p['e2_mid_mm'].copy();cw=p['content_w_lr'].copy();cb=float(p['content_b_lr'])
rows=[];max_err=0.;prefixes={};reading_hidden={}
with zipfile.ZipFile(archive) as z:
    protocol=json.loads(z.read('protocol.json'));plans=json.loads(z.read('probe_position_plan.json'))
    old=json.loads(z.read('probe_scores.json'))
    assert hashlib.sha256(weights.read_bytes()).hexdigest()==protocol['probe_sha256']
    oldmap={(r['job'],r['position']):r for r in old['rows']}
    for i,job in enumerate(protocol['jobs']):
        plan=plans[i];assert plan['job']==i
        with np.load(io.BytesIO(z.read(f'probe_{i:03d}.npz')),allow_pickle=False) as a:
            assert np.array_equal(a['input_ids'],plan['input_ids'])
            assert np.array_equal(a['indices'],plan['indices'])
            assert a['hidden_states'].shape[1:]==(32,4096)
            for n,idx in enumerate(a['indices']):
                position='primary' if n==0 else 'reading'
                h=a['hidden_states'][n,25].astype(np.float32)
                assert np.isfinite(h).all()
                row=dict(job=i,item_id=job['item_id'],kind=job['kind'],question=job.get('question'),
                    label=job['label'],position=position,token_index=int(idx),
                    score_e2=float(np.dot(h-em,ew)),score_content_lr=float(np.dot(h,cw)+cb))
                original=oldmap[(i,position)]
                assert original['token_index']==int(idx)
                max_err=max(max_err,abs(row['score_e2']-original['score_e2']))
                row['causal_prefix_sha256']=hashlib.sha256(a['input_ids'][:int(idx)+1].tobytes()).hexdigest()
                if position=='reading':
                    key=(job['item_id'],job['label'])
                    if key in prefixes:
                        assert np.array_equal(prefixes[key],a['input_ids'][:int(idx)+1])
                        assert np.array_equal(reading_hidden[key],h)
                    else:
                        prefixes[key]=a['input_ids'][:int(idx)+1].copy();reading_hidden[key]=h.copy()
                rows.append(row)
assert len(rows)==160 and max_err<1e-5
groups=defaultdict(list)
for r in rows:groups[(r['kind'],r['question'],r['position'])].append(r)
summaries={f'{k[0]}|{k[1]}|{k[2]}':summary(v) for k,v in groups.items()}
dedup={}
for r in rows:
    if r['position']=='reading':dedup.setdefault((r['item_id'],r['label']),r)
summaries['e2_tool|unprompted_reading_deduplicated']=summary(list(dedup.values()))
interaction={}
for kind in ['e2_original','e2_tool']:
    grouped=defaultdict(dict)
    for r in rows:
        if r['kind']==kind and r['position']=='primary':grouped[r['item_id']][(r['label'],r['question'])]=r
    interaction[kind]={}
    for score in ['score_e2','score_content_lr']:
        values=[(g[(1,'welfare')][score]-g[(1,'value')][score])-(g[(0,'welfare')][score]-g[(0,'value')][score]) for g in grouped.values()]
        interaction[kind][score]={'mean_paired_interaction':float(np.mean(values)),'positive_items':sum(v>0 for v in values),'items':len(values),'item_interactions':dict(zip(grouped.keys(),values))}
report=dict(scope='Exact cached-input same-layer diagnostic rescoring; development evidence, not new validation',layer=26,probe_npzs=120,scored_positions=160,deduplicated_reading_positions=20,
    input_ids_and_indices_match_all_plans=True,e2_max_absolute_difference_from_saved_scores=max_err,
    duplicated_reading_prefix_and_states_exactly_equal=True,
    cosine_e2_content_lr=float(np.dot(ew,cw)/(np.linalg.norm(ew)*np.linalg.norm(cw))),
    archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),weights_sha256=hashlib.sha256(weights.read_bytes()).hexdigest(),
    environment=old['environment'],summaries=summaries,interaction=interaction,rows=rows,
    limitations=['Same layer does not mean same training context/position: saved content LR was trained on tool-response states, E2 on pre-answer states.',
    'E1 groups label judgement polarity on identical harmful facts; E2 groups label harmful/safe listings. Their AUROCs are not the same task.',
    'Previously inspected ten-item diagnostic set; no fresh holdout, no scientific pass claim.',
    'Reading observations duplicated across welfare/value future questions share identical causal prefixes and states; aggregate once per item/label.',
    'Changed descriptions/tags/context require new activations; these historical scores cannot be assigned to revised pilot prompts.',
    'Content LR and E2 score scales differ; absolute shift magnitudes are not directly comparable effect sizes.'],model_forwards=0,network_calls=0)
(OUT/'diagnostic_rescore.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k in ['scope','probe_npzs','scored_positions','e2_max_absolute_difference_from_saved_scores','cosine_e2_content_lr','summaries']},indent=2))
lines=['Exact cached diagnostic rescoring: E2 vs content LR, both L26','',
       'No new prompts, model forwards or network calls. 120 cached NPZs / 160 positions. All input IDs and indices match extraction plans. E2 scores reproduce saved results to <1e-5.',
       '', 'Group | E2 AUROC | Content LR AUROC | E2 positive pairs | Content positive pairs']
for name,s in summaries.items():
    lines.append(f"{name} | {s['score_e2']['auroc']:.3f} | {s['score_content_lr']['auroc']:.3f} | {s['score_e2']['positive_pairs']}/{s['independent_items']} | {s['score_content_lr']['positive_pairs']}/{s['independent_items']}")
lines+=['','Interpretation limits:']+report['limitations']
lines+=['','The stored tool-response reading boundary is not the later assistant-start silent position. These are historical baseline diagnostics, not the revised v3 pilot.']
(OUT/'diagnostic_rescore.txt').write_text('\n'.join(lines)+'\n')
