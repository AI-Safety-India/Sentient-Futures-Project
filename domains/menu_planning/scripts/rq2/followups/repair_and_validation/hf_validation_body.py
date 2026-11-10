def run_rq2_validation_hf():
    from pathlib import Path
    import json, hashlib, importlib.util, importlib.metadata, gc, zipfile, copy
    import zipfile_zstd
    import numpy as np
    import torch
    from transformers import AutoTokenizer, Qwen3_5ForConditionalGeneration
    from huggingface_hub import hf_hub_download
    # REQUEST_HELPERS
    root=Path('/marimo/rq2_validation_v1')
    repo=Path('/home/marimo/Sentient-Futures-Project')
    protocol=json.loads((root/'protocol.json').read_text())
    revision='c202236235762e1c871ad0ccb60c8ee5ba337b9a'
    snapshot=Path(hf_hub_download('Qwen/Qwen3.5-9B','config.json',revision=revision,local_files_only=True)).parent
    tok=AutoTokenizer.from_pretrained(str(snapshot),local_files_only=True)
    assert hashlib.sha256(str(tok.chat_template).encode()).hexdigest()=='a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
    probes_path=repo/'results/rq2/probe_directions.npz'
    assert hashlib.sha256(probes_path.read_bytes()).hexdigest()==protocol['probe_sha256']
    spec=importlib.util.spec_from_file_location('validation_rebuild',repo/'domains/menu_planning/scripts/rq2/replay_rebuild.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    positions=[json.loads(s) for s in (repo/'results/rq2/t2/qwen35_positions_1200.jsonl').read_text().splitlines()]
    selected=[r for r in positions if r['run_id'] in protocol['backend_runs']]
    backend=[]
    for condition in ('neutral','ethical'):
        wanted={(r['sample_id'],int(r['epoch'])):r for r in selected if r['prompt_condition']==condition}
        path=next((repo/'results/logs/full/qwen3.5-9b'/condition).glob('*.eval'))
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if not name.startswith('samples/') or not name.endswith('.json'):continue
                sample=json.loads(z.read(name));rec=wanted.get((str(sample['id']),int(sample['epoch'])))
                if rec is None:continue
                event,request,source=requests(sample)[rec['target_call_idx']]
                messages,tools=helper.rebuild_messages(request)
                prefix=tok.apply_chat_template(messages,tools=tools,add_generation_prompt=True,tokenize=False)
                final=dict(request,messages=request['messages']+[assistant(event['output']['choices'][0]['message'])])
                fm,ft=helper.rebuild_messages(final)
                full=tok.apply_chat_template(fm,tools=ft,add_generation_prompt=False,tokenize=False)
                prefix_ids=tok.encode(prefix,add_special_tokens=False);ids=tok.encode(full,add_special_tokens=False)
                assert ids[:len(prefix_ids)]==prefix_ids
                backend.append(dict(run_id=rec['run_id'],messages=messages,tools=tools,text=full,input_ids=ids,prefix_ids=prefix_ids,prefix_length=len(prefix_ids),source=source,historical_logprobs_present=bool(event['output']['choices'][0].get('logprobs'))))
    assert len(backend)==20
    (root/'backend_inputs.json').write_text(json.dumps(dict(snapshot=str(snapshot),revision=revision,runs=backend)))
    plans=[]
    for i,job in enumerate(protocol['jobs']):
        enc=tok(job['text'],add_special_tokens=False,return_offsets_mapping=True)
        ids=enc['input_ids'];offsets=enc['offset_mapping']
        def at(char):return next(i for i,(a,b) in enumerate(offsets) if a<=char<b)
        if job['index_rule']=='stored':index=job['stored_index']
        elif job['index_rule']=='matched_suffix':
            ref=tok(job['reference_text'],add_special_tokens=False,return_offsets_mapping=True)
            char=len(job['text'])-(len(job['reference_text'])-ref['offset_mapping'][job['stored_index']][0])
            index=at(char)
            assert tok.decode([ids[index]])==tok.decode([ref['input_ids'][job['stored_index']]])
        else:index=len(ids)-1
        indices=[index]
        if job.get('reading_boundary'):indices.append(at(job['text'].rindex('</tool_response>')))
        plans.append(dict(job=i,indices=indices,input_ids=ids,primary_token=tok.decode([ids[index]])))
    (root/'probe_position_plan.json').write_text(json.dumps(plans))
    environment=dict(revision=revision,dtype='bfloat16',attention='sdpa',historical_revision_verified=False,versions={p:importlib.metadata.version(p) for p in ('torch','transformers','numpy')})
    scores=[];backend_scores=[]
    print('HF plans verified: 120 probe forwards and 20 teacher-forced backend forwards.',flush=True)
    gc.collect();torch.cuda.empty_cache()
    model=Qwen3_5ForConditionalGeneration.from_pretrained(str(snapshot),local_files_only=True,dtype=torch.bfloat16,device_map={'':0},attn_implementation='sdpa').eval()
    model.requires_grad_(False)
    try:
        with np.load(probes_path,allow_pickle=False) as probes, torch.inference_mode():
            for plan,job in zip(plans,protocol['jobs']):
                path=root/f"probe_{plan['job']:03d}.npz"
                if path.exists():
                    with np.load(path,allow_pickle=False) as a:
                        assert np.array_equal(a['input_ids'],plan['input_ids']);h=a['hidden_states'].copy()
                else:
                    inputs=torch.tensor([plan['input_ids']],device='cuda')
                    out=model(input_ids=inputs,use_cache=False,output_hidden_states=True,return_dict=True,logits_to_keep=1)
                    assert len(out.hidden_states)==33
                    h=np.stack([x[0,plan['indices']].to(torch.float16).cpu().numpy() for x in out.hidden_states[1:]],axis=1)
                    assert np.isfinite(h).all()
                    np.savez_compressed(path,hidden_states=h,input_ids=np.asarray(plan['input_ids']),indices=np.asarray(plan['indices']))
                    del out,inputs
                for row,idx in enumerate(plan['indices']):
                    result={k:v for k,v in job.items() if k not in ('text','reference_text')}
                    result.update(job=plan['job'],position='primary' if row==0 else 'reading',token_index=idx,token=tok.decode([plan['input_ids'][idx]]))
                    for name in ('content','e1','e2'):
                        result['score_'+name]=float(np.dot(h[row,int(probes[name+'_layer'])-1].astype(np.float32)-probes[name+'_mid_mm'],probes[name+'_w_mm']))
                    scores.append(result)
                if (plan['job']+1)%10==0: print('Probe forwards',plan['job']+1,'/120',flush=True)
                (root/'hf_status.json').write_text(json.dumps(dict(status='running',probe_forwards=plan['job']+1,backend_forwards=0)))
            (root/'probe_scores.json').write_text(json.dumps(dict(environment=environment,rows=scores),indent=2))
            for number,job in enumerate(backend):
                dest=root/f'hf_backend_{number:02d}.npz'
                ids=job['input_ids'];start=job['prefix_length'];count=len(ids)-start
                assert count>0
                if dest.exists():
                    with np.load(dest,allow_pickle=False) as a:
                        assert np.array_equal(a['input_ids'],ids);values=a['logprobs'].tolist()
                else:
                    inp=torch.tensor([ids],device='cuda')
                    out=model(input_ids=inp,use_cache=False,return_dict=True,logits_to_keep=count+1)
                    logits=out.logits[0,:-1];targets=inp[0,start:]
                    assert logits.shape[0]==len(targets)
                    values=[]
                    for begin in range(0,len(targets),64):
                        part=logits[begin:begin+64].float()
                        lp=part.gather(1,targets[begin:begin+64,None]).squeeze(1)-torch.logsumexp(part,dim=-1)
                        values.extend(lp.cpu().tolist())
                    np.savez_compressed(dest,input_ids=np.asarray(ids),logprobs=np.asarray(values))
                    del out,inp,logits,targets,part,lp
                backend_scores.append(dict(run_id=job['run_id'],prefix_length=start,logprobs=values))
                print('HF backend forwards',number+1,'/20',flush=True)
                (root/'hf_status.json').write_text(json.dumps(dict(status='running',probe_forwards=120,backend_forwards=number+1)))
        (root/'hf_backend_scores.json').write_text(json.dumps(dict(environment=environment,runs=backend_scores)))
        (root/'hf_status.json').write_text(json.dumps(dict(status='complete',probe_forwards=120,backend_forwards=20)))
        print('HF validation extraction complete.',flush=True)
    finally:
        del model
        gc.collect();torch.cuda.empty_cache()

run_rq2_validation_hf()
