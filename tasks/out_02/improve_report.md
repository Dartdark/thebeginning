# Phase 2 Strategy Improvement Report — Task 02: `NQVaultBreak` (`NQ-USD` `30m`)

## 1. Objective & Guardrails
- **Strategy**: `NQVaultBreak` (`NQ-USD`, `30m` bars, CME E-mini Nasdaq-100 Futures, `$20.00/point`, tick size `0.25 pt = $5.00`)
- **Design Window**: `2018-01-02` to `2022-12-31` (5 years)
- **Holdout Window**: `2023-01-01` to `2026-10-09` (3.77 years)
- **Transaction Cost Model**:
  - **Strict Brief ($14.50 RT)**: `$7.25/side` (`$14.50` round-trip commission) + `1 tick` (`$5.00`) slippage per market/stop fill (`$5.00` total slippage when Take-Profit limit order fills; `$10.00` total slippage when Stop-Loss or 14:30 CT time-exit fills). Total round-trip cost: `$19.50` on limit TP exits, `$24.50` on stop/time exits.
  - **Standard Apex ($7.25 RT)**: `$3.625/side` (`$7.25` round-trip commission) + same slippage (`$12.25` on limit TP exits, `$17.25` on stop/time exits).
- **Acceptance Gate**: Must beat original (`Base`) in **BOTH** `2018–2022` and `2023–2026` on **BOTH** Net $ per contract AND Max Drawdown, flat by `15:59 CT`, max 1 contract (`1.0` unit).

---

## 2. Pre-Registered Variants (`improve_plan.md`)
1. **`NQVaultBreakBase` (Baseline)**: Long `1` NQ at `30m` bar close in `[10:00, 14:30)` CT (`[10:00, 11:00)` early close) when `close > session_open + 0.30 * ATR15` and `close > session_vwap`, max 3 trades/day, `TP = +40 pts` (`+$800`), `SL = -75 pts` (`-$1,500`), flatten at `14:30 CT` (`11:30 CT` early close).
2. **`NQVaultBreakV1` (Single-Shot Entry `trades_taken_today < 1`)**: Eliminates re-entries after a stop-out or early target fill to avoid whipsaw/chop days.
3. **`NQVaultBreakV2` (Earlier Entry Cutoff `12:30 CT` instead of `14:00 CT`)**: Requires at least 2.0 hours before the `14:30 CT` time exit so the `+40 pt` target has sufficient RTH runway before forced liquidation.
4. **`NQVaultBreakV3` (Volatility-Scaled Bracket `TP = 0.15 * ATR15`, `SL = 0.25 * ATR15`)**: Scales the fixed `+40 / -75 pt` bracket to the 15-day Daily True Range (`ATR15`).
5. **`NQVaultBreakV4` (Bullish Trigger Bar Confirmation `b_close > b_open`)**: Requires the `30m` breakout bar itself to close green (`close > open`), filtering out bars that spiked up intrabar and sold off before the `30m` close.
6. **`NQVaultBreakV5` (Combined V1 + V2 + V3)**: Single trade/day + `12:30 CT` entry cutoff + `0.15x / 0.25x ATR15` bracket.

---

## 3. Design Window Results (`2018-01-02` to `2022-12-31`)

| Variant | Session ID & Dashboard URL | Trades (TP Limit) | Win Rate ($14.50c) | Gross P&L | Net P&L ($14.50c) | Max DD ($14.50c) | NP/DD ($14.50c) | Net P&L ($7.25c) | Max DD ($7.25c) | Sharpe / Sortino / Calmar | Design Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Base`** | `9d26a1da-a6f3-42a1-b8c7-4662ae42978a`<br>Dashboard: http://localhost:9000/#/backtest/9d26a1da-a6f3-42a1-b8c7-4662ae42978a | 864 (373) | 64.00% | $90,645.00 | $71,342.00 | $9,198.50 | 7.76 | $77,606.00 | $8,959.25 | 1.7498 / 2.7639 / 2.3386 | Baseline |
| **`V1`** | `32abeefa-39da-4eda-b78c-cfe43ec6e954`<br>Dashboard: http://localhost:9000/#/backtest/32abeefa-39da-4eda-b78c-cfe43ec6e954 | 534 (223) | 63.11% | $50,555.00 | $38,587.00 | $10,223.50 | 3.77 | $42,458.50 | $9,839.25 | 1.2906 / 1.7100 / 1.1188 | Rejected (2nd/3rd entries add +$32.7k net) |
| **`V2`** | `f6c6b915-eb9a-495f-b1a4-64d4f1335aef`<br>Dashboard: http://localhost:9000/#/backtest/f6c6b915-eb9a-495f-b1a4-64d4f1335aef | 685 (330) | **65.99%** | $82,955.00 | $67,822.50 | **$9,162.00** | 7.40 | $72,788.75 | **$8,901.00** | 1.7035 / 2.6580 / **2.3495** | Lower DD & higher WR/Calmar; test Holdout |
| **`V3`** | `6d5cae8b-874d-4d31-a776-b788e4a49166`<br>Dashboard: http://localhost:9000/#/backtest/6d5cae8b-874d-4d31-a776-b788e4a49166 | 862 (178) | 60.56% | $63,466.17 | $43,237.17 | $11,875.12 | 3.64 | $49,486.67 | $11,585.12 | 1.0366 / 1.5214 / 1.2366 | Rejected (ATR bracket underperforms fixed +40/-75) |
| **`V4`** | `3b2dc397-6869-4bbe-8482-224fd457c66d`<br>Dashboard: http://localhost:9000/#/backtest/3b2dc397-6869-4bbe-8482-224fd457c66d | 810 (348) | 64.07% | **$102,745.00** | **$84,640.00** | **$8,844.50** | **9.57** | **$90,512.50** | **$8,547.25** | **2.1392 / 3.5057 / 2.6043** | **Design Winner (Beats Base on Net $ AND Max DD)** |
| **`V5`** | `a54c16bb-0ff4-4e02-a87f-da712568ba4f`<br>Dashboard: http://localhost:9000/#/backtest/a54c16bb-0ff4-4e02-a87f-da712568ba4f | 534 (130) | 62.55% | $44,791.98 | $32,358.98 | $14,067.95 | 2.30 | $36,230.48 | $13,683.70 | 0.8505 / 1.1058 / 0.6974 | Rejected |

---

## 4. Holdout Window Validation (`2023-01-01` to `2026-10-09`)

| Variant | Session ID & Dashboard URL | Trades (TP Limit) | Win Rate ($14.50c) | Gross P&L | Net P&L ($14.50c) | Max DD ($14.50c) | NP/DD ($14.50c) | Net P&L ($7.25c) | Max DD ($7.25c) | Sharpe / Sortino / Calmar | Holdout Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Base`** | `294ab48e-9ee7-438b-901f-2b705bb59f23`<br>Dashboard: http://localhost:9000/#/backtest/294ab48e-9ee7-438b-901f-2b705bb59f23 | 880 (525) | 67.61% | **$100,275.00** | **$81,340.00** | $16,803.00 | 4.84 | **$87,720.00** | $16,194.00 | **1.8675** / 2.9360 / **2.1094** | **Retained Baseline** |
| **`V4`** | `ab81863e-3ad2-47e8-a9eb-d6114761e652`<br>Dashboard: http://localhost:9000/#/backtest/ab81863e-3ad2-47e8-a9eb-d6114761e652 | 826 (471) | 66.71% | $80,110.00 | $62,228.00 | **$15,309.50** | 4.06 | $68,216.50 | **$14,649.75** | 1.5614 / 2.4176 / 1.6018 | Lower DD (-$1,493.50), but lower Net $ |
| **`V2`** | `12becaa9-6cab-41ac-adde-e2300002bda3`<br>Dashboard: http://localhost:9000/#/backtest/12becaa9-6cab-41ac-adde-e2300002bda3 | 707 (458) | **69.31%** | $89,815.00 | $74,783.50 | **$13,638.50** | **5.48** | $79,909.25 | **$13,181.75** | 1.8260 / **2.9386** / 2.0998 | **Lowest DD (-$3,164.50) & Highest NP/DD (5.48)**, but lower Net $ |

---

## 5. Final Verdict
- **Strict Acceptance Gate**: Under Guardrail 5 (which requires beating `Base` on **BOTH** Net $ AND Max Drawdown in **BOTH** `2018–2022` and `2023–2026`), **Original `NQVaultBreak` (`Base`) is retained**:
  - `V4` (`b_close > b_open`) improved both Net $ (`$84,640` vs `$71,342`) and Max DD (`$8,844.50` vs `$9,198.50`) in `2018–2022` and reduced Holdout Max DD (`$15,309.50` vs `$16,803.00`), but reduced Holdout Net $ (`$62,228.00` vs `$81,340.00`).
  - `V2` (stopping new entries at `12:30 CT`) reduced Max DD in both windows (`$9,162.00` Design; **`$13,638.50` Holdout vs `$16,803.00` Base**) and raised Holdout NP/DD from `4.84` to **`5.48`** (and Win Rate to **`69.31%`**), making `V2` an attractive drawdown-reduction option for trailing-drawdown prop accounts, though with `-8.1%` lower total net dollars.
