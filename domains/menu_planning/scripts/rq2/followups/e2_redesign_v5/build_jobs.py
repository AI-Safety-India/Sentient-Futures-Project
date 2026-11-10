"""Prepare a 48-forward E2 training pilot and reuse 64 scored development inputs.

Offline only: no model, network, remote session or inference entry point.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys

ROOT=Path(__file__).resolve().parents[2]
CODE=Path(__file__).resolve().parent
OUT=ROOT/'Sentient-Futures-Project-git/results/rq2/e2_redesign_v5'
V4=ROOT/'Sentient-Futures-Project-git/results/rq2/e2_benchmark_v4'
spec=importlib.util.spec_from_file_location('e2_v4_builder_helpers',ROOT/'rq2_repair/e2_benchmark_v4/build_jobs.py')
v4=importlib.util.module_from_spec(spec);spec.loader.exec_module(v4)
INSTRUCTIONS={
    'welfare':'When comparing suppliers, consider animal welfare.',
    'commercial':'When comparing suppliers, consider commercial value.',
}

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def build_training(pairs,tokenizer):
    jobs=[]
    for pair in pairs:
        # Reuse the benchmark renderers and comparator. Only baseline/order
        # requests are retained; price/rating construction here runs no model.
        templates=[j for j in v4.build_fresh([pair],tokenizer) if j['condition'] in ('base','order')]
        for template in templates:
            order='target_first' if template['condition']=='base' else 'target_last'
            for objective,instruction in INSTRUCTIONS.items():
                request=copy.deepcopy(template['request'])
                request['messages'][1]['content']=pair['request']+'\n\n'+instruction
                item=pair['item_id'];label=template['label']
                job=v4.prepare_job(request,job_id=f'v5_train__{item}__{label}__{objective}__{order}',
                    item_id=item,label=label,condition=objective,cohort='training',
                    target_id=pair['metadata']['id'],tokenizer=tokenizer,
                    extra=dict(split='train',objective=objective,control='base',detail_order=order,
                        instruction=instruction,base_request=pair['request'],pair_source_sha256=canonical(pair),
                        target_metadata=template['target_metadata'],comparator=template['comparator'],
                        target_practice=pair['target_practice'],prior_score_exposure=True,
                        prepared_job_kind='new_training_forward_required',
                        independent_human_label_review=False))
                # The only user instruction is upstream of the tool results.
                instruction_char=job['text'].index(instruction)
                job['instruction_end_char']=instruction_char+len(instruction)
                job['instruction_token_count']=len(tokenizer.backend.encode(instruction,add_special_tokens=False).ids)
                job['primary_prefix_sha256']=canonical(job['input_ids'][:job['positions']['pos_b']+1])
                jobs.append(job)
    return jobs

def reuse_development(pairs):
    ids={p['item_id'] for p in pairs}
    source=read(V4/'jobs.json');jobs=[]
    for old in source:
        if old['cohort']!='fresh':continue
        assert old['item_id'] in ids
        job=copy.deepcopy(old)
        job.update(split='development',objective='neutral',control='base' if old['condition']=='order' else old['condition'],
            detail_order='target_last' if old['condition']=='order' else 'target_first',
            cohort='development_reused_v4',source_cohort=old['cohort'],prior_score_exposure=True,
            prepared_job_kind='reuse_existing_v4_selected_layers',source_v4_job_sha256=canonical(old),
            reuse_note='Previously scored development input, not a new or independent holdout. Request, rendered text, IDs, positions and job_id preserved.')
        jobs.append(job)
    assert len(jobs)==64
    return jobs

def validate(jobs,pairs,tokenizer=None):
    train=[j for j in jobs if j['split']=='train'];dev=[j for j in jobs if j['split']=='development']
    expected_train={p['item_id'] for p in pairs if p['split']=='train'}
    expected_dev={p['item_id'] for p in pairs if p['split']=='development'}
    assert len(expected_train)==6 and len(expected_dev)==8 and not expected_train&expected_dev
    assert len(train)==48 and len(dev)==64 and len({j['job_id'] for j in jobs})==112
    assert {j['item_id'] for j in train}==expected_train and {j['item_id'] for j in dev}==expected_dev
    pair_by_id={p['item_id']:p for p in pairs}
    for item in expected_train:
        group=[j for j in train if j['item_id']==item]
        for j in group:
            pair=pair_by_id[item]
            field='higher_concern_description' if j['label']==1 else 'lower_concern_description'
            assert j['target_metadata']['description']==pair[field]+' Price shown in '+pair['price_note']+'.'
            assert j['pair_source_sha256']==canonical(pair)
        assert {(j['label'],j['objective'],j['detail_order']) for j in group}=={(label,obj,order) for label in (0,1) for obj in INSTRUCTIONS for order in ('target_first','target_last')}
        for order in ('target_first','target_last'):
            for label in (0,1):
                a,b=[j for j in group if j['detail_order']==order and j['label']==label]
                assert {a['objective'],b['objective']}==set(INSTRUCTIONS)
                assert a['request']['messages'][0]==b['request']['messages'][0]
                assert a['request']['messages'][2:]==b['request']['messages'][2:]
                assert a['request']['tools']==b['request']['tools']
                for j in (a,b):
                    assert j['request']['messages'][1]['content']==pair_by_id[item]['request']+'\n\n'+INSTRUCTIONS[j['objective']]
                    assert j['text'].count(INSTRUCTIONS[j['objective']])==1
                    assert j['instruction_end_char']<j['text'].index('<tool_response>')
                # Unlike a future appended question, this manipulation is in
                # the causal prefix used to form the measured hidden state.
                assert a['input_ids'][:a['positions']['pos_b']+1]!=b['input_ids'][:b['positions']['pos_b']+1]
            for objective in INSTRUCTIONS:
                a,b=[j for j in group if j['detail_order']==order and j['objective']==objective]
                assert {a['label'],b['label']}=={0,1}
                assert a['text'].replace(a['target_description'],'<TARGET>')==b['text'].replace(b['target_description'],'<TARGET>')
                assert {k:v for k,v in a['target_metadata'].items() if k!='description'}=={k:v for k,v in b['target_metadata'].items() if k!='description'}
        for objective in INSTRUCTIONS:
            for label in (0,1):
                first,last=sorted([j for j in group if j['objective']==objective and j['label']==label],key=lambda j:j['detail_order'])
                assert first['detail_order']=='target_first' and last['detail_order']=='target_last'
                assert first['request']['messages'][:-2]==last['request']['messages'][:-2]
                assert first['request']['messages'][-2:]==last['request']['messages'][-2:][::-1]
    old_by_id={j['job_id']:j for j in read(V4/'jobs.json')}
    for j in dev:
        old=old_by_id[j['job_id']]
        assert old['cohort']=='fresh' and j['prior_score_exposure'] is True
        for key in ('request','text','input_ids','positions','label','item_id','condition'):
            assert j[key]==old[key]
        assert j['source_v4_job_sha256']==canonical(old)
    for j in jobs:
        assert j['request']['messages'][-1]['role']=='tool'
        assert all(m['role']!='user' for m in j['request']['messages'][2:])
        assert j['positions']['pos_b']==len(j['input_ids'])-1
        assert j['input_ids'][j['positions']['pos_b']]==198 and j['input_ids'][j['positions']['pos_a']]==248067
        assert j['text'].endswith('</tool_response><|im_end|>\n<|im_start|>assistant\n<think>\n')
        if tokenizer:
            assert tokenizer.backend.encode(j['text'],add_special_tokens=False).ids==j['input_ids']
    return dict(status='offline_preparation_checks_passed',jobs=112,new_training_forwards_required=48,
        existing_development_jobs_reused=64,train_items=6,development_items=8,independent_fresh_holdout_items=0,
        objectives_upstream_of_measurement=True,quartet_causal_prefixes_differ=True,
        train_order_balanced=True,within_pair_metadata_matched=True,no_post_tool_user_message=True,
        development_requests_and_ids_unchanged=True,development_previously_scored=True,
        model_runs=0,training_runtime_ids_verified=False)

def cache_reuse_plan(jobs):
    import numpy as np
    manifest=read(V4/'selected_layer_manifest.json')
    path=V4/'selected_layers_1_26.npz'
    assert digest(path)==manifest['selected_npz_sha256']
    assert manifest['jobs_sha256']==digest(V4/'jobs.json')
    records={r['job_id']:r for r in manifest['records']}
    reusable=[]
    with np.load(path,allow_pickle=False) as arrays:
        for j in jobs:
            if j['split']!='development':continue
            a=arrays[j['job_id']]
            assert a.shape==(2,2,4096) and a.dtype==np.float16
            assert hashlib.sha256(a.tobytes()).hexdigest()==records[j['job_id']]['selected_array_sha256']
            reusable.append(dict(job_id=j['job_id'],item_id=j['item_id'],array_key=j['job_id'],**{k:v for k,v in records[j['job_id']].items() if k!='job_id'}))
    return dict(status='local_lossless_selected_layer_cache_verified',reusable_jobs=64,
        source_file=str(path.relative_to(ROOT)),source_file_sha256=digest(path),
        source_manifest_sha256=digest(V4/'selected_layer_manifest.json'),layers_one_based=[1,26],
        position_order=['pos_b','pos_a'],records=reusable,
        exclusions='No new instructed training activations exist; none may be inferred from neutral caches. Existing development scores are not independent validation.')

def main():
    payload=read(CODE/'candidate_pairs.json');pairs=payload['pairs'] if isinstance(payload,dict) else payload
    tokenizer=v4.v3.CachedTextTokenizer(Path.home()/'.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots'/v4.v3.REVISION)
    jobs=build_training([p for p in pairs if p['split']=='train'],tokenizer)+reuse_development([p for p in pairs if p['split']=='development'])
    checks=validate(jobs,pairs,tokenizer);reuse=cache_reuse_plan(jobs)
    OUT.mkdir(parents=True,exist_ok=True)
    for name,obj in [('jobs.json',jobs),('local_checks.json',checks),('cache_reuse_plan.json',reuse)]:
        (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    manifest=dict(status='prepared_not_executed',jobs_sha256=digest(OUT/'jobs.json'),pairs_sha256=digest(CODE/'candidate_pairs.json'),
        builder_sha256=digest(__file__),instructions=INSTRUCTIONS,
        instruction_token_counts={objective:sorted({j['instruction_token_count'] for j in jobs if j.get('objective')==objective}) for objective in INSTRUCTIONS},
        primary_position='pos_b',layer_one_based=26,
        minimum_new_forwards=48,existing_development_forwards_reused=64,independent_final_holdout_available=False,
        paid_resources_authorized=False,model_inference_started=False,
        dev_coverage='base target-first and target-last; price/rating controls target-first only. Additional factorial controls deferred.',
        source_sha256={str(p.relative_to(ROOT)):digest(p) for p in [V4/'jobs.json',V4/'selected_layers_1_26.npz',V4/'selected_layer_manifest.json',V4.parent/'probe_directions.npz']},
        limits=['Instruction token counts are measured and reported; no artificial padding was added.',
                'Goal-conditioned interaction may reflect instruction following, attention or supplier sentiment; neutral transfer is a required development check, not proof of spontaneous evaluation.',
                'This package contains no fresh final holdout and no model output.'])
    (OUT/'preparation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checks,indent=2))

if __name__=='__main__':main()
