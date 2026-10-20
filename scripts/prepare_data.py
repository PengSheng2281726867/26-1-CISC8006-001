"""Download through PyG; save source fingerprints and fixed splits only locally."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course.common import ROOT, RESEARCH, save, sha256, utc_now
import argparse
import hashlib
import json
import urllib.request
import uuid


def verify_raw_cache(name, expected, check_only):
    """Avoid accepting truncated PyG downloads; replace only our new cache files."""
    from torch_geometric.datasets import WebKB, Actor, WikipediaNetwork
    base = (WikipediaNetwork.processed_url if name in ('Chameleon','Squirrel')
            else Actor.url if name == 'Actor' else WebKB.url)
    for rel, required in expected['raw_files'].items():
        rel=rel.replace('\\','/')
        path=(RESEARCH/rel).resolve()
        assert path.is_relative_to((RESEARCH/'data/cache').resolve())
        if path.exists() and sha256(path)==required: continue
        if check_only: raise RuntimeError('Missing or different raw content: '+rel)
        filename=path.name
        graph_name='film' if name=='Actor' else name.lower()
        suffix=f'splits/{filename}' if filename.endswith('.npz') else f'new_data/{graph_name}/{filename}'
        url=base+'/'+suffix
        failures=[]
        for attempt in range(1,4):
            try:
                with urllib.request.urlopen(url,timeout=45) as response: data=response.read()
                if hashlib.sha256(data).hexdigest()!=required:
                    raise ValueError('Downloaded bytes do not match the historical raw SHA256.')
                path.parent.mkdir(parents=True,exist_ok=True)
                temporary=path.with_suffix(path.suffix+'.verified-download')
                temporary.write_bytes(data)
                temporary.replace(path)
                print(name,filename,'verified download',attempt)
                break
            except Exception as error:
                failures.append(dict(attempt=attempt,error_type=type(error).__name__,error=str(error)))
        else:
            save(ROOT/'outputs'/('download_failure_'+name+'_'+uuid.uuid4().hex+'.json'),
                 dict(dataset=name,url=url,failures=failures,utc=utc_now()))
            raise RuntimeError('Verified download failed; failure evidence saved in outputs/.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--datasets', nargs='+', default=['Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor'])
    args = parser.parse_args()
    import numpy as np
    import torch
    from src.data import DATASETS, SHAPES, load_dataset, load_masks, split_path
    expected = json.loads((ROOT/'experiments/data_manifest.json').read_text())
    manifest_path = RESEARCH/'data/manifest.json'
    local = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for name in args.datasets:
        assert name in DATASETS
        cache = RESEARCH/'data/cache'/name
        if args.check_only and not cache.exists(): raise FileNotFoundError('Dataset cache is absent: '+name)
        verify_raw_cache(name, expected[name], args.check_only)
        dataset = load_dataset(name)
        graph = dataset[0]
        assert tuple(graph.x.shape) == SHAPES[name]
        raw = {}
        for path in dataset.raw_paths:
            path = Path(path)
            rel = path.relative_to(RESEARCH).as_posix()
            actual = sha256(path)
            target = {k.replace('\\','/'):v for k,v in expected[name]['raw_files'].items()}.get(rel)
            if target is not None and actual != target:
                raise RuntimeError('Raw dataset differs from historical evidence: '+rel)
            raw[rel] = actual
        splits = []
        for split in range(10):
            path = split_path(name, split)
            if not path.exists():
                if args.check_only: raise FileNotFoundError(path.name)
                perm = torch.randperm(graph.num_nodes, generator=torch.Generator().manual_seed(102+split)).numpy()
                a,b=int(.6*graph.num_nodes),int(.2*graph.num_nodes)
                masks=[]
                for indices in np.split(perm,[a,a+b]):
                    mask=np.zeros(graph.num_nodes,dtype=np.bool_);mask[indices]=True;masks.append(mask)
                path.parent.mkdir(parents=True,exist_ok=True)
                np.savez(path,train_mask=masks[0],val_mask=masks[1],test_mask=masks[2])
            masks=load_masks(name,split,graph.num_nodes)
            expected_hash=next(s['sha256'] for s in expected[name]['splits'] if s['split']==split)
            actual=sha256(path)
            if actual != expected_hash:
                # NPZ ZIP metadata can differ; mask identity is independently checked
                # by load_masks against the exact historical seeded permutation.
                match='ARRAY_IDENTICAL_TO_GENERATOR_ARCHIVE_BYTES_DIFFER'
            else: match='EXACT_ARCHIVE_SHA256'
            splits.append(dict(split=split,seed=102+split,sha256=actual,historical_sha256=expected_hash,
                               identity_status=match,sizes=[int(m.sum()) for m in masks]))
        local[name]=dict(nodes=graph.num_nodes,features=graph.num_node_features,classes=dataset.num_classes,
            edges=graph.num_edges,raw_files=raw,splits=splits,processed_sha256=sha256(dataset.processed_paths[0]),
            historical_processed_sha256=expected[name]['processed_sha256'],verified_utc=utc_now())
        print(name,'raw hashes and split arrays verified')
    if not args.check_only: save(manifest_path,local)
    return 0


if __name__=='__main__': sys.exit(main())
