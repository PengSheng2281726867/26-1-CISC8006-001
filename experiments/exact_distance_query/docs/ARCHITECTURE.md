# Audited model differences

```mermaid
flowchart LR
  X[Normalized node features] --> Z[Shared biased Linear: Z]
  Z --> A[Original directed weighted Walk]
  Z --> B[Binary directed shortest-distance shells]
  A --> H[H0 through H4: gamma and LayerNorm]
  B --> E[E0 through E4: gamma and LayerNorm]
  E --> M[Zero and mask empty shells]
  H --> G0[G0: Consensus R2]
  M --> G1[G1: Consensus R2]
  H --> Q0[H0 Query]
  H --> Q4[H4 Query]
  M --> G2[G2: Dot with H0 then Softmax]
  M --> G3[G3: Dot with H4 then Softmax]
  Q0 --> G2
  Q4 --> G3
  G0 --> F[Squash and final bias]
  G1 --> F
  G2 --> F
  G3 --> F
  F --> O[Output LayerNorm and dropout and Linear/log_softmax]
```

Only the selected group executes. G0 retains five independent projections and
ten original propagations; G3 computes H4 from the same Z used by Exact shells.
H4 is only a query, never an additional fusion candidate. G2 uses the same shared
normalization/scaling definition for H0. No gradients are detached.

At R2, first valid-hop uniform fusion is squashed to v0, logits=dot(hop,v0).
Second softmax is used_alpha; second squash and final bias produce the layer
output. G1-one-shot uses v0 as its query and is checked numerically with nonzero
fusion/LN biases and real selected checkpoints. The unused final logits update
is never converted into a reported output weight.
