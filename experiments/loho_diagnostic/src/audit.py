"""Inventory only actual files; primary load/data verification is repeated per run."""
import argparse
from collections import Counter
from .common import *
from .inputs import source_root,checkpoint_path,graph_for,load_verified

def main():
    import torch
    torch.set_num_threads(1)
    from research.src.paths import tensor_hash
    root=source_root();out=unique_run(private_root(),'audit');rows=[];counts=Counter()
    for path in root.rglob('model.pt'):
        rel=path.relative_to(root).as_posix()
        counts['all_model_files']+=1
        counts['dot_path' if '/dot/' in rel else 'other_or_unknown_path']+=1
    selected=[]
    for name in ('Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor'):
        graph=graph_for(name)
        for split in range(10):
            for seed in (2026,2027,2028):
                path=checkpoint_path(name,split,seed)
                if not path.exists(): continue
                row=dict(dataset=name,k=4,r=2,actual_gamma_layers=1,seed=seed,split_id=split,cohort='stability_v1_core',source=path.relative_to(root).as_posix(),checkpoint_sha256=sha(path))
                try:
                    model,r,masks,pred=load_verified(path,graph,'cpu')
                    row.update(status='VERIFIED_LOAD_AND_DATA',config_sha256=__import__('hashlib').sha256(__import__('json').dumps(r['exact_training_config'],sort_keys=True).encode()).hexdigest(),graph_sha256=r['graph_sha256'],split_sha256=r['split_sha256'],trained_state_sha256=r['trained_state_sha256'],historical_protocol_sha256=r['frozen_hash'],result_sha256=sha(path.with_name('result.json')),model_type='dot')
                except Exception as e: row.update(status='REJECTED',reason=str(e))
                rows.append(row)
        print(name,'inventoried',flush=True)
    # Historical cohort: inventory actual files, strict CPU loading only; no pooling.
    for path in (root/'test_mlp/runs/v2/full').glob('*/k_4/split_*/dot/attempt_01/model.pt'):
        r=read(path.with_name('result.json'))
        try:
            c=torch.load(path,weights_only=True,map_location='cpu')
            from research.src.model import GammaNet
            m=GammaNet(**c['model_kwargs']);m.load_state_dict(c['state_dict'],strict=True)
            assert tensor_hash(m.state_dict())==r['trained_state_sha256']
            assert sha(path)==r['artifacts']['model.pt']
            status='LOADABLE_NOT_PRIMARY'
        except Exception: status='REJECTED'
        rows.append(dict(dataset=r['dataset'],k=r['k'],r=r['r'],actual_gamma_layers=r['actual_gamma_layers'],seed=r['seed'],split_id=r['split_id'],model_type=r['routing_method'],cohort='historical_v2',source=path.relative_to(root).as_posix(),checkpoint_sha256=sha(path),split_sha256=r['split_sha256'],config_sha256=r['protocol_sha256'],graph_sha256='NOT_RECORDED',status=status))
    csv_write(EXPERIMENT/'results/checkpoint_inventory.csv',rows)
    save(out/'inventory.json',dict(counts=dict(counts),rows=rows,utc=now()))
    save(EXPERIMENT/'results/discovery_summary.json',dict(counts=dict(counts),primary=Counter(r['status'] for r in rows if r['cohort']=='stability_v1_core'),historical=Counter(r['status'] for r in rows if r['cohort']=='historical_v2')))
    print(out)
if __name__=='__main__': main()
