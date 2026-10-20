from src.paths import tensor_hash
from src.factory import build_model as build_frozen,seed_all
from .model import ComponentNet,canonical_scorer_state
import torch

def build_model(in_channels,out_channels,k,method,seed,device='cuda'):
    reference,reference_meta=build_frozen(in_channels,out_channels,k,'mlp',seed,'cpu')
    kwargs={**reference_meta['model_kwargs'],'routing_score':method}
    model=ComponentNet(**kwargs)
    mapped={key.replace('.scorer.2.','.scorer.3.') if method=='mlp_ln' else key:value
            for key,value in reference.state_dict().items()}
    missing,unexpected=model.load_state_dict(mapped,strict=False)
    expected={f'convs.{i}.scorer.1.{name}' for i in range(len(model.convs)) for name in ('weight','bias')} if method=='mlp_ln' else set()
    assert set(missing)==expected and not unexpected
    assert tensor_hash(canonical_scorer_state(model))==tensor_hash(canonical_scorer_state(reference))
    shared={key:value for key,value in model.state_dict().items() if '.scorer.' not in key}
    assert tensor_hash(shared)==tensor_hash({key:value for key,value in reference.state_dict().items() if '.scorer.' not in key})
    model=model.to(device);seed_all(seed)
    meta=dict(common_init_sha256=reference_meta['common_init_sha256'],
        full_common_init_sha256=tensor_hash(shared),full_init_sha256=tensor_hash(model.state_dict()),
        scorer_init_sha256=tensor_hash({key:value for key,value in model.state_dict().items() if '.scorer.' in key}),
        common_scorer_linear_init_sha256=tensor_hash(canonical_scorer_state(model)),
        reference_full_init_sha256=reference_meta['full_init_sha256'],
        cpu_rng_sha256=tensor_hash({'rng':torch.get_rng_state()}),
        cuda_rng_sha256=tensor_hash({'rng':torch.cuda.get_rng_state()}) if str(device).startswith('cuda') else None,
        model_kwargs=kwargs)
    del reference
    return model,meta
