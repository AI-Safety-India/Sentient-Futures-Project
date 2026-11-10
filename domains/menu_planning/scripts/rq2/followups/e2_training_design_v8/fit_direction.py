"""Prespecified v8 factorial estimator. No model or file loading on import.

Coordinates: (item_id, objective, detail_order, price_condition,
              service_condition, label).
Accept a mapping or a sequence of (coordinate, vector) records. The sequence
form detects duplicate coordinates before dictionary construction; callers
must not silently overwrite duplicate job coordinates in a mapping.
"""
from collections.abc import Mapping
from itertools import product
import hashlib
import numpy as np

GOALS = ('welfare', 'facts')
ORDERS = ('target_first', 'target_last')
PRICES = ('base', 'double')
SERVICES = ('positive', 'negative')
LABELS = (0, 1)


def _validated_states(training_states):
    records = list(training_states.items() if isinstance(training_states, Mapping) else training_states)
    states = {}
    for coordinate, state in records:
        if not isinstance(coordinate, tuple) or len(coordinate) != 6:
            raise ValueError('Expected six-field tuple coordinate')
        if coordinate in states:
            raise ValueError('Duplicate training coordinate')
        item, goal, order, price, service, label = coordinate
        if not isinstance(item, str) or not item:
            raise ValueError('Item IDs must be nonempty strings')
        if goal not in GOALS or order not in ORDERS or price not in PRICES or service not in SERVICES:
            raise ValueError('Unknown factorial condition')
        if isinstance(label, (bool, np.bool_)) or not isinstance(label, (int, np.integer)) or label not in LABELS:
            raise ValueError('Labels must be integer0/1')
        value = np.asarray(state, dtype=np.float64)
        if value.ndim != 1 or not value.size or not np.isfinite(value).all():
            raise ValueError('Expected finite nonempty vector')
        states[coordinate] = value
    items = sorted({key[0] for key in states})
    if len(items) != 6:
        raise ValueError('Expected exactly six training items')
    expected = set(product(items, GOALS, ORDERS, PRICES, SERVICES, LABELS))
    if set(states) != expected or len(states) != 192:
        raise ValueError('Incomplete or unexpected full factorial; expected192unique cells')
    if len({value.shape for value in states.values()}) != 1:
        raise ValueError('Inconsistent state dimensions')
    return states, items


def _cosine(a, b):
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denominator) if denominator > 1e-12 else None


def _projected_summary(vectors, direction):
    matrix = np.stack(vectors)
    scores = matrix @ direction
    return {
        'contrasts': len(vectors),
        'mean_projected_difference': float(scores.mean()),
        'median_projected_difference': float(np.median(scores)),
        'mean_absolute_projected_difference': float(np.abs(scores).mean()),
        'positive_contrasts': int(np.sum(scores > 0)),
        'negative_contrasts': int(np.sum(scores < 0)),
        'zero_contrasts': int(np.sum(scores == 0)),
        'mean_vector_norm': float(np.linalg.norm(matrix.mean(0))),
    }


def fit_direction(training_states):
    """Fit one fixed interaction; return(direction, center, JSON-safe report).

Never accepts development or held-out scores. It is the caller's responsibility
to verify job/cache identities and ensure every record belongs to the frozen
training manifest. No inference, files, normalization search or sign selection.
"""
    h, items = _validated_states(training_states)
    interaction = []
    item_interactions = {}
    for item in items:
        vectors = []
        for order, price, service in product(ORDERS, PRICES, SERVICES):
            key = lambda goal, label: (item, goal, order, price, service, label)
            delta = (h[key('welfare', 1)] - h[key('welfare', 0)]) - (h[key('facts', 1)] - h[key('facts', 0)])
            interaction.append(delta)
            vectors.append(delta)
        item_interactions[item] = np.mean(vectors, axis=0)
    raw = np.mean(interaction, axis=0)
    norm = float(np.linalg.norm(raw))
    if not np.isfinite(norm) or norm <= 1e-12:
        raise ValueError('Zero/undefined interaction; do not fabricate a direction')
    direction = raw / norm
    center = np.mean(list(h.values()), axis=0)

    # Finite-difference effects, with every other factor matched. The score
    # effects below are training diagnostics, never independent validation.
    effects = {}
    by_goal = {}
    dimensions = {
        'treatment_higher_minus_lower': (5, 0, 1),
        'goal_welfare_minus_facts': (1, 'facts', 'welfare'),
        'price_double_minus_base': (3, 'base', 'double'),
        'service_negative_minus_positive': (4, 'positive', 'negative'),
        'order_last_minus_first': (2, 'target_first', 'target_last'),
    }
    effect_vectors = {}
    for name, (dimension, low, high) in dimensions.items():
        vectors = []
        grouped = {g: [] for g in GOALS}
        for coordinate, value in h.items():
            if coordinate[dimension] != low:
                continue
            other = list(coordinate)
            other[dimension] = high
            delta = h[tuple(other)] - value
            vectors.append(delta)
            if dimension != 1:
                grouped[coordinate[1]].append(delta)
        effects[name] = _projected_summary(vectors, direction)
        effect_vectors[name] = np.mean(vectors, axis=0)
        if dimension != 1:
            by_goal[name] = {g: _projected_summary(v, direction) for g, v in grouped.items()}

    price_service = []
    price_service_goal = []
    for item, goal, order, label in product(items, GOALS, ORDERS, LABELS):
        def state(price, service):
            return h[item, goal, order, price, service, label]
        price_service.append((state('double', 'negative') - state('base', 'negative'))
                             - (state('double', 'positive') - state('base', 'positive')))
    for item, order, label in product(items, ORDERS, LABELS):
        def joint(goal):
            return ((h[item, goal, order, 'double', 'negative', label] - h[item, goal, order, 'base', 'negative', label])
                    - (h[item, goal, order, 'double', 'positive', label] - h[item, goal, order, 'base', 'positive', label]))
        price_service_goal.append(joint('welfare') - joint('facts'))

    report = {
        'training_items': items, 'training_states': len(h), 'layer_one_based': 26, 'position': 'pos_b',
        'definition': 'equalmean_items_orders_prices_service((higher_welfare-lower_welfare)-(higher_facts-lower_facts))',
        'factor_levels': {'objective': list(GOALS), 'detail_order': list(ORDERS),
                          'price_condition': list(PRICES), 'service_condition': list(SERVICES), 'label': list(LABELS)},
        'coordinate_order': ['item_id', 'objective', 'detail_order', 'price_condition', 'service_condition', 'label'],
        'raw_interaction_norm': norm, 'raw_interaction': raw.tolist(),
        'normalized_interaction_norm': float(np.linalg.norm(direction)),
        'direction_sha256': hashlib.sha256(direction.tobytes()).hexdigest(),
        'equal_item_and_factor_weights': True, 'development_states_used_for_fit': 0,
        'sign_rule': 'unmodified higher-minus-lower welfare-minus-facts',
        'score_center': 'mean192trainingstates; not a calibrated probability/threshold',
        'within_training_paired_effects': effects, 'within_training_effects_by_goal': by_goal,
        'within_training_price_service_interaction': _projected_summary(price_service, direction),
        'within_training_price_service_goal_interaction': _projected_summary(price_service_goal, direction),
        'item_interaction_norms': {i: float(np.linalg.norm(v)) for i, v in item_interactions.items()},
        'item_interaction_cosines_with_pooled_direction': {i: _cosine(v, direction) for i, v in item_interactions.items()},
        'own_training_content_main_effect_cosine': _cosine(raw, effect_vectors['treatment_higher_minus_lower']),
        'goal_main_effect_cosine': _cosine(raw, effect_vectors['goal_welfare_minus_facts']),
        'interpretation': 'Training diagnostics only. Interaction averaging does not prove welfare specificity or nuisance invariance. Compare candidates on the unchanged64development states separately; no fitting to their scores.',
        'measurement_validated': False, 'rq3_ready': False,
    }
    return direction, center, report
