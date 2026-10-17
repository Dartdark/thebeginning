# Task 08 (`NQNFPFade`) — Phase 2 Improvement Report

## 1. Executive Summary & Guardrail Verification
- **Strategy**: `NQNFPFade` (`NQ-USD`, 5-minute bars, US Central Time).
- **Design Window**: `2018-01-02` to `2022-12-31` (5 years).
- **Holdout Window**: `2023-01-01` to `2026-10-09` (3.77 years).
- **Cost Model**:
  - Conservative: `$7.25/side` (`$14.50` round-trip commission) + `1 tick` (`$5.00`) slippage per fill (`2` market fills = `$10.00` slippage, total `$24.50` RT cost).
  - Standard: `$7.25` round-trip commission + `$10.00` slippage = `$17.25` RT cost.
- **Contract Size**: Exactly 1 NQ contract (`$20/pt`, `$5.00/tick`), 0 overnight risk (flat at `09:00 CT`, well before `15:59 CT`).

---

## 2. Pre-Registered Variants Tested on Design Window (`2018–2022`)
*(Analysis Job: `b4c13eb94a474c7abdad202779c28437`)*

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQNFPFadeBase`** | `3430760c-ee12-440c-b431-c51fb5c5d0d3` | http://localhost:9000/#/backtest/3430760c-ee12-440c-b431-c51fb5c5d0d3 | 44 | 45.45% | $8,878.17 | **$7,800.17** | $8,269.33 | **0.94** | **0.4087** | **0.7675** | **0.2249** |
| **`NQNFPFadeV1`** | `9cc91e03-d82f-4735-a06e-bebf3b8d4a6e` | http://localhost:9000/#/backtest/9cc91e03-d82f-4735-a06e-bebf3b8d4a6e | 33 | 48.48% | $6,363.17 | $5,554.67 | **$6,149.83** | 0.90 | 0.3587 | 0.5936 | 0.2192 |
| **`NQNFPFadeV2`** | `758f15c7-00fe-450c-b818-50b7c389bf06` | http://localhost:9000/#/backtest/758f15c7-00fe-450c-b818-50b7c389bf06 | 44 | 50.00% | $2,325.00 | $1,247.00 | $7,476.50 | 0.17 | 0.2020 | 0.2907 | 0.0637 |
| **`NQNFPFadeV3`** | `895cbc57-c91c-4fd7-bbc9-195a599726b7` | http://localhost:9000/#/backtest/895cbc57-c91c-4fd7-bbc9-195a599726b7 | 37 | **59.46%** | $1,633.17 | $726.67 | **$5,402.00** | 0.13 | 0.1125 | 0.1508 | 0.0622 |
| **`NQNFPFadeV4`** | `a45d105c-7c07-4aab-aefd-78bf0a34210d` | http://localhost:9000/#/backtest/a45d105c-7c07-4aab-aefd-78bf0a34210d | 44 | 40.91% | $5,695.20 | $4,617.20 | $8,811.60 | 0.52 | 0.2653 | 0.5017 | 0.1320 |
| **`NQNFPFadeV5`** | `2033eae7-7f07-49e0-a0f1-ab10fcbe3ad6` | http://localhost:9000/#/backtest/2033eae7-7f07-49e0-a0f1-ab10fcbe3ad6 | 33 | 42.42% | $5,656.20 | $4,847.70 | **$6,379.90** | 0.76 | 0.3444 | 0.6482 | 0.1818 |

---

## 3. Holdout Period (`2023-01-01` to `2026-10-09`) Results

| Variant | Session ID | Dashboard URL | Trades | Win Rate | Gross ($) | Net ($14.50c + 2t) | Max DD ($14.50c) | NP/DD | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`NQNFPFadeBase`** | `06082db7-3f4b-4d33-b8cc-61eeb24b8a47` | http://localhost:9000/#/backtest/06082db7-3f4b-4d33-b8cc-61eeb24b8a47 | 33 | 57.58% | $17,505.00 | **$16,696.50** | $4,783.00 | 3.49 | **1.0158** | **2.3822** | 0.9922 |
| **`NQNFPFadeV1`** | `ec350357-9b12-4918-a321-57c547437e70` | http://localhost:9000/#/backtest/ec350357-9b12-4918-a321-57c547437e70 | 27 | **59.26%** | $16,650.00 | $15,988.50 | **$4,313.50** | **3.71** | 0.9818 | 2.3272 | **1.0427** |
| **`NQNFPFadeV5`** | `308018c6-fea3-400b-9744-0753e31b0e33` | http://localhost:9000/#/backtest/308018c6-fea3-400b-9744-0753e31b0e33 | 27 | 51.85% | $10,018.00 | $9,356.50 | $7,286.50 | 1.28 | 0.5832 | 1.1663 | 0.3791 |

---

## 4. Acceptance Gate Verdict
- **Strict Guardrail 5 Gate**: The original **`NQNFPFade` (`Base`)** is retained as the baseline under strict Guardrail 5 because `V1` produces `$15,988.50` vs `$16,696.50` net profit in holdout (due to filtering out 6 trades).
- **Funded Account Option (`NQNFPFadeV1`)**:
  - `V1` achieves a **higher expectancy per trade (`$592.17/trade` vs `$505.95/trade`, +17.0%)**, lower drawdown in both periods (**`$6,149.83` vs `$8,269.33` in Design; `$4,313.50` vs `$4,783.00` in Holdout)**, and a higher NP/DD ratio (`3.71` vs `3.49`). Both `Base` and `V1` are retained and documented in `tasks/out_08/improve_strategy.py`.
