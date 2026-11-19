# Evidence manifest

Execution date2026-10-29. Storage location: owner-authorized execution workstation,
local LOHO workspace, private_outputs/ relative to that workspace. Terminal records are copied into
evidence_snapshot/notes/ to preserve the exact hashed versions.
These artifacts are private and cannot be obtained directly from this public
repository. No public hosting or redistribution authorization is implied.

[Private artifact hash index](../results/private_artifact_checksums.csv) maps
relative batch/cell artifact IDs to bytes and SHA256 for actual arrays, metadata,
batch configuration/completion records and retained terminal/gate logs.
Each full_val/full_test/evidence.csv maps dataset/split/seed/checkpoint to run ID,
raw array/metadata/checkpoint/graph/split hashes, before/after state hashes,
identity errors, current execution Git commit/dirty status and runtime.
[Checkpoint inventory](../results/checkpoint_inventory.csv) records actual
external weights with relative owner-source IDs. Audit inventory in private
storage is distinct from the public CSV. Historical execution commits are not
inferred from current hashes. Inputs, labels and predictions are not included.

Validation observations: 94110; test observations:
94320, counting checkpoint-node pairs, not independent nodes.
Runtime sum across checkpoint evaluations: validation28.322s, test27.198s.
These wall times include repeated input hashing/loading and control forwards;
they are not pure GPU kernel timings or monetary costs. Device RTX5090,
existing torch2.8+cu128/PyG2.7 environment, one serial GPU process. Monetary cost
UNKNOWN. Summary/plot time and startup are not included in those cell sums.

Primary checkpoint coverage180/180 for val and180/180 for test, zero real failures.
Pilot6 cells reused in validation180. Each cell's metadata contains exact config,
start/end UTC, source/protocol hashes and actual Git/dirty state. Extension runs
honestly record dirty trees caused by newly generated public pilot summaries;
test starts after commit85bcfce. PRETEST_FREEZE.json has13 unchanged hashes.
All240 inventoried original weight files rechecked unchanged after test. Root
smoke verifies byte-identical protected sources. Existing historical registry,
old results and MLP source are unchanged.

This manifest intentionally publishes checksums and summary evidence, not raw
private logs. Git push/PR receipts are retained privately; actual publication
status is reported by the final task response. No merge or teacher approval is
claimed. See SYSTEM_TESTS.md and NEGATIVE_AND_FAILED_RUNS.md.
