# Experiment recovery and evidence grades

Recovered 2026-10-20 from source/configuration files, JSON/CSV, terminal logs,
serialized predictions, checkpoints and existing verifier reports. Originals were
read only. A normalized, path-redacted derivative is published; it does not replace
the original records. Source hashes let the owner audit each derivation.

| Stage | Registry entries |
| --- | --- |
| historical_readme | 100 |
| early_gate | 120 |
| gate_sweep | 360 |
| dot_mlp | 480 |
| components | 480 |
| v1_pilot | 24 |
| anchor | 2 |


Total1,566 unique IDs. Major/historical matrices total1,540; superseded Pilot24
and anchor2 are additionally identified. Qualified Pilot copies reused in Full
are not counted as new training. The three main matrices have1,320 execution
records, but180 Dot conditions were exactly re-executed, giving1,140 unique
method/K/Split cells. None becomes20 independent splits.

## Evidence grades

- **ARTIFACT_HASHES_AND_SAVED_PREDICTIONS_VERIFIED (1,466)**: all4,398 model,
  prediction and trace-file hashes checked; saved predictions/labels/masks align,
  masks partition nodes, and recomputed test counts equal records. Existing full
  model-reload verifier reports are retained; this recovery did not re-infer all
  checkpoints. This verifies saved-file consistency, not a historical execution commit.
- **METRIC_COUNTS_AND_TERMINAL_LOG_HASH_VERIFIED_NO_CHECKPOINT (100)**:
  README experiments have aggregate records, per-split correct/size and terminal
  log checksum matches. Original script saved no weights; checkpoint-based
  re-inference is impossible without a new run. Explicit seed metadata exists
  for60 records;40 remain UNKNOWN rather than promoting code inference to fact.
- **Historical failure narratives**: memory drift, analysis assertion/type errors,
  PDF download and plot-layout problems have documents. Not every original terminal
  exception has a retained raw log. No `failure.json` files or TensorBoard event
  files were found in the inspected research tree; absence is not proof no failure occurred.

Registry: [CSV](../experiments/registry.csv), [normalized JSONL](../experiments/recovered_runs.jsonl),
[external artifacts](../experiments/artifacts_manifest.jsonl), [source manifest](../experiments/recovery_manifest.json).
Every execution has a stable ID based on stage/dataset/K/split/method, a source
checksum, evidence status and UNKNOWN execution commit. No historical Git date
or timestamp was generated. Per-run start/end is UNKNOWN unless an original record
actually supplied it; group-level time is never assigned as an individual duration.
Costs remain UNKNOWN.

## Source/data limits and privacy

Raw graph files/labels, splits, model weights and predictions are excluded from
Git. External locations use `external://historical/` plus research-relative paths,
never a private drive or user home. These logical locations identify the owner's
local archive; they are not functioning public download links. An authorized durable
archive is still needed before final course freeze.

Raw dataset SHA256, node/feature counts and split seeds are published. A new cache
may serialize the same graph to different torch bytes; new NPZ container metadata
may change SHA while arrays match. Preparation verifies raw content and exact
seed-generated mask arrays, recording both archive hashes and identity status.
Six datasets were freshly downloaded into this independent course cache, their
raw hashes checked and60 exact historical split archives recreated; a subsequent
check-only command passed. This validates data preparation in the existing
environment, not a new environment rebuild or a full real-data training rerun.
See [actual data preparation check](../reports/data_preparation_verification.json).

## What requires a future rerun

1. At least3 training seeds per fixed split, or explicit instructor approval of the
   historical split-based uncertainty approach. Existing10 seeds only provide1 per split.
2. A course-approved frozen claim/protocol. Current scientific code/config hashes
   are retrospective evidence, not instructor approval.
3. Strict paper Table3 protocol if exact numerical replication is claimed; use a
   new group for50/25/25, layer/normalization/hop changes rather than altering history.
4. A clean-commit execution to link artifacts prospectively to the import-derived code.
   This is a new experiment, not a replacement execution hash for an old one.

Commands: `python -B scripts/run_experiment.py --config configs/paired_texas_three_seeds.json --plan`
and `python -B scripts/run_experiment.py --config configs/future_three_seeds.json --plan`.
They plan6 and1,440 runs. No training is launched with `--plan`; no follow-up was
silently run during recovery. The new runner preserves failures and never overwrites
a previous output directory.
