"""Verified local data and fixed masks; source workspace is never imported."""
from pathlib import Path
import shutil
import hashlib
import urllib.request
import numpy as np
import torch
from torch_geometric.datasets import WebKB, WikipediaNetwork, Actor
from torch_geometric.transforms import NormalizeFeatures
from .common import REPO, read, save, sha, digest, now, external

DATASETS = ('Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor')


def dataset(name, root):
    if name not in DATASETS:
        raise ValueError('Unknown dataset: '+name)
    options = dict(root=str(Path(root)/'cache'/name), transform=NormalizeFeatures())
    if name in DATASETS[:3]:
        return WebKB(name=name, **options)
    if name == 'Actor':
        return Actor(**options)
    return WikipediaNetwork(name=name.lower(), **options)


def masks(root, name, split, nodes):
    if type(split) is not int or not 0 <= split < 10:
        raise ValueError('split must be in 0..9')
    path = Path(root)/'splits'/f'{name.lower()}_split_0.6_0.2_{split}.npz'
    with np.load(path, allow_pickle=False) as f:
        values = [f[key].copy() for key in ('train_mask','val_mask','test_mask')]
    a,b = int(.6*nodes), int(.2*nodes)
    perm = torch.randperm(nodes, generator=torch.Generator().manual_seed(102+split)).numpy()
    for mask, ids in zip(values, np.split(perm,[a,a+b])):
        expected = np.zeros(nodes,dtype=np.bool_); expected[ids] = True
        if mask.shape != (nodes,) or mask.dtype != np.bool_ or not np.array_equal(mask,expected):
            raise ValueError('Split differs from the frozen CPU generator')
    if not np.all(np.stack(values).sum(axis=0)==1):
        raise ValueError('Masks must be disjoint and exhaustive')
    return values, path


def tensor_digest(graph):
    h = hashlib.sha256()
    for key in ('x','edge_index','y'):
        arr = graph[key].detach().cpu().contiguous().numpy()
        h.update(key.encode()); h.update(str(arr.shape).encode()); h.update(str(arr.dtype).encode())
        h.update(arr.tobytes())
    return h.hexdigest()


def prepare(root, import_from=None, check_only=False):
    root = external(root)
    expected = read(REPO/'experiments/data_manifest.json')
    result = {}
    failures = []
    for name in DATASETS:
        spec = expected[name]
        for rel, required in spec['raw_files'].items():
            relative = Path(rel.replace('\\','/')).relative_to('data')
            target = root/relative
            if target.exists() and sha(target)==required:
                continue
            if check_only:
                raise FileNotFoundError('Missing or different raw content: '+str(relative))
            origin = Path(import_from)/relative if import_from else None
            target.parent.mkdir(parents=True,exist_ok=True)
            if origin and origin.exists() and sha(origin)==required:
                shutil.copy2(origin,target)
            else:
                base = (WikipediaNetwork.processed_url if name in ('Chameleon','Squirrel')
                        else Actor.url if name=='Actor' else WebKB.url)
                filename = target.name
                graph_name = 'film' if name=='Actor' else name.lower()
                suffix = 'splits/'+filename if filename.endswith('.npz') else f'new_data/{graph_name}/{filename}'
                for attempt in range(1,4):
                    try:
                        with urllib.request.urlopen(base+'/'+suffix,timeout=45) as response:
                            content = response.read()
                        if hashlib.sha256(content).hexdigest()!=required:
                            raise ValueError('Downloaded content checksum mismatch')
                        target.write_bytes(content)
                        break
                    except Exception as error:
                        failures.append(dict(dataset=name,file=filename,attempt=attempt,
                                             error_type=type(error).__name__,reason=str(error),utc=now()))
                        save(root/'preparation_failures.json',failures)
                else:
                    raise RuntimeError('Verified download failed; evidence retained locally')
            if sha(target)!=required:
                raise ValueError('Raw hash mismatch')
        ds = dataset(name,root); graph = ds[0]
        if (graph.num_nodes,graph.num_node_features,graph.num_edges,ds.num_classes) != (
                spec['nodes'],spec['features'],spec['edges'],spec['classes']):
            raise ValueError('Graph shape/edges/classes mismatch: '+name)
        split_records = []
        for split in range(10):
            target = root/'splits'/f'{name.lower()}_split_0.6_0.2_{split}.npz'
            if not target.exists() and not check_only:
                target.parent.mkdir(parents=True,exist_ok=True)
                origin = Path(import_from)/'splits'/target.name if import_from else None
                if origin and origin.exists():
                    shutil.copy2(origin,target)
                else:
                    perm=torch.randperm(graph.num_nodes,generator=torch.Generator().manual_seed(102+split)).numpy()
                    a,b=int(.6*graph.num_nodes),int(.2*graph.num_nodes)
                    values=[]
                    for ids in np.split(perm,[a,a+b]):
                        mask=np.zeros(graph.num_nodes,dtype=np.bool_);mask[ids]=True;values.append(mask)
                    np.savez(target,**dict(zip(('train_mask','val_mask','test_mask'),values)))
            values,path=masks(root,name,split,graph.num_nodes)
            historical=next(s['sha256'] for s in spec['splits'] if s['split']==split)
            split_records.append(dict(split=split,seed=102+split,sha256=sha(path),historical_sha256=historical,
                array_sha256=digest([hashlib.sha256(m.tobytes()).hexdigest() for m in values]),
                status='EXACT_ARCHIVE_SHA256' if sha(path)==historical else 'IDENTICAL_ARRAYS_DIFFERENT_ARCHIVE',
                sizes=[int(m.sum()) for m in values]))
        result[name]=dict(nodes=graph.num_nodes,features=graph.num_node_features,edges=graph.num_edges,
            classes=ds.num_classes,graph_tensor_sha256=tensor_digest(graph),
            raw_files={rel:sha(root/Path(rel.replace('\\','/')).relative_to('data')) for rel in spec['raw_files']},
            processed_sha256=sha(ds.processed_paths[0]),splits=split_records)
        print(name,'verified raw graph and 10 splits',flush=True)
    manifest=dict(verified_utc=now(),historical_manifest_sha256=sha(REPO/'experiments/data_manifest.json'),
                  datasets=result,download_failures=failures)
    if not check_only:
        save(root/'manifest.json',manifest)
    return manifest


def load_graph(root, name, split, device):
    root=external(root)
    manifest=read(root/'manifest.json')['datasets'][name]
    # Recheck raw hashes, graph identity and exact split archive for every cell.
    for rel,expected in manifest['raw_files'].items():
        if sha(root/Path(rel.replace('\\','/')).relative_to('data')) != expected:
            raise ValueError('Raw graph changed after preparation')
    ds=dataset(name,root);graph=ds[0]
    if tensor_digest(graph)!=manifest['graph_tensor_sha256']:
        raise ValueError('Processed graph content changed')
    values,path=masks(root,name,split,graph.num_nodes)
    split_record=manifest['splits'][split]
    if sha(path)!=split_record['sha256']:
        raise ValueError('Split archive changed after preparation')
    graph=graph.to(device)
    for label,mask in zip(('train_mask','val_mask','test_mask'),values):
        graph[label]=torch.from_numpy(mask).to(device)
    return graph,manifest,split_record
