# Phase 2 Improvement Report — Task 05: `NQMondayLong` (NQ Unconditional Monday 09:30 CT -> 16:00 CT Long)

## 1. Executive Summary & Acceptance Gate Verdict

- **Strategy:** `NQMondayLong` (`NQ-USD`, `5m` bars, buy 1 contract every Monday at `09:30 CT` (`09:35 CT` bar close), exit at `16:00 CT` (`15:55 CT` bar close), `0.40 × 14-day Daily ATR` stop loss)
- **Pre-Registered Plan:** `tasks/out_05/improve_plan.md` (5 mechanism-driven variants tested on `2018-01-02` to `2022-12-31` design window)
- **Design Window (`2018-01-02` to `2022-12-31`) Winners:**
  - Three variants (`V1`, `V3`, and `V5`) beat the original baseline on **both** Net Profit and Max Drawdown in `2018–2022`, led by **`NQMondayLongV1` (Opening Drive Confirmation: `close_0930 >= open_0830`)**:
    - **Net Profit (`$14.50` RT comm + `$10` slip):** **`$71,771.33`** vs Baseline **`$38,244.17`** (**`+$33,527.16`**, `+87.7%`)
    - **Net Profit (`$7.25` RT comm + `$10` slip):** **`$73,156.08`** vs Baseline **`$39,926.17`** (**`+$33,229.91`**, `+83.2%`)
    - **Max Drawdown (`$14.50` RT comm + slip):** **`$15,771.00`** vs Baseline **`$22,766.50`** (**`-$6,995.50`** lower drawdown)
    - **Sharpe / Sortino / Calmar (Gross Jesse):** **`1.2324` / `2.1795` / `0.9838`** vs Baseline **`0.6437` / `1.0355` / `0.3918`**
  - **`NQMondayLongV5` (`0.30 × Daily ATR` tighter stop)** also beat the baseline on both metrics in `2018–2022` (`$44,322.78` net vs `$38,244.17`; Max DD `$17,554.85` vs `$22,766.50`).
- **Holdout Validation (`2023-01-01` to `2026-10-09`, touched once):**
  - On the `2023–2026` holdout, **`NQMondayLongBase`** delivered extraordinary out-of-sample performance: **`$148,290.67`** Net (`$14.50` RT comm + `$10` slip, 176 trades, 60.80% net WR, Max DD **`$15,783.67`**, Sharpe **`1.8624`**, Sortino **`3.5600`**, Calmar **`2.5904`**), outperforming both **`NQMondayLongV1`** (`$107,407.17` Net, 147 trades, Max DD `$24,308.33`, Sharpe `1.4880`) and **`NQMondayLongV5`** (`$77,048.77` Net, 176 trades, Max DD `$27,498.83`, Sharpe `1.0708`).
  - Why: Whereas `2018–2022` (which included the 2022 rate-hike bear market) rewarded skipping weak Monday first hours (`close_0930 < open_0830`), the `2023–2026` secular AI bull market exhibited strong institutional dip-buying on Mondays where the first hour pulled back (`+$40,883.50` net across those 29 Monday morning dips). Likewise, tightening the stop from `0.40 ATR` to `0.30 ATR` (`V5`) caused premature stop-outs during normal midday volatility before afternoon recovery rallies.
- **Acceptance Gate Verdict:** **REJECT IMPROVEMENT / KEEP ORIGINAL (`NQMondayLong` Baseline)**.
  - Per Guardrail #5, an improvement is accepted *only* if it beats the original in **BOTH** `2018–2022` and `2023–2026` on **BOTH** Net $ per contract and Max Drawdown. Because the unconditional `NQMondayLong` baseline dominates `2023–2026` on both Net $ and Max Drawdown, the original strategy is retained.

---

## 2. Transaction Cost Model Applied

All numbers below are computed per 1 E-mini NQ contract (`$20.00 / pt`, tick size `0.25 pt = $5.00`):
1. **Brief / Guardrail #3 Strict Cost Model (`$7.25/side` = `$14.50` RT commission):**
   - Market / Stop exit trade: `$14.50` commission + `2 ticks` (`$10.00`) slippage = **`$24.50` RT**
   - Limit target exit trade (`V4`): `$14.50` commission + `1 tick` (`$5.00`) entry slippage + `0 tick` limit exit slippage = **`$19.50` RT**
2. **Standard Reference Cost Model (`$7.25` RT commission):**
   - Market / Stop exit trade: `$7.25` commission + `$10.00` slippage = **`$17.25` RT**
   - Limit target exit trade (`V4`): `$7.25` commission + `$5.00` slippage = **`$12.25` RT**

---

## 3. Design Window Log (`2018-01-02` to `2022-12-31`, `warm_up_candles: 210`, `fast_mode: false`)

| Variant | Session ID & Dashboard Link | Exact Change | Trades (Lmt Exits) | Net WR (`$14.50`c) | Gross PnL | Net PnL (`$14.50`c + slip) | Max DD (`$14.50`c + slip) | Net PnL (`$7.25`c + slip) | Max DD (`$7.25`c + slip) | Sharpe / Sortino / Calmar | Design Conclusion |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NQMondayLongBase`** | `88c4e09d-807c-4c76-aa61-1fa602053d56` — [View on dashboard](http://localhost:9000/#/backtest/88c4e09d-807c-4c76-aa61-1fa602053d56) | Unchanged baseline: Long Monday `09:30 CT`, exit `16:00 CT`, `0.40 ATR` stop | 232 (0) | 51.29% | `$43,928.17` | `$38,244.17` | `$22,766.50` | `$39,926.17` | `$22,685.92` | `0.6437` / `1.0355` / `0.3918` | Baseline reference |
| **`NQMondayLongV1`** | `afe3d9f8-700a-4991-aac0-2785eef97f7a` — [View on dashboard](http://localhost:9000/#/backtest/afe3d9f8-700a-4991-aac0-2785eef97f7a) | Require positive first hour (`close_0930 >= open_0830`) | 191 (0) | **56.02%** | **`$76,450.83`** | **`$71,771.33`** | **`$15,771.00`** | **`$73,156.08`** | **`$15,720.25`** | **`1.2324` / `2.1795` / `0.9838`** | **#1 Design Winner: `+$33,527` Net $, `-$6,996` Max DD** |
| **`NQMondayLongV2`** | `e6338186-7feb-45c8-90aa-ca641b31f106` — [View on dashboard](http://localhost:9000/#/backtest/e6338186-7feb-45c8-90aa-ca641b31f106) | Skip if overnight + first-hour rally `> +0.60 × Daily ATR` | 229 (0) | 51.09% | `$42,570.83` | `$36,960.33` | `$22,766.50` | `$38,620.58` | `$22,685.92` | `0.6258` / `1.0058` / `0.3797` | Slightly lower Net $ (`-$1,283.84`) (REJECT) |
| **`NQMondayLongV3`** | `62d6fe0d-2a0c-493b-909d-b8d0e0ba29b0` — [View on dashboard](http://localhost:9000/#/backtest/62d6fe0d-2a0c-493b-909d-b8d0e0ba29b0) | Combined `V1 + V2`: `close_0930 >= open_0830` and rally `<= +0.60 ATR` | 188 (0) | 55.85% | `$75,093.50` | **`$70,487.50`** | **`$15,771.00`** | **`$71,850.50`** | **`$15,720.25`** | `1.2152` / `2.1478` / `0.9664` | **Beats Base Net $ (`+$32,243`) and DD (`-$6,996`)**, dominated by `V1` |
| **`NQMondayLongV4`** | `3c95a21c-27b9-44a6-8f52-3d539ec647d2` — [View on dashboard](http://localhost:9000/#/backtest/3c95a21c-27b9-44a6-8f52-3d539ec647d2) | Resting Limit Take-Profit at `entry + 0.60 × Daily ATR` | 232 (9) | 51.72% | `$41,595.00` | `$35,956.00` | `$22,766.50` | `$37,638.00` | `$22,685.92` | `0.6172` / `0.9814` / `0.3710` | Clips large afternoon trend days (`-$2,288.17` Net $) (REJECT) |
| **`NQMondayLongV5`** | `7c37590d-cb66-45ff-acc0-79c4ff39192c` — [View on dashboard](http://localhost:9000/#/backtest/7c37590d-cb66-45ff-acc0-79c4ff39192c) | Tighter protective stop at `0.30 × Daily ATR` | 232 (0) | 46.98% | `$50,006.78` | **`$44,322.78`** | **`$17,554.85`** | **`$46,004.78`** | **`$17,475.10`** | `0.7823` / `1.3919` / `0.5805` | **#2 Design Winner: `+$6,078.61` Net $, `-$5,211.65` Max DD** |

---

## 4. Holdout Validation Log (`2023-01-01` to `2026-10-09`, `warm_up_candles: 210`, `fast_mode: false`)

| Variant | Session ID & Dashboard Link | Trades (Lmt Exits) | Net WR (`$14.50`c) | Gross PnL | Net PnL (`$14.50`c + slip) | Max DD (`$14.50`c + slip) | Net PnL (`$7.25`c + slip) | Max DD (`$7.25`c + slip) | Sharpe / Sortino / Calmar | Holdout Verdict vs Base |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NQMondayLongBase`** | `ef913690-6b4a-4a3f-b4e0-ce7b25db4f56` — [View on dashboard](http://localhost:9000/#/backtest/ef913690-6b4a-4a3f-b4e0-ce7b25db4f56) | 176 (0) | **60.80%** | **`$152,602.67`** | **`$148,290.67`** | **`$15,783.67`** | **`$149,566.67`** | **`$15,761.92`** | **`1.8624` / `3.5600` / `2.5904`** | **Holdout Winner (Original Baseline)** |
| **`NQMondayLongV1`** | `ff082e01-f7e3-4e1f-830c-222bda018449` — [View on dashboard](http://localhost:9000/#/backtest/ff082e01-f7e3-4e1f-830c-222bda018449) | 147 (0) | 58.50% | `$111,008.67` | `$107,407.17` | `$24,308.33` | `$108,472.92` | `$24,264.83` | `1.4880` / `2.7490` / `1.2245` | Fails Holdout Net $ (`-$40,883.50`) and DD (`+$8,524.66`) |
| **`NQMondayLongV5`** | `74d8ad14-e88b-49e3-9884-1f8b10fd1b2e` — [View on dashboard](http://localhost:9000/#/backtest/74d8ad14-e88b-49e3-9884-1f8b10fd1b2e) | 176 (0) | 52.84% | `$81,360.77` | `$77,048.77` | `$27,498.83` | `$78,324.77` | `$27,174.47` | `1.0708` / `1.9449` / `0.8120` | Fails Holdout Net $ (`-$71,241.90`) and DD (`+$11,715.16`) |

---

## 5. Key Takeaways & Final Selection

1. **Why the Original Baseline (`NQMondayLong`) Won Out-of-Sample:**
   - The `09:30 CT -> 16:00 CT` Monday long effect captures weekly institutional capital deployment after the initial `08:30–09:30 CT` weekend-hedge digestion window.
   - In `2023–2026`, Mondays where the first hour (`08:30–09:30 CT`) pulled back (`close_0930 < open_0830`) actually offered the best institutional dip-buying entry prices at `09:30 CT`, generating `+$40,883.50` of net profit across 29 trades and keeping Max Drawdown at `$15,783.67`.
2. **Final Selected Strategy:** Retain original **`NQMondayLong`** (`tasks/out_05/strategy.py`, mirrored in `tasks/out_05/improve_strategy.py`), which achieved **`$186,534.84` combined 2018–2026 net profit** after `$24.50` RT friction across 408 trades.
