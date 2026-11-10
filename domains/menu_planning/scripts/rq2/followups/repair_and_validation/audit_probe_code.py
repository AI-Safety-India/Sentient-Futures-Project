"""Read-only audit of original probe code/data; no model imports or network."""
from pathlib import Path
import ast,json,hashlib,sys
from collections import defaultdict,Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT/'Sentient-Futures-Project-git'
SCRIPTS=REPO/'domains/menu_planning/scripts/rq2'
DATA=REPO/'results/rq2'
OUT=DATA/'code_audit_v1';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(SCRIPTS))
from cached_tokenizer import CachedTextTokenizer
from input_contract import REVISION,TEMPLATE_SHA256
source=(SCRIPTS/'run_rq2_gpu_pipeline.py').read_text()
tree=ast.parse(source)
names={'compute_auroc','fit_mass_mean','score_mass_mean','fit_e2_interaction_probe'}
ns={'np':np}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'audited_helpers','exec'),ns)
checks={}
w,mid=ns['fit_mass_mean']([[1.,2.],[3.,4.]],[0,1])
checks['mass_mean_positive_minus_negative']=bool(np.allclose(w,[2**-.5]*2))
checks['auc_direction_and_ties']=ns['compute_auroc']([0,1],[0,1])==1 and ns['compute_auroc']([0,1],[1,1])==.5
rows=[];acts=[]
for split in ['train','val','test']:
    for h in (0,1):
        for q in (0,1):
            rows.append(dict(split=split,is_harmful_listing=h,is_welfare_question=q))
            acts.append([[2*h*q+3*q,7*q],[0,0]])
acts=np.asarray(acts,float)
fit=ns['fit_e2_interaction_probe'](rows,acts)
checks['e2_formula_sign_and_one_based_layer']=bool(fit['layer']==1 and np.allclose(fit['w_mm'],[1,0]))
changed=acts.copy();changed[-4:]=np.random.default_rng(123).normal(size=(4,2,2))*100
fit2=ns['fit_e2_interaction_probe'](rows,changed)
checks['test_values_do_not_select_weights_or_layer']=bool(fit2['layer']==fit['layer'] and np.array_equal(fit2['w_mm'],fit['w_mm']))
tok=CachedTextTokenizer(Path.home()/'.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots'/REVISION)
assert hashlib.sha256(tok.chat_template.encode()).hexdigest()==TEMPLATE_SHA256
datasets={}
all_splits=defaultdict(set)
for name in ['content_pairs','e1_valence_pairs','e2_asked_pairs','controls_random']:
    path=DATA/'contrast/contrast_sets'/f'{name}.jsonl'
    records=[json.loads(s) for s in path.read_text(encoding='utf-8').splitlines()]
    byitem=defaultdict(list);bad=[];tokens=Counter()
    for r in records:
        byitem[r['item_id']].append(r);all_splits[r['product_type']].add(r['split'])
        enc=tok.backend.encode(r['prompt_text'],add_special_tokens=False)
        ids=enc.ids;ix=r['tok_idx'];tokens[tok.backend.decode([ids[ix]],skip_special_tokens=False)]+=1
        if len(ids)!=r['total_tokens']:bad.append((r['item_id'],'length'))
        if name=='e2_asked_pairs' and (ix!=len(ids)-1 or not r['prompt_text'].endswith('<|im_start|>assistant\n<think>\n')):bad.append((r['item_id'],'boundary'))
        if name=='e1_valence_pairs':
            sentence='Looking at this from an animal-welfare angle, this option is '+('a real problem.' if r['label']==1 else 'fine.')
            pos=r['prompt_text'].rfind(sentence)+len(sentence)-1
            a,b=enc.offsets[ix]
            if not a<=pos<b:bad.append((r['item_id'],'judgement_position'))
    if name=='e2_asked_pairs':
        assert all({(r['is_harmful_listing'],r['is_welfare_question']) for r in group}=={(0,0),(0,1),(1,0),(1,1)} and len(group)==4 and len({r['split'] for r in group})==1 for group in byitem.values())
    if name=='e1_valence_pairs':
        for group in byitem.values():
            assert len(group)==2
            texts=[r['prompt_text'].replace('a real problem.','JUDGEMENT').replace('fine.','JUDGEMENT') for r in group]
            assert texts[0]==texts[1]
    datasets[name]=dict(rows=len(records),items=len(byitem),token_counts=dict(tokens),position_or_length_errors=bad,split_counts=dict(Counter(r['split'] for r in records)),tool_context_rows=sum('<tool_response>' in r['prompt_text'] for r in records))
checks['product_type_split_disjoint']=all(len(s)==1 for s in all_splits.values())
checks['all_stored_primary_positions_and_lengths_match']=all(not d['position_or_length_errors'] for d in datasets.values())
with np.load(DATA/'probe_directions.npz',allow_pickle=False) as p:
    weights={k:int(p[k]) for k in ['content_layer','e1_layer','e2_layer']}
    checks['saved_weights_finite_unit_norm']=all(np.isfinite(p[k]).all() and np.isclose(np.linalg.norm(p[k]),1,atol=1e-5) for k in ['content_w_mm','e1_w_mm','e2_w_mm'])
out=dict(checks=checks,datasets=datasets,saved_layers=weights,source_sha256=hashlib.sha256(source.encode()).hexdigest(),probe_sha256=hashlib.sha256((DATA/'probe_directions.npz').read_bytes()).hexdigest(),limitations=['Original full contrast activation arrays not found in local probes directory; saved weights cannot be re-fitted end-to-end here.','Synthetic tests verify the current helper formula and selection behavior, not provenance of the historical GPU execution.','Data integrity is not semantic validation of welfare labels.'],model_runs=0)
(OUT/'local_audit.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
assert all(checks.values())
