# Implementation audit

2026-10-29. Repository base935a4303ed0d1410e29d9374cc1ce91b82dc527c,
origin main; initial working tree clean. Protected scientific sources unchanged.
Read root AGENTS/README/CLAIM_AND_REPRODUCTION/IMPROVEMENTS/AI_USAGE and checker.
Original GAMMA2 and prior hop workspace were read only.

`research/src/model.py`: num_layers2 creates one GammaLayer and a Linear head.
Each hop independently projects x with shared biased Linear, repeats additive
propagation p times, applies channel scales and per-hop LayerNorm. No adjacency
normalization or paper-style L2 substitution. Routing starts at zero, executes
R softmax/fusion/squash/dot-accumulation rounds, then adds bias. GammaNet applies
nodewise LayerNorm, disabled eval dropout and Linear/log_softmax.
`used_alpha` is last actual fusion, whereas `post_update_logits` has one extra
agreement accumulation. `F.nll_loss` computes true-label per-node losses.

Adapter calls protected hop_embeddings, score and squash methods; rebuilding
only routing and eval head. Every real condition reuses the same hop tensor.
One-node/global equivalence is valid only after propagation with this one-layer,
nodewise post-processing architecture. Adapter rejects multilayer, MLP,
BatchNorm, unsupported powers and training mode. Real runs verify equivalence,
normalization, zero weights, original no-mask output/alpha/NLL, saved predictions
and immutable states. Synthetic tests cover K1/4/5, R1/2/3, CPU/CUDA, alpha timing,
loss signs, removed-branch independence, unsupported coupling and provenance.

Primary inventory:180 existing stability_v1/core K4/R2 Dot checkpoints, six
graphs x ten splits x three optimization seeds. All180 load strictly and match
recorded artifact, state, graph (including label/node order) and split hashes.
Historical v2 K4 Dot60 loadable weights inventoried separately, not pooled.
Other model files include MLP, Uniform, other K, direct-construction and extra
suites; path classification is discovery only, never evidence of baseline type.
Historical execution Git commits are not inferred from current source equality.
Source equality establishes a compatible implementation, not a complete history.

Environment: existing GAMMA Python3.12/torch2.8+cu128/PyG2.7, RTX5090; plotting
uses existing base matplotlib. Shared environments were not modified. No new
training was launched beyond the root smoke test's tiny synthetic fixture.
