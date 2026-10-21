# Strategy Mechanics & Microstructure Library

This directory contains in-depth, institutional-grade explanations of the economic mechanisms, order-flow dynamics, failure signatures, and live-trading management rules for each quantitative strategy in our portfolio.

---

## Purpose of Strategy Mechanics Documentation

Backtests and performance tables show *what* a strategy produced historically, but they do not explain *how* the market generates the edge or *why* the strategy experiences drawdowns. 

When trading live capital on prop accounts (e.g., **Apex Trader Funding $2,000 trailing drawdown**), an automated trader must understand:
1. **The Core Economic Engine**: Why does this trade have positive expectancy? Who is on the losing side of the trade (e.g., forced rebalancers, unwinding dealer hedges, emotional retail break chasers)?
2. **The Anatomy of Failure**: Exactly what does a losing trade look like? Why does the entry get stopped out? (e.g., Vault Break "top-ticking" into a liquidity sweep; Overnight Bias failing on chop days).
3. **Loss Clustering & Drawdown Signatures**: What is the normal frequency of consecutive losses? How fast do stops occur?
4. **Execution & Management Safeguards**: Concrete parameter optimizations (e.g., entry window limits, trigger bar filters) and account cushion rules to prevent liquidation during inevitable drawdown clusters.

---

## Strategy Index

| Strategy | Asset / TF | Classification | Core Driver | Mechanics Guide |
|---|---|---|---|---|
| **Vault Break** | NQ (30m) | Session Momentum Breakout | 10:00 CT institutional liquidity takeover above midnight VWAP + ATR volatility noise band. | [Vault Break Mechanics](file:///c:/Users/dmoto/jesse-bot/tasks/strategy_mechanics/vault_break_mechanics.md) |
| **Overnight Bias (ADX30 & ML)** | NQ (15m) | Range Expansion / Breakout | Open position relative to overnight range + trend momentum filter (ADX > 30 / Ridge ML). | [Overnight Bias Mechanics](file:///c:/Users/dmoto/jesse-bot/tasks/strategy_mechanics/overnight_bias_mechanics.md) |
| **Expiration Open Short (EOS)** | NQ (5m) | Calendar Institutional Flow | Monthly OPEX 3rd Friday options dealer delta-hedging unwind from 08:30 to 10:00 CT. | [Expiration Open Short Mechanics](file:///c:/Users/dmoto/jesse-bot/tasks/strategy_mechanics/expiration_open_short_mechanics.md) |
| **Monday Long** | NQ (5m) | Weekly Capital Deployment | Post-weekend institutional capital inflow and equity positioning re-establishment. | [Monday Long Mechanics](file:///c:/Users/dmoto/jesse-bot/tasks/strategy_mechanics/monday_long_mechanics.md) |
| **Late-Day Flow** | NQ (5m) | End-of-Day Settlement | Institutional 14:00–14:30 CT index rebalancing, Leveraged ETF flows, and MOC pressure. | [Late-Day Flow Mechanics](file:///c:/Users/dmoto/jesse-bot/tasks/strategy_mechanics/late_day_flow_mechanics.md) |
| **NFP Fade** | NQ (5m) | Macro Release Mean-Reversion | Fading pre-market liquidity overshoot on backward-looking labor employment data (07:30 CT). | [NFP Fade Mechanics](file:///c:/Users/dmoto/jesse-bot/tasks/strategy_mechanics/nfp_fade_mechanics.md) |
| **CL Sunday Gap Fade** | CL (5m) | Physical Commodity Reopen | Fading weekend commercial inventory mismatches on Globex 17:00 CT reopen. | [CL Sunday Gap Fade Mechanics](file:///c:/Users/dmoto/jesse-bot/tasks/strategy_mechanics/cl_sunday_gap_fade_mechanics.md) |
