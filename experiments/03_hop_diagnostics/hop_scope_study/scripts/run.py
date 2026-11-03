"""Paired, resumable real executions; immutable attempts and checkpoint checks."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,REPO,now,sha,save,read,digest,git_state,sources,external
import argparse
import contextlib
import gc
import json
import time
import traceback
import uuid
import platform
import numpy as np
import torch
from src.model import ScopeNet
from src.data import DATASETS,load_graph
from research.src.factory import seed_all,configure_determinism
from research.src.paths import tensor_hash
from research.src.train import run_one


def jobs(config):
    for name in config['datasets']:
        if name not in DATASETS:
            raise ValueError('Unknown dataset')
        for split in config['splits']:
            if type(split) is not int or not 0<=split<10:
                raise ValueError('Bad split')
            xs=config['max_gating_hops']
            for x in (xs if split%2==0 else list(reversed(xs))):
                if type(x) is not int or not 1<=x<=5:
                    raise ValueError('Bad routing scope')
                yield dict(dataset=name,split_id=split,seed=42+split,max_propagation_hop=5,max_gating_hop=x)


def fingerprint(job,config,source_hashes,manifest):
    return digest(dict(job=job,protocol=config['protocol'],sources=source_hashes,
                       data=manifest['datasets'][job['dataset']]))


def verified(folder,expected=None):
    try:
        meta=read(folder/'metadata.json'); result=read(folder/'result.json')
        if meta['status']!='complete' or result['status']!='complete': return False
        if expected and meta['fingerprint']!=expected: return False
        return all((folder/name).is_file() and sha(folder/name)==value
                   for name,value in meta['artifacts'].items())
    except (KeyError,ValueError,OSError):
        return False


def execute(job,config,config_path,data_root,run_root,source_hashes,manifest):
    fp=fingerprint(job,config,source_hashes,manifest)
    for folder in sorted(run_root.glob('runs/*')):
        if verified(folder,fp):
            print(json.dumps(dict(status='verified_skip',job=job,run_id=folder.name)),flush=True)
            return 0
    run_id=now().replace(':','').replace('+','_')+'-'+uuid.uuid4().hex[:10]
    folder=run_root/'runs'/run_id;folder.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter()
    state=git_state()
    meta=dict(run_id=run_id,status='running',phase=config['phase'],started_utc=now(),git=state,
              source_sha256=source_hashes,config_sha256=sha(config_path),protocol_sha256=digest(config['protocol']),
              fingerprint=fp,job=job,device='cuda',output_path='runs/'+run_id,
              teacher_approval='NOT_VERIFIED',monetary_cost='UNKNOWN',
              environment=dict(python=sys.version.split()[0],torch=torch.__version__,
                               cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),
                               platform=platform.platform(),cpu_threads=torch.get_num_threads()))
    save(folder/'config.json',config);save(folder/'metadata.json',meta)
    code=0
    try:
        with (folder/'terminal.log').open('w',encoding='utf8') as log:
            with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
                graph,data,split=load_graph(data_root,job['dataset'],job['split_id'],'cuda')
                gc.collect();torch._C._cuda_clearCublasWorkspaces();torch.cuda.empty_cache()
                seed_all(job['seed'])
                model=ScopeNet(graph.num_node_features,32,int(graph.y.max())+1,
                               max_propagation_hop=5,max_gating_hop=job['max_gating_hop'],num_iterations=2).to('cuda')
                assert len(model.convs)==1 and model.convs[0].powers==list(range(6))
                initial=tensor_hash(model.state_dict())
                seed_all(job['seed'])
                model_kwargs=dict(in_channels=graph.num_node_features,hidden_channels=32,
                                  out_channels=int(graph.y.max())+1,max_propagation_hop=5,
                                  max_gating_hop=job['max_gating_hop'],num_iterations=2)
                info=dict(**job,run_id=run_id,git=state,model_kwargs=model_kwargs,
                          powers=list(range(6)),actual_gamma_layers=1,r=2,routing_method='dot_scope_mask',
                          full_init_sha256=initial,cpu_rng_sha256=tensor_hash({'rng':torch.get_rng_state()}),
                          cuda_rng_sha256=tensor_hash({'rng':torch.cuda.get_rng_state()}),
                          graph_tensor_sha256=data['graph_tensor_sha256'],split_sha256=split['sha256'],
                          split_array_sha256=split['array_sha256'],split_seed=102+job['split_id'],
                          config_sha256=sha(config_path),protocol_sha256=digest(config['protocol']),
                          source_sha256=source_hashes,fingerprint=fp)
                report=run_one(model,graph,config['protocol']['training'],info,folder)
                # Reload the actual on-disk checkpoint; check all logits and saved
                # predictions, validation-best metric and unchanged state hash.
                checkpoint=torch.load(folder/'model.pt',map_location='cpu',weights_only=False)
                model.load_state_dict(checkpoint['state_dict']);model.eval()
                with torch.no_grad():
                    logits=model(graph.x,graph.edge_index)
                    if not bool(torch.isfinite(logits).all()): raise FloatingPointError('Nonfinite checkpoint logits')
                    pred=logits.argmax(dim=1).cpu().numpy()
                with np.load(folder/'predictions.npz',allow_pickle=False) as arrays:
                    if not np.array_equal(pred,arrays['predictions']): raise ValueError('Checkpoint prediction mismatch')
                    if not np.array_equal(logits.cpu().numpy(),arrays['log_probs']):
                        raise ValueError('Checkpoint log-probability mismatch')
                    for label in ('train','val','test'):
                        mask=arrays[label+'_mask']
                        actual=float((pred[mask]==arrays['labels'][mask]).mean())
                        if actual!=report[label+'_accuracy']: raise ValueError('Saved accuracy mismatch')
                if tensor_hash(model.state_dict())!=report['trained_state_sha256']:
                    raise ValueError('Reloaded state hash differs')
                report['checkpoint_reload_verified']=True
                report['checkpoint_sha256']=sha(folder/'model.pt')
                save(folder/'result.json',report)
                meta.update(status='complete',full_init_sha256=initial,split_sha256=split['sha256'],
                            graph_tensor_sha256=data['graph_tensor_sha256'],checkpoint_reload_verified=True)
                del model,graph,checkpoint,logits
    except BaseException as error:
        code=1
        meta.update(status='failed',failure_type=type(error).__name__,failure_reason=str(error),
                    traceback=traceback.format_exc())
        with (folder/'terminal.log').open('a',encoding='utf8') as log: log.write(traceback.format_exc())
        if isinstance(error,(KeyboardInterrupt,SystemExit)):
            meta['status']='interrupted'
    meta.update(finished_utc=now(),wall_seconds=time.perf_counter()-start,exit_code=code)
    meta['artifacts']={p.name:sha(p) for p in folder.iterdir() if p.name!='metadata.json' and p.is_file()}
    save(folder/'metadata.json',meta)
    print(json.dumps(dict(run_id=run_id,status=meta['status'],job=job,seconds=meta['wall_seconds'])),flush=True)
    gc.collect();torch.cuda.empty_cache()
    return code


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--data-root',type=Path,required=True)
    p.add_argument('--run-root',type=Path,required=True)
    p.add_argument('--plan',action='store_true')
    p.add_argument('--limit',type=int)
    args=p.parse_args();config=read(args.config);planned=list(jobs(config))
    if args.plan:
        print(json.dumps(dict(cells=len(planned),first=planned[0],last=planned[-1]),indent=2));return 0
    if config['phase'] not in ('pilot','full'): raise ValueError('Use eval_only.py for post-hoc')
    if read(STUDY/'results/validation.json')['status']!='passed': raise RuntimeError('Validation gate not passed')
    if config['phase']=='full' and not (STUDY/'docs/02_PILOT.md').exists():
        raise RuntimeError('Write Pilot summary before Full')
    configure_determinism();torch.set_num_threads(config['protocol']['cpu_threads'])
    data_root=external(args.data_root);run_root=external(args.run_root);run_root.mkdir(parents=True,exist_ok=True)
    manifest=read(data_root/'manifest.json');hashes=sources()
    codes=[]
    for job in planned[:args.limit]:
        codes.append(execute(job,config,args.config,data_root,run_root,hashes,manifest))
    return int(any(codes))

if __name__=='__main__':sys.exit(main())
