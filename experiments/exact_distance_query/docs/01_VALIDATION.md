# Pre-training validation

Before any real training:13 study unittest methods passed on CPU/CUDA. Includes
five-node chain sets at all hops/nodes, triangle/C4 backtracking, directed and
duplicate edges/self-loops, disconnected/isolated nodes, topology-only cache
stability, sparse reference/gradient parity, guard failures, four-arm parameter/
initialization/gradient/mask/save-load checks, original forward/input/parameter
gradient and used_alpha parity, weighted Walk fallback, consensus-one-shot
forward/gradient parity with nonzero bias and empty policies, exact query formulas,
and frozen protocol/matrix sizes. Float32 atol2e-6/rtol2e-5 for alignment.

Legacy smoke:13 tests passed, including20 author-alignment cases, source-mapping
hashes, validation selection and failure provenance. The smoke's deliberately
failed synthetic fixture is expected and preserved in ignored outputs; it is not
a failed scientific training. Six datasets and all60 split arrays verified from
read-only local cache into this study's external private_data. No data downloaded
by this study's preparation. Real checkpoint parity will be recorded per G0/G1
run, including one-shot gradient alignment and reload checks.

Environment:Python3.12.14,torch2.8.0+cu128,PyG2.7.0,RTX5090,CUDA12.8,threads1,
deterministic algorithms,TF32 disabled. Shared environment unchanged.
