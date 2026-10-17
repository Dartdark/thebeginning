# Task 07 (`NQLateDayFlow`) — Phase 2 Improvement Report

## 1. Executive Summary & Guardrail Verification
- **Strategy**: `NQLateDayFlow` (`NQ-USD`, 5-minute bars, US Central Time).
- **Design Window**: `2018-01-02` to `2022-12-31` (5 years).
- **Holdout Window**: `2023-01-01` to `2026-10-09` (3.77 years).
- **Cost Model**:
  - Conservative: `$7.25/side` (`$14.50` round-trip commission) + `1 tick` (`$5.00`) slippage per market fill (`2` market fills per trade = `$10.00` slippage, total `$24.50` RT cost).
  - Standard: `$7.25` round-trip commission + `$10.00` slippage = `$17.25` RT cost.
- **Contract Size**: Exactly 1 NQ contract (`$20/pt`, `$5.00/tick`), 0 overnight risk (flat at `14:30 CT`, well before `15:59 CT`).

---

## 2. Pre-Registered Variants Tested on Design Window (`2018–2022`)
*(Analysis Job: `a21802d508ba4f6f90dbae1997ea58a9`)*

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQLateDayBase`** | `fe9fa114-b758-48d3-91a1-17dd61e09ce7` | http://localhost:9000/#/backtest/fe9fa114-b758-48d3-91a1-17dd61e09ce7 | 486 | 53.91% | $46,161.17 | **$34,254.17** | $16,156.00 | 2.12 | **1.6004** | **2.7582** | 0.7260 |
| **`NQLateDayV1`** | `7db0afce-1ea2-482e-93de-56882c472f9f` | http://localhost:9000/#/backtest/7db0afce-1ea2-482e-93de-56882c472f9f | 375 | 53.60% | $35,665.25 | $26,477.75 | **$10,380.33** | **2.55** | 1.3973 | 2.4148 | **0.9025** |
| **`NQLateDayV2`** | `003aee35-3631-40c4-83bf-fc91e25ba6fd` | http://localhost:9000/#/backtest/003aee35-3631-40c4-83bf-fc91e25ba6fd | 472 | 53.81% | $43,102.58 | $31,538.58 | $15,426.08 | 2.04 | 1.5166 | 2.5999 | 0.7148 |
| **`NQLateDayV3`** | `895fd04d-bb35-4fb1-aee4-836c3adc3fbb` | http://localhost:9000/#/backtest/895fd04d-bb35-4fb1-aee4-836c3adc3fbb | 256 | 51.56% | $21,976.33 | $15,704.33 | $14,390.83 | 1.09 | 0.9811 | 1.6815 | 0.3532 |
| **`NQLateDayV4`** | `66471cd9-6133-4c7f-9fdb-8d7f9c9ace84` | http://localhost:9000/#/backtest/66471cd9-6133-4c7f-9fdb-8d7f9c9ace84 | 486 | 54.73% | $42,899.42 | $30,992.42 | $15,440.00 | 2.01 | 1.5784 | 2.5644 | 0.7150 |
| **`NQLateDayV5`** | `1d04806b-6874-4389-9c09-b4d4845f388d` | http://localhost:9000/#/backtest/1d04806b-6874-4389-9c09-b4d4845f388d | 361 | 53.46% | $32,606.67 | $23,762.17 | **$9,650.42** | 2.46 | 1.3021 | 2.2347 | 0.8998 |

---

## 3. Holdout Period (`2023-01-01` to `2026-10-09`) Results

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQLateDayBase`** | `fa1082b3-0d21-41e3-a4f3-25b07ef5e0fb` | http://localhost:9000/#/backtest/fa1082b3-0d21-41e3-a4f3-25b07ef5e0fb | 398 | 57.04% | $54,068.92 | **$44,317.92** | $10,516.67 | 4.21 | 1.5640 | 2.8715 | 1.3983 |
| **`NQLateDayV1`** | `cd4bce44-5904-4450-aa2f-97de1fa80be6` | http://localhost:9000/#/backtest/cd4bce44-5904-4450-aa2f-97de1fa80be6 | 286 | **57.34%** | $47,978.25 | $40,971.25 | **$6,288.50** | **6.52** | **1.6253** | **3.1356** | **2.1790** |
| **`NQLateDayV5`** | `2f8c4692-1aa4-4203-aa92-9f300589eee2` | http://localhost:9000/#/backtest/2f8c4692-1aa4-4203-aa92-9f300589eee2 | 273 | 56.78% | $32,998.25 | $26,309.75 | $8,587.67 | 3.06 | 1.2874 | 2.1607 | 1.2533 |

---

## 4. Acceptance Gate Verdict
- **Strict Guardrail 5 Gate**: The original **`NQLateDayFlow` (`Base`)** is retained as the baseline under strict Guardrail 5 because `V1` generates `$40,971.25` vs `$44,317.92` net profit (due to taking 112 fewer trades).
- **Funded Account Variant**: **`NQLateDayV1`** is an outstanding risk-adjusted improvement for funded accounts:
  - Holdout Max Drawdown is reduced by **-$4,228.17 (-40.2%)** from `$10,516.67` down to `$6,288.50`.
  - Expectancy per trade jumps from `$111.35/trade` to **`$143.26/trade`** (+28.6%).
  - Holdout Sharpe rises from `1.5640` to **`1.6253`**, Sortino from `2.8715` to **`3.1356`**, Calmar from `1.3983` to **`2.1790`**, and NP/DD from `4.21` to **`6.52`**.
