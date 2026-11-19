# CISC8006 Course Project — GAMMA

**主线：Baseline 复现对比 → 实验 1：Scorer → 实验 2：Hop 范围 → 实验 3：Exact-distance / Query。**

研究六个异配（heterophilic）数据集：Texas、Wisconsin、Cornell、Chameleon、Squirrel、Actor。
原论文：Amir Ghazizadeh、Rickard Ewetz、Hao Zheng，*GAMMA: Gated Multi-hop Message Passing
for Homophily-Agnostic Node Representation in GNNs*，NeurIPS 2025。
[论文](https://amir-ghz.github.io/PDFs/GAMMA.pdf) · [官方代码](https://github.com/amir-ghz/GAMMA) · [来源与 MIT 许可](NOTICE.md)。

## 从这里阅读

| 阶段 | 想法 / 研究问题 | 已有结果 |
| --- | --- | --- |
| [Baseline 复现对比](experiments/00_baseline/README.md) | 整体准确率是否接近？门控是否优于 Uniform？ | 准确率近似重现；门控有局部正向支持，一致收益未重现 |
| [实验 1：Scorer](experiments/01_scorer/README.md) | 可学习 MLP 与 LN/GELU 是否改善 agreement？ | 更复杂的 scorer 未带来稳定收益 |
| [实验 2：Hop 范围](experiments/02_hop_scope/README.md) | 固定传播后限制路由范围，是否更好？ | 范围效应依赖数据集；重训与推理删 hop 不等价 |
| [实验 3：Exact-distance / Query](experiments/03_distance_query/README.md) | 换候选表示和 Query 是否改善融合？ | 没有普遍收益；H0 Query 高度集中于自身特征 |

**[完整 Story line](STORYLINE.md)** 将问题、三个想法、对照、结果和结论连成一条论证。
[实验目录](experiments/README.md) · [课程要求对应](docs/COURSE_COMPLIANCE.md) · [三个改进想法](docs/IMPROVEMENTS.md)。
LOHO 按本次展示范围移入 [supplementary](experiments/supplementary/README.md)，不进入主线；原始证据保留。

## 结论范围

这是 **Component reproduction**。整体准确率近似重现不等于证明门控普遍有益，也不等于本地重现 SOTA 排名。
本地 Dot−Uniform 为 11/18 条件正向、7/18 负向，平均 +1.51 pp，Holm18 后无显著比较。
我们把门控总体收益表述为 inconclusive / 部分正向支持，把一致收益表述为本地未复现；
这是当前解释，不伪称历史预注册判定。论文与本地协议差异、负结果和失败均保留。
教师批准仍 `NOT_VERIFIED`，最终课程报告、slides、贡献确认和 Week 12 freeze 尚未完成。

## 实际目录

```text
STORYLINE.md                   课程论证与结果解释
experiments/
  00_baseline/                 baseline 复现与 Dot/Uniform
  01_scorer/                   实验 1：MLP、LN/GELU
  02_hop_scope/                实验 2：固定传播、变量路由范围
  03_distance_query/           实验 3：Exact-distance / Query
  supplementary/              LOHO；不进入课程主线
  analysis/, protocols/        不改写的共享历史证据
  registry.csv, catalog.json   历史记录与实验文件映射
research/                     冻结科学实现与官方快照
course/, scripts/, tests/      公共运行和验证工具
configs/, environment/        公共配置与环境版本
reports/, docs/, archives/     报告、审计和历史来源
```

前次 `03_hop_diagnostics/README.md` 仅保留为旧入口跳转，不是额外实验。

## 安装与快速检查

完整环境、数据准备、训练和评价命令见 [运行指南](docs/REPRODUCIBILITY.md)。在兼容环境中：

```powershell
python -B scripts/smoke_test.py
python -B -m experiments.exact_distance_query.src.run full --plan
```

第一条只做合成检查；第二条仅列计划。此次组织不启动新 benchmark 训练。
新环境重建仍 `NOT_VERIFIED`。数据、标签、权重和逐节点产物保存在 Git 外；校验和不等于可下载。
历史执行 commit 的 UNKNOWN 不用导入 commit 替代。目录变动后的指纹不能冒充历史运行版本。
[AI 使用](AI_USAGE.md) · [个人贡献](CONTRIBUTIONS.md) · [本次迁移](docs/STORYLINE_REORGANIZATION.md)。
