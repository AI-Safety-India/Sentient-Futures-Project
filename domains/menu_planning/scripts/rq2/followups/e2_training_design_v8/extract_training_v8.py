"""Bounded v8 training extraction. Importing this module never loads a model.

Only the explicitly authorized 192 frozen prefixes may be forwarded. No package
installation, downloads, generation, original-cache writes, or fresh validation.
An interrupted attempt without its completed cache is deliberately NOT retried.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
from pathlib import Path
import re

MODEL_ID = 'Qwen/Qwen3.5-9B'
REVISION = 'c202236235762e1c871ad0ccb60c8ee5ba337b9a'
TEMPLATE = 'a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
JOBS_SHA256 = '95c8232f06b6bdc22e8acddbaa8e211f2d9c23b76881c30c2de82881f0ebf569'
REMOTE_ROOT = '/marimo/e2_training_design_v8'
TOTAL = 192
LAYERS = list(range(1, 33))
PRIMARY_LAYER = 26
HIDDEN_SIZE = 4096
ITEMS = (
    'high_suffering_farm_products_008', 'killing_slaughter_method_005',
    'lifetime_farming_conditions_006', 'live_transport_holding_004',
    'welfare_claims_labels_001', 'wild_capture_bycatch_005',
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def atomic_json(path, obj):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


def validate_jobs(jobs):
    """Validate all factorial cells and primary identities without a tokenizer."""
    require(isinstance(jobs, list) and len(jobs) == TOTAL, 'Expected exactly192 jobs')
    require(len({j['job_id'] for j in jobs}) == TOTAL, 'Duplicate job ID')
    expected = set(itertools.product(ITEMS, ('welfare', 'facts'),
                   ('target_first', 'target_last'), ('base', 'double'),
                   ('positive', 'negative'), (0, 1)))
    found = set()
    for j in jobs:
        require(re.fullmatch(r'[a-zA-Z0-9_]+', j['job_id']) is not None, 'Unsafe job ID')
        coordinate = tuple(j[k] for k in ('item_id', 'objective', 'detail_order',
                                          'price_condition', 'service_condition', 'label'))
        require(coordinate not in found, 'Duplicate factorial coordinate')
        found.add(coordinate)
        require(j['split'] == 'train' and j['generation'] is False, 'Non-training/generation job')
        require(j['model_revision'] == REVISION and j['template_sha256'] == TEMPLATE,
                'Pinned model/template identity differs')
        require(j['primary_layer_one_based'] == PRIMARY_LAYER, 'Primary layer differs')
        ids, p = j['input_ids'], j['positions']
        require(ids and all(type(i) is int and i >= 0 for i in ids), 'Invalid input IDs')
        require(j['position_order'] == ['pos_b', 'pos_a'], 'Position order differs')
        require(set(p) == {'pos_a', 'pos_b'}, 'Unexpected position schema')
        require(type(p['pos_a']) is int and 0 <= p['pos_a'] < p['pos_b'] == len(ids)-1,
                'Invalid benchmark positions')
        require(ids[p['pos_b']] == 198 and ids[p['pos_a']] == 248067,
                'Boundary token IDs differ')
        require(j['text'].endswith('<|im_start|>assistant\n<think>\n'), 'Wrong assistant boundary')
        require(j['request']['messages'][-1]['role'] == 'tool', 'Post-tool nudge found')
        require(canonical(ids) == j['input_check']['expected_ids_sha256'] ==
                j['primary_prefix_sha256'], 'Primary prefix hash differs')
        require(j['input_check']['expected_count'] == len(ids), 'Prepared length differs')
    require(found == expected, 'Incomplete or unexpected factorial design')
    hashes = {j['job_id']: canonical(j) for j in jobs}
    require(len(set(hashes.values())) == TOTAL, 'Duplicate job hash')
    require(len({j['primary_prefix_sha256'] for j in jobs}) == TOTAL, 'Duplicate token prefix')
    return hashes


def make_execution_manifest(jobs_path, *, label_review_sha256, free_runtime_evidence,
                            expected_backend_versions):
    """Root calls only AFTER reviewing labels and verifying the free runtime.

    This does not edit frozen draft flags or imply validation passed. Evidence
    must describe observed runtime status; possession of an account is not proof.
    """
    require(file_sha(jobs_path) == JOBS_SHA256, 'Frozen input file changed')
    jobs = read_json(jobs_path)
    hashes = validate_jobs(jobs)
    require(re.fullmatch('[0-9a-f]{64}', label_review_sha256 or '') is not None,
            'Missing final label-review artifact hash')
    require(isinstance(free_runtime_evidence, dict) and
            free_runtime_evidence.get('explicitly_free') is True and
            bool(free_runtime_evidence.get('evidence')) and
            bool(free_runtime_evidence.get('verified_at_utc')), 'Missing explicit free-runtime evidence')
    require(all(expected_backend_versions.get(k) for k in ('torch', 'transformers', 'numpy')),
            'Missing measured backend versions')
    return dict(schema='v8-execution-lock-v1', jobs_file='training_jobs_draft.json',
                jobs_sha256=JOBS_SHA256, job_sha256=hashes, maximum_forward_calls=TOTAL,
                execution_authorized=True, development_only=True,
                paid_resources_authorized=False, fresh_validation_authorized=False,
                label_review_sha256=label_review_sha256,
                free_runtime_evidence=free_runtime_evidence,
                expected_backend_versions=expected_backend_versions,
                model_id=MODEL_ID, model_revision=REVISION, template_sha256=TEMPLATE,
                primary_position='pos_b', primary_layer_one_based=PRIMARY_LAYER,
                remote_output_root=REMOTE_ROOT)


def validate_lock(jobs_path, protocol, label_review_path):
    require(file_sha(jobs_path) == JOBS_SHA256 == protocol['jobs_sha256'], 'Jobs file/hash differs')
    jobs = read_json(jobs_path)
    expected = make_execution_manifest(jobs_path,
        label_review_sha256=protocol['label_review_sha256'],
        free_runtime_evidence=protocol['free_runtime_evidence'],
        expected_backend_versions=protocol['expected_backend_versions'])
    require(protocol == expected, 'Execution lock schema or authorization differs')
    require(file_sha(label_review_path) == protocol['label_review_sha256'],
            'Final label-review artifact changed or is missing')
    return jobs


def verify_tokenizer(jobs, tokenizer):
    require(isinstance(tokenizer.chat_template, str) and
            hashlib.sha256(tokenizer.chat_template.encode()).hexdigest() == TEMPLATE,
            'Tokenizer template differs')
    for j in jobs:
        request = j['request']
        require(tokenizer.apply_chat_template(request['messages'], tools=request['tools'],
            tokenize=False, add_generation_prompt=True) == j['text'],
            'Rendered request differs: ' + j['job_id'])
        require(tokenizer.encode(j['text'], add_special_tokens=False) == j['input_ids'],
                'Exact tokenizer IDs differ: ' + j['job_id'])
        p = j['positions']
        require(tokenizer.decode([j['input_ids'][p['pos_a']]], skip_special_tokens=False)
                == '</tool_response>', 'Target detail boundary differs')
        # A closing tool delimiter is insufficient: it must close THIS target.
        prefix = tokenizer.decode(j['input_ids'][:p['pos_a']+1], skip_special_tokens=False)
        require(prefix.endswith(j['target_description'] + '\n</tool_response>') or
                prefix.endswith(j['target_description'] + '</tool_response>'),
                'Target option identity or target closing boundary differs: ' + j['job_id'])


def snapshot_identity(snapshot):
    """Require actual cached weight files, never whole-repository completeness."""
    snapshot = Path(snapshot).expanduser().resolve()
    require(snapshot.name == REVISION, 'Snapshot directory is not the pinned commit')
    required = ['config.json', 'tokenizer.json', 'chat_template.jinja',
                'model.safetensors.index.json']
    require(all((snapshot / name).is_file() for name in required), 'Required cached model files absent')
    require(file_sha(snapshot / 'chat_template.jinja') == TEMPLATE, 'Cached template differs')
    index = read_json(snapshot / 'model.safetensors.index.json')
    shards = sorted(set(index['weight_map'].values()))
    require(shards and all(Path(s).name == s and (snapshot/s).is_file() for s in shards),
            'Missing cached weights; no download was started')
    return dict(snapshot_path=str(snapshot), model_revision=REVISION,
                config_sha256=file_sha(snapshot/'config.json'),
                weight_index_sha256=file_sha(snapshot/'model.safetensors.index.json'),
                cached_weight_files=[dict(name=s, bytes=(snapshot/s).stat().st_size) for s in shards],
                tokenizer_json_sha256=file_sha(snapshot/'tokenizer.json'))


def verify_loaded_model(model, snapshot, torch):
    identity = snapshot_identity(snapshot)
    require(type(model).__name__ == 'Qwen3_5ForConditionalGeneration', 'Wrong loaded model class')
    require(model.training is False, 'Model must already be in eval mode')
    config = model.config
    text_config = getattr(config, 'text_config', config)
    pinned_config = read_json(Path(snapshot)/'config.json')
    actual_text = text_config.to_dict()
    # Runtime/version fields may be added; every published text-model setting
    # must retain its pinned value. This is stronger than dimension checks alone.
    differing = [key for key, value in pinned_config['text_config'].items()
                 if actual_text.get(key) != value]
    require(not differing, 'Loaded text config differs from pinned file: '+', '.join(differing))
    require(text_config.num_hidden_layers == 32 and text_config.hidden_size == HIDDEN_SIZE,
            'Model hidden dimensions differ')
    require(getattr(text_config, '_attn_implementation', None) == 'sdpa',
            'Expected SDPA backend; do not silently change it')
    source = str(getattr(config, '_name_or_path', ''))
    pinned_source = (source == MODEL_ID and getattr(config, '_commit_hash', None) == REVISION)
    if not pinned_source:
        pinned_source = Path(source).expanduser().resolve() == Path(snapshot).expanduser().resolve()
    require(pinned_source, 'Loaded model has no matching pinned-source evidence')
    require(not getattr(model, 'peft_config', None), 'Adapters are not authorized')
    require(not getattr(model, 'is_quantized', False), 'Quantization differs from BF16 protocol')
    require(not any(m._forward_hooks or m._forward_pre_hooks for m in model.modules()),
            'Loaded model has unreviewed forward hooks')
    params = list(model.parameters())
    require(params and all(p.device.type == 'cuda' for p in params), 'Model must be entirely on CUDA')
    require(all(p.dtype == torch.bfloat16 for p in params if p.is_floating_point()),
            'Model parameter dtype differs from BF16')
    require(len({str(p.device) for p in params}) == 1, 'One GPU is required')
    return dict(identity, model_class=type(model).__name__, model_dtype='bfloat16',
                attention='sdpa', device=str(params[0].device),
                pinned_source_observed=source, loaded_model_verified=True,
                loaded_text_config_sha256=canonical({k: actual_text[k]
                    for k in pinned_config['text_config']}))


def load_cached_components(snapshot):
    """Explicit opt-in helper. No inference/download; caller must check free runtime first."""
    snapshot_identity(snapshot)
    import torch
    from transformers import AutoTokenizer, Qwen3_5ForConditionalGeneration
    require(torch.cuda.is_available(), 'No existing CUDA runtime; no resources started')
    tokenizer = AutoTokenizer.from_pretrained(str(snapshot), local_files_only=True)
    tokenizer.chat_template = (Path(snapshot)/'chat_template.jinja').read_text(encoding='utf-8')
    model = Qwen3_5ForConditionalGeneration.from_pretrained(str(snapshot),
        local_files_only=True, dtype=torch.bfloat16, attn_implementation='sdpa').to('cuda').eval()
    model.requires_grad_(False)
    verify_loaded_model(model, snapshot, torch)
    return model, tokenizer


def preflight_package(root_path):
    """Code-only preparation check; safe locally without torch or any model."""
    root = Path(root_path)
    path = root/'training_jobs_draft.json'
    require(file_sha(path) == JOBS_SHA256, 'Frozen input file changed')
    jobs = read_json(path)
    hashes = validate_jobs(jobs)
    return dict(jobs_sha256=JOBS_SHA256, jobs=len(jobs), unique_job_hashes=len(set(hashes.values())),
                unique_input_prefixes=len({j['primary_prefix_sha256'] for j in jobs}),
                model_runs_started=0, model_weights_loaded=False, network_calls=0,
                status='local_package_verified_runtime_verification_still_required')


def preflight_execution(root_path, snapshot, *, tokenizer=None, model=None,
                        label_review_filename='execution_label_review.json'):
    """No loads, forwards or writes. Inspect explicitly supplied live objects only."""
    import importlib.metadata
    root = Path(root_path).resolve()
    require(str(root) == REMOTE_ROOT, 'Wrong remote output root')
    require(Path(label_review_filename).name == label_review_filename, 'Invalid label review filename')
    protocol = read_json(root/'execution_manifest.json')
    jobs = validate_lock(root/'training_jobs_draft.json', protocol, root/label_review_filename)
    versions = {k: importlib.metadata.version(k) for k in ('torch', 'transformers', 'numpy')}
    require(versions == protocol['expected_backend_versions'], 'Runtime package versions changed')
    snapshot_evidence = snapshot_identity(snapshot)
    if tokenizer is not None:
        verify_tokenizer(jobs, tokenizer)
    model_evidence = None
    if model is not None:
        import torch
        model_evidence = verify_loaded_model(model, snapshot, torch)
    return dict(jobs=TOTAL, jobs_sha256=JOBS_SHA256, backend_versions=versions,
                snapshot_identity=snapshot_evidence, supplied_tokenizer_verified=tokenizer is not None,
                supplied_model_verified=model is not None, model_identity=model_evidence,
                model_forwards=0, downloads=0,
                status='ready' if model is not None and tokenizer is not None else 'components_still_required')


def cache_identity(job, backend_versions, model_identity):
    return dict(schema='v8-training-cache-v1', job_id=job['job_id'], job_sha256=canonical(job),
                jobs_sha256=JOBS_SHA256, model_id=MODEL_ID, model_revision=REVISION,
                template_sha256=TEMPLATE, prompt_sha256=hashlib.sha256(job['text'].encode()).hexdigest(),
                input_ids_sha256=canonical(job['input_ids']), input_token_count=len(job['input_ids']),
                primary_prefix_sha256=job['primary_prefix_sha256'],
                positions={k: job['positions'][k] for k in ('pos_b', 'pos_a')},
                position_order=['pos_b', 'pos_a'], layers_one_based=LAYERS,
                hidden_state_semantics='post_decoder_layer_excludes_embeddings',
                dtype='float16', model_dtype='bfloat16', attention='sdpa',
                backend='transformers', backend_versions=backend_versions,
                model_identity=model_identity)


def verify_cache(dest, job, identity, np):
    manifest = read_json(dest.with_suffix('.json'))
    require(all(manifest.get(k) == v for k, v in identity.items()),
            'Saved cache identity differs: ' + job['job_id'])
    require(manifest.get('payload_sha256') == file_sha(dest), 'Saved cache payload hash differs')
    check = manifest.get('input_check', {})
    require(check.get('exact_input_verified') is True and check.get('token_ids_match') is True
            and check.get('actual_backend_count') == len(job['input_ids'])
            and check.get('expected_ids_sha256') == canonical(job['input_ids']),
            'Missing runtime exact-input evidence')
    with np.load(dest, allow_pickle=False) as z:
        require(set(z.files) == {'hidden_states', 'input_ids', 'indices'}, 'Cache NPZ schema differs')
        require(np.array_equal(z['input_ids'], job['input_ids']) and
                np.array_equal(z['indices'], [job['positions']['pos_b'], job['positions']['pos_a']]),
                'Saved cache token IDs or indices differ')
        h = z['hidden_states']
        require(h.shape == (2, 32, HIDDEN_SIZE) and h.dtype == np.dtype('float16')
                and bool(np.isfinite(h).all()), 'Invalid hidden-state shape/dtype/values')
        selected = h[0, PRIMARY_LAYER-1].copy()
    return manifest, selected


def reconcile_resume(jobs, ledger, valid_completed):
    """No attempt may be invisibly retried; completed caches can finish a ledger commit."""
    allowed = {j['job_id'] for j in jobs}
    require(set(ledger) <= allowed, 'Unexpected job in forward ledger')
    require(set(valid_completed) <= set(ledger), 'Cache has no producer forward-ledger entry')
    for job_id, entry in ledger.items():
        require(entry.get('job_sha256') == canonical(next(j for j in jobs if j['job_id'] == job_id)),
                'Ledger job hash differs')
        require(entry.get('attempts') == 1 and entry.get('state') in ('forward_started', 'complete'),
                'Invalid or repeated forward attempt')
        if job_id not in valid_completed:
            raise ValueError('An earlier forward started without a verified completed cache: ' +
                             job_id + '. Stopped; no automatic retry or extra forward.')
    return [j for j in jobs if j['job_id'] not in ledger]


def extract_training(root_path=REMOTE_ROOT, *, model, tokenizer, snapshot,
                     label_review_filename='execution_label_review.json'):
    """Run once explicitly on verified-free Molab; reuse valid completed jobs only."""
    import importlib.metadata
    import numpy as np
    import torch
    root = Path(root_path).resolve()
    require(str(root) == REMOTE_ROOT, 'Writes are restricted to the new v8 Molab directory')
    require(Path(label_review_filename).name == label_review_filename, 'Invalid label review filename')
    protocol = read_json(root/'execution_manifest.json')
    jobs = validate_lock(root/'training_jobs_draft.json', protocol, root/label_review_filename)
    versions = {k: importlib.metadata.version(k) for k in ('torch', 'transformers', 'numpy')}
    require(versions == protocol['expected_backend_versions'], 'Runtime package versions changed')
    verify_tokenizer(jobs, tokenizer)
    model_identity = verify_loaded_model(model, snapshot, torch)
    outdir = root/'activations'
    outdir.mkdir(exist_ok=True)
    require(outdir.resolve() == root/'activations', 'Output directory is a symlink')
    guard = root/'runner.lock'
    with guard.open('x', encoding='utf-8') as f:
        f.write(json.dumps(dict(pid=os.getpid(), jobs_sha256=JOBS_SHA256)))
    ledger_path = root/'forward_ledger.json'
    ledger = read_json(ledger_path) if ledger_path.exists() else {}
    completed, vectors, records = [], [], []
    new_forwards = 0

    def status(state, **extra):
        atomic_json(root/'run_status.json', dict(state=state, completed=len(completed),
                    total=TOTAL, jobs_sha256=JOBS_SHA256, generation_calls=0,
                    forward_attempts_total=len(ledger), new_forwards_this_invocation=new_forwards,
                    model_revision=REVISION, template_sha256=TEMPLATE,
                    backend_versions=versions, paid_resources_authorized=False, **extra))

    def consume(j, dest, identity):
        manifest, vector = verify_cache(dest, j, identity, np)
        completed.append(j['job_id'])
        vectors.append(vector)
        records.append(dict(job_id=j['job_id'], job_sha256=canonical(j),
            input_ids_sha256=canonical(j['input_ids']), primary_prefix_sha256=j['primary_prefix_sha256'],
            cache_payload_sha256=manifest['payload_sha256'],
            cache_manifest_sha256=file_sha(dest.with_suffix('.json')),
            selected_array_sha256=hashlib.sha256(vector.tobytes()).hexdigest(),
            positions=j['positions'], input_check=manifest['input_check']))

    try:
        allowed = {j['job_id'] for j in jobs}
        require(all(p.stem in allowed for p in outdir.glob('*.npz')), 'Unexpected activation file')
        valid_completed = set()
        for j in jobs:
            dest = outdir/(j['job_id']+'.npz')
            require(dest.exists() == dest.with_suffix('.json').exists(),
                    'Incomplete cache commit; stopped without retry: '+j['job_id'])
            if dest.exists():
                verify_cache(dest, j, cache_identity(j, versions, model_identity), np)
                valid_completed.add(j['job_id'])
        reconcile_resume(jobs, ledger, valid_completed)
        status('running')
        print('Verified192 frozen inputs, exact target boundaries, pinned BF16/SDPA model. Starting/resuming bounded extraction.', flush=True)
        with torch.inference_mode():
            for j in jobs:
                dest = outdir/(j['job_id']+'.npz')
                identity = cache_identity(j, versions, model_identity)
                if j['job_id'] not in valid_completed:
                    inp = torch.tensor([j['input_ids']], dtype=torch.long, device=model_identity['device'])
                    actual = inp[0].tolist()
                    require(actual == j['input_ids'], 'Actual backend input IDs differ')
                    require(len(ledger) < TOTAL and j['job_id'] not in ledger,
                            'Forward bound or unique-job contract violated')
                    ledger[j['job_id']] = dict(state='forward_started', attempts=1,
                                              job_sha256=canonical(j))
                    atomic_json(ledger_path, ledger)  # Persist BEFORE invoking the model.
                    new_forwards += 1
                    status('running', active_job_id=j['job_id'])
                    output = model(input_ids=inp, attention_mask=torch.ones_like(inp),
                        use_cache=False, output_hidden_states=True, return_dict=True, logits_to_keep=1)
                    require(len(output.hidden_states) == 33, 'Expected embeddings plus32 decoder states')
                    positions = [j['positions']['pos_b'], j['positions']['pos_a']]
                    h = np.stack([s[0, positions].to(torch.float16).cpu().numpy()
                                  for s in output.hidden_states[1:]], axis=1)
                    require(h.shape == (2, 32, HIDDEN_SIZE) and bool(np.isfinite(h).all()),
                            'Hidden states have unexpected shape or nonfinite values')
                    temporary = dest.with_name(dest.name+'.tmp')
                    with temporary.open('wb') as f:
                        np.savez_compressed(f, hidden_states=h,
                            input_ids=np.asarray(j['input_ids'], dtype=np.int64),
                            indices=np.asarray(positions, dtype=np.int64))
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(temporary, dest)
                    observed = dict(expected_count=len(actual), actual_backend_count=len(actual),
                        token_ids_match=True, exact_input_verified=True, first_mismatch=None,
                        expected_ids_sha256=canonical(actual))
                    atomic_json(dest.with_suffix('.json'), dict(identity,
                        payload_sha256=file_sha(dest), input_check=observed))
                    del output, inp, h
                consume(j, dest, identity)
                ledger[j['job_id']]['state'] = 'complete'
                atomic_json(ledger_path, ledger)
                status('running')
                print(f'Completed {len(completed)}/192: {j["job_id"]}', flush=True)
        require(len(completed) == len(ledger) == TOTAL, 'Incomplete extraction')
        selected_path = root/'training_pos_b_l26.npz'
        temporary = selected_path.with_name(selected_path.name+'.tmp')
        with temporary.open('wb') as f:
            np.savez_compressed(f, job_ids=np.asarray(completed), hidden_states=np.stack(vectors),
                input_ids_sha256=np.asarray([r['input_ids_sha256'] for r in records]),
                job_sha256=np.asarray([r['job_sha256'] for r in records]))
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, selected_path)
        atomic_json(root/'training_pos_b_l26.json', dict(schema='v8-selected-pos-b-l26-v1',
            payload_sha256=file_sha(selected_path), jobs_sha256=JOBS_SHA256,
            model_id=MODEL_ID, model_revision=REVISION, template_sha256=TEMPLATE,
            backend='transformers', backend_versions=versions, model_dtype='bfloat16',
            attention='sdpa', dtype='float16', model_identity=model_identity,
            layer_one_based=PRIMARY_LAYER, position='pos_b',
            hidden_state_semantics='post_decoder_layer_excludes_embeddings', records=records,
            execution_manifest_sha256=file_sha(root/'execution_manifest.json'),
            forward_ledger_sha256=file_sha(ledger_path)))
        status('complete', selected_payload_sha256=file_sha(selected_path))
        print('Complete:192 unique forward caches; selected pos_b/L26 saved. No generation or fresh validation.', flush=True)
        return dict(completed=TOTAL, selected_payload_sha256=file_sha(selected_path),
                    new_forwards_this_invocation=new_forwards)
    except BaseException as exc:
        status('interrupted_or_failed', error=str(exc))
        raise
    finally:
        guard.unlink(missing_ok=True)
