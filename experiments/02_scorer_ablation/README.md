# 门控评分函数与组件消融

先比较 Dot 与 MLP scorer，再分别分析 LayerNorm 和 GELU。组件实验复用原 MLP / Dot 对照，不能重复计数；没有执行 LN+GELU 组合。

| 实验目录 | 研究问题 | 已有证据 |
| --- | --- | --- |
| [dot_mlp](dot_mlp/README.md) | MLP scorer 是否优于 Dot agreement | Recovered: 480 main + 24 superseded Pilot + 2 anchors |
| [mlp_components](mlp_components/README.md) | 分别加入 LayerNorm、替换 GELU 的影响 | Recovered: 480 new LN/GELU executions |

各子目录保存其代码、配置、报告与结果，或指向共享历史证据的文件归属表。分组表示研究主题；成对比较仍遵循各实验自己的协议。

[全部实验](../README.md) · [项目首页](../../README.md)
