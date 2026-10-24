# Exact native backtest settings (spent reference)

Recovered from the authoritative forum / native spent template artifacts:

- `templates/forum/BTC_H1_FORUM_NATIVE_SPENT.md`
- `templates/StrategyAnalyzer/BTCREOPENMR_V4_H1_SPENT_PARITY.xml`

## Analyzer

| Setting | Value | Provenance |
| --- | --- | --- |
| Strategy | BTCFuturesReopenResidualFairValueV4 | template |
| Namespace | NinjaTrader.NinjaScript.Strategies.EOF.MR | template |
| Instrument | BTC (continuous CME BTC futures label) | template `InstrumentOrInstrumentList=BTC` |
| Continuous / merge | MergeNonBackAdjusted required on instrument/global UI | docs / forum template notes (NOT stored in template XML) |
| Bars type | Minute | template |
| Bars period | 1 | template |
| Market data type | Last | template |
| Primary Trading Hours | CME FX Futures ETH | template |
| From | 2018-06-11 | template |
| To | 2024-09-01 | template |
| Calculate | OnBarClose | template + strategy defaults |
| Order Fill Resolution | Standard | template |
| Order Fill Resolution type/value | Minute / 1 | template |
| Fill limit on touch | false | template |
| Slippage | 0 | native historical reference |
| Include commission | false | template |
| Backtest commission template | (empty) | template |
| Entries per direction | 1 | template |
| Entry handling | AllEntries | template |
| Exit on session close | false (strategy-controlled exit) | template |
| Default quantity | 1 | template |
| Set order quantity | Strategy | template |
| Time in force | Gtc | template |
| Start behavior | WaitUntilFlat | template |
| Tick replay | false | template |
| Bars required to trade | 1 | template |
| Maximum bars lookback | TwoHundredFiftySix | template |
| Stop | none | strategy (no SetStopLoss) |
| Target | none | strategy (no SetProfitTarget) |

## Spot series

| Setting | Value |
| --- | --- |
| Spot instrument | BTCUSD |
| Spot bars | 1 Minute Last |
| Spot Trading Hours | Cryptocurrency (hardcoded in strategy `AddDataSeries`) |
| Intended identity | CryptoCurrency BTCUSD / Gdax |

## Frozen strategy parameters

| Property | Value |
| --- | --- |
| SpotInstrument | BTCUSD |
| SpotBarsPeriodMinutes | 1 |
| MaximumSpotAgeMinutes | 5 |
| MinimumFuturesClosedMinutes | 30 |
| ResidualLookbackEvents | 60 |
| AbsResidualZThreshold | 1.5 |
| ExecutableExitHoldMinutes | 60 |
| EnableDiagnostics | true |
| DiagnosticsCsvPath | (empty) |

## Signal / exit semantics

- Residual lookback: 60 prior eligible events
- Absolute residual Z threshold: 1.5
- Direction: fade residual (positive Z -> short, negative Z -> long)
- Exit hold: 60 clock minutes from entry fill
- No stop
- No target
- No V2/V3 spot-move gate
- No raw-dollar basis entry gate
- No basis-mean exit

## USER_VERIFY items

These can differ by installation and must be verified locally:

- Exact continuous BTC instrument label available on your PC
- Global / instrument MergeNonBackAdjusted policy actually active
- BTCUSD master instrument id / exchange mapping equals intended CryptoCurrency+Gdax
- Cryptocurrency and CME FX Futures ETH Trading Hours templates present
- Historical coverage for the full From/To window
