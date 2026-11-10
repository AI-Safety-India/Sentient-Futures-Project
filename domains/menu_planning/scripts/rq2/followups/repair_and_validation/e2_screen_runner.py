def run_e2_screen_42():
    from pathlib import Path
    import json, hashlib, re, gc
    import numpy as np
    import torch
    from transformers import AutoTokenizer, Qwen3_5ForConditionalGeneration
    root=Path('/marimo/e2_screen_42')
    jobs=json.loads((root/'screen_42_jobs.json').read_text())
    records={r['job_id']:r for r in json.loads((root/'tokenized_inputs.json').read_text())}
    approval=json.loads((root/'screen_criteria_approved.json').read_text())
    assert approval['user_label_approval_recorded'] and not approval['paid_execution_authorized']
    revision='c202236235762e1c871ad0ccb60c8ee5ba337b9a'
    snapshot=Path.home()/'.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots'/revision
    tok=AutoTokenizer.from_pretrained(str(snapshot),local_files_only=True)
    tok.chat_template=(snapshot/'chat_template.jinja').read_text()
    assert hashlib.sha256(tok.chat_template.encode()).hexdigest()=='a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
    assert len(jobs)==42
    for j in jobs:
        assert tok.encode(j['text'],add_special_tokens=False)==records[j['job_id']]['input_ids']
    with np.load(root/'probe_directions.npz',allow_pickle=False) as p:
        w=p['e2_w_mm'].astype(np.float32); mid=p['e2_mid_mm'].astype(np.float32)
        assert int(p['e2_layer'])==26
    torch.manual_seed(20261110)
    status=lambda **kw:(root/'status.json').write_text(json.dumps(kw))
    status(state='loading_model',completed=0)
    print('42 inputs verified. Loading cached pinned model on existing free runtime.',flush=True)
    model=Qwen3_5ForConditionalGeneration.from_pretrained(str(snapshot),local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda').eval()
    model.requires_grad_(False)
    rows=json.loads((root/'results.json').read_text())['rows'] if (root/'results.json').exists() else []
    completed={r['job_id']:r for r in rows}
    for r in rows:
        assert r['input_ids']==records[r['job_id']]['input_ids'] and r['input_verified']
    try:
        with torch.inference_mode():
            for n,j in enumerate(jobs):
                if j['job_id'] in completed:
                    continue
                ids=records[j['job_id']]['input_ids']
                inp=torch.tensor([ids],device='cuda')
                assert inp[0].tolist()==ids
                result={'job_id':j['job_id'],'item_id':j['item_id'],'input_ids':ids,'input_verified':True}
                if 'relative_concern_label' in j:
                    out=model(input_ids=inp,use_cache=False,output_hidden_states=True,return_dict=True,logits_to_keep=1)
                    h=out.hidden_states[26][0,-1].float().cpu().numpy()
                    assert h.shape==w.shape and np.isfinite(h).all()
                    result.update(kind='silent',label=j['relative_concern_label'],score=float(np.dot(h-mid,w)))
                    np.savez_compressed(root/(j['job_id']+'.npz'),hidden=h,input_ids=np.array(ids))
                    del out
                else:
                    out=model.generate(input_ids=inp,attention_mask=torch.ones_like(inp),max_new_tokens=2048,do_sample=False,use_cache=True,pad_token_id=tok.eos_token_id)
                    assert out[0,:len(ids)].tolist()==ids
                    generated=out[0,len(ids):].tolist()
                    raw=tok.decode(generated,skip_special_tokens=False)
                    final=raw.rsplit('</think>',1)[1] if '</think>' in raw else None
                    cleaned=re.sub(r'<\|[^>]+\|>','',final).strip() if final is not None else ''
                    match=re.fullmatch(r'\s*(A|B|equal|uncertain)[.!]?\s*',cleaned,re.I)
                    answer=match[1].lower() if match else None
                    result.update(kind=j['task'],order=j['order'],proposed_expected=j['proposed_expected_answer'],raw_output=raw,final_answer=final,parsed_answer=answer,new_tokens=len(generated),hit_token_limit=len(generated)>=2048,needs_manual_review=not bool(match))
                    del out
                rows.append(result)
                (root/'results.json').write_text(json.dumps({'revision':revision,'dtype':'bfloat16','attention':'sdpa','seed':20261110,'max_new_tokens':2048,'rows':rows},indent=2))
                status(state='running',completed=n+1,total=42,last_job=j['job_id'])
                print(f'Completed {n+1}/42: {j["job_id"]}',flush=True)
                del inp
        status(state='complete_needs_scoring',completed=42,total=42)
    except Exception as e:
        status(state='error',completed=len(rows),error=str(e))
        raise
    finally:
        del model
        gc.collect();torch.cuda.empty_cache()

run_e2_screen_42()
