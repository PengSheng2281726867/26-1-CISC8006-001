"""Validate coverage and aggregate seeds within split before split summaries."""
import argparse
from collections import defaultdict
import numpy as np
from .common import *
from .statistics import stats,fractions

def collect(inputs):
    cells={};expected=set();failures=[]
    for path in inputs:
        for batch in Path(path).rglob('batch.json'):
            b=read(batch)
            expected.update((j['dataset'],j['split_id'],j['seed'],b['evaluation_set']) for j in b['expected_jobs'])
        for path in Path(path).rglob('metadata.json'):
            m=read(path)
            if m['status']!='complete': failures.append((path,m));continue
            if sha(path.with_name('nodes.npz'))!=m['nodes_sha256']: raise ValueError('Private array hash mismatch')
            j=m['job'];key=(j['dataset'],j['split_id'],j['seed'],m['evaluation_set'])
            if key in cells:
                if cells[key][1]['nodes_sha256']!=m['nodes_sha256']: raise ValueError('Conflicting duplicate cell')
                continue
            cells[key]=(path,m)
    missing=expected-set(cells)
    return cells,missing,failures

def aggregate(rows,groups,metrics):
    buckets=defaultdict(list)
    for row in rows: buckets[tuple(row[k] for k in groups)].append(row)
    out=[]
    for key,rs in sorted(buckets.items()):
        row=dict(zip(groups,key));row['n_units']=len(rs)
        for metric in metrics:
            vs=[r[metric] for r in rs if r.get(metric) is not None]
            row[metric+'_mean']=float(np.mean(vs)) if vs else None
            row[metric+'_sample_sd']=float(np.std(vs,ddof=1)) if len(vs)>1 else None
            row[metric+'_n']=len(vs)
        out.append(row)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',action='append',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    out=Path(args.output)
    if out.exists(): raise ValueError('Refuse to overwrite summary directory')
    out.mkdir(parents=True)
    cells,missing,failures=collect(args.input)
    save(out/'coverage.json',dict(complete=len(cells),missing=[list(k) for k in sorted(missing)],failures=len(failures)))
    if missing or failures: raise ValueError('Incomplete runs; inspect coverage.json')
    hoprows=[];corrows=[];pairrows=[];evidence=[]
    for key,(path,m) in sorted(cells.items()):
        with np.load(path.with_name('nodes.npz')) as z: arr={k:z[k] for k in z.files}
        common=dict(dataset=key[0],split_id=key[1],seed=key[2],evaluation_set=key[3],checkpoint_id=m['checkpoint_id'],n_nodes=m['n_nodes'])
        for mask in ('final_only','full_routing'):
            shared,hs=stats(arr,mask)
            corrows.append(dict(**common,mask_type=mask,**shared))
            hoprows.extend(dict(**common,mask_type=mask,**h) for h in hs)
        diff=arr['full_routing_delta_loss']-arr['final_only_delta_loss']
        for h in range(4):
            pairrows.append(dict(**common,hop=h+1,mean_paired_difference=float(diff[:,h].mean()),median_paired_difference=float(np.median(diff[:,h])),mean_absolute_paired_difference=float(np.abs(diff[:,h]).mean()),sign_reversal_fraction=float(((arr['full_routing_delta_loss'][:,h]>1e-5)&(arr['final_only_delta_loss'][:,h]<-1e-5)|(arr['full_routing_delta_loss'][:,h]<-1e-5)&(arr['final_only_delta_loss'][:,h]>1e-5)).mean()),**fractions(diff[:,h])))
        evidence.append(dict(run_id=m['run_id'],**common,nodes_sha256=m['nodes_sha256'],metadata_sha256=sha(path),checkpoint_sha256=m['checkpoint_sha256'],graph_sha256=m['graph_sha256'],split_sha256=m['split_sha256'],state_before=m['trained_state_sha256'],state_after=m['state_after_sha256'],identity_max_output_error=m['identity_max_output_error'],identity_max_alpha_error=m['identity_max_alpha_error'],wall_seconds=m['wall_seconds'],git_commit=m['git']['commit'],git_dirty=m['git']['dirty'],protocol_sha256=m['protocol_sha256']))
    csv_write(out/'summary_by_checkpoint.csv',hoprows);csv_write(out/'correlations.csv',corrows);csv_write(out/'paired_by_checkpoint.csv',pairrows);csv_write(out/'evidence.csv',evidence)
    metric_h=['mean_alpha','mean_delta','median_delta','rho','accuracy_full','accuracy_masked','accuracy_change','nll_full','nll_masked','flip_fraction','positive_fraction','negative_fraction','near_zero_fraction']
    metric_c=['overall_rho','within_mean','within_median','within_valid','within_undefined_fraction','top1_mean_delta','top1_median_delta','top1_tie_fraction','top1_positive_fraction','top1_negative_fraction','top1_near_zero_fraction']
    metric_p=['mean_paired_difference','median_paired_difference','mean_absolute_paired_difference','sign_reversal_fraction']
    for rows,metrics,extra,name in [(hoprows,metric_h,['mask_type','hop'],'summary'),(corrows,metric_c,['mask_type'],'alignment'),(pairrows,metric_p,['hop'],'paired')]:
        groups=['dataset','evaluation_set']+extra
        split=aggregate(rows,groups+['split_id'],metrics)
        csv_write(out/(name+'_by_split.csv'),split)
        dataset=aggregate(split,groups,[m+'_mean' for m in metrics])
        csv_write(out/(name+'_by_dataset.csv'),dataset)
    print('summarized',len(cells),'cells to',out)
if __name__=='__main__':main()
