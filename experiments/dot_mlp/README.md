# Dot vs MLP routing scorer

MLP scorer 是否优于 Dot agreement。

**Recovered: 480 main + 24 superseded Pilot + 2 anchors**. Teacher approval: **NOT_VERIFIED**.

The main comparison has 480 Dot/MLP executions across six graphs, K1–4 and ten splits. The 24 superseded Pilot entries and two anchors are retained as separate registry stages, not extra main cells. Execution commits remain UNKNOWN / pre-git experiment. Proposed three-seed configs are future work, not evidence that those matrices ran.

## File map / 文件归属

[All experiments / 全部实验](../README.md) · [Repository home](../../README.md)

| Purpose | Canonical files |
| --- | --- |
| Code | [`research/src`](../../research/src)<br>[`course`](../../course) |
| Historical protocol and configs | [`experiments/protocols/dot_mlp.json`](../protocols/dot_mlp.json)<br>[`configs/historical_main.json`](../../configs/historical_main.json)<br>[`configs/historical_pilot.json`](../../configs/historical_pilot.json) |
| Prospective configs | [`configs/baseline_texas.json`](../../configs/baseline_texas.json)<br>[`configs/mlp_texas.json`](../../configs/mlp_texas.json)<br>[`configs/paired_texas_three_seeds.json`](../../configs/paired_texas_three_seeds.json)<br>[`configs/future_three_seeds.json`](../../configs/future_three_seeds.json) |
| Results | [`experiments/analysis/dot_mlp.json`](../analysis/dot_mlp.json)<br>[`reports/RESULTS_SUMMARY.md`](../../reports/RESULTS_SUMMARY.md) |
| Figures | [`reports/figures/accuracy_overview.png`](../../reports/figures/accuracy_overview.png)<br>[`reports/figures/delta_accuracy.png`](../../reports/figures/delta_accuracy.png) |
| Verification | [`experiments/verification/dot_mlp.json`](../verification/dot_mlp.json)<br>[`experiments/verification/historical_mlp_tests.json`](../verification/historical_mlp_tests.json) |

## Registry and evaluation

Records stay in the shared [registry](../registry.csv) and [run evidence](../recovered_runs.jsonl). Select the following exact `stage` values:

| Registry stage | Recovered entries |
| --- | ---: |
| `dot_mlp` | 480 |
| `v1_pilot` | 24 |
| `anchor` | 2 |

From repository root, summarize existing records without training:

```powershell
python -B scripts/evaluate.py --registry experiments/registry.csv --stage dot_mlp
```

All counts above are recovered registry entries. Original metrics, hashes, failures and source provenance remain at their canonical paths. See [recovery audit](../../docs/EXPERIMENT_RECOVERY.md) and [historical failures](../HISTORICAL_FAILURES.md).
