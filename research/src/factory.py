from .paths import tensor_hash
from .model import GammaNet
import numpy as np
import torch

def configure_determinism():
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.deterministic=True
    torch.backends.cudnn.benchmark=False

def seed_all(seed):
    np.random.seed(seed);torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)

def build_model(in_channels,out_channels,k,method,seed,device='cuda'):
    seed_all(seed)
    options=dict(in_channels=in_channels,hidden_channels=32,out_channels=out_channels,
                 num_layers=2,num_iterations=2,mlp_hidden_dim=32)
    canonical=GammaNet(**options,powers=[0,1,2,3,4],routing_score='dot')
    bank=canonical.state_dict()
    model=GammaNet(**options,powers=list(range(k+1)),routing_score=method)
    shared={}
    for key,value in bank.items():
        shared[key]=value[:k+1] if key.endswith('scale_params') else value
    missing,unexpected=model.load_state_dict(shared,strict=False)
    assert not unexpected and all('.scorer.' in key for key in missing)
    if method=='mlp':
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(10000+seed)
            for conv in model.convs:
                for module in conv.scorer.modules():
                    if isinstance(module,torch.nn.Linear): module.reset_parameters()
    model=model.to(device)
    seed_all(seed)
    shared_state={key:(value[:2] if key.endswith('scale_params') else value)
                  for key,value in model.state_dict().items() if '.scorer.' not in key}
    return model,dict(common_init_sha256=tensor_hash(shared_state),
        full_init_sha256=tensor_hash(model.state_dict()),
        scorer_init_sha256=tensor_hash({key:value for key,value in model.state_dict().items() if '.scorer.' in key}),
        cpu_rng_sha256=tensor_hash({'rng':torch.get_rng_state()}),
        cuda_rng_sha256=tensor_hash({'rng':torch.cuda.get_rng_state()}) if str(device).startswith('cuda') else None,
        model_kwargs={**options,'powers':list(range(k+1)),'routing_score':method})
