"""CPU-only post-audit RQ2 analysis; never overwrites original research outputs."""
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

SEED = 20261106

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def first_reads(rows):
    first = {}
    for row in sorted(rows, key=lambda r: (int(r['tok_idx']), int(r['sub_idx']))):
        first.setdefault((row['run_id'], row['option_id']), row)
    return list(first.values())

def auc_summary(rows, score, n_boot=10000):
    # Pairwise wins by scenario permit exact weighted cluster resampling.
    scenarios = sorted({r['scenario_id'] for r in rows})
    positive = [np.array([float(r[score]) for r in rows if r['scenario_id'] == s and r['option_label'] == 'harmful']) for s in scenarios]
    negative = [np.array([float(r[score]) for r in rows if r['scenario_id'] == s and r['option_label'] == 'safe']) for s in scenarios]
    nh, ns = np.array(list(map(len, positive))), np.array(list(map(len, negative)))
    if not nh.sum() or not ns.sum():
        return dict(auroc=None, ci95=None, harmful=int(nh.sum()), safe=int(ns.sum()))
    wins = np.array([[np.sum(p[:, None] > n) + .5*np.sum(p[:, None] == n) for n in negative] for p in positive])
    weights = np.random.default_rng(SEED).multinomial(len(scenarios), np.full(len(scenarios), 1/len(scenarios)), size=n_boot)
    denominator = (weights @ nh) * (weights @ ns)
    valid = denominator > 0
    values = np.einsum('bi,ij,bj->b', weights[valid], wins, weights[valid], optimize=True) / denominator[valid]
    return dict(auroc=float(wins.sum()/(nh.sum()*ns.sum())), ci95=np.quantile(values,[.025,.975]).tolist(), harmful=int(nh.sum()), safe=int(ns.sum()), valid_bootstraps=int(valid.sum()))

def split_scenarios(rows):
    categories = defaultdict(set)
    for r in rows:
        categories[r['category']].add(r['scenario_id'])
    rng = random.Random(SEED)
    halves = [set(), set()]
    for index, category in enumerate(sorted(categories)):
        scenarios = sorted(categories[category])
        rng.shuffle(scenarios)
        cut = 3 if index % 2 == 0 else 2
        halves[0].update(scenarios[:cut])
        halves[1].update(scenarios[cut:])
    return halves

def run(data=None, n_boot=10000, output_dir=None):
    data = Path(data) if data else Path(__file__).resolve().parents[4] / 'results/rq2'
    output = Path(output_dir) if output_dir else data / 'repair_v1'
    output.mkdir(exist_ok=True)
    paths = [data/'benchmark_probe_scores_1200.csv', data/'t2/qwen35_positions_1200.jsonl', data/'qwen35_rq1_scores_1200.csv', data/'probe_directions.npz']
    rows = read_csv(paths[0])
    positions = [json.loads(line) for line in paths[1].read_text().splitlines() if line.strip()]
    rq1 = read_csv(paths[2])
    assert len({r['run_id'] for r in positions}) == len(positions)
    assert len({r['run_id'] for r in rq1}) == len(rq1)
    assert len({(r['run_id'],r['pos_type'],r['sub_idx']) for r in rows}) == len(rows)
    lookup = {r['run_id']:r for r in rq1}
    assert {r['run_id'] for r in positions} == set(lookup)
    for row in rows:
        truth = lookup[row['run_id']]
        assert all(row[k] == truth[k] for k in ('sample_id','scenario_id','prompt_condition','epoch'))
    assert all(np.isfinite(float(r[k])) for r in rows for k in ['score_content','score_e1','score_e2'])
    pure = {(r['run_id'],str(b['sub_idx'])):b['turn_summary_label'] for r in positions for b in r['pos_b']}
    a = first_reads([r for r in rows if r['pos_type']=='pos_a'])
    b = [dict(r, option_label=pure[r['run_id'],r['sub_idx']]) for r in rows if r['pos_type']=='pos_b' and pure[r['run_id'],r['sub_idx']] in ('harmful','safe')]
    c = [r for r in rows if r['pos_type']=='pos_c']
    report = dict(status='Exploratory post-audit analysis; not construct validation', seed=SEED, bootstrap_resamples=n_boot, input_sha256={str(p.relative_to(data)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, auroc={}, paired={}, thresholds=[], coverage={})
    grouped = defaultdict(list)
    for r in a:
        grouped[r['run_id']].append(r)
    for condition in ('neutral','ethical'):
        report['auroc'][condition] = {}
        for name, subset in [('first_read',a),('pure_persistence',b),('action',c)]:
            subset = [r for r in subset if r['prompt_condition']==condition]
            report['auroc'][condition][name] = {p:auc_summary(subset,'score_'+p,n_boot) for p in ('content','e1','e2')}
        pairs = []
        for run_id, rr in grouped.items():
            if rr[0]['prompt_condition'] != condition or {r['option_label'] for r in rr} != {'harmful','safe'}:
                continue
            pair = dict(run_id=run_id, scenario_id=rr[0]['scenario_id'])
            for p in ('content','e1','e2'):
                pair[p] = max(float(r['score_'+p]) for r in rr if r['option_label']=='harmful') - max(float(r['score_'+p]) for r in rr if r['option_label']=='safe')
            pairs.append(pair)
        report['paired'][condition] = dict(runs=len(pairs), mean_max_harm_minus_max_safe={p:float(np.mean([r[p] for r in pairs])) for p in ('content','e1','e2')}, fraction_positive={p:float(np.mean([r[p]>0 for r in pairs])) for p in ('content','e1','e2')})
        report['coverage'][condition] = dict(runs=sum(r['prompt_condition']==condition for r in positions), zero_position_runs=[r['run_id'] for r in positions if r['prompt_condition']==condition and not r['pos_a'] and not r['pos_b'] and r['pos_c'] is None], mixed_persistence_excluded=sum(r['prompt_condition']==condition and r['pos_type']=='pos_b' and pure[r['run_id'],r['sub_idx']]=='mixed' for r in rows))
    halves = split_scenarios(rows)
    assert len(halves[0]) == len(halves[1]) == 25 and not halves[0]&halves[1]
    report['calibration_halves'] = [sorted(s) for s in halves]
    decisions = []
    # Preserve option calibration as baseline; run-max-safe is a separate sensitivity.
    # Neither is a validated false-positive rate for internal moral evaluation.
    for unit in ('option','run_max_safe'):
        calibration = []
        for half in halves:
            safe = [r for r in a if r['prompt_condition']=='neutral' and r['option_label']=='safe' and r['scenario_id'] in half]
            if unit=='option':
                calibration.append([float(r['score_e1']) for r in safe])
            else:
                maxima = defaultdict(list)
                for r in safe:
                    maxima[r['run_id']].append(float(r['score_e1']))
                calibration.append([max(v) for v in maxima.values()])
        for target in (.01,.05,.10):
            tau = [float(np.quantile(v,1-target)) for v in calibration]
            for condition in ('neutral','ethical'):
                counts = Counter()
                for run_id, truth in lookup.items():
                    if truth['prompt_condition']!=condition or truth['outcome']!='harmful':
                        continue
                    harmful = [r for r in grouped.get(run_id,[]) if r['option_label']=='harmful']
                    threshold = tau[1] if truth['scenario_id'] in halves[0] else tau[0]
                    if not harmful:
                        category = 'missing_harmful_read'
                    elif truth['score_a'] not in ('0','1','2'):
                        category = 'missing_judge_score'
                    else:
                        above = max(float(r['score_e1']) for r in harmful)>threshold
                        category = ('above' if above else 'below') + ('_stated' if truth['score_a']=='2' else '_unstated')
                    counts[category] += 1
                    if unit=='option' and target==.05:
                        decisions.append(dict(run_id=run_id,condition=condition,category=category,threshold=threshold,maximum_harmful_read_score=max((float(r['score_e1']) for r in harmful),default=None)))
                safe_groups = defaultdict(list)
                for r in a:
                    if r['prompt_condition']==condition and r['option_label']=='safe':
                        safe_groups[r['run_id']].append(r)
                hits = total = 0
                for rr in safe_groups.values():
                    threshold = tau[1] if rr[0]['scenario_id'] in halves[0] else tau[0]
                    values = [float(r['score_e1']) for r in rr]
                    if unit=='run_max_safe':
                        values = [max(values)]
                    hits += sum(v>threshold for v in values)
                    total += len(values)
                report['thresholds'].append(dict(unit=unit,target_safe_exceedance=target,condition=condition,tau=tau,harmful_outcomes=sum(counts.values()),counts=dict(counts),heldout_safe_hits=hits,heldout_safe_total=total,heldout_safe_exceedance=hits/total))
    (output/'analysis.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    lines = ['# Repaired RQ2 analysis', '', 'Exploratory post-audit reanalysis. Original outputs are preserved. These scores do not establish whether moral evaluation occurred.', '', '## Corrected measurement', '', 'First reading per run and option; mixed persistence batches excluded; action positions analysed separately. Missing harmful readings stay missing, with no action-score substitution. AUROC intervals use 10,000 scenario-cluster bootstrap resamples (seed 20261106).', '', '| Condition | Position | E1 AUROC | 95% interval |', '|---|---|---:|---|']
    for condition, groups in report['auroc'].items():
        for name, values in groups.items():
            value = values['e1']
            lines.append(f"| {condition} | {name} | {value['auroc']:.4f} | {value['ci95'][0]:.4f} to {value['ci95'][1]:.4f} |")
    lines += ['', '## Harmful outcomes at the original option threshold', '', 'Thresholds are calibrated on deduplicated neutral safe options in opposite scenario halves. They are not a 5% run-level false-positive guarantee. Above means strictly greater than threshold; below includes equality. Stated means RQ1 Score A equals 2.', '', '| Condition | Above stated | Above unstated | Below unstated | Below stated | Missing reading | Total harmful |', '|---|---:|---:|---:|---:|---:|---:|']
    for result in report['thresholds']:
        if result['unit']=='option' and result['target_safe_exceedance']==.05:
            counts = result['counts']
            values = [counts.get(k,0) for k in ('above_stated','above_unstated','below_unstated','below_stated','missing_harmful_read')]
            lines.append('| '+result['condition']+' | '+' | '.join(map(str,values))+f" | {result['harmful_outcomes']} |")
    lines += ['', '## Interpretation and remaining checks', '', 'The corrected analysis does not rescue E1 as a moral-evaluation detector. Do not interpret below-threshold results as absent recognition or above-threshold unstated results as a proven monitoring gap. E2 action associations remain exploratory.', '', 'analysis.json includes 1%, 5% and 10% threshold sensitivities, held-out safe exceedance rates, separate run-maximum-safe calibration, input hashes, paired run comparisons and missingness. Paired comparisons are descriptive, without confidence intervals. Run-max-safe calibration aligns the aggregation operation but does not match the number or context of harmful readings, and does not validate the construct.', '', 'Before causal RQ3 interpretation: verify original-call versus final-replay token prefixes and cached layer positions; check matched backend probabilities if available; independently test probe specificity and context transfer. New prompts or corrected prefixes need only targeted new extraction.']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    with (output/'harmful_run_classification.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=list(decisions[0]))
        writer.writeheader(); writer.writerows(decisions)
    print(f'Repaired analysis saved to {output}; original outputs preserved.')
    return report

if __name__=='__main__':
    run()
