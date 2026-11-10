"""Prepare the missing factual-reading control; no model inference or network."""
from pathlib import Path
import copy,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
CODE=Path(__file__).resolve().parent
OUT=ROOT/'Sentient-Futures-Project-git/results/rq2/e2_factual_v6'
SOURCE=OUT.parent/'e2_redesign_v5'
spec=importlib.util.spec_from_file_location('v6_v4_builder_helpers',ROOT/'rq2_repair/e2_benchmark_v4/build_jobs.py')
v4=importlib.util.module_from_spec(spec);spec.loader.exec_module(v4)
FACTS='When comparing suppliers, identify animal-treatment facts.'
WELFARE='When comparing suppliers, consider animal welfare.'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build(tokenizer):
    originals=[j for j in read(SOURCE/'jobs.json') if j['split']=='train' and j['objective']=='welfare']
    assert len(originals)==24
    jobs=[]
    for old in originals:
        req=copy.deepcopy(old['request'])
        assert req['messages'][1]['content']==old['base_request']+'\n\n'+WELFARE
        req['messages'][1]['content']=old['base_request']+'\n\n'+FACTS
        j=v4.prepare_job(req,job_id=old['job_id'].replace('v5_train__','v6_train__').replace('__welfare__','__facts__'),
            item_id=old['item_id'],label=old['label'],condition='facts',cohort='training',
            target_id=old['target_option_id'],tokenizer=tokenizer,
            extra=dict(split='train',objective='facts',control='base',detail_order=old['detail_order'],
                instruction=FACTS,base_request=old['base_request'],target_metadata=old['target_metadata'],
                comparator=old['comparator'],target_practice=old['target_practice'],
                source_welfare_job_id=old['job_id'],source_v5_job_id=old['job_id'],source_welfare_job_sha256=v4.canonical(old),
                prior_score_exposure=True,independent_human_label_review=False,
                instruction_token_count=len(tokenizer.backend.encode(FACTS,add_special_tokens=False).ids)))
        jobs.append(j)
    validate(jobs,originals,tokenizer)
    return jobs,originals

def validate(jobs,originals,tokenizer=None):
    assert len(jobs)==24 and len({j['job_id'] for j in jobs})==24
    source={j['job_id']:j for j in originals};items={j['item_id'] for j in jobs}
    assert len(items)==6
    assert {(j['item_id'],j['label'],j['detail_order']) for j in jobs}=={(i,l,o) for i in items for l in (0,1) for o in ('target_first','target_last')}
    assert {j['source_welfare_job_id'] for j in jobs}==set(source)
    for j in jobs:
        old=source[j['source_welfare_job_id']]
        for key in ['item_id','label','detail_order','target_metadata','comparator','target_option_id']:
            assert j[key]==old[key]
        assert j['source_welfare_job_sha256']==v4.canonical(old)
        assert j['objective']=='facts' and j['condition']=='facts'
        a=copy.deepcopy(j['request']);a['messages'][1]['content']=old['request']['messages'][1]['content']
        assert a==old['request']
        assert j['request']['messages'][1]['content']==old['base_request']+'\n\n'+FACTS
        assert j['text'].replace(FACTS,WELFARE)==old['text']
        assert j['text'].index(FACTS)<j['text'].index('<tool_response>')
        assert j['request']['messages'][-1]['role']=='tool'
        assert j['positions']['pos_b']==len(j['input_ids'])-1
        assert j['input_ids'][j['positions']['pos_b']]==198
        assert j['input_ids'][j['positions']['pos_a']]==248067
        assert j['text'].endswith('</tool_response><|im_end|>\n<|im_start|>assistant\n<think>\n')
        if tokenizer:assert tokenizer.backend.encode(j['text'],add_special_tokens=False).ids==j['input_ids']
    return dict(jobs=24,items=6,labels=2,orders=2,only_initial_clause_changes=True,upstream_instruction=True,
        saved_welfare_jobs_reused=24,cached_neutral_development_jobs_reused=64,
        positions_verified=True,token_ids_verified_offline=True,model_runs=0)

def main():
    tokenizer=v4.v3.CachedTextTokenizer(Path.home()/'.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots'/v4.v3.REVISION)
    jobs,originals=build(tokenizer);OUT.mkdir(exist_ok=True)
    (OUT/'jobs.json').write_text(json.dumps(jobs,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (OUT/'local_checks.json').write_text(json.dumps(validate(jobs,originals,tokenizer),indent=2),encoding='utf-8')
    mapping=[dict(factual_job_id=j['job_id'],welfare_job_id=j['source_welfare_job_id'],item_id=j['item_id'],label=j['label'],detail_order=j['detail_order']) for j in jobs]
    (OUT/'welfare_reuse_map.json').write_text(json.dumps(dict(source_v5_jobs_sha256=sha(SOURCE/'jobs.json'),records=mapping),indent=2),encoding='utf-8')
    (OUT/'input_manifest.json').write_text(json.dumps(dict(jobs_sha256=sha(OUT/'jobs.json'),builder_sha256=sha(__file__),
        source_v5_jobs_sha256=sha(SOURCE/'jobs.json'),instruction=FACTS,welfare_instruction=WELFARE,
        factual_instruction_tokens=sorted({j['instruction_token_count'] for j in jobs}),
        welfare_instruction_tokens=sorted({j['instruction_token_count'] for j in originals}),
        new_forwards=24,reused_welfare=24,reused_development=64,layer_one_based=26,primary_position='pos_b',
        model_runs=0,paid_resources_authorized=False,
        limits=['Factual attention is a control for attention to animal treatment, not proof that evaluation is isolated.','No independent fresh validation set.','Instruction token counts measured; no artificial padding.']),indent=2),encoding='utf-8')
    print(json.dumps(read(OUT/'local_checks.json'),indent=2));print('jobs_sha256',sha(OUT/'jobs.json'))

if __name__=='__main__':main()
