# 三个改进想法与实验对应

本页是 2026-11-19 的课程组织方案，不能替代各实验原始冻结协议，也不重写发现时间。
[完整 Story line](../STORYLINE.md)。

| 想法 | 动机与假设 | Pilot / Full 技术证据 | 主对照与限制 |
| --- | --- | --- | --- |
| [1：可学习 scorer](../experiments/01_scorer/README.md) | Dot 表达能力可能不足；用共享 MLP，再做 LN/GELU 单因素消融 | Dot/MLP Pilot24 计入 Full480；LN/GELU Pilot24 计入两变体 Full480 | 本组匹配 Dot/MLP；历史单 seed/split、增参和 commit UNKNOWN |
| [2：限制 Hop 路由范围](../experiments/02_hop_scope/README.md) | 完整范围不一定最优；固定传播后比较 0..x | Pilot12 计入 Full300；额外300次推理掩码 | 本组新训练 x5；不是自适应 selector，未减少传播，单 seed/split |
| [3：Exact-distance / Query](../experiments/03_distance_query/README.md) | Walk 混合与参考向量可能影响融合；比较 G0–G3 | Pilot48 和 Smoke4 计入 Full720；9个额外控制，720次 profiling | 本组 G0/G1；三 seeds/split，query尺度与多因素变化限制归因 |

教师指南要求至少三个想法、至少两个**获批** Pilot、至少一个完整评估；不是规定必须做三个 Full。
本仓库采用 Baseline + 三个实验来承载这些要求。技术完成不等于教师批准；所有批准仍 `NOT_VERIFIED`。
实验2是范围消融与改进探索，是否作为课程改进想法接受需真实教师确认，不能写成已实现自动选择器。

共享 controls 和 Pilot 复用不重复计数。改进不必胜出；没有普遍收益的结果也应完整报告。
各实验都使用自身协议的匹配 baseline，不能把历史 Uniform、K5 x5 与 K4 G0 当成同一个冻结模型池。

[旧想法和后续建议记录](IMPROVEMENTS_HISTORY.md) 保留未执行 temperature/cosine 和 hop dropout 的真实 Proposed 状态，
不把它们算成本次三项已执行实验。LOHO 独立放入补充材料，不进入本页主线。
