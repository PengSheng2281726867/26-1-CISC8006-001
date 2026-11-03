# Hop 范围与贡献诊断

研究允许哪些 Hop 参与融合，以及删除 Hop 的影响。Fixed-K 使用 K5 并区分重新训练与推理掩码；LOHO 使用已有 K4 检查点，两者是相关但独立的实验。

| 实验目录 | 研究问题 | 已有证据 |
| --- | --- | --- |
| [hop_scope_study](hop_scope_study/README.md) | 固定传播到 5-hop，只改变门控范围 | Complete: 300 trainings + 300 inference-only masks |
| [loho_diagnostic](loho_diagnostic/README.md) | Hop 权重是否对应删除该 Hop 的损失变化 | Complete: 180 checkpoints, validation + test; no new training |

各子目录保存其代码、配置、报告与结果，或指向共享历史证据的文件归属表。分组表示研究主题；成对比较仍遵循各实验自己的协议。

[全部实验](../README.md) · [项目首页](../../README.md)
