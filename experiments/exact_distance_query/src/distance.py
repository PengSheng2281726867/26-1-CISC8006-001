"""Binary directed shortest-message-distance CSR shells; no labels accepted."""
import hashlib
import time
import numpy as np
import torch
from scipy.sparse import csr_matrix
from .common import save, read, sha, digest
VERSION='reverse-bfs-csr-v1'
def edge_hash(edge_index,n):
    a=edge_index.detach().cpu().contiguous().numpy().astype('<i8')
    return hashlib.sha256(str(n).encode()+a.tobytes()).hexdigest()
def build(edge_index,n,k=4,max_nnz=100_000_000):
    if edge_index.ndim!=2 or edge_index.shape[0]!=2: raise ValueError('edge_index must be [2,E]')
    a=edge_index.detach().cpu().numpy()
    if a.size and (a.min()<0 or a.max()>=n): raise ValueError('Node outside graph')
    start=time.perf_counter()
    adj=csr_matrix((np.ones(a.shape[1],dtype=np.int32),(a[1],a[0])),shape=(n,n))
    adj.sum_duplicates(); adj.sort_indices()
    cols=[[] for _ in range(k+1)]; pointers=[[0] for _ in range(k+1)]
    total=0
    for target in range(n):
        seen={target}; frontier={target}
        for p in range(k+1):
            layer=sorted(frontier); total+=len(layer)
            if total>max_nnz: raise MemoryError('Exact shell NNZ guard exceeded')
            cols[p].extend(layer); pointers[p].append(len(cols[p]))
            if p<k:
                following=set()
                for node in frontier:
                    following.update(adj.indices[adj.indptr[node]:adj.indptr[node+1]].tolist())
                following.difference_update(seen); seen.update(following); frontier=following
    shells=[(np.asarray(ptr,dtype=np.int64),np.asarray(col,dtype=np.int64)) for ptr,col in zip(pointers,cols)]
    return shells,dict(version=VERSION,edge_order_sha256=edge_hash(edge_index,n),nodes=n,K=k,
        topology_sha256=hashlib.sha256(adj.indptr.tobytes()+adj.indices.tobytes()).hexdigest(),
        construction_seconds=time.perf_counter()-start,
        shells=[dict(p=p,nnz=len(col),mean_neighbors=float(np.diff(ptr).mean()),max_neighbors=int(np.diff(ptr).max()),
                     empty_fraction=float((np.diff(ptr)==0).mean())) for p,(ptr,col) in enumerate(shells)],
        csr_storage_bytes=sum(ptr.nbytes+col.nbytes+4*len(col) for ptr,col in shells),
        shell_content_sha256=hashlib.sha256(b''.join(ptr.tobytes()+col.tobytes() for ptr,col in shells)).hexdigest())
def cached(edge_index,n,root,k=4):
    root.mkdir(parents=True,exist_ok=True)
    key=digest([VERSION,edge_hash(edge_index,n),k]); path=root/(key+'.npz'); meta_path=root/(key+'.json')
    if path.exists():
        meta=read(meta_path)
        if sha(path)!=meta['cache_sha256']: raise ValueError('Distance cache checksum changed')
        with np.load(path,allow_pickle=False) as f: shells=[(f['ptr'+str(p)],f['col'+str(p)]) for p in range(k+1)]
        actual=hashlib.sha256(b''.join(ptr.tobytes()+col.tobytes() for ptr,col in shells)).hexdigest()
        if actual!=meta['shell_content_sha256']: raise ValueError('Distance content differs')
        return shells,meta
    shells,meta=build(edge_index,n,k)
    np.savez(path,**{key+str(p):value for p,pair in enumerate(shells) for key,value in zip(('ptr','col'),pair)})
    meta.update(cache_sha256=sha(path),cache_bytes=path.stat().st_size); save(meta_path,meta)
    return shells,meta
def tensors(shells,n,device):
    operators=[]; valid=[]
    for ptr,col in shells:
        operators.append(torch.sparse_csr_tensor(torch.from_numpy(ptr),torch.from_numpy(col),
            torch.ones(len(col)),size=(n,n),device=device))
        valid.append(torch.from_numpy(np.diff(ptr)>0))
    return operators,torch.stack(valid,dim=1).to(device)
