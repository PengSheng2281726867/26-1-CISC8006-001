# 实验索引 / Experiment index

按研究问题选择实验，再进入其目录查看代码、配置、报告、结果、图表和测试。
[机器可读文件归属](catalog.json)使用仓库根目录相对路径；目录链接在 GitHub 与本地克隆中均可浏览。

## 历史复现与消融 / Recovered experiments

这些是 `pre-git experiment`，执行 commit 为 UNKNOWN；不要将导入提交当作实验执行版本。

| 实验目录 | 研究问题 | 已有证据 |
| --- | --- | --- |
| [historical_readme](historical_readme/README.md) | 最初 README 基线复现 | Recovered: 100 executions |
| [early_gate](early_gate/README.md) | 早期 K2 门控与均匀融合对照 | Recovered: 120 executions |
| [gate_sweep](gate_sweep/README.md) | K2–4 的 Dot / Uniform 对照 | Recovered: 360 executions |
| [dot_mlp](dot_mlp/README.md) | MLP scorer 是否优于 Dot agreement | Recovered: 480 main + 24 superseded Pilot + 2 anchors |
| [mlp_components](mlp_components/README.md) | 分别加入 LayerNorm、替换 GELU 的影响 | Recovered: 480 new LN/GELU executions |

## 新实验 / Dedicated studies

| 实验目录 | 研究问题 | 已完成范围 |
| --- | --- | --- |
| [hop_scope_study](hop_scope_study/README.md) | 固定传播到 5-hop，只改变门控范围 | Complete: 300 trainings + 300 inference-only masks |
| [loho_diagnostic](loho_diagnostic/README.md) | Hop 权重是否对应删除该 Hop 的损失变化 | Complete: 180 checkpoints, validation + test; no new training |
| [exact_distance_query](exact_distance_query/README.md) | 严格距离聚合与固定 H0 / Walk H4 Query | Complete: 720 primary trainings + 9 controls + 720 inference profiles |

## 文件组织规则 / File organization

- 每项实验目录的 `README.md` 是入口，`File map / 文件归属`列出其代码、配置、协议、结果、图表与测试。
- 新实验各自使用 `src/`、`configs/`、`results/`、`tests/`，报告位于 `docs/` 或 `reports/`；图表沿用各实验的实际存放位置。
- 历史实验目录提供归属索引，原文件保留在 `analysis/`、`protocols/`、根 `configs/`、`reports/` 等规范路径。共享源码与证据只维护一份，保证旧脚本、源码哈希和历史记录仍然有效。
- `registry.csv` 的 1,566 条记录属于历史恢复批次，不包含后来三个新实验；新实验使用各自的覆盖文件和运行清单。Pilot 复用、共享对照、推理评估与独立训练不能相加当作新模型数量。
- `configs/future*.json` 等是待执行方案，不能当作已完成结果；各实验的教师批准仍为 `NOT_VERIFIED`。
- 私有数据、模型权重和逐节点产物存放在 Git 仓库之外；公开目录保存代码与汇总证据。

## 共享文件 / Shared files

| 用途 | 入口 |
| --- | --- |
| Frozen implementations and attribution | [`research/src`](../research/src)<br>[`research/ablation_mlp`](../research/ablation_mlp)<br>[`research/upstream_snapshot`](../research/upstream_snapshot)<br>[`NOTICE.md`](../NOTICE.md)<br>[`LICENSE`](../LICENSE) |
| Shared adapters and entry points | [`course`](../course)<br>[`scripts`](../scripts)<br>[`tests`](../tests)<br>[`environment`](../environment) |
| Historical run and artifact evidence | [`experiments/registry.csv`](registry.csv)<br>[`experiments/recovered_runs.jsonl`](recovered_runs.jsonl)<br>[`experiments/artifacts_manifest.jsonl`](artifacts_manifest.jsonl)<br>[`experiments/recovery_manifest.json`](recovery_manifest.json)<br>[`experiments/source_mapping.json`](source_mapping.json)<br>[`experiments/data_manifest.json`](data_manifest.json)<br>[`experiments/paper_reference_values.json`](paper_reference_values.json)<br>[`experiments/sample_logs`](sample_logs) |
| Course audits and historical report | [`docs`](../docs)<br>[`reports`](../reports)<br>[`archives`](../archives)<br>[`AI_USAGE.md`](../AI_USAGE.md)<br>[`CONTRIBUTIONS.md`](../CONTRIBUTIONS.md) |

[Repository home / 返回项目首页](../README.md) · [本次整合与验证](../docs/REPOSITORY_ORGANIZATION.md)
