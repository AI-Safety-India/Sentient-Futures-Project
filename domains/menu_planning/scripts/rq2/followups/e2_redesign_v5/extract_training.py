"""Versioned forward-only follow-up; imports never start inference."""
def extract_training(root_path):
    from pathlib import Path
    import json,hashlib,gc,importlib.metadata
    import numpy as np
    import torch
    from transformers import AutoTokenizer,Qwen3_5ForConditionalGeneration
    from validation_helpers import make_cache_identity,verify_cache,measured_input_check
    root=Path(root_path)
    jobs_path=root/'jobs.json'
    jobs=[j for j in json.loads(jobs_path.read_text(encoding='utf-8')) if j['split']=='train']
    protocol=json.loads((root/'execution_manifest.json').read_text())
    assert hashlib.sha256(jobs_path.read_bytes()).hexdigest()==protocol['jobs_sha256']
    assert protocol['development_only'] and protocol['paid_resources_authorized'] is False
    assert len(jobs)==48 and len({j['job_id'] for j in jobs})==48
    revision='c202236235762e1c871ad0ccb60c8ee5ba337b9a'
    template_hash='a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
    snapshot=Path.home()/'.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots'/revision
    tok=AutoTokenizer.from_pretrained(str(snapshot),local_files_only=True)
    tok.chat_template=(snapshot/'chat_template.jinja').read_text()
    assert hashlib.sha256(tok.chat_template.encode()).hexdigest()==template_hash
    for j in jobs:
        assert tok.encode(j['text'],add_special_tokens=False)==j['input_ids']
        req=j['request']
        assert req['messages'][-1]['role']=='tool'
        assert tok.apply_chat_template(req['messages'],tools=req['tools'],add_generation_prompt=True,tokenize=False)==j['text']
        assert j['text'].endswith('<|im_start|>assistant\n<think>\n')
        assert j['positions']['pos_b']==len(j['input_ids'])-1
        assert tok.decode([j['input_ids'][j['positions']['pos_a']]],skip_special_tokens=False)=='</tool_response>'
    versions={k:importlib.metadata.version(k) for k in ['torch','transformers','numpy']}
    versions.update(model_dtype='bfloat16',attention='sdpa')
    outdir=root/'activations';outdir.mkdir(exist_ok=True)
    completed=[]
    def status(state,**kwargs):
        (root/'run_status.json').write_text(json.dumps(dict(state=state,completed=len(completed),total=len(jobs),jobs_sha256=protocol['jobs_sha256'],**kwargs),indent=2))
    status('loading_cached_model')
    print('Verified48 exact inputs and benchmark boundaries; no generation or orders.',flush=True)
    model=Qwen3_5ForConditionalGeneration.from_pretrained(str(snapshot),local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda').eval()
    model.requires_grad_(False)
    try:
        with torch.inference_mode():
            for j in jobs:
                positions=[j['positions']['pos_b'],j['positions']['pos_a']]
                identity=make_cache_identity(model_id='Qwen/Qwen3.5-9B',model_revision=revision,template_sha256=template_hash,prompt_text=j['text'],input_ids=j['input_ids'],positions=positions,layers_one_based=list(range(1,33)),dtype='float16',backend='transformers',backend_versions=versions)
                dest=outdir/(j['job_id']+'.npz');mpath=dest.with_suffix('.json')
                if dest.exists():
                    manifest=json.loads(mpath.read_text());verify_cache(dest,manifest,identity)
                    with np.load(dest,allow_pickle=False) as z:
                        assert np.array_equal(z['input_ids'],j['input_ids']) and np.array_equal(z['indices'],positions)
                        assert z['hidden_states'].shape==(2,32,4096) and np.isfinite(z['hidden_states']).all()
                else:
                    inp=torch.tensor([j['input_ids']],device='cuda')
                    observed=measured_input_check(j['input_ids'],actual_backend_ids=inp[0].tolist())
                    assert observed['exact_input_verified']
                    output=model(input_ids=inp,attention_mask=torch.ones_like(inp),use_cache=False,output_hidden_states=True,return_dict=True,logits_to_keep=1)
                    assert len(output.hidden_states)==33
                    h=np.stack([s[0,positions].to(torch.float16).cpu().numpy() for s in output.hidden_states[1:]],axis=1)
                    assert h.shape==(2,32,4096) and np.isfinite(h).all()
                    np.savez_compressed(dest,hidden_states=h,input_ids=np.asarray(j['input_ids']),indices=np.asarray(positions))
                    manifest=dict(identity,payload_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),input_check=observed,job_id=j['job_id'])
                    mpath.write_text(json.dumps(manifest,indent=2));verify_cache(dest,manifest,identity)
                    del output,inp,h
                completed.append(dict(job_id=j['job_id'],payload_sha256=manifest['payload_sha256']))
                status('running');print(f'Completed {len(completed)}/48: {j["job_id"]}',flush=True)
                (root/'completed_jobs.json').write_text(json.dumps(completed,indent=2))
        status('complete',generation_calls=0,model_revision=revision,backend_versions=versions)
    except BaseException as exc:
        status('interrupted_or_failed',error=str(exc));raise
    finally:
        del model;gc.collect();torch.cuda.empty_cache()
