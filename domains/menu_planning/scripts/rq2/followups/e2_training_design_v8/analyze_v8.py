"""Offline v8 fixed-candidate analysis. No inference, network, or fresh examples.

Execution requires the completed 192-state producer package. The sole candidate
is fit on those states, never on the 64 previously inspected development states.
Historical weights, reports, input manifests and activation files are read-only.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
from itertools import product
import json
from pathlib import Path

import numpy as np

from fit_direction import fit_direction

MODEL = 'Qwen/Qwen3.5-9B'
REVISION = 'c202236235762e1c871ad0ccb60c8ee5ba337b9a'
TEMPLATE = 'a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
JOBS_SHA = '95c8232f06b6bdc22e8acddbaa8e211f2d9c23b76881c30c2de82881f0ebf569'
PAIRS_SHA = '92953e2d5a94efca30e03212cf43666ff71a43c343d363a4c86875970bc25fb0'
FIT_SHA = '9538540c2b330afdf2ec13868eddf998f756f79fb63573e73a16d210f2923415'
WEIGHTS_SHA = 'bcd29390210350dd707a37db85b83ce21ab5db2fa55f74ec9fa0b5ab64679749'
CONDITIONS = ('base', 'price', 'rating', 'order')
CANDIDATES = ('original_e2', 'v5', 'v6', 'v7_corrected_v6', 'v8')
EXCLUDED_REINDEER = 'fresh_v4_07'


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


def array_sha(value):
    return hashlib.sha256(value.tobytes()).hexdigest()


def unique_map(records, key='job_id'):
    mapping = {}
    for record in records:
        require(record[key] not in mapping, 'Duplicate ' + key)
        mapping[record[key]] = record
    return mapping


def cosine(a, b):
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / norm) if norm > 1e-12 else None


def validate_selected_record(job, record, state, table_job_sha, table_ids_sha):
    """Bind each selected row to a frozen input and producer-observed IDs."""
    require(record['job_id'] == job['job_id'], 'Selected row job differs')
    require(record['job_sha256'] == table_job_sha == canonical_sha(job), 'Selected job hash differs')
    ids_hash = canonical_sha(job['input_ids'])
    require(record['input_ids_sha256'] == table_ids_sha == ids_hash, 'Selected input hash differs')
    require(record['primary_prefix_sha256'] == job['primary_prefix_sha256'] == ids_hash,
            'Causal prefix hash differs')
    require(record['positions'] == job['positions'], 'Selected measurement position differs')
    require(job['positions']['pos_b'] == len(job['input_ids']) - 1, 'pos_b is not final input token')
    require(job['split'] == 'train' and job['primary_layer_one_based'] == 26, 'Wrong training split/layer')
    require(state.shape == (4096,) and state.dtype == np.float16 and np.isfinite(state).all(),
            'Invalid selected activation shape/dtype/values')
    require(array_sha(state) == record['selected_array_sha256'], 'Selected activation row hash differs')
    check = record['input_check']
    require(check.get('exact_input_verified') is True and check.get('token_ids_match') is True,
            'Producer did not verify exact input IDs')
    require(check.get('expected_ids_sha256') == ids_hash and check.get('actual_backend_count') == len(job['input_ids']),
            'Producer input verification has different input/count')
    for field in ('cache_payload_sha256', 'cache_manifest_sha256'):
        value = record.get(field)
        require(isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value),
                'Missing producer provenance: ' + field)


def validate_execution_evidence(manifest, lock, release, jobs):
    """Reject a different model or a release/lock for different reviewed inputs."""
    identity = manifest.get('model_identity', {})
    require(identity.get('loaded_model_verified') is True, 'Loaded model identity differs: loaded_model_verified')
    for field, expected in {'model_revision': REVISION,
                            'model_dtype': 'bfloat16', 'attention': 'sdpa',
                            'model_class': 'Qwen3_5ForConditionalGeneration'}.items():
        require(identity.get(field) == expected, 'Loaded model identity differs: ' + field)
    require(lock.get('job_sha256') == {job['job_id']: canonical_sha(job) for job in jobs},
            'Execution lock per-job hashes differ')
    for field, expected in {'model_id': MODEL, 'model_revision': REVISION, 'template_sha256': TEMPLATE,
                            'primary_position': 'pos_b', 'primary_layer_one_based': 26}.items():
        require(lock.get(field) == expected, 'Execution lock measurement differs: ' + field)
    require(release.get('schema') == 'rq2_v8_review_release_v1', 'Unknown review release')
    require(release.get('source_files', {}).get('training_jobs_draft.json') == JOBS_SHA and
            release.get('source_files', {}).get('training_pairs_reviewed_draft.json') == PAIRS_SHA,
            'Review release has different reviewed jobs/pairs')
    require(release.get('pilot_authorized_by_user') is True and release.get('maximum_new_forwards') == 192
            and release.get('paid_resources_authorized') is False and release.get('remaining_label_reviews') == 0,
            'Review release scope is incomplete or different')
    reviewed = unique_map(release['items'], 'item_id')
    require(set(reviewed) == {job['item_id'] for job in jobs}, 'Reviewed training items differ')
    require(sum(row.get('human_annotation') is True for row in reviewed.values()) == 2 and
            sum(row.get('human_annotation') is False for row in reviewed.values()) == 4,
            'Expected two human approvals and four delegated reviews')
    require(all(row.get('decision') in ('approved', 'accepted_for_bounded_pilot_by_delegated_agent')
                for row in reviewed.values()), 'An item review is not accepted')


def load_training(root, design):
    """Load only verified selected states; never reconstruct provenance."""
    jobs_path = design / 'training_jobs_draft.json'
    require(sha(jobs_path) == JOBS_SHA, 'Frozen v8 jobs changed')
    require(sha(design / 'training_pairs_reviewed_draft.json') == PAIRS_SHA, 'Frozen v8 pairs changed')
    jobs = read(jobs_path)
    jobs_by_id = unique_map(jobs)
    require(len(jobs) == 192, 'Expected 192 frozen training jobs')
    # A remote copy must contain the exact bytes, not regenerated near-equivalents.
    require(sha(root / 'training_jobs_draft.json') == JOBS_SHA, 'Executed jobs differ from frozen design')
    status = read(root / 'run_status.json')
    require(status.get('state') == 'complete' and status.get('completed') == 192 and status.get('total') == 192,
            'Expected all 192 forwards complete')
    require(status.get('jobs_sha256') == JOBS_SHA and status.get('model_revision') == REVISION,
            'Completed run identity differs')
    require(status.get('generation_calls') == 0 and status.get('forward_attempts_total') == 192,
            'Expected exactly 192 bounded forward attempts and no generation')
    manifest_path = root / 'training_pos_b_l26.json'
    manifest = read(manifest_path)
    path = root / 'training_pos_b_l26.npz'
    for field, expected in {
        'schema': 'v8-selected-pos-b-l26-v1', 'jobs_sha256': JOBS_SHA,
        'model_id': MODEL, 'model_revision': REVISION, 'template_sha256': TEMPLATE,
        'backend': 'transformers', 'model_dtype': 'bfloat16', 'attention': 'sdpa', 'dtype': 'float16',
        'layer_one_based': 26, 'position': 'pos_b',
        'hidden_state_semantics': 'post_decoder_layer_excludes_embeddings',
    }.items():
        require(manifest.get(field) == expected, 'Selected manifest mismatch: ' + field)
    require(manifest.get('payload_sha256') == sha(path), 'Selected payload bytes differ')
    versions = manifest.get('backend_versions', {})
    require(versions == status.get('backend_versions') and all(versions.get(k) for k in ('torch', 'transformers', 'numpy')),
            'Missing/inconsistent producer backend versions')
    lock_path, ledger_path = root / 'execution_manifest.json', root / 'forward_ledger.json'
    require(manifest.get('execution_manifest_sha256') == sha(lock_path), 'Execution lock hash differs')
    require(manifest.get('forward_ledger_sha256') == sha(ledger_path), 'Forward ledger hash differs')
    lock, ledger = read(lock_path), read(ledger_path)
    release_path = root / 'review_release_v8.json'
    require(sha(release_path) == lock.get('label_review_sha256') == sha(design / 'review_release_v8.json'),
            'Executed review release differs from local approved release')
    validate_execution_evidence(manifest, lock, read(release_path), jobs)
    require(lock.get('jobs_sha256') == JOBS_SHA and lock.get('expected_backend_versions') == versions,
            'Execution lock has different jobs/backend')
    require(lock.get('maximum_forward_calls') == 192 and lock.get('execution_authorized') is True
            and lock.get('paid_resources_authorized') is False and lock.get('fresh_validation_authorized') is False,
            'Execution lock scope differs')
    require(lock.get('free_runtime_evidence', {}).get('explicitly_free') is True, 'Missing explicit free-runtime record')
    require(set(ledger) == set(jobs_by_id), 'Forward ledger has missing/extra jobs')
    for job_id, entry in ledger.items():
        require(entry.get('state') == 'complete' and entry.get('attempts') == 1
                and entry.get('job_sha256') == canonical_sha(jobs_by_id[job_id]), 'Forward ledger completion/identity differs')
    records = unique_map(manifest['records'])
    require(set(records) == set(jobs_by_id), 'Selected records missing/extra jobs')
    states = []
    with np.load(path, allow_pickle=False) as data:
        require(set(data.files) == {'job_ids', 'hidden_states', 'input_ids_sha256', 'job_sha256'}, 'Unexpected selected payload schema')
        ids = data['job_ids'].tolist()
        require(len(ids) == 192 and len(set(ids)) == 192 and set(ids) == set(jobs_by_id), 'Duplicate/missing selected rows')
        require(data['hidden_states'].shape == (192, 4096), 'Wrong selected payload shape')
        require(data['input_ids_sha256'].shape == data['job_sha256'].shape == (192,), 'Wrong selected hash table shape')
        for n, job_id in enumerate(ids):
            job, record, state = jobs_by_id[job_id], records[job_id], data['hidden_states'][n]
            validate_selected_record(job, record, state, str(data['job_sha256'][n]), str(data['input_ids_sha256'][n]))
            coordinate = tuple(job[k] for k in ('item_id', 'objective', 'detail_order', 'price_condition', 'service_condition', 'label'))
            states.append((coordinate, state.astype(np.float64)))
    return states, versions, {'selected_manifest_sha256': sha(manifest_path),
                             'selected_payload_sha256': sha(path), 'records': manifest['records'],
                             'execution_manifest_sha256': sha(lock_path), 'forward_ledger_sha256': sha(ledger_path),
                             'review_release_sha256': sha(release_path), 'model_identity': manifest['model_identity'],
                             'provenance_scope': 'Producer manifest and selected per-row hashes; original full caches remain on producer unless separately transferred.'}


def independently_verify_fit(records, direction, center, fit_report):
    """Independent signed-sum formula, unlike the estimator's matched loops."""
    matrix = np.stack([value for _, value in records]).astype(np.float64)
    signs = np.array([(1 if k[1] == 'welfare' else -1) * (1 if k[5] == 1 else -1)
                      for k, _ in records], dtype=float)
    raw = signs @ matrix / 48.0
    reference = raw / np.linalg.norm(raw)
    require(np.allclose(raw, fit_report['raw_interaction'], rtol=1e-12, atol=1e-10), 'Independent raw interaction differs')
    require(np.allclose(reference, direction, rtol=1e-12, atol=1e-12), 'Independent normalized direction differs')
    require(np.allclose(matrix.mean(axis=0), center, rtol=1e-12, atol=1e-12), 'Independent center differs')
    return {'method': 'signed sum of all 192 states / 48, with fixed label x goal signs',
            'raw_max_absolute_error': float(np.max(np.abs(raw - fit_report['raw_interaction']))),
            'direction_max_absolute_error': float(np.max(np.abs(reference - direction))), 'passed': True}


def training_interaction_strata(records, direction):
    """Expose training heterogeneity without refitting per-stratum directions."""
    states = dict(records)
    groups = defaultdict(list)
    for key, value in records:
        item, goal, order, price, service, label = key
        if goal != 'welfare' or label != 1:
            continue
        effect = (value - states[item, 'welfare', order, price, service, 0]) - (
            states[item, 'facts', order, price, service, 1] - states[item, 'facts', order, price, service, 0])
        for group in (f'order|{order}', f'price|{price}', f'service|{service}', f'item_order|{item}|{order}'):
            groups[group].append(effect)
    result = {}
    for group, vectors in sorted(groups.items()):
        matrix = np.stack(vectors)
        projections = matrix @ direction
        mean = matrix.mean(axis=0)
        result[group] = {'contrasts': len(vectors), 'mean_vector_norm': float(np.linalg.norm(mean)),
                         'mean_projection': float(projections.mean()), 'median_projection': float(np.median(projections)),
                         'positive_contrasts': int(np.sum(projections > 0)), 'negative_contrasts': int(np.sum(projections < 0)),
                         'zero_contrasts': int(np.sum(projections == 0)), 'cosine_with_pooled_direction': cosine(mean, direction)}
    return {'groups': result, 'interpretation': 'In-sample heterogeneity, using the single pooled fixed direction. No per-group candidate is fit or selected.'}


def summarize_scores(scores, expected_items=None):
    """scores[item][condition,label]. Center-free paired/control diagnostics."""
    items = sorted(scores)
    require(bool(items) and (expected_items is None or len(items) == expected_items), 'Unexpected development item count')
    required = set(product(CONDITIONS, (0, 1)))
    for item in items:
        require(set(scores[item]) == required, 'Incomplete/extra development conditions or labels')
        require(all(np.isfinite(value) for value in scores[item].values()), 'Nonfinite development score')
    summaries, controls = {}, {}
    for condition in CONDITIONS:
        higher = np.array([scores[i][condition, 1] for i in items])
        lower = np.array([scores[i][condition, 0] for i in items])
        gaps = higher - lower
        summaries[condition] = {
            'items': len(items), 'positive_pairs': int(np.sum(gaps > 0)),
            'negative_pairs': int(np.sum(gaps < 0)), 'ties': int(np.sum(gaps == 0)),
            'mean_pair_gap': float(gaps.mean()), 'median_pair_gap': float(np.median(gaps)),
            'pair_gaps': dict(zip(items, map(float, gaps))),
            'auroc': float(np.mean((higher[:, None] > lower) + .5 * (higher[:, None] == lower))),
        }
    for condition in CONDITIONS[1:]:
        shifts = {f'{i}|{l}': scores[i][condition, l] - scores[i]['base', l] for i in items for l in (0, 1)}
        common = {i: .5 * (shifts[f'{i}|0'] + shifts[f'{i}|1']) for i in items}
        changes = {i: summaries[condition]['pair_gaps'][i] - summaries['base']['pair_gaps'][i] for i in items}
        magnitude = float(np.mean(np.abs(list(shifts.values()))))
        controls[condition] = {
            'mean_common_offset': float(np.mean(list(common.values()))),
            'mean_absolute_common_offset': float(np.mean(np.abs(list(common.values())))),
            'mean_absolute_variant_shift': magnitude,
            'mean_pair_gap_change': float(np.mean(list(changes.values()))),
            'mean_absolute_pair_gap_change': float(np.mean(np.abs(list(changes.values())))),
            'pair_sign_changes': int(sum(np.sign(summaries[condition]['pair_gaps'][i]) != np.sign(summaries['base']['pair_gaps'][i]) for i in items)),
            'common_offsets': common, 'pair_gap_changes': changes, 'variant_shifts': shifts,
            'positive_welfare_mean_exceeds_nuisance_magnitude': bool(summaries['base']['mean_pair_gap'] > 0 and summaries['base']['mean_pair_gap'] > magnitude),
        }
    return {'pair_summaries': summaries, 'nuisance_effects': controls,
            'descriptive_7_of_8_flags': {c: summaries[c]['positive_pairs'] >= 7 for c in CONDITIONS} if len(items) == 8 else None,
            'interpretation': 'Previously inspected development data. Flags are descriptive continuity checks, not original H2 criteria or validation.'}


def score_states(states, direction, center):
    return {item: {key: float(np.dot(value - center, direction)) for key, value in cells.items()}
            for item, cells in states.items()}


def _vector(value):
    result = np.asarray(value, dtype=np.float64)
    require(result.shape == (4096,) and np.isfinite(result).all(), 'Invalid saved direction/center')
    return result


def load_development_and_comparators(base, versions):
    """Read and reproduce existing results only; no estimation on development."""
    v4, v5, v6, v7 = (base / name for name in ('e2_benchmark_v4', 'e2_redesign_v5', 'e2_factual_v6', 'e2_nuisance_v7'))
    paths = []
    def remember(path):
        paths.append(path)
        return path
    jobs = read(remember(v4 / 'jobs.json'))
    selected = read(remember(v4 / 'selected_layer_manifest.json'))
    original_report = read(remember(v4 / 'benchmark_validation.json'))
    require(sha(v4 / 'jobs.json') == selected['jobs_sha256'] == original_report['core_jobs_sha256'], 'Historical development inputs differ')
    require(sha(remember(v4 / 'selected_layers_1_26.npz')) == selected['selected_npz_sha256'], 'Historical development states differ')
    require(selected['position_order'] == ['pos_b', 'pos_a'] and selected['layers_one_based'] == [1, 26], 'Historical selection semantics differ')
    # Backend mismatches block the controlled comparison, rather than silently mixing.
    for folder in (v4, v5, v6):
        oldstatus = read(remember(folder / 'run_status.json'))
        oldversions = oldstatus.get('backend_versions', {})
        require(oldstatus.get('state') == 'complete' and
                all(oldversions.get(k) == versions.get(k) for k in ('torch', 'transformers', 'numpy')) and
                oldversions.get('model_dtype') == 'bfloat16' and oldversions.get('attention') == 'sdpa',
                'Historical training/development producer backend differs: ' + folder.name)
    weights = remember(base / 'probe_directions.npz')
    require(sha(weights) == WEIGHTS_SHA, 'Original weights changed')
    probes = {}
    with np.load(weights, allow_pickle=False) as data:
        require(int(data['e2_layer']) == 26 and int(data['content_lr_layer']) == 26, 'Original layer identity differs')
        probes['original_e2'] = (_vector(data['e2_w_mm']), _vector(data['e2_mid_mm']))
        content = _vector(data['content_w_lr'])
    reports = {}
    for name, folder, filename in (('v5', v5, 'development_analysis.json'), ('v6', v6, 'factual_analysis.json')):
        report = read(remember(folder / filename)); reports[name] = report
        require(sha(remember(folder / 'jobs.json')) == report['jobs_sha256'], 'Historical candidate jobs changed')
        with np.load(remember(folder / f'candidate_{name}_direction.npz'), allow_pickle=False) as data:
            require(int(data['layer_one_based']) == 26 and str(data['jobs_sha256']) == report['jobs_sha256'], 'Historical candidate identity differs')
            require(array_sha(data['direction']) == report['fit']['direction_sha256'], 'Historical candidate direction changed')
            probes[name] = (_vector(data['direction']), _vector(data['center']))
    comparison = read(remember(v7 / 'local_comparison.json'))
    corrected = remember(v7 / 'nuisance_corrected_candidates.npz')
    require(sha(corrected) == comparison['corrected_candidates_sha256'], 'Corrected v6 candidate changed')
    with np.load(corrected, allow_pickle=False) as data:
        probes['v7_corrected_v6'] = (_vector(data['v6_projected_unit']), _vector(data['v6_center']))
    require(np.array_equal(probes['v7_corrected_v6'][1], probes['v6'][1]), 'Corrected v6 center differs')
    records = unique_map(selected['records'])
    payloads = unique_map(original_report['cache_evidence'])
    oldrows = unique_map([row for row in reports['v6']['rows'] if row['position'] == 'pos_b'])
    dev = [job for job in jobs if job['cohort'] == 'fresh']
    require(len(dev) == 64 and len(unique_map(dev)) == 64, 'Expected exact 64 historical neutral development jobs')
    states, identifiers = defaultdict(dict), {}
    with np.load(v4 / 'selected_layers_1_26.npz', allow_pickle=False) as data:
        for job in dev:
            value = data[job['job_id']]
            require(value.shape == (2, 2, 4096) and value.dtype == np.float16 and np.isfinite(value).all(), 'Invalid historical selected state')
            record = records[job['job_id']]
            require(array_sha(value) == record['selected_array_sha256'] and record['original_npz_sha256'] == payloads[job['job_id']]['payload_sha256'], 'Historical selected provenance differs')
            key = (job['condition'], job['label'])
            require(key not in states[job['item_id']], 'Duplicate historical development coordinate')
            state = value[0, 1].astype(np.float64)
            states[job['item_id']][key] = state
            identifiers[job['item_id'], *key] = job['job_id']
            for name, field in (('original_e2', 'original_e2_l26'), ('v5', 'candidate_v5_l26'), ('v6', 'candidate_v6_l26')):
                direction, center = probes[name]
                require(abs(float(np.dot(state - center, direction)) - oldrows[job['job_id']][field]) < 1e-8,
                        'Historical score reproduction mismatch: ' + name)
    require(EXCLUDED_REINDEER in states and len(states) == 8, 'Expected all eight historical families including reindeer')
    corrected_summary = summarize_scores(score_states(states, *probes['v7_corrected_v6']), 8)
    for condition in CONDITIONS:
        previous = comparison['candidates']['v6']['projected_unit']['pair_summaries'][condition]
        reproduced = corrected_summary['pair_summaries'][condition]
        require(reproduced['positive_pairs'] == previous['positive_pairs'] and abs(reproduced['auroc'] - previous['auroc']) < 1e-12,
                'Historical corrected v6 summary mismatch')
        require(all(abs(gap - previous['pair_gaps'][item]) < 1e-8 for item, gap in reproduced['pair_gaps'].items()), 'Historical corrected v6 gaps differ')
    return dict(states), identifiers, probes, content, {str(p.resolve()): sha(p) for p in paths}


def comparison_deltas(reports):
    """Descriptive changes against every frozen comparator, not selection."""
    candidate = reports['v8']
    result = {}
    for name in CANDIDATES[:-1]:
        old = reports[name]
        result[name] = {
            'pairs': {condition: {field: candidate['pair_summaries'][condition][field] - old['pair_summaries'][condition][field]
                                   for field in ('positive_pairs', 'auroc', 'mean_pair_gap', 'median_pair_gap')}
                      for condition in CONDITIONS},
            'nuisance': {condition: {field: candidate['nuisance_effects'][condition][field] - old['nuisance_effects'][condition][field]
                                      for field in ('mean_absolute_variant_shift', 'mean_absolute_common_offset', 'mean_absolute_pair_gap_change', 'pair_sign_changes')}
                         for condition in CONDITIONS[1:]},
        }
    return result


def write_once_json(path, value):
    """Idempotent reproduction is allowed; different previous output is preserved."""
    text = json.dumps(value, indent=2, allow_nan=False)
    if path.exists():
        require(read(path) == value, 'Refusing different analysis overwrite: ' + str(path))
    else:
        path.write_text(text, encoding='utf-8')


def analyze(root, design, base):
    root, design, base = map(Path, (root, design, base))
    require(root.resolve() == (base / 'e2_training_design_v8').resolve(), 'Output must be the separate v8 results directory')
    require(root.is_dir(), 'No completed v8 results directory')
    require(sha(Path(__file__).with_name('fit_direction.py')) == FIT_SHA, 'Frozen estimator changed')
    records, versions, evidence = load_training(root, design)
    states, identifiers, probes, original_content, sources = load_development_and_comparators(base, versions)
    require(not {key[0] for key, _ in records} & set(states), 'Training/development item overlap')
    direction, center, fit_report = fit_direction(records)
    independent = independently_verify_fit(records, direction, center, fit_report)
    probes['v8'] = direction, center
    reports, sensitivity, rows = {}, {}, []
    for name in CANDIDATES:
        scores = score_states(states, *probes[name])
        reports[name] = summarize_scores(scores, 8)
        sensitivity[name] = summarize_scores({i: s for i, s in scores.items() if i != EXCLUDED_REINDEER}, 7)
        for item, cells in scores.items():
            for (condition, label), value in cells.items():
                rows.append({'candidate': name, 'job_id': identifiers[item, condition, label], 'item_id': item,
                             'condition': condition, 'label': label, 'position': 'pos_b', 'layer_one_based': 26, 'score': value})
    fit_report['independent_algebra_check'] = independent
    fit_report['within_training_interaction_strata'] = training_interaction_strata(records, direction)
    fit_report['cosines_to_frozen_directions'] = {name: cosine(direction, probes[name][0]) for name in CANDIDATES[:-1]}
    fit_report['original_content_lr_cosine'] = cosine(direction, original_content)
    fit_report['content_overlap_interpretation'] = 'Geometric diagnostics only. Own-training content cosines use changed references across experiments and cannot establish content/evaluation separation.'
    flags = reports['v8']['descriptive_7_of_8_flags']
    magnitude_flags = {c: reports['v8']['nuisance_effects'][c]['positive_welfare_mean_exceeds_nuisance_magnitude'] for c in CONDITIONS[1:]}
    all_flags = all(flags.values()) and all(magnitude_flags.values())
    result = {
        'status': 'completed_fixed_v8_development_analysis', 'jobs_sha256': JOBS_SHA, 'pairs_sha256': PAIRS_SHA,
        'primary_position': 'pos_b', 'layer_one_based': 26, 'new_training_states': 192,
        'reused_neutral_development_states': 64, 'model_forwards_by_analyzer': 0,
        'fresh_validation_states_used': 0, 'fit': fit_report, 'producer_backend_versions': versions,
        'local_analysis_numpy_version': np.__version__, 'training_cache_evidence': evidence,
        'analyzer_sha256': sha(Path(__file__)), 'estimator_sha256': FIT_SHA,
        'candidates': reports, 'v8_minus_fixed_comparators': comparison_deltas(reports), 'rows': rows,
        'predeclared_reindeer_sensitivity': {'excluded_item': EXCLUDED_REINDEER,
            'reason': 'Related deer/venison family overlap; descriptive only, never a replacement primary.', 'candidates': sensitivity},
        'source_sha256': sources, 'sources_unchanged': all(sha(path) == value for path, value in sources.items()),
        'development_flags': {'at_least_7_of_8_by_condition': flags, 'positive_gap_exceeds_nuisance': magnitude_flags,
                              'all_descriptive_flags': all_flags},
        'next_step': ('Propose separate independent validation; no automatic RQ3 authorization.' if all_flags else
                      'Stop this pilot and report failed development screens. Do not change sign/layer or consume reserved validation to rescue it.'),
        'measurement_validated': False, 'rq3_ready': False, 'paid_resources_started': False,
        'limitations': [
            'These eight neutral development items were already inspected. No fresh independent validation was run.',
            'Instruction interaction is not proof of internal welfare evaluation; factual attention can itself evoke evaluation.',
            'Cleaner wording and balanced contexts changed together; improvements cannot be attributed to one component.',
            'Training nuisance effects are in-sample. Paperwork is one mild control, not every form of negative sentiment.',
            'Lower concern is relative to the stated treatment; neither label implies whole-option harmlessness.',
            'Raw score gaps/offsets depend on direction geometry. Centers are display centers, not calibrated probabilities.',
            'Historical backend/template limitations remain; this pilot does not revalidate all original benchmark caches.',
        ],
    }
    require(result['sources_unchanged'], 'Source files changed during analysis')
    candidate_path = root / 'candidate_v8_direction.npz'
    arrays = {'direction': direction, 'center': center, 'raw_interaction': np.asarray(fit_report['raw_interaction']),
              'layer_one_based': np.array(26), 'jobs_sha256': np.array(JOBS_SHA), 'pairs_sha256': np.array(PAIRS_SHA)}
    if candidate_path.exists():
        with np.load(candidate_path, allow_pickle=False) as old:
            require(set(old.files) == set(arrays) and all(np.array_equal(old[k], value) for k, value in arrays.items()), 'Refusing different candidate overwrite')
    else:
        np.savez_compressed(candidate_path, **arrays)
    result['candidate_sha256'] = sha(candidate_path)
    write_once_json(root / 'development_analysis_v8.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'design', 'base'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = analyze(args.root, args.design, args.base)
    except (ValueError, KeyError, FileNotFoundError) as error:
        parser.exit(2, 'Analysis blocked: ' + str(error) + '\n')
    print(json.dumps(result['development_flags'], indent=2))
