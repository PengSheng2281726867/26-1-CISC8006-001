# Code and research evidence audit

Audited 2026-10-20; factual recovery, not retroactive approval. Labels: VERIFIED_FROM_FILES,
INFERRED_FROM_CODE, UNKNOWN, NOT_VERIFIED. Source and artifact hashes are in
[the manifest](../experiments/recovery_manifest.json).

## Project roots and provenance

The existing workspace held an official `GAMMA/` clone and an isolated `test_mlp/`
experiment tree. The workspace root itself was not a Git repository. The official
clone had real author history, HEAD `36d054b4ae53c0c8e360d85d056f5207d61c8281` and origin
https://github.com/amir-ghz/GAMMA.git. Existing worktree differences were present
before this course recovery. No history was reset or rewritten. A new independent
course repository was created, without copying nested `.git` directories.

Paper authors: Amir Ghazizadeh, Rickard Ewetz, Hao Zheng; NeurIPS2025.
[Primary paper](https://amir-ghz.github.io/PDFs/GAMMA.pdf). The author code has MIT permission; both MIT notices
are preserved. Dataset and paper-PDF redistribution rights are NOT_VERIFIED,
so these artifacts are not uploaded. Author code license does not imply data rights.

## Original / reproduction / improvement mapping

| Area | Origin and behavior | Evidence |
| --- | --- | --- |
| research/upstream_snapshot | Seven unchanged author files from cited Git commit | Per-file SHA256 and MIT license |
| research/src/model.py | Independent equivalent GAMMA forward plus optional shared MLP | Historical 20-case alignment; re-run in course copy |
| research/src/factory.py | Random K4 template, matched shared weights, separate scorer init, seeds | Frozen file hash; paired initialization metadata |
| research/src/train.py | Common optimizer/training/selection/evaluation; deep-copy best validation state | Frozen file hash; saved epoch traces |
| research/src/data.py | PyG loaders, NormalizeFeatures, persisted seeded 60/20/20 masks | Raw/processed/split hashes and graph shapes |
| research/ablation_mlp | Existing LN-only and GELU-only variants and matched initializers | Unchanged file hashes, gradients, 480 new models |
| course and scripts | Newly added course configs, provenance, evaluation, safety checks | Actual current Git commits, smoke reports |

Exact mapping and all copied Python hashes: [source_mapping.json](../experiments/source_mapping.json).
Independent Baseline/MLP commands share one runner and unchanged `run_one()`;
config method is the selector. Current code is runnable with the recorded environment.
Fresh installation remains NOT_VERIFIED. Fresh downloads/preparation for six
datasets were checked; full new real-data model training was not launched.
Historical harnesses are also retained as audit-only text:36 exact copies and3
path-redacted report-script derivatives with both hashes in
[archives](../archives/README.md); this does not claim their old directory-based
entry points can run from the archive layout.

## Important behavior and differences

- num_layers2 counts the final Linear: one actual GAMMA message-passing layer.
- K changes actual powers to0..K, including0-hop; R2 is separate. Each branch
  recomputes projection/propagation, so total propagations are1/3/6/10 for K1..4.
- Hop tensor is[N,P,32]; shared learnable LayerNorm is used, not paper node-L2.
  Shared projection, hop channel scales, squash and bias are retained.
- Routing logits start at0 each forward. Dot=sum(hop*fused); MLP outputs scalar
  agreement from concat64. b is accumulated, then next routing softmax uses it.
  The final score update is unused in the current output, as in author code.
- Author helper for routing weights uses a post-final-update softmax; diagnostics
  use the last coefficients actually consumed in forward instead.
- Authors' best-state `.copy()` is shallow. Controlled experiments consistently
  deep-copy best validation weights; historical README runs retained shallow copy.
- gamma.py hardcodes R1 on the homophilic scripts despite CLI default2. These
  historical results cannot test R2 dynamic-routing gains.

## Datasets, metrics, randomness and environment

Six heterophilic graphs, ten fixed60/20/20 splits (102–111), training seed42+split.
No per-fixed-split multi-seed matrix exists. Accuracy correct/count is a fraction,
tables use percent, deltas pp. Mean±sampleSD is the public aggregation convention;
earlier reports used population SD. All normalization and mask details are recorded.
PyG edge counts for Texas/Wisconsin/Cornell (325/515/298) differ from paper Table1
(309/499/280); exact raw hashes and preprocessing take precedence over names.

Recorded runtime: Python3.12.14, torch2.8.0+cu128, PyG2.7.0, CUDA12.8, RTX5090.
The paper used RTX A2000; speedups are not transferred across hardware.
Historical installed version list is retained; one direct local build reference
was replaced by its installed version in a documented public lock derivative.

## Recovered evidence and limitations

1,566 registry entries: 1,540 major/historical executions plus24 superseded
resource pilots and2 anchors. 1,466 saved-prediction executions were rechecked
against4,398 artifact SHA256 values and reconstructed test counts. The100 README
runs have metrics/counts and terminal-log hashes, not weights. Forty of those
README records omit explicit seeds; their seed is UNKNOWN in the registry even
though source inspection suggests42+split. No TensorBoard events were found.

Full model re-inference during this recovery was not repeated for all old
models; existing full-checkpoint verifier outputs are preserved. Current audit
checks hash integrity and predictions, not historical wall-clock truth or proof
that an old configuration file was exactly the one executed. Run-level Git hash,
many individual timestamps, monetary costs, teacher approval, full agent transcripts
and human contributions are UNKNOWN/NOT_VERIFIED.

Potential fairness limitations: MLP adds2,113 parameters (not parameter matched),
LN adds64; no asymmetric tuning was done but default fixed hyperparameters need
not be optimal for all methods. Split overlap/one seed confound two variability
sources. LN/GELU train timing uses a historical MLP control; fresh inference was
remeasured contemporaneously. Repeated test-set inspection makes future tuning
on this same evidence exploratory. Current course gaps are explicit in
[COURSE_COMPLIANCE](COURSE_COMPLIANCE.md).
