# 当前课程要求对应与缺口

更新：2026-11-19。依据用户提供的 CISC8006 Student Guide；实际日期、格式、审批以 UMMoodle 为准。
这是材料审查，不是教师评分或批准。[早期审查原文](COURSE_COMPLIANCE_20261020.md) 仅作历史记录。

| 要求 | 当前证据 | 尚缺内容 |
| --- | --- | --- |
| 一篇论文、一个可检验主张、复现级别 | GAMMA，门控 vs Uniform，Component；[baseline](../experiments/00_baseline/README.md) | 真实教师批准、最终判定规则的课程确认；不补造历史预注册 |
| Baseline 复现、论文对照、差异分析 | README 背景、Dot/Uniform 主对照、完整负值与不确定性 | 历史运行 commit UNKNOWN；split与训练seed耦合是否被接受仍需确认 |
| 三个改进想法 | [Scorer、Hop范围、Exact-distance/Query](IMPROVEMENTS.md) | 与课程正式范围和审批相对应 |
| 至少两个获批 Pilot、至少一个 Full | 三组均有技术 Pilot / Full 材料；复用计数单列 | 教师批准均 NOT_VERIFIED；技术完成不自动等于课程通过 |
| 至少三随机seeds或获准替代 | 实验3已完成每固定split三训练seeds | 早期复现、实验1/2各自的不确定性与替代方案仍需确认；不能笼统称全项目未做三seeds |
| 公平controls、ablations、失败与负结果 | 对照、LN/GELU、范围、G0–G3及empty控制都有记录 | 参数容量、Query尺度、独立图与重叠splits等限制保留 |
| 环境、来源、准备、checksums、一键检查 | 版本pin、数据manifest、测试与运行指南 | 干净环境安装、数据许可与外部证据访问方式尚未全部验证 |
| 结果链接commit/config/seed/runtime/cost/output | 历史registry与新实验run manifests；[实验目录](../experiments/README.md) | 早期commit/部分日志/成本 UNKNOWN；不要用后来导入commit替代 |
| 三阶段AI与人工检查 | [AI_USAGE](../AI_USAGE.md)已有实际记录 | 三阶段覆盖核验；至少一个有真实人工接受/修改/拒绝依据的案例 |
| 贡献与个人答辩 | [CONTRIBUTIONS](../CONTRIBUTIONS.md)模板 | 真实成员、工作证据与确认；个人答辩安排和完成情况仓库无法验证 |
| 最终report/slides/demo/peer evidence check | [Story line草案](../STORYLINE.md)与各实验技术报告 | 正式课程报告、slides、demo步骤、同伴证据检查 |
| Week12 tag与commit冻结 | 普通版本历史存在 | 按真实课程安排完成最终冻结；本次不创建课程final tag |

若已超过共同 Week12 冻结，不增加实验或修改科学结果。本次仅重组展示、路径和材料，
现有结果、配置、冻结协议与负结果原样保存。不得把新的叙事解释伪称冻结前写好的决策。
