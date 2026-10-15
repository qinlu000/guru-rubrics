# Buffett 语料首批选择（pilot）

官方来源：<https://www.berkshirehathaway.com/letters/letters.html>。下载与处理记录见 [`manifest.json`](manifest.json)，推荐集合见 [`selected_sources.json`](selected_sources.json)。

## 取舍原则

1. 只用伯克希尔官网托管的股东信和《Owner's Manual》，保证作者和版本可追溯。
2. 优先选择明确讲投资判断的方法论段落，而不是只报告经营结果的段落。
3. 覆盖不同决策维度：理解业务、管理层、估值、现金流、风险、市场心理、持有期限、资本配置。
4. 跨越早期明确规则、后期定义和近期重申，区分长期稳定原则与阶段性表达。
5. 案例段落先当作“应用证据”，不直接升级为普遍 Rubric。

## 推荐 MVP

| 年份 | 来源 | 用途 | 主要主题 | 官方链接 |
|---:|---|---|---|---|
| 1977 | Berkshire Hathaway 1977 Shareholder Letter | core | business_understanding, long_term_prospects, management_quality, price_discipline, anti_short_termism | [原文](https://www.berkshirehathaway.com/letters/1977.html) |
| 1986 | Berkshire Hathaway 1986 Shareholder Letter | core | owner_earnings, cash_flow, maintenance_capex, business_analysis | [原文](https://www.berkshirehathaway.com/letters/1986.html) |
| 1987 | Berkshire Hathaway 1987 Shareholder Letter | core | market_psychology, price_vs_business, temperament, opportunity_in_declines | [原文](https://www.berkshirehathaway.com/letters/1987.html) |
| 1989 | Berkshire Hathaway 1989 Shareholder Letter | core | quality_over_bargain, economic_moat, management_quality, anti_cigar_butt | [原文](https://www.berkshirehathaway.com/letters/1989.html) |
| 1992 | Berkshire Hathaway 1992 Shareholder Letter | core | intrinsic_value, margin_of_safety, discounted_cash_flows, growth_quality | [原文](https://www.berkshirehathaway.com/letters/1992.html) |
| 1993 | Berkshire Hathaway 1993 Shareholder Letter | supporting | market_price_vs_value, short_run_noise, long_run_business_value | [原文](https://www.berkshirehathaway.com/letters/1993.html) |
| 1996 | Berkshire Hathaway 1996 Shareholder Letter | core | circle_of_competence, business_understanding, rational_price, long_horizon, concentration | [原文](https://www.berkshirehathaway.com/letters/1996.html) |
| 1997 | Berkshire Hathaway 1997 Shareholder Letter | core | market_psychology, long_term_saving, price_volatility, behavioral_discipline | [原文](https://www.berkshirehathaway.com/letters/1997.html) |
| 2000 | Berkshire Hathaway 2000 Shareholder Letter | core | discounted_cash_flow, certainty, timing_of_cash_flows, growth_not_equal_value | [原文](https://www.berkshirehathaway.com/letters/2000pdf.pdf) |
| 2008 | Berkshire Hathaway 2008 Shareholder Letter | core | liquidity, financial_resilience, risk_control, opportunity_cost, sleep_at_night | [原文](https://www.berkshirehathaway.com/letters/2008ltr.pdf) |
| 2011 | Berkshire Hathaway 2011 Shareholder Letter | core | definition_of_risk, purchasing_power, productive_assets, inflation, beta_is_not_risk | [原文](https://www.berkshirehathaway.com/letters/2011ltr.pdf) |
| 2013 | Berkshire Hathaway 2013 Shareholder Letter | core | future_productivity, anti_speculation, simplicity, circle_of_competence, quick_profit_rejection | [原文](https://www.berkshirehathaway.com/letters/2013ltr.pdf) |
| 2023 | Berkshire Hathaway 2023 Shareholder Letter | core | permanent_loss, long_duration_ownership, patience, business_quality, price_dependent_buybacks | [原文](https://www.berkshirehathaway.com/letters/2023ltr.pdf) |
| 1999 | Berkshire Hathaway: An Owner's Manual | foundational | owner_orientation, long_term_partnership, capital_allocation, debt_discipline, shareholder_alignment, intrinsic_value | [原文](https://www.berkshirehathaway.com/owners.html) |

## 第二批候选

| 年份 | 官方链接 | 主题 |
|---:|---|---|
| 1990 | [原文](https://www.berkshirehathaway.com/letters/1990.html) | look_through_earnings, earnings_quality |
| 1994 | [原文](https://www.berkshirehathaway.com/letters/1994.html) | intrinsic_value, insurance_float, capital_allocation |
| 1999 | [原文](https://www.berkshirehathaway.com/letters/final1999pdf.pdf) | capital_allocation, intrinsic_value, mistake_admission |
| 2004 | [原文](https://www.berkshirehathaway.com/letters/2004ltr.pdf) | business_quality, capital_allocation |
| 2014 | [原文](https://www.berkshirehathaway.com/letters/2014ltr.pdf) | intrinsic_value, capital_allocation, operating_businesses |
| 2016 | [原文](https://www.berkshirehathaway.com/letters/2016ltr.pdf) | mistakes, business_acquisition, owner_earnings |
| 2024 | [原文](https://www.berkshirehathaway.com/letters/2024ltr.pdf) | mistake_correction, manager_quality, business_understanding |

## 推荐使用顺序

先用《Owner's Manual》建立原则词表，再用 1977、1986、1987、1989、1992、1996、1997、2000、2008、2011、2013、2023 逐主题提取；1993 作为市场价格/内在价值的交叉验证来源。每条候选 Rubric 都保留 source_id、原文锚点、适用情境和可观察轨迹证据。
