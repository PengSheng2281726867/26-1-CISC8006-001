"""Dedicated inference-only profiling of every hash-verified selected checkpoint."""
from .common import *
import argparse
import csv
import time
import torch
from .analyze import collect,DATASETS
from .run import environment,close
from .distance import cached,tensors
from .model import build_model
from src.factory import configure_determinism
from src.train import inference_benchmark
from experiments.hop_scope_study.src.data import load_graph
def main():
    p=argparse.ArgumentParser();p.add_argument('--runs-root',default='../private_runs');p.add_argument('--data-root',default='../private_data');p.add_argument('--device',default='cuda');a=p.parse_args()
    configure_determinism();torch.set_num_threads(1)
    root=external(a.runs_root);data=external(a.data_root);records,failures,stale=collect(root)
    records=[r for r in records if r['empty_policy']=='mask'];records.sort(key=lambda r:(DATASETS.index(r['dataset']),r['split'],r['seed'],r['group']))
    rows=[];pair=None;name=None;start=now()
    for i,r in enumerate(records):
        current=(r['dataset'],r['split'])
        if current!=pair:
            graph,_,_=load_graph(data,*current,a.device);pair=current
        if r['dataset']!=name:
            shells,bmeta=cached(graph.edge_index,graph.num_nodes,data/'distance_cache')
            ops,valid=tensors(shells,graph.num_nodes,a.device);name=r['dataset']
        path=root/r['run_id']/'model.pt'
        if sha(path)!=r['artifacts']['model.pt']:raise ValueError('Checkpoint changed')
        model,_=build_model(graph.num_node_features,int(graph.y.max())+1,r['group'],r['seed'],a.device,ops,valid)
        model.load_state_dict(torch.load(path,map_location=a.device,weights_only=True)['state_dict']);model.eval()
        with torch.no_grad():
            output,details=model(graph.x,graph.edge_index,True)
            alpha=details[0]['used_alpha']; eligibility=details[0]['valid'].sum(1)
            ent=-(alpha*alpha.clamp_min(1e-30).log()).sum(1)
            normalized_ent=torch.where(eligibility>1,ent/eligibility.float().log().clamp_min(1e-8),torch.zeros_like(ent))
            entropy=float(normalized_ent.mean())
            query=details[0]['query'] if details[0]['query'] is not None else details[0]['iterations'][0]['fused']
            query_norm=float(query.norm(dim=-1).mean())
            scores=(details[0]['hops']*query[:,None]).sum(-1)
            score_std=float(scores.std(dim=1).mean())
            concentrated=float((alpha.max(1).values>.95).float().mean())
            # Matched topology-valid denominators for all groups: supplementary diagnostic.
            h=torch.nn.functional.normalize(details[0]['hops'],dim=-1);cs=[]
            for left in range(5):
                for right in range(left+1,5):
                    keep=valid[:,left]&valid[:,right]
                    if keep.any():cs.append(float((h[keep,left]*h[keep,right]).sum(-1).mean()))
            matched_cosine=sum(cs)/len(cs) if cs else None
            correct=int((output.argmax(1)[graph.test_mask]==graph.y[graph.test_mask]).sum())
            if correct!=r['test_correct']:raise ValueError('Label/output alignment changed')
        result=inference_benchmark(model,graph,5,20)
        rows.append(dict(run_id=r['run_id'],dataset=r['dataset'],split=r['split'],seed=r['seed'],group=r['group'],
            checkpoint_sha256=sha(path),gate_entropy_normalized_by_eligible_hops=entropy,query_norm_mean=query_norm,
            unmasked_score_std_across_hops=score_std,max_alpha_above_095_fraction=concentrated,
            cosine_ln_matched_exact_valid_pairs=matched_cosine,**result))
        if (i+1)%60==0:print('profiled',i+1,'/',len(records),flush=True)
        del model,output,details,alpha,h,query,scores
    out=STUDY/'results/full';out.mkdir(exist_ok=True)
    with (out/'dedicated_inference.csv').open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    save(out/'dedicated_inference_provenance.json',dict(started_utc=start,ended_utc=now(),count=len(rows),
        environment=environment(),git=git_state(),sources=sources(),profile_source_sha256=sha(Path(__file__)),
        labels_used='only verify unchanged selected-checkpoint accuracy; no training or model selection',
        training_started=False,optimizer_steps=0,hardware_load='serial task; unrelated system load not controlled'))
if __name__=='__main__':main()
