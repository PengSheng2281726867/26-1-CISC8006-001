# MLP normalization and activation ablations

分别加入 LayerNorm、替换 GELU 的影响。

**Recovered: 480 new LN/GELU executions**. Teacher approval: **NOT_VERIFIED**.

There are 240 LN-only and 240 GELU-only executions. MLP/Dot controls are reused from the Dot/MLP study and must not be counted as new executions here. No combined LN+GELU experiment was executed. Historical execution commits remain UNKNOWN / pre-git experiment. The prospective three-seed component Pilot remains unlaunched.

## File map / 文件归属

[All experiments / 全部实验](../README.md) · [Repository home](../../README.md)

| Purpose | Canonical files |
| --- | --- |
| Code | [`research/ablation_mlp`](../../research/ablation_mlp)<br>[`research/src`](../../research/src)<br>[`course`](../../course) |
| Protocol | [`experiments/protocols/components.json`](../protocols/components.json) |
| Prospective config | [`configs/future_component_pilot.json`](../../configs/future_component_pilot.json) |
| Results | [`experiments/analysis/mlp_components.json`](../analysis/mlp_components.json)<br>[`reports/RESULTS_SUMMARY.md`](../../reports/RESULTS_SUMMARY.md) |
| Figures | [`reports/figures/components_accuracy_overview.png`](../../reports/figures/components_accuracy_overview.png)<br>[`reports/figures/components_delta_accuracy.png`](../../reports/figures/components_delta_accuracy.png)<br>[`reports/figures/components_hop_weights.png`](../../reports/figures/components_hop_weights.png)<br>[`reports/figures/components_inference_time.png`](../../reports/figures/components_inference_time.png) |
| Verification | [`experiments/verification/components_delivery.json`](../verification/components_delivery.json)<br>[`experiments/verification/historical_component_tests.json`](../verification/historical_component_tests.json) |

## Registry and evaluation

Records stay in the shared [registry](../registry.csv) and [run evidence](../recovered_runs.jsonl). Select the following exact `stage` values:

| Registry stage | Recovered entries |
| --- | ---: |
| `components` | 480 |

From repository root, summarize existing records without training:

```powershell
python -B scripts/evaluate.py --registry experiments/registry.csv --stage components
```

All counts above are recovered registry entries. Original metrics, hashes, failures and source provenance remain at their canonical paths. See [recovery audit](../../docs/EXPERIMENT_RECOVERY.md) and [historical failures](../HISTORICAL_FAILURES.md).
