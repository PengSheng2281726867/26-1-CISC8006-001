# Dot vs Uniform across propagation ranges

K2–4 的 Dot / Uniform 对照。

**Recovered: 360 executions**. Teacher approval: **NOT_VERIFIED**.

Six graphs, K2–4, ten splits, Dot and Uniform: 360 recovered executions. Changing K changes propagation and routing scope together. This differs from the fixed-K5 study, which holds propagation fixed. Uniform K1 was not run. Historical execution commits remain UNKNOWN / pre-git experiment.

## File map / 文件归属

[All experiments / 全部实验](../README.md) · [Repository home](../../README.md)

| Purpose | Canonical files |
| --- | --- |
| Related imported code | [`research/src`](../../research/src) |
| Recovered configuration | [`experiments/historical_configs.json#gate_sweep`](../historical_configs.json#gate_sweep) |
| Results | [`experiments/analysis/gate_sweep.json`](../analysis/gate_sweep.json)<br>[`reports/RESULTS_SUMMARY.md`](../../reports/RESULTS_SUMMARY.md) |
| Audit | [`docs/CLAIM_AND_REPRODUCTION.md`](../../docs/CLAIM_AND_REPRODUCTION.md)<br>[`experiments/verification/historical_alignment.json`](../verification/historical_alignment.json) |

## Registry and evaluation

Records stay in the shared [registry](../registry.csv) and [run evidence](../recovered_runs.jsonl). Select the following exact `stage` values:

| Registry stage | Recovered entries |
| --- | ---: |
| `gate_sweep` | 360 |

From repository root, summarize existing records without training:

```powershell
python -B scripts/evaluate.py --registry experiments/registry.csv --stage gate_sweep
```

All counts above are recovered registry entries. Original metrics, hashes, failures and source provenance remain at their canonical paths. See [recovery audit](../../docs/EXPERIMENT_RECOVERY.md) and [historical failures](../HISTORICAL_FAILURES.md).
