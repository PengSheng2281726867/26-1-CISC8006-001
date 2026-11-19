"""No-update checkpoint masking; one full-hop state per split/seed."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,external,read,save,sha,digest,now,git_state,sources
from src.model import ScopeNet
from src.data import load_graph
from run import verified
from research.src.factory import configure_determinism
from research.src.paths import tensor_hash
from research.src.train import inference_benchmark
import argparse
import json
import time
import traceback
import uuid
import torch


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data-root',type=Path,required=True);p.add_argument('--run-root',type=Path,required=True)
    p.add_argument('--config',type=Path,default=STUDY/'configs/eval_only.json')
    a=p.parse_args();cfg=read(a.config);run_root=external(a.run_root);data_root=external(a.data_root)
    configure_determinism();torch.set_num_threads(cfg['protocol']['cpu_threads'])
    successes={}
    for folder in sorted((run_root/'runs').glob('*')):
        if not verified(folder): continue
        r=read(folder/'result.json');key=(r['dataset'],r['split_id'])
        if r['max_gating_hop']==5 and r['dataset'] in cfg['datasets'] and r['split_id'] in cfg['splits']:
            if key in successes: raise ValueError('Ambiguous duplicate full-hop checkpoint')
            successes[key]=folder
    for key,folder in successes.items():
        cp_hash=sha(folder/'model.pt')
        previous=[p for p in (run_root/'eval').glob('*/result.json')
                  if read(p).get('checkpoint_sha256')==cp_hash and read(p).get('status')=='complete'
                  and read(p).get('source_sha256')==sources()]
        if previous: continue
        identifier='eval-'+uuid.uuid4().hex[:12];out=run_root/'eval'/identifier;out.mkdir(parents=True,exist_ok=False)
        report=dict(run_id=identifier,source_run_id=folder.name,checkpoint_sha256=cp_hash,started_utc=now(),
                    git=git_state(),source_sha256=sources(),config_sha256=sha(a.config),protocol_sha256=digest(cfg['protocol']),
                    dataset=key[0],split_id=key[1],seed=42+key[1],max_propagation_hop=5,
                    powers=list(range(6)),r=2,actual_gamma_layers=1,status='running',rows=[])
        start=time.perf_counter()
        try:
            checkpoint=torch.load(folder/'model.pt',map_location='cpu',weights_only=False)
            model=ScopeNet(**checkpoint['model_kwargs']).to('cuda');model.load_state_dict(checkpoint['state_dict']);model.eval()
            graph,data,split=load_graph(data_root,*key,'cuda')
            before=tensor_hash(model.state_dict())
            report.update(full_state_sha256=before,full_init_sha256=checkpoint['report']['full_init_sha256'],
                          split_sha256=split['sha256'],graph_tensor_sha256=data['graph_tensor_sha256'],
                          device=torch.cuda.get_device_name(0))
            with torch.no_grad():
                baseline=model(graph.x,graph.edge_index).argmax(1)
                for x in cfg['max_gating_hops']:
                    model.set_scope(x);logits,details=model(graph.x,graph.edge_index,return_diagnostics=True)
                    if not bool(torch.isfinite(logits).all()): raise FloatingPointError('Nonfinite post-hoc logits')
                    for iteration in details[0]['iterations']:
                        alpha=iteration['alpha']
                        assert torch.count_nonzero(alpha[:,x+1:])==0
                        torch.testing.assert_close(alpha.sum(1),torch.ones(graph.num_nodes,device='cuda'))
                    pred=logits.argmax(1)
                    row=dict(max_gating_hop=x,prediction_change_fraction=float((pred!=baseline).float().mean()),
                             hop_weights_mean=details[0]['used_alpha'].mean(0).cpu().tolist())
                    for label in ('train','val','test'):
                        mask=graph[label+'_mask']; row[label+'_accuracy']=int((pred[mask]==graph.y[mask]).sum())/int(mask.sum())
                    row.update(inference_benchmark(model,graph,5,20));report['rows'].append(row)
            assert tensor_hash(model.state_dict())==before and all(p.grad is None for p in model.parameters())
            if report['rows'][-1]['test_accuracy']!=checkpoint['report']['test_accuracy']:
                raise ValueError('x5 inference differs from retrain control')
            report.update(status='complete',state_unchanged=True,no_gradients=True)
        except BaseException as error:
            report.update(status='failed',failure_type=type(error).__name__,failure_reason=str(error))
            (out/'terminal.log').write_text(traceback.format_exc(),encoding='utf8')
        report.update(finished_utc=now(),wall_seconds=time.perf_counter()-start)
        save(out/'result.json',report);print(json.dumps(dict(run_id=identifier,dataset=key[0],split=key[1],status=report['status'])),flush=True)
    return 0

if __name__=='__main__':sys.exit(main())
