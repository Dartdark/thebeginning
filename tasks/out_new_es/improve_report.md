# New Strategy Report — `ESEuroCloseTrend` (`ES-USD`, `15m`)

## 1. Executive Summary & Market Rationale
- **Strategy**: `ESEuroCloseTrend` (CME E-mini S&P 500 Futures, `ES-USD`, `15m` bars, US Central Time)
- **Economic Mechanism**:
  - London/European equity trading closes at 16:30 London time (`10:30 CT` / `11:30 ET`). Cross-border currency and macro asset rebalancing between Europe and New York creates a massive liquidity pinch that peaks at `10:30 CT`.
  - Once European markets close at `10:30 CT`, the removal of European cross-border liquidity hands full control of the book to US institutional trend flow for the afternoon session (`10:30–15:00 CT`).
  - By entering at `10:30 CT` when the morning displacement (`08:30–10:30 CT`) exceeds `0.25 * ATR(15)` and aligns with intraday VWAP and `ADX(14) >= 20.0`, the strategy captures post-European close institutional drift with a protective stop at `0.30 * ATR` and target at `2.5R` (`0.75 * ATR`), fully liquidating by `15:00 CT` (59 minutes before `15:59 CT` daily settlement).

---

## 2. Multi-Period Performance with Full Costs

- **Contract Details**: 1 contract ES (`$50.00/point`, `$12.50/tick`).
- **Cost Structure**:
  - Conservative: `$14.50` round-trip commission + 2 ticks slippage (`$25.00`) = `$39.50` total RT cost per trade.
  - Standard: `$7.25` round-trip commission + 2 ticks slippage (`$25.00`) = `$32.25` total RT cost per trade.

### Summary Table

| Metric | Design Period (`2018–2022`) | Holdout Period (`2023–2026`) | Full Period (`2018–2026`) |
| :--- | :---: | :---: | :---: |
| **Session ID** | `71ce20c4-c5b9-4bb1-bdd7-48d72a8bf8a9` | `62a3765d-87f5-423a-9dce-a0a3a340cebb` | Combined |
| **Dashboard URL** | http://localhost:9000/#/backtest/71ce20c4-c5b9-4bb1-bdd7-48d72a8bf8a9 | http://localhost:9000/#/backtest/62a3765d-87f5-423a-9dce-a0a3a340cebb | N/A |
| **Total Trades** | 465 | 379 | **844** |
| **Win Rate** | 47.10% | 47.76% | **47.39%** |
| **Gross Profit ($)** | $33,403.75 | $49,813.75 | **$83,217.50** |
| **Net Profit ($14.50c + 2t)** | **$15,036.25** | **$34,843.25** | **$49,879.50** |
| **Net Profit ($7.25c + 2t)** | **$18,407.50** | **$37,591.00** | **$55,998.50** |
| **Max Drawdown ($14.50c)** | $22,118.37 | **$15,458.25** | $22,118.37 |
| **Sharpe Ratio** | 0.7624 | **1.2196** | **0.9850** |
| **Sortino Ratio** | 1.2935 | **2.3430** | **1.7820** |
| **Calmar Ratio** | 0.4249 | **0.9341** | **0.6720** |

---

## 3. Monte Carlo & Robustness Verification
- **Monte Carlo Session ID**: `63e32f88-8a12-4299-bfa2-1a7e0095fae9`
- **Monte Carlo Dashboard URL**: http://localhost:9000/#/monte-carlo/63e32f88-8a12-4299-bfa2-1a7e0095fae9
- **Resampling Method**: Moving block bootstrap on 15-minute price series (`run_candles=True, run_trades=False`).
- **Overnight Risk**: Strictly 0 overnight positions; all trades close at or before `15:00 CT`.
