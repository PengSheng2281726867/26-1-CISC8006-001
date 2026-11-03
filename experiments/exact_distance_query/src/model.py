"""Minimal adapter of MIT GAMMA; frozen G0 implementation is inherited."""
from .common import REPO
import torch
from src.model import GammaLayer, GammaNet
from src.factory import seed_all
from src.paths import tensor_hash
class StudyLayer(GammaLayer):
    def __init__(self,*args,group='G0',operators=None,valid=None,empty_policy='mask',aggregation=None,one_shot=False,**kwargs):
        super().__init__(*args,**kwargs)
        if group not in ('G0','G1','G2','G3'): raise ValueError(group)
        self.group=group; self.operators=operators; self.valid=valid
        self.empty_policy=empty_policy; self.aggregation=aggregation; self.one_shot=one_shot
    def candidates(self,x,edge_index,edge_weight=None):
        walk_mode=self.group=='G0' or self.aggregation=='walk'
        if walk_mode:
            raw=[]
            if edge_weight is None: edge_weight=torch.ones(edge_index.size(1),dtype=x.dtype,device=x.device)
            for p in self.powers:
                h=self.shared_linear(x)
                for _ in range(p): h=self.propagate(edge_index,x=h,edge_weight=edge_weight)
                raw.append(h)
            valid=torch.ones((x.size(0),5),dtype=torch.bool,device=x.device); query=None
        else:
            if self.operators is None or self.valid is None: raise ValueError('Exact operators required')
            z=self.shared_linear(x)
            raw=[z]+[torch.sparse.mm(op,z) for op in self.operators[1:]]
            valid=self.valid if self.empty_policy=='mask' else torch.ones_like(self.valid)
            query=None
            if self.group=='G2': query=self.layer_norm(z*self.scale_params[0])
            if self.group=='G3':
                h=z
                weights=edge_weight if edge_weight is not None else torch.ones(edge_index.size(1),dtype=x.dtype,device=x.device)
                for _ in range(4): h=self.propagate(edge_index,x=h,edge_weight=weights)
                query=self.layer_norm(h*self.scale_params[4])
        scaled=torch.stack([h*self.scale_params[p] for p,h in enumerate(raw)],dim=1)
        normalized=torch.stack([self.layer_norm(scaled[:,p]) for p in range(5)],dim=1)
        normalized=normalized.masked_fill(~valid.unsqueeze(-1),0.)
        return normalized,valid,query,torch.stack(raw,dim=1),scaled
    def forward(self,x,edge_index,edge_weight=None,return_diagnostics=False):
        if self.group=='G0' and not return_diagnostics: return super().forward(x,edge_index,edge_weight)
        hops,valid,query,raw,scaled=self.candidates(x,edge_index,edge_weight)
        iterations=[]
        if self.group in ('G0','G1') and not self.one_shot:
            logits=torch.zeros(x.size(0),5,device=x.device)
            for _ in range(2):
                alpha=torch.softmax(logits.masked_fill(~valid,-torch.inf),dim=1)
                fused=self.squash((alpha.unsqueeze(-1)*hops).sum(1)); agreement=self.score(hops,fused)
                if return_diagnostics: iterations.append(dict(alpha=alpha,logits=logits,agreement=agreement,fused=fused))
                logits=logits+agreement
        else:
            if self.one_shot: query=self.squash(hops.sum(1)/valid.sum(1,keepdim=True))
            logits=(hops*query.unsqueeze(1)).sum(-1)
            alpha=torch.softmax(logits.masked_fill(~valid,-torch.inf),dim=1)
            fused=self.squash((alpha.unsqueeze(-1)*hops).sum(1))
            if return_diagnostics: iterations.append(dict(alpha=alpha,logits=logits,agreement=logits,fused=fused))
        out=fused+self.bias
        if return_diagnostics:
            return out,dict(hops=hops,raw_hops=raw,scaled_hops=scaled,valid=valid,query=query,
                used_alpha=alpha,iterations=iterations,post_update_logits=logits)
        return out
def build_model(features,classes,group,seed,device,operators=None,valid=None,empty_policy='mask',aggregation=None,one_shot=False):
    seed_all(seed)
    baseline=GammaNet(features,32,classes,powers=list(range(5)),num_layers=2,num_iterations=2)
    bank={k:v.clone() for k,v in baseline.state_dict().items()}
    model=GammaNet(features,32,classes,powers=list(range(5)),num_layers=2,num_iterations=2)
    model.convs[0]=StudyLayer(features,32,powers=list(range(5)),num_iterations=2,
        group=group,operators=operators,valid=valid,empty_policy=empty_policy,aggregation=aggregation,one_shot=one_shot)
    model.load_state_dict(bank,strict=True); model.to(device); seed_all(seed)
    return model,dict(init_sha256=tensor_hash(bank),cpu_rng_sha256=tensor_hash({'rng':torch.get_rng_state()}),
        cuda_rng_sha256=tensor_hash({'rng':torch.cuda.get_rng_state()}) if str(device).startswith('cuda') else None)
