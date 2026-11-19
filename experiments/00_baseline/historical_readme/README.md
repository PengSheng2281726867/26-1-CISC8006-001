# Historical README reproduction

最初 README 基线复现。

**Recovered: 100 executions**. Teacher approval: **NOT_VERIFIED**.

These early records retain shallow best-checkpoint copying and non-strict GPU determinism. They are historical context and must not be pooled with the later matched controls. The imported implementation is related code, not proof of the historical execution version; execution commits remain UNKNOWN / pre-git experiment.

## File map / 文件归属

[All experiments / 全部实验](../../README.md) · [Repository home](../../../README.md)

| Purpose | Canonical files |
| --- | --- |
| Related imported code | [`research/src`](../../../research/src) |
| Recovered configuration | [`experiments/historical_configs.json#readme`](../../historical_configs.json#readme) |
| Results | [`experiments/analysis/readme.json`](../../analysis/readme.json) |
| Audit | [`docs/EXPERIMENT_RECOVERY.md`](../../../docs/EXPERIMENT_RECOVERY.md)<br>[`experiments/HISTORICAL_FAILURES.md`](../../HISTORICAL_FAILURES.md) |

## Registry and evaluation

Records stay in the shared [registry](../../registry.csv) and [run evidence](../../recovered_runs.jsonl). Select the following exact `stage` values:

| Registry stage | Recovered entries |
| --- | ---: |
| `historical_readme` | 100 |

From repository root, summarize existing records without training:

```powershell
python -B scripts/evaluate.py --registry experiments/registry.csv --stage historical_readme
```

All counts above are recovered registry entries. Original metrics, hashes, failures and source provenance remain at their canonical paths. See [recovery audit](../../../docs/EXPERIMENT_RECOVERY.md) and [historical failures](../../HISTORICAL_FAILURES.md).
