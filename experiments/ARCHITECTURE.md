# GAMMA 架构图总览

这组图由内置 ImageGen 生成。原始架构根据 GAMMA 论文绘制，实验图依据仓库的模型实现与实验协议绘制。

## 原始 GAMMA

![GAMMA 从共享投影、多跳计算、缩放和归一化到逐节点迭代路由](00_baseline/figures/gamma-architecture.png)

路由从 hop 权重计算加权表示，经 squash 后计算 Dot agreement，并更新下一轮的 logits。图示参考 [GAMMA 论文](https://amir-ghz.github.io/PDFs/GAMMA.pdf)与[本地实现对照](../docs/CLAIM_AND_REPRODUCTION.md)。

## Baseline · Dot vs Uniform

![两个独立实验组共享 hop 候选和全局缩放，分别使用 Dot 和 Uniform 权重](00_baseline/figures/dot-vs-uniform.png)

Dot 组使用逐节点的动态权重，Uniform 组对参与的 hop 等权融合。参见 [Baseline 实验](00_baseline/README.md)。

## 实验 1 · Scorer

![Dot、MLP、MLP+LN 和 MLP+GELU 的 agreement 函数对照](01_scorer/figures/routing-scorer.png)

四行代表四种独立配置。计算出的 agreement 用于更新路由 logits。参见 [Scorer 实验](01_scorer/README.md)。

## 实验 2 · Hop 范围

![全量计算 H0 至 H5，固定掩码控制参与路由的 hop](02_hop_scope/figures/fixed-propagation-routing-scope.png)

图中 x=2 是受限范围示例。它与 x=5 都计算全部六个 hop 表示。参见 [Hop 范围实验](02_hop_scope/README.md)。

## 实验 3 · Exact-distance / Query

![G0 使用 Walk 与 Consensus，G1 至 G3 在 Exact shells 上分别比较 Consensus、H0 和 Walk H4](03_distance_query/figures/exact-distance-query.png)

G1–G3 的融合候选来自 Exact-distance shells。G3 另外计算 Walk H4 作为 Query。参见 [Exact-distance / Query 实验](03_distance_query/README.md)。
