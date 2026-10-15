# 公开 Trading Agent 轨迹清单

核验日期：2026-10-02（UTC）。这里把“轨迹”分成三类：

- **完整或近完整轨迹**：有多轮观察、分析、行动、组合状态和结果，可以按时间顺序评测。
- **推理/行动快照**：有单次分析、方向、信心或理由，但没有持续的组合状态和多轮行动。
- **框架或数据环境**：可以自己运行 agent，但仓库没有已经生成的 agent 轨迹。

## 结论

目前最适合作为第一批直接评测材料的是 [LLM-Trading-Lab](https://github.com/LuckyOne7777/LLM-Trading-Lab)。它同时提供公开 ChatGPT 对话、交易日志、每日组合状态和每周研究记录，足以把一段行为还原成“观察 → 理由 → 行动/不行动 → 下一状态”。它是单一实验、偏微型生物科技股票，且仓库顶层没有明确开源许可证，所以适合研究内部的试点评测和引用，不宜直接再分发原始对话。

## 候选清单

| 候选 | 类型 | 可直接用于轨迹评测？ | 可得到的字段 | 许可证/访问 | 判断 |
|---|---|---:|---|---|---|
| [LLM-Trading-Lab](https://github.com/LuckyOne7777/LLM-Trading-Lab) | 完整/近完整公开实验 | **可以，首选真实轨迹** | 多轮 ChatGPT 消息、持仓、现金、买卖、理由、止损、每日净值、结果、周研究 | 仓库公开；未发现顶层 LICENSE；对话通过公开 ChatGPT 分享页 | 最接近真实 agent 轨迹。需处理早期对话缺口，并保留原始链接而非再分发全文。 |
| [corelabel/agent-trading](https://huggingface.co/datasets/corelabel/agent-trading) | 有 context 的合成轨迹库 | **可以，首选结构化轨迹** | 7,670 条 trajectory trees、10,391 条终局路径、46,725 个标注步骤；每步有 `sim_time`、action/tool、observation payload、thought、state delta、任务和 reward | Apache-2.0；Hugging Face 公开；合成数据 | 最适合解决 TradeBank 的 context 缺失问题，但 ticker、价格、新闻和 agent 行为都是合成/脚本化的，不能当真实投资风格证据。 |
| [StockBench snapshot](https://huggingface.co/datasets/stock-agent/snapshot_20260428) | 真实市场上的模型运行缓存 | **可以，需解包整理** | 约 32,000 个 analysis/decision JSON；完整 system/user prompt、20 只股票的价格/新闻/基本面/持仓/历史决策、模型输出、模型和 run 元数据 | 公开 1.8GB ZIP；数据集页面未声明单独许可证；源代码 [StockBench](https://github.com/ChenYXxxx/stockbench) 为 Apache-2.0 | 这是最像“有 context 的 TradeBank”且规模较大的候选；不是现成单一 JSONL，需要按 `run_id + 日期` 配对 analysis/decision，并先核对生成数据的再分发和模型输出许可。 |
| [FinAgent Opinions](https://huggingface.co/datasets/suanlab/finagent-opinions) | 推理/行动快照 | **部分可以** | ticker、日期、agent、方向、信心、reasoning、关键论点、1 周/1 月未来收益和正确性 | Apache-2.0，Hugging Face 公开数据集 | 适合先测 rubric grader 对一条理由是否符合 Buffett 原则；不是完整轨迹。 |
| [LLM Investor Behavior Benchmark](https://github.com/LuckyOne7777/LLM-Investor-Behavior-Benchmark) | 评测框架 | **不可以直接用** | 运行后可保存组合状态、交易日志、研究、行为/绩效指标 | MIT | 有很好的轨迹 schema 和 replay 思路，但需要自己运行 agent。 |
| [TraderHarness](https://github.com/HephaestLab/TraderHarness) | 有 context 的回测/轨迹框架 | **有一个 demo 可读，批量轨迹需运行** | 可生成完整消息、工具 schema、工具调用、时点市场信息、成交和组合状态 | Apache-2.0（仓库声明）；公开 A 股数据集另有数据许可说明 | 仓库附带的 `momentum_dragon_2024-03-14.jsonl` 只有输出和 context digest，完整请求需靠环境回放；因此不能把它当作已经打包好的大规模 context 轨迹集。 |
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | 多 agent 运行框架 | **不可以直接用** | 代码、角色、prompt、工具链 | Apache-2.0 | 是可运行系统，不是已生成的轨迹库。 |
| [StockBench](https://github.com/ChenYXxxx/stockbench) | 多步交易 benchmark/框架 | **不可以直接用** | 历史市场、新闻、财务数据和生成报告的代码路径 | Apache-2.0 | 仓库没有核实到已提交的 LLM 轨迹；运行需要 API key。 |
| [trading-agents-data](https://huggingface.co/datasets/jackzhousmu/trading-agents-data) | 市场数据 | **不可以** | 价格和新闻 JSONL | 页面公开 | 压缩包检查到的内容只有 price/news，没有 agent 消息、行动或组合状态。 |
| [FinAgent Benchmark](https://huggingface.co/datasets/Guen/finagent-benchmark) | 金融 QA/工具问答 | **不可以** | 问题、答案、证据、SEC filing 来源 | MIT | 是金融问答 benchmark，不是交易轨迹。 |
| [Trade LLM Quant Trading Data](https://huggingface.co/datasets/yaothehobbit/trade-llm-quant-trading-data) | 单步生成样例 | **不可以作为轨迹** | 技术形态/新闻/财报 prompt，方向、入场、止损、目标等 | Hugging Face 公开 | 可用来测试单条交易理由的 rubric，但没有跨日状态和真实行动。 |

## 首选材料的具体入口

### LLM-Trading-Lab

- [仓库 README](https://github.com/LuckyOne7777/LLM-Trading-Lab)
- [交易日志 CSV](https://raw.githubusercontent.com/LuckyOne7777/LLM-Trading-Lab/main/Experiments/chatgpt_micro-cap/csv_files/Trade%20Log.csv)
- [每日组合更新 CSV](https://raw.githubusercontent.com/LuckyOne7777/LLM-Trading-Lab/main/Experiments/chatgpt_micro-cap/csv_files/Daily%20Updates.csv)
- [对话索引](https://raw.githubusercontent.com/LuckyOne7777/LLM-Trading-Lab/main/Experiments/chatgpt_micro-cap/collected_artifacts/chats.md)
- [评测报告](https://raw.githubusercontent.com/LuckyOne7777/LLM-Trading-Lab/main/Experiments/chatgpt_micro-cap/evaluation/evaluation_report.md)
- 对话 1：[ChatGPT share](https://chatgpt.com/share/6897c737-2b10-8004-82f3-a32e00665b2d)
- 对话 2：[ChatGPT share](https://chatgpt.com/share/68b5b245-1730-8004-a917-d5539c3adf48)
- 对话 3：[ChatGPT share](https://chatgpt.com/share/68d88db7-4a38-8004-ae29-aafbaa4214c8)

它的可用结构大致是：

```text
用户提供的当日组合/市场信息
        ↓
ChatGPT 的研究、理由、风险判断、买卖或不行动
        ↓
Trade Log + Daily Updates 中的实际行动和组合变化
        ↓
后续日期的盈亏与持仓结果
```

### StockBench snapshot

这个快照不是一个整理好的单文件轨迹集，而是一个公开的 1.8GB ZIP。中央目录中可以看到大量：

- `analysis_*.json`：fundamental filter 的完整 system prompt、用户输入和模型输出；
- `decision_*.json`：portfolio、20 只股票的市场/新闻/基本面/持仓状态、历史决策，以及最终 action/reasons/confidence；
- 同一 `run_id` 下按日期组织的连续调用，可以组成“当日 context → 分析 → 决策 → 下一日 history”的轨迹。

它覆盖多个模型和多种运行设置，适合做跨 agent 的风格对照。下载时不需要把整个 ZIP 解开：可以先读取 ZIP central directory，只按需要的日期、模型和 `analysis_/decision_` 文件做 HTTP range 提取。

## 对 Buffett rubric 的适用限制

LLM-Trading-Lab 的实验集中在微型生物科技股和催化剂事件，组合也比较集中。因此它很适合检验 rubric 是否能识别“这不是 Buffett 风格”，但不能单独证明 rubric 对所有资产类别都可靠。对于“长期持有”“能力圈边界”“安全边际”等条目，必须要求评测器只使用当时已经出现的消息和状态，不能把后来的涨跌结果倒灌进早期评分。

## 建议的落地顺序

1. 先把 LLM-Trading-Lab 的三段公开对话、Trade Log、Daily Updates 和周研究报告整理成一个 `trajectory.jsonl`。
2. 每个时间点保留 `observation`、`evidence`、`reasoning`、`action`、`portfolio_before`、`portfolio_after`、`outcome` 和原始 URL。
3. 用现有的 20 条 Buffett rubric 做一次“逐时间点 + 不适用”评测；没有相关证据时输出 `not_applicable`，不要强行判定为不符合。
4. 再用 FinAgent Opinions 做大批量的单条理由测试，把它标成 snapshot 集，不能和完整轨迹分数混在一起。
