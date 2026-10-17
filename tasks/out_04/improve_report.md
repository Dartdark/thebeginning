# Task 04 (`NQOvernightBiasML`) — Phase 2 Improvement Report

## 1. Executive Summary & Guardrail Verification
- **Strategy**: `NQOvernightBiasML` (`NQ-USD`, 15-minute bars, US Central Time).
- **Design Window**: `2018-01-02` to `2022-12-31` (5 years).
- **Holdout Window**: `2023-01-01` to `2026-10-09` (3.77 years).
- **Cost Model**:
  - Conservative: `$7.25/side` (`$14.50` round-trip commission) + `1 tick` (`$5.00`) slippage per stop/market fill (`$10.00` round-trip slippage, total `$24.50` RT cost).
  - Standard: `$7.25` round-trip commission + `$10.00` slippage = `$17.25` RT cost.
- **Contract Size**: Exactly 1 NQ contract (`$20/pt`, `$5.00/tick`), 0 overnight risk (flat at `14:30 CT`, well before `15:59 CT`).

---

## 2. Pre-Registered Variants Tested on Design Window (`2018–2022`)

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQONBiasMLBase`** | `00ae3725-5d8a-4e47-98c1-043323306b07` | http://localhost:9000/#/backtest/00ae3725-5d8a-4e47-98c1-043323306b07 | 177 | 58.19% | $120,973.70 | **$116,637.20** | $7,922.30 | 14.72 | **2.1811** | 5.8284 | 3.1050 |
| **`NQONBiasMLV1`** | `1f456305-643d-40e9-8fa0-3d68c104e304` | http://localhost:9000/#/backtest/1f456305-643d-40e9-8fa0-3d68c104e304 | 164 | 57.32% | $113,378.70 | $109,360.70 | $7,457.80 | 14.66 | 2.0662 | 5.4875 | 3.0844 |
| **`NQONBiasMLV2`** | `7448b3bc-1d71-44c1-b16b-4b01bb2b30cf` | http://localhost:9000/#/backtest/7448b3bc-1d71-44c1-b16b-4b01bb2b30cf | 151 | **58.94%** | $105,066.30 | $101,366.80 | **$5,367.00** | **18.89** | 2.0545 | 5.5500 | **3.9917** |
| **`NQONBiasMLV3`** | `74fb879e-bc89-4be7-8c4c-dc7c4f0e4e30` | http://localhost:9000/#/backtest/74fb879e-bc89-4be7-8c4c-dc7c4f0e4e30 | 136 | 57.35% | $91,069.10 | $87,737.10 | $5,692.70 | 15.41 | 1.8482 | 4.9008 | 3.2581 |
| **`NQONBiasMLV4`** | `6dc9896e-3a28-4ff5-9e9f-2a25c0cdff0a` | http://localhost:9000/#/backtest/6dc9896e-3a28-4ff5-9e9f-2a25c0cdff0a | 177 | 55.93% | $116,233.02 | $111,896.52 | $7,859.33 | 14.24 | 2.1166 | **5.9202** | 3.0077 |
| **`NQONBiasMLV5`** | `f3161a9c-bb10-41b8-9c45-2e2e0bcbc7aa` | http://localhost:9000/#/backtest/f3161a9c-bb10-41b8-9c45-2e2e0bcbc7aa | 151 | 56.29% | $100,466.80 | $96,767.30 | **$5,725.83** | 16.90 | 1.9838 | 5.5873 | 3.5737 |

- **Design Diagnostics**:
  - `V2` (symmetric regime score `today_score >= 0.03`) dramatically compressed Max Drawdown by **-32.3%** (`$5,367.00` vs `$7,922.30`), elevating NP/DD to `18.89` and Calmar to `3.9917`.
  - `V5` (`V2` + `V4` combined) also cut Max Drawdown by **-27.7%** to `$5,725.83`.
  - Both were promoted to Holdout testing.

---

## 3. Holdout Period (`2023-01-01` to `2026-10-09`) Results

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQONBiasMLBase`** | `0f37af3d-6485-4b40-892a-e515760e4c9f` | http://localhost:9000/#/backtest/0f37af3d-6485-4b40-892a-e515760e4c9f | 141 | 58.87% | $108,153.60 | **$104,699.10** | $15,640.10 | 6.69 | 1.7886 | 3.5793 | 1.8476 |
| **`NQONBiasMLV2`** | `fe90495d-f136-4e68-acf7-72b3f224c459` | http://localhost:9000/#/backtest/fe90495d-f136-4e68-acf7-72b3f224c459 | 120 | **60.83%** | $96,704.70 | $93,764.70 | $11,470.00 | 8.17 | 1.7101 | 3.4772 | 2.2748 |
| **`NQONBiasMLV5`** | `9552c81c-acf0-4228-9eaa-80bc96a1791c` | http://localhost:9000/#/backtest/9552c81c-acf0-4228-9eaa-80bc96a1791c | 120 | 59.17% | $104,392.58 | $101,452.58 | **$10,085.67** | **10.06** | **1.8991** | **4.2503** | **2.7645** |

---

## 4. Acceptance Gate Verdict
- **Strict Guardrail 5 Gate**: The original **`NQOvernightBiasML` (`Base`)** is retained as the default code because filtering lower-conviction short setups reduced cumulative trade count by 21 in holdout, generating `$101,452.58` vs `$104,699.10` net profit.
- **Funded Account Variant**: **`NQONBiasMLV5`** is the superior variant for funded accounts:
  - Holdout Max Drawdown is reduced by **-$5,554.43 (-35.5%)** from `$15,640.10` down to `$10,085.67`.
  - Expectancy jumps from `$742.55/trade` to **`$845.44/trade`** (+13.9%).
  - Holdout Sharpe rises from `1.7886` to **`1.8991`**, Sortino from `3.5793` to **`4.2503`**, and Calmar from `1.8476` to **`2.7645`**.
