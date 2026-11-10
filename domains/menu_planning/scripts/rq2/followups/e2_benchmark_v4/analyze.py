"""Offline, fixed-probe analysis of the prospective benchmark-boundary screen.

No inference, fitting, sign/layer search, or approval of scientific validity.
"""
from pathlib import Path
from collections import defaultdict
import argparse, hashlib, json, math
import numpy as np
from validation_helpers import make_cache_identity, verify_cache, ids_sha256, ValidationBlocked

WEIGHTS_SHA='bcd29390210350dd707a37db85b83ce21ab5db2fa55f74ec9fa0b5ab64679749'
REVISION='c202236235762e1c871ad0ccb60c8ee5ba337b9a'
TEMPLATE='a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
PROBES=('saved_e2_l26','content_lr_l26','e1_l1')
CONDITIONS=('base','price','rating','order')

def auc(labels,scores):
    high=np.asarray([s for y,s in zip(labels,scores) if y==1],dtype=float)
    low=np.asarray([s for y,s in zip(labels,scores) if y==0],dtype=float)
    if not len(high) or not len(low):raise ValueError('Both labels required')
    return float(np.mean((high[:,None]>low)+.5*(high[:,None]==low)))

def sign_p(positive,negative):
    n=positive+negative
    return sum(math.comb(n,k) for k in range(positive,n+1))/(2**n) if n else None

def pair_summary(pairs):
    shifts={item:float(values[1]-values[0]) for item,values in sorted(pairs.items())}
    positive=sum(v>0 for v in shifts.values());negative=sum(v<0 for v in shifts.values())
    values=[(label,pairs[item][label]) for item in sorted(pairs) for label in (0,1)]
    return dict(items=len(pairs),positive_pairs=positive,negative_pairs=negative,
        ties=len(pairs)-positive-negative,mean_pair_shift=float(np.mean(list(shifts.values()))),
        median_pair_shift=float(np.median(list(shifts.values()))),pair_shifts=shifts,
        paired_sign_p_one_sided=sign_p(positive,negative),
        auroc=auc([x[0] for x in values],[x[1] for x in values]))

def summarize(rows):
    """Score fresh and bridge cohorts separately; do not pool controls as samples."""
    grouped=defaultdict(dict)
    for row in rows:
        if row['cohort'] not in ('fresh','legacy_bridge'):raise ValueError('Unknown cohort')
        if row['condition'] not in CONDITIONS or row['label'] not in (0,1):raise ValueError('Unknown condition/label')
        if row['position'] not in ('pos_b','pos_a'):raise ValueError('Unknown position')
        for probe in PROBES:
            if not np.isfinite(row[probe]):raise ValueError('Nonfinite score')
            key=(row['cohort'],row['position'],probe,row['condition'])
            itemkey=(row['item_id'],row['label'])
            if itemkey in grouped[key]:raise ValueError('Duplicate observation')
            grouped[key][itemkey]=float(row[probe])
    report={};control_report={}
    for cohort,n,conditions in [('fresh',8,CONDITIONS),('legacy_bridge',7,('base',))]:
        for position in ('pos_b','pos_a'):
            for probe in PROBES:
                groups={}
                for condition in conditions:
                    values=grouped[(cohort,position,probe,condition)]
                    items=sorted({i for i,l in values})
                    if len(items)!=n or set(values)!={(i,l) for i in items for l in (0,1)}:
                        raise ValueError('Incomplete cohort/condition: '+str((cohort,position,probe,condition)))
                    groups[condition]=values
                    pairs={i:{l:values[i,l] for l in (0,1)} for i in items}
                    report['|'.join((cohort,position,condition,probe))]=pair_summary(pairs)
                if cohort!='fresh':continue
                base=groups['base'];baseline_shifts={i:base[i,1]-base[i,0] for i in items}
                controls={}
                for condition in CONDITIONS[1:]:
                    values=groups[condition]
                    if set(values)!=set(base):raise ValueError('Different item identities across controls')
                    variant_shifts={f'{i}|{l}':values[i,l]-base[i,l] for i,l in sorted(base)}
                    common={i:((values[i,1]-base[i,1])+(values[i,0]-base[i,0]))/2 for i in items}
                    interaction={i:(values[i,1]-values[i,0])-baseline_shifts[i] for i in items}
                    magnitude=float(np.mean(np.abs(list(variant_shifts.values()))))
                    mean_welfare=float(np.mean(list(baseline_shifts.values())))
                    controls[condition]=dict(variant_score_shifts=variant_shifts,
                        common_nuisance_shift_by_item=common,interaction_by_item=interaction,
                        mean_absolute_variant_shift=magnitude,
                        mean_absolute_interaction=float(np.mean(np.abs(list(interaction.values())))),
                        baseline_mean_welfare_shift=mean_welfare,
                        positive_welfare_mean_exceeds_nuisance_magnitude=bool(mean_welfare>0 and mean_welfare>magnitude))
                control_report['|'.join((position,probe))]=controls
    primary=report['fresh|pos_b|base|saved_e2_l26']
    robustness={c:report[f'fresh|pos_b|{c}|saved_e2_l26']['positive_pairs']>=7 for c in CONDITIONS[1:]}
    dominance={c:control_report['pos_b|saved_e2_l26'][c]['positive_welfare_mean_exceeds_nuisance_magnitude'] for c in CONDITIONS[1:]}
    screen=dict(primary_minimum_positive_pairs=7,primary_total_pairs=8,
        primary_pair_screen_pass=primary['positive_pairs']>=7,
        control_pair_screen_pass=robustness,nuisance_dominance_flags=dominance,
        all_prespecified_development_flags_pass=bool(primary['positive_pairs']>=7 and all(robustness.values()) and all(dominance.values())),
        status='prospective_development_screen_only',rq3_ready=False,measurement_validated=False,
        note='Thresholds are prospective diagnostic flags, not proof of welfare evaluation; labels are agent-reviewed and fresh samples are small. Secondary position never rescues primary failure.')
    novelty_sensitivity={}
    for position in ('pos_b','pos_a'):
        for probe in PROBES:
            for condition in CONDITIONS:
                values=grouped[('fresh',position,probe,condition)]
                items=sorted({i for i,l in values if i!='fresh_v4_07'})
                if len(items)==7:
                    novelty_sensitivity['|'.join((position,condition,probe))]=pair_summary({i:{l:values[i,l] for l in (0,1)} for i in items})
    return dict(pair_summaries=report,matched_control_contrasts=control_report,development_screen=screen,
        predeclared_novelty_sensitivity=dict(excluded_item='fresh_v4_07',reason='Reindeer is related to earlier deer/venison meat examples; exclude before seeing scores, no replacement or threshold tuning.',summaries=novelty_sensitivity))

def analyze(root,weights_path):
    root=Path(root);weights_path=Path(weights_path)
    jobpath=root/'jobs.json';payload=json.loads(jobpath.read_text(encoding='utf-8'))
    jobs=payload['jobs'] if isinstance(payload,dict) else payload
    if len(jobs)!=78 or len({j['job_id'] for j in jobs})!=78:raise ValidationBlocked('Expected exactly78 distinct jobs')
    status=json.loads((root/'run_status.json').read_text())
    if status.get('state')!='complete' or status.get('completed')!=78:raise ValidationBlocked('Run incomplete')
    versions=status.get('backend_versions',{})
    if versions.get('model_dtype')!='bfloat16' or versions.get('attention')!='sdpa':raise ValidationBlocked('Unexpected backend')
    if any(not versions.get(x) for x in ('torch','transformers','numpy')):raise ValidationBlocked('Missing environment versions')
    if hashlib.sha256(weights_path.read_bytes()).hexdigest()!=WEIGHTS_SHA:raise ValidationBlocked('Original weights changed')
    with np.load(weights_path,allow_pickle=False) as p:
        if (int(p['e2_layer']),int(p['content_lr_layer']),int(p['e1_layer']))!=(26,26,1):raise ValidationBlocked('Saved probe layers changed')
        ew=p['e2_w_mm'].copy();em=p['e2_mid_mm'].copy();cw=p['content_w_lr'].copy();cb=float(p['content_b_lr']);e1w=p['e1_w_mm'].copy();e1m=p['e1_mid_mm'].copy()
    rows=[];evidence=[]
    for j in jobs:
        ids=j['input_ids'];positions=[j['positions']['pos_b'],j['positions']['pos_a']]
        if positions[0]!=len(ids)-1 or positions[1]>=positions[0]:raise ValidationBlocked('Incorrect benchmark position ordering')
        if not j['text'].endswith('<|im_start|>assistant\n<think>\n'):raise ValidationBlocked('Unexpected assistant boundary')
        if j.get('request',{}).get('messages',[{}])[-1].get('role')!='tool':raise ValidationBlocked('Final message must be tool result without a nudge/question')
        identity=make_cache_identity(model_id='Qwen/Qwen3.5-9B',model_revision=REVISION,template_sha256=TEMPLATE,prompt_text=j['text'],input_ids=ids,positions=positions,layers_one_based=list(range(1,33)),dtype='float16',backend='transformers',backend_versions=versions)
        path=root/'activations'/(j['job_id']+'.npz');manifest=json.loads(path.with_suffix('.json').read_text())
        verified=verify_cache(path,manifest,identity);check=manifest.get('input_check',{})
        if manifest.get('job_id')!=j['job_id'] or check.get('exact_input_verified') is not True or check.get('token_ids_match') is not True or check.get('expected_ids_sha256')!=ids_sha256(ids):raise ValidationBlocked('Missing actual input/identity evidence')
        with np.load(path,allow_pickle=False) as a:
            h=a['hidden_states']
            if not np.array_equal(a['input_ids'],ids) or not np.array_equal(a['indices'],positions):raise ValidationBlocked('Payload IDs/positions differ')
            if h.shape!=(2,32,4096) or h.dtype!=np.float16 or not np.isfinite(h).all():raise ValidationBlocked('Invalid activation array')
            for n,position in enumerate(('pos_b','pos_a')):
                h26=h[n,25].astype(np.float64);h1=h[n,0].astype(np.float64)
                rows.append(dict(job_id=j['job_id'],item_id=j['item_id'],label=j['label'],condition=j['condition'],cohort=j['cohort'],position=position,token_index=positions[n],saved_e2_l26=float(np.dot(h26-em,ew)),content_lr_l26=float(np.dot(h26,cw)+cb),e1_l1=float(np.dot(h1-e1m,e1w))))
        evidence.append(dict(job_id=j['job_id'],**verified))
    summary=summarize(rows)
    report=dict(status='completed_prospective_development_screen',core_jobs_sha256=hashlib.sha256(jobpath.read_bytes()).hexdigest(),baseline_weights_sha256=WEIGHTS_SHA,verified_cache_count=len(evidence),scored_positions=len(rows),cache_evidence=evidence,rows=rows,**summary,
        rq3_ready=False,measurement_validated=False,
        limitations=['Fresh wording/family audit and independent agent review are not independent human label validation.',
        'Small synthetic option contrasts are not naturally occurring benchmark trajectories or proof of a welfare-specific construct.',
        'Target pos_a is option-specific reading; pos_b follows the whole tool-result batch.',
        'Original content LR is a comparator, not an orthogonal construct ground truth. Raw scores are not directly comparable between different probes.',
        'No model generation, causal intervention, layer search, sign reversal, or new probe fitting occurred.',
        'Bridge pairs were previously inspected and are never pooled with fresh tests; controls are repeated measurements, not extra independent items.'])
    (root/'benchmark_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(verified_cache_count=len(evidence),development_screen=summary['development_screen']),indent=2))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--weights',type=Path,required=True)
    args=parser.parse_args();analyze(args.root,args.weights)
