# 课程实验索引：Baseline + 三个实验

[完整 Story line](../STORYLINE.md) · [项目首页](../README.md) · [三个想法与评分要求](../docs/IMPROVEMENTS.md)

[架构图总览](ARCHITECTURE.md) 收录原始 GAMMA、Baseline 门控对照和三个主实验的配图。

[课程 PPT 制作指南](../docs/PRESENTATION_GUIDE.md) 将实验图、数据和讲稿按汇报顺序对应到每一页。

| 顺序 | 问题 | 主要证据 |
| --- | --- | --- |
| [00_baseline](00_baseline/README.md) | GAMMA 准确率与门控收益复现到什么程度？ | 历史 README + 后期 Dot/Uniform 主对照 |
| [01_scorer](01_scorer/README.md) | 学习更复杂的 agreement 是否有效？ | Dot/MLP、LN/GELU |
| [02_hop_scope](02_hop_scope/README.md) | 限制可参与路由的范围是否有效？ | 固定 K5、x1–5 重训与推理掩码 |
| [03_distance_query](03_distance_query/README.md) | 改变候选表示和 Query 是否有效？ | G0–G3、三 seeds、完整控制 |

三个实验对应三个具体想法，不把每个消融变体重复算作独立课程实验。
各主实验目录 README 写明想法、假设、基线、结果、限制和叙事连接。
[补充 LOHO](supplementary/README.md) 独立保留，不进入主线。

## 运行与溯源

[安装与运行指南](../docs/REPRODUCIBILITY.md)。稳定的 Python 模块名继续可用：

```powershell
python -B scripts/smoke_test.py
python -B -m experiments.exact_distance_query.src.run full --plan
```

旧运行中的路径、哈希和执行 commit 不改写；使用 [本次路径映射](storyline_migration.json)
与 [前次路径映射](layout_migration.json) 追溯。目录变化会改变当前源码指纹，不能自动复用旧私有运行。
共享 registry 的 1,566 行只覆盖历史恢复批次；新实验使用各自运行清单。训练、Pilot 复用、推理评估分别计数。
教师批准仍为 `NOT_VERIFIED`。

## 共享文件 / Shared files

| 用途 | 入口 |
| --- | --- |
| Frozen implementations and attribution | [`research/src`](../research/src)<br>[`research/ablation_mlp`](../research/ablation_mlp)<br>[`research/upstream_snapshot`](../research/upstream_snapshot)<br>[`NOTICE.md`](../NOTICE.md)<br>[`LICENSE`](../LICENSE) |
| Shared adapters and entry points | [`course`](../course)<br>[`scripts`](../scripts)<br>[`tests`](../tests)<br>[`environment`](../environment) |
| Historical run and artifact evidence | [`experiments/registry.csv`](registry.csv)<br>[`experiments/recovered_runs.jsonl`](recovered_runs.jsonl)<br>[`experiments/artifacts_manifest.jsonl`](artifacts_manifest.jsonl)<br>[`experiments/recovery_manifest.json`](recovery_manifest.json)<br>[`experiments/source_mapping.json`](source_mapping.json)<br>[`experiments/data_manifest.json`](data_manifest.json)<br>[`experiments/paper_reference_values.json`](paper_reference_values.json)<br>[`experiments/sample_logs`](sample_logs) |
| Course audits and historical report | [`docs`](../docs)<br>[`reports`](../reports)<br>[`archives`](../archives)<br>[`AI_USAGE.md`](../AI_USAGE.md)<br>[`CONTRIBUTIONS.md`](../CONTRIBUTIONS.md) |

[Repository home / 返回项目首页](../README.md) · [目录迁移说明](../docs/EXPERIMENT_DIRECTORY_MIGRATION.md)
