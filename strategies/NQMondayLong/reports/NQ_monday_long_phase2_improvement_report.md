# Phase 2 Improvement Report — Task 05: `NQMondayLong` (NQ Unconditional Monday 09:30 CT -> 16:00 CT Long)

## 1. Executive Summary & Acceptance Gate Verdict

- **Strategy:** `NQMondayLong` (`NQ-USD`, `5m` bars, buy 1 contract every Monday at `09:30 CT` (`09:35 CT` bar close), exit at `16:00 CT` (`15:55 CT` bar close), `0.40 × 14-day Daily ATR` stop loss)
- **Pre-Registered Plan:** `tasks/out_05/improve_plan.md` (5 mechanism-driven variants tested on `2018-01-02` to `2022-12-31` design window)
- **Design Window (`2018-01-02` to `2022-12-31`) Winners:**
  - **`NQMondayLongV1` (`close_0930 >= open_0830`)**: 191 trades, Net (`$14.50`c + slip) **`$71,771.33`** vs Baseline **`$38,244.17`** (`+$33,527.16`), Max DD **`$15,771.00`** vs Baseline **`$22,766.50`** (`-$6,995.50`), Sharpe **`1.2324`** vs `0.6437`.
  - **`NQMondayLongV5` (`0.30 × Daily ATR` tighter stop)**: 232 trades, Net (`$14.50`c + slip) **`$44,322.78`**, Max DD **`$17,554.85`**, Sharpe `0.7823`.
- **Holdout Validation (`2023-01-01` to `2026-10-09`, touched once):**
  - **`NQMondayLongBase`** generated **`$148,290.67`** Net (`$14.50`c + slip, 176 trades, 60.80% net WR, Max DD **`$15,783.67`**, Sharpe **`1.8624`**, Sortino **`3.5600`**, Calmar **`2.5904`**), beating both **`NQMondayLongV1`** (`$107,407.17` Net, Max DD `$24,308.33`, Sharpe `1.4880`) and **`NQMondayLongV5`** (`$77,048.77` Net, Max DD `$27,498.83`, Sharpe `1.0708`).
- **Acceptance Gate Verdict:** **REJECT IMPROVEMENT / KEEP ORIGINAL (`NQMondayLong` Baseline)**.

---

## 2. Iteration & Session Log

### Design Window (`2018-01-02` to `2022-12-31`)
1. **`NQMondayLongBase` (Baseline)**
   - Session ID: `88c4e09d-807c-4c76-aa61-1fa602053d56`
   - Dashboard: http://localhost:9000/#/backtest/88c4e09d-807c-4c76-aa61-1fa602053d56
   - Metrics: 232 trades, 51.29% net WR, Gross `$43,928.17`, Net (`$14.50`c + slip) `$38,244.17`, Max DD `$22,766.50`, Sharpe `0.6437`, Sortino `1.0355`.
2. **`NQMondayLongV1` (Require `close_0930 >= open_0830`)**
   - Session ID: `afe3d9f8-700a-4991-aac0-2785eef97f7a`
   - Dashboard: http://localhost:9000/#/backtest/afe3d9f8-700a-4991-aac0-2785eef97f7a
   - Metrics: 191 trades, 56.02% net WR, Gross `$76,450.83`, Net (`$14.50`c + slip) `$71,771.33`, Max DD `$15,771.00`, Sharpe `1.2324`, Sortino `2.1795`.
3. **`NQMondayLongV2` (Skip overnight + first-hour rally `> +0.60 × Daily ATR`)**
   - Session ID: `e6338186-7feb-45c8-90aa-ca641b31f106`
   - Dashboard: http://localhost:9000/#/backtest/e6338186-7feb-45c8-90aa-ca641b31f106
   - Metrics: 229 trades, 51.09% net WR, Gross `$42,570.83`, Net (`$14.50`c + slip) `$36,960.33`, Max DD `$22,766.50`, Sharpe `0.6258`.
4. **`NQMondayLongV3` (`V1 + V2` Combined)**
   - Session ID: `62d6fe0d-2a0c-493b-909d-b8d0e0ba29b0`
   - Dashboard: http://localhost:9000/#/backtest/62d6fe0d-2a0c-493b-909d-b8d0e0ba29b0
   - Metrics: 188 trades, 55.85% net WR, Gross `$75,093.50`, Net (`$14.50`c + slip) `$70,487.50`, Max DD `$15,771.00`, Sharpe `1.2152`.
5. **`NQMondayLongV4` (Limit Profit Target `+0.60 × Daily ATR`)**
   - Session ID: `3c95a21c-27b9-44a6-8f52-3d539ec647d2`
   - Dashboard: http://localhost:9000/#/backtest/3c95a21c-27b9-44a6-8f52-3d539ec647d2
   - Metrics: 232 trades (9 limit target exits), 51.72% net WR, Gross `$41,595.00`, Net (`$14.50`c + slip) `$35,956.00`, Max DD `$22,766.50`, Sharpe `0.6172`.
6. **`NQMondayLongV5` (Tighter stop `0.30 × Daily ATR`)**
   - Session ID: `7c37590d-cb66-45ff-acc0-79c4ff39192c`
   - Dashboard: http://localhost:9000/#/backtest/7c37590d-cb66-45ff-acc0-79c4ff39192c
   - Metrics: 232 trades, 46.98% net WR, Gross `$50,006.78`, Net (`$14.50`c + slip) `$44,322.78`, Max DD `$17,554.85`, Sharpe `0.7823`, Sortino `1.3919`.

### Holdout Window (`2023-01-01` to `2026-10-09`)
1. **`NQMondayLongBase` (Baseline)**
   - Session ID: `ef913690-6b4a-4a3f-b4e0-ce7b25db4f56`
   - Dashboard: http://localhost:9000/#/backtest/ef913690-6b4a-4a3f-b4e0-ce7b25db4f56
   - Metrics: 176 trades, 60.80% net WR, Gross `$152,602.67`, Net (`$14.50`c + slip) `$148,290.67`, Max DD `$15,783.67`, Sharpe `1.8624`, Sortino `3.5600`, Calmar `2.5904`.
2. **`NQMondayLongV1` (Holdout)**
   - Session ID: `ff082e01-f7e3-4e1f-830c-222bda018449`
   - Dashboard: http://localhost:9000/#/backtest/ff082e01-f7e3-4e1f-830c-222bda018449
   - Metrics: 147 trades, 58.50% net WR, Gross `$111,008.67`, Net (`$14.50`c + slip) `$107,407.17`, Max DD `$24,308.33`, Sharpe `1.4880`.
3. **`NQMondayLongV5` (Holdout)**
   - Session ID: `74d8ad14-e88b-49e3-9884-1f8b10fd1b2e`
   - Dashboard: http://localhost:9000/#/backtest/74d8ad14-e88b-49e3-9884-1f8b10fd1b2e
   - Metrics: 176 trades, 52.84% net WR, Gross `$81,360.77`, Net (`$14.50`c + slip) `$77,048.77`, Max DD `$27,498.83`, Sharpe `1.0708`.

## 3. Final Selected Variant
Original `NQMondayLong` baseline is retained (`$186,534.84` combined 2018–2026 net profit after `$24.50` RT friction across 408 trades).
