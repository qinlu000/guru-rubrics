# Rubric 与 Trading Framework 的适配设计

## 核心原则

Buffett rubric 衡量的是投资哲学，不能把它写成 TradeBank 的字段规则。TradeBank 适配应发生在评测层：把框架中的动作、理由、时间和结果映射到统一的 canonical trajectory，再执行同一套 rubric。

## 三层结构

### 1. Rubric core

框架无关，描述大师原则本身：

- `criterion`
- `applicable_conditions`
- `source_quote`
- `source`
- `operationalization`
- `evidence_requirements`
- `pass_rule`
- `violation_rule`
- `unknown_rule`

### 2. Canonical trajectory

统一字段建议为：

```text
episode_id
timestamp
observation
market_context
portfolio_context
agent_reasoning
action
order_parameters
outcome
source_refs
```

字段缺失时保留 `null` 和缺失原因，不能用后续结果或外部猜测填充。

### 3. Framework adapter

每个框架单独维护字段映射和可观测性：

```text
framework_id: tradebank
action_path: trajectory.action
reasoning_path: trajectory.rationale
timestamp_path: trajectory.timestamp
portfolio_path: null
market_context_path: null
outcome_path: trajectory.outcome
```

适配器还要声明每条 rubric 所需字段是否存在。

## TradeBank 的评分状态

不要只使用二元的 pass/fail，至少使用四种状态：

- `pass`：有足够证据支持符合；
- `violate`：有足够证据支持违反；
- `not_applicable`：该条目不适用于当前决策；
- `not_observable`：条目适用，但 TradeBank 轨迹没有提供判断所需 context。

`not_observable` 不能计为违反。例如，TradeBank 没有提供估值或内在价值时，不能因为 agent 没有展示安全边际就判定它违反 Buffett 原则。

## 分数报告

同时报告行为分数和可观测覆盖率：

```text
coverage = (pass + violate) / (pass + violate + not_observable)
observable_score = pass / (pass + violate)
```

总分必须带上 coverage。否则一个只暴露 action、不暴露 portfolio/context 的框架会因为大量信息不可见而产生虚假的高分或低分。

## 示例

```yaml
criterion: 只有在价格显著低于保守内在价值时买入
applicable_conditions:
  - action in [buy, increase]
evidence_requirements:
  - market_price
  - intrinsic_value_estimate
  - margin_of_safety_or_valuation_comparison
pass_rule: 明确比较价格与保守内在价值，并说明安全边际
violation_rule: 明确以价格上涨、短期催化剂或未经估值的预测作为唯一买入理由
unknown_rule: 缺少价格、估值或买入时的市场 context
framework_adapters:
  tradebank:
    action: trajectory.action
    reasoning: trajectory.rationale
    market_price: null
    intrinsic_value_estimate: null
    result: trajectory.outcome
```

这个例子在 TradeBank 中可能返回 `not_observable`，而不是 `violate`。如果以后通过时间戳把 TradeBank 与行情、组合和基本面数据对齐，只需补全 adapter，Rubric core 不需要重写。

## 当前 TradeBank 的适用范围

优先使用 TradeBank 评测能够从动作和理由直接观察到的条目，例如：

- 是否追逐短期价格波动；
- 是否给出持有期限或退出条件；
- 是否在理由中讨论风险和不确定性；
- 是否频繁反转交易方向；
- 是否明确承认不知道或选择不行动。

需要完整 context 才能判断的条目先标成低覆盖或不可观察，例如：

- 安全边际是否真实存在；
- 是否处于能力圈内；
- 组合是否过度集中；
- 买入价格是否低于保守内在价值；
- 对新信息的反应是否合理。

