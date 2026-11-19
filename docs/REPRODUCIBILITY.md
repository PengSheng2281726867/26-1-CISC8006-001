# 安装、数据与运行

[项目首页](../README.md) · [实验索引](../experiments/README.md)

## Environment and installation

Existing tested training environment: Python 3.12.14, torch 2.8.0+cu128,
torch-geometric 2.7.0, CUDA 12.8, RTX 5090. Do not modify a shared environment.
Create an isolated environment and use the recovered versions:

```powershell
conda create -n cisc8006-gamma python=3.12.14
conda activate cisc8006-gamma
python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
python -m pip install torch-scatter==2.1.2+pt28cu128 torch-sparse==0.6.18+pt28cu128 -f https://data.pyg.org/whl/torch-2.8.0+cu128.html
python -m pip install -r environment/historical-runtime.lock.txt
```

The existing environment is verified; the above **fresh installation is
NOT_VERIFIED**, especially platform-specific wheels. The recovered lock converts
one local build reference to its installed package version; see
[environment recovery](../environment/lock_recovery.json). This is a version pin
list, not a hash-locked, independently rebuilt environment. The imported model
can use CPU; CUDA is needed to match GPU measurements. No global dependency
changes were made during recovery.

## One-command checks (no dataset download, no full training)

From the repository root, using a compatible environment:

```powershell
python -B scripts/smoke_test.py
python -B scripts/run_experiment.py --config configs/future_three_seeds.json --plan
```

The smoke test checks official forward/gradients, K1–4, all four scorers,
nonzero gradients, metric answers/units/direction, node-ID alignment, matched
configs, label isolation, unique registry IDs, frozen source hashes and failure
provenance. It retains a deliberately failed missing-data fixture under ignored
`outputs/`. See [actual results](../reports/SYSTEM_TESTS.md).

## Data preparation

No graph data or split archives are redistributed. Dataset license and
redistribution permission remain NOT_VERIFIED; download from upstream through
PyG according to its terms. Raw content SHA256 and expected graph shapes are
recorded in [data manifest](../experiments/data_manifest.json).

```powershell
python -B scripts/prepare_data.py
python -B scripts/prepare_data.py --check-only
```

These commands create only ignored `research/data/` caches and ten CPU-seeded
60/20/20 splits (seeds102–111), use NormalizeFeatures and verify raw hashes and
split arrays. Recreated NPZ ZIP metadata may change archive hashes despite
identical mask arrays; both facts are recorded. Processed torch serialization
hashes may be environment-dependent. No silent acceptance of different raw
graph content is allowed. Fresh downloads/preparation of all six datasets and60
exact split archives were actually checked in the existing recorded environment;
a fresh environment build remains NOT_VERIFIED. See
[data validation evidence](../reports/data_preparation_verification.json).

## Independently run Baseline and MLP

```powershell
python -B scripts/run_experiment.py --config configs/baseline_texas.json --device cuda
python -B scripts/run_experiment.py --config configs/mlp_texas.json --device cuda
```

Both use the same frozen training loop and only switch the scorer. They start
from matched random initializations; neither loads pretrained weights. Each run
gets a fresh `outputs/<unique-run-id>/` directory with `config.json`,
`metadata.json`, `terminal.log`, `epochs.csv`, `result.json`, `metrics.json`,
`predictions.npz`, `model.pt` and checksums. Failure metadata is retained. Git
commit/dirty state and code/config/data/split hashes are captured. A dirty or
uncommitted tree warns explicitly. No old result is resumed or overwritten.

## Evaluate existing metrics or local predictions

```powershell
python -B scripts/evaluate.py --registry experiments/registry.csv --stage dot_mlp
python -B scripts/evaluate.py --predictions outputs/<run-id>/predictions.npz
```

The second command uses the actual run ID produced by training. Accuracy is a
fraction, higher is better; percent=100×fraction. Across splits we report equal
weight means and sample SD (ddof1), never pool test nodes across overlapping
splits as independent samples. Recovered reports give paired sign-flip tests,
descriptive t intervals and Holm correction; see [claim](../docs/CLAIM_AND_REPRODUCTION.md).

## Historical Dot/MLP three-seed follow-up (not launched)

```powershell
python -B scripts/run_experiment.py --config configs/paired_texas_three_seeds.json --plan
python -B scripts/run_experiment.py --config configs/future_three_seeds.json --plan
```

These enumerate 6 and 1,440 runs respectively. Removing `--plan` starts training;
do so only after human/teacher protocol approval and budget review. This plan applies to historical Dot/MLP only. Experiment 3 already has three optimization seeds per fixed split; do not launch this legacy plan solely to repair an outdated global status.
[Historical improvement ideas](IMPROVEMENTS_HISTORY.md) records two additional untested ideas
as Proposed, not completed pilots.
