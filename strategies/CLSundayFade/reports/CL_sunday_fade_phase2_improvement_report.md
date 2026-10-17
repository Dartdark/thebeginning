# Task 01 (`CLSundayFade`) — Phase 2 Improvement Report

## 1. Objective & Strict Guardrails
- **Strategy**: `CLSundayFade` (WTI Crude Oil `CL-USD`, 5-minute bars, Sunday `18:05 ET` up-gap fade short, `0.75 * ATR(15)` stop, Monday `10:00 ET` exit).
- **Guardrails Enforced**:
  1. Pre-registered maximum 5 mechanism-driven variants in `tasks/out_01/improve_plan.md` prior to testing.
  2. Evaluated all 5 variants strictly on the **Design Period (`2018-01-01` to `2022-12-31`)**.
  3. Evaluated the baseline and the best risk-control design variant (`V5`) once on the **Holdout Period (`2023-01-01` to `2026-10-13`)**.
  4. Applied full transaction costs (`$34.50` RT conservative / `$27.25` RT standard).

## 2. All Pre-Registered Trials & Jesse Session Dashboard Links

### A. Design Period (`2018-01-01` to `2022-12-31`, `warm_up_candles = 5400`, `fast_mode = False`)
- **`CLSundayFadeBase` (Original)**:
  - Session ID: `607fed35-8718-4721-b0c3-1023fe50e86a`
  - Dashboard: http://localhost:9000/#/backtest/607fed35-8718-4721-b0c3-1023fe50e86a
  - Metrics: 42 trades, 71.4% WR, Gross `$23,745.50`, Net (`$34.50` RT) `$22,296.50`, Max DD `$3,168.00`, Sharpe `1.0632`, Sortino `3.8428`.
- **`CLSundayFadeV1` (Friday Close Limit Target)**:
  - Session ID: `b5924d2a-e67b-45fd-b2b4-122e654f78d4`
  - Dashboard: http://localhost:9000/#/backtest/b5924d2a-e67b-45fd-b2b4-122e654f78d4
  - Metrics: 40 trades, 80.0% WR, Gross `$19,535.50`, Net (`$34.50` RT) `$18,405.50`, Max DD `$3,168.00`.
- **`CLSundayFadeV2` (Cap Shock Gap <= 1.00 ATR)**:
  - Session ID: `fd2b36fd-edfe-4cf4-b6d9-8a3f98d313aa`
  - Dashboard: http://localhost:9000/#/backtest/fd2b36fd-edfe-4cf4-b6d9-8a3f98d313aa
  - Metrics: 40 trades, 70.0% WR, Gross `$13,215.50`, Net (`$34.50` RT) `$11,835.50`, Max DD `$3,168.00`.
- **`CLSundayFadeV3` (NYMEX Open 09:00 ET Exit)**:
  - Session ID: `70ce3c90-ae25-45c7-a7b6-9ef76ba3c020`
  - Dashboard: http://localhost:9000/#/backtest/70ce3c90-ae25-45c7-a7b6-9ef76ba3c020
  - Metrics: 42 trades, 59.5% WR, Gross `$18,215.50`, Net (`$34.50` RT) `$16,766.50`, Max DD `$4,208.00`, Sharpe `0.9470`, Sortino `2.8893`.
- **`CLSundayFadeV4` (Combined V1 + V2)**:
  - Session ID: `7b305309-3aa4-4f3f-aca7-aff6de37a458`
  - Dashboard: http://localhost:9000/#/backtest/7b305309-3aa4-4f3f-aca7-aff6de37a458
  - Metrics: 38 trades, 78.9% WR, Gross `$9,005.50`, Net (`$34.50` RT) `$7,944.50`, Max DD `$3,168.00`, Sharpe `0.7832`, Sortino `1.5860`.
- **`CLSundayFadeV5` (Tight Stop 0.50 ATR)**:
  - Session ID: `745974f7-419e-4438-aff9-0b5dd72d1911`
  - Dashboard: http://localhost:9000/#/backtest/745974f7-419e-4438-aff9-0b5dd72d1911
  - Metrics: 42 trades, 66.7% WR, Gross `$21,123.67`, Net (`$34.50` RT) `$19,674.67`, Max DD `$2,993.17`, Sharpe `0.9372`, Sortino `3.0418`, Calmar `1.4636`.

### B. Holdout Period (`2023-01-01` to `2026-10-13`, `warm_up_candles = 5400`, `fast_mode = False`)
- **`CLSundayFadeBase` (Original)**:
  - Session ID: `6f4cc884-6cdc-46e5-91a3-c9af444cf2f2`
  - Dashboard: http://localhost:9000/#/backtest/6f4cc884-6cdc-46e5-91a3-c9af444cf2f2
  - Metrics: 55 trades, 63.6% WR, Gross `$42,543.50`, Net (`$34.50` RT) `$40,646.00`, Max DD `$5,182.50`, Sharpe `1.5443`, Sortino `3.8802`, Calmar `2.0892`.
- **`CLSundayFadeV5` (Tight Stop 0.50 ATR)**:
  - Session ID: `e46778ba-1a73-491b-bb9b-7d994e51ae6a`
  - Dashboard: http://localhost:9000/#/backtest/e46778ba-1a73-491b-bb9b-7d994e51ae6a
  - Metrics: 55 trades, 61.8% WR, Gross `$42,606.00`, Net (`$34.50` RT) `$40,708.50`, Max DD `$7,093.50`, Sharpe `1.5758`, Sortino `4.3223`, Calmar `1.5447`.

## 3. Final Conclusion
- Retained original `CLSundayFade` specification (`gap >= 0.10 ATR`, `0.75 ATR` stop, Monday `10:00 ET` exit) as no variant beat the original on both Net $ and Max Drawdown across both 2018–2022 and 2023–2026.
