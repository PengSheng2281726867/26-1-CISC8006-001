from .paths import ROOT,sha256,save_json
import numpy as np
import torch
from torch_geometric.datasets import WebKB,WikipediaNetwork,Actor
from torch_geometric.transforms import NormalizeFeatures

DATASETS=('Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor')
SHAPES={'Texas':(183,1703),'Wisconsin':(251,1703),'Cornell':(183,1703),
        'Chameleon':(2277,2325),'Squirrel':(5201,2089),'Actor':(7600,932)}

def load_dataset(name,force_reload=False):
    options=dict(root=str(ROOT/'data/cache'/name),transform=NormalizeFeatures(),force_reload=force_reload)
    if name in ('Texas','Wisconsin','Cornell'): return WebKB(name=name,**options)
    if name=='Actor': return Actor(**options)
    return WikipediaNetwork(name=name.lower(),**options)

def split_path(name,split):
    return ROOT/'data/splits'/f'{name.lower()}_split_0.6_0.2_{split}.npz'

def load_masks(name,split,nodes):
    with np.load(split_path(name,split)) as file:
        masks=[file[key].copy() for key in ('train_mask','val_mask','test_mask')]
    assert all(mask.shape==(nodes,) and mask.dtype==np.bool_ for mask in masks)
    assert np.all(np.stack(masks).sum(axis=0)==1)
    train,val=int(.6*nodes),int(.2*nodes)
    assert [int(mask.sum()) for mask in masks]==[train,val,nodes-train-val]
    permutation=torch.randperm(nodes,generator=torch.Generator().manual_seed(102+split)).numpy()
    for mask,indices in zip(masks,np.split(permutation,[train,train+val])):
        expected=np.zeros(nodes,dtype=np.bool_);expected[indices]=True
        assert np.array_equal(mask,expected)
    return masks
