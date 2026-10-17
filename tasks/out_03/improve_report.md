# Phase 2 Strategy Improvement Report — Task 03: `NQOvernightBiasADX30` (`NQ-USD` `15m`)

## 1. Objective & Guardrails
- **Strategy**: `NQOvernightBiasADX30` (`NQ-USD`, `15m` bars, CME E-mini Nasdaq-100 Futures, `$20.00/point`, tick size `0.25 pt = $5.00`)
- **Design Window**: `2018-01-02` to `2022-12-31` (5 years)
- **Holdout Window**: `2023-01-01` to `2026-10-09` (3.77 years)
- **Transaction Cost Model**:
  - **Strict Brief ($14.50 RT)**: `$7.25/side` (`$14.50` round-trip commission) + `1 tick` (`$5.00`) slippage per fill (`$24.50` round-trip per contract).
  - **Standard Apex ($7.25 RT)**: `$3.625/side` (`$7.25` round-trip commission) + `1 tick` (`$5.00`) slippage per fill (`$17.25` round-trip per contract).
- **Acceptance Gate**: Must beat original (`Base`) in **BOTH** `2018–2022` and `2023–2026` on **BOTH** Net $ per contract AND Max Drawdown, flat by `15:59 CT`, max 1 contract (`1.0` unit).

---

## 2. Pre-Registered Variants (`improve_plan.md`)
1. **`NQONBiasADX30Base` (Baseline)**: Tracks Globex overnight range (`23:00–08:30 CT`) and `08:30–08:45 CT` RTH opening range (`or_high`, `or_low`). If `08:30 CT` open is in top third (`>= 0.6667`) of overnight range (`bias = +1`) or bottom third (`<= 0.3333`, `bias = -1`), enters 1 contract on `or_high`/`or_low` breakout when `ADX(14) > 30.0` before `14:00 CT` (`11:00 CT` early close). `SL = 0.25 * ATR15`, `TP = 0.75 * ATR15` (`3.0R`), time exit `14:30 CT` (`11:30 CT` early close).
2. **`NQONBiasADX30V1` (Higher Trend Conviction `ADX(14) > 32.0`)**: Filters out marginal ADX trend readings (`30.0–32.0`) to reduce false breakouts.
3. **`NQONBiasADX30V2` (Morning Entry Cutoff `11:00 CT`)**: Restricts new breakout entries to the morning institutional trend window (`08:45–11:00 CT`), avoiding midday breakout traps.
4. **`NQONBiasADX30V3` (Stricter Overnight Extremes `>= 0.75` / `<= 0.25`)**: Requires the `08:30 CT` RTH open to sit in the top/bottom quartile of the overnight range.
5. **`NQONBiasADX30V4` (Closer Profit Target `TP = 0.50 * ATR15` / `2.0R`)**: Reduces the profit target from `3.0R` (`0.75 * ATR15`) to `2.0R` (`0.50 * ATR15`) to lock in gains before midday reversals.
6. **`NQONBiasADX30V5` (Combined V1 + V2)**: `ADX(14) > 32.0` + `11:00 CT` entry cutoff.

---

## 3. Design Window Results (`2018-01-02` to `2022-12-31`)

| Variant | Session ID & Dashboard URL | Trades | Win Rate ($14.50c) | Gross P&L | Net P&L ($14.50c) | Max DD ($14.50c) | NP/DD ($14.50c) | Net P&L ($7.25c) | Max DD ($7.25c) | Sharpe / Sortino / Calmar | Design Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Base`** | `32bfbf06-67e8-41a1-848d-961b6bfbe908`<br>Dashboard: http://localhost:9000/#/backtest/32bfbf06-67e8-41a1-848d-961b6bfbe908 | 361 | 50.97% | **$132,289.58** | **$123,445.08** | $6,798.75 | **18.16** | **$126,062.33** | $6,487.00 | **2.0573 / 4.5791 / 4.4360** | **Best Net $, NP/DD, Sharpe** |
| **`V1`** | `a3091c3e-d265-43dd-998b-a37a3178f9fc`<br>Dashboard: http://localhost:9000/#/backtest/a3091c3e-d265-43dd-998b-a37a3178f9fc | 335 | 51.04% | $125,541.33 | $117,333.83 | **$6,575.67** | 17.84 | $119,762.58 | **$6,388.58** | 1.9774 / 4.4039 / 4.2095 | Slightly lower DD (-$223), lower Net $ |
| **`V2`** | `2b3602dd-caaa-4fe2-bc17-fa7c95f5d8d7`<br>Dashboard: http://localhost:9000/#/backtest/2b3602dd-caaa-4fe2-bc17-fa7c95f5d8d7 | 267 | 53.18% | $91,536.42 | $84,994.92 | **$5,799.75** | 14.65 | $86,930.67 | **$5,727.25** | 1.7167 / 3.6455 / 3.3006 | Lower DD (-$999), higher WR; test Holdout |
| **`V3`** | `1049381d-f28a-4574-afe3-1d8272b1a78f`<br>Dashboard: http://localhost:9000/#/backtest/1049381d-f28a-4574-afe3-1d8272b1a78f | 286 | 49.30% | $102,834.50 | $95,827.50 | $7,486.42 | 12.80 | $97,901.00 | $7,341.42 | 1.7626 / 4.0005 / 2.9448 | Rejected |
| **`V4`** | `1b5f3fc1-0715-42c2-babd-db9e95af1860`<br>Dashboard: http://localhost:9000/#/backtest/1b5f3fc1-0715-42c2-babd-db9e95af1860 | 361 | 51.80% | $107,867.58 | $99,953.08 | $7,508.92 | 13.31 | $102,570.33 | $7,197.17 | 1.9113 / 3.7597 / 3.1931 | Rejected (3.0R target superior to 2.0R) |
| **`V5`** | `a227e47a-91c9-4988-b44f-4d5d491d80e0`<br>Dashboard: http://localhost:9000/#/backtest/a227e47a-91c9-4988-b44f-4d5d491d80e0 | 249 | **53.41%** | $87,531.50 | $81,431.00 | **$5,575.08** | 14.61 | $83,236.25 | **$5,553.33** | 1.6600 / 3.5389 / 3.1902 | **Lowest Design DD (-$1,223.67)**; test Holdout |

---

## 4. Holdout Window Validation (`2023-01-01` to `2026-10-09`)

| Variant | Session ID & Dashboard URL | Trades | Win Rate ($14.50c) | Gross P&L | Net P&L ($14.50c) | Max DD ($14.50c) | NP/DD ($14.50c) | Net P&L ($7.25c) | Max DD ($7.25c) | Sharpe / Sortino / Calmar | Holdout Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Base`** | `5cc12f34-5f0e-4c5b-95f5-3a1d4d1f2852`<br>Dashboard: http://localhost:9000/#/backtest/5cc12f34-5f0e-4c5b-95f5-3a1d4d1f2852 | 308 | **51.30%** | **$135,292.25** | **$127,746.25** | **$13,652.00** | **9.36** | **$129,979.25** | **$13,608.50** | **1.8524 / 3.7682 / 2.6719** | **Retained Winner (Dominates Net $ and DD)** |
| **`V2`** | `3832589a-183b-4501-b9a0-5e0eb85a1758`<br>Dashboard: http://localhost:9000/#/backtest/3832589a-183b-4501-b9a0-5e0eb85a1758 | 236 | 51.27% | $80,408.58 | $74,626.58 | $20,345.00 | 3.67 | $76,337.58 | $20,185.50 | 1.3700 / 2.5173 / 1.0815 | Rejected on Holdout |
| **`V5`** | `c12652fe-371b-451c-9a61-d4fcd7acd6b0`<br>Dashboard: http://localhost:9000/#/backtest/c12652fe-371b-451c-9a61-d4fcd7acd6b0 | 211 | 49.29% | $71,966.83 | $66,797.33 | $16,178.67 | 4.13 | $68,327.08 | $16,055.42 | 1.2770 / 2.3799 / 1.2157 | Rejected on Holdout |

---

## 5. Final Verdict
- **Retained Strategy**: **Original `NQOvernightBiasADX30` (`Base`)**.\n- Across both `2018–2022` (`+$123,445.08` net at `$14.50` RT comm + `$10` slip, Max DD `$6,798.75`, NP/DD `18.16`, Sharpe `2.06`) and `2023–2026` (`+$127,746.25` net, Max DD `$13,652.00`, NP/DD `9.36`, Sharpe `1.85`), the original `ADX > 30` + `08:45–14:00 CT` entry window + `3.0R` (`0.75 * ATR15` TP / `0.25 * ATR15` SL) parameters outperform all five variants on both total net dollars and out-of-sample drawdown.
