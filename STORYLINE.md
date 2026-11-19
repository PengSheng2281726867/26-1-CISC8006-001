# Story line：GAMMA 的门控收益在什么条件下成立？

本页是课程叙事与综合结果草案，不是已冻结的最终课程报告。
2026-11-19 按用户确定的范围，将 Baseline、Scorer、Hop 范围、Exact-distance / Query 作为主线。
这是对已完成工作的组织方式，不暗示所有问题都在观察结果前提出；预注册状态以各原协议为准。
LOHO 不参与这条论证。

## 研究范围与起点

论文研究异配图中逐 hop 的全局模式和逐节点的局部模式，使用共享变换、channel scaling 与动态门控融合多跳信息。
课程范围只取六个异配图，Component reproduction；同配数据集为背景。审批状态仍 NOT_VERIFIED。

我们区分三个层次：整体准确率接近论文、门控相对 Uniform 有收益、门控能解释性地识别任务相关 hop。
前一个层次不会自动证明后两个。本项目主线直接检验前两层，后续实验研究 scorer、候选范围和 query 的条件效应。

## Baseline：先回答复现到什么程度

| 数据集 | 论文 Table 1 | 历史 README 复现 | 本地 K2 Dot 主对照 | 本地 K2 Uniform |
| --- | --- | --- | --- | --- |
| Texas | 87.37 | 83.16 | 82.89 | 78.95 |
| Wisconsin | 86.27 | 85.49 | 84.51 | 85.49 |
| Cornell | 78.68 | 77.63 | 75.79 | 71.58 |
| Chameleon | 51.16 | 48.27 | 48.38 | 49.06 |
| Squirrel | 36.20 | 34.59 | 33.85 | 32.91 |
| Actor | 35.59 | 35.27 | 35.47 | 35.18 |

单位为 accuracy %，高为好；仅并列描述，不作跨协议配对统计。
历史 README 六图平均绝对差距约 1.81 pp，但含浅拷贝 checkpoint 等限制，仅作背景。
后期 K2–4 Dot−Uniform 对照共有 11/18 正向、7/18 负向，平均 +1.51 pp；Holm18 后无显著比较。
准确率水平大体接近，但论文 Table 3 的一致门控增益没有在本地设置重现。

论文文字的两层 GNN、50/25/25、固定 500 epochs 和网格搜索，与本地实际一层 GAMMA 加分类头、
60/20/20、早停、固定超参数并不一致。0-hop、归一化、边数也需说明。不能因此直接反驳论文原协议。
对总体门控收益，当前解释为 inconclusive / 局部正向支持；对一致收益，表述为本地未复现。
不是历史预注册判定，也不是“p>.05 证明门控无效”。

证据：[主张与差异](docs/CLAIM_AND_REPRODUCTION.md)、[README 历史数值](experiments/analysis/readme.json)、
[完整门控对照](experiments/analysis/gate_sweep.json)、[结果与不确定性](reports/RESULTS_SUMMARY.md)。

## 想法 1 → 实验 1：提高 agreement 的表达能力

**问题：收益不稳是否因为 Dot scorer 太简单？** 共享 MLP 替代 Dot，再做单因素 LN/GELU 消融。
配对 splits、共享初始参数、训练预算和验证集选模保持一致，MLP 增参限制单独披露。

MLP−Dot 平均 −0.51 pp；LN−MLP +0.02 pp；GELU−MLP +0.47 pp；GELU 整体仍比 Dot 低约 0.04 pp。
没有校正后显著的 fixed-K 直接收益。更复杂的 scorer 在已测范围没有稳定改善，不能推出 Dot 最优。

**连接到下一问：** 不只 scorer 形式，候选 hop 的集合也可能影响路由。
[实验 1 的想法、Pilot、Full、控制和证据](experiments/01_scorer/README.md)。

## 想法 2 → 实验 2：限制允许参与路由的 Hop 范围

**问题：完整候选集合是否总是最好？** 固定传播到 5-hop，仅改变可路由的 0..x，x1–5。
300 次重训与 300 次从 x5 checkpoint 出发的推理掩码分别报告；相同参数与完整传播。

六图均值曲线均非单调，不同图的验证集偏好范围不同；24 个主比较经各图 Holm4 后无显著差异。
Squirrel x1 的 post-hoc−retrain 为 −4.48 pp，提示“推理时删掉”与“训练时就限制”不等价。
这是固定范围探索，没有实现自适应 selector，也没有减少传播计算。

**连接到下一问：** 改变范围仍沿用 Walk 候选；候选表示和 Query 定义本身是否值得改变？
[实验 2 的协议、全结果和限制](experiments/02_hop_scope/README.md)。

## 想法 3 → 实验 3：改变候选表示与 Query

**问题：Exact-distance 和固定 Query 是否改善融合？** 四组为 G0 Walk+Consensus、
G1 Exact+Consensus、G2 Exact+H0、G3 Exact+原 Walk-H4。
同初始化、参数、预算和选模；720 个主训练 cells，三训练 seeds/固定 split，含48 Pilot/4 Smoke 复用。
另有9个 empty-policy 控制和720次 checkpoint 推理 profiling。

| 数据集 | G1−G0 | G2−G1 | G3−G1 |
| --- | --- | --- | --- |
| Texas | +0.35 | +1.23 | −4.21 |
| Wisconsin | −1.63 | +2.29 | −3.53 |
| Cornell | +3.07 | +2.02 | −1.58 |
| Chameleon | +0.40 | −0.72 | −0.93 |
| Squirrel | −0.11 | −0.84 | +1.09 |
| Actor | −0.03 | +1.24 | −0.26 |

单位为 pp；先每 split 平均三个 seeds，再等权汇总 splits。完整 SD、CI、名义 p 值在原报告。
G1−G0 没有比较通过各图 Holm3；Actor 的 G2−G1 正向、Texas/Chameleon 的 G3−G1 负向通过该家族阈值。
splits 来自同图且重叠，统计结论仅作描述性证据。

G2 平均 98.5%–100% 的 alpha 集中于0-hop；其部分收益与自身特征依赖相容，尚不能证明更好的远邻选择。
缺 H0-only 对照，Query 范数也不同；不能隔离 query 信息与尺度。
G1 同时改变路径计数、距离混合、shell/empty 策略及计算方式；不能把变化全部归因于去除冗余。
推理时间下降包含共享计算与算子实现影响，一次性距离构建/存储成本单列。
[实验 3 全部证据与负结果](experiments/03_distance_query/README.md)。

## 可以成立的综合结论

GAMMA 在异配图上的准确率可大体重现，门控相对 Uniform 的收益则依赖数据集与本地协议。
已测更复杂的 scorer 没有稳定改善；候选范围、训练方式、表示与 Query 的选择都会影响结果。
三项研究提供的是有控制、有局限的改进尝试，不声称普遍胜出或已证明因果机制。

若未来继续研究，H0-only 与统一 Query 尺度控制可区分自身特征依赖与路由收益；
优化 Walk 计算对照可区分语义与实现速度。它们仅为后续建议，未执行、不补写成已完成实验。

## 课程要求的落点

三个想法对应三个主实验；至少两个 Pilot 与一个 Full 已有技术材料，但教师批准没有验证。
原始复现和实验1/2的历史 seed/commit 限制，不因实验3完成三 seeds 自动消失。
最终报告与 slides 应沿本页组织，并保留所有比较方向、失败、不确定性和真实阶段顺序。
[当前课程缺口](docs/COURSE_COMPLIANCE.md) · [三个想法的对应表](docs/IMPROVEMENTS.md)。
