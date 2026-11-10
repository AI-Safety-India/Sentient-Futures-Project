"""Prospective fixed-layer interaction fit; no inference or execution on import.

Neutral development activations are never arguments to the fitting function.
The output is an instruction-modulated candidate feature, not a validated
measurement of spontaneous welfare evaluation.
"""
import hashlib
import numpy as np

GOALS=('welfare','commercial')
ORDERS=('target_first','target_last')

def fit_direction(training_states):
    """states[(item_id, goal, order, label)] -> pos_b L26 vector.

Equal weight for each of six items and both orders. No layer selection,
regression on development labels, sign correction or nuisance orthogonalizing.
"""
    if not training_states:raise ValueError('Training states absent; no fit performed')
    items=sorted({k[0] for k in training_states})
    if len(items)!=6:raise ValueError('Expected six reviewed training items')
    required={(i,g,o,l) for i in items for g in GOALS for o in ORDERS for l in (0,1)}
    if set(training_states)!=required:raise ValueError('Incomplete, unexpected, or mixed training factors')
    shapes={np.asarray(v).shape for v in training_states.values()}
    if len(shapes)!=1 or len(next(iter(shapes)))!=1:raise ValueError('Expected equal-dimensional vectors')
    if any(not np.isfinite(v).all() for v in training_states.values()):raise ValueError('Nonfinite training states')
    states={k:np.asarray(v,dtype=np.float64) for k,v in training_states.items()}
    interaction=[];content=[];goal_main=[];by_order={o:[] for o in ORDERS}
    for i in items:
        for o in ORDERS:
            hw=states[i,'welfare',o,1];lw=states[i,'welfare',o,0]
            hc=states[i,'commercial',o,1];lc=states[i,'commercial',o,0]
            delta=(hw-lw)-(hc-lc)
            interaction.append(delta);by_order[o].append(delta)
            content.append(((hw-lw)+(hc-lc))/2)
            goal_main.append(((hw-hc)+(lw-lc))/2)
    raw=np.mean(interaction,axis=0);norm=float(np.linalg.norm(raw))
    if norm<=1e-12:raise ValueError('Zero interaction; do not manufacture a direction')
    direction=raw/norm
    center=np.mean(list(states.values()),axis=0)
    def cosine(a,b):
        denominator=np.linalg.norm(a)*np.linalg.norm(b)
        return float(np.dot(a,b)/denominator) if denominator>1e-12 else None
    order_means={o:np.mean(v,axis=0) for o,v in by_order.items()}
    report=dict(training_items=items,training_states=48,layer_one_based=26,position='pos_b',
        normalized_interaction_norm=1.0,raw_interaction_norm=norm,
        definition='mean_items(mean_orders((higher_welfare-lower_welfare)-(higher_commercial-lower_commercial)))',
        development_states_used=0,sign_rule='unmodified higher-minus-lower welfare-minus-commercial',
        direction_sha256=hashlib.sha256(direction.tobytes()).hexdigest(),
        order_interaction_cosine=cosine(order_means[ORDERS[0]],order_means[ORDERS[1]]),
        content_main_effect_cosine=cosine(raw,np.mean(content,axis=0)),
        goal_main_effect_cosine=cosine(raw,np.mean(goal_main,axis=0)),
        score_center='mean of training states; no classification threshold or calibrated probability',
        rq3_ready=False,measurement_validated=False,
        interpretation='Candidate instruction-modulated welfare sensitivity; diagnostics are not construct validation.')
    return direction,center,report

def score_pairs(direction,center,pairs):
    """Read-only neutral transfer scores, never changes the direction."""
    result={}
    for item,pair in sorted(pairs.items()):
        if set(pair)!={0,1}:raise ValueError('Both relative-concern variants required')
        scores={l:float(np.dot(np.asarray(pair[l],dtype=float)-center,direction)) for l in (0,1)}
        result[item]=dict(scores=scores,higher_minus_lower=scores[1]-scores[0])
    return result
