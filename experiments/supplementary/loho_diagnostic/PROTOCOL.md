# LOHO protocol v1

Frozen before diagnostic outcomes, 2026-10-29. Teacher approval: NOT_VERIFIED.
This is a frozen-weight mechanism diagnostic, not an improvement pilot.
Base commit: 935a4303ed0d1410e29d9374cc1ce91b82dc527c. GAMMA attribution and MIT
terms remain in root LICENSE and NOTICE.md. Do not change protected source.

## Scope and sequence

Primary cohort: existing stability_v1/core Dot checkpoints, K4/R2, powers0..4,
one actual GAMMA layer, nodewise LayerNorm and Linear head. Seeds2026/2027/2028,
splits0..9, six heterophilic graphs. No new training. Pilot: Chameleon and Actor,
split0, all three seeds. Extended evaluation reuses pilot cells without duplication.
Historical v2 weights are inventoried separately; other K, scorers and variable-hop
models are outside this primary matrix. Missing cells are NOT_AVAILABLE.
Synthetic tests and original smoke precede validation pilot/full evaluation.
Freeze analysis implementation and validation report before test confirmation.
Use identical cohort/thresholds for test. Historical test exposure prevents a
claim of pristine study-level holdout. Graph access is transductive and distinct
from label selection; exploration uses validation labels only.

## Interventions and controls

Delta_loss = true-label NLL(masked) - NLL(full). Positive means deletion hurts.
Use original additive propagation, shared projection, channel scales, per-hop
LayerNorm, squash, bias, output LayerNorm and Linear/log_softmax. Eval disables
both dropouts. Never substitute paper L2 normalization.
Final-only leaves rounds0..R-2 unchanged; mask a selected nonzero hop before the
last used softmax, renormalize and recompute fusion/output. Full-routing masks
before every softmax from zero initial logits. Removed-branch agreement cannot
enter later fusion. Never remove0-hop. Use used_alpha, never softmax of final
post-update logits. Restrict global masking to the audited one-layer model.
Verify single-node/global equivalence; original/new outputs, alpha, NLL at
atol2e-6/rtol2e-5 float32; immutable state hashes; graph tensor hash including
labels/order, split file hash, masks vs saved artifacts/permutation and checkpoint
hashes. Reject unverifiable primary weights.

## Fixed analysis

Per checkpoint/mask: pooled nonzero-hop and per-hop descriptive Spearman;
within-node Spearman across hops1..4 with average ranks, valid count, undefined
fraction, mean/median. NA and reason for constants/nonfinite inputs.
Top1 excludes0-hop; ties choose lowest hop. Fixed epsilon1e-5 for positive,
negative and negligible delta fractions; no post-hoc threshold adjustment.
Report per-hop weights, mean/median delta, accuracy/NLL full and masked,
accuracy(masked)-accuracy(full), flips and paired full-routing minus final-only
loss changes, absolute differences and sign reversals. Average seeds within
split first, then equal-weight split means with sample SD(ddof1); report seed
SD within split and counts. Overlapping splits are not independent graph trials.
No p-values, significance claims or node bootstrap. Comparisons are exploratory.
Figures from real runs only: alpha/delta scatter with zero line, per-hop mean
weights/deltas, paired intervention differences, Top1 histograms/negative
fractions, split rho. Titles state dataset/K/R/masks/evaluation set/seed and
checkpoint counts. Preserve all signs and failures.

## Budget and provenance

At most180 existing checkpoints, nine conditions each, separately val/test.
One serial GPU process, <=30 GPU minutes inference and <=2 GiB GPU/private
artifacts expected. Caps/estimates are not measured costs; monetary cost UNKNOWN.
No optimizer/backward. Every attempt records UUID/time, git/dirty state,
config/source/protocol hashes, device/runtime, immutable inputs and failure log.
Private arrays/absolute locations stay in authorized local storage. Public
outputs contain aggregates, figures, relative artifact identifiers and hashes.

## Interpretation

Deletion sensitivity is not strict causal attribution. Correlated hops,
renormalization, nonlinear interactions and intervention distribution shift
are alternatives to incorrect agreement. Near-zero does not prove redundancy.
Routing differences may be consistent with compensation without identifying its
cause. Results cannot establish Sparse Hop Selection, Leave-One-Out Agreement
or MLP superiority. Changes require dated version/rationale, preserving v1.
