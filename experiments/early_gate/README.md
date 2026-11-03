# Early K2 Dot vs Uniform diagnostic

早期 K2 门控与均匀融合对照。

**Recovered: 120 executions**. Teacher approval: **NOT_VERIFIED**.

The early K2 experiment has a different initialization construction from the later gate sweep and Dot/MLP comparisons. Keep its 60 Dot and 60 Uniform records separate. The imported implementation is related code; historical execution commits remain UNKNOWN / pre-git experiment.

## File map / 文件归属

[All experiments / 全部实验](../README.md) · [Repository home](../../README.md)

| Purpose | Canonical files |
| --- | --- |
| Related imported code | [`research/src`](../../research/src) |
| Recovered configuration | [`experiments/historical_configs.json#early_gate`](../historical_configs.json#early_gate) |
| Results | [`experiments/analysis/early_gate.json`](../analysis/early_gate.json) |
| Audit | [`docs/CLAIM_AND_REPRODUCTION.md`](../../docs/CLAIM_AND_REPRODUCTION.md)<br>[`experiments/HISTORICAL_FAILURES.md`](../HISTORICAL_FAILURES.md) |

## Registry and evaluation

Records stay in the shared [registry](../registry.csv) and [run evidence](../recovered_runs.jsonl). Select the following exact `stage` values:

| Registry stage | Recovered entries |
| --- | ---: |
| `early_gate` | 120 |

From repository root, summarize existing records without training:

```powershell
python -B scripts/evaluate.py --registry experiments/registry.csv --stage early_gate
```

All counts above are recovered registry entries. Original metrics, hashes, failures and source provenance remain at their canonical paths. See [recovery audit](../../docs/EXPERIMENT_RECOVERY.md) and [historical failures](../HISTORICAL_FAILURES.md).
