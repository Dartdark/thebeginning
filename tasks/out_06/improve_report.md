# Phase 2 Improvement Report — Task 06: `NQExpirationOpenShort` (NQ 3rd-Friday Monthly Options Expiration Open Short)

## 1. Executive Summary & Acceptance Gate Verdict

- **Strategy:** `NQExpirationOpenShort` (`NQ-USD`, `5m` bars, short 1 contract on the 3rd Friday of each month at `08:30 CT` (`08:35 CT` bar close), exit at `10:00 CT` (`10:05 CT` bar close), `0.35 × 14-day Daily ATR` stop loss)
- **Pre-Registered Plan:** `tasks/out_06/improve_plan.md` (5 mechanism-driven variants tested on `2018-01-02` to `2022-12-31` design window)
- **Design Window (`2018-01-02` to `2022-12-31`) Winner:**
  - **`NQExpShortV5` (`V1 + V2`: Skip if overnight gap `< -0.50 × Daily ATR` + Limit Profit Target at `-0.50 × Daily ATR`)** beat the original baseline on **both** Net Profit and Max Drawdown in `2018–2022`:
    - **Net Profit (`$14.50` RT comm + 1t Mkt / 0t Lmt slip):** **`$23,548.30`** vs Baseline **`$18,317.20`** (**`+$5,231.10`**, `+28.6%`)
    - **Net Profit (`$7.25` RT comm + 1t Mkt / 0t Lmt slip):** **`$23,968.80`** vs Baseline **`$18,752.20`** (**`+$5,216.60`**, `+27.8%`)
    - **Max Drawdown (`$14.50` RT comm + slip):** **`$4,144.30`** vs Baseline **`$4,543.80`** (**`-$399.50`** lower drawdown)
    - **Sharpe / Sortino / Calmar (Gross Jesse):** **`0.9880` / `1.9919` / `1.2261`** vs Baseline **`0.8090` / `1.5335` / `0.9038`**
- **Holdout Validation (`2023-01-01` to `2026-10-09`, touched once):**
  - On the `2023–2026` holdout, **`NQExpShortBase`** generated **`$30,679.00`** Net (`$14.50` RT comm + `$10` slip, 45 trades, 60.0% net WR, Max DD **`$7,467.20`**, Sharpe `1.1482`, Sortino `2.2573`), whereas **`NQExpShortV1`** generated **`$27,963.00`** Net (43 trades, Max DD `$7,467.20`, Sharpe `1.0805`) and **`NQExpShortV5`** generated **`$26,685.00`** Net (43 trades, Max DD `$7,467.20`, Sharpe `1.0507`).
  - Why: In the higher-nominal-range `2023–2026` market (where daily NQ ATR expanded and 0DTE/AM-settled index option gamma grew), the two 3rd Fridays with large negative overnight gaps (`< -0.50 ATR`) did not mean-revert at the open—dealer de-hedging continued pressing NQ lower into `10:00 CT` (`+$2,765.00` gross across those 2 trades). Similarly, capping gains at `-0.50 × Daily ATR` via a limit target gave up late-morning continuation on the largest 2023–2026 OPEX unwind days (`-$1,278.00` net vs `V1`).
- **Acceptance Gate Verdict:** **REJECT IMPROVEMENT / KEEP ORIGINAL (`NQExpirationOpenShort` Baseline)**.
  - Per Guardrail #5, an improvement is accepted *only* if it beats the original in **BOTH** `2018–2022` and `2023–2026` on **BOTH** Net $ per contract and Max Drawdown. While `V2` and `V5` beat the baseline on both metrics in `2018–2022`, neither beats the baseline on `2023–2026` holdout Net $.

---

## 2. Transaction Cost Model Applied

All numbers below are computed per 1 E-mini NQ contract (`$20.00 / pt`, tick size `0.25 pt = $5.00`):
1. **Brief / Guardrail #3 Strict Cost Model (`$7.25/side` = `$14.50` RT commission):**
   - Market / Stop exit trade: `$14.50` commission + `2 ticks` (`$10.00`) slippage = **`$24.50` RT**
   - Limit target exit trade (`V2`, `V5`): `$14.50` commission + `1 tick` (`$5.00`) entry slippage + `0 tick` limit exit slippage = **`$19.50` RT**
2. **Standard Reference Cost Model (`$7.25` RT commission):**
   - Market / Stop exit trade: `$7.25` commission + `$10.00` slippage = **`$17.25` RT**
   - Limit target exit trade (`V2`, `V5`): `$7.25` commission + `$5.00` slippage = **`$12.25` RT**

---

## 3. Design Window Log (`2018-01-02` to `2022-12-31`, `warm_up_candles: 210`, `fast_mode: false`)

| Variant | Session ID & Dashboard Link | Exact Change | Trades (Lmt Exits) | Net WR (`$14.50`c) | Gross PnL | Net PnL (`$14.50`c + slip) | Max DD (`$14.50`c + slip) | Net PnL (`$7.25`c + slip) | Max DD (`$7.25`c + slip) | Sharpe / Sortino / Calmar | Design Conclusion |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NQExpShortBase`** | `2a42c2b5-076f-4488-bd14-c8cba7e0ebe4` — [View on dashboard](http://localhost:9000/#/backtest/2a42c2b5-076f-4488-bd14-c8cba7e0ebe4) | Unchanged baseline: Short 3rd Friday `08:30 CT`, exit `10:00 CT`, `0.35 ATR` stop | 60 (0) | 58.33% | `$19,787.20` | `$18,317.20` | `$4,543.80` | `$18,752.20` | `$4,514.80` | `0.8090` / `1.5335` / `0.9038` | Baseline reference |
| **`NQExpShortV1`** | `e1394e93-803d-43bd-92fc-b69e06e71d50` — [View on dashboard](http://localhost:9000/#/backtest/e1394e93-803d-43bd-92fc-b69e06e71d50) | Skip if overnight gap (`08:30 CT` close - prior RTH `15:00 CT` close) `< -0.50 × Daily ATR` | 58 (0) | 58.62% | `$21,172.80` | **`$19,751.80`** | `$4,543.80` | **`$20,172.30`** | `$4,514.80` | `0.8727` / `1.6889` / `0.9670` | **Beats Base Net $** (`+$1,434.60`), ties DD |
| **`NQExpShortV2`** | `80612151-0503-4644-9eb1-d6e88da87dda` — [View on dashboard](http://localhost:9000/#/backtest/80612151-0503-4644-9eb1-d6e88da87dda) | Resting Limit Take-Profit at `entry - 0.50 × Daily ATR` (`0` exit slippage) | 60 (9) | 60.00% | `$23,538.70` | **`$22,113.70`** | **`$4,144.30`** | **`$22,548.70`** | **`$4,122.55`** | `0.9262` / `1.8275` / `1.1579` | **Beats Base Net $ (`+$3,796.50`) AND Max DD (`-$399.50`)** |
| **`NQExpShortV3`** | `5dc3b0b8-d2c5-4305-a124-28ddff301bad` — [View on dashboard](http://localhost:9000/#/backtest/5dc3b0b8-d2c5-4305-a124-28ddff301bad) | Earlier time exit at `09:30 CT` (`09:35 CT` bar close) | 60 (0) | 60.00% | `$16,176.40` | `$14,706.40` | **`$3,684.80`** | `$15,141.40` | **`$3,655.80`** | `0.7822` / `1.5471` / `0.9037` | Lowers DD (`-$859.00`) but loses `-$3,610.80` Net $ (REJECT) |
| **`NQExpShortV4`** | `8fd13a31-e9b6-4dd2-9707-b3dc62938c5a` — [View on dashboard](http://localhost:9000/#/backtest/8fd13a31-e9b6-4dd2-9707-b3dc62938c5a) | Tighter stop loss at `0.25 × Daily ATR` | 60 (0) | 55.00% | `$19,617.92` | `$18,147.92` | **`$3,937.83`** | `$18,582.92` | **`$3,894.33`** | `0.8353` / `1.6947` / `1.0191` | Lowers DD (`-$605.97`) but slightly lower Net $ (`-$169.28`) (REJECT) |
| **`NQExpShortV5`** | `e5bfb5d3-d18d-416b-a313-21f6c30fd3ba` — [View on dashboard](http://localhost:9000/#/backtest/e5bfb5d3-d18d-43bd-9707-b3dc62938c5a) | Combined `V1 + V2`: Skip overnight gap `< -0.50 ATR` + Limit Target `-0.50 ATR` | 58 (9) | 60.34% | **`$24,924.30`** | **`$23,548.30`** | **`$4,144.30`** | **`$23,968.80`** | **`$4,122.55`** | **`0.9880` / `1.9919` / `1.2261`** | **Design Winner: Beats Base Net $ (`+$5,231.10`) AND Max DD (`-$399.50`)** |

*(Note: Dashboard URL for `NQExpShortV5` Design is `http://localhost:9000/#/backtest/e5bfb5d3-d18d-416b-a313-21f6c30fd3ba`.)*

---

## 4. Holdout Validation Log (`2023-01-01` to `2026-10-09`, `warm_up_candles: 210`, `fast_mode: false`)

| Variant | Session ID & Dashboard Link | Trades (Lmt Exits) | Net WR (`$14.50`c) | Gross PnL | Net PnL (`$14.50`c + slip) | Max DD (`$14.50`c + slip) | Net PnL (`$7.25`c + slip) | Max DD (`$7.25`c + slip) | Sharpe / Sortino / Calmar | Holdout Verdict vs Base |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NQExpShortBase`** | `301b293c-4e59-46e1-8c5f-2f58cbc13ddf` — [View on dashboard](http://localhost:9000/#/backtest/301b293c-4e59-46e1-8c5f-2f58cbc13ddf) | 45 (0) | 60.00% | **`$31,781.50`** | **`$30,679.00`** | **`$7,467.20`** | **`$31,005.25`** | **`$7,438.20`** | **`1.1482` / `2.2573` / `1.1453`** | **Holdout Winner (Original Baseline)** |
| **`NQExpShortV1`** | `5c583e39-3201-4df8-8c54-63467454edbe` — [View on dashboard](http://localhost:9000/#/backtest/5c583e39-3201-4df8-8c54-63467454edbe) | 43 (0) | 60.47% | `$29,016.50` | `$27,963.00` | `$7,467.20` | `$28,274.75` | `$7,438.20` | `1.0805` / `2.0760` / `1.0464` | Fails Holdout Net $ (`-$2,716.00`) |
| **`NQExpShortV5`** | `e234a9d9-cc49-4782-8ad2-5cfe503e6398` — [View on dashboard](http://localhost:9000/#/backtest/e234a9d9-cc49-4782-8ad2-5cfe503e6398) | 43 (10) | 60.47% | `$27,688.50` | `$26,685.00` | `$7,467.20` | `$26,996.75` | `$7,438.20` | `1.0507` / `1.9765` / `1.0001` | Fails Holdout Net $ (`-$3,994.00`) |

---

## 5. Key Takeaways & Final Selection

1. **Why the Original Baseline (`NQExpirationOpenShort`) Won Out-of-Sample:**
   - The 3rd-Friday `08:30–10:00 CT` dealer gamma-unwind edge is driven by forced mechanical hedging flows during the SOQ (Special Opening Quotation) print and the first 90 minutes of RTH.
   - Because there are only 12 monthly expirations per year (~60 in 5 years), adding conditional filters (`V1`) or capping right-tail continuation (`V2`) overfits to specific 2018–2022 intraday paths and clips the fattest trend days in `2023–2026`.
2. **Final Selected Strategy:** Retain original **`NQExpirationOpenShort`** (`tasks/out_06/strategy.py`, also mirrored in `tasks/out_06/improve_strategy.py`).
