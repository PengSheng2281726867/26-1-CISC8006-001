# Course repository handoff

Repository: https://github.com/PengSheng2281726867/26-1-CISC8006-001

The verified full import is `0f061de5377202f232afd26899826e8c5a825fb3`. The following
handoff commit is a real new publication; inspect Git HEAD for its final hash.
It adds verification records and a tested prospective CUDA-resource-reset fix,
without changing scientific model/factory/train source. Normal HTTPS Git push was
unavailable in the noninteractive shell; publication used the already authorized
GitHub connector, followed by Git fetch/tree verification. No force push or
credential extraction was used. The local recovery history remains separately preserved.

## What is actually complete

- 1,566 uniquely identified recovered execution records: 1,540 major/historical,
  24 superseded resource pilots, 2 anchor replays.
- 1,466 saved-prediction executions verified against4,398 artifact checksums and
  recomputed counts;100 historical README runs have count/log evidence, no weights.
- Frozen original/reproduction/MLP/LN/GELU source mapping, MIT notices, original
  source archive, privacy review and explicit unknown execution commits.
- 13 actual smoke tests passed, including20 official CPU/CUDA forward-gradient
  cases and CPU/CUDA synthetic run provenance. A deliberate missing-data failure
  fixture is retained, not classified as a scientific experiment.
- Six fresh upstream dataset preparations checked:72 raw files and60 exact split
  archives; independent evaluation CLI reproduced48 original summary groups.
- New configs/runner record commit, dirty state, config/seed/data/split/device,
  metrics, timing, logs, hashes and failures in unique ignored output directories.
- All required course audit documents, ideas, registry, AI-use and contribution
  templates are present. No existing scientific model was retrained.

## Scientific status

Reproduction is Component, not exact Table1/Table3 replication. The Dot forward
matches author code, but the universal gating-benefit claim is not established
under the different local protocol. MLP has a completed technical full matrix:
MLP?Dot mean?0.51pp, without significant direct improvements after Holm24.
LN?MLP mean+0.02pp; GELU?MLP+0.47pp; neither has a corrected direct gain.
Teacher approval and per-fixed-split3-seed requirement remain unresolved.

## Unknown / incomplete

Historical execution Git commits, many timestamps, monetary costs, teacher
approvals and individual human contributions remain UNKNOWN/NOT_VERIFIED.
Forty README records lack explicit seed metadata;100 lack checkpoints. Original
agent transcripts and3-phase human verification are incomplete. Installed versions
are recovered, but a fresh environment rebuild is unverified. External artifacts
have hashes and local logical locations, not a verified public archive.

Still required: confirm/approve claim and two pilots; at least3 optimization seeds
per fixed split or explicit instructor-approved alternative; human AI-use/contribution
verification; final course report/slides and Week12 freeze. No final Week12 tag exists.

## Exact local commands (from repository root)

```powershell
python -B scripts/smoke_test.py
python -B scripts/prepare_data.py --check-only
python -B scripts/run_experiment.py --config configs/baseline_texas.json --device cuda
python -B scripts/run_experiment.py --config configs/mlp_texas.json --device cuda
python -B scripts/evaluate.py --registry experiments/registry.csv --stage dot_mlp
python -B scripts/run_experiment.py --config configs/future_three_seeds.json --plan
```

Use the recorded compatible environment. Only the Baseline/MLP commands above
start real training; they were not run during recovery. The future command plans
1,440 runs without executing them; approval remains NOT_VERIFIED.
