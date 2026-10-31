# Forum summary (scientific interpretation)

- Native Strategy Analyzer backtest on the spent window looked strong
  (121 trades, ~+$31.9k, PF ~2).
- Realistic synchronous-BBO execution reconstruction on the matched 118-trade
  panel removed about **~64%** of same-panel native PnL
  (+$30,475 -> +$10,877.20 Lifetime).
- A smaller MBT implementation path failed after depth/spread + commissions.
- Strategy is currently **parked**.
- Clean later BTC OOS (**2024-09-02 through 2026-08-31**) remains **unopened**.

This package supports native source inspection and native SA reproduction only.
It does not ship external BBO data needed for the realistic reconstruction.
