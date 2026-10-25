# CISC8006 — GAMMA reproduction and MLP routing

Research evidence recovery and a prospective reproducibility harness. **This is
a component-level reproduction, not an exact reproduction of the paper tables.**

Paper: Amir Ghazizadeh, Rickard Ewetz, Hao Zheng. *GAMMA: Gated Multi-hop Message
Passing for Homophily-Agnostic Node Representation in GNNs*, NeurIPS 2025.
[Paper](https://amir-ghz.github.io/PDFs/GAMMA.pdf); [official code](https://github.com/amir-ghz/GAMMA),
MIT, upstream `36d054b4ae53c0c8e360d85d056f5207d61c8281`. See [NOTICE](NOTICE.md).

## Claim and findings

Candidate course claim: node-specific iterative gating improves node classification
over uniform hop fusion while retaining shared projection and global channel scaling.
It corresponds to Appendix B/Table 3. Teacher approval: **NOT_VERIFIED**. The
retrospective protocol is documented but is not a claimed course-approved freeze.

Local Dot−Uniform is positive in 11/18 Dataset×K conditions. MLP−Dot averages
−0.51 pp (12/24 positive). LN−MLP averages +0.02 pp; GELU−MLP +0.47 pp.
None of those direct comparisons is significant after its original family-wise
Holm correction. A separate Actor/GELU K3-versus-K1 interaction has corrected
p=0.03516; this does not establish a significant fixed-K improvement.
[All results](reports/RESULTS_SUMMARY.md) and [course gaps](docs/COURSE_COMPLIANCE.md).

## Layout and historical status

```text
research/src/                  frozen Dot/MLP implementation, training and data helpers
research/ablation_mlp/         frozen LN/GELU scorer variants
research/upstream_snapshot/    author code + MIT license at the cited commit
course/                       new provenance, config and evaluation adapters
configs/                      historical configs + proposed future seed matrices
experiments/registry.csv       1,566 uniquely identified recovered executions
experiments/recovered_runs.jsonl  normalized per-run metrics and provenance
experiments/artifacts_manifest.jsonl  4,398 external artifact hashes
archives/                     historical source audit copies with explicit redaction metadata
environment/                  recovered installed versions, installation limitations
scripts/                      run, prepare, evaluate, smoke and publication checks
tests/                        synthetic evaluation, fairness and provenance tests
reports/                      results, figures and actual system-test evidence
docs/                         audits, claim, recovery and course compliance
```

All recovered execution commits are UNKNOWN (`pre-git experiment`). The import
commit does not identify the code version at execution. No weights or datasets
are uploaded. Obtain external artifacts from their owner; no public artifact
hosting/availability is implied by a checksum. Original files remain intact.

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
[environment recovery](environment/lock_recovery.json). This is a version pin
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
`outputs/`. See [actual results](reports/SYSTEM_TESTS.md).

## Data preparation

No graph data or split archives are redistributed. Dataset license and
redistribution permission remain NOT_VERIFIED; download from upstream through
PyG according to its terms. Raw content SHA256 and expected graph shapes are
recorded in [data manifest](experiments/data_manifest.json).

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
[data validation evidence](reports/data_preparation_verification.json).

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
descriptive t intervals and Holm correction; see [claim](docs/CLAIM_AND_REPRODUCTION.md).

## Proposed three-seed follow-up (not launched)

```powershell
python -B scripts/run_experiment.py --config configs/paired_texas_three_seeds.json --plan
python -B scripts/run_experiment.py --config configs/future_three_seeds.json --plan
```

These enumerate 6 and 1,440 runs respectively. Removing `--plan` starts training;
do so only after human/teacher protocol approval and budget review. Historical
ten-split variability does not supply three optimization seeds per fixed split.
[Improvement ideas](docs/IMPROVEMENTS.md) records two additional untested ideas
as Proposed, not completed pilots.

## Course evidence and limitations

- [Code audit](docs/CODE_AUDIT.md), [recovery](docs/EXPERIMENT_RECOVERY.md),
  [claim/paper differences](docs/CLAIM_AND_REPRODUCTION.md),
  [improvements](docs/IMPROVEMENTS.md), [compliance](docs/COURSE_COMPLIANCE.md).
- [AI usage](AI_USAGE.md) is factual and still needs human verification;
  [contributions](CONTRIBUTIONS.md) leaves unverified names/roles unassigned.
- [Publishing review](docs/PUBLICATION_REVIEW.md), [Git recovery](docs/GIT_RECOVERY.md).
- Teacher approvals, full multi-seed follow-up, fresh environment installation,
  externally accessible artifact archive, final course slides and Week12 freeze
  are not complete. No Week12 final tag is created.


- [Fixed-propagation / variable-hop-gating study (2026-10-25)](experiments/hop_scope_study/README.md):300 retrainings and300 inference-only mask evaluations; technical matrix complete, teacher approval NOT_VERIFIED.
