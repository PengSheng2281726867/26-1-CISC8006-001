"""Read-only tensor parity against an existing processed cache, no reference imports."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,external,save,sha,now
from src.data import DATASETS,dataset,tensor_digest
import argparse
import torch
from torch_geometric.transforms import NormalizeFeatures
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True)
p.add_argument('--reference-data-root',type=Path,required=True);a=p.parse_args()
root=external(a.data_root);reference=a.reference_data_root.resolve();rows=[]
for name in DATASETS:
    ds=dataset(name,root);graph=ds[0]
    local=Path(ds.processed_paths[0]);other=reference/local.relative_to(root)
    before=sha(other);obj=torch.load(other,map_location='cpu',weights_only=False)
    if not isinstance(obj,tuple) or len(obj)!=3 or obj[1] is not None:
        raise ValueError('Unsupported reference serialization; do not modify it')
    historical=NormalizeFeatures()(obj[2].from_dict(obj[0]))
    if tensor_digest(graph)!=tensor_digest(historical):raise ValueError('Graph tensors differ: '+name)
    if before!=sha(other):raise ValueError('Reference bytes changed during read-only check')
    rows.append(dict(dataset=name,normalized_features_edges_labels_identical=True,
                     graph_tensor_sha256=tensor_digest(graph),reference_processed_sha256=before,
                     local_processed_sha256=sha(local),reference_bytes_unchanged=True))
save(STUDY/'results/data_content_parity.json',dict(utc=now(),status='passed',datasets=rows))
print('All six normalized feature/edge/label tensor hashes match original cache exactly')
