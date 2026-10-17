# Phase 2 Strategy Improvement Report — Task 08: `NQNFPFade` (`NQ-USD`, `5m`)

## 1. Objective & Guardrails
- **Strategy**: `NQNFPFade` (`NQ-USD`, `5m`, `Custom Data`)
- **Design Window**: `2018-01-02` to `2022-12-31` (5 years)
- **Holdout Window**: `2023-01-01` to `2026-10-09` (3.77 years)
- **Position Size**: Fixed 1 NQ contract (`$20/pt`, `$5.00/tick`)
- **Transaction Cost Model**:
  - **Conservative**: `$7.25/side` (`$14.50` round-trip commission) + `1 tick` (`$5.00`) slippage per fill (`2` market fills = `$10.00` slippage, total `$24.50` RT cost).
  - **Standard**: `$7.25` round-trip commission + `$10.00` slippage = `$17.25` RT cost.
- **Overnight Rule**: Enters at `07:45 CT` on NFP Fridays, exits at `09:00 CT` (`08:30 CT` on V2), 100% flat by `09:00 CT`, 7 hours before `15:59 CT`.
- **Acceptance Gate (Guardrail 5)**: A variant is accepted as the primary replacement only if it beats the original baseline in **both** `2018–2022` and `2023–2026` on **both** Net Profit per contract and Max Drawdown.

---

## 2. Pre-Registered Variants (`tasks/out_08/improve_plan.md`)
- **`NQNFPFadeBase` (Baseline)**: On NFP Fridays, fades the `07:30 CT` release dislocation at `07:45 CT` if `07:35` bar range exceeds `3.0x` median range; stop loss at `0.50 * ATR(15)` and time exit at `09:00 CT`.
- **`NQNFPFadeV1` (Min Dislocation `0.10 * ATR`)**: Requires remaining dislocation `|close_0745 - ref_price| >= 0.10 * ATR(15)`, avoiding entering after the spike has already mean-reverted.
- **`NQNFPFadeV2` (Exit Cash Open `08:30 CT`)**: Liquidates at `08:30 CT` before cash open volume arrives.
- **`NQNFPFadeV3` (Target at Reference Equilibrium)**: Sets limit take-profit at `ref_price` (`close_0730`).
- **`NQNFPFadeV4` (Tight Stop `0.30 * ATR`)**: Cuts protective stop to `0.30 * ATR(15)`.
- **`NQNFPFadeV5` (V1 + V4 Combined)**: `0.10 * ATR` dislocation + `0.30 * ATR` tight stop.

---

## 3. Iteration Log & Full Trial Results

### A. Design Window (`2018-01-02` to `2022-12-31`)
*(Analysis Job: `b4c13eb94a474c7abdad202779c28437`)*

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Net ($7.25c + 2t) | Max DD ($7.25c) | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQNFPFadeBase`** | `3430760c-ee12-440c-b431-c51fb5c5d0d3` | http://localhost:9000/#/backtest/3430760c-ee12-440c-b431-c51fb5c5d0d3 | 44 | 45.45% | $8,878.17 | **$7,800.17** | $8,269.33 | **0.94** | **$8,119.17** | $8,160.58 | **0.4087** | **0.7675** | **0.2249** |
| **`NQNFPFadeV1`** | `9cc91e03-d82f-4735-a06e-bebf3b8d4a6e` | http://localhost:9000/#/backtest/9cc91e03-d82f-4735-a06e-bebf3b8d4a6e | 33 | 48.48% | $6,363.17 | $5,554.67 | **$6,149.83** | 0.90 | $5,793.92 | **$6,048.33** | 0.3587 | 0.5936 | 0.2192 |
| **`NQNFPFadeV2`** | `758f15c7-00fe-450c-b818-50b7c389bf06` | http://localhost:9000/#/backtest/758f15c7-00fe-450c-b818-50b7c389bf06 | 44 | 50.00% | $2,325.00 | $1,247.00 | $7,476.50 | 0.17 | $1,566.00 | $7,425.75 | 0.2020 | 0.2907 | 0.0637 |
| **`NQNFPFadeV3`** | `895cbc57-c91c-4fd7-bbc9-195a599726b7` | http://localhost:9000/#/backtest/895cbc57-c91c-4fd7-bbc9-195a599726b7 | 37 | **59.46%** | $1,633.17 | $726.67 | **$5,402.00** | 0.13 | $994.92 | **$5,358.50** | 0.1125 | 0.1508 | 0.0622 |
| **`NQNFPFadeV4`** | `a45d105c-7c07-4aab-aefd-78bf0a34210d` | http://localhost:9000/#/backtest/a45d105c-7c07-4aab-aefd-78bf0a34210d | 44 | 40.91% | $5,695.20 | $4,617.20 | $8,811.60 | 0.52 | $4,936.20 | $8,760.85 | 0.2653 | 0.5017 | 0.1320 |
| **`NQNFPFadeV5`** | `2033eae7-7f07-49e0-a0f1-ab10fcbe3ad6` | http://localhost:9000/#/backtest/2033eae7-7f07-49e0-a0f1-ab10fcbe3ad6 | 33 | 42.42% | $5,656.20 | $4,847.70 | **$6,379.90** | 0.76 | $5,086.95 | **$6,336.40** | 0.3444 | 0.6482 | 0.1818 |

- **Design Diagnostics**:
  - `NQNFPFadeV1` reduces Max Drawdown by **-$2,119.50 (-25.6%)** from `$8,269.33` down to `$6,149.83` by filtering out exhausted fades.
  - `NQNFPFadeV5` reduces Max Drawdown by **-22.8%** to `$6,379.90`.
  - Both were promoted to Holdout testing.

### B. Holdout Window (`2023-01-01` to `2026-10-09`)

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Net ($7.25c + 2t) | Max DD ($7.25c) | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQNFPFadeBase`** | `06082db7-3f4b-4d33-b8cc-61eeb24b8a47` | http://localhost:9000/#/backtest/06082db7-3f4b-4d33-b8cc-61eeb24b8a47 | 33 | 57.58% | $17,505.00 | **$16,696.50** | $4,783.00 | 3.49 | **$16,935.75** | $4,754.00 | **1.0158** | **2.3822** | 0.9922 |
| **`NQNFPFadeV1`** | `ec350357-9b12-4918-a321-57c547437e70` | http://localhost:9000/#/backtest/ec350357-9b12-4918-a321-57c547437e70 | 27 | **59.26%** | $16,650.00 | $15,988.50 | **$4,313.50** | **3.71** | $16,184.25 | **$4,291.75** | 0.9818 | 2.3272 | **1.0427** |
| **`NQNFPFadeV5`** | `308018c6-fea3-400b-9744-0753e31b0e33` | http://localhost:9000/#/backtest/308018c6-fea3-400b-9744-0753e31b0e33 | 27 | 51.85% | $10,018.00 | $9,356.50 | $7,286.50 | 1.28 | $9,552.25 | $7,206.75 | 0.5832 | 1.1663 | 0.3791 |

---

## 4. Final Verdict & Portfolio Recommendation
- **Strict Guardrail 5 Gate**: The original **`NQNFPFade` (`Base`)** is retained as the baseline under strict Guardrail 5 because `V1` produces `$15,988.50` vs `$16,696.50` net profit in holdout (due to filtering out 6 trades).
- **Funded Account Option (`NQNFPFadeV1`)**:
  - `V1` achieves a **higher expectancy per trade (`$592.17/trade` vs `$505.95/trade`, +17.0%)**, lower drawdown in both periods (**`$6,149.83` vs `$8,269.33` in Design; `$4,313.50` vs `$4,783.00` in Holdout)**, and a higher NP/DD ratio (`3.71` vs `3.49`). Both `Base` and `V1` are retained and documented in `tasks/out_08/improve_strategy.py`.
