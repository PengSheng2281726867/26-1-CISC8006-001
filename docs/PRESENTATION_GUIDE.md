# GAMMA 课程汇报 PPT 制作指南

组员可以从本页开始。建议做 **12 页正文**，再按课堂要求添加演示与答辩备用页。每个实验用两页，一页解释想法和公平对照，一页呈现前后结果。时间较紧时，可以把同一实验的两页合为一页。汇报时长和提交格式以 UMMoodle 的最终公告为准。

项目检验的问题是 **在异配图节点分类中，为每个节点动态分配多跳融合权重，能否比均匀融合做得更好？** 我们用 Dot 与 Uniform 做组件级复现，再从打分函数、候选范围、候选构造与 Query 三个角度检查结果为何会因设置而变化。先读[项目 Story line](../STORYLINE.md)，再用[架构图总览](../experiments/ARCHITECTURE.md)下载对应的 PNG。

## 逐页提纲

| 页 | 可用标题 | 上台讲什么 | 放什么与去哪取 |
| --- | --- | --- | --- |
| 1 | GAMMA on heterophilic graphs | 交代论文、课程项目和一句话问题。组员名称按实际贡献填写。 | [论文 PDF](https://amir-ghz.github.io/PDFs/GAMMA.pdf)、[项目首页](../README.md)、[贡献记录](../CONTRIBUTIONS.md)。 |
| 2 | 动态门控能否改善节点分类？ | 说明异配图相邻节点可能不同类。论文 Table 3 在六个异配数据集上比较动态门控与均匀 hop 权重，报告的组合方向全部为正。我们的复现范围是 **Component**，聚焦这项对照。 | [主张与论文对照](CLAIM_AND_REPRODUCTION.md)。论文 **第 16 页 Table 3** 对应门控贡献，**第 8 页 Table 1** 提供完整模型准确率背景。 |
| 3 | GAMMA 怎样融合多跳表示？ | 看上方主流程讲 `H0` 自身特征、`H1…HK` 传播候选、共享投影和逐 hop 缩放。再指着下方循环讲权重、加权摘要、Dot agreement 和下一轮 logits。 | [原始 GAMMA 架构图 PNG](../experiments/00_baseline/figures/gamma-architecture.png)、[模型代码](../research/src/model.py)。 |
| 4 | Baseline 控制了什么？ | 两组都保留候选与全局缩放。Dot 使用节点特定权重，Uniform 使用等权。介绍本地六数据集、K2–4、十个划分、每固定划分一个训练 seed 和验证集选模。 | [Dot vs Uniform 架构图 PNG](../experiments/00_baseline/figures/dot-vs-uniform.png)、[Baseline 实验说明](../experiments/00_baseline/README.md)、[历史配置](../experiments/historical_configs.json)。 |
| 5 | 整体准确率接近，门控增益随图变化 | 先交代历史 README 运行相对论文 Table 1 的平均绝对差约 **1.81 pp**。再用匹配的本地 Dot/Uniform 数据讲 **11/18 正向、7/18 负向、平均 +1.51 pp**，Holm 校正后 0/18 达到显著阈值。 | [论文与本地并列表](CLAIM_AND_REPRODUCTION.md#paper-versus-local-result)、[K2–4 逐条件结果](../experiments/analysis/gate_sweep.json)、[完整方法准确率表](../reports/RESULTS_SUMMARY.md#complete-comparable-main-table)。 |
| 6 | 实验 1 · 学一个更灵活的 scorer | 在相同的候选和路由流程中，把 Dot 换为接收 hop 表示和当前摘要的共享 MLP。随后分别加入 LN 或替换为 GELU。指着图说明四行各自对应一次配置。 | [Scorer 架构图 PNG](../experiments/01_scorer/figures/routing-scorer.png)、[实验设计](../experiments/01_scorer/README.md)、[Dot/MLP 协议](../experiments/protocols/dot_mlp.json)、[组件消融协议](../experiments/protocols/components.json)。 |
| 7 | 更复杂的打分没有带来稳定提升 | 汇报三个配对差值 **MLP−Dot −0.51 pp、LN−MLP +0.02 pp、GELU−MLP +0.47 pp**。标清比较对象，说明直接比较经校正均无显著收益。MLP 多了 2,113 个参数，因此容量也是解释限制。 | [方法均值与完整对比](../reports/RESULTS_SUMMARY.md)、[Dot/MLP 分析数据](../experiments/analysis/dot_mlp.json)、[LN/GELU 配对数据](../experiments/analysis/mlp_components.json)、[组件差值图 PNG](../reports/figures/components_delta_accuracy.png)。 |
| 8 | 实验 2 · 固定传播，改变路由范围 | 所有组都计算 `H0…H5`。图里的 `x=5` 允许全部参与，`x=2` 只允许 `H0…H2`。说明掩码在 softmax 前生效，`x=1…5` 分别训练。本组的完整范围模型是对照。 | [Hop 范围架构图 PNG](../experiments/02_hop_scope/figures/fixed-propagation-routing-scope.png)、[实验设计](../experiments/02_hop_scope/README.md)、[协议](../experiments/02_hop_scope/hop_scope_study/docs/00_AUDIT_AND_PROTOCOL.md)、[Full 配置](../experiments/02_hop_scope/hop_scope_study/configs/full.json)。 |
| 9 | 更多候选未带来单调收益 | 放重训曲线，说明六个数据集的均值曲线都非单调，24 个 `x` 对 `x5` 的比较经各数据集内 Holm 校正后均未达显著阈值。备用例子用 Squirrel 的 `x=1`，从头限制范围重训 **34.60%**，训练后临时遮罩 **30.12%**。 | [重训准确率曲线 PNG](../experiments/02_hop_scope/hop_scope_study/figures/accuracy_vs_x.png)、[完整结果](../experiments/02_hop_scope/hop_scope_study/docs/03_RESULTS.md)、[准确率 CSV](../experiments/02_hop_scope/hop_scope_study/results/accuracy_summary.csv)、[配对差值 CSV](../experiments/02_hop_scope/hop_scope_study/results/paired_delta.csv)、[重训与临时遮罩图 PNG](../experiments/02_hop_scope/hop_scope_study/figures/posthoc_vs_retrain.png)。 |
| 10 | 实验 3 · 候选的定义和 Query 都会影响路由 | 先讲 Walk 可以重复经过节点，Exact 只收集最短距离恰好为该 hop 的节点。用图指明 `G1−G0` 对比聚合方案，`G2−G1` 与 `G3−G1` 检查 Exact 候选下更换 Query。G3 用 Walk H4 打分，融合仍使用 Exact 候选。 | [G0–G3 架构图 PNG](../experiments/03_distance_query/figures/exact-distance-query.png)、[四组设计](../experiments/03_distance_query/README.md)、[实现流程](../experiments/03_distance_query/exact_distance_query/docs/ARCHITECTURE.md)、[协议](../experiments/03_distance_query/exact_distance_query/PROTOCOL.md)、[Full 配置](../experiments/03_distance_query/exact_distance_query/configs/full.json)。 |
| 11 | Exact 没有普遍收益，H0 Query 常集中于自身 | 交代 **6 数据集 × 10 划分 × 3 seeds × 4 组 = 720 个主训练单元**，已计入复用的 Pilot 和 Smoke。展示全六图的三项配对差值。可标注 Actor `G2−G1` 为 **+1.24 pp**，Texas `G3−G1` 为 **−4.21 pp**。G2 的平均权重约 **98.5%–100%** 落在 0-hop。 | [完整准确率和差值表](../experiments/03_distance_query/exact_distance_query/docs/03_FULL_RESULTS.md)、[配对差值图 PNG](../experiments/03_distance_query/exact_distance_query/results/full/paired_deltas.png)、[准确率 CSV](../experiments/03_distance_query/exact_distance_query/results/full/accuracy.csv)、[配对汇总 CSV](../experiments/03_distance_query/exact_distance_query/results/full/paired_summary.csv)、[逐 seed 配对 CSV](../experiments/03_distance_query/exact_distance_query/results/full/paired_cells.csv)、[Query 权重解释](../experiments/03_distance_query/exact_distance_query/docs/04_INTERPRETATION.md)。 |
| 12 | 门控收益取决于候选与评估设置 | 回到开场主张。整体准确率近似重现，动态门控只有局部正向证据，本地协议未重现一致增益。用一句话概括三个实验各自提供的证据。把实验 3 作为完整评估重点，并说明主要局限。 | [综合论证](../STORYLINE.md)、[改进想法与课程要求](IMPROVEMENTS.md)、[课程证据和待确认事项](COURSE_COMPLIANCE.md)。 |

## 组员可以直接使用的讲稿逻辑

**从主张讲到 Baseline。**「论文希望每个节点能自己决定各 hop 的权重。我们把融合权重改成均匀，同时保留相同候选和全局缩放，看看动态权重实际带来了多少收益。」讲 Baseline 结果时，可以从论文表与本地表各取同一个数据集的对应行。Texas 的门控差值接近论文，Chameleon 的差值方向相反。介绍共用设置后，再说明论文和本地的划分、层数、hop 标签和训练协议差异。 [对照表与协议差异](CLAIM_AND_REPRODUCTION.md)

**从 Scorer 讲到 Hop 范围。**「更复杂的打分没有稳定改善结果。我们接着问，即便保持 Dot 打分，开放给它的候选范围会不会影响结果？」讲清楚 `x` 是路由允许的最大 hop。传播范围始终是 0 至 5。用一条重训曲线展示范围的影响，用一张备用图解释训练后临时遮罩。 [Scorer 汇总](../reports/RESULTS_SUMMARY.md) · [Hop 范围解释](../experiments/02_hop_scope/hop_scope_study/docs/04_INTERPRETATION_AND_LIMITATIONS.md)

**从 Hop 范围讲到 Exact-distance。**「范围决定哪些候选能参加。接下来我们检查候选由 Walk 还是严格最短距离构造，以及拿哪个向量给这些候选打分。」用双向链 `A ↔ B ↔ C` 解释两步 Walk 可以从 A 经 B 返回 A，而距离恰好为二的候选只包含 C。讲 G2 时，先报准确率，再解释为什么很高的 0-hop 权重提示模型主要依赖自身信息。 [架构图与 G0–G3](../experiments/03_distance_query/README.md)

## 把文件放进 PPT 的步骤

1. **先确定每页的结论。** 照上表建页，再把对应架构图 PNG 插入方法页。打开 GitHub 上的 PNG 原文件并下载，投影时保留足够的字号和清晰度。
2. **为结果页选一个主证据。** Baseline 用论文与本地的同数据集并列表。Scorer 用三项配对差值。Hop 范围用重训曲线。Exact-distance 用 G0–G3 的三项配对差值图或表。每张主图旁写明对照组、数据范围和一句结论。
3. **保留可追溯来源。** 在页脚或讲者备注贴上该页的 GitHub 源链接。绝对准确率写 `%`，两组准确率之差写 `pp`。从 CSV 重绘时注意单位，以原报告的汇总方式为准。对实验 3，先按固定 split 平均三个 seeds，再汇总 splits。报告里的 `±` 是样本标准差，和置信区间分别标注。
4. **让另一位组员做证据核对。** 对照每页数字和原表，检查差值方向、seed 与复用计数是否正确，确认每个成员都能解释自己负责的对照。最后确认演示方式、组员分工和课程提交要求。 [贡献记录](../CONTRIBUTIONS.md) · [课程证据](COURSE_COMPLIANCE.md)

## 可以用于演示和答辩的备用材料

| 备份页 | 建议内容 | 应用文件 |
| --- | --- | --- |
| 实验能否跑通 | 在已准备的兼容环境里运行 `python -B scripts/smoke_test.py`。再打开一份已保存的结果表讲解如何读数据。 | [一键检查命令](REPRODUCIBILITY.md#one-command-checks-no-dataset-download-no-full-training)、[测试记录](../reports/SYSTEM_TESTS.md)、[数据来源和校验](../experiments/data_manifest.json)。 |
| 如何查到一次运行 | 早期实验从历史 registry 找数据集、split、方法、配置和运行记录。Hop 从 run matrix 查 run ID。Exact-distance 从逐次结果表和 manifest 对照参数、种子、时间和校验和。 | [历史 registry](../experiments/registry.csv)、[Hop run matrix](../experiments/02_hop_scope/hop_scope_study/results/run_matrix.csv)、[Exact 逐次结果](../experiments/03_distance_query/exact_distance_query/results/full/cells.csv)、[Exact 运行清单](../experiments/03_distance_query/exact_distance_query/results/full/run_manifest.json)。 |
| 为什么保留负结果 | 用 Wisconsin 或 Chameleon 的 Baseline 反向结果，以及 Texas 的 G3 退化说明边界。保留校正结果和失败记录。 | [Baseline 论文对比](CLAIM_AND_REPRODUCTION.md#paper-versus-local-result)、[Exact 负结果分析](../experiments/03_distance_query/exact_distance_query/docs/04_INTERPRETATION.md)、[历史失败记录](../experiments/HISTORICAL_FAILURES.md)。 |
| 如何解释局限 | Baseline 与实验 1/2 各自的固定 split 只有一个训练 seed，早期部分 Git 执行版本未知。实验 3 的三种子只覆盖该实验。Hop 范围消融的传播量恒定。Query 对照还有尺度差异，原实验缺少同协议的 H0-only。 | [研究边界](../STORYLINE.md)、[实验 2 限制](../experiments/02_hop_scope/hop_scope_study/docs/04_INTERPRETATION_AND_LIMITATIONS.md)、[实验 3 限制](../experiments/03_distance_query/exact_distance_query/docs/04_INTERPRETATION.md)。 |
| 谁做了什么 | 按实际工作、对应证据和确认情况填写。课堂指南要求三个改进想法、至少两个获批 Pilot、至少一个完整评估。审批以真实记录为准。 | [AI 使用记录](../AI_USAGE.md)、[个人贡献](../CONTRIBUTIONS.md)、[课程要求对应](COURSE_COMPLIANCE.md)。 |

正文使用仓库已经发布的 Baseline 和三个主实验。LOHO 可在答辩被问到时从[补充证据](../experiments/supplementary/README.md)取图。报告若必须给门控总体收益一个课程判定标签，建议使用 **inconclusive** 并说明局部正向证据，最终以团队确认的判定规则和教师要求为准。
