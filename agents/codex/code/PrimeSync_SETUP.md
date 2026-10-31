# PrimeSync v1 research setup

Code: [PrimeSync_v1.txt](PrimeSync_v1.txt). This is a reconstruction from the
user's description, with assumed parameters. It has not been compiled or
trade-matched in MultiCharts. Use a separate home-PC research chart.

## Inputs and selected exit

Default `ExitMode=0`: the entire position remains open through the 1.5R and
2.5R milestones; stop advances to entry, then to the original 1.5R price.
The remaining position exits at 4.5R. `ExitMode=1` takes equal thirds and
advances stops after the actual first/second partial fill. Quantities are
multiples of three in both modes, as in the comparison.

Assumed entries: SMA150 crossing; bar-typical-price session VWAP from 08:30 CT;
total volume >1.5 x previous20-bar average; range >1.2 x previous20-bar average;
ADX14>=20; stop1.5 x simple ATR14; four-parent-bar cooldown after exit.
Signals only after08:30 and strictly before14:30; out at15:00; known holiday/
half-day sessions skipped. No optimized slope/runner/time-window variants.

## MultiCharts chart

1. In PowerLanguage Editor, create a **new Signal**, `PrimeSync_v1`; paste
   the entire txt file and compile. This Linux workspace cannot compile it.
2. Data1 only; **15-minute or30-minute** ES/NQ chart, full Globex session,
   Exchange time **Central**, total futures volume. No second data series.
3. MaxBarsBack **200**; MinimumStudyBars100; load at least1,000 bars before
   the test's first date. The code forces IntrabarOrderGeneration true.
4. **Bar Magnifier1 minute**; realistic limits require price to trade **1 point**
   through, matching the screen's convention. This is not one tick. Do not
   enable a bar-close-only override or add a second strategy/stop manager.
5. Set and export the actual commission/slippage assumptions. Entry/market/
   stop fills need1 tick adverse; do not also charge limit exits market slippage.
   Export List of Trades, Settings and relevant minute/volume data for parity.

## Sizing and the Python screen's units

The code uses the chart's **BigPointValue** and tick. Its default planned
budget is $500, including a $5 per-contract sizing reserve; max30 contracts;
round down to a multiple of3. If three contracts do not fit, it skips the
entry. It never forces a minimum position or risks a percentage of equity.
The reserve is not a second P&L charge and does not guarantee a loss bound.

The Python comparison used **NQ/ES price and total-volume signals with MNQ/MES
equivalent sizing and $1.04 micro round-trip fees**. Native micro-chart volume
can produce different signals; do not claim those charts reproduce the screen.

To compare signal/fill geometry using a full-size NQ/ES research chart, the
same quantities result from scaling both sizing dollars/reserve by10:
RiskDollars5000 and CostReservePerContract50. Those are **unit conversions
for a research backtest**, not account-size recommendations. To match the
micro cost proxy, that full-size report would charge $10.40 per contract
round trip and one native tick per market/stop fill; divide dollar outputs
by10. Verify the report actually charges that round-trip amount. Never use
these benchmark settings as funded-account trading instructions.

## What needs confirmation

- Compilation on the installed MultiCharts version; total-volume semantics.
- ADX seeding, first valid bars, exact VWAP/ATR/cross signals and data gaps.
- Initial built-in stop/target active on entry; custom raised stop ratchets.
- With IOG, orders update at the next execution event. Stop movement is not
  retrospectively applied to a bar; tick data are stronger than a1-minute model.
- TP1/TP2 partial order quantities, remaining final target and cancellation
  after an exit. Partial live entry fills/rejections are not verified here.
- The Python close at15:00 versus MC's next tick after that close; missing
  scheduled checks/early closes, contract rolls and live slippage.

No Apex placement has been established. The selected style is the better
exit in this bounded historical comparison; that does not validate the entry.
