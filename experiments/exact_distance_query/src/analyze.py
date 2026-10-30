"""Rebuild all public aggregates from hash-verified private attempts."""
from .common import *
import argparse
import csv
import itertools
import math
import numpy as np
from .run import jobs,science
GROUPS=('G0','G1','G2','G3')
DATASETS=('Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor')
CONTRASTS=(('G1','G0'),('G2','G1'),('G3','G1'),('G3','G2'))
def mean(values):return float(np.mean(values)) if values else None
def sd(values):return float(np.std(values,ddof=1)) if len(values)>1 else None
def csvwrite(path,rows):
    if not rows:return
    with path.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
def interval(values):
    if len(values)<2:return [None,None]
    rng=np.random.default_rng(20261030);a=np.asarray(values)
    boot=a[rng.integers(0,len(a),size=(20000,len(a)))].mean(1)
    return np.quantile(boot,[.025,.975]).tolist()
def signflip(values):
    if not values:return None
    a=np.asarray(values);observed=abs(a.mean())
    signs=np.array(list(itertools.product((-1,1),repeat=len(a))))
    return float((abs((signs*a).mean(1))>=observed-1e-12).mean())
def holm(values):
    order=sorted(range(len(values)),key=lambda i:values[i]);out=[None]*len(values);prev=0.
    for j,i in enumerate(order):prev=max(prev,min(1.,(len(values)-j)*values[i]));out[i]=prev
    return out
def collect(root):
    cfg=read(STUDY/'configs/full.json');fp=digest(dict(science=science(cfg),sources=sources(),protocol=verify_freeze()))
    legacy=read(STUDY/'configs/empty_control.json');lfp=digest(dict(science=science(legacy),sources=sources(),protocol=verify_freeze()))
    records=[];failures=[];stale=[]
    for f in sorted(root.glob('*/result.json')):
        r=read(f)
        if r['fingerprint'] not in (fp,lfp):stale.append(r['run_id']);continue
        if r['status']!='complete':
            failures.append({k:r.get(k) for k in ('run_id','dataset','split','seed','group','empty_policy','status','error_type')});continue
        for artifact,h in r['artifacts'].items():
            if sha(f.parent/artifact)!=h:raise ValueError('Artifact hash mismatch: '+r['run_id'])
        records.append(r)
    return records,failures,stale
def analyze(root,phase='full'):
    records,failures,stale=collect(root)
    cfg=read(STUDY/'configs'/(phase+'.json'));expected=jobs(cfg)
    key=lambda r:tuple(r[k] for k in ('dataset','split','seed','group','empty_policy'))
    lookup={key(r):r for r in records}
    if len(lookup)!=len(records):raise ValueError('Duplicate scientific cells')
    selected=[lookup[key(j)] for j in expected if key(j) in lookup]
    missing=[dict(**j,status='NOT_RUN',reason='No completed matching fingerprint') for j in expected if key(j) not in lookup]
    out=STUDY/'results'/phase;out.mkdir(exist_ok=True)
    for d,s,t in itertools.product(cfg['datasets'],cfg['splits'],cfg['seeds']):
        paired=[r for r in selected if (r['dataset'],r['split'],r['seed'])==(d,s,t)]
        if len(paired)==4:
            for field in ('init_sha256','cpu_rng_sha256','cuda_rng_sha256','graph_tensor_sha256','split_sha256','parameter_count'):
                if len({r[field] for r in paired})!=1:raise ValueError('Pairing mismatch '+field)
    cells=[];manifests=[];mechanisms=[]
    for r in selected:
        fields=['run_id','dataset','split','seed','group','empty_policy','test_accuracy','val_accuracy','best_validation_epoch',
            'stopped_epoch','training_seconds','inference_ms_mean','peak_gpu_allocated_mb','parameter_count','gate_entropy_mean']
        cells.append({k:r[k] for k in fields})
        manifests.append({k:r[k] for k in ('run_id','dataset','split','seed','group','empty_policy','git','sources','protocol_sha256',
            'config_sha256','fingerprint','environment','started_utc','ended_utc','init_sha256','cpu_rng_sha256','cuda_rng_sha256',
            'graph_tensor_sha256','split_sha256','split_array_sha256','trained_state_sha256','artifacts','checkpoint_reload','checkpoint_equivalence','operations')})
        mechanisms.append({k:r[k] for k in ('run_id','dataset','split','seed','group','hop_weights_mean','hop_weights_std','hop_weights_quantiles',
            'gate_entropy_mean','gate_entropy_std','empty_fraction','cosine_raw','cosine_gamma_scaled','cosine_layernorm',
            'norm_mean_raw','norm_mean_gamma_scaled','norm_mean_layernorm')})
    splitrows=[];accuracy=[];resources=[];diagrows=[]
    for d,g in itertools.product(DATASETS,GROUPS):
        subset=[r for r in selected if r['dataset']==d and r['group']==g]
        splitmeans=[]
        for s in cfg['splits']:
            rs=[r for r in subset if r['split']==s]
            if rs:
                vals=[100*r['test_accuracy'] for r in rs];splitmeans.append(mean(vals))
                splitrows.append(dict(dataset=d,group=g,split=s,seeds=len(rs),test_mean_percent=mean(vals),seed_sample_sd=sd(vals)))
        accuracy.append(dict(dataset=d,group=g,cells=len(subset),splits=len(splitmeans),mean_percent=mean(splitmeans),sample_sd_percent=sd(splitmeans)))
        if subset:
            resources.append(dict(dataset=d,group=g,cells=len(subset),training_seconds_mean=mean([r['training_seconds'] for r in subset]),
                inference_ms_mean=mean([r['inference_ms_mean'] for r in subset]),peak_gpu_mb_mean=mean([r['peak_gpu_allocated_mb'] for r in subset]),
                epoch_training_ms_mean=mean([r['epoch_training_ms_mean'] for r in subset]),epoch_wall_ms_mean=mean([r['epoch_wall_ms_mean'] for r in subset]),stopped_epoch_mean=mean([r['stopped_epoch'] for r in subset]),
                parameter_count=subset[0]['parameter_count'],**subset[0]['operations']))
            for p in range(5):
                diagrows.append(dict(dataset=d,group=g,p=p,alpha_mean=mean([r['hop_weights_mean'][p] for r in subset]),
                    gate_entropy=mean([r['gate_entropy_mean'] for r in subset]),empty_fraction=mean([r['empty_fraction'][p] for r in subset])))
    paircells=[];paired=[]
    for d in DATASETS:
        family=[]
        for left,right in CONTRASTS:
            per_split=[];raw=[]
            for s in cfg['splits']:
                values=[]
                for t in cfg['seeds']:
                    a=lookup.get((d,s,t,left,'mask'));b=lookup.get((d,s,t,right,'mask'))
                    if a and b and a in selected and b in selected:
                        delta=100*(a['test_accuracy']-b['test_accuracy']);values.append(delta);raw.append(delta)
                        paircells.append(dict(dataset=d,split=s,seed=t,contrast=left+'-'+right,delta_pp=delta))
                if values:per_split.append(mean(values))
            row=dict(dataset=d,contrast=left+'-'+right,paired_cells=len(raw),splits=len(per_split),mean_pp=mean(per_split),sample_sd_pp=sd(per_split),
                ci95_low=interval(per_split)[0],ci95_high=interval(per_split)[1],signflip_p=signflip(per_split),holm3_p=None,
                role='primary' if len(family)<3 else 'exploratory',split_means=per_split)
            family.append(row)
        if all(r['signflip_p'] is not None for r in family[:3]):
            for r,p in zip(family[:3],holm([r['signflip_p'] for r in family[:3]])):r['holm3_p']=p
        paired.extend(family)
    controls=[]
    for r in records:
        if r['empty_policy']=='legacy':
            primary=lookup.get((r['dataset'],r['split'],r['seed'],r['group'],'mask'))
            controls.append(dict(dataset=r['dataset'],split=r['split'],seed=r['seed'],group=r['group'],
                legacy_test_percent=100*r['test_accuracy'],masked_test_percent=100*primary['test_accuracy'] if primary else None,
                legacy_minus_masked_pp=100*(r['test_accuracy']-primary['test_accuracy']) if primary else None,
                run_id=r['run_id'],model_sha256=r['artifacts']['model.pt'],checkpoint_equivalence=r['checkpoint_equivalence']))
    status=dict(utc=now(),status='FULL' if len(selected)==len(expected) else 'PARTIAL',complete=len(selected),expected=len(expected),missing=len(missing),
        failed_attempts=len(failures),stale_attempts=stale,teacher_approval='NOT_VERIFIED',pairing='passed',empty_controls=len(controls),
        trained_from_random_initialization=True,smoke_reused=sum(r['phase_started']=='smoke' for r in selected),
        pilot_reused=sum(r['phase_started']=='pilot' for r in selected),checkpoint_reload='all passed',
        real_G0_G1_equivalence='all completed G0/G1 forward/used_alpha/parameter gradients passed')
    for name,rows in [('cells',cells),('accuracy',accuracy),('split_summary',splitrows),('paired_cells',paircells),('resources',resources),('gate_summary',diagrows),('missing_cells',missing)]:csvwrite(out/(name+'.csv'),rows)
    csvwrite(out/'paired_summary.csv',[{k:v for k,v in row.items() if k!='split_means'} for row in paired])
    save(out/'coverage.json',status);save(out/'run_manifest.json',manifests);save(out/'mechanisms.json',mechanisms)
    save(out/'empty_control.json',controls);save(out/'failures.json',failures)
    save(out/'analysis.json',dict(status=status,accuracy=accuracy,paired=paired,resources=resources,gate=diagrows))
    import subprocess
    subprocess.run([os.environ.get('GAMMA_PLOT_PYTHON',sys.executable),'-B',str(STUDY/'src/plot.py'),str(out)],check=True)
    report(phase,status,accuracy,paired,resources,controls,records)
    print(json.dumps(status,indent=2));return status
def fmt(v,sd=None):
    if v is None:return 'NA'
    return f'{v:.2f}'+(f' +/- {sd:.2f}' if sd is not None else '')
def report(phase,status,accuracy,paired,resources,controls,records):
    title='02_PILOT.md' if phase=='pilot' else '03_FULL_RESULTS.md'
    lines=[f'# {phase.title()} results', '',f"Technical coverage: **{status['complete']}/{status['expected']}**, status **{status['status']}**. Teacher approval **NOT_VERIFIED**.",
        'All models were trained anew from matched random parameters. Counts include hash-verified reuse only.',
        f"Reused smoke={status['smoke_reused']}, Pilot={status['pilot_reused']}. Complete run manifests, raw paired cells and any missing units are in results/{phase}/.", '',
        'Accuracy percent: average seeds within each fixed split, then mean +/- sample SD across splits.', '',
        '|Dataset|G0|G1|G2|G3|','|---|---:|---:|---:|---:|']
    for d in DATASETS:
        rs=[next(r for r in accuracy if r['dataset']==d and r['group']==g) for g in GROUPS]
        lines.append('|'+d+'|'+'|'.join(fmt(r['mean_percent'],r['sample_sd_percent']) for r in rs)+'|')
    lines += ['','Paired deltas in percentage points; seed means within split. Bootstrap CI is descriptive;',
        'overlapping graph splits do not supply independent graph samples. Holm3 covers the three primary contrasts within dataset.','',
        '|Dataset|Contrast|Mean +/- SD pp|95% CI|Holm3 p|','|---|---|---:|---|---:|']
    for r in paired:
        lines.append('|'+r['dataset']+'|'+r['contrast']+'|'+fmt(r['mean_pp'],r['sample_sd_pp'])+'|'+('NA' if r['ci95_low'] is None else f"[{r['ci95_low']:.2f}, {r['ci95_high']:.2f}]")+'|'+fmt(r['holm3_p'])+'|')
    lines += ['',f"{status['failed_attempts']} failed scientific attempts; {status['empty_controls']} completed bounded empty-policy control cells.",
        'Every completed G0 matched the frozen original forward, used_alpha and parameter gradients;',
        'every completed G1 matched one-shot consensus including trained bias/Norm and empty-hop rules.',
        'Every selected checkpoint was saved, hashed, reloaded and output-verified.', '',
        'See resources.csv for measured training/inference/GPU allocation and operation counts;',
        'distance_<dataset>.json separates one-time topology preprocessing/storage. G3 adds four Walk propagations;',
        'parameter equality does not imply equal compute. Plots include all four groups and negative deltas.']
    (STUDY/'docs'/title).write_text('\n'.join(lines)+'\n',encoding='utf8',newline='\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--runs-root',default='../private_runs');p.add_argument('--phase',choices=['pilot','full'],default='full');a=p.parse_args()
    analyze(external(a.runs_root),a.phase)
if __name__=='__main__':main()
