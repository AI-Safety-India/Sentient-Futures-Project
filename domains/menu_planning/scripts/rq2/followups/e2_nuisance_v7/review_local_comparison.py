"""Independent CPU review of the saved nuisance-removal comparison.

Recomputes projections with QR rather than the producer's SVD. Reads only
existing inputs and writes a new review artifact; never loads a model.
"""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'Sentient-Futures-Project-git/results/rq2'
OUT = BASE / 'e2_nuisance_v7'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = read(OUT / 'local_comparison.json')
    assert all(sha(ROOT / p) == h for p, h in report['source_sha256'].items())
    jobs = [j for j in read(BASE / 'e2_benchmark_v4/jobs.json') if j['cohort'] == 'fresh']
    with np.load(BASE / 'e2_benchmark_v4/selected_layers_1_26.npz', allow_pickle=False) as z:
        states = {(j['item_id'], j['condition'], j['label']): z[j['job_id']][0, 1].astype(float) for j in jobs}
    items = sorted({j['item_id'] for j in jobs})
    conditions = ('base', 'price', 'rating', 'order')
    assert len(items) == 8 and len(states) == 64

    def basis(used):
        columns = [np.stack([states[i, c, l] - states[i, 'base', l]
                             for i in used for l in (0, 1)]).mean(0)
                   for c in conditions[1:]]
        matrix = np.column_stack(columns)
        assert np.linalg.matrix_rank(matrix) == 3
        return np.linalg.qr(matrix, mode='reduced')[0]

    probes = {}
    with np.load(BASE / 'probe_directions.npz', allow_pickle=False) as z:
        probes['original_e2'] = (z['e2_w_mm'].astype(float), z['e2_mid_mm'].astype(float))
    for name, folder in [('v5', 'e2_redesign_v5'), ('v6', 'e2_factual_v6')]:
        with np.load(BASE / folder / ('candidate_' + name + '_direction.npz'), allow_pickle=False) as z:
            probes[name] = (z['direction'].astype(float), z['center'].astype(float))

    q = basis(items)
    max_error = 0.0
    comparisons = 0

    def close(actual, expected):
        nonlocal max_error, comparisons
        error = abs(float(actual) - float(expected))
        max_error = max(max_error, error)
        comparisons += 1
        assert error < 1e-9, (actual, expected)

    def review_scores(scores, saved, pooled):
        for c in conditions:
            positive = [scores[i, c, 1] for i in items]
            negative = [scores[i, c, 0] for i in items]
            gaps = np.array(positive) - negative
            row = saved['pair_summaries'][c]
            close(np.count_nonzero(gaps > 0), row['positive_pairs'])
            close(gaps.mean(), row['mean_pair_gap'])
            close(np.median(gaps), row['median_pair_gap'])
            for i, g in zip(items, gaps):
                close(g, row['pair_gaps'][i])
            if pooled:
                wins = sum(float(h > l) + .5 * float(h == l) for h in positive for l in negative)
                close(wins / 64, row['auroc'])
            else:
                assert row['auroc'] is None
        for c in conditions[1:]:
            delta = np.array([[scores[i, c, l] - scores[i, 'base', l] for l in (0, 1)] for i in items])
            common = delta.mean(1)
            interactions = delta[:, 1] - delta[:, 0]
            row = saved['nuisance_effects'][c]
            close(common.mean(), row['mean_common_offset'])
            close(np.abs(common).mean(), row['mean_absolute_common_offset'])
            close(np.abs(delta).mean(), row['mean_absolute_variant_shift'])
            close(np.abs(interactions).mean(), row['mean_absolute_interaction'])

    corrected = {}
    with np.load(OUT / 'nuisance_corrected_candidates.npz', allow_pickle=False) as z:
        saved_weights = {k: z[k] for k in z.files}
    assert sha(OUT / 'nuisance_corrected_candidates.npz') == report['corrected_candidates_sha256']
    for name, (w, center) in probes.items():
        raw = w - q @ (q.T @ w)
        unit = raw / np.linalg.norm(raw)
        assert np.allclose(raw, saved_weights[name + '_projected_raw'], atol=1e-12, rtol=0)
        assert np.allclose(unit, saved_weights[name + '_projected_unit'], atol=1e-12, rtol=0)
        assert np.array_equal(center, saved_weights[name + '_center'])
        corrected[name] = unit
        saved = report['candidates'][name]
        close(np.linalg.norm(raw) / np.linalg.norm(w), saved['projection']['retained_norm_fraction'])
        for label, direction in [('before', w), ('projected_raw', raw), ('projected_unit', unit)]:
            scores = {k: np.dot(v - center, direction) for k, v in states.items()}
            review_scores(scores, saved[label], True)
        folds = {'raw': {}, 'unit': {}}
        for i in items:
            qi = basis([k for k in items if k != i])
            ri = w - qi @ (qi.T @ w)
            for label, direction in [('raw', ri), ('unit', ri / np.linalg.norm(ri))]:
                folds[label].update({k: np.dot(v - center, direction) for k, v in states.items() if k[0] == i})
        for label in folds:
            review_scores(folds[label], saved['leave_one_item_out'][label], False)

    # Fixed pre-existing content reference, identical for all comparisons.
    train_jobs = [j for j in read(BASE / 'e2_redesign_v5/jobs.json') if j['cohort'] == 'training']
    with np.load(BASE / 'e2_redesign_v5/training_pos_b_l26.npz', allow_pickle=False) as z:
        h = {(j['item_id'], j['condition'], j['detail_order'], j['label']): z[j['job_id']].astype(float) for j in train_jobs}
    train_items = sorted({k[0] for k in h})
    content = np.mean([h[i, g, o, 1] - h[i, g, o, 0]
                       for i in train_items for g in ('welfare', 'commercial')
                       for o in ('target_first', 'target_last')], axis=0)
    content /= np.linalg.norm(content)
    content_reference = {
        name: {'before_cosine': float(np.dot(w / np.linalg.norm(w), content)),
               'corrected_cosine': float(np.dot(corrected[name], content))}
        for name, (w, _) in probes.items()
    }
    old = read(BASE / 'e2_factual_v6/fixed_reference_content_diagnostic.json')
    close(content_reference['v5']['before_cosine'], old['v5_cosine'])
    close(content_reference['v6']['before_cosine'], old['v6_cosine'])
    review = {
        'status': 'independent_QR_review_passed', 'numeric_comparisons': comparisons,
        'maximum_absolute_error': max_error, 'source_hashes_unchanged': True,
        'model_forward_count': 0, 'paid_resources_started': False,
        'reviewed_report_sha256': sha(OUT / 'local_comparison.json'),
        'saved_candidate_arrays_verified': True,
        'fixed_content_reference': 'Same frozen v5 training main effect used in the previous v6 diagnostic.',
        'content_reference_comparison': content_reference,
        'content_interpretation': 'Post-run geometric diagnostic, not candidate selection or proof of semantic content/evaluation separation.',
        'extra_reference_inputs': {str(p.relative_to(ROOT)): sha(p) for p in [
            BASE / 'e2_redesign_v5/jobs.json', BASE / 'e2_redesign_v5/training_pos_b_l26.npz',
            BASE / 'e2_factual_v6/fixed_reference_content_diagnostic.json']},
    }
    (OUT / 'independent_review.json').write_text(json.dumps(review, indent=2), encoding='utf-8')
    print(json.dumps(review, indent=2))


if __name__ == '__main__':
    main()
