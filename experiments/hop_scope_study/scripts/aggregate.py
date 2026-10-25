"""Public scalar-only aggregation, paired inference and plotting; no node arrays."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,REPO,read,save,now,external,sources,digest
from run import verified,jobs,fingerprint
import argparse
import collections
import csv
import itertools
import json
import math
import numpy as np


def statistics(values):
    values=np.asarray(values,dtype=float)
    return dict(n=len(values),mean=float(values.mean()) if len(values) else None,
                sample_sd=float(values.std(ddof=1)) if len(values)>1 else None)


def paired(values):
    a=np.asarray(values,dtype=float);result=statistics(a)
    if not len(a):return result
    rng=np.random.default_rng(20261025)
    means=a[rng.integers(0,len(a),(20000,len(a)))].mean(1)
    result.update(ci95_low=float(np.quantile(means,.025)),ci95_high=float(np.quantile(means,.975)))
    signs=np.array(list(itertools.product([-1,1],repeat=len(a))))
    result['p_sign_flip']=float((np.abs((signs*a).mean(1))>=abs(a.mean())-1e-12).mean())
    return result


def holm(rows):
    ordered=sorted(rows,key=lambda row:row['p_sign_flip']);running=0
    for i,row in enumerate(ordered):
        running=max(running,min(1,(len(rows)-i)*row['p_sign_flip']));row['p_holm']=running


def csv_write(name,rows):
    if not rows:return
    columns=list(dict.fromkeys(k for row in rows for k in row))
    with (STUDY/'results'/name).open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)


def fmt(row):
    if row['mean'] is None:return 'NOT_RUN'
    sd='NA' if row['sample_sd'] is None else f"{row['sample_sd']:.2f}"
    return f"{row['mean']:.2f} +/- {sd}"


def collect(run_root):
    complete=[];attempts=[]
    for folder in sorted((run_root/'runs').glob('*')):
        meta=read(folder/'metadata.json')
        public={k:v for k,v in meta.items() if k not in ('traceback','failure_reason')}
        if 'failure_reason' in meta:
            public['failure_reason']='See private terminal log; type recorded above'
        public['artifacts_verified']=verified(folder)
        attempts.append(public)
        if public['artifacts_verified']:
            r=read(folder/'result.json');r.update(started_utc=meta['started_utc'],finished_utc=meta['finished_utc'],
                                                 wall_seconds=meta['wall_seconds'],phase=meta['phase'],
                                                 device=meta['environment']['gpu'],environment=meta['environment'])
            complete.append(r)
    return complete,attempts


def pilot_summary(complete,attempts):
    rs=[r for r in complete if r['phase']=='pilot']
    rows=[]
    for d in ('Texas','Chameleon'):
        for x in (1,3,5):
            subset=[r for r in rs if r['dataset']==d and r['max_gating_hop']==x]
            rows.append(dict(dataset=d,x=x,**statistics([100*r['test_accuracy'] for r in subset])))
    text='# Pilot results and decision\n\n'
    text+=f"Recorded {now()}. {len(rs)}/12 required Pilot cells complete; all successful checkpoints reloaded and independently checked.\n\n"
    text+='| Dataset | x | n | Test accuracy %, mean +/- sample SD |\n| --- | --- | --- | --- |\n'
    for row in rows:text+=f"| {row['dataset']} | {row['x']} | {row['n']} | {fmt(row)} |\n"
    text+='\nPilot uses split0/1 only; these preliminary scores do not determine hyperparameters or remove datasets.\n\n'
    for d in ('Texas','Chameleon'):
        times=[r['wall_seconds'] for r in rs if r['dataset']==d]
        if times:text+=f"{d}: mean wall time {np.mean(times):.2f}s per run (range {min(times):.2f}-{max(times):.2f}s).\n\n"
    bad=[a for a in attempts if a['phase']=='pilot' and a['status']!='complete']
    text+=f"Pilot failures: {len(bad)}. No OOM or nonfinite result is claimed unless present in the attempt ledger.\n\n"
    text+='All matched cells share complete initialization hashes and graph/split/protocol/source fingerprints. The full500/50 protocol is retained. '
    text+='**GO to Full**: remaining288 cells plus all full-checkpoint diagnostics; reuse the12 verified Pilot cells without retraining. ' if len(rs)==12 else '**NOT READY**: finish missing Pilot cells first. '
    text+='Throughput is hardware/runtime dependent; larger graphs may cost more than this Pilot. No scientific changes were made after Pilot.\n'
    (STUDY/'docs/02_PILOT.md').write_text(text,encoding='utf8')
    csv_write('pilot_summary.csv',rows)


def cell_status(result, relevant):
    if result:return 'complete'
    if any(t['status']=='running' for t in relevant):return 'running'
    if any(t['status'] in ('failed','interrupted') for t in relevant):return 'failed'
    return 'invalid_artifacts' if relevant else 'not_run'


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-root',type=Path,required=True)
    p.add_argument('--data-root',type=Path,required=True);p.add_argument('--pilot',action='store_true');a=p.parse_args()
    run_root=external(a.run_root);data_root=external(a.data_root)
    complete,attempts=collect(run_root)
    by_cell={}
    for r in complete:
        key=(r['dataset'],r['split_id'],r['max_gating_hop'])
        if key in by_cell:raise ValueError('Duplicate verified cell; explicit adjudication required')
        by_cell[key]=r
    # Full-state, graph, split, RNG and protocol equality within each paired group.
    for dataset,split in {(r['dataset'],r['split_id']) for r in complete}:
        group=[r for r in complete if r['dataset']==dataset and r['split_id']==split]
        for key in ('full_init_sha256','cpu_rng_sha256','cuda_rng_sha256','graph_tensor_sha256',
                    'split_sha256','parameter_count','protocol_sha256'):
            if len({str(r[key]) for r in group})!=1:raise ValueError('Pairing failed: '+key)
    if a.pilot:pilot_summary(complete,attempts)
    cfg=read(STUDY/'configs/full.json');manifest=read(data_root/'manifest.json');matrix=[]
    for job in jobs(cfg):
        key=(job['dataset'],job['split_id'],job['max_gating_hop']);r=by_cell.get(key)
        relevant=[t for t in attempts if t['job']==job]
        matrix.append(dict(**job,status=cell_status(r,relevant),
                           run_id=r['run_id'] if r else None,attempts=len(relevant),
                           fingerprint_matches_current=bool(r and r['fingerprint']==fingerprint(job,cfg,sources(),manifest))))
    summary=[];deltas=[];selection=[];cost=[]
    for d in cfg['datasets']:
        family=[]
        for x in range(1,6):
            group=[r for r in complete if r['dataset']==d and r['max_gating_hop']==x]
            for metric in ('test','val'):
                summary.append(dict(dataset=d,x=x,metric=metric,unit='percent',
                                    **statistics([100*r[metric+'_accuracy'] for r in group])))
            pair=[100*(r['test_accuracy']-by_cell[d,r['split_id'],5]['test_accuracy'])
                  for r in group if (d,r['split_id'],5) in by_cell]
            row=dict(dataset=d,x=x,unit='pp',**paired(pair));deltas.append(row)
            if x<5 and pair:family.append(row)
            if group:
                cost.append(dict(dataset=d,x=x,n=len(group),parameter_count=group[0]['parameter_count'],
                    training_seconds_mean=float(np.mean([r['training_seconds'] for r in group])),
                    wall_seconds_mean=float(np.mean([r['wall_seconds'] for r in group])),
                    inference_ms_mean=float(np.mean([r['inference_ms_mean'] for r in group])),
                    peak_allocated_mib_mean=float(np.mean([r['peak_gpu_allocated_mb'] for r in group])),
                    peak_increment_mib_mean=float(np.mean([r['peak_training_increment_mb'] for r in group])),
                    stopped_epoch_mean=float(np.mean([r['stopped_epoch'] for r in group])),
                    attempts=sum(t['job']['dataset']==d and t['job']['max_gating_hop']==x for t in attempts),
                    failed_attempts=sum(t['job']['dataset']==d and t['job']['max_gating_hop']==x and t['status'] in ('failed','interrupted') for t in attempts)))
        holm(family)
        for split in range(10):
            group=[by_cell.get((d,split,x)) for x in range(1,6)]
            if not all(group):continue
            best=min(group,key=lambda r:(-r['val_accuracy'],r['max_gating_hop']))
            selection.append(dict(dataset=d,split_id=split,seed=42+split,x_star=best['max_gating_hop'],
                                  val_accuracy_percent=100*best['val_accuracy'],test_accuracy_percent=100*best['test_accuracy'],
                                  delta_vs_full_pp=100*(best['test_accuracy']-group[-1]['test_accuracy']),run_id=best['run_id']))
    eval_reports=[];eval_rows=[]
    for path in sorted((run_root/'eval').glob('*/result.json')):
        e=read(path);eval_reports.append(e)
        if e['status']!='complete':continue
        for row in e['rows']:
            eval_rows.append(dict(dataset=e['dataset'],split_id=e['split_id'],seed=e['seed'],
                source_run_id=e['source_run_id'],checkpoint_sha256=e['checkpoint_sha256'],**row))
    eval_summary=[]
    for d in cfg['datasets']:
        for x in range(1,6):
            group=[e for e in eval_rows if e['dataset']==d and e['max_gating_hop']==x]
            eval_summary.append(dict(dataset=d,x=x,unit='percent',**statistics([100*e['test_accuracy'] for e in group])))
    eval_by_cell={(e['dataset'],e['split_id'],e['max_gating_hop']):e for e in eval_rows}
    posthoc_delta=[];posthoc_vs_retrain=[]
    for d in cfg['datasets']:
        for x in range(1,6):
            group=[e for e in eval_rows if e['dataset']==d and e['max_gating_hop']==x]
            values=[100*(e['test_accuracy']-eval_by_cell[d,e['split_id'],5]['test_accuracy'])
                    for e in group if (d,e['split_id'],5) in eval_by_cell]
            posthoc_delta.append(dict(dataset=d,x=x,unit='pp',**paired(values)))
            values=[100*(e['test_accuracy']-by_cell[d,e['split_id'],x]['test_accuracy'])
                    for e in group if (d,e['split_id'],x) in by_cell]
            posthoc_vs_retrain.append(dict(dataset=d,x=x,unit='pp',**paired(values)))
    csv_write('posthoc_delta.csv',posthoc_delta)
    csv_write('posthoc_minus_retrain.csv',posthoc_vs_retrain)
    for name,rows in [('accuracy_summary.csv',summary),('paired_delta.csv',deltas),('validation_selection.csv',selection),
                      ('resource_summary.csv',cost),('run_matrix.csv',matrix),('posthoc_summary.csv',eval_summary),
                      ('posthoc_per_run.csv',[{k:v for k,v in row.items() if k!='hop_weights_mean'} for row in eval_rows])]:
        csv_write(name,rows)
    for name,rows in [('per_run.jsonl',complete),('attempts.jsonl',attempts),('posthoc.jsonl',eval_reports)]:
        (STUDY/'results'/name).write_text(''.join(json.dumps(row,allow_nan=False)+'\n' for row in rows),encoding='utf8')
    status=dict(generated_utc=now(),status='FULL' if len(complete)==300 else 'PARTIAL',
                primary_complete=len(complete),primary_expected=300,primary_failed_cells=sum(r['status']=='failed' for r in matrix),
                primary_not_run=sum(r['status']=='not_run' for r in matrix),primary_running=sum(r['status']=='running' for r in matrix),attempts=len(attempts),
                failed_attempts=sum(t['status'] in ('failed','interrupted') for t in attempts),
                posthoc_checkpoints=sum(e['status']=='complete' for e in eval_reports),posthoc_evaluations=len(eval_rows),
                pairing_checks_passed=True,current_fingerprints_match=all(r['fingerprint_matches_current'] for r in matrix if r['status']=='complete'))
    save(STUDY/'results/status.json',status)
    save(STUDY/'results/analysis.json',dict(status=status,accuracy=summary,paired_delta=deltas,selection=selection,
                                          resources=cost,posthoc=eval_summary,posthoc_delta=posthoc_delta,posthoc_minus_retrain=posthoc_vs_retrain))
    report='# Fixed-propagation / variable-routing results\n\n'
    report+=f"**{status['status']}**: {len(complete)}/300 primary cells; {status['failed_attempts']} failed/incomplete attempts; {status['primary_not_run']} not-run cells. Post-hoc {len(eval_rows)}/300 evaluations from {status['posthoc_checkpoints']}/60 checkpoints. Generated {status['generated_utc']}.\n\n"
    report+='Test accuracy %, equal-weight split mean +/- sample SD (ddof1); n in the CSVs. Propagation fixed0..5, routing active0..x.\n\n| Dataset | x1 | x2 | x3 | x4 | x5 |\n| --- | --- | --- | --- | --- | --- |\n'
    for d in cfg['datasets']:
        entries=[next(r for r in summary if r['dataset']==d and r['x']==x and r['metric']=='test') for x in range(1,6)]
        report+='| '+d+' | '+' | '.join(fmt(r) for r in entries)+' |\n'
    report+='\nValidation accuracy %, same validation-best checkpoints, mean +/- sample SD:\n\n| Dataset | x1 | x2 | x3 | x4 | x5 |\n| --- | --- | --- | --- | --- | --- |\n'
    for d in cfg['datasets']:
        entries=[next(r for r in summary if r['dataset']==d and r['x']==x and r['metric']=='val') for x in range(1,6)]
        report+='| '+d+' | '+' | '.join(fmt(r) for r in entries)+' |\n'
    report+='\nPaired test delta vs x5, pp, mean +/- sample SD:\n\n| Dataset | x1 | x2 | x3 | x4 |\n| --- | --- | --- | --- | --- |\n'
    for d in cfg['datasets']:
        entries=[next(r for r in deltas if r['dataset']==d and r['x']==x) for x in range(1,5)]
        report+='| '+d+' | '+' | '.join(fmt(r) for r in entries)+' |\n'
    report+='\nValidation-based selection (ties smallest x), evaluated on test only after selection:\n\n| Dataset | Selected x counts | Selected test % | Delta vs full pp |\n| --- | --- | --- | --- |\n'
    for d in cfg['datasets']:
        group=[r for r in selection if r['dataset']==d]
        if group:report+=f"| {d} | {dict(sorted(collections.Counter(r['x_star'] for r in group).items()))} | {fmt(statistics([r['test_accuracy_percent'] for r in group]))} | {fmt(statistics([r['delta_vs_full_pp'] for r in group]))} |\n"
    significant=[r for r in deltas if r.get('p_holm',1)<.05]
    report+=f"\nExploratory Holm-within-dataset contrasts below0.05: {len(significant)}/24. Full intervals and unadjusted/corrected p values are in paired_delta.csv. Overlapping same-graph splits are not independent datasets.\n\n"
    report+='Post-hoc test accuracy %, from frozen x5 checkpoints (distinct from retraining):\n\n| Dataset | x1 | x2 | x3 | x4 | x5 |\n| --- | --- | --- | --- | --- | --- |\n'
    for d in cfg['datasets']:
        entries=[next(r for r in eval_summary if r['dataset']==d and r['x']==x) for x in range(1,6)]
        report+='| '+d+' | '+' | '.join(fmt(r) for r in entries)+' |\n'
    report+='\nPost-hoc delta vs full and paired post-hoc-minus-retrain are exported separately in posthoc_delta.csv and posthoc_minus_retrain.csv; these are exploratory interventions with distribution mismatch.\n\n'
    report+='| Dataset | Parameters (all x) | Wall seconds x1 / x5 | GPU peak MiB x1 / x5 | Failed / attempts |\n| --- | --- | --- | --- | --- |\n'
    for d in cfg['datasets']:
        low=next((r for r in cost if r['dataset']==d and r['x']==1),None)
        high=next((r for r in cost if r['dataset']==d and r['x']==5),None)
        cells=[r for r in cost if r['dataset']==d]
        if low and high:
            report+=f"| {d} | {low['parameter_count']} | {low['wall_seconds_mean']:.2f} / {high['wall_seconds_mean']:.2f} | {low['peak_allocated_mib_mean']:.2f} / {high['peak_allocated_mib_mean']:.2f} | {sum(r['failed_attempts'] for r in cells)} / {sum(r['attempts'] for r in cells)} |\n"
    report+='\nWall duration includes data checks, training, saving, reload verification and benchmark; training-only and incremental GPU memory are in resource_summary.csv. CPU RSS/extra host memory and monetary cost are UNKNOWN.\n\n'
    report+='Validation curves: accuracy_summary.csv. Resource costs: resource_summary.csv (MiB and seconds; fixed propagation, no claimed propagation savings). Full run matrix and scalar evidence: results/. No test-based best-x selection. Validation reuse for epoch/x selection can bias the selected test estimate.\n\n'
    report+='![Accuracy](../figures/accuracy_vs_x.png)\n\n![Paired delta](../figures/paired_delta.png)\n\n![Retrain and post-hoc](../figures/posthoc_vs_retrain.png)\n'
    (STUDY/'docs/03_RESULTS.md').write_text(report,encoding='utf8')
    print(json.dumps(status,indent=2))
    return 0

if __name__=='__main__':sys.exit(main())
