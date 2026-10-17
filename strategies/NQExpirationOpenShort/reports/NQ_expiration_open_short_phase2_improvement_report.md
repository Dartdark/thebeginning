# Phase 2 Improvement Report — Task 06: `NQExpirationOpenShort` (NQ 3rd-Friday Monthly Options Expiration Open Short)

## 1. Executive Summary & Acceptance Gate Verdict

- **Strategy:** `NQExpirationOpenShort` (`NQ-USD`, `5m` bars, short 1 contract on the 3rd Friday of each month at `08:30 CT` (`08:35 CT` bar close), exit at `10:00 CT` (`10:05 CT` bar close), `0.35 × 14-day Daily ATR` stop loss)
- **Pre-Registered Plan:** `tasks/out_06/improve_plan.md` (5 mechanism-driven variants tested on `2018-01-02` to `2022-12-31` design window)
- **Design Window (`2018-01-02` to `2022-12-31`) Winner:**
  - **`NQExpShortV5` (`V1 + V2`: Skip if overnight gap `< -0.50 × Daily ATR` + Limit Profit Target at `-0.50 × Daily ATR`)** beat the original baseline on **both** Net Profit and Max Drawdown in `2018–2022`:
    - **Net Profit (`$14.50` RT comm + 1t Mkt / 0t Lmt slip):** **`$23,548.30`** vs Baseline **`$18,317.20`** (**`+$5,231.10`**, `+28.6%`)
    - **Net Profit (`$7.25` RT comm + 1t Mkt / 0t Lmt slip):** **`$23,968.80`** vs Baseline **`$18,752.20`** (**`+$5,216.60`**, `+27.8%`)
    - **Max Drawdown (`$14.50` RT comm + slip):** **`$4,144.30`** vs Baseline **`$4,543.80`** (**`-$399.50`** lower drawdown)
    - **Sharpe / Sortino / Calmar (Gross Jesse):** **`0.9880` / `1.9919` / `1.2261`** vs Baseline **`0.8090` / `1.5335` / `0.9038`**
- **Holdout Validation (`2023-01-01` to `2026-10-09`, touched once):**
  - On the `2023–2026` holdout, **`NQExpShortBase`** generated **`$30,679.00`** Net (`$14.50` RT comm + `$10` slip, 45 trades, 60.0% net WR, Max DD **`$7,467.20`**, Sharpe `1.1482`, Sortino `2.2573`), whereas **`NQExpShortV1`** generated **`$27,963.00`** Net (43 trades, Max DD `$7,467.20`, Sharpe `1.0805`) and **`NQExpShortV5`** generated **`$26,685.00`** Net (43 trades, Max DD `$7,467.20`, Sharpe `1.0507`).
- **Acceptance Gate Verdict:** **REJECT IMPROVEMENT / KEEP ORIGINAL (`NQExpirationOpenShort` Baseline)**.

---

## 2. Iteration & Session Log

### Design Window (`2018-01-02` to `2022-12-31`)
1. **`NQExpShortBase` (Baseline)**
   - Session ID: `2a42c2b5-076f-4488-bd14-c8cba7e0ebe4`
   - Dashboard: http://localhost:9000/#/backtest/2a42c2b5-076f-4488-bd14-c8cba7e0ebe4
   - Metrics: 60 trades, 58.33% net WR, Gross `$19,787.20`, Net (`$14.50`c + slip) `$18,317.20`, Max DD `$4,543.80`, Sharpe `0.8090`, Sortino `1.5335`.
2. **`NQExpShortV1` (Skip if overnight gap `< -0.50 × Daily ATR`)**
   - Session ID: `e1394e93-803d-43bd-92fc-b69e06e71d50`
   - Dashboard: http://localhost:9000/#/backtest/e1394e93-803d-43bd-92fc-b69e06e71d50
   - Metrics: 58 trades, 58.62% net WR, Gross `$21,172.80`, Net (`$14.50`c + slip) `$19,751.80`, Max DD `$4,543.80`, Sharpe `0.8727`, Sortino `1.6889`.
3. **`NQExpShortV2` (Limit Profit Target at `-0.50 × Daily ATR`)**
   - Session ID: `80612151-0503-4644-9eb1-d6e88da87dda`
   - Dashboard: http://localhost:9000/#/backtest/80612151-0503-4644-9eb1-d6e88da87dda
   - Metrics: 60 trades (9 limit target exits), 60.00% net WR, Gross `$23,538.70`, Net (`$14.50`c + slip) `$22,113.70`, Max DD `$4,144.30`, Sharpe `0.9262`, Sortino `1.8275`.
4. **`NQExpShortV3` (Earlier exit at `09:30 CT`)**
   - Session ID: `5dc3b0b8-d2c5-4305-a124-28ddff301bad`
   - Dashboard: http://localhost:9000/#/backtest/5dc3b0b8-d2c5-4305-a124-28ddff301bad
   - Metrics: 60 trades, 60.00% net WR, Gross `$16,176.40`, Net (`$14.50`c + slip) `$14,706.40`, Max DD `$3,684.80`, Sharpe `0.7822`.
5. **`NQExpShortV4` (Tighter stop `0.25 × Daily ATR`)**
   - Session ID: `8fd13a31-e9b6-4dd2-9707-b3dc62938c5a`
   - Dashboard: http://localhost:9000/#/backtest/8fd13a31-e9b6-4dd2-9707-b3dc62938c5a
   - Metrics: 60 trades, 55.00% net WR, Gross `$19,617.92`, Net (`$14.50`c + slip) `$18,147.92`, Max DD `$3,937.83`, Sharpe `0.8353`.
6. **`NQExpShortV5` (`V1 + V2` Combined)**
   - Session ID: `e5bfb5d3-d18d-416b-a313-21f6c30fd3ba`
   - Dashboard: http://localhost:9000/#/backtest/e5bfb5d3-d18d-416b-a313-21f6c30fd3ba
   - Metrics: 58 trades (9 limit target exits), 60.34% net WR, Gross `$24,924.30`, Net (`$14.50`c + slip) `$23,548.30`, Max DD `$4,144.30`, Sharpe `0.9880`, Sortino `1.9919`, Calmar `1.2261`.

### Holdout Window (`2023-01-01` to `2026-10-09`)
1. **`NQExpShortBase` (Baseline)**
   - Session ID: `301b293c-4e59-46e1-8c5f-2f58cbc13ddf`
   - Dashboard: http://localhost:9000/#/backtest/301b293c-4e59-46e1-8c5f-2f58cbc13ddf
   - Metrics: 45 trades, 60.00% net WR, Gross `$31,781.50`, Net (`$14.50`c + slip) `$30,679.00`, Max DD `$7,467.20`, Sharpe `1.1482`, Sortino `2.2573`.
2. **`NQExpShortV1` (Holdout)**
   - Session ID: `5c583e39-3201-4df8-8c54-63467454edbe`
   - Dashboard: http://localhost:9000/#/backtest/5c583e39-3201-4df8-8c54-63467454edbe
   - Metrics: 43 trades, 60.47% net WR, Gross `$29,016.50`, Net (`$14.50`c + slip) `$27,963.00`, Max DD `$7,467.20`, Sharpe `1.0805`.
3. **`NQExpShortV5` (Holdout)**
   - Session ID: `e234a9d9-cc49-4782-8ad2-5cfe503e6398`
   - Dashboard: http://localhost:9000/#/backtest/e234a9d9-cc49-4782-8ad2-5cfe503e6398
   - Metrics: 43 trades (10 limit target exits), 60.47% net WR, Gross `$27,688.50`, Net (`$14.50`c + slip) `$26,685.00`, Max DD `$7,467.20`, Sharpe `1.0507`.

## 3. Final Selected Variant
Original `NQExpirationOpenShort` baseline is retained (`$48,996.20` combined 2018–2026 net profit after `$24.50` RT friction across 105 trades).
