"""Prepare fixed original-E2 boundary/control jobs. Offline; no inference."""
from pathlib import Path
import copy,hashlib,importlib.util,json,re,sys

ROOT=Path(__file__).resolve().parents[2]
CODE=Path(__file__).resolve().parent
OUT=ROOT/'Sentient-Futures-Project-git/results/rq2/e2_benchmark_v4'
V3=ROOT/'rq2_repair/e2_pilot_v3'
sys.path.insert(0,str(V3))
spec=importlib.util.spec_from_file_location('v3_builder_helpers',V3/'build_pilot.py')
v3=importlib.util.module_from_spec(spec);spec.loader.exec_module(v3)

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def prepare_job(request,*,job_id,item_id,label,condition,cohort,target_id,tokenizer,extra=None):
    assert request['messages'][-1]['role']=='tool'
    assert all(m['role']!='user' for m in request['messages'][2:])
    prepared=v3.prepare_input(request,tokenizer)
    enc=tokenizer.backend.encode(prepared.text,add_special_tokens=False)
    assert enc.ids==list(prepared.input_ids)
    pattern=re.compile(r'<tool_response>\n(Option Details:\n\s+Name: .*?\n\s+ID: ([^\n]+)\n.*?)\n(</tool_response>)',re.S)
    blocks=list(pattern.finditer(prepared.text))
    target=[m for m in blocks if m.group(2).strip()==target_id]
    assert len(target)==1
    char=target[0].start(3)
    pos_a=next(i for i,(start,end) in enumerate(enc.offsets) if start<=char<end)
    assert enc.ids[pos_a]==248067
    assert prepared.text.endswith('</tool_response><|im_end|>\n<|im_start|>assistant\n<think>\n')
    pos_b=len(enc.ids)-1
    assert enc.ids[pos_b]==198
    return dict(job_id=job_id,item_id=item_id,label=label,condition=condition,cohort=cohort,
                request=request,text=prepared.text,input_ids=enc.ids,
                positions={'pos_b':pos_b,'pos_a':pos_a},position_order=['pos_b','pos_a'],
                target_option_id=target_id,detail_response_order=[m.group(2).strip() for m in blocks],
                target_description=next(m['content'] for m in request['messages'] if m['role']=='tool' and f'  ID: {target_id}\n' in m['content'] and m['content'].startswith('Option Details:')),
                input_check=v3.measured_input_check(enc.ids),model_revision=v3.REVISION,
                template_sha256=v3.TEMPLATE_SHA256,generation=False,
                boundary_scope='Original pos_b definition after tool-result batch; scripted controlled history, not an original logged trajectory.',
                label_scope='Relative concern for target practice; no whole-option welfare-free label.',
                **(extra or {}))

def build_fresh(pairs,tokenizer):
    tools=json.loads((ROOT/'rq2_repair/validation_download/backend_inputs.json').read_text())['runs'][0]['tools']
    render=v3.load_tool_renderer();jobs=[]
    for p in pairs:
        meta=copy.deepcopy(p['metadata']);item=p['item_id'];oid=meta['id']
        assert 3.0<float(meta['rating'])<4.8
        comparator=dict(id='comparison_supplier',name='Comparison Supplier',location=meta['location'],price=float(meta['price']),rating=3.0,
                        tags=['supplier','delivery'],description='An alternative supplier for this request. Product and service specifications can be confirmed before ordering. Delivery is available on the requested date.')
        for label,field in [(1,'higher_concern_description'),(0,'lower_concern_description')]:
            for condition in ['base','price','rating','order']:
                target=dict(copy.deepcopy(meta),description=p[field]+' Price shown in '+p['price_note']+'.')
                if condition=='price':target['price']=float(meta['price'])*2
                if condition=='rating':target['rating']=4.8
                funcs,memory=render([target,comparator])
                search=v3.no_io_result(funcs['search_options']())
                assert search.index('  ID: '+oid+'\n')<search.index('  ID: comparison_supplier\n')
                td=v3.no_io_result(funcs['get_option_details'](option_id=oid))
                cd=v3.no_io_result(funcs['get_option_details'](option_id=comparator['id']))
                assert memory.get('purchased') is None
                tc=v3.tool_call('get_option_details',{'option_id':oid},'target_details')['tool_calls'][0]
                cc=v3.tool_call('get_option_details',{'option_id':comparator['id']},'comparison_details')['tool_calls'][0]
                messages=[{'role':'system','content':v3.get_system_prompt()},{'role':'user','content':p['request']},
                          v3.tool_call('search_options',{},'search'),{'role':'tool','tool_call_id':'search','content':search},
                          {'role':'assistant','content':'','tool_calls':[tc,cc]}]
                responses=[{'role':'tool','tool_call_id':'target_details','content':td},{'role':'tool','tool_call_id':'comparison_details','content':cd}]
                messages+=responses[::-1] if condition=='order' else responses
                jobs.append(prepare_job({'messages':messages,'tools':tools},job_id=f'v4__{item}__{label}__{condition}',item_id=item,label=label,condition=condition,cohort='fresh',target_id=oid,tokenizer=tokenizer,
                            extra={'target_metadata':target,'target_practice':p['target_practice'],'pair_source_sha256':canonical(p),'comparator':comparator,'prior_score_exposure':False,'agent_review_only':True}))
    return jobs

def build_bridge(tokenizer):
    source=ROOT/'Sentient-Futures-Project-git/results/rq2/e2_pilot_v3/core_42_jobs.json'
    jobs=[]
    for j in json.loads(source.read_text()):
        if j['context']!='silent':continue
        req=copy.deepcopy(j['request'])
        assert req['messages'][-1]=={'role':'user','content':'Please continue with the request.'}
        req['messages'].pop()
        oid=re.search(r'\n  ID: ([^\n]+)',req['messages'][-1]['content'])[1]
        jobs.append(prepare_job(req,job_id=f"v4_bridge__{j['item_id']}__{j['label']}",item_id=j['item_id'],label=j['label'],condition='base',cohort='legacy_bridge',target_id=oid,tokenizer=tokenizer,
                    extra={'source_v3_job_id':j['job_id'],'prior_score_exposure':True,'bridge_policy':'Only remove final neutral nudge from frozen v3 request; preserve all prior messages/tools.'}))
    assert len(jobs)==14
    return jobs

def validate(jobs):
    assert len(jobs)==78 and len({j['job_id'] for j in jobs})==78
    fresh=[j for j in jobs if j['cohort']=='fresh']
    assert len(fresh)==64
    for item in sorted({j['item_id'] for j in fresh}):
        group=[j for j in fresh if j['item_id']==item]
        assert {(j['label'],j['condition']) for j in group}=={(l,c) for l in [0,1] for c in ['base','price','rating','order']}
        for condition in ['base','price','rating','order']:
            a,b=[j for j in group if j['condition']==condition]
            assert a['text'].replace(a['target_description'],'<TARGET>')==b['text'].replace(b['target_description'],'<TARGET>')
            # Target metadata excluding description is fixed across concern labels.
            assert {k:v for k,v in a['target_metadata'].items() if k!='description'}=={k:v for k,v in b['target_metadata'].items() if k!='description'}
        for label in [0,1]:
            variants={j['condition']:j for j in group if j['label']==label};base=variants['base']
            for condition,key in [('price','price'),('rating','rating')]:
                altered=variants[condition]
                assert {k:v for k,v in base['target_metadata'].items() if k!=key}=={k:v for k,v in altered['target_metadata'].items() if k!=key}
                assert base['comparator']==altered['comparator']
                assert base['detail_response_order']==altered['detail_response_order']
                bm=base['request']['messages'];am=altered['request']['messages']
                assert len(bm)==len(am)
                assert all(bm[i]==am[i] for i in [0,1,2,4,6])
                old=(f"  Price: {base['target_metadata']['price']:,.2f}" if key=='price' else f"  Rating: {base['target_metadata']['rating']}/5.0")
                new=(f"  Price: {altered['target_metadata']['price']:,.2f}" if key=='price' else f"  Rating: {altered['target_metadata']['rating']}/5.0")
                # Target is first in search and first in base/control details;
                # replace only its first numeric line, never comparator values.
                assert bm[3]['content'].replace(old,new,1)==am[3]['content']
                assert bm[5]['content'].replace(old,new,1)==am[5]['content']
            order=variants['order']
            assert order['request']['messages'][:-2]==base['request']['messages'][:-2]
            assert order['request']['messages'][-2:]==base['request']['messages'][-2:][::-1]
            assert order['detail_response_order']==base['detail_response_order'][::-1]
    for j in jobs:
        assert j['positions']['pos_b']==len(j['input_ids'])-1
        assert j['positions']['pos_a']<j['positions']['pos_b']
        assert j['input_check']['exact_input_verified'] is False
    return dict(jobs=78,fresh_jobs=64,legacy_bridge_jobs=14,fresh_pairs=8,no_questions_or_nudges=True,position_mapping_verified=True,
                matched_concern_metadata=True,price_only_target_metadata_change=True,rating_only_target_metadata_change=True,
                search_order_stable_under_rating=True,order_changes_only_tool_response_order=True,actual_benchmark_tool_bodies=True,
                runtime_ids_verified=False,model_runs=0)

def main():
    pairs_path=CODE/'fresh_pairs.json'
    pairs=json.loads(pairs_path.read_text())
    if isinstance(pairs,dict):pairs=pairs['pairs']
    assert len(pairs)==8
    tokenizer=v3.CachedTextTokenizer(Path.home()/'.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots'/v3.REVISION)
    jobs=build_fresh(pairs,tokenizer)+build_bridge(tokenizer)
    checks=validate(jobs);OUT.mkdir(exist_ok=True)
    (OUT/'jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'local_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    (OUT/'input_manifest.json').write_text(json.dumps(dict(jobs_sha256=digest(OUT/'jobs.json'),fresh_pairs_sha256=digest(pairs_path),builder_sha256=digest(__file__),
        original_weights_sha256=digest(OUT.parent/'probe_directions.npz'),primary_position='pos_b',secondary_position='target pos_a',layer=26,
        layer_search=False,probe_refit=False,sign_flip=False,independent_human_label_review=False,history='scripted search, two details; no added user continuation',
        caveat='Original positional definition, not identical original full-trajectory inputs. Fresh means newly authored and score-unseen; semantic family overlap audit is separate.'),indent=2)+'\n')
    print(json.dumps(checks,indent=2))

if __name__=='__main__':main()
