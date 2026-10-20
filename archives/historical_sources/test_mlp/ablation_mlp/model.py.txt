"""Reuse the frozen GAMMA forward; change exactly one MLP component."""
from src.paths import ROOT
from src.model import GammaNet
from torch import nn

METHODS=('mlp','mlp_ln','mlp_gelu')

class ComponentNet(GammaNet):
    def __init__(self,in_channels,hidden_channels,out_channels,powers=(0,1,2),num_layers=2,
                 num_iterations=2,routing_score='mlp',mlp_hidden_dim=32):
        if routing_score not in METHODS:raise ValueError(routing_score)
        super().__init__(in_channels,hidden_channels,out_channels,powers,num_layers,
                         num_iterations,'mlp',mlp_hidden_dim)
        self.component_variant=routing_score
        for conv in self.convs:
            first,last=conv.scorer[0],conv.scorer[2]
            if routing_score=='mlp_ln':
                conv.scorer=nn.Sequential(first,nn.LayerNorm(mlp_hidden_dim,eps=1e-5),nn.ReLU(),last)
            elif routing_score=='mlp_gelu':
                conv.scorer=nn.Sequential(first,nn.GELU(approximate='none'),last)
            conv.routing_score=routing_score

def canonical_scorer_state(model):
    result={}
    for index,conv in enumerate(model.convs):
        for label,module in [('fc1',conv.scorer[0]),('fc2',conv.scorer[-1])]:
            for name,value in module.state_dict().items():result[f'{index}.{label}.{name}']=value
    return result
