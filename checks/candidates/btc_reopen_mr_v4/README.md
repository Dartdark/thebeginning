# BTC Reopen MR V4 - Public Test Package

Strategy: **BTCFuturesReopenResidualFairValueV4**

This package is for public forum review and independent native NinjaTrader 8
reproduction of the **spent research period** backtest.

It is a **source / documentation package only**.

## What this package is for

1. Inspect the complete BTC H1 strategy logic
2. Install the required NinjaScript source files
3. Reproduce the native Strategy Analyzer spent-period backtest
4. Compare against the documented native reference result
5. Understand which realistic-execution results are **not** reproducible here

## Requirements

- NinjaTrader 8
- NinjaScript / Strategy Analyzer
- CME BTC futures historical data (your vendor)
- BTCUSD CryptoCurrency / Gdax (or equivalent intended spot mapping) 1-minute data
- Trading Hours template: Cryptocurrency for spot; CME FX Futures ETH for primary

This is **not** standalone vanilla C#. It requires NinjaTrader 8 assemblies.

## Attribution

Research concept inspired by Matteo's BTC reopen mean-reversion video.

This implementation, testing, execution qualification, and residual fair-value
formulation are subsequent research work. Matteo did **not** author this V4
implementation.

## Frozen rule (H1)

- Signal: CME reopen residual relative to spot closure move
- `|Z| >= 1.5`
- prior 60 eligible events
- fade residual
- 60 clock-minute exit from fill
- no stop
- no target

## Research firewall

Spent research window:

`2018-06-11` through `2024-09-01`

Sealed / unopened period:

`2024-09-02` through `2026-08-31`

## CRITICAL: native vs realistic execution

The native Strategy Analyzer result looks strong, but it is **not** the
economically realistic headline result.

Matched realistic-execution panel (external reconstruction; **not in this package**):

| Track | Trades | PnL | PF | MaxDD |
| --- | ---: | ---: | ---: | ---: |
| Native full spent (SA Last, commission off) | 121 | ~+$31,925 | ~2.00 | ~$4,075 |
| Same-panel native (118 trade IDs) | 118 | +$30,475 | (panel) | (panel) |
| External synchronous-BBO + Ninja Lifetime commission | 118 | +$10,877.20 | 1.2653 | $6,354.40 |

Realistic BBO reconstruction used external historical order-book / BBO data
and is **NOT** reproduced by this package.

Do **not** include or request proprietary Databento / vendor quote redistribution
to force-match those numbers inside Strategy Analyzer.

## Package layout

```
BTC_Reopen_MR_V4_Public_Test_Package/
  README.md
  LICENSE_NOTICE.md
  INSTALLATION.md
  BACKTEST_SETTINGS.md
  EXPECTED_RESULTS.md
  FORUM_SUMMARY.md
  PACKAGE_MANIFEST.txt
  DEPENDENCY_SANITIZATION.md
  NinjaTrader/
    Strategies/EOF/MR/
      BTCFuturesReopenResidualFairValueV4.cs
    Core/
      V4ResidualFairValueCore.cs
      BtcReopenBasisMrSignalCore.cs
      BtcReopenEventGate.cs
      GeneratedV1Calendars.cs
      Spot24x7DiagnosticCore.cs
```

## EXPECTED FIRST TEST

1. Install source (see `INSTALLATION.md`).
2. Compile in NinjaTrader.
3. Run exact native reference configuration (`BACKTEST_SETTINGS.md`).
4. Compare:
   - N = 121
   - PnL approx $31,925
   - PF approx 2.0
5. If materially different, first investigate:
   - futures roll / merge settings
   - spot BTCUSD identity
   - Trading Hours
   - historical provider / data
   - bar timestamps
   before changing strategy logic.

**DO NOT tune parameters merely to force parity.**
