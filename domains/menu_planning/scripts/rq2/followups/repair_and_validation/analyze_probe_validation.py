"""Analyze the fixed diagnostic screen without fitting or changing any direction."""
import json,hashlib,csv
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'Sentient-Futures-Project-git/results/rq2/validation_v1'
OUT.mkdir(exist_ok=True)
raw=json.loads((ROOT/'validation_download/probe_scores.json').read_text())
protocol=json.loads((ROOT/'validation_protocol.json').read_text())
rows=raw['rows'];assert len(rows)==160 and len(protocol['selected_items'])==10
def auc(labels,scores):
    a=np.asarray([s for l,s in zip(labels,scores) if l==1]);b=np.asarray([s for l,s in zip(labels,scores) if l==0])
    return float(np.mean((a[:,None]>b)+.5*(a[:,None]==b)))
groups=[]
for kind in sorted({r['kind'] for r in rows}):
    for pos in sorted({r['position'] for r in rows if r['kind']==kind}):
        for question in sorted({r.get('question','none') for r in rows if r['kind']==kind and r['position']==pos}):
            rr=[r for r in rows if r['kind']==kind and r['position']==pos and r.get('question','none')==question]
            item_ids=sorted({r['item_id'] for r in rr})
            assert len(rr)==20 and len(item_ids)==10
            g=dict(kind=kind,position=pos,question=question,items=10,rows=20,metrics={})
            for probe in ('content','e1','e2'):
                pairs=np.array([[next(r['score_'+probe] for r in rr if r['item_id']==item and r['label']==label) for label in (1,0)] for item in item_ids])
                diff=pairs[:,0]-pairs[:,1]
                draws=np.random.default_rng(20261110).integers(0,10,(10000,10))
                sampled=pairs[draws]
                boot=np.mean((sampled[:,:,0,None]>sampled[:,None,:,1])+.5*(sampled[:,:,0,None]==sampled[:,None,:,1]),axis=(1,2))
                g['metrics'][probe]=dict(auroc=auc([r['label'] for r in rr],[r['score_'+probe] for r in rr]),paired_item_bootstrap_ci95=np.quantile(boot,[.025,.975]).tolist(),mean_paired_difference=float(diff.mean()),positive_pairs=int((diff>0).sum()),paired_differences=diff.tolist())
            groups.append(g)
out=dict(scope=protocol['scope'],selection_rule=protocol['selection_rule'],selected_items=protocol['selected_items'],environment=raw['environment'],human_review_verified=False,original_test_split_previously_inspected=True,new_training_or_sign_selection=False,groups=groups)
(OUT/'probe_diagnostic.json').write_text(json.dumps(out,indent=2))
(OUT/'probe_scores.json').write_text(json.dumps(raw,indent=2))
(OUT/'protocol.json').write_text(json.dumps(protocol,indent=2))
base=[json.loads(x) for x in (OUT.parents[0]/'contrast/contrast_base_items.jsonl').read_text(encoding='utf-8').splitlines()]
selected=[r for r in base if r['item_id'] in protocol['selected_items'].values()]
with (OUT/'selected_items_review_needed.csv').open('w',newline='',encoding='utf-8') as f:
    keys=['item_id','category','description_harmful','description_safe','source_note','review_status']
    writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
    for r in selected:writer.writerow({**{k:r.get(k,'') for k in keys[:-1]},'review_status':'Independent human review not established'})
for g in groups:print(g['kind'],g['position'],g['question'],{p:round(v['auroc'],3) for p,v in g['metrics'].items()})
print('Diagnostic saved to',OUT)
