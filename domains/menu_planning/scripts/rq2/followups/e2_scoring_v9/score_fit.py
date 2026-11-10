"""Fixed, local ridge scorer. No file/model/network access in this module."""
from itertools import product
import hashlib
import numpy as np

GOALS=('welfare','facts')
ORDERS=('target_first','target_last')
PRICES=('base','double')
SERVICES=('positive','negative')
LABELS=(0,1)
RIDGE_FRACTION=0.01
GROUPS=('price','order','service')


def validate(records, expected_items=None):
    states={}
    for key,value in records:
        if not isinstance(key,tuple) or len(key)!=6 or key in states:
            raise ValueError('Malformed or duplicate training coordinate')
        item,goal,order,price,service,label=key
        if not isinstance(item,str) or not item or goal not in GOALS or order not in ORDERS or price not in PRICES or service not in SERVICES or type(label) is not int or label not in LABELS:
            raise ValueError('Unknown factorial level')
        vector=np.asarray(value,dtype=np.float64)
        if vector.ndim!=1 or not vector.size or not np.isfinite(vector).all():
            raise ValueError('Expected a finite vector')
        states[key]=vector
    items=sorted({key[0] for key in states})
    if not items or (expected_items is not None and len(items)!=expected_items):
        raise ValueError('Unexpected number of training items')
    if set(states)!=set(product(items,GOALS,ORDERS,PRICES,SERVICES,LABELS)):
        raise ValueError('Incomplete factorial; every item needs 32 cells')
    if len({value.shape for value in states.values()})!=1:
        raise ValueError('Inconsistent activation dimensions')
    return states,items


def matrices(records, expected_items=None):
    states,items=validate(records,expected_items)
    target=[]
    for item,order,price,service in product(items,ORDERS,PRICES,SERVICES):
        target.append((states[item,'welfare',order,price,service,1]-states[item,'welfare',order,price,service,0])
                     -(states[item,'facts',order,price,service,1]-states[item,'facts',order,price,service,0]))
    nuisance={}
    for name,(dimension,low,high) in {'price':(3,'base','double'),'order':(2,'target_first','target_last'),'service':(4,'positive','negative')}.items():
        rows=[]
        for key in sorted(states):
            if key[dimension]==low:
                other=list(key);other[dimension]=high
                rows.append(states[tuple(other)]-states[key])
        nuisance[name]=np.stack(rows)
    return states,items,np.stack(target),nuisance


def system(target,nuisance):
    scale2=float(np.mean(np.sum(target*target,axis=1)))
    if not np.isfinite(scale2) or scale2<=1e-20:
        raise ValueError('No finite target interaction energy')
    scale=scale2**0.5
    blocks=[target/np.sqrt(len(target))]
    blocks.extend(nuisance[group]/np.sqrt(3*len(nuisance[group])) for group in GROUPS)
    design=np.vstack(blocks)/scale
    labels=np.concatenate([np.ones(len(target))/np.sqrt(len(target)),np.zeros(sum(len(nuisance[g]) for g in GROUPS))])
    return design,labels,scale


def fit(records, expected_items=None):
    """One fixed dual ridge solution; targets and penalties use fitting data only."""
    records=list(records)
    states,items,target,nuisance=matrices(records,expected_items)
    design,labels,scale=system(target,nuisance)
    dual=np.linalg.solve(design@design.T+RIDGE_FRACTION*np.eye(len(design)),labels)
    scaled_w=design.T@dual
    raw_w=scaled_w/scale
    norm=float(np.linalg.norm(raw_w))
    if not np.isfinite(norm) or norm<=1e-12:
        raise ValueError('Zero or invalid fitted direction')
    direction=raw_w/norm
    center=np.mean([states[key] for key in sorted(states)],axis=0)
    # First-order residual checks the implemented solve on actual data.
    gradient=design.T@(design@scaled_w-labels)+RIDGE_FRACTION*scaled_w
    relative_residual=float(np.linalg.norm(gradient)/max(np.linalg.norm(design.T@labels),1e-15))
    if relative_residual>1e-8:
        raise ValueError('Ridge normal equations not satisfied')
    info={
        'items':items,'states':len(states),'target_rows':len(target),
        'nuisance_rows':{g:len(nuisance[g]) for g in GROUPS},
        'scale_squared':scale**2,'ridge_fraction':RIDGE_FRACTION,
        'raw_weight_norm':norm,'direction_sha256':hashlib.sha256(direction.tobytes()).hexdigest(),
        'relative_stationarity_residual':relative_residual,
        'raw_objective':float(np.mean((target@raw_w-1)**2)+sum(np.mean((nuisance[g]@raw_w)**2) for g in GROUPS)/3+RIDGE_FRACTION*scale**2*norm**2),
        'raw_target_mse':float(np.mean((target@raw_w-1)**2)),
        'raw_nuisance_mse':{g:float(np.mean((nuisance[g]@raw_w)**2)) for g in GROUPS},
    }
    return direction,center,raw_w,info


def mean_baseline(records):
    states,items,target,_=matrices(records)
    direction=target.mean(axis=0)
    norm=np.linalg.norm(direction)
    if norm<=1e-12:raise ValueError('Undefined mean baseline')
    return direction/norm,np.mean([states[k] for k in sorted(states)],axis=0)


def projected(values,direction):
    scores=values@direction
    return {'contrasts':len(scores),'positive':int(np.sum(scores>0)),
            'negative':int(np.sum(scores<0)),'ties':int(np.sum(scores==0)),
            'mean':float(scores.mean()),'mean_absolute':float(np.abs(scores).mean()),
            'scores':scores.tolist()}


def diagnose(records,direction):
    states,items,target,nuisance=matrices(records)
    treatment={}
    for goal in GOALS:
        rows=[states[i,goal,o,p,s,1]-states[i,goal,o,p,s,0]
              for i,o,p,s in product(items,ORDERS,PRICES,SERVICES)]
        treatment[goal]=projected(np.stack(rows),direction)
    return {'items':items,'interaction':projected(target,direction),
            'treatment_by_goal':treatment,
            'nuisance':{g:projected(nuisance[g],direction) for g in GROUPS}}


def item_split(records, held_out):
    states,items=validate(records)
    if held_out not in items:raise ValueError('Unknown held-out item')
    train=[(k,states[k]) for k in sorted(states) if k[0]!=held_out]
    test=[(k,states[k]) for k in sorted(states) if k[0]==held_out]
    return train,test


def leave_one_item_out(records):
    _,items=validate(records,6)
    folds=[]
    for held_out in items:
        train,test=item_split(records,held_out)
        direction,_,_,info=fit(train,5)
        baseline,_=mean_baseline(train)
        folds.append({'held_out_item':held_out,'fitting_items':info['items'],
                      'fitting_states':len(train),'held_out_states':len(test),
                      'fit':info,'v9':diagnose(test,direction),
                      'mean_interaction_baseline':diagnose(test,baseline)})
    aggregate={}
    for candidate in ('v9','mean_interaction_baseline'):
        aggregate[candidate]={}
        collections={'interaction': [f[candidate]['interaction'] for f in folds]}
        collections.update({g:[f[candidate]['nuisance'][g] for f in folds] for g in GROUPS})
        for name,parts in collections.items():
            scores=np.concatenate([part['scores'] for part in parts])
            aggregate[candidate][name]={'contrasts':len(scores),'positive':int(np.sum(scores>0)),
                'mean':float(scores.mean()),'mean_absolute':float(np.abs(scores).mean())}
    return {'folds':folds,'aggregate':aggregate,
            'hyperparameter_selection':False,
            'scope':'Excluded-item diagnostics within welfare/factual training contexts; not neutral-context or independent benchmark validation.'}
