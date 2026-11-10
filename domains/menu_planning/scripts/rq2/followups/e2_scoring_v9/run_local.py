"""Three explicit local phases: freeze, fit, compare. No model/network imports."""
import argparse
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import sys

# Bound CPU use before NumPy loads; do not create many BLAS worker threads.
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
sys.dont_write_bytecode=True
import numpy as np
import score_fit as scorer

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[1]
BASE=WORKSPACE/'Sentient-Futures-Project-git/results/rq2'
OUT=BASE/'e2_scoring_v9'
DESIGN=HERE.parent/'e2_training_design_v8'
V8=BASE/'e2_training_design_v8'
sys.path.insert(0,str(DESIGN))
import analyze_v8 as existing


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):
    text=json.dumps(value,indent=2,allow_nan=False)+'\n'
    if path.exists():
        if path.read_text(encoding='utf-8')!=text:raise FileExistsError('Refusing changed output: '+str(path))
    else:path.write_text(text,encoding='utf-8')


def freeze():
    if (OUT/'fit_complete.json').exists():raise RuntimeError('Already fitted; freeze cannot be rewritten')
    protocol=read(HERE/'protocol.json')
    assert protocol['ridge_fraction']==scorer.RIDGE_FRACTION==.01
    assert protocol['hyperparameter_search'] is False and protocol['new_model_passes']==0
    old=read(V8/'development_analysis_v8.json')
    paths={Path(p) for p in old['source_sha256']}
    paths.update(V8/name for name in ['training_jobs_draft.json','run_status.json','execution_manifest.json',
        'forward_ledger.json','review_release_v8.json','training_pos_b_l26.npz','training_pos_b_l26.json',
        'candidate_v8_direction.npz','development_analysis_v8.json','independent_producer_evidence_review.json'])
    paths.update(DESIGN/name for name in ['training_jobs_draft.json','training_pairs_reviewed_draft.json',
        'review_release_v8.json','analyze_v8.py','fit_direction.py'])
    assert all(sha(p)==digest for p,digest in old['source_sha256'].items())
    source={str(p.resolve()):sha(p) for p in sorted(paths)}
    code={name:sha(HERE/name) for name in ['protocol.json','score_fit.py','test_score_fit.py','run_local.py']}
    OUT.mkdir(parents=True,exist_ok=True)
    write_json(OUT/'analysis_freeze.json',{
        'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'protocol':protocol,
        'code_sha256':code,'source_sha256':source,'new_model_passes':0,
        'result_examined_before_freeze':False,
        'disclosure':'Prior v4-v8 development results were already known. This is a new exploratory scoring test, not a preregistered original hypothesis.'})
    print('FROZEN: one scorer; 192 saved training states; 64 cached development states; no new model passes.')


def check_freeze():
    lock=read(OUT/'analysis_freeze.json')
    for name,digest in lock['code_sha256'].items():
        if sha(HERE/name)!=digest:raise ValueError('Frozen code changed: '+name)
    for path,digest in lock['source_sha256'].items():
        if sha(path)!=digest:raise ValueError('Source changed: '+path)
    return lock


def verify_svd(records,raw):
    _,_,target,nuisance=scorer.matrices(records,6)
    design,labels,scale=scorer.system(target,nuisance)
    u,values,vt=np.linalg.svd(design,full_matrices=False)
    reference=vt.T@((values/(values**2+scorer.RIDGE_FRACTION))*(u.T@labels))/scale
    error=float(np.max(np.abs(reference-raw)))
    if not np.allclose(reference,raw,rtol=1e-8,atol=1e-11):
        raise ValueError('Independent SVD solution differs')
    return {'method':'Independent singular-value solution versus dual ridge solve',
            'maximum_raw_weight_absolute_error':error,'passed':True}


def fit():
    lock=check_freeze()
    if (OUT/'candidate_v9_direction.npz').exists() or (OUT/'fit_complete.json').exists():
        raise RuntimeError('Candidate already exists; refusing a new fit')
    records,versions,evidence=existing.load_training(V8,DESIGN)
    print('Verified 192 cached training states. Starting six excluded-item checks.',flush=True)
    cv=scorer.leave_one_item_out(records)
    direction,center,raw,info=scorer.fit(records,6)
    info['independent_solver_check']=verify_svd(records,raw)
    baseline,baseline_center=scorer.mean_baseline(records)
    with np.load(V8/'candidate_v8_direction.npz',allow_pickle=False) as old:
        if not np.allclose(baseline,old['direction'],rtol=1e-11,atol=1e-12):
            raise ValueError('Saved v8 baseline not reproduced')
        if not np.allclose(baseline_center,old['center'],atol=1e-10,rtol=1e-12):
            raise ValueError('Saved v8 center not reproduced')
    candidate=OUT/'candidate_v9_direction.npz'
    np.savez_compressed(candidate,direction=direction,center=center,raw_weights=raw,
        layer_one_based=np.array(26),position=np.array('pos_b'),
        jobs_sha256=np.array(existing.JOBS_SHA),protocol_sha256=np.array(sha(HERE/'protocol.json')))
    write_json(OUT/'excluded_item_diagnostics.json',cv)
    write_json(OUT/'training_diagnostics.json',{'v9':scorer.diagnose(records,direction),
                'v8_mean_baseline':scorer.diagnose(records,baseline),
                'interpretation':'In-sample diagnostic, not independent validation.'})
    check_freeze()
    write_json(OUT/'fit_complete.json',{'completed_at_utc':datetime.now(timezone.utc).isoformat(),
        'fit':info,'candidate_sha256':sha(candidate),'analysis_freeze_sha256':sha(OUT/'analysis_freeze.json'),
        'cv_sha256':sha(OUT/'excluded_item_diagnostics.json'),
        'training_diagnostics_sha256':sha(OUT/'training_diagnostics.json'),
        'producer_backend_versions':versions,
        'training_evidence':{k:v for k,v in evidence.items() if k!='records'},
        'cached_training_states_used':192,'development_states_used_for_fit_or_selection':0,
        'six_excluded_item_diagnostic_fits':6,'final_candidate_fits':1,
        'parameter_search':False,'new_model_passes':0,'paid_resources_started':False,
        'local_numpy_version':np.__version__})
    print('FIT SAVED: one candidate, six diagnostic folds. Development activations not yet opened in this run.',flush=True)


def ratio(summary,condition):
    gap=summary['pair_summaries']['base']['mean_pair_gap']
    return summary['nuisance_effects'][condition]['mean_absolute_variant_shift']/gap if gap>0 else None


def compare():
    lock=check_freeze()
    if (OUT/'comparison.json').exists():raise RuntimeError('Comparison already saved; no repeated scoring requested')
    commit=read(OUT/'fit_complete.json')
    if sha(OUT/'candidate_v9_direction.npz')!=commit['candidate_sha256']:
        raise ValueError('Frozen candidate changed')
    states,identifiers,probes,content,sources=existing.load_development_and_comparators(BASE,commit['producer_backend_versions'])
    old_report=read(V8/'development_analysis_v8.json')
    with np.load(V8/'candidate_v8_direction.npz',allow_pickle=False) as data:
        probes['v8']=(data['direction'].copy(),data['center'].copy())
    with np.load(OUT/'candidate_v9_direction.npz',allow_pickle=False) as data:
        probes['v9']=(data['direction'].copy(),data['center'].copy())
    summaries={};sensitivities={};rows=[]
    for name,(direction,center) in probes.items():
        scores=existing.score_states(states,direction,center)
        summaries[name]=existing.summarize_scores(scores,8)
        sensitivities[name]=existing.summarize_scores({i:s for i,s in scores.items() if i!=existing.EXCLUDED_REINDEER},7)
        if name!='v9':
            saved=old_report['candidates'][name]
            for condition in existing.CONDITIONS:
                a,b=summaries[name]['pair_summaries'][condition],saved['pair_summaries'][condition]
                if a['positive_pairs']!=b['positive_pairs'] or abs(a['auroc']-b['auroc'])>1e-12:
                    raise ValueError('Old summary not reproduced: '+name)
                if any(abs(gap-b['pair_gaps'][item])>1e-8 for item,gap in a['pair_gaps'].items()):
                    raise ValueError('Old gaps not reproduced: '+name)
        for item,cells in scores.items():
            for (condition,label),score in cells.items():
                rows.append({'candidate':name,'job_id':identifiers[item,condition,label],
                    'item_id':item,'condition':condition,'label':label,'score':score})
    new,old=summaries['v9'],summaries['v8']
    flags={
        'all_condition_pair_counts_at_least_v8':all(new['pair_summaries'][c]['positive_pairs']>=old['pair_summaries'][c]['positive_pairs'] for c in existing.CONDITIONS),
        'base_auroc_at_least_v8':new['pair_summaries']['base']['auroc']>=old['pair_summaries']['base']['auroc'],
        'positive_base_gap':new['pair_summaries']['base']['mean_pair_gap']>0,
        'price_ratio_lower':ratio(new,'price') is not None and ratio(new,'price')<ratio(old,'price'),
        'order_ratio_lower':ratio(new,'order') is not None and ratio(new,'order')<ratio(old,'order'),
        'some_discrimination_metric_improved':new['pair_summaries']['base']['auroc']>old['pair_summaries']['base']['auroc'] or any(new['pair_summaries'][c]['positive_pairs']>old['pair_summaries'][c]['positive_pairs'] for c in existing.CONDITIONS),
    }
    deltas={}
    for name,previous in summaries.items():
        if name=='v9':continue
        deltas[name]={
            'pair_counts':{c:new['pair_summaries'][c]['positive_pairs']-previous['pair_summaries'][c]['positive_pairs'] for c in existing.CONDITIONS},
            'auroc':{c:new['pair_summaries'][c]['auroc']-previous['pair_summaries'][c]['auroc'] for c in existing.CONDITIONS},
            'absolute_score_shift':{c:new['nuisance_effects'][c]['mean_absolute_variant_shift']-previous['nuisance_effects'][c]['mean_absolute_variant_shift'] for c in existing.CONDITIONS[1:]}}
    check_freeze()
    report={'status':'completed_local_scoring_test','new_model_passes':0,'network_calls':0,
        'paid_resources_started':False,'cached_training_states_used':192,'cached_development_states_used':64,
        'independent_training_items':6,'development_items':8,'fresh_validation_states_used':0,
        'fit_commit_sha256':sha(OUT/'fit_complete.json'),'protocol_sha256':sha(HERE/'protocol.json'),
        'candidate_sha256':commit['candidate_sha256'],'candidates':summaries,
        'v9_minus_comparators':deltas,'rows':rows,
        'shift_to_base_gap_ratios':{name:{c:ratio(summary,c) for c in ('price','rating','order')} for name,summary in summaries.items()},
        'prespecified_reindeer_sensitivity':sensitivities,'comparison_flags':flags,
        'clear_development_improvement':all(flags.values()),
        'direction_cosines':{name:existing.cosine(probes['v9'][0],direction) for name,(direction,center) in probes.items() if name!='v9'},
        'original_content_cosine':existing.cosine(probes['v9'][0],content),
        'source_sha256':lock['source_sha256'],'sources_unchanged':True,
        'measurement_validated':False,'confirmatory_rq3_ready':False,
        'interpretation':'This fixed scorer is evaluated on eight already-inspected development items. Improvement is descriptive, not validation of internal welfare evaluation. A later exploratory causal test is a separate decision.',
        'stopping_rule':'No further candidate, strength, layer, sign, exclusion or fresh examples in this local test.'}
    write_json(OUT/'comparison.json',report)
    lines=['RQ2 local scoring test v9','',
        'Completed locally: 192 saved training states and 64 cached development states.',
        'Zero new model passes, network calls or paid resources. Original files unchanged.',
        'One frozen regularized scorer; no parameter search. Six whole-item holdouts.',
        '','Correctly ordered pairs (out of eight):',
        'Candidate             Base   Price   Rating   Order    Base AUROC']
    for name,summary in summaries.items():
        values=[summary['pair_summaries'][c]['positive_pairs'] for c in existing.CONDITIONS]
        lines.append(f"{name:21} {values[0]:>3}     {values[1]:>3}     {values[2]:>3}     {values[3]:>3}       {summary['pair_summaries']['base']['auroc']:.4f}")
    lines.extend(['','Absolute score changes / average base welfare gap:',
                  'Candidate             Price     Rating     Order'])
    for name in ('v6','v7_corrected_v6','v8','v9'):
        ratios=report['shift_to_base_gap_ratios'][name]
        lines.append(name+': '+', '.join(f'{c}={value:.3f}' if value is not None else f'{c}=undefined (nonpositive welfare gap)' for c,value in ratios.items()))
    lines.extend(['','Clear development improvement under the frozen descriptive rule: '+str(all(flags.values())),
        'This flag is not original H2, independent validation or automatic RQ3 approval.',
        'Lower concern does not mean harmless. A factual-reading prompt does not prove absent evaluation.',
        'No directions, signs or parameters were changed after inspecting this comparison.',
        'Full metrics and paired gaps: comparison.json. Excluded-item checks: excluded_item_diagnostics.json.'])
    text='\n'.join(lines)+'\n'
    (OUT/'RESULT.txt').write_text(text,encoding='utf-8')
    print(text)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('phase',choices=['freeze','fit','compare'])
    args=parser.parse_args()
    {'freeze':freeze,'fit':fit,'compare':compare}[args.phase]()
