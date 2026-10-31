# Installation (NinjaTrader 8)

Manual steps for the recipient. This package does not launch or compile
NinjaTrader for you.

## 1. Close Strategy Analyzer / NinjaScript Editor sessions as needed

Work on a quiet NT8 instance. Avoid compiling while a long Analyzer run is active.

## 2. Copy source files into your Custom tree

Assume your NinjaTrader 8 Custom root is:

`Documents\NinjaTrader 8\bin\Custom\`

(Exact Documents location depends on your Windows user profile.)

### Strategy (namespace requires EOF\MR)

Copy:

`NinjaTrader\Strategies\EOF\MR\BTCFuturesReopenResidualFairValueV4.cs`

to:

`Documents\NinjaTrader 8\bin\Custom\Strategies\EOF\MR\BTCFuturesReopenResidualFairValueV4.cs`

Create the `EOF\MR` folders if they do not exist.

The strategy namespace is:

`NinjaTrader.NinjaScript.Strategies.EOF.MR`

### Core helpers (`BtcReopenMr.Core`)

Copy every file from:

`NinjaTrader\Core\`

into **either**:

- `Documents\NinjaTrader 8\bin\Custom\AddOns\BtcReopenMr\`
  (recommended; keeps helpers out of Strategies), **or**
- `Documents\NinjaTrader 8\bin\Custom\Strategies\EOF\MR\`
  (also works; NT compiles all Custom `.cs` files)

Required core files:

- `V4ResidualFairValueCore.cs`
- `BtcReopenBasisMrSignalCore.cs`
- `BtcReopenEventGate.cs`
- `GeneratedV1Calendars.cs`
- `Spot24x7DiagnosticCore.cs`

Do **not** rename classes or change namespaces.

## 3. Compile

1. Open **NinjaScript Editor**
2. Compile (F5)
3. Fix any missing-instrument / Trading Hours template issues on your machine
4. Confirm zero compile errors for these files

## 4. Confirm strategy appears

Strategy Analyzer / Strategies list should show:

`BTCFuturesReopenResidualFairValueV4`

## 5. Required instruments / identity

### Primary

- CME standard BTC futures (continuous series used for parity research)
- Bars: **1 Minute**, Market data type **Last**
- Primary Trading Hours: **CME FX Futures ETH**
- Continuous merge policy used for authoritative parity:
  **MergeNonBackAdjusted**
  (set on instrument / global merge UI; not stored inside the strategy `.cs`)

### Spot (secondary series added by strategy)

- Instrument name parameter: **BTCUSD**
- Intended identity: **CryptoCurrency BTCUSD / Gdax**
- Trading Hours: **Cryptocurrency** (hardcoded in `AddDataSeries`)
- Bars: 1 Minute Last

The strategy performs a hard BIP1 identity / Trading Hours certification at
DataLoaded. If your BTCUSD master instrument id / type / exchange / hours do
not match the intended CryptoCurrency+Gdax+Cryptocurrency mapping, compilation
may succeed but the strategy will abort at runtime with a certification error.

## 6. Data vendor disclaimer

Data availability and provider mappings differ between installations.
You must verify:

- continuous BTC futures history coverage for 2018-06-11 .. 2024-09-01
- BTCUSD 1-minute history over the same window
- roll dates / merge behavior under MergeNonBackAdjusted
- Trading Hours templates exist and match the names above

## 7. Do not deploy proprietary vendor data from this package

This ZIP contains source and documentation only. No market-data archives.
