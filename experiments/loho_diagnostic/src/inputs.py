"""Read owner-supplied artifacts without writing into their source workspace."""
import os
from pathlib import Path
import shutil
import numpy as np
import torch
from torch_geometric.datasets import WebKB,WikipediaNetwork,Actor
from torch_geometric.transforms import NormalizeFeatures
from research.src.model import GammaNet
from research.src.paths import tensor_hash
from .common import read,sha,private_root
from .intervention import validate_model

def source_root():
    if not os.environ.get('LOHO_SOURCE_ROOT'): raise ValueError('Set LOHO_SOURCE_ROOT to owner artifact root')
    return Path(os.environ['LOHO_SOURCE_ROOT'])

def graph_for(name):
    src=source_root()/'test_mlp/data/cache'/name
    dst=private_root()/'inputs/cache'/name
    if not dst.exists(): shutil.copytree(src,dst)
    opts=dict(root=str(dst),transform=NormalizeFeatures())
    if name in ('Texas','Wisconsin','Cornell'): dataset=WebKB(name=name,**opts)
    elif name=='Actor': dataset=Actor(**opts)
    else: dataset=WikipediaNetwork(name=name.lower(),**opts)
    return dataset[0]

def checkpoint_path(dataset,split,seed):
    return source_root()/f'stability_validation/runs/multiseed_v1/runs/core/{dataset}/k_4/split_{split}/seed_{seed}/dot/attempt_01/model.pt'

def masks_for(name,split,n):
    path=source_root()/f'test_mlp/data/splits/{name.lower()}_split_0.6_0.2_{split}.npz'
    with np.load(path) as z: masks=[z[k].copy() for k in ('train_mask','val_mask','test_mask')]
    if any(m.dtype!=np.bool_ or m.shape!=(n,) for m in masks): raise ValueError('Mask shape/dtype')
    if not np.all(np.stack(masks).sum(0)==1): raise ValueError('Mask partition')
    perm=torch.randperm(n,generator=torch.Generator().manual_seed(102+split)).numpy()
    for m,idx in zip(masks,np.split(perm,[int(.6*n),int(.6*n)+int(.2*n)])):
        expected=np.zeros(n,dtype=bool);expected[idx]=True
        if not np.array_equal(m,expected): raise ValueError('Node/split ordering mismatch')
    return masks,sha(path)

def load_verified(path,graph,device='cuda'):
    report=read(path.with_name('result.json'))
    if report['status']!='complete' or report['method']!='dot' or report['suite']!='core':
        raise ValueError('Untrained or wrong baseline')
    for name,expected in report['artifacts'].items():
        if sha(path.with_name(name))!=expected: raise ValueError('Artifact hash mismatch: '+name)
    frozen=read(source_root()/'stability_validation/runs/multiseed_v1/frozen.json')
    if report['frozen_hash']!=frozen['sha256']: raise ValueError('Historical protocol mismatch')
    # Check actual source bytes against the preserved training snapshot.
    from .common import ROOT
    for name in ('model.py','factory.py','train.py'):
        if sha(source_root()/'test_mlp/src'/name)!=sha(ROOT/'research/src'/name):
            raise ValueError('Historical scientific source differs: '+name)
    checkpoint=torch.load(path,map_location='cpu',weights_only=True)
    if checkpoint['task']!={k:report[k] for k in ('suite','dataset','k','split','seed','method')}:
        raise ValueError('Checkpoint task mismatch')
    kwargs=checkpoint['model_metadata']['model_kwargs']
    if kwargs!=report['model_kwargs'] or kwargs['powers']!=list(range(5)) or kwargs['num_iterations']!=2:
        raise ValueError('K/R/kwargs mismatch')
    model=GammaNet(**kwargs).to(device);model.load_state_dict(checkpoint['state_dict'],strict=True);model.eval()
    validate_model(model)
    if tensor_hash(model.state_dict())!=report['trained_state_sha256']: raise ValueError('State hash mismatch')
    if tensor_hash(dict(x=graph.x,edge_index=graph.edge_index,y=graph.y))!=report['graph_sha256']:
        raise ValueError('Graph/label/node ordering hash mismatch')
    masks,split_hash=masks_for(report['dataset'],report['split'],graph.num_nodes)
    if split_hash!=report['split_sha256']: raise ValueError('Split file hash mismatch')
    with np.load(path.with_name('predictions.npz')) as z:
        for m,key in zip(masks,('train_mask','val_mask','test_mask')):
            if not np.array_equal(m,z[key]): raise ValueError('Saved mask mismatch')
        saved_pred=z['predictions'].copy()
    return model,report,masks,saved_pred
