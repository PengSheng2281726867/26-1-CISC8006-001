# GAMMA Exact-distance and Query-gating

Prospective technical study; teacher approval **NOT_VERIFIED**. MIT GAMMA by
Amir Ghazizadeh, Rickard Ewetz and Hao Zheng; root LICENSE and NOTICE apply.
[Frozen protocol](PROTOCOL.md), [audit](docs/00_SOURCE_AUDIT.md),
[validation](docs/01_VALIDATION.md). Historical experiments remain immutable.

Four matched arms: G0 Walk+Consensus; G1 binary shortest-distance+Consensus;
G2 Exact+normalized H0 query; G3 Exact+normalized original Walk H4 query.
Empty Exact candidates are zeroed after LN and masked in softmax. All include0.
Parameters, initialization, data splits and training budget are matched.

From repository root in the existing compatible GAMMA environment:

```powershell
python -B -m unittest discover -s experiments/exact_distance_query/tests -v
python -B scripts/smoke_test.py
python -B -m experiments.exact_distance_query.src.run full --plan
python -B -m experiments.exact_distance_query.src.run prepare --data-root ../private_data --import-from <VERIFIED_CACHE_ROOT>
python -B -m experiments.exact_distance_query.src.run smoke --data-root ../private_data --runs-root ../private_runs
python -B -m experiments.exact_distance_query.src.run pilot --data-root ../private_data --runs-root ../private_runs
python -B -m experiments.exact_distance_query.src.run full --data-root ../private_data --runs-root ../private_runs
python -B -m experiments.exact_distance_query.src.run empty_control --data-root ../private_data --runs-root ../private_runs
python -B -m experiments.exact_distance_query.src.analyze --runs-root ../private_runs
```

Private inputs are external `<PRIVATE_DATA_ROOT>`; logs/checkpoints are external
`<PRIVATE_RUN_ROOT>/<run_id>/`. No dataset, label, node prediction or weight is
published. Reuse checks artifact hashes and identical scientific fingerprints;
failed attempts are retained. Existing external Git metadata is optional and
recorded in the audit; ordinary clones use normal Git metadata.

If the training environment lacks matplotlib, set `GAMMA_PLOT_PYTHON` to the
executable of an existing NumPy/matplotlib environment before `analyze`.
Plots use that interpreter; scientific training is unchanged.

Technical matrix completed: **Pilot48/48; Full720/720**, with48 Pilot and4 Smoke
cells reused exactly once. Nine bounded empty-policy controls and720 dedicated
checkpoint inference profiles also completed. Teacher approval NOT_VERIFIED.
[Full results](docs/03_FULL_RESULTS.md), [interpretation and negative cases](docs/04_INTERPRETATION.md),
[failures/deviations](docs/05_FAILURES.md), [Git/provenance](docs/06_GIT_AND_PROVENANCE.md),
[machine-readable coverage](results/full/coverage.json).

Optional dedicated measurement (no training):
`python -B -m experiments.exact_distance_query.src.profile --data-root ../private_data --runs-root ../private_runs`.
Scientific code fingerprints exclude reporting/profiling code; those scripts and
their actual Git commits/source hashes are separately recorded. Public index
checks do not imply data access or external weight availability.
