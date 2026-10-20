# Claim and reproduction

Citation: Amir Ghazizadeh, Rickard Ewetz, Hao Zheng (2025), *GAMMA: Gated Multi-hop
Message Passing for Homophily-Agnostic Node Representation in GNNs*, NeurIPS.
[Primary author PDF](https://amir-ghz.github.io/PDFs/GAMMA.pdf); [official repository](https://github.com/amir-ghz/GAMMA).

## One operational candidate claim

Node-specific iterative routing improves node-classification accuracy over
uniform weighting of the same available hops while retaining shared projection
and learnable hop-specific channel scaling. Reference: Appendix B, Table3,
printed p16. Table1 supplies full-model accuracy context; the up-to20× efficiency
claim is not the chosen reproduction target and is not verified locally.

Reproduction level: **Component**. Teacher approval: **NOT_VERIFIED**. This claim
formulation is a retrospective recovery of the existing gating ablation, not a
pre-registered or teacher-approved course claim. Future formal work needs human
confirmation and a frozen protocol before training. Scientific hashes exist;
they do not constitute teacher approval.

## Baseline and protocol

Uniform disables node-specific routing while retaining channel scaling and the
remaining network. Dot is the authors' agreement and routing. Six graphs, K2–4,
powers0..K, R2, hidden32, one actual GAMMA layer plus Linear. Fixed60/20/20
split seeds102–111 and one training seed42+split. NormalizeFeatures, additive
message passing and LayerNorm follow actual source. Adam.02, wd1e-4, dropout.2/.8,
clip1, at most500 epochs, early stopping50, deep-copy validation-best selection.
No pretrained weights and no test-based model selection.

## Paper versus local result

The following six **paper 1–2 hop** entries are transcribed from Table3 and are
juxtaposed with **local powers0,1,2**. These are context comparisons, not identical
protocols or matched statistical replications. Paper Table3 gives means without
per-Split data; its per-entry uncertainty is NOT_VERIFIED. Local ± uses sampleSD.

| Dataset | Paper Uniform % | Paper Dot % | Paper Δ pp | Local Uniform % | Local Dot % | Local Δ pp |
| --- | --- | --- | --- | --- | --- | --- |
| Texas | 83.25 | 87.37 | +4.12 | 78.95 ± 9.20 | 82.89 ± 6.48 | +3.95 |
| Wisconsin | 81.40 | 86.27 | +4.87 | 85.49 ± 4.73 | 84.51 ± 4.84 | -0.98 |
| Cornell | 75.31 | 78.68 | +3.37 | 71.58 ± 8.93 | 75.79 ± 5.66 | +4.21 |
| Chameleon | 44.79 | 51.16 | +6.37 | 49.06 ± 1.27 | 48.38 ± 1.79 | -0.68 |
| Squirrel | 28.33 | 36.20 | +7.87 | 32.91 ± 1.73 | 33.85 ± 1.47 | +0.94 |
| Actor | 30.72 | 35.59 | +4.87 | 35.18 ± 0.90 | 35.47 ± 1.26 | +0.28 |


Paper source and transcribed numbers: [paper_reference_values.json](../experiments/paper_reference_values.json).
Full local K2–4 outcomes and all negative conditions: [results](../reports/RESULTS_SUMMARY.md).
Local Dot−Uniform improves11/18 means, decreases7/18; all18 Holm-adjusted
comparisons are non-significant. The original universal benefit is **not
reproduced under the local component protocol**, but this is not a disproof under
the paper's different protocol.

## Differences and uncertainty

Paper training description: two GNN layers,50/25/25 heterophilic splits, L2 hop
normalization, fixed500 epochs and validation grid search. Source-faithful local
setup: one actual GAMMA layer,60/20/20, LayerNorm, early stopping and fixed
hyperparameters; best-state shallow copy is corrected for both comparison arms.
Appendix hop labels may exclude0-hop; local inclusion is explicit. Three WebKB
edge counts also differ. No difference is silently removed to improve scores.

Ten split seeds are not three independent optimization seeds per fixed split.
Paired sign-flip tests, descriptive t95% intervals and per-family Holm correction
are exploratory because splits overlap on the same graph. Resource was an RTX5090;
paper uses A2000. Individual measured training durations are recovered where
recorded, but monetary cost is UNKNOWN and is not inferred from GPU time.

No extra GPU training was started for recovery. [Future three-seed config](../configs/future_three_seeds.json)
plans1,440 Dot/MLP runs; it is Proposed and NOT_VERIFIED for teacher approval.
Strict paper-protocol replication and node/hop intervention studies remain future
separate groups. Any future claim must distinguish replication from an improvement.
