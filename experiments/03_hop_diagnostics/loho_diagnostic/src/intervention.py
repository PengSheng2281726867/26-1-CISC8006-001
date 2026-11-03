"""Source-faithful GAMMA adapter, under root MIT LICENSE/NOTICE."""
import torch
from torch import nn
from research.src.model import GammaNet,GammaLayer

def validate_model(model):
    if type(model) is not GammaNet or len(model.convs)!=1 or len(model.norms)!=1:
        raise ValueError('Only the audited single GAMMA layer architecture is supported')
    layer=model.convs[0]
    if type(layer) is not GammaLayer or layer.routing_score!='dot' or layer.num_iterations<1:
        raise ValueError('Requires original Dot routing with R>=1')
    if layer.powers!=list(range(len(layer.powers))) or len(layer.powers)<2:
        raise ValueError('Requires consecutive powers starting at zero and K>=1')
    if type(model.norms[0]) is not nn.LayerNorm or type(model.lin) is not nn.Linear:
        raise ValueError('Unknown post-routing coupling')
    if model.training: raise ValueError('eval() required')
    return layer

def route(layer,hops,mask_type='none',hop=None,nodes=None):
    if mask_type not in ('none','final_only','full_routing'): raise ValueError(mask_type)
    if (mask_type=='none') != (hop is None): raise ValueError('Mask and hop required together')
    if hop is not None and (hop<1 or hop>=len(layer.powers)):
        raise ValueError('Zero-hop protected; hop must be in 1..K')
    b=torch.zeros(hops.size(0),len(layer.powers),device=hops.device)
    trace=[]
    for t in range(layer.num_iterations):
        logits=b
        if hop is not None and (mask_type=='full_routing' or t==layer.num_iterations-1):
            logits=b.clone()
            if nodes is None: logits[:,hop]=-torch.inf
            else: logits[nodes,hop]=-torch.inf
        alpha=torch.softmax(logits,dim=1)
        fused=layer.squash(torch.sum(alpha.unsqueeze(-1)*hops,dim=1))
        agreement=layer.score(hops,fused)
        trace.append(dict(logits=b,alpha=alpha,fused=fused,agreement=agreement))
        b=b+agreement
    return fused+layer.bias,dict(hops=hops,iterations=trace,used_alpha=alpha,post_update_logits=b)

def forward(model,x,edge_index,mask_type='none',hop=None,nodes=None,hops=None):
    layer=validate_model(model)
    if hops is None: hops=layer.hop_embeddings(x,edge_index)
    out,details=route(layer,hops,mask_type,hop,nodes)
    out=model.norms[0](out)
    return torch.nn.functional.log_softmax(model.lin(out),dim=1),details
