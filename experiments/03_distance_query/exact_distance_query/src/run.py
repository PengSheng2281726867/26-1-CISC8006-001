"""Plan, prepare, train and resume without overwriting private attempts."""
from .common import *
import argparse
import contextlib
import itertools
import platform
import time
import traceback
import uuid
import numpy as np
import torch
import torch_geometric
from src.factory import configure_determinism, seed_all
from src.model import GammaNet
from src.paths import tensor_hash
from src.train import train_model, inference_benchmark
from experiments.hop_scope_study.src.data import prepare, load_graph
from .distance import cached, tensors
from .model import build_model

def jobs(cfg):
    return [dict(dataset=d,split=s,seed=t,group=g,empty_policy=cfg['empty_policy'])
        for d,s,t,g in itertools.product(cfg['datasets'],cfg['splits'],cfg['seeds'],cfg['groups'])]
def science(cfg):
    return {k:cfg[k] for k in ('version','K','powers','actual_gamma_layers','hidden_dim','R','training','empty_policy')}
def environment():
    return dict(python=platform.python_version(),platform=platform.platform(),torch=torch.__version__,
        pyg=torch_geometric.__version__,numpy=np.__version__,cuda=torch.version.cuda,
        gpu=torch.cuda.get_device_name() if torch.cuda.is_available() else None,
        threads=torch.get_num_threads(),deterministic=torch.are_deterministic_algorithms_enabled(),tf32=False)
def close(a,b): torch.testing.assert_close(a,b,atol=2e-6,rtol=2e-5)
def equivalence(model,graph,group):
    model.eval()
    if group=='G0':
        ref=GammaNet(graph.num_node_features,32,model.lin.out_features,powers=list(range(5))).to(graph.x.device)
        ref.load_state_dict(model.state_dict());ref.eval()
    elif group=='G1':
        ref,_=build_model(graph.num_node_features,model.lin.out_features,'G1',1,graph.x.device,
            model.convs[0].operators,model.convs[0].valid,model.convs[0].empty_policy,one_shot=True)
        ref.load_state_dict(model.state_dict());ref.eval()
    else: return dict(status='not_applicable')
    left,ld=model(graph.x,graph.edge_index,True);right,rd=ref(graph.x,graph.edge_index,True)
    close(left,right);close(ld[0]['used_alpha'],rd[0]['used_alpha'])
    model.zero_grad();ref.zero_grad()
    torch.nn.functional.nll_loss(left[graph.train_mask],graph.y[graph.train_mask]).backward()
    torch.nn.functional.nll_loss(right[graph.train_mask],graph.y[graph.train_mask]).backward()
    maximum=0.
    for (name,a),(other,b) in zip(model.named_parameters(),ref.named_parameters()):
        assert name==other;close(a.grad,b.grad);maximum=max(maximum,float((a.grad-b.grad).abs().max()))
    model.zero_grad()
    return dict(status='passed',output_max_abs=float((left-right).abs().max().detach()),
        alpha_max_abs=float((ld[0]['used_alpha']-rd[0]['used_alpha']).abs().max().detach()),gradient_max_abs=maximum)
def mechanism(details):
    d=details[0];alpha=d['used_alpha'];valid=d['valid'];out={}
    out['hop_weights_mean']=alpha.mean(0).tolist();out['hop_weights_std']=alpha.std(0).tolist()
    out['hop_weights_quantiles']=torch.quantile(alpha,torch.tensor([0.,.25,.5,.75,1.],device=alpha.device),dim=0).tolist()
    entropy=-(alpha*alpha.clamp_min(1e-30).log()).sum(1)
    out['gate_entropy_mean']=float(entropy.mean());out['gate_entropy_std']=float(entropy.std())
    out['empty_fraction']=(~valid).float().mean(0).tolist()
    for name,key in [('raw','raw_hops'),('gamma_scaled','scaled_hops'),('layernorm','hops')]:
        h=d[key];h=torch.nn.functional.normalize(h,dim=-1);pairs=[]
        for p in range(5):
            for q in range(p+1,5):
                keep=valid[:,p]&valid[:,q]
                pairs.append(dict(p=p,q=q,count=int(keep.sum()),mean=float((h[keep,p]*h[keep,q]).sum(-1).mean()) if keep.any() else None))
        out['cosine_'+name]=pairs
        out['norm_mean_'+name]=d[key].norm(dim=-1).mean(0).tolist()
    return out
def run(cfg,data_root,runs_root,device):
    protocol=verify_freeze();source=sources();fingerprint=digest(dict(science=science(cfg),sources=source,protocol=protocol))
    alljobs=jobs(cfg);runs_root.mkdir(parents=True,exist_ok=True)
    completed={}
    for f in sorted(runs_root.glob('*/result.json')):
        r=read(f)
        if r['status']=='complete' and r['fingerprint']==fingerprint:
            for name,h in r['artifacts'].items():
                if sha(f.parent/name)!=h: raise ValueError('Existing attempt artifact changed')
            key=tuple(r[k] for k in ('dataset','split','seed','group','empty_policy'))
            if key in completed: raise ValueError('Duplicate complete cell')
            completed[key]=r
    print('matrix',cfg['phase'],'expected',len(alljobs),'matching existing',sum(tuple(j.values()) in completed for j in alljobs),flush=True)
    # Rotate group order while keeping matched cells adjacent.
    alljobs.sort(key=lambda j:(cfg['datasets'].index(j['dataset']),j['split'],j['seed'],
        (int(j['group'][1])-(j['split']+j['seed'])%4)%4))
    graph_cache={};shell_cache={}
    for job in alljobs:
        key=tuple(job.values())
        if key in completed: continue
        run_id=now().replace(':','').replace('.','')+'-'+uuid.uuid4().hex[:8]
        folder=runs_root/run_id;folder.mkdir(exist_ok=False)
        metadata=dict(**job,run_id=run_id,phase_started=cfg['phase'],status='running',started_utc=now(),
            git=git_state(),sources=source,protocol_sha256=protocol,config=cfg,config_sha256=digest(cfg),
            fingerprint=fingerprint,environment=environment())
        save(folder/'metadata.json',metadata);start=time.perf_counter()
        try:
            pair=(job['dataset'],job['split'])
            if pair not in graph_cache:
                # Keep only one graph/split resident on device.
                graph_cache.clear()
                graph_cache[pair]=load_graph(data_root,*pair,device)
            graph,manifest,split=graph_cache[pair]
            metadata.update(graph_tensor_sha256=manifest['graph_tensor_sha256'],split=job['split'],
                split_sha256=split['sha256'],split_array_sha256=split['array_sha256'])
            name=job['dataset']
            if name not in shell_cache:
                shell_cache.clear()
                shells,bmeta=cached(graph.edge_index,graph.num_nodes,data_root/'distance_cache')
                operators,valid=tensors(shells,graph.num_nodes,device)
                shell_cache[name]=(operators,valid,bmeta)
                save(STUDY/'results'/('distance_'+name+'.json'),bmeta)
            operators,valid,bmeta=shell_cache[name]
            metadata['distance']=bmeta
            model,initial=build_model(graph.num_node_features,int(graph.y.max())+1,job['group'],job['seed'],device,
                operators,valid,job['empty_policy'])
            metadata.update(initial);save(folder/'metadata.json',metadata)
            if device.startswith('cuda'): torch.cuda.reset_peak_memory_stats()
            with (folder/'terminal.log').open('w',encoding='utf8') as log,contextlib.redirect_stdout(log):
                fit=train_model(model,graph,cfg['training'],folder/'epochs.csv')
            peak=torch.cuda.max_memory_allocated() if device.startswith('cuda') else 0
            model.eval()
            with torch.no_grad():
                output,details=model(graph.x,graph.edge_index,True)
                if not output.isfinite().all(): raise FloatingPointError('Nonfinite final output')
                metrics={}
                for label in ('train','val','test'):
                    mask=graph[label+'_mask'];correct=int((output.argmax(1)[mask]==graph.y[mask]).sum());n=int(mask.sum())
                    metrics.update({label+'_accuracy':correct/n,label+'_correct':correct,label+'_size':n})
                assert metrics['val_accuracy']==fit['best_validation_accuracy']
                diagnostics=mechanism(details)
            benchmark=inference_benchmark(model,graph,cfg['training']['infer_warmup'],cfg['training']['infer_repeats'])
            state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
            torch.save(dict(state_dict=state,group=job['group'],empty_policy=job['empty_policy'],
                graph_tensor_sha256=manifest['graph_tensor_sha256'],fingerprint=fingerprint),folder/'model.pt')
            # Reload every selected checkpoint and verify exact prediction/log-prob alignment.
            loaded=torch.load(folder/'model.pt',map_location=device,weights_only=True)
            model.load_state_dict(loaded['state_dict'])
            with torch.no_grad(): close(model(graph.x,graph.edge_index),output)
            checks=equivalence(model,graph,job['group'])
            costs=dict(projections=5 if job['group']=='G0' else 1,
                walk_propagations=10 if job['group']=='G0' else 4 if job['group']=='G3' else 0,
                shell_sparse_mm=0 if job['group']=='G0' else 4)
            report=dict(**metadata,**{k:v for k,v in fit.items() if k!='history'},**metrics,**benchmark,**diagnostics,
                checkpoint_equivalence=checks,checkpoint_reload='passed',trained_state_sha256=tensor_hash(state),
                parameter_count=sum(p.numel() for p in model.parameters()),peak_gpu_allocated_mb=peak/1024**2,
                operations=costs,ended_utc=now(),wall_seconds=time.perf_counter()-start)
            report['status']='complete';report['artifacts']={n:sha(folder/n) for n in ('model.pt','epochs.csv','terminal.log','metadata.json')}
            save(folder/'result.json',report)
            completed[key]=report
            print(len(completed),job,'test',round(metrics['test_accuracy']*100,3),'sec',round(report['wall_seconds'],2),flush=True)
            del model,output,details
        except Exception as error:
            (folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf8')
            metadata.update(status='failed',ended_utc=now(),error_type=type(error).__name__,
                # Private traceback is retained; no absolute error text enters public tables.
                wall_seconds=time.perf_counter()-start)
            save(folder/'result.json',metadata)
            print('FAILED',job,type(error).__name__,flush=True)
            raise
    return completed
def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['smoke','pilot','full','empty_control','prepare']);p.add_argument('--plan',action='store_true')
    p.add_argument('--data-root',default='../private_data');p.add_argument('--runs-root',default='../private_runs');p.add_argument('--import-from')
    p.add_argument('--device',default='cuda');args=p.parse_args()
    configure_determinism();torch.set_num_threads(1)
    if args.phase=='prepare':
        manifest=prepare(external(args.data_root),args.import_from)
        save(STUDY/'results/data_verification.json',manifest);return
    cfg=read(STUDY/'configs'/(args.phase+'.json'));verify_freeze()
    if args.plan:
        print(json.dumps(dict(phase=args.phase,count=len(jobs(cfg)),units=jobs(cfg)),indent=2));return
    run(cfg,external(args.data_root),external(args.runs_root),args.device)
if __name__=='__main__': main()
