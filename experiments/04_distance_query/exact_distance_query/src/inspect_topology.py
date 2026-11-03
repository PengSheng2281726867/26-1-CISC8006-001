"""Safe topology scalars; labels/features never enter calculations."""
from .common import *
import argparse
import numpy as np
from experiments.hop_scope_study.src.data import dataset,DATASETS
from .distance import edge_hash
def main():
    p=argparse.ArgumentParser();p.add_argument('--data-root',default='../private_data');a=p.parse_args();root=external(a.data_root)
    rows=[]
    for name in DATASETS:
        graph=dataset(name,root)[0];e=graph.edge_index.cpu().numpy();edges=set(zip(e[0].tolist(),e[1].tolist()))
        inbound=np.bincount(e[1],minlength=graph.num_nodes);outbound=np.bincount(e[0],minlength=graph.num_nodes)
        rows.append(dict(dataset=name,nodes=graph.num_nodes,raw_edges=e.shape[1],unique_directed_edges=len(edges),
            duplicate_edges=e.shape[1]-len(edges),self_loop_edges=int((e[0]==e[1]).sum()),
            reciprocal_unique_edge_fraction=sum((t,s) in edges for s,t in edges)/len(edges),
            no_incoming_fraction=float((inbound==0).mean()),no_outgoing_fraction=float((outbound==0).mean()),
            edge_order_sha256=edge_hash(graph.edge_index,graph.num_nodes),operator='source_to_target add; no symmetrization'))
    save(STUDY/'results/topology_audit.json',dict(utc=now(),label_usage=False,topologies=rows));print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
