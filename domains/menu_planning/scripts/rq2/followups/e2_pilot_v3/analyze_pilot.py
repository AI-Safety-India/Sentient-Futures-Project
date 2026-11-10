"""Offline development analysis for versioned E2 pilot activations.

Never performs model inference, downloads, sign/layer searches or automatic
scientific pass decisions. A runner-schema-specific loader is defined below.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from validation_helpers import make_cache_identity,verify_cache,ValidationBlocked,ids_sha256


def exact_auc(labels, scores):
    labels=np.asarray(labels);scores=np.asarray(scores,dtype=np.float64)
    high=scores[labels==1];low=scores[labels==0]
    if not len(high) or not len(low):return None
    return float(((high[:,None]>low).sum()+.5*(high[:,None]==low).sum())/(len(high)*len(low)))


def loo_e2_interactions(states):
    """Fixed-L26 LOO difference-in-differences; states[item][(label,condition)].

    Each state is a vector already read from the primary L26 position. The four
    questioned vectors fit each fold; silent vectors never enter fitting.
    The held-out item's questioned states are excluded too. No sign flipping.
    """
    expected={(label,condition) for label in (0,1) for condition in ('silent','welfare','value')}
    if len(states)<2:raise ValueError('At least two items required')
    for item,group in states.items():
        if set(group)!=expected:raise ValueError(f'Incomplete/duplicate conditions for {item}')
        if any(np.asarray(v).ndim!=1 or not np.isfinite(v).all() for v in group.values()):raise ValueError('Invalid activation vector')
    dims={np.asarray(v).shape for g in states.values() for v in g.values()}
    if len(dims)!=1:raise ValueError('Hidden dimensions differ')
    results=[]
    for omitted in sorted(states):
        training=[item for item in sorted(states) if item!=omitted]
        differences=[]
        for item in training:
            g=states[item]
            differences.append((g[(1,'welfare')]-g[(1,'value')])-(g[(0,'welfare')]-g[(0,'value')]))
        direction=np.mean(differences,axis=0,dtype=np.float64)
        norm=float(np.linalg.norm(direction))
        if norm<=1e-12:
            results.append(dict(held_out_item=omitted,training_items=training,status='zero_interaction_direction',silent_pair_shift=None))
            continue
        direction/=norm
        g=states[omitted]
        shift=float(np.dot(g[(1,'silent')]-g[(0,'silent')],direction))
        results.append(dict(held_out_item=omitted,training_items=training,status='computed',
            training_interaction_norm=norm,silent_pair_shift=shift,positive=shift>0,tied=shift==0,
            direction=direction.tolist()))
    return dict(layer_one_based=26,fit_conditions=['welfare','value'],evaluated_condition='silent',
        evaluated_position='primary assistant-start boundary',sign_rule='unmodified harmful-minus-lower welfare-minus-value interaction',
        folds=results,positive_pairs=sum(r.get('positive',False) for r in results),items=len(states),
        undefined_folds=sum(r['status']!='computed' for r in results),
        pooled_auroc=None,pooled_auroc_note='Each omitted pair uses a different direction; do not pool cross-fold score levels as one frozen probe.',
        interpretation='Development cross-validation only; seven reused items do not create a fresh independent holdout.')


def summarize_baselines(rows):
    grouped=defaultdict(list)
    for row in rows:grouped[(row['condition'],row['position'])].append(row)
    report={}
    for (condition,position),group in sorted(grouped.items()):
        itemrows=defaultdict(dict)
        for row in group:
            if row['label'] in itemrows[row['item_id']]:raise ValueError('Duplicate item/label in analysis group')
            itemrows[row['item_id']][row['label']]=row
        if any(set(g)!={0,1} for g in itemrows.values()):raise ValueError('Incomplete pair in analysis group')
        entry={'observations':len(group),'items':len(itemrows),'probes':{}}
        for key in ['saved_e2_l26','content_lr_l26','e1_l1']:
            shifts={item:g[1][key]-g[0][key] for item,g in itemrows.items()}
            entry['probes'][key]=dict(auroc=exact_auc([r['label'] for r in group],[r[key] for r in group]),
                positive_pairs=sum(v>0 for v in shifts.values()),ties=sum(v==0 for v in shifts.values()),
                mean_pair_shift=float(np.mean(list(shifts.values()))),pair_shifts=shifts)
        report[f'{condition}|{position}']=entry
    return report


def analyze(root,weights_path):
    root=Path(root);weights_path=Path(weights_path)
    jobpath=root/'core_jobs.json'
    if not jobpath.is_file():raise ValidationBlocked('core_jobs.json absent; no analysis performed')
    payload=json.loads(jobpath.read_text(encoding='utf-8'))
    jobs=payload['jobs'] if isinstance(payload,dict) else payload
    if len(jobs)!=42 or len({j['job_id'] for j in jobs})!=42:raise ValidationBlocked('Expected 42 distinct core jobs')
    statuspath=root/'run_status.json'
    if not statuspath.is_file():raise ValidationBlocked('No completed producer status; extraction has not been verified')
    status=json.loads(statuspath.read_text())
    if status.get('state')!='complete' or status.get('completed')!=42:raise ValidationBlocked('Core extraction incomplete')
    versions=status.get('backend_versions')
    if not isinstance(versions,dict) or versions.get('model_dtype')!='bfloat16' or versions.get('attention')!='sdpa':raise ValidationBlocked('Producer environment missing or unexpected')
    for key in ('torch','transformers','numpy'):
        if not versions.get(key):raise ValidationBlocked('Incomplete backend version manifest')
    expected_weights='bcd29390210350dd707a37db85b83ce21ab5db2fa55f74ec9fa0b5ab64679749'
    weights_hash=hashlib.sha256(weights_path.read_bytes()).hexdigest()
    if weights_hash!=expected_weights:raise ValidationBlocked('Baseline weights differ from frozen original probes')
    with np.load(weights_path,allow_pickle=False) as p:
        if int(p['e2_layer'])!=26 or int(p['content_lr_layer'])!=26 or int(p['e1_layer'])!=1:raise ValidationBlocked('Unexpected saved baseline layer')
        ew=p['e2_w_mm'].copy();em=p['e2_mid_mm'].copy()
        cw=p['content_w_lr'].copy();cb=float(p['content_b_lr'])
        e1w=p['e1_w_mm'].copy();e1m=p['e1_mid_mm'].copy()
    rows=[];states=defaultdict(dict);cache_evidence=[];reading={}
    for job in jobs:
        item=job['item_id'];label=job['label'];condition=job['condition']
        if label not in (0,1) or condition not in ('silent','welfare','value'):raise ValidationBlocked('Unknown core condition/label')
        ids=job['input_ids'];positions=[job['positions']['assistant_start'],job['positions']['tool_close']]
        expected=make_cache_identity(model_id='Qwen/Qwen3.5-9B',model_revision='c202236235762e1c871ad0ccb60c8ee5ba337b9a',
            template_sha256='a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715',
            prompt_text=job['text'],input_ids=ids,positions=positions,layers_one_based=list(range(1,33)),dtype='float16',backend='transformers',backend_versions=versions)
        path=root/'activations'/(job['job_id']+'.npz');manifest_path=path.with_suffix('.json')
        if not path.is_file() or not manifest_path.is_file():raise ValidationBlocked('Missing activation/manifest for '+job['job_id'])
        manifest=json.loads(manifest_path.read_text())
        verified=verify_cache(path,manifest,expected)
        if manifest.get('job_id')!=job['job_id']:raise ValidationBlocked('Manifest job identity mismatch')
        check=manifest.get('input_check',{})
        if check.get('exact_input_verified') is not True or check.get('token_ids_match') is not True or check.get('expected_ids_sha256')!=ids_sha256(ids):raise ValidationBlocked('Producer actual input-ID comparison missing/mismatched')
        with np.load(path,allow_pickle=False) as a:
            if not np.array_equal(a['input_ids'],ids) or not np.array_equal(a['indices'],positions):raise ValidationBlocked('Payload IDs or positions differ')
            hs=a['hidden_states']
            if hs.shape!=(2,32,4096) or hs.dtype!=np.float16 or not np.isfinite(hs).all():raise ValidationBlocked('Invalid activation shape/dtype/values')
            primary=hs[0,25].astype(np.float64)
            if (label,condition) in states[item]:raise ValidationBlocked('Duplicate item condition')
            states[item][(label,condition)]=primary
            prefix=ids[:positions[1]+1]
            key=(item,label)
            if key in reading:
                if reading[key]['ids']!=prefix:raise ValidationBlocked('Question conditions changed the supposed shared reading prefix')
                reading[key]['max_absolute_hidden_difference']=max(reading[key]['max_absolute_hidden_difference'],float(np.max(np.abs(hs[1].astype(np.float32)-reading[key]['hidden']))))
            else:reading[key]={'ids':prefix,'hidden':hs[1].astype(np.float32).copy(),'max_absolute_hidden_difference':0.}
            for n,position in enumerate(('assistant_start','tool_close')):
                h26=hs[n,25].astype(np.float32);h1=hs[n,0].astype(np.float32)
                rows.append(dict(job_id=job['job_id'],item_id=item,label=label,condition=condition,position=position,
                    token_index=positions[n],saved_e2_l26=float(np.dot(h26-em,ew)),content_lr_l26=float(np.dot(h26,cw)+cb),e1_l1=float(np.dot(h1-e1m,e1w))))
        cache_evidence.append(dict(job_id=job['job_id'],**verified))
    if len(states)!=7:raise ValidationBlocked('Expected seven independent items')
    loo=loo_e2_interactions(states)
    direction_rows={r['held_out_item']:np.asarray(r.pop('direction'),dtype=np.float64) for r in loo['folds'] if 'direction' in r}
    # Freeze each fold's fitted direction alongside result; never substitute for saved E2.
    np.savez_compressed(root/'development_loo_directions.npz',**direction_rows)
    report=dict(status='development_analysis_only',model_forwards_by_analyzer=0,
        core_jobs_sha256=hashlib.sha256(jobpath.read_bytes()).hexdigest(),baseline_weights_sha256=weights_hash,
        expected_jobs=42,verified_cache_count=len(cache_evidence),cache_evidence=cache_evidence,
        scored_positions=len(rows),baseline_summary=summarize_baselines(rows),leave_one_item_out=loo,
        shared_reading_prefixes_verified=True,shared_reading_max_activation_difference=max(v['max_absolute_hidden_difference'] for v in reading.values()),
        duplicate_reading_policy='tool_close summaries are stratified by future condition; do not pool these duplicates as independent examples.',
        rows=rows,rq3_ready=False,measurement_validated=False,
        limitations=['These seven revised examples are development items. No fresh heldout validation claim.',
        'Saved probes retain their original training-context limitations. L26 content comparison matches measurement layer, not all training conditions.',
        'E1 L1 is a supplied-polarity baseline, not a same-layer control.',
        'No final-answer generation or price/rating/position extension is included in these 42 forwards.',
        'Larger or better scores do not by themselves establish welfare evaluation distinct from content.',
        'LOO uses six items per fold and does not provide a single independently validated steering vector.'])
    (root/'pilot_analysis.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:report[k] for k in ('status','verified_cache_count','scored_positions','shared_reading_max_activation_difference','rq3_ready')},indent=2))
    print('LOO positive pairs:',loo['positive_pairs'],'/',loo['items'],'; undefined folds:',loo['undefined_folds'])
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    default_root=Path(__file__).resolve().parents[2]/'Sentient-Futures-Project-git/results/rq2/e2_pilot_v3'
    parser.add_argument('--root',type=Path,default=default_root)
    parser.add_argument('--weights',type=Path,default=default_root.parent/'probe_directions.npz')
    args=parser.parse_args()
    try:analyze(args.root,args.weights)
    except (ValidationBlocked,FileNotFoundError) as exc:
        parser.exit(2,f'Analysis not run: {exc}\n')


if __name__=='__main__':main()
