"""Execute frozen-checkpoint diagnostics; never trains."""
import argparse
import itertools
import time
import traceback
import numpy as np
import torch
import torch.nn.functional as F
from research.src.paths import tensor_hash
from research.src.factory import configure_determinism
from .common import *
from .inputs import checkpoint_path,graph_for,load_verified
from .intervention import forward

def jobs(c):
    if c['k']!=4 or c['r']!=2 or c['epsilon']!=1e-5: raise ValueError('Config differs from frozen protocol')
    rows=[dict(dataset=d,split_id=s,seed=z) for d,s,z in itertools.product(c['datasets'],c['splits'],c['seeds'])]
    if len({tuple(r.values()) for r in rows})!=len(rows): raise ValueError('Duplicate jobs')
    return rows

def run_one(job,c,split,output):
    start=time.perf_counter();folder=unique_run(output,'cell');meta=dict(run_id=folder.name,job=job,evaluation_set=split,started_utc=now(),status='running',git=git_state(),config=c,protocol_sha256=sha(EXPERIMENT/'PROTOCOL.md'),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted((EXPERIMENT/'src').glob('*.py'))},device=c['device'])
    save(folder/'metadata.json',meta)
    try:
        graph=graph_for(job['dataset']);path=checkpoint_path(job['dataset'],job['split_id'],job['seed'])
        model,r,masks,saved=load_verified(path,graph,c['device'])
        graph=graph.to(c['device']);before=tensor_hash(model.state_dict())
        idx=np.flatnonzero(masks[('train','val','test').index(split)])
        ids=torch.as_tensor(idx,device=c['device']);labels=graph.y[ids]
        with torch.inference_mode():
            original,od=model(graph.x,graph.edge_index,return_diagnostics=True)
            full,fd=forward(model,graph.x,graph.edge_index)
            for a,b in [(original,full),(od[0]['used_alpha'],fd['used_alpha']),(F.nll_loss(original[ids],labels,reduction='none'),F.nll_loss(full[ids],labels,reduction='none'))]:
                torch.testing.assert_close(a,b,atol=2e-6,rtol=2e-5)
            if not np.array_equal(full.argmax(1).cpu().numpy(),saved): raise ValueError('Reload prediction/node alignment mismatch')
            loss=F.nll_loss(full[ids],labels,reduction='none');pred=full[ids].argmax(1)
            arrays=dict(node_id=idx,alpha_used_full=fd['used_alpha'][ids].cpu().numpy(),loss_full=loss.cpu().numpy(),pred_full=pred.cpu().numpy(),correct_full=(pred==labels).cpu().numpy(),prob_true_full=(-loss).exp().cpu().numpy())
            for mask in ('final_only','full_routing'):
                all_loss=[];all_pred=[]
                for hop in range(1,5):
                    out,md=forward(model,graph.x,graph.edge_index,mask,hop,hops=fd['hops'])
                    if not bool(torch.isfinite(out).all()): raise FloatingPointError('Nonfinite output')
                    for t,item in enumerate(md['iterations']):
                        torch.testing.assert_close(item['alpha'].sum(1),torch.ones(graph.num_nodes,device=c['device']))
                        if mask=='full_routing' or t==1:
                            assert bool((item['alpha'][:,hop]==0).all())
                        else:
                            for key in ('logits','alpha','fused'): torch.testing.assert_close(item[key],fd['iterations'][t][key],atol=0,rtol=0)
                    # Actual data check of the global/single-node equivalence for each condition.
                    target=int(idx[0])
                    single,_=forward(model,graph.x,graph.edge_index,mask,hop,nodes=[target],hops=fd['hops'])
                    torch.testing.assert_close(single[target],out[target],atol=2e-6,rtol=2e-5)
                    all_loss.append(F.nll_loss(out[ids],labels,reduction='none'))
                    all_pred.append(out[ids].argmax(1))
                ml=torch.stack(all_loss,dim=1);mp=torch.stack(all_pred,dim=1)
                arrays.update({mask+'_loss_masked':ml.cpu().numpy(),mask+'_delta_loss':(ml-loss[:,None]).cpu().numpy(),mask+'_pred_masked':mp.cpu().numpy(),mask+'_correct_masked':(mp==labels[:,None]).cpu().numpy(),mask+'_prob_true_masked':(-ml).exp().cpu().numpy()})
            after=tensor_hash(model.state_dict());assert before==after
            if c['device'].startswith('cuda'): torch.cuda.synchronize()
        np.savez_compressed(folder/'nodes.npz',**arrays)
        meta.update(status='complete',checkpoint_sha256=sha(path),checkpoint_id=sha(path)[:16],trained_state_sha256=before,state_after_sha256=after,graph_sha256=r['graph_sha256'],split_sha256=r['split_sha256'],identity_max_output_error=float((original-full).abs().max()),identity_max_alpha_error=float((od[0]['used_alpha']-fd['used_alpha']).abs().max()),identity_atol=2e-6,identity_rtol=2e-5,original_run_id=r['unique_run_id'],nodes_sha256=sha(folder/'nodes.npz'),n_nodes=len(idx),gpu_name=torch.cuda.get_device_name() if c['device'].startswith('cuda') else None)
    except Exception as e:
        meta.update(status='failed',reason=str(e));(folder/'exception.log').write_text(traceback.format_exc(),encoding='utf-8')
    finally:
        meta.update(finished_utc=now(),wall_seconds=time.perf_counter()-start);save(folder/'metadata.json',meta)
    print(job,meta['status'],flush=True)
    return meta

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--plan',action='store_true');ap.add_argument('--split',choices=['train','val','test'],default='val');ap.add_argument('--output');ap.add_argument('--reuse-batch',action='append',default=[]);args=ap.parse_args()
    c=read(args.config);rows=jobs(c)
    if args.plan:
        for j in rows: print(j,'AVAILABLE' if checkpoint_path(j['dataset'],j['split_id'],j['seed']).exists() else 'NOT_AVAILABLE')
        print('checkpoints',len(rows),'conditions',9*len(rows),'training',False);return
    torch.set_num_threads(1);configure_determinism()
    batch=unique_run(args.output or private_root(),'batch-'+args.split)
    save(batch/'batch.json',dict(config=c,evaluation_set=args.split,expected_jobs=rows,started_utc=now()))
    reused={}
    if args.reuse_batch:
        from .summarize import collect
        reused,missing,failed=collect(args.reuse_batch)
        if missing or failed: raise ValueError('Cannot reuse incomplete batch')
        if any(m['protocol_sha256']!=sha(EXPERIMENT/'PROTOCOL.md') for p,m in reused.values()): raise ValueError('Cannot reuse different protocol')
    results=[]
    for j in rows:
        key=(j['dataset'],j['split_id'],j['seed'],args.split)
        if key in reused:
            results.append(reused[key][1]);print(j,'reused',flush=True)
        else: results.append(run_one(j,c,args.split,batch))
    save(batch/'completion.json',dict(finished_utc=now(),complete=sum(r['status']=='complete' for r in results),failed=sum(r['status']!='complete' for r in results)))
    print('BATCH',batch)
    if any(r['status']!='complete' for r in results): raise SystemExit(1)
if __name__=='__main__': main()
