# 实验索引 / Experiment index

项目按四条研究主线组织，八个实验目录实际位于对应组目录内。
[机器可读目录与文件归属](catalog.json)使用仓库根目录相对路径。

| 分组 | 内容 | 子实验 |
| --- | --- | --- |
| [01_reproduction](01_reproduction/README.md) | 原版复现与门控验证 | [historical_readme](01_reproduction/historical_readme/README.md) · [early_gate](01_reproduction/early_gate/README.md) · [gate_sweep](01_reproduction/gate_sweep/README.md) |
| [02_scorer_ablation](02_scorer_ablation/README.md) | 门控评分函数与组件消融 | [dot_mlp](02_scorer_ablation/dot_mlp/README.md) · [mlp_components](02_scorer_ablation/mlp_components/README.md) |
| [03_hop_diagnostics](03_hop_diagnostics/README.md) | Hop 范围与贡献诊断 | [hop_scope_study](03_hop_diagnostics/hop_scope_study/README.md) · [loho_diagnostic](03_hop_diagnostics/loho_diagnostic/README.md) |
| [04_distance_query](04_distance_query/README.md) | 严格距离聚合与 Query 对照 | [exact_distance_query](04_distance_query/exact_distance_query/README.md) |

## 使用方式

先进入组目录，再进入具体实验目录；各实验 README 列出代码、配置、协议、报告、结果、图表和测试。
共享科学实现、公共工具、环境以及历史 registry/analysis/protocol 文件继续共用，避免复制与改写证据。

编号目录用于浏览，Python 模块名保持稳定，例如：

```powershell
python -B -m experiments.exact_distance_query.src.run full --plan
python -B -m unittest discover -s experiments/03_hop_diagnostics/loho_diagnostic/tests -v
```

脚本和配置的文件路径采用新的分组路径。原 Python 模块入口由 `experiments/__init__.py` 的包搜索路径兼容，无需保留旧目录或复制源码。
旧运行记录中的路径、哈希、日期和指标保持原样；其历史位置可通过[迁移映射](layout_migration.json)和原 Git 提交追溯。
目录迁移和路径适配会改变当前源码指纹，旧私有运行不会被当作当前版本结果自动复用。教师批准状态仍为 `NOT_VERIFIED`。

`registry.csv` 的 1,566 条记录属于历史恢复批次。新实验使用各自覆盖文件和运行清单；Pilot 复用、共享对照、推理评估与独立训练需分别计数。
`configs/future*.json` 等仍是待执行方案；私有数据、权重与逐节点产物保存在仓库之外。

## 共享文件 / Shared files

| 用途 | 入口 |
| --- | --- |
| Frozen implementations and attribution | [`research/src`](../research/src)<br>[`research/ablation_mlp`](../research/ablation_mlp)<br>[`research/upstream_snapshot`](../research/upstream_snapshot)<br>[`NOTICE.md`](../NOTICE.md)<br>[`LICENSE`](../LICENSE) |
| Shared adapters and entry points | [`course`](../course)<br>[`scripts`](../scripts)<br>[`tests`](../tests)<br>[`environment`](../environment) |
| Historical run and artifact evidence | [`experiments/registry.csv`](registry.csv)<br>[`experiments/recovered_runs.jsonl`](recovered_runs.jsonl)<br>[`experiments/artifacts_manifest.jsonl`](artifacts_manifest.jsonl)<br>[`experiments/recovery_manifest.json`](recovery_manifest.json)<br>[`experiments/source_mapping.json`](source_mapping.json)<br>[`experiments/data_manifest.json`](data_manifest.json)<br>[`experiments/paper_reference_values.json`](paper_reference_values.json)<br>[`experiments/sample_logs`](sample_logs) |
| Course audits and historical report | [`docs`](../docs)<br>[`reports`](../reports)<br>[`archives`](../archives)<br>[`AI_USAGE.md`](../AI_USAGE.md)<br>[`CONTRIBUTIONS.md`](../CONTRIBUTIONS.md) |

[Repository home / 返回项目首页](../README.md) · [目录迁移说明](../docs/EXPERIMENT_DIRECTORY_MIGRATION.md)
