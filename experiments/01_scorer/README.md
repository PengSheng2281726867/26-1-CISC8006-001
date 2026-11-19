# 实验 1：评分函数与组件消融

[Baseline](../00_baseline/README.md) → 实验 1 → [实验 2](../02_hop_scope/README.md)

## 想法与假设

Dot agreement 只衡量固定形式的相似性。想法：以共享 MLP 学习 hop 表示与当前融合表示的兼容度，
再分别测试 LayerNorm 与 GELU；假设它能更好地选择与分类相关的信息。
这是已执行的改进尝试，不承诺优于 Dot。原始阶段与当前叙事的组织顺序分开记录。

## 对照和消融

| 比较 | 改变什么 | 保持什么 |
| --- | --- | --- |
| MLP vs Dot | agreement scorer | 同 splits、共享初始参数、训练路径、预算、验证集选模 |
| MLP+LN vs MLP | 增加隐藏 LayerNorm | 其余 MLP 设置 |
| MLP-GELU vs MLP | ReLU 换为 GELU | 不增加参数，其他设置相同 |

MLP 增加 2,113 参数，缺参数匹配对照，因此函数形式与容量影响未完全分离。
没有执行 LN+GELU 组合，不应把它写成第四个已完成方法。

## 已有实验与结果

| 证据 | 内容 |
| --- | --- |
| [Dot / MLP](dot_mlp/README.md) | 24 个 Pilot cells 计入 480 次 full 训练；6 数据集×4 K×2 方法×10 splits |
| [LN / GELU 消融](mlp_components/README.md) | 两个变体各 240 次 full 训练；共享 24-cell Pilot 计入 full，Dot/MLP 对照不重复计数 |

MLP−Dot 平均 −0.51 pp；LN−MLP +0.02 pp；GELU−MLP +0.47 pp，
GELU 整体仍比 Dot 低约 0.04 pp。原比较家族校正后均无显著的 fixed-K 直接收益。
这表明已测范围内增加 scorer 复杂性没有稳定收益，不能推出 Dot 全局最优。
MLP 时间和参数开销、负结果、单 split/seed 耦合和历史 commit 缺口均保留。
见 [全结果与图表](../../reports/RESULTS_SUMMARY.md)。

## 在 story line 中的作用

收益不稳定可能不只来自 scorer 能力。接下来考察：哪些 hop 被允许参与路由，是否影响结果？
[进入实验 2](../02_hop_scope/README.md)。教师批准与人工科学核验仍 `NOT_VERIFIED`。
