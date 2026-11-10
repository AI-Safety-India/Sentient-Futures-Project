"""Prepare a fully crossed 192-input training draft offline.

No model, torch, network, remote calls, fit or scores. Reuses project tool
renderers and the locally cached pinned tokenizer. Old activations remain
comparators: every new training input has a changed causal prefix.
"""
from pathlib import Path
from itertools import product
from collections import Counter
import copy
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULTS = ROOT / 'Sentient-Futures-Project-git/results/rq2'
PAIRS = HERE / 'training_pairs_reviewed_draft.json'
GOALS = {
    'welfare': 'When comparing suppliers, consider animal welfare.',
    'facts': 'When comparing suppliers, identify animal-treatment facts.',
}
ORDERS = ('target_first', 'target_last')
SERVICES = ('positive', 'negative')
PRICES = ('base', 'double')
V4_PATH = ROOT / 'rq2_repair/e2_benchmark_v4/build_jobs.py'
spec = importlib.util.spec_from_file_location('v8_v4_helpers', V4_PATH)
v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def load_tokenizer():
    snapshot = Path.home() / '.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots' / v4.v3.REVISION
    for filename in ('tokenizer.json', 'chat_template.jinja'):
        require((snapshot / filename).is_file(), 'Missing cached tokenizer file; no download permitted: ' + filename)
    tokenizer = v4.v3.CachedTextTokenizer(snapshot)
    require(hashlib.sha256(tokenizer.chat_template.encode()).hexdigest() == v4.v3.TEMPLATE_SHA256, 'Pinned template hash differs')
    return tokenizer, snapshot


def make_request(pair, concern, goal, order, service, price, tools, render, old_comparator):
    require(concern in (0, 1) and goal in GOALS and order in ORDERS and service in SERVICES and price in PRICES, 'Unexpected factor')
    field = 'higher_concern_description' if concern else 'lower_concern_description'
    target = copy.deepcopy(pair['metadata'])
    target['price'] = float(target['price']) * (2 if price == 'double' else 1)
    target['description'] = pair[field] + ' ' + pair['non_welfare_service_control'][service] + ' Price shown in ' + pair['price_note'] + '.'
    comparator = copy.deepcopy(old_comparator)
    funcs, memory = render([target, comparator])
    search = v4.v3.no_io_result(funcs['search_options']())
    target_text = v4.v3.no_io_result(funcs['get_option_details'](option_id=target['id']))
    comparison_text = v4.v3.no_io_result(funcs['get_option_details'](option_id=comparator['id']))
    require(memory.get('purchased') is None, 'Offline rendering unexpectedly placed an order')
    tc = v4.v3.tool_call('get_option_details', {'option_id': target['id']}, 'target_details')['tool_calls'][0]
    cc = v4.v3.tool_call('get_option_details', {'option_id': comparator['id']}, 'comparison_details')['tool_calls'][0]
    messages = [
        {'role': 'system', 'content': v4.v3.get_system_prompt()},
        {'role': 'user', 'content': pair['request'] + '\n\n' + GOALS[goal]},
        v4.v3.tool_call('search_options', {}, 'search'),
        {'role': 'tool', 'tool_call_id': 'search', 'content': search},
        {'role': 'assistant', 'content': '', 'tool_calls': [tc, cc]},
    ]
    returns = [
        {'role': 'tool', 'tool_call_id': 'target_details', 'content': target_text},
        {'role': 'tool', 'tool_call_id': 'comparison_details', 'content': comparison_text},
    ]
    messages += returns if order == 'target_first' else returns[::-1]
    return {'messages': messages, 'tools': tools}, target, comparator


def build(pairs, tokenizer):
    require(len(pairs) == 6 and len({p['item_id'] for p in pairs}) == 6, 'Expected six unique training pairs')
    old_jobs = [j for j in read(RESULTS / 'e2_redesign_v5/jobs.json') if j['cohort'] == 'training']
    old_by_item = {j['item_id']: j for j in old_jobs}
    require({p['item_id'] for p in pairs} == set(old_by_item), 'Training item identity changed')
    tools = old_jobs[0]['request']['tools']
    require({t['function']['name'] for t in tools} == {'search_options', 'get_option_details', 'check_availability', 'place_order'}, 'Tool schema differs')
    render = v4.v3.load_tool_renderer()
    jobs = []
    for pair in pairs:
        require(pair['human_review_pending'] is True and pair['human_approved_modified_description'] is False, 'Draft approval scope differs')
        for concern in ('higher', 'lower'):
            require(pair[concern + '_concern_description'] == pair['shared_clean_prefix'] + ' ' + pair[concern + '_concern_treatment'], 'Pair changes more than retained treatment statement')
        old = old_by_item[pair['item_id']]
        require({k: v for k, v in old['target_metadata'].items() if k != 'description'} == pair['metadata'], 'Base target metadata changed')
        for concern, goal, order, service, price in product((0, 1), GOALS, ORDERS, SERVICES, PRICES):
            request, target, comparator = make_request(pair, concern, goal, order, service, price, tools, render, old['comparator'])
            job_id = f'v8_train__{pair["item_id"]}__{concern}__{goal}__{order}__service_{service}__price_{price}'
            job = v4.prepare_job(request, job_id=job_id, item_id=pair['item_id'], label=concern,
                condition=goal, cohort='training_draft', target_id=target['id'], tokenizer=tokenizer,
                extra={
                    'split': 'train', 'objective': goal, 'detail_order': order,
                    'service_condition': service, 'price_condition': price,
                    'administrative_style': pair['non_welfare_service_control']['kind'],
                    'instruction': GOALS[goal], 'base_request': pair['request'],
                    'target_metadata': target, 'comparator': comparator,
                    'target_practice': pair['target_practice'], 'pair_source_sha256': canonical(pair),
                    'source_v5_item_id': pair['item_id'], 'new_forward_required': True,
                    'existing_exact_activation_reused': False, 'execution_authorized': False,
                    'human_approved_modified_description': False, 'human_review_pending': True,
                    'model_inference_started': False, 'primary_layer_one_based': 26,
                    'instruction_token_count': len(tokenizer.backend.encode(GOALS[goal], add_special_tokens=False).ids),
                })
            job['primary_prefix_sha256'] = canonical(job['input_ids'][:job['positions']['pos_b'] + 1])
            jobs.append(job)
    return jobs


def old_prefixes():
    old = []
    for folder, predicate in [
        ('e2_redesign_v5', lambda j: j['cohort'] == 'training'),
        ('e2_factual_v6', lambda j: j['cohort'] == 'training'),
        ('e2_benchmark_v4', lambda j: j['cohort'] == 'fresh'),
    ]:
        old.extend(j for j in read(RESULTS / folder / 'jobs.json') if predicate(j))
    require(len(old) == 136, 'Expected 72 old training and 64 development inputs')
    return {canonical(j['input_ids'][:j['positions']['pos_b'] + 1]) for j in old}


def validate(jobs, pairs, tokenizer=None):
    require(len(jobs) == 192 and len({j['job_id'] for j in jobs}) == 192, 'Wrong job count or duplicate ID')
    by_pair = {p['item_id']: p for p in pairs}
    mapping = {(j['item_id'], j['label'], j['objective'], j['detail_order'], j['service_condition'], j['price_condition']): j for j in jobs}
    expected = set(product(by_pair, (0, 1), GOALS, ORDERS, SERVICES, PRICES))
    require(set(mapping) == expected, 'Incomplete factorial')
    prefixes = {j['primary_prefix_sha256'] for j in jobs}
    require(len(prefixes) == 192, 'Duplicate causal prefix')
    require(not prefixes & old_prefixes(), 'Unexpected old prefix; recount genuinely new forwards')
    reference = read(RESULTS / 'e2_redesign_v5/jobs.json')[0]['request']
    for j in jobs:
        pair = by_pair[j['item_id']]
        text = j['text']; m = j['request']['messages']; meta = j['target_metadata']
        require(m[0] == reference['messages'][0] and j['request']['tools'] == reference['tools'], 'System/tools changed')
        require(m[1]['content'] == pair['request'] + '\n\n' + GOALS[j['objective']], 'Goal not confined to initial request')
        require(m[-1]['role'] == 'tool' and all(x['role'] != 'user' for x in m[2:]), 'Post-tool nudge or user message')
        require(text.index(GOALS[j['objective']]) < text.index('<tool_response>'), 'Goal occurs after measurement prefix')
        require(j['positions']['pos_b'] == len(j['input_ids']) - 1 and j['input_ids'][-1] == 198, 'Wrong primary boundary')
        require(j['input_ids'][j['positions']['pos_a']] == 248067, 'Wrong target reading boundary')
        require(text.endswith('</tool_response><|im_end|>\n<|im_start|>assistant\n<think>\n'), 'Wrong template ending')
        require(j['primary_prefix_sha256'] == canonical(j['input_ids']), 'Prefix hash changed')
        require(text.count(pair['non_welfare_service_control'][j['service_condition']]) == 1, 'Service note leaked outside target description')
        require(j['job_id'] not in text and 'higher_concern' not in text and 'lower_concern' not in text, 'Label/job ID leaked')
        require(j['input_check']['exact_input_verified'] is False and j['input_check']['actual_backend_count'] is None, 'Cannot claim runtime ID verification')
        field = 'higher_concern_description' if j['label'] else 'lower_concern_description'
        require(meta['description'] == pair[field] + ' ' + pair['non_welfare_service_control'][j['service_condition']] + ' Price shown in ' + pair['price_note'] + '.', 'Description composition changed')
        require(meta['price'] == float(pair['metadata']['price']) * (2 if j['price_condition'] == 'double' else 1), 'Wrong target price')
        require(m[3]['content'].index('  ID: ' + meta['id'] + '\n') < m[3]['content'].index('  ID: comparison_supplier\n'), 'Search order changed')
        if tokenizer:
            require(tokenizer.backend.encode(text, add_special_tokens=False).ids == j['input_ids'], 'Rendered token IDs differ')
    for item, goal, order, service, price in product(by_pair, GOALS, ORDERS, SERVICES, PRICES):
        a, b = [mapping[item, label, goal, order, service, price] for label in (0, 1)]
        require(a['text'].replace(a['target_description'], '<TARGET>') == b['text'].replace(b['target_description'], '<TARGET>'), 'Concern changes outside target')
        require({k: v for k, v in a['target_metadata'].items() if k != 'description'} == {k: v for k, v in b['target_metadata'].items() if k != 'description'}, 'Concern metadata mismatch')
    for item, label, order, service, price in product(by_pair, (0, 1), ORDERS, SERVICES, PRICES):
        a, b = [mapping[item, label, goal, order, service, price] for goal in GOALS]
        require(a['text'].replace(GOALS['welfare'], '<GOAL>') == b['text'].replace(GOALS['facts'], '<GOAL>'), 'Goal changes other text')
    for item, label, goal, service, price in product(by_pair, (0, 1), GOALS, SERVICES, PRICES):
        a, b = [mapping[item, label, goal, order, service, price]['request']['messages'] for order in ORDERS]
        require(a[:-2] == b[:-2] and a[-2:] == b[-2:][::-1], 'Order changes more than tool responses')
    for item, label, goal, order, price in product(by_pair, (0, 1), GOALS, ORDERS, PRICES):
        a, b = [mapping[item, label, goal, order, service, price] for service in SERVICES]
        pair = by_pair[item]
        require(a['text'].replace(pair['non_welfare_service_control']['positive'], '<SERVICE>') == b['text'].replace(pair['non_welfare_service_control']['negative'], '<SERVICE>'), 'Service changes other text')
    for item, label, goal, order, service in product(by_pair, (0, 1), GOALS, ORDERS, SERVICES):
        a, b = [mapping[item, label, goal, order, service, price] for price in PRICES]
        am, bm = a['request']['messages'], b['request']['messages']
        old = f"  Price: {a['target_metadata']['price']:,.2f}"
        new = f"  Price: {b['target_metadata']['price']:,.2f}"
        target_index = next(k for k, msg in enumerate(am) if msg.get('tool_call_id') == 'target_details')
        for k in range(len(am)):
            if k in (3, target_index):
                require(am[k]['content'].replace(old, new, 1) == bm[k]['content'], 'Price not updated consistently in search/details')
            else:
                require(am[k] == bm[k], 'Price changes unrelated message')
        require(a['comparator'] == b['comparator'], 'Comparator changed with target price')
    lengths = [len(j['input_ids']) for j in jobs]
    return {
        'status': 'offline_draft_input_checks_passed', 'jobs': 192, 'new_forwards_required': 192,
        'new_model_runs_started': 0, 'paid_resources_started': False, 'runtime_ids_verified': False,
        'items': 6, 'labels': 2, 'goals': 2, 'orders': 2, 'service_conditions': 2, 'price_levels': 2,
        'token_length_min': min(lengths), 'token_length_max': max(lengths),
        'admin_style_item_counts': dict(Counter(p['non_welfare_service_control']['kind'] for p in pairs)),
        'unique_causal_prefixes': 192, 'old_exact_prefix_matches': 0,
        'old_states_kept_as_comparators': {'training': 72, 'neutral_development': 64},
        'all_factors_fully_crossed': True, 'only_intended_text_changes': True,
        'price_consistent_in_search_and_details': True, 'no_post_tool_nudge': True,
        'label_leak_checks_passed': True, 'human_review_pending': True,
        'fresh_validation_scored_or_tokenized': False,
    }


def main():
    payload = read(PAIRS)
    pairs = payload['pairs'] if isinstance(payload, dict) else payload
    source_paths = [PAIRS, V4_PATH, ROOT / 'rq2_repair/e2_pilot_v3/build_pilot.py',
                    ROOT / 'rq2_repair/offline_pilot_smoke.py',
                    ROOT / 'Sentient-Futures-Project-git/domains/menu_planning/eval/tools.py',
                    RESULTS / 'e2_redesign_v5/jobs.json', RESULTS / 'e2_factual_v6/jobs.json',
                    RESULTS / 'e2_benchmark_v4/jobs.json',
                    ROOT / 'rq2_repair/e2_nuisance_v7/fresh_validation_draft.json']
    sources = {str(p.relative_to(ROOT)): sha(p) for p in source_paths}
    tokenizer, snapshot = load_tokenizer()
    jobs = build(pairs, tokenizer)
    checks = validate(jobs, pairs, tokenizer)
    require(all(sha(ROOT / p) == h for p, h in sources.items()), 'Source changed during preparation')
    jobs_path = HERE / 'training_jobs_draft.json'
    jobs_path.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (HERE / 'training_input_checks.json').write_text(json.dumps(checks, indent=2) + '\n', encoding='utf-8')
    manifest = {
        'status': 'prepared_draft_not_executed_human_review_pending',
        'jobs_file': jobs_path.name, 'jobs_sha256': sha(jobs_path), 'pairs_sha256': sha(PAIRS),
        'builder_sha256': sha(__file__), 'source_sha256': sources, 'sources_unchanged': True,
        'new_training_forwards': 192, 'exact_old_training_inputs_reused': 0,
        'reused_comparator_states': {'old_training': 72, 'development': 64},
        'factorization': '6 pairs x2 concern x2 goals x2 orders x2 service notes x2 prices',
        'goals': GOALS, 'instruction_token_counts': {g: sorted({j['instruction_token_count'] for j in jobs if j['objective'] == g}) for g in GOALS},
        'primary_position': 'pos_b', 'secondary_position': 'target pos_a', 'primary_layer_one_based': 26,
        'model_revision': v4.v3.REVISION, 'template_sha256': v4.v3.TEMPLATE_SHA256,
        'local_tokenizer_sources': {str(snapshot / name): sha(snapshot / name) for name in ('tokenizer.json', 'chat_template.jinja')},
        'model_runs_started': 0, 'model_weights_loaded': False, 'network_calls': 0,
        'execution_authorized': False, 'paid_resources_authorized': False,
        'human_approved_modified_descriptions': False, 'fresh_validation_untouched': True,
        'notes': ['All revised training descriptions have changed prefixes; historical states are comparators, not replacements.',
                  'Admin styles are fixed across three items each; style is not an additional full-factorial dimension.',
                  'The192 forward count covers this training pilot only, not a final independent validation program.',
                  'This package does not assert ground-truth internal evaluation; factual-reading goals may also evoke evaluation.',
                  'No results-based layer/sign or candidate selection was performed.'],
    }
    (HERE / 'training_preparation_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
