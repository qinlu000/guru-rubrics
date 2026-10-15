# Buffett rubric v0.1 审查报告

审查目标：判断每条 rubric 能否直接作用于 trading-agent trajectory，而不是只表达一个抽象投资理念。

## 总体结论

20 条结构完整、来源字段齐全，已经具备候选 rubric 的基本形态；但目前还不适合直接用于 TradeBank 评分。主要问题有四类：

1. **缺少 `not_observable_if`**：很多条目把“没有相关证据”写成 `not_applicable`，会掩盖真正的行为缺失，也无法处理 TradeBank 的 context 缺口。
2. **抽象词没有阈值或证据标准**：如 `attractive`、`favorable`、`high-quality`、`meaningful buffer`、`materially higher`、`highly uncertain`、`excessive leverage`。
3. **条目之间有重复**：若不去重，同一种行为会被重复计分。
4. **部分条目要求多项行为或跨越不同决策类型**：不满足原子化要求，或者不适合股票 trading agent。

## 分条建议

| ID | 当前判断 | 主要问题 | 建议 |
|---|---|---|---|
| r001 | 保留，修改 | 买入但没有业务分析时被错误地允许 `not_applicable`；`经济引擎`仍需最低证据标准 | 只要发生买入分析且有业务信息就适用；缺业务 context 用 `not_observable`，有 context 却不分析才 `violate` |
| r002 | 重写/与 r012 去重 | `favorable long-term prospects` 太宽；与“多年盈利增长”重复 | 保留为“竞争优势/行业结构支持的长期经济性”，把盈利增长留给 r012，并规定 horizon 与证据 |
| r003 | 拆分或重写 | 同时评估 integrity 和 competence；`集中或长期购买`是额外条件 | 拆为管理层诚信、管理层能力，或只保留一个；没有管理信息时 `not_observable` |
| r004 | 保留，细化 | `attractive price` 未定义；与 r010 有重叠 | 设为“价格与价值比较”；r010 单独评估“缓冲幅度/安全边际” |
| r005 | 保留，修改 | 没有短期价格理由不等于符合；`primarily` 不可直接判定 | 缺理由用 `not_observable`；明确“短期价格预测是主要依据”需要证据比例或原文表述 |
| r006 | 保留 | 需要明确维护性资本支出不可得时的处理 | 加 `required_evidence` 和 `not_observable_if`；不要把缺少 capex 数据直接判违反 |
| r007 | 拆分或收窄 | 同时要求识别基本面变化、区分报价变化、再决定行动 | 保留为“价格变化后先检查业务是否变化”；把行动后果作为另一条或结果字段 |
| r008 | 重写 | `high-quality` 与 `reasonable` 未操作化；适用场景较少 | 指定可观察质量证据，如资本回报、竞争优势、现金转化；仅在明确比较两个候选时适用 |
| r009 | 重写 | 可能过度要求正式 DCF；与 r014 重叠 | 改为“价值判断是否连接到未来现金流”；不要要求固定估值模型 |
| r010 | 保留，细化 | `meaningful buffer` 没有标准；缺 value/price 时状态不清 | 规定区间、情景或下行测试；缺信息用 `not_observable` |
| r011 | 重写 | “已知能力圈”通常无法从单条轨迹验证；要求 Agent 自我声明过强 | 触发条件改成 Agent 明确表示陌生/无法理解，或轨迹提供 coverage context；否则 `not_observable` |
| r012 | 与 r002 去重 | `materially higher`、`multi-year` 未定义；TradeBank 短线任务中覆盖率会很低 | 设为长期持有专用条目，规定 horizon；不要和 r002 同时计分 |
| r013 | 保留，细化 | `highly uncertain` 与“precise valuation”主观 | 要求范围、情景、置信度、仓位或放弃其中一种可观察处理 |
| r014 | 与 r009 合并或重新定位 | 未来现金流估值与折现估值重复 | 如果保留，专门评估“现金流时间点/延迟的敏感性”，不要重复检查是否做 DCF |
| r015 | 保留但低频 | 条件复杂，只有涉及增长投入时才适用 | 保留为高级条目；明确增长投入、增量现金流和比较关系必须出现 |
| r016 | 移出首批或拆分 | 把公司流动性、投资组合流动性、危机融资混在一起 | 拆成“组合现金缓冲”和“企业融资依赖”；TradeBank 无 obligations context 时不可观察 |
| r017 | 拆分 | 企业负债和 Agent 使用杠杆是两种不同风险 | 分为“标的资产负债表杠杆”和“投资组合杠杆”；明确适用对象 |
| r018 | 移出首批或收窄 | 购买力损失需要通胀、期限、实际收益 context，TradeBank 通常没有 | 仅在存在持有期限和实际收益信息时评估；否则 `not_observable` |
| r019 | 与 r013 区分 | 与不确定性条目接近 | 将 r019 定义为“无法形成粗略生产力估计时不投资”；r013 只评估如何表达和管理不确定性 |
| r020 | 保留但细化 | 与 r010 重叠；`permanent impairment` 需要具体情景 | r010 评估价格-价值缓冲，r020 评估不可逆损失情景和仓位约束，分别保留 |

## 建议的最小字段补充

当前四个固定部分可以保留，但 `operationalization` 应增加：

```json
{
  "trigger": "触发此条 rubric 的轨迹情境",
  "observable_behavior": "实际观察什么行为",
  "required_context": ["需要哪些字段或证据"],
  "pass_if": "满足条件",
  "violate_if": "违反条件",
  "not_observable_if": "缺少 context 时返回 unknown",
  "evidence_span": "需要引用的轨迹范围"
}
```

## 首批 TradeBank 子集

建议先保留 r001、r004、r005、r007、r010、r011、r013、r019、r020，重写后再测试；r016、r017、r018 暂时移出首批。r002/r012、r009/r014、r013/r019 需要先去重或明确边界。

任何条目若不能让评测器引用一段具体 trajectory evidence，并在 `pass`、`violate`、`not_observable` 之间做出稳定区分，都不应进入最终 rubric bank。

