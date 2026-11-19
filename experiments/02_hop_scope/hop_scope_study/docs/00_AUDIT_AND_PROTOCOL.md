# Fixed propagation / variable routing scope: frozen protocol v1

Frozen before implementation/training, 2026-10-25. Explicit user authorization;
teacher approval **NOT_VERIFIED**. Diagnostic ablation, not a new adaptive network.
H1: accuracy need not increase monotonically with x. H2: validation-selected x may
vary by dataset. H3 exploratory: retraining and post-hoc curves may differ.
Null and negative results are valid.

## Audit

Target main SHA `935a4303ed0d1410e29d9374cc1ce91b82dc527c`; initially clean.
Remote `PengSheng2281726867/26-1-CISC8006-001`. Clone succeeded with OpenSSL after
Schannel SEC_E_NO_CREDENTIALS. Fetch and branch creation were attempted but denied
Git metadata writes; escalation is disabled. Record publication limits honestly.
No force push, history rewrite or main modification.

Read root AGENTS, README, AI_USAGE, CONTRIBUTIONS, claim/improvements/results,
research/src, course, preparation/run/evaluation/smoke/publication scripts,
historical configs, protocols, data manifests and registries. Read original
workspace HOP_SWEEP, GATE_ABLATION, baseline reproduction, v2 protocol/environment
and provenance. Original root has no Git repo; upstream GAMMA subtree HEAD
`36d054b4ae53c0c8e360d85d056f5207d61c8281`. Original workspace remains read-only.
Source/document search found no identical fixed-propagation/variable-routing
experiment. Local before/after inventories protect frozen files and histories.

| Study | Computed powers | Routing candidates | Budget | Role |
| --- | --- | --- | --- | --- |
| Historical Dot/MLP K1-4 | 0..K | 0..K | changes with K | context |
| Historical Dot/Uniform K2-4 | 0..K | dynamic/uniform, same powers | changes with K | context |
| New full control | 0..5 | 0..5 | six scale rows | retrain x5 |
| New intervention | 0..5 | 0..x | six scale rows | retrain each x |
| New post-hoc | 0..5 | 0..x | frozen x5 checkpoint | inference only |

Code evidence: research/src/model.py hop_embeddings independently projects each
branch and propagates power times. Powers0..5 yield **15 propagate calls**, maximum
chain5, six retained tensors. GammaLayer.forward: softmax, weighted sum, squash,
Dot agreement, accumulated logits, R iterations. GammaNet constructs num_layers-1
convs: num_layers2 means **one GAMMA layer** plus Linear. Adapter will inherit
verified components and alter only allowed routing softmax candidates. MIT
attribution in NOTICE and upstream LICENSE retained; versions are main/upstream
SHAs above. Historical originals and registries must remain byte-identical.

## Locked protocol

K_max5; powers_full=[0,1,2,3,4,5]; active0..x (always0), x1-5; hidden32;
actual GAMMA layers1; R2; six gamma rows at all x. Original additive directed-edge
operator, gamma scaling, LayerNorm, Dot agreement, squash. p-hop means p-step
walks, not shortest-path shells. Mask before every softmax: inactive alpha exactly0,
active sum1; never truncate propagation. x5 matches unmasked original forward,
input and parameter gradients. No extra scorer/layer/normalization/loss.

Adam lr0.02, weight_decay0.0001; dropout input0.2/hidden0.8; gradient clip1;
ReduceLROnPlateau(mode=max,factor0.5,patience50,min_lr1e-6); max500 epochs;
early-stop50; strict validation improvement, earliest epoch on ties; deep-copy
best checkpoint. Reuse research/src/train.py unchanged. Test only after selection.
New random six-hop Dot initial state, identical full-state hashes at every x,
not historical K4 initialization. Reset RNG per arm. Dropout shapes match; stopping
times can differ. Inactive gamma classification gradients zero; Adam weight decay
may still update rows. All parameters stay in the same optimizer groups.

All six datasets: Texas,Wisconsin,Cornell,Chameleon,Squirrel,Actor. Preserve
NormalizeFeatures and raw graph hashes/shapes/edges from experiments/data_manifest.json.
Ten fixed60/20/20 splits, CPU torch.randperm seeds102..111; training seed42+split
(42..51). Verify raw hashes and mask arrays/checksums. Copy verified local inputs
read-only into external local_data, or download upstream. Never redistribute them.
Paper text differs (L2,50/25/25,two GNN layers); preserve reproducible local
LayerNorm,60/20/20,one actual GAMMA layer. Paper1-x is not local inclusive0..x.
K5/x5 is the new matched control, never a historical frozen reproduction.

Environment verified: Python3.12.14,torch2.8.0+cu128,PyG2.7.0,NumPy2.5.2,
SciPy1.18.1,CUDA12.8,RTX5090 32GB,driver610.88. Strict deterministic algorithms,
CUBLAS_WORKSPACE_CONFIG=:4096:8,TF32 off. CPU threads1 throughout new study.
No shared environment changes. Monetary cost UNKNOWN.

## Stages and budget

Audit precedes Build; synthetic propagation/mask/parity/gradient/fairness/invalid
input tests, split verification and existing smoke precede Pilot; record validation.
Pilot Texas/Chameleon, split0/1, x1/3/5=12 trainings at full500/50 budget.
Write Pilot summary before Full. Reuse Pilot only with identical scientific source,
config,data,initialization and verified checkpoint hashes. Full6x10x5=300 unique
cells, including validated Pilot cells. Alternate x order by split, one GPU process.
All60 x5 checkpoints get five eval-only masks=300 diagnostics, without updates.
Pilot measures throughput; run all feasible batches, never silently reduce budget
or drop poor datasets. External limits require PARTIAL plus pending/failed matrix.
Record OOM before equivalent optimization; K4 fallback would be separate, not pooled.

Each attempt: unique ID,Git SHA/dirty,config/source/graph/split/init/checkpoint
hashes,seed,actual layers/powers/R,environment,UTC start/end,runtime,memory,
status,failure traceback and artifact hashes. Never overwrite runs. Resume verifies
fingerprints/artifacts. Weights/logs/arrays outside Git; public scalar stats/hashes.

## Pre-specified analysis

Primary paired delta=100*(test_accuracy_x-test_accuracy_5),pp, within dataset/split/
seed: mean and sampleSD(ddof1), percentile bootstrap95% CI (20,000 draws,
seed20261025), exact two-sided sign-flip p, Holm within four contrasts per dataset.
Overlapping splits limit independence; inference descriptive/exploratory. Report
all x validation/test mean+/-SD,accuracy/delta plots,time,memory,parameters,failures.
Per split choose maximum validation accuracy, ties smallest x; report selected
test score and x distribution. Reused validation for epoch/x induces selection
bias. Dataset validation-best mean is descriptive; no test-based choice.
Separate retrain and post-hoc statistics/curves. Post-hoc has train/inference
mismatch and measures dependence of trained x5. All propagation cost remains;
no unmeasured speedup or universal optimal-hop/per-node-adaptive claims.
