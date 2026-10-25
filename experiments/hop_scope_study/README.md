# Fixed K=5, variable routing scope study

Technical execution: **300/300 primary trainings and300/300 mask evaluations complete**, with0 scientific training failures. All primary checkpoint reload checks passed.

This diagnostic ablation always computes hops0..5 and retrains with active
routing hops0..x, x1-5, including0-hop. It preserves the original Dot scorer,
LayerNorm, squash, one actual GAMMA layer, R2 and six scale rows. It does not
implement adaptive hop selection. Teacher approval: **NOT_VERIFIED**; user
execution authorization is explicit. Live completion status is in
[results/status.json](results/status.json).

[Audit/protocol](docs/00_AUDIT_AND_PROTOCOL.md),
[validation](docs/01_VALIDATION.md), [Pilot](docs/02_PILOT.md),
[results](docs/03_RESULTS.md), [limitations](docs/04_INTERPRETATION_AND_LIMITATIONS.md),
[failures](docs/05_FAILURE_LOG.md), [Git/provenance](docs/06_GIT_AND_PROVENANCE.md).
Historical source/results/registries remain unchanged. New K5/x5 is this study's
matched control, not the old frozen K2 reproduction.

## Reproduce

Use the repository's documented training environment (Python3.12.14,
torch2.8.0+cu128, PyG2.7.0; exact installed evidence in results/environment.json).
Fresh installation remains NOT_VERIFIED. Do not upgrade a shared environment.
Commands below start from the parent working directory; all datasets, split
archives, logs, node arrays and checkpoints stay outside the Git checkout.

```powershell
git clone --branch exp/fixed-k-hop-gating https://github.com/PengSheng2281726867/26-1-CISC8006-001.git course_repo_checkout
Set-Location course_repo_checkout
python -B experiments/hop_scope_study/scripts/prepare.py --data-root ../local_data
python -B experiments/hop_scope_study/scripts/check.py --data-root ../local_data --run-root ../local_runs
python -B experiments/hop_scope_study/tests/test_analysis.py
python -B experiments/hop_scope_study/scripts/run.py --config experiments/hop_scope_study/configs/pilot.json --data-root ../local_data --run-root ../local_runs
python -B experiments/hop_scope_study/scripts/aggregate.py --pilot --data-root ../local_data --run-root ../local_runs
python -B experiments/hop_scope_study/scripts/run.py --config experiments/hop_scope_study/configs/full.json --data-root ../local_data --run-root ../local_runs
python -B experiments/hop_scope_study/scripts/eval_only.py --config experiments/hop_scope_study/configs/eval_only.json --data-root ../local_data --run-root ../local_runs
python -B experiments/hop_scope_study/scripts/aggregate.py --data-root ../local_data --run-root ../local_runs
python -B experiments/hop_scope_study/scripts/finalize_report.py
```

If a verified local cache is already available, preparation supports
`--import-from <existing-data-directory>`; it checks raw hashes and all masks,
then copies into the new external directory without editing the source.
`prepare.py --check-only` verifies inputs without preparing missing ones.
`run.py --plan` enumerates a config without training. Run the identical Full
command to resume: only complete cells with matching scientific fingerprints
and artifact hashes are skipped; failures remain immutable, retries get new IDs.
Pilot and Full use the same protocol and initialization; the12 verified Pilot
cells are included in the300 total, not counted as additional independent runs.
A fresh rerun creates new records; published hashes do not imply hosted checkpoints.

Plotting uses a separate existing environment with Python3.14.6,
Matplotlib3.11.0 and NumPy2.4.6 because the training environment has no Matplotlib.
From the repository root, invoke that environment's Python for:

```powershell
python -B experiments/hop_scope_study/scripts/plot.py
```

The actual local executions used existing interpreters; this workflow was not
independently rebuilt in a new environment. Dataset redistribution licensing is
NOT_VERIFIED. No datasets/labels/splits/predictions/checkpoints are published.

## Interpretation and evidence

Accuracy is reported in percent, deltas in percentage points. Error bars are
sample SD across10 overlapping splits, not uncertainty across independent graphs.
Full paired means,20,000-draw bootstrap95% intervals, exact sign-flip p and
within-dataset Holm correction are in results/paired_delta.csv. Validation-only
scope selection uses smallest x on ties; reusing validation for epoch/x can
create selection bias. No test-selected best-x claim.

Post-hoc masking uses each frozen x5 checkpoint, without updates, and has a
train/inference distribution mismatch. It measures dependence of that trained
model; its curve is distinct from retraining. Turning off routing candidates
does not avoid propagation, which stays at15 calls and maximum path5.
CPU RSS/additional host memory and monetary cost are UNKNOWN; GPU peak/increment
and actual times are measured. No universal acceleration claim.

Public results/ contains scalar per-run evidence, attempt/run matrix, graph/
split/source/checkpoint hashes and aggregate statistics. Raw local terminal/epoch
logs and arrays are retained by unique run ID under local_runs/runs. Scientific
runs truthfully record main SHA plus dirty status/source hashes because original
local Git metadata was read-only; the later publication commit is not their
execution commit. See docs/06_GIT_AND_PROVENANCE.md.

## Publication checks

For a normal writable clone, stage only reviewed new study paths and the three
minimal navigation/AI-use updates, then run the existing whole-index checker:

```powershell
python -B scripts/smoke_test.py
python -B scripts/check_publication.py
```

For a clone with read-only Git metadata, the following creates an exact candidate
index/object store in the external run directory and runs the same checker on
all index entries. It preserves actual source bytes and does not write refs,
push, or alter the original .git. Add `--commit` to create a local commit object
after the audit; the evidence receipt stays local.

```powershell
python -B experiments/hop_scope_study/scripts/publication_snapshot.py --run-root ../local_runs
```
