"""Isolated, pinned vLLM comparison; no new agent trajectory generation."""
from pathlib import Path
import json, os, inspect, traceback, importlib.metadata
os.environ['VLLM_WORKER_MULTIPROC_METHOD']='spawn'
ROOT=Path('/marimo/rq2_validation_v1')

def main():
    from vllm import LLM, SamplingParams
    data=json.loads((ROOT/'backend_inputs.json').read_text())
    print('LLM.chat signature',inspect.signature(LLM.chat),flush=True)
    config=dict(model=data['snapshot'],tokenizer=data['snapshot'],dtype='bfloat16',max_model_len=max(len(r['input_ids']) for r in data['runs'])+32,gpu_memory_utilization=0.50,max_num_seqs=1,enforce_eager=True,enable_prefix_caching=False,disable_log_stats=True,limit_mm_per_prompt={'image':0,'video':0},seed=20261110)
    llm=LLM(**config)
    environment=dict(config=config,versions={n:importlib.metadata.version(n) for n in ('vllm','torch','transformers','numpy')},historical_revision_verified=False)
    results=[]
    for number,job in enumerate(data['runs']):
        # Exercise vLLM's chat rendering on the reconstructed logged request.
        chat=llm.chat(job['messages'],sampling_params=SamplingParams(temperature=0,max_tokens=1),tools=job['tools'],use_tqdm=False)[0]
        # Teacher-force the same full continuation; backend tokenizes text itself.
        scored=llm.generate(job['text'],sampling_params=SamplingParams(temperature=0,max_tokens=1,prompt_logprobs=0),use_tqdm=False)[0]
        actual_ids=list(scored.prompt_token_ids)
        row=dict(run_id=job['run_id'],prefix_ids=list(chat.prompt_token_ids),chat_prefix_matches=list(chat.prompt_token_ids)==job['prefix_ids'],input_ids=actual_ids,full_input_matches=actual_ids==job['input_ids'],prefix_length=job['prefix_length'])
        row['logprobs']=[float(scored.prompt_logprobs[i][actual_ids[i]].logprob) for i in range(job['prefix_length'],len(actual_ids))]
        results.append(row)
        (ROOT/'vllm_backend_scores.json').write_text(json.dumps(dict(environment=environment,runs=results)))
        (ROOT/'vllm_status.json').write_text(json.dumps(dict(status='running',completed=number+1,chat_match=row['chat_prefix_matches'],full_match=row['full_input_matches'])))
        print('VLLM scored',number+1,'/20',row['chat_prefix_matches'],row['full_input_matches'],flush=True)
    (ROOT/'vllm_status.json').write_text(json.dumps(dict(status='complete',completed=len(results))))

if __name__=='__main__':
    try:main()
    except Exception as e:
        (ROOT/'vllm_status.json').write_text(json.dumps(dict(status='failed',error=repr(e))))
        traceback.print_exc()
        raise
