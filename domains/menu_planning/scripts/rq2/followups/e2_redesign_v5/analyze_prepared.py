"""Fail-closed future v5 fit and cached neutral-development analysis; no inference."""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,itertools,json,math
import numpy as np
from fit_direction import fit_direction
from validation_helpers import make_cache_identity,verify_cache,ids_sha256,ValidationBlocked

REVISION='c202236235762e1c871ad0ccb60c8ee5ba337b9a'
TEMPLATE='a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
WEIGHTS_SHA='bcd29390210350dd707a37db85b83ce21ab5db2fa55f74ec9fa0b5ab64679749'
CONDITIONS=('base','price','rating','order')
PROBES=('candidate_v5_l26','original_e2_l26','content_lr_l26','e1_l1')

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(condition,message):
    if not condition:raise ValidationBlocked(message)
def cosine(a,b):
    denom=np.linalg.norm(a)*np.linalg.norm(b)
    return float(np.dot(a,b)/denom) if denom>1e-12 else None

def summarize(rows):
    groups=defaultdict(dict)
    for r in rows:
        require(r['condition'] in CONDITIONS and r['position'] in ('pos_b','pos_a') and r['label'] in (0,1),'Unexpected development factor')
        for probe in PROBES:
            key=(r['position'],r['condition'],probe);item=(r['item_id'],r['label'])
            require(item not in groups[key] and np.isfinite(r[probe]),'Duplicate or nonfinite development score')
            groups[key][item]=float(r[probe])
    summaries={};controls={}
    for pos in ('pos_b','pos_a'):
        for probe in PROBES:
            for condition in CONDITIONS:
                values=groups[pos,condition,probe];items=sorted({i for i,l in values})
                require(len(items)==8 and set(values)=={(i,l) for i in items for l in (0,1)},'Incomplete development group')
                shifts={i:values[i,1]-values[i,0] for i in items}
                hi=np.array([values[i,1] for i in items]);lo=np.array([values[i,0] for i in items])
                summaries[f'{pos}|{condition}|{probe}']=dict(items=8,positive_pairs=sum(x>0 for x in shifts.values()),negative_pairs=sum(x<0 for x in shifts.values()),ties=sum(x==0 for x in shifts.values()),mean_pair_shift=float(np.mean(list(shifts.values()))),pair_shifts=shifts,auroc=float(np.mean((hi[:,None]>lo)+.5*(hi[:,None]==lo))))
            base=groups[pos,'base',probe];control={}
            for condition in CONDITIONS[1:]:
                values=groups[pos,condition,probe]
                require(set(values)==set(base),'Different items across nuisance conditions')
                changes={f'{i}|{l}':values[i,l]-base[i,l] for i,l in sorted(base)}
                interaction={i:(values[i,1]-values[i,0])-(base[i,1]-base[i,0]) for i in items}
                mean=summaries[f'{pos}|base|{probe}']['mean_pair_shift'];magnitude=float(np.mean(np.abs(list(changes.values()))))
                control[condition]=dict(variant_score_shifts=changes,interaction_by_item=interaction,mean_absolute_variant_shift=magnitude,mean_absolute_interaction=float(np.mean(np.abs(list(interaction.values())))),baseline_mean_welfare_shift=mean,positive_welfare_mean_exceeds_nuisance=bool(mean>0 and mean>magnitude))
            controls[f'{pos}|{probe}']=control
    primary=summaries['pos_b|base|candidate_v5_l26']
    flags=dict(primary_at_least_7_of_8=primary['positive_pairs']>=7,control_at_least_7_of_8={c:summaries[f'pos_b|{c}|candidate_v5_l26']['positive_pairs']>=7 for c in CONDITIONS[1:]},nuisance_dominance={c:controls['pos_b|candidate_v5_l26'][c]['positive_welfare_mean_exceeds_nuisance'] for c in CONDITIONS[1:]},rq3_ready=False,measurement_validated=False,status='development_diagnostics_only')
    sensitivity={}
    for key,summary in summaries.items():
        shifts={i:v for i,v in summary['pair_shifts'].items() if i!='fresh_v4_07'}
        if len(shifts)==7:
            pos,condition,probe=key.split('|');values=groups[pos,condition,probe];items=sorted(shifts)
            hi=np.array([values[i,1] for i in items]);lo=np.array([values[i,0] for i in items])
            sensitivity[key]=dict(items=7,positive_pairs=sum(v>0 for v in shifts.values()),mean_pair_shift=float(np.mean(list(shifts.values()))),pair_shifts=shifts,auroc=float(np.mean((hi[:,None]>lo)+.5*(hi[:,None]==lo))))
    return dict(pair_summaries=summaries,matched_controls=controls,development_flags=flags,
        predeclared_novelty_sensitivity=dict(excluded_item='fresh_v4_07',reason='Related deer/venison family overlap; descriptive sensitivity only, never a replacement primary.',summaries=sensitivity))

def sign_flip_diagnostic(states,neutral_pair_differences,direction):
    """Enumerate six-item label flips; descriptive reference, never selection."""
    items=sorted({k[0] for k in states});require(len(items)==6,'Expected six fit items')
    contributions=[]
    for i in items:
        contributions.append(np.mean([(states[i,'welfare',o,1]-states[i,'welfare',o,0])-(states[i,'commercial',o,1]-states[i,'commercial',o,0]) for o in ('target_first','target_last')],axis=0))
    diffs=np.asarray(neutral_pair_differences,dtype=float);observed=float(np.mean(diffs@direction));values=[];undefined=0
    for signs in itertools.product((-1,1),repeat=6):
        raw=np.mean(np.asarray(contributions)*np.asarray(signs)[:,None],axis=0);norm=np.linalg.norm(raw)
        if norm<=1e-12:undefined+=1;continue
        values.append(float(np.mean(diffs@(raw/norm))))
    return dict(label_flip_patterns=64,defined_patterns=len(values),undefined_patterns=undefined,observed_mean_pair_shift=observed,reference_mean_pair_shifts=values,reference_count_at_least_observed=sum(v>=observed-1e-12 for v in values),selection_performed=False,interpretation='Descriptive training-item sign-flip reference on already inspected development items; not a confirmatory p-value or alternative fitted probe.')

def analyze(root_v5,source_v4,weights_path,include_sign_flip_diagnostic=True):
    root=Path(root_v5);source=Path(source_v4);weights_path=Path(weights_path)
    require((root/'run_status.json').is_file(),'No completed v5 training run; analysis has not started')
    status=read(root/'run_status.json')
    require(status.get('state')=='complete' and status.get('completed')==48 and status.get('total')==48,'Expected completed48 training extraction')
    execution=read(root/'execution_manifest.json');jobs=read(root/'jobs.json')
    jobs_sha=sha(root/'jobs.json')
    require(jobs_sha==execution['jobs_sha256']==status['jobs_sha256'],'V5 jobs/producer/freeze hashes differ')
    require(len(jobs)==112 and len({j['job_id'] for j in jobs})==112,'Expected112 unique planned jobs')
    train=[j for j in jobs if j['split']=='train'];dev=[j for j in jobs if j['split']=='development']
    require(len(train)==48 and len(dev)==64,'Wrong training/development counts')
    require(not {j['item_id'] for j in train}&{j['item_id'] for j in dev},'Training/development item overlap')
    versions=status.get('backend_versions',{})
    require(versions.get('model_dtype')=='bfloat16' and versions.get('attention')=='sdpa' and all(versions.get(k) for k in ('torch','transformers','numpy')),'Incomplete backend identity')
    oldstatus=read(source/'run_status.json')
    require(oldstatus.get('state')=='complete' and oldstatus.get('completed')==78,'V4 cache producer incomplete')
    require(versions==oldstatus.get('backend_versions'),'Training/development backend versions differ')
    states={};evidence=[]
    for j in train:
        positions=[j['positions']['pos_b'],j['positions']['pos_a']];ids=j['input_ids']
        require(positions[0]==len(ids)-1 and positions[1]<positions[0] and j['request']['messages'][-1]['role']=='tool','Invalid training benchmark boundary')
        identity=make_cache_identity(model_id='Qwen/Qwen3.5-9B',model_revision=REVISION,template_sha256=TEMPLATE,prompt_text=j['text'],input_ids=ids,positions=positions,layers_one_based=list(range(1,33)),dtype='float16',backend='transformers',backend_versions=versions)
        path=root/'activations'/(j['job_id']+'.npz');manifest=read(path.with_suffix('.json'));verified=verify_cache(path,manifest,identity);check=manifest.get('input_check',{})
        require(manifest.get('job_id')==j['job_id'] and check.get('exact_input_verified') is True and check.get('token_ids_match') is True and check.get('expected_ids_sha256')==ids_sha256(ids),'Training actual-input evidence absent')
        with np.load(path,allow_pickle=False) as z:
            h=z['hidden_states'];require(h.shape==(2,32,4096) and h.dtype==np.float16 and np.isfinite(h).all(),'Invalid training hidden states')
            require(np.array_equal(z['input_ids'],ids) and np.array_equal(z['indices'],positions),'Training payload IDs/positions mismatch')
            key=(j['item_id'],j['objective'],j['detail_order'],j['label']);require(key not in states,'Duplicate training factor')
            states[key]=h[0,25].astype(np.float64)
        evidence.append(dict(job_id=j['job_id'],**verified))
    direction,center,fit_report=fit_direction(states)
    require(sha(weights_path)==WEIGHTS_SHA,'Original comparison weights changed')
    oldjobs=read(source/'jobs.json');oldmap={j['job_id']:j for j in oldjobs};oldreport=read(source/'benchmark_validation.json');selected_manifest=read(source/'selected_layer_manifest.json')
    require(sha(source/'jobs.json')==selected_manifest['jobs_sha256']==oldreport['core_jobs_sha256'],'V4 input provenance mismatch')
    require(sha(source/'selected_layers_1_26.npz')==selected_manifest['selected_npz_sha256'],'Selected cache bytes changed')
    require(selected_manifest['layers_one_based']==[1,26] and selected_manifest['position_order']==['pos_b','pos_a'],'Selected cache semantics differ')
    records={x['job_id']:x for x in selected_manifest['records']};payloads={x['job_id']:x['payload_sha256'] for x in oldreport['cache_evidence']};oldrows={(r['job_id'],r['position']):r for r in oldreport['rows']}
    require(len(oldmap)==78 and len(records)==len(selected_manifest['records'])==78 and len(payloads)==78 and oldreport['verified_cache_count']==78,'Incomplete/duplicate source provenance inventory')
    rows=[];devstates={}
    with np.load(source/'selected_layers_1_26.npz',allow_pickle=False) as z,np.load(weights_path,allow_pickle=False) as w:
        require((int(w['e2_layer']),int(w['content_lr_layer']),int(w['e1_layer']))==(26,26,1),'Original baseline layers differ')
        for j in dev:
            old=oldmap[j['job_id']]
            require(old['cohort']=='fresh','Unexpected cached development cohort')
            for key in ('request','text','input_ids','positions','item_id','label','condition'):require(j[key]==old[key],'Development cache input changed: '+key)
            h=z[j['job_id']];record=records[j['job_id']]
            require(h.shape==(2,2,4096) and h.dtype==np.float16 and np.isfinite(h).all(),'Invalid selected development states')
            require(hashlib.sha256(h.tobytes()).hexdigest()==record['selected_array_sha256'] and record['original_npz_sha256']==payloads[j['job_id']],'Selected array provenance mismatch')
            devstates[j['item_id'],j['condition'],j['label']]=h[0,1].astype(float)
            for n,pos in enumerate(('pos_b','pos_a')):
                h1=h[n,0].astype(float);h26=h[n,1].astype(float)
                baseline=dict(original_e2_l26=float(np.dot(h26-w['e2_mid_mm'],w['e2_w_mm'])),content_lr_l26=float(np.dot(h26,w['content_w_lr'])+float(w['content_b_lr'])),e1_l1=float(np.dot(h1-w['e1_mid_mm'],w['e1_w_mm'])))
                for key,value in baseline.items():require(abs(value-oldrows[j['job_id'],pos]['saved_e2_l26' if key=='original_e2_l26' else key])<1e-8,'Cached baseline reproduction failed')
                rows.append(dict(job_id=j['job_id'],item_id=j['item_id'],label=j['label'],condition=j['condition'],position=pos,candidate_v5_l26=float(np.dot(h26-center,direction)),**baseline))
        fit_report['original_e2_direction_cosine']=cosine(direction,w['e2_w_mm'])
        fit_report['original_content_lr_direction_cosine']=cosine(direction,w['content_w_lr'])
    development_items=sorted({j['item_id'] for j in dev})
    fit_report['neutral_development_nuisance_mean_shift_cosines']={}
    for condition in CONDITIONS[1:]:
        shift=np.mean([devstates[i,condition,label]-devstates[i,'base',label] for i in development_items for label in (0,1)],axis=0)
        fit_report['neutral_development_nuisance_mean_shift_cosines'][condition]=dict(cosine=cosine(direction,shift),mean_shift_norm=float(np.linalg.norm(shift)),used_for_fitting=False,orthogonalization_performed=False)
    diagnostics=None
    if include_sign_flip_diagnostic:
        differences=[devstates[i,'base',1]-devstates[i,'base',0] for i in sorted({j['item_id'] for j in dev})]
        diagnostics=sign_flip_diagnostic(states,differences,direction)
    result=dict(status='completed_development_analysis_only',jobs_sha256=jobs_sha,verified_training_caches=48,reused_development_caches=64,model_runs_by_analyzer=0,fit=fit_report,training_cache_evidence=evidence,rows=rows,sign_flip_diagnostic=diagnostics,**summarize(rows),rq3_ready=False,measurement_validated=False,limitations=['Six training items and eight previously inspected development items; no independent fresh holdout.','This learns an instruction-modulated candidate feature; no inference of spontaneous evaluation follows automatically.','Price/rating controls are target-first only; order control is baseline-price/rating only, not a complete nuisance factorial.','No model generation or intervention; final-answer and causal claims remain untested.'])
    dest=root/'candidate_v5_direction.npz'
    if dest.exists():
        with np.load(dest,allow_pickle=False) as existing:require(np.array_equal(existing['direction'],direction) and np.array_equal(existing['center'],center),'Refusing to replace different v5 candidate weights')
    else:np.savez_compressed(dest,direction=direction,center=center,layer_one_based=np.array(26),jobs_sha256=np.array(jobs_sha))
    (root/'development_analysis.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--source-v4',type=Path,required=True);p.add_argument('--weights',type=Path,required=True)
    a=p.parse_args()
    try:report=analyze(a.root,a.source_v4,a.weights)
    except (ValidationBlocked,FileNotFoundError) as exc:p.exit(2,f'Analysis not run: {exc}\n')
    print(json.dumps(report['development_flags'],indent=2))
