"""CPU-only descriptive nuisance projection; never performs model inference.

All source files are read-only. The calibration examples have already been
inspected. Neither in-sample orthogonality nor leave-one-item-out diagnostics
constitute fresh validation of the candidate construct.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
CODE=Path(__file__).resolve().parent
BASE=ROOT/'Sentient-Futures-Project-git/results/rq2'
OUT=BASE/'e2_nuisance_v7'
CONDITIONS=('base','price','rating','order')
NUISANCES=CONDITIONS[1:]
ORIGINAL_SHA='bcd29390210350dd707a37db85b83ce21ab5db2fa55f74ec9fa0b5ab64679749'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(value,message):
    if not value:raise ValueError(message)
def cosine(a,b):
    d=np.linalg.norm(a)*np.linalg.norm(b)
    return float(np.dot(a,b)/d) if d>1e-12 else None

def learn_nuisance_span(states,training_items):
    """Mean within-item, equal-concern-variant control differences only."""
    items=sorted(training_items)
    require(bool(items),'No calibration items')
    for i in items:
        require(set(states[i])=={(c,l) for c in CONDITIONS for l in (0,1)},'Incomplete nuisance factorial')
    vectors={c:np.mean([np.mean([states[i][c,l]-states[i]['base',l] for l in (0,1)],axis=0) for i in items],axis=0) for c in NUISANCES}
    matrix=np.column_stack([vectors[c] for c in NUISANCES])
    require(matrix.ndim==2 and np.isfinite(matrix).all(),'Invalid nuisance vectors')
    u,s,_=np.linalg.svd(matrix,full_matrices=False)
    tol=np.finfo(float).eps*max(matrix.shape)*(float(s[0]) if len(s) else 0.)
    rank=int(np.sum(s>tol));basis=u[:,:rank]
    meta=dict(calibration_items=items,equal_weight_items=True,equal_weight_concern_variants=True,
        singular_values=s.tolist(),svd_tolerance=tol,rank=rank,
        condition_number=float(s[0]/s[rank-1]) if rank else None,
        raw_vector_norms={c:float(np.linalg.norm(vectors[c])) for c in NUISANCES},
        pairwise_nuisance_cosines={f'{a}|{b}':cosine(vectors[a],vectors[b]) for n,a in enumerate(NUISANCES) for b in NUISANCES[n+1:]})
    return basis,vectors,meta

def project_direction(direction,basis):
    w=np.asarray(direction,dtype=float)
    require(w.ndim==1 and basis.ndim==2 and basis.shape[0]==len(w),'Direction/basis shape mismatch')
    require(np.isfinite(w).all() and np.linalg.norm(w)>1e-12,'Invalid direction')
    require(np.allclose(basis.T@basis,np.eye(basis.shape[1]),atol=1e-10),'Basis not orthonormal')
    residual=w-basis@(basis.T@w);norm=float(np.linalg.norm(residual));original=float(np.linalg.norm(w))
    meta=dict(original_norm=original,projected_norm=norm,retained_norm_fraction=norm/original,
        retained_squared_norm_fraction=(norm/original)**2,removed_squared_norm_fraction=1-(norm/original)**2,
        max_projection_on_fitted_basis=float(np.max(np.abs(basis.T@residual))) if basis.shape[1] else 0.,
        normalization='raw residual reported; unit-normalized residual is the frozen steering candidate',
        note='Training-calibration orthogonality is guaranteed by construction, not validation.')
    return residual,(residual/norm if norm>1e-12 else None),meta

def score(states,items,direction,center):
    return {i:{(c,l):float(np.dot(states[i][c,l]-center,direction)) for c in CONDITIONS for l in (0,1)} for i in sorted(items)}

def summaries(scores,pooled_auc=True):
    items=sorted(scores);report={};controls={}
    for c in CONDITIONS:
        gaps={i:scores[i][c,1]-scores[i][c,0] for i in items}
        hi=np.array([scores[i][c,1] for i in items]);lo=np.array([scores[i][c,0] for i in items])
        report[c]=dict(items=len(items),positive_pairs=sum(g>0 for g in gaps.values()),negative_pairs=sum(g<0 for g in gaps.values()),ties=sum(g==0 for g in gaps.values()),mean_pair_gap=float(np.mean(list(gaps.values()))),median_pair_gap=float(np.median(list(gaps.values()))),pair_gaps=gaps,
            auroc=float(np.mean((hi[:,None]>lo)+.5*(hi[:,None]==lo))) if pooled_auc else None)
    for c in NUISANCES:
        variant={f'{i}|{l}':scores[i][c,l]-scores[i]['base',l] for i in items for l in (0,1)}
        common={i:np.mean([scores[i][c,l]-scores[i]['base',l] for l in (0,1)]).item() for i in items}
        interaction={i:report[c]['pair_gaps'][i]-report['base']['pair_gaps'][i] for i in items}
        controls[c]=dict(mean_common_offset=float(np.mean(list(common.values()))),mean_absolute_common_offset=float(np.mean(np.abs(list(common.values())))),mean_absolute_variant_shift=float(np.mean(np.abs(list(variant.values())))),mean_absolute_interaction=float(np.mean(np.abs(list(interaction.values())))),pair_sign_changes=int(sum(np.sign(report[c]['pair_gaps'][i])!=np.sign(report['base']['pair_gaps'][i]) for i in items)),common_offsets=common,interactions=interaction,variant_shifts=variant,
            positive_welfare_mean_exceeds_nuisance_magnitude=bool(report['base']['mean_pair_gap']>0 and report['base']['mean_pair_gap']>np.mean(np.abs(list(variant.values())))))
    return dict(pair_summaries=report,nuisance_effects=controls,
        descriptive_7_of_8_flags={c:report[c]['positive_pairs']>=7 for c in CONDITIONS},
        flags_interpretation='Historical development screens only; no new validation pass.',
        pooled_auroc_note=None if pooled_auc else 'Each held-out item uses a different correction; no pooled cross-fold AUROC.')

def verify_and_load():
    v4=BASE/'e2_benchmark_v4';v5=BASE/'e2_redesign_v5';v6=BASE/'e2_factual_v6'
    manifest=read(v4/'selected_layer_manifest.json');jobs=read(v4/'jobs.json');r4=read(v4/'benchmark_validation.json');r6=read(v6/'factual_analysis.json')
    require(sha(v4/'jobs.json')==manifest['jobs_sha256']==r4['core_jobs_sha256'],'V4 inputs changed')
    require(sha(v4/'selected_layers_1_26.npz')==manifest['selected_npz_sha256'],'V4 subset changed')
    require(manifest['layers_one_based']==[1,26] and manifest['position_order']==['pos_b','pos_a'],'Wrong subset semantics')
    records={r['job_id']:r for r in manifest['records']};payloads={r['job_id']:r['payload_sha256'] for r in r4['cache_evidence']}
    states=defaultdict(dict);rows={r['job_id']:r for r in r6['rows'] if r['position']=='pos_b'}
    require(sha(BASE/'probe_directions.npz')==ORIGINAL_SHA,'Original probe changed')
    probes={}
    with np.load(BASE/'probe_directions.npz',allow_pickle=False) as z:
        require(int(z['e2_layer'])==26,'Original E2 layer differs')
        probes['original_e2']=(z['e2_w_mm'].astype(float),z['e2_mid_mm'].astype(float))
    for name,folder,filename,reportname in [('v5',v5,'candidate_v5_direction.npz','development_analysis.json'),('v6',v6,'candidate_v6_direction.npz','factual_analysis.json')]:
        r=read(folder/reportname)
        with np.load(folder/filename,allow_pickle=False) as z:
            require(int(z['layer_one_based'])==26 and str(z['jobs_sha256'])==sha(folder/'jobs.json')==r['jobs_sha256'],'Candidate input/layer identity differs')
            require(hashlib.sha256(z['direction'].tobytes()).hexdigest()==r['fit']['direction_sha256'],'Candidate direction changed')
            probes[name]=(z['direction'].astype(float),z['center'].astype(float))
    with np.load(v4/'selected_layers_1_26.npz',allow_pickle=False) as z:
        for j in jobs:
            if j['cohort']!='fresh':continue
            h=z[j['job_id']];rec=records[j['job_id']]
            require(h.shape==(2,2,4096) and h.dtype==np.float16 and np.isfinite(h).all(),'Invalid selected state')
            require(hashlib.sha256(h.tobytes()).hexdigest()==rec['selected_array_sha256'] and rec['original_npz_sha256']==payloads[j['job_id']],'Selected state provenance differs')
            state=h[0,1].astype(float);states[j['item_id']][j['condition'],j['label']]=state
            for name,key in [('v6','candidate_v6_l26'),('v5','candidate_v5_l26'),('original_e2','original_e2_l26')]:
                w,center=probes[name]
                require(abs(float(np.dot(state-center,w))-rows[j['job_id']][key])<1e-8,'Original score reproduction mismatch')
    require(len(states)==8,'Expected eight calibration items')
    sources=[v4/'jobs.json',v4/'selected_layers_1_26.npz',v4/'selected_layer_manifest.json',v4/'benchmark_validation.json',v5/'candidate_v5_direction.npz',v5/'development_analysis.json',v6/'candidate_v6_direction.npz',v6/'factual_analysis.json',BASE/'probe_directions.npz']
    return dict(states),probes,{str(p.relative_to(ROOT)):sha(p) for p in sources}

def main():
    states,probes,sources=verify_and_load();items=sorted(states)
    basis,vectors,span=learn_nuisance_span(states,items);reports={};arrays={'nuisance_basis':basis}
    for c,v in vectors.items():arrays['nuisance_'+c]=v
    for name,(w,center) in probes.items():
        residual,normalized,projection=project_direction(w,basis)
        require(normalized is not None,'Projection annihilated '+name+'; do not fabricate direction')
        before=summaries(score(states,items,w,center));raw=summaries(score(states,items,residual,center));after=summaries(score(states,items,normalized,center))
        arrays[name+'_projected_raw']=residual;arrays[name+'_projected_unit']=normalized;arrays[name+'_center']=center
        folds=[];oof_raw={};oof_unit={}
        for heldout in items:
            train=[i for i in items if i!=heldout];fold_basis,fold_vectors,fold_span=learn_nuisance_span(states,train)
            rw,nw,meta=project_direction(w,fold_basis);require(nw is not None,'Undefined fold '+name+heldout)
            oof_raw.update(score(states,[heldout],rw,center));oof_unit.update(score(states,[heldout],nw,center))
            folds.append(dict(heldout_item=heldout,calibration_items=train,rank=fold_span['rank'],condition_number=fold_span['condition_number'],projection=meta,
                corrected_cosines_with_heldout_control_vectors={c:cosine(nw,np.mean([states[heldout][c,l]-states[heldout]['base',l] for l in (0,1)],axis=0)) for c in NUISANCES}))
        reports[name]=dict(projection=projection,before=before,projected_raw=raw,projected_unit=after,
            before_nuisance_cosines={c:cosine(w,v) for c,v in vectors.items()},after_nuisance_cosines={c:cosine(normalized,v) for c,v in vectors.items()},
            leave_one_item_out=dict(folds=folds,raw=summaries(oof_raw,False),unit=summaries(oof_unit,False),interpretation='Held-out item excluded from nuisance estimation only. The candidate itself and design have already seen this development set; not independent construct validation. Different folds have different directions; per-item gaps and effects only.'))
    OUT.mkdir(exist_ok=True)
    weightpath=OUT/'nuisance_corrected_candidates.npz'
    if weightpath.exists():
        with np.load(weightpath,allow_pickle=False) as old:require(set(old.files)==set(arrays) and all(np.array_equal(old[k],v) for k,v in arrays.items()),'Refusing different candidate overwrite')
    else:np.savez_compressed(weightpath,**arrays)
    report=dict(status='completed_local_development_nuisance_projection',primary_candidate='v6',layer_one_based=26,position='pos_b',calibration_items=items,calibration_states=64,nuisances=list(NUISANCES),content_projection_performed=False,nuisance_span=span,candidates=reports,source_sha256=sources,corrected_candidates_sha256=sha(weightpath),source_hashes_unchanged=all(sha(ROOT/p)==h for p,h in sources.items()),model_forward_count=0,paid_resources_started=False,rq3_ready=False,independent_validation_pass=False,limitations=['In-sample nuisance orthogonality is algebraically guaranteed and cannot establish generalisation.','Calibration examples and candidates have been previously inspected; OOF nuisance checks do not make them fresh.','Removing a linear mean-effect span does not remove all nonlinear or item-specific nuisance information.','No content direction is removed. Evaluation-versus-content remains unresolved.','Raw projected and unit-normalized outputs are both retained; no sign flip, layer search, or favourable candidate selection.','Raw score levels and cross-fold pooled AUROC are not claimed calibrated or comparable.'])
    (OUT/'local_comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    for name,r in reports.items():
        print(name,'retained_norm',r['projection']['retained_norm_fraction'],'pairs before/after/LOIO',[r['before']['pair_summaries']['base']['positive_pairs'],r['projected_unit']['pair_summaries']['base']['positive_pairs'],r['leave_one_item_out']['unit']['pair_summaries']['base']['positive_pairs']])
    print('rank',span['rank'],'condition',span['condition_number'],'sources unchanged',report['source_hashes_unchanged'])

if __name__=='__main__':main()
