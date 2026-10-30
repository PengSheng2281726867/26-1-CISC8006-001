# Implementation and data validation

Status: **PASSED**, 2026-10-25T11:21:54.614815+00:00.

Seven scientific tests passed: 15 actual propagation calls and six independently checked hop tensors at all five x; zero inactive alpha throughout R1-4; inactive feature/gradient exclusion; scope-sensitive synthetic output; constant architecture/full initialization/RNG/parameter budget; invalid masks/devices/scopes/missing data and finite empty graph; test-label perturbation leaves training state/selection unchanged.

Direct upstream network parity: CPU float64 and CUDA float32, R1/2/3, both eval and matched-dropout training; output, input gradient and every parameter gradient checked (12 cases). Tolerances CPU atol1e-10/rtol1e-9; CUDA atol2e-6/rtol2e-5. Actual errors in results/adapter_validation.json. No scientific behavior was changed to pass.

Four analysis known-answer tests also passed, covering sample SD, exact sign-flip, Holm, reproducible bootstrap and running-cell accounting. Existing repository smoke:13 tests,20 historical parity cases; retains a deliberate missing-data failure and two synthetic successful fixtures, excluded from scientific training counts. All six graphs and60 fixed splits rechecked against raw manifests and CPU seeded arrays; archive identity status in results/data_verification.json.

One command from repository root:

```powershell
python -B experiments/hop_scope_study/scripts/check.py --data-root ../local_data --run-root ../local_runs
```

Private logs are retained under local_runs/checks; public scalar acceptance evidence is results/validation.json. All old source bytes remain unchanged.
