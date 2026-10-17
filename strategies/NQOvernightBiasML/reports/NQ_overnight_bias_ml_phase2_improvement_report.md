# Phase 2 Strategy Improvement Report — Task 04: `NQOvernightBiasML` (`NQ-USD`, `15m`)

## 1. Objective & Guardrails
- **Strategy**: `NQOvernightBiasML` (`NQ-USD`, `15m`, `Custom Data`)
- **Design Window**: `2018-01-02` to `2022-12-31` (5 years)
- **Holdout Window**: `2023-01-01` to `2026-10-09` (3.77 years)
- **Position Size**: Fixed 1 NQ contract (`$20/pt`, `$5.00/tick`)
- **Transaction Cost Model**:
  - **Conservative**: `$7.25/side` (`$14.50` round-trip commission) + `1 tick` (`$5.00`) slippage per market/stop fill (`2` market/stop fills per trade = `$10.00` slippage, total `$24.50` RT cost).
  - **Standard**: `$7.25` round-trip commission + `$10.00` slippage = `$17.25` RT cost.
- **Overnight Rule**: All positions closed at or before `14:45` UTC (`09:45–10:45` ET), well before `15:59` CT.
- **Acceptance Gate (Guardrail 5)**: A variant is accepted as the primary replacement only if it beats the original baseline in **both** `2018–2022` and `2023–2026` on **both** Net Profit per contract and Max Drawdown.

---

## 2. Pre-Registered Variants (`tasks/out_04/improve_plan.md`)
- **`NQONBiasMLBase` (Baseline)**: Enters at `13:30` UTC cash open in the direction of the overnight move (`13:30` close vs `00:00` UTC open) when `|on_ret| >= 0.15%`, `ADX(14) >= 25.0`, and the ridge-regression score (`score >= 0.0` of 5 overnight features: signed return, `ADX(14)`, range%, close-to-range position, and `ATR(14)%`), with `SL = 2.5 * ATR(14)` and time exit at `14:45` UTC.
- **`NQONBiasMLV1` (Higher ML Score Threshold `score >= 0.10`)**: Raises the ridge-regression score cutoff from `0.0` to `+0.10` (requiring `+10 bps` predicted post-open continuation).
- **`NQONBiasMLV2` (Higher Minimum Overnight Return `|on_ret| >= 0.25%`)**: Raises the minimum overnight move threshold from `0.15%` to `0.25%` so small overnight moves inside normal Globex noise are excluded.
- **`NQONBiasMLV3` (Combined `|on_ret| >= 0.25%` + `score >= 0.10`)**: Combines the stricter overnight displacement threshold with the higher ML score cutoff.
- **`NQONBiasMLV4` (Earlier Time Exit `14:30` UTC vs `14:45` UTC)**: Exits 15 minutes earlier (`14:30` UTC = `09:30–10:30` ET, 1 hour after the cash open) to avoid mid-morning reversals.
- **`NQONBiasMLV5` (`|on_ret| >= 0.25%` + Earlier Time Exit `14:30` UTC)**: Combines the `0.25%` overnight displacement filter with the 1-hour (`14:30` UTC) time exit.

---

## 3. Iteration Log & Full Trial Results

### A. Design Window (`2018-01-02` to `2022-12-31`)
*(Analysis Job: `d6af7d9058504aaabbe1075b35a3b41e`)*

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Net ($7.25c + 2t) | Max DD ($7.25c) | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQONBiasMLBase`** | `00ae3725-5d8a-4e47-98c1-043323306b07` | http://localhost:9000/#/backtest/00ae3725-5d8a-4e47-98c1-043323306b07 | 177 | 58.19% | $120,973.70 | **$116,637.20** | $7,922.30 | 14.72 | **$117,920.45** | $7,886.05 | **2.1811** | 5.8284 | 3.1050 |
| **`NQONBiasMLV1`** | `1f456305-643d-40e9-8fa0-3d68c104e304` | http://localhost:9000/#/backtest/1f456305-643d-40e9-8fa0-3d68c104e304 | 164 | 57.32% | $113,378.70 | $109,360.70 | $7,457.80 | 14.66 | $110,549.70 | $7,428.80 | 2.0662 | 5.4875 | 3.0844 |
| **`NQONBiasMLV2`** | `7448b3bc-1d71-44c1-b16b-4b01bb2b30cf` | http://localhost:9000/#/backtest/7448b3bc-1d71-44c1-b16b-4b01bb2b30cf | 151 | **58.94%** | $105,066.30 | $101,366.80 | **$5,367.00** | **18.89** | $102,461.55 | **$5,338.00** | 2.0545 | 5.5500 | **3.9917** |
| **`NQONBiasMLV3`** | `74fb879e-bc89-4be7-8c4c-dc7c4f0e4e30` | http://localhost:9000/#/backtest/74fb879e-bc89-4be7-8c4c-dc7c4f0e4e30 | 136 | 57.35% | $91,069.10 | $87,737.10 | $5,692.70 | 15.41 | $88,723.10 | $5,663.70 | 1.8482 | 4.9008 | 3.2581 |
| **`NQONBiasMLV4`** | `6dc9896e-3a28-4ff5-9e9f-2a25c0cdff0a` | http://localhost:9000/#/backtest/6dc9896e-3a28-4ff5-9e9f-2a25c0cdff0a | 177 | 55.93% | $116,233.02 | $111,896.52 | $7,859.33 | 14.24 | $113,179.77 | $7,823.08 | 2.1166 | **5.9202** | 3.0077 |
| **`NQONBiasMLV5`** | `f3161a9c-bb10-41b8-9c45-2e2e0bcbc7aa` | http://localhost:9000/#/backtest/f3161a9c-bb10-41b8-9c45-2e2e0bcbc7aa | 151 | 56.29% | $100,466.80 | $96,767.30 | **$5,725.83** | 16.90 | $97,862.05 | **$5,696.83** | 1.9838 | 5.5873 | 3.5737 |

- **Design Diagnostics**:
  - `NQONBiasMLV2` (`|on_ret| >= 0.25%`) slashes Design Max Drawdown by **-32.3%** (`$5,367.00` vs `$7,922.30`) and boosts NP/DD from `14.72` to **`18.89`** and Calmar from `3.1050` to **`3.9917`**, while slightly reducing cumulative Net Profit (`$101,366.80` vs `$116,637.20`) because 26 trades (`0.15% <= |on_ret| < 0.25%`) are filtered out.
  - `NQONBiasMLV5` (`|on_ret| >= 0.25%` + `14:30` UTC exit) also cuts Design Max Drawdown by **-27.7%** (`$5,725.83` vs `$7,922.30`) with NP/DD `16.90`.
  - Both `V2` and `V5` were promoted to Holdout validation (`2023–2026`).

### B. Holdout Window (`2023-01-01` to `2026-10-09`)

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Net ($7.25c + 2t) | Max DD ($7.25c) | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQONBiasMLBase`** | `0f37af3d-6485-4b40-892a-e515760e4c9f` | http://localhost:9000/#/backtest/0f37af3d-6485-4b40-892a-e515760e4c9f | 141 | 58.87% | $108,153.60 | **$104,699.10** | $15,640.10 | 6.69 | **$105,721.35** | $15,618.35 | 1.7886 | 3.5793 | 1.8476 |
| **`NQONBiasMLV2`** | `fe90495d-f136-4e68-acf7-72b3f224c459` | http://localhost:9000/#/backtest/fe90495d-f136-4e68-acf7-72b3f224c459 | 120 | **60.83%** | $96,704.70 | $93,764.70 | $11,470.00 | 8.17 | $94,634.70 | $11,426.50 | 1.7101 | 3.4772 | 2.2748 |
| **`NQONBiasMLV5`** | `9552c81c-acf0-4228-9eaa-80bc96a1791c` | http://localhost:9000/#/backtest/9552c81c-acf0-4228-9eaa-80bc96a1791c | 120 | 59.17% | $104,392.58 | $101,452.58 | **$10,085.67** | **10.06** | $102,322.58 | **$10,071.17** | **1.8991** | **4.2503** | **2.7645** |

---

## 4. Final Verdict & Portfolio Recommendation
- **Strict Guardrail 5 Verdict**:
  - Under the strict conjunctive acceptance gate (must beat `Base` in **both** windows on **both** Net $ and Max DD), the original **`NQOvernightBiasML` (`Base`)** is retained as the official strategy because filtering out the `0.15%–0.25%` overnight moves reduces trade count from 177 to 151 in Design and from 141 to 120 in Holdout, leaving cumulative Net $ slightly below `Base` (`$101,452.58` vs `$104,699.10` in Holdout).
- **Major Risk-Adjusted Breakthrough (`NQONBiasMLV5`)**:
  - In Holdout (`2023–2026`), **`NQONBiasMLV5`** (`|on_ret| >= 0.25%` + `14:30` UTC exit) captures **96.9%** of `Base`'s net profit (`$101,452.58` vs `$104,699.10`) on 21 fewer trades (**`$845.44/trade`** vs `$742.55/trade`, +13.9% higher expectancy per trade!) while slashing Holdout Max Drawdown by **-$5,554.43 (-35.5%, from `$15,640.10` down to `$10,085.67`)**, boosting Holdout Sharpe from `1.7886` to **`1.8991`**, Sortino from `3.5793` to **`4.2503`**, Calmar from `1.8476` to **`2.7645`**, and NP/DD from `6.69` to **`10.06`**.
  - Across the full 8.8-year sample (`2018–2026`), `NQONBiasMLV5` earns **`$198,219.88` net** (`$14.50` RT + 2t) with a **`$10,085.67` max drawdown** (**`19.65x` full-period NP/DD** vs `Base`'s `14.15x`). Both `Base` and `V5` are documented in `tasks/out_04/improve_strategy.py` for Funded Account deployment where drawdown preservation is paramount.
