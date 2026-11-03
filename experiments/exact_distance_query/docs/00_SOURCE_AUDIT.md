# Source audit

Read root AGENTS/README, research/src/{model,train,data,factory,paths}.py,
course/common.py and metrics.py, claim/improvements/code audit, preparation,
smoke/publication scripts, existing hop-scope and LOHO protocols/configs/results,
source mapping, data manifest and original workspace reproduction notes.
Remote main verified `5e7eb902d32bda4665b5235582dc59eebf556178`; historical
branches Fixed-K and LOHO exist; requested new branch absent at audit.
Original workspace root has no Git repository. Read-only verified cache can be
copied into external private_data; never train or write in original workspace.
Source mapping SHA checks all passed. preservation_before.json inventories all
historical tracked content for final verification. No historical edits authorized.

Frozen GammaLayer uses PyG aggr=add/source_to_target. Supplied edge weights
multiply source messages; duplicate edges sum; no automatic loops or undirecting.
Five branches independently run biased Linear then p propagations, gamma scaling,
affine LayerNorm. R2: uniform fusion/squash, dot update, second weighted
fusion/squash; last updated logits are unused. used_alpha is the second round.
Bias follows final fusion; output LN/dropout/head/log_softmax. train_model uses
CrossEntropy (equivalent NLL), Adam, clipping and validation-best deep copies.
Checkpoint state dict has convs.0.*, norms.0.*, lin.*; keep compatible keys.
Initialization resets shared Linear, gamma Normal(1,.1), zero fusion bias;
LayerNorm defaults affine ones/zeros. G0 reuses frozen code without alteration.

Data manifest fixes graph content including directed edge counts. WebKB loaders
do not imply an undirected graph; retain actual edge_index. NormalizeFeatures,
CPU torch.randperm seeds102..111 and exact60/20/20 arrays are verified on reuse.
Existing prospective seed convention42/43/44 adopted. Labels never enter B or
query construction; transductive full topology is shared across all arms.

Paper [Table3](https://amir-ghz.github.io/PDFs/GAMMA.pdf), Appendix B, compares
gating versus uniform fusion at hop scopes1-2/1-3/1-4. It does not test binary
shortest-distance shells or fixed H0/H4 queries. Local LayerNorm/one actual layer/
60-20-20 differ from paper normalization/layer/split choices and stay frozen.
Official [code](https://github.com/amir-ghz/GAMMA), upstream
36d054b4ae53c0c8e360d85d056f5207d61c8281, MIT; attribution preserved.

Engineering issues: default Python lacks torch; existing GAMMA environment is
Python3.12.14/torch2.8.0+cu128/PyG2.7.0 on RTX5090. No shared environment changes.
Schannel clone failed SEC_E_NO_CREDENTIALS; command-local OpenSSL clone worked.
Nested .git ref creation is denied by workspace metadata protections. An independent
external Git metadata clone is used with GIT_DIR/GIT_WORK_TREE; original nested
.git remains intact. No global Git security/TLS settings changed, no history reset.
Teacher approval NOT_VERIFIED. User explicitly authorized actual training and PR.

## Verified topology scalars after cache preparation

All six actual edge tables are directed and contain original self-loops.
Raw edge duplicates are absent in these caches; tests separately cover duplicates.
Self-loop counts Texas16/Wisconsin16/Cornell3/Chameleon50/Squirrel140/Actor93.
Reciprocal unique-edge fractions range0.131-0.261. Chameleon/Squirrel have
no-incoming fractions0.621/0.576; these are directed upstream empty cases,
not proof of graph-wide isolation. Source tables and edge-order hashes are in
results/topology_audit.json, generated without labels/features in calculations.
Original loops remain in A; B0 has self-distance0 and Bp>0 excludes self.
