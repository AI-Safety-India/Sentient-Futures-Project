"""Fixed factual-attention interaction and reused development analysis; no inference."""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,itertools,json,math
import numpy as np
from validation_helpers import make_cache_identity,verify_cache,ids_sha256,ValidationBlocked

REVISION='c202236235762e1c871ad0ccb60c8ee5ba337b9a'
TEMPLATE='a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
WEIGHTS_SHA='bcd29390210350dd707a37db85b83ce21ab5db2fa55f74ec9fa0b5ab64679749'
CONDITIONS=('base','price','rating','order')
PROBES=('candidate_v6_l26','candidate_v5_l26','original_e2_l26','content_lr_l26','e1_l1')

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
                common={i:((values[i,1]-base[i,1])+(values[i,0]-base[i,0]))/2 for i in items}
                flips=sum(np.sign(values[i,1]-values[i,0])!=np.sign(base[i,1]-base[i,0]) for i in items)
                mean=summaries[f'{pos}|base|{probe}']['mean_pair_shift'];magnitude=float(np.mean(np.abs(list(changes.values()))))
                control[condition]=dict(common_offset_by_item=common,mean_absolute_common_offset=float(np.mean(np.abs(list(common.values())))),pair_sign_changes=int(flips),variant_score_shifts=changes,interaction_by_item=interaction,mean_absolute_variant_shift=magnitude,mean_absolute_interaction=float(np.mean(np.abs(list(interaction.values())))),baseline_mean_welfare_shift=mean,positive_welfare_mean_exceeds_nuisance=bool(mean>0 and mean>magnitude))
            controls[f'{pos}|{probe}']=control
    primary=summaries['pos_b|base|candidate_v6_l26']
    flags=dict(primary_at_least_7_of_8=primary['positive_pairs']>=7,control_at_least_7_of_8={c:summaries[f'pos_b|{c}|candidate_v6_l26']['positive_pairs']>=7 for c in CONDITIONS[1:]},nuisance_dominance={c:controls['pos_b|candidate_v6_l26'][c]['positive_welfare_mean_exceeds_nuisance'] for c in CONDITIONS[1:]},rq3_ready=False,measurement_validated=False,status='development_diagnostics_only')
    sensitivity={}
    for key,summary in summaries.items():
        shifts={i:v for i,v in summary['pair_shifts'].items() if i!='fresh_v4_07'}
        if len(shifts)==7:
            pos,condition,probe=key.split('|');values=groups[pos,condition,probe];items=sorted(shifts)
            hi=np.array([values[i,1] for i in items]);lo=np.array([values[i,0] for i in items])
            sensitivity[key]=dict(items=7,positive_pairs=sum(v>0 for v in shifts.values()),mean_pair_shift=float(np.mean(list(shifts.values()))),pair_shifts=shifts,auroc=float(np.mean((hi[:,None]>lo)+.5*(hi[:,None]==lo))))
    return dict(pair_summaries=summaries,matched_controls=controls,development_flags=flags,
        predeclared_novelty_sensitivity=dict(excluded_item='fresh_v4_07',reason='Related deer/venison family overlap; descriptive sensitivity only, never a replacement primary.',summaries=sensitivity))

GOALS=('welfare','facts')
ORDERS=('target_first','target_last')

def fit_direction(training_states):
    """states[(item_id, goal, order, label)] -> pos_b L26 vector.

Equal weight for each of six items and both orders. No layer selection,
regression on development labels, sign correction or nuisance orthogonalizing.
"""
    if not training_states:raise ValueError('Training states absent; no fit performed')
    items=sorted({k[0] for k in training_states})
    if len(items)!=6:raise ValueError('Expected six reviewed training items')
    required={(i,g,o,l) for i in items for g in GOALS for o in ORDERS for l in (0,1)}
    if set(training_states)!=required:raise ValueError('Incomplete, unexpected, or mixed training factors')
    shapes={np.asarray(v).shape for v in training_states.values()}
    if len(shapes)!=1 or len(next(iter(shapes)))!=1:raise ValueError('Expected equal-dimensional vectors')
    if any(not np.isfinite(v).all() for v in training_states.values()):raise ValueError('Nonfinite training states')
    states={k:np.asarray(v,dtype=np.float64) for k,v in training_states.items()}
    interaction=[];content=[];goal_main=[];by_order={o:[] for o in ORDERS}
    for i in items:
        for o in ORDERS:
            hw=states[i,'welfare',o,1];lw=states[i,'welfare',o,0]
            hc=states[i,'facts',o,1];lc=states[i,'facts',o,0]
            delta=(hw-lw)-(hc-lc)
            interaction.append(delta);by_order[o].append(delta)
            content.append(((hw-lw)+(hc-lc))/2)
            goal_main.append(((hw-hc)+(lw-lc))/2)
    raw=np.mean(interaction,axis=0);norm=float(np.linalg.norm(raw))
    if norm<=1e-12:raise ValueError('Zero interaction; do not manufacture a direction')
    direction=raw/norm
    center=np.mean(list(states.values()),axis=0)
    def cosine(a,b):
        denominator=np.linalg.norm(a)*np.linalg.norm(b)
        return float(np.dot(a,b)/denominator) if denominator>1e-12 else None
    order_means={o:np.mean(v,axis=0) for o,v in by_order.items()}
    report=dict(training_items=items,training_states=48,layer_one_based=26,position='pos_b',
        normalized_interaction_norm=1.0,raw_interaction_norm=norm,
        definition='mean_items(mean_orders((higher_welfare-lower_welfare)-(higher_facts-lower_facts)))',
        development_states_used=0,sign_rule='unmodified higher-minus-lower welfare-minus-facts',
        direction_sha256=hashlib.sha256(direction.tobytes()).hexdigest(),
        order_interaction_cosine=cosine(order_means[ORDERS[0]],order_means[ORDERS[1]]),
        content_main_effect_cosine=cosine(raw,np.mean(content,axis=0)),
        goal_main_effect_cosine=cosine(raw,np.mean(goal_main,axis=0)),
        score_center='mean of training states; no classification threshold or calibrated probability',
        rq3_ready=False,measurement_validated=False,
        interpretation='Candidate instruction-modulated welfare sensitivity; diagnostics are not construct validation.')
    return direction,center,report

FACTS='When comparing suppliers, identify animal-treatment facts.'
WELFARE='When comparing suppliers, consider animal welfare.'

def verify_instruction_pair(new,old):
    require(new['objective']=='facts' and old['objective']=='welfare','Wrong goal pair')
    for key in ('item_id','label','detail_order'):
        require(new[key]==old[key],'Welfare/factual factor mismatch: '+key)
    a=new['request'];b=old['request']
    require(a['tools']==b['tools'] and a['messages'][0]==b['messages'][0] and a['messages'][2:]==b['messages'][2:],'Noninstruction request content changed')
    require(a['messages'][1]['role']==b['messages'][1]['role']=='user','Instruction must be initial user')
    require(new['instruction']==FACTS and old['instruction']==WELFARE,'Unexpected instruction wording')
    require(a['messages'][1]['content'].count(FACTS)==1 and b['messages'][1]['content'].count(WELFARE)==1,'Repeated instruction')
    require(a['messages'][1]['content'].replace(FACTS,WELFARE)==b['messages'][1]['content'],'Initial request differs beyond goal')
    require(new['text'].replace(FACTS,WELFARE)==old['text'],'Rendered text differs beyond goal')
    require(new['text'].index(FACTS)<new['text'].index('<tool_response>'),'Goal after tool results')

def load_verified_state(root,job,versions):
    ids=job['input_ids'];positions=[job['positions']['pos_b'],job['positions']['pos_a']]
    require(positions[0]==len(ids)-1 and positions[1]<positions[0] and job['request']['messages'][-1]['role']=='tool','Invalid measurement boundary')
    require(job['text'].endswith('<|im_start|>assistant\n<think>\n'),'Wrong benchmark suffix')
    identity=make_cache_identity(model_id='Qwen/Qwen3.5-9B',model_revision=REVISION,template_sha256=TEMPLATE,prompt_text=job['text'],input_ids=ids,positions=positions,layers_one_based=list(range(1,33)),dtype='float16',backend='transformers',backend_versions=versions)
    path=Path(root)/'activations'/(job['job_id']+'.npz');manifest=read(path.with_suffix('.json'))
    verified=verify_cache(path,manifest,identity);check=manifest.get('input_check',{})
    require(manifest.get('job_id')==job['job_id'] and check.get('exact_input_verified') is True and check.get('token_ids_match') is True and check.get('expected_ids_sha256')==ids_sha256(ids),'Missing producer input check')
    with np.load(path,allow_pickle=False) as z:
        h=z['hidden_states']
        require(h.shape==(2,32,4096) and h.dtype==np.float16 and np.isfinite(h).all(),'Invalid activation payload')
        require(np.array_equal(z['input_ids'],ids) and np.array_equal(z['indices'],positions),'Payload input/position mismatch')
        state=h[0,25].astype(float)
    return state,dict(job_id=job['job_id'],**verified)

def analyze(root_v6,source_v5,source_v4,weights_path):
    root=Path(root_v6);v5=Path(source_v5);v4=Path(source_v4);weights_path=Path(weights_path)
    require((root/'run_status.json').is_file(),'No completed factual-reading run')
    status=read(root/'run_status.json');jobs=read(root/'jobs.json');execution=read(root/'execution_manifest.json')
    require(status.get('state')=='complete' and status.get('completed')==24 and status.get('total')==24,'Expected24 completed factual forwards')
    require(len(jobs)==24 and len({j['job_id'] for j in jobs})==24,'Expected24 unique factual jobs')
    require(sha(root/'jobs.json')==execution['jobs_sha256']==status['jobs_sha256'],'New input hashes differ')
    oldjobs=read(v5/'jobs.json');oldmap={j['job_id']:j for j in oldjobs};oldstatus=read(v5/'run_status.json');oldreport=read(v5/'development_analysis.json')
    require(oldstatus.get('state')=='complete' and oldstatus.get('completed')==48,'Saved welfare producer incomplete')
    require(sha(v5/'jobs.json')==oldstatus['jobs_sha256']==oldreport['jobs_sha256'],'Saved welfare input hashes differ')
    versions=status.get('backend_versions',{})
    require(versions==oldstatus.get('backend_versions')==read(v4/'run_status.json').get('backend_versions'),'Backend identity differs across runs')
    require(versions.get('model_dtype')=='bfloat16' and versions.get('attention')=='sdpa' and all(versions.get(k) for k in ('torch','transformers','numpy')),'Incomplete backend identity')
    states={};evidence=[];reused=[];mapped=set()
    for j in jobs:
        source_id=j.get('source_v5_job_id',j.get('source_welfare_job_id'))
        require(source_id in oldmap and source_id not in mapped,'Missing/duplicate source welfare job')
        old=oldmap[source_id];mapped.add(source_id);verify_instruction_pair(j,old)
        require(old['split']=='train','Welfare state not training')
        value,proof=load_verified_state(root,j,versions);welfare,oldproof=load_verified_state(v5,old,versions)
        for goal,state in [('facts',value),('welfare',welfare)]:
            key=(j['item_id'],goal,j['detail_order'],j['label']);require(key not in states,'Duplicate training factor');states[key]=state
        evidence.append(proof);reused.append(oldproof)
    direction,center,fit_report=fit_direction(states)
    dev=[j for j in oldjobs if j['split']=='development'];require(len(dev)==64,'Expected64 unchanged neutral checks')
    require(not {j['item_id'] for j in jobs}&{j['item_id'] for j in dev},'Training/development overlap')
    source_jobs=read(v4/'jobs.json');source_map={j['job_id']:j for j in source_jobs};source_report=read(v4/'benchmark_validation.json');selected=read(v4/'selected_layer_manifest.json')
    require(sha(v4/'jobs.json')==selected['jobs_sha256']==source_report['core_jobs_sha256'],'V4 input hash mismatch')
    require(sha(v4/'selected_layers_1_26.npz')==selected['selected_npz_sha256'],'V4 selected bytes differ')
    require(selected['layers_one_based']==[1,26] and selected['position_order']==['pos_b','pos_a'],'Selected layer semantics differ')
    records={r['job_id']:r for r in selected['records']};payloads={r['job_id']:r['payload_sha256'] for r in source_report['cache_evidence']}
    oldrows={(r['job_id'],r['position']):r for r in oldreport['rows']}
    require(sha(weights_path)==WEIGHTS_SHA,'Original weights differ')
    rows=[];devstates={}
    with np.load(v5/'candidate_v5_direction.npz',allow_pickle=False) as p,np.load(weights_path,allow_pickle=False) as w,np.load(v4/'selected_layers_1_26.npz',allow_pickle=False) as z:
        prior=p['direction'].copy();prior_center=p['center'].copy()
        require(int(p['layer_one_based'])==26 and str(p['jobs_sha256'])==sha(v5/'jobs.json'),'V5 candidate identity differs')
        require(hashlib.sha256(prior.tobytes()).hexdigest()==oldreport['fit']['direction_sha256'],'V5 direction changed')
        require((int(w['e2_layer']),int(w['content_lr_layer']),int(w['e1_layer']))==(26,26,1),'Original layers differ')
        for j in dev:
            source=source_map[j['job_id']]
            for key in ('request','text','input_ids','positions','item_id','label','condition'):require(j[key]==source[key],'Changed neutral check '+key)
            h=z[j['job_id']];record=records[j['job_id']]
            require(h.shape==(2,2,4096) and h.dtype==np.float16 and np.isfinite(h).all(),'Invalid neutral cached state')
            require(hashlib.sha256(h.tobytes()).hexdigest()==record['selected_array_sha256'] and record['original_npz_sha256']==payloads[j['job_id']],'Neutral provenance mismatch')
            devstates[j['item_id'],j['condition'],j['label']]=h[0,1].astype(float)
            for n,pos in enumerate(('pos_b','pos_a')):
                h1=h[n,0].astype(float);h26=h[n,1].astype(float)
                baseline=dict(candidate_v5_l26=float(np.dot(h26-prior_center,prior)),original_e2_l26=float(np.dot(h26-w['e2_mid_mm'],w['e2_w_mm'])),content_lr_l26=float(np.dot(h26,w['content_w_lr'])+float(w['content_b_lr'])),e1_l1=float(np.dot(h1-w['e1_mid_mm'],w['e1_w_mm'])))
                for key,value in baseline.items():require(abs(value-oldrows[j['job_id'],pos][key])<1e-8,'Baseline reproduction mismatch '+key)
                rows.append(dict(job_id=j['job_id'],item_id=j['item_id'],label=j['label'],condition=j['condition'],position=pos,candidate_v6_l26=float(np.dot(h26-center,direction)),**baseline))
        fit_report['v5_direction_cosine']=cosine(direction,prior)
        fit_report['original_e2_direction_cosine']=cosine(direction,w['e2_w_mm'])
        fit_report['original_content_lr_direction_cosine']=cosine(direction,w['content_w_lr'])
    items=sorted({j['item_id'] for j in dev});fit_report['neutral_nuisance_mean_shift_cosines']={}
    for condition in CONDITIONS[1:]:
        shift=np.mean([devstates[i,condition,l]-devstates[i,'base',l] for i in items for l in (0,1)],axis=0)
        fit_report['neutral_nuisance_mean_shift_cosines'][condition]=dict(cosine=cosine(direction,shift),used_for_fitting=False)
    result=dict(status='completed_factual_control_development_analysis',jobs_sha256=sha(root/'jobs.json'),new_factual_caches_verified=24,reused_welfare_caches_verified=24,reused_development_caches=64,model_runs_by_analyzer=0,fit=fit_report,new_cache_evidence=evidence,welfare_cache_evidence=reused,rows=rows,**summarize(rows),rq3_ready=False,measurement_validated=False,limitations=['All eight neutral development examples were previously inspected; no fresh holdout.','Factual attention controls animal-topic attention, not all instruction/valence/quality confounds.','Two instructions can differ in token count; same measured boundary and exact input identity are preserved.','Price and rating checks are target-first only; no complete nuisance factorial.','No final-answer generation or causal intervention.'])
    dest=root/'candidate_v6_direction.npz'
    if dest.exists():
        with np.load(dest,allow_pickle=False) as p:require(np.array_equal(p['direction'],direction) and np.array_equal(p['center'],center),'Refusing different candidate overwrite')
    else:np.savez_compressed(dest,direction=direction,center=center,layer_one_based=np.array(26),jobs_sha256=np.array(sha(root/'jobs.json')))
    (root/'factual_analysis.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('root','source-v5','source-v4','weights'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    try:r=analyze(a.root,a.source_v5,a.source_v4,a.weights)
    except (ValidationBlocked,FileNotFoundError) as exc:p.exit(2,f'Analysis not run: {exc}\n')
    print(json.dumps(r['development_flags'],indent=2))

