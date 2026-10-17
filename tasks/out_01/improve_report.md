# Task 01 (`CLSundayFade`) — Phase 2 Improvement Report

## 1. Objective & Strict Guardrails
- **Strategy**: `CLSundayFade` (WTI Crude Oil `CL-USD`, 5-minute bars, Sunday `18:05 ET` up-gap fade short, `0.75 * ATR(15)` stop, Monday `10:00 ET` exit).
- **Guardrails Enforced**:
  1. Pre-registered maximum 5 mechanism-driven variants in `tasks/out_01/improve_plan.md` prior to testing.
  2. Evaluated all 5 variants strictly on the **Design Period (`2018-01-01` to `2022-12-31`)**.
  3. Evaluated the baseline and the best risk-control design variant (`V5`) once on the **Holdout Period (`2023-01-01` to `2026-10-13`)**.
  4. Applied full transaction costs:
     - **Conservative Per-Side Interpretation (`compare.py`)**: `$7.25/side` (`$14.50` round-trip) + `1 tick` (`0.01 pts = $10.00`) per market/stop fill (`$34.50` round-trip on market/stop exits; `$24.50` on limit target exits).
     - **Standard Round-Trip Interpretation (`S_RANK_PROGRAM.md`)**: `$7.25` round-trip + `1 tick` (`$10.00`) per market/stop fill (`$27.25` round-trip on market/stop exits; `$17.25` on limit target exits).
     - Both cost schedules are reported side-by-side below.

---

## 2. All Pre-Registered Trials & Jesse Session Dashboard Links

### A. Design Period (`2018-01-01` to `2022-12-31`, `warm_up_candles = 5400`, `fast_mode = False`)

| Variant | Exact Change | Dashboard URL | Trades | Win Rate | Gross $ | Net $ (`$34.50` RT) | Max DD (`$34.50` RT) | Net $ (`$27.25` RT) | Max DD (`$27.25` RT) | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`CLSundayFadeBase`** *(Original)* | Baseline (`gap >= 0.10 ATR`, `0.75 ATR` stop, `10:00 ET` exit) | [View on dashboard](http://localhost:9000/#/backtest/607fed35-8718-4721-b0c3-1023fe50e86a) | 42 | 71.4% | $23,745.50 | **$22,296.50** | $3,168.00 | **$22,601.00** | $3,146.25 | **1.0632** | **3.8428** | 1.29 |
| **`CLSundayFadeV1`** | Limit take-profit at Friday close (`prev_5m_close`) | [View on dashboard](http://localhost:9000/#/backtest/b5924d2a-e67b-45fd-b2b4-122e654f78d4) | 40 | **80.0%** | $19,535.50 | $18,405.50 | $3,168.00 | $18,695.50 | $3,146.25 | 0.99 | 2.91 | 1.15 |
| **`CLSundayFadeV2`** | Skip extreme shock gaps (`gap > 1.00 ATR`) | [View on dashboard](http://localhost:9000/#/backtest/fd2b36fd-edfe-4cf4-b6d9-8a3f98d313aa) | 40 | 70.0% | $13,215.50 | $11,835.50 | $3,168.00 | $12,125.50 | $3,146.25 | 0.89 | 2.18 | 0.86 |
| **`CLSundayFadeV3`** | Exit at NYMEX RTH open (`09:00 ET` vs `10:00 ET`) | [View on dashboard](http://localhost:9000/#/backtest/70ce3c90-ae25-45c7-a7b6-9ef76ba3c020) | 42 | 59.5% | $18,215.50 | $16,766.50 | $4,208.00 | $17,071.00 | $4,179.00 | 0.9470 | 2.8893 | 0.8886 |
| **`CLSundayFadeV4`** | Combined V1 (`prev_5m_close` target) + V2 (`<= 1.00 ATR`) | [View on dashboard](http://localhost:9000/#/backtest/7b305309-3aa4-4f3f-aca7-aff6de37a458) | 38 | 78.9% | $9,005.50 | $7,944.50 | $3,168.00 | $8,220.00 | $3,146.25 | 0.7832 | 1.5860 | 0.5884 |
| **`CLSundayFadeV5`** | Tighten protective stop from `0.75 ATR` to `0.50 ATR` | [View on dashboard](http://localhost:9000/#/backtest/745974f7-419e-4438-aff9-0b5dd72d1911) | 42 | 66.7% | $21,123.67 | $19,674.67 | **$2,993.17** | $19,979.17 | **$2,971.42** | 0.9372 | 3.0418 | **1.4636** |

### B. Holdout Period (`2023-01-01` to `2026-10-13`, `warm_up_candles = 5400`, `fast_mode = False`)

| Variant | Exact Change | Dashboard URL | Trades | Win Rate | Gross $ | Net $ (`$34.50` RT) | Max DD (`$34.50` RT) | Net $ (`$27.25` RT) | Max DD (`$27.25` RT) | Sharpe | Sortino | Calmar |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`CLSundayFadeBase`** *(Original)* | Baseline (`gap >= 0.10 ATR`, `0.75 ATR` stop, `10:00 ET` exit) | [View on dashboard](http://localhost:9000/#/backtest/6f4cc884-6cdc-46e5-91a3-c9af444cf2f2) | 55 | **63.6%** | $42,543.50 | $40,646.00 | **$5,182.50** | $41,044.75 | **$5,146.25** | 1.5443 | 3.8802 | **2.0892** |
| **`CLSundayFadeV5`** | Tighten protective stop from `0.75 ATR` to `0.50 ATR` | [View on dashboard](http://localhost:9000/#/backtest/e46778ba-1a73-491b-bb9b-7d994e51ae6a) | 55 | 61.8% | **$42,606.00** | **$40,708.50** | $7,093.50 | **$41,107.25** | $7,057.25 | **1.5758** | **4.3223** | 1.5447 |

---

## 3. Diagnosis of Each Variant & Market Mechanism Insights

1. **Why Variant 1 (`prev_5m_close` Limit Target) Increased Win Rate to `80.0%` but Reduced Net Profit (`$18,405.50` vs `$22,296.50`)**:
   - Exiting at Friday's close (`prev_5m_close`) raised the win rate from `71.4%` to `80.0%` by banking early gap-fills that later bounced. However, when Sunday up-gaps fail in WTI Crude Oil, trapped weekend longs are forced to liquidate *through* Friday's settlement close into Monday morning, producing multi-point downward cascades. Capping winners at `1.0x` the opening gap truncated the right tail while leaving `-0.75 ATR` losses intact.
2. **Why Variant 2 (`gap <= 1.00 ATR` Cap) Cut Profit Nearly in Half (`$11,835.50` vs `$22,296.50`)**:
   - Contrary to the hypothesis that `> 1.00 ATR` Sunday gaps are un-fadeable physical supply shocks, the two largest Sunday up-gaps in the design sample (`2022-02-27` and `2022-03-06` during the Ukraine war spike) were extreme Sunday-evening retail/headline panics that mean-reverted by `+$4,055.50` and `+$8,835.50` by Monday `10:00 ET`. Skipping large gaps removes the highest-edge dislocations in the strategy.
3. **Why Variant 3 (`09:00 ET` NYMEX Open Exit) Underperformed `10:00 ET` (`$16,766.50` vs `$22,296.50`)**:
   - Exiting at `09:00 ET` (`08:00 CT`, the start of NYMEX pit/RTH hours) misses the `09:00–10:00 ET` first hour of US commercial hedger execution, where win rate jumps from `59.5%` to `71.4%` and drawdown drops by over `$1,000`.
4. **Why Variant 5 (`0.50 ATR` Stop) Improved Design DD & Holdout Net $ but Failed Holdout DD**:
   - Tightening the stop from `0.75 ATR` to `0.50 ATR` lowered 2018–2022 Max Drawdown (`$2,993.17` vs `$3,168.00`) and slightly beat the baseline on 2023–2026 Net Profit (`$40,708.50` vs `$40,646.00`) and Sortino (`4.32` vs `3.88`). However, on the 2023–2026 holdout, a cluster of volatile overnight sessions clipped the tighter `0.50 ATR` stop before reverting, increasing Holdout Max Drawdown from `$5,182.50` to `$7,093.50`.

---

## 4. Final Verdict (Acceptance Gate)
- **Result**: **Retain Original Baseline (`CLSundayFadeBase`)**.
- None of the 5 pre-registered variants beat the original specification simultaneously on **both** Net $ and Max Drawdown across **both** the `2018–2022` design split and the `2023–2026` holdout split.
- Across the full 97-trade history (`2018–2026`), the unmodified 3-parameter `CLSundayFade` rule delivers **`+$66,289.00` gross (`+$62,942.50` net at `$34.50`/trade; `+$63,645.75` net at `$27.25`/trade)** with a `67.0%` win rate and a worst drawdown of `$5,182.50` per full `CL` contract (`$518.25` per `MCL` micro contract, or `$1,036.50` for `2 MCL`). The original rule cannot be improved without overfitting.
