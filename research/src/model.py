"""Independent GAMMA: source-faithful dot or shared learnable MLP agreement."""
from .paths import ROOT
import torch
from torch import nn
from torch_geometric.nn import MessagePassing


class GammaLayer(MessagePassing):
    def __init__(self,in_channels,out_channels,powers=(0,1,2),num_iterations=2,routing_score='dot',mlp_hidden_dim=32):
        super().__init__(aggr='add')
        if routing_score not in ('dot','mlp'): raise ValueError(routing_score)
        self.in_channels=in_channels;self.out_channels=out_channels
        self.powers=list(powers);self.num_iterations=num_iterations;self.routing_score=routing_score
        self.shared_linear=nn.Linear(in_channels,out_channels,bias=True)
        self.separate_linears=None
        self.scale_params=nn.Parameter(torch.randn(len(self.powers),out_channels))
        self.bias=nn.Parameter(torch.empty(out_channels))
        torch.nn.init.zeros_(self.bias)
        self.layer_norm=nn.LayerNorm(out_channels)
        self.reset_parameters()
        self.scorer=(nn.Sequential(nn.Linear(2*out_channels,mlp_hidden_dim),nn.ReLU(),
                                   nn.Linear(mlp_hidden_dim,1)) if routing_score=='mlp' else None)

    def reset_parameters(self):
        self.shared_linear.reset_parameters()
        nn.init.normal_(self.scale_params,mean=1.0,std=0.1)
        nn.init.zeros_(self.bias)

    def hop_embeddings(self,x,edge_index,edge_weight=None):
        if edge_weight is None:
            edge_weight=torch.ones(edge_index.size(1),dtype=x.dtype,device=x.device)
        outputs=[]
        for index,power in enumerate(self.powers):
            xp=self.shared_linear(x)
            for _ in range(power):
                xp=self.propagate(edge_index,x=xp,edge_weight=edge_weight,size=None)
            outputs.append(xp*self.scale_params[index])
        return torch.stack([self.layer_norm(xp) for xp in outputs],dim=1)

    def score(self,hops,fused):
        if self.routing_score=='dot':
            return torch.sum(hops*fused.unsqueeze(1),dim=-1)
        expanded=fused.unsqueeze(1).expand(-1,hops.size(1),-1)
        return self.scorer(torch.cat((hops,expanded),dim=-1)).squeeze(-1)

    def forward(self,x,edge_index,edge_weight=None,return_diagnostics=False):
        hops=self.hop_embeddings(x,edge_index,edge_weight)
        b=torch.zeros(x.size(0),len(self.powers),device=x.device)
        diagnostics=[]
        for iteration in range(self.num_iterations):
            alpha=torch.softmax(b,dim=1)
            fused=self.squash(torch.sum(alpha.unsqueeze(-1)*hops,dim=1))
            agreement=self.score(hops,fused)
            if return_diagnostics:
                diagnostics.append(dict(logits=b,alpha=alpha,fused=fused,agreement=agreement))
            b=b+agreement
        out=fused+self.bias
        if return_diagnostics:
            return out,dict(hops=hops,iterations=diagnostics,used_alpha=alpha,post_update_logits=b)
        return out

    @staticmethod
    def squash(s):
        squared=torch.sum(s**2,dim=-1,keepdim=True)
        return (squared/(1+squared))*s/torch.sqrt(squared+1e-8)

    def message(self,x_j,edge_weight):
        return x_j if edge_weight is None else edge_weight.view(-1,1)*x_j


class GammaNet(nn.Module):
    def __init__(self,in_channels,hidden_channels,out_channels,powers=(0,1,2),num_layers=2,
                 num_iterations=2,routing_score='dot',mlp_hidden_dim=32):
        super().__init__()
        if num_layers<2: raise ValueError('num_layers includes the linear head and must be >=2')
        self.convs=nn.ModuleList();self.norms=nn.ModuleList()
        for layer in range(num_layers-1):
            self.convs.append(GammaLayer(in_channels if layer==0 else hidden_channels,hidden_channels,
                powers,num_iterations,routing_score,mlp_hidden_dim))
            self.norms.append(nn.LayerNorm(hidden_channels))
        self.lin=nn.Linear(hidden_channels,out_channels)

    def forward(self,x,edge_index,return_diagnostics=False):
        x=nn.functional.dropout(x,p=0.2,training=self.training)
        diagnostics=[]
        for conv,norm in zip(self.convs,self.norms):
            if return_diagnostics:
                x,details=conv(x,edge_index,return_diagnostics=True)
                diagnostics.append(details)
            else: x=conv(x,edge_index)
            x=norm(x)
            x=nn.functional.dropout(x,p=0.8,training=self.training)
        out=nn.functional.log_softmax(self.lin(x),dim=1)
        return (out,diagnostics) if return_diagnostics else out
