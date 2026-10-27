# ORB30 EMA: TEST — bounded reconstruction, not verified author replication

Summary: User requests NQ/MNQ review, code and actual tests of a long-only 30-minute ORB.
The supplied posts claim profitable CFD/futures results, but provide no source, settings or ledgers.
Two EMA session definitions and a 15:55 CT flatten proxy are explicitly user-authorized.
Test the frozen design screen; no claim of tick-data or cross-broker validation.

## Mechanism and information
Opening price discovery and stops above the opening high may support continuation. There is no established forced-flow buyer or measured demand independent of prices. This is a price-pattern replication, not a new institutional-flow claim. Long stop orders take liquidity and can suffer gap/slippage losses; a trend gate can merely select equity-index drift. NQ transmits index exposure directly, but CFD pricing/quotes and NQ trades are not identical.

Prior reviewed relatives include Fabio ORB (weak after costs), Bridge ONB, and opening-volume ORBs in TIER_LIST. Increment: exact 30-minute OR, M30 EMA20 gate and 1.85R bracket, plus requested exit comparison. Losses may overlap ONB, VB and Swing Target on failed-breakout days. No presumption of hedging or offset before an account breach.

## Data feasibility and power
Reuse scratch_data/g24.pkl, CT close-stamped minute OHLC, nominal complete coverage through 2026-10-09; warm-up precedes 2018. No native tick/bid/ask or CFD report supplied. Opening range information ends 09:00 CT; stop becomes active at the next minute open. No use of future range/EMA bars. Each trading date is one potential independent event; assumed design ~1250 dates, ~450-650 entries, SD~1R means required mean for t2 approximately .08-.10R/trade before serial dependence. Author's reported ~.10R is marginal at that hurdle; sufficient to screen, not to promote. NQ round trip $7.25 plus adverse tick each market/stop fill; native MNQ fee $1.24 (sensitivity $1.04) plus $.50 each such fill. Wide ORs reduce R costs but integer micro sizing and tail gaps remain material.

## Failure/diversification and falsifiers
Exclude known cash holidays/half-days using the existing deterministic calendar at actual OR date. Failures: nonpositive design edge after costs/stress; no advantage over matched market/random-time entries; trend gate merely drops profitable trades; concentrated profit or missing held paths. No-trade days remain in daily statistics. Reshuffling does not test entry causality. Floating equity and constant-percent compounded risk must be reported separately from closed-dollar curves. Shared future 2023+ is historical validation only. No parameter expansion on failure.

Decision: TEST bounded proxy only. Exact author replication NEEDS original code, flatten time, chart/EMA settings and trade exports. Return trials at registration: zero here; author RR search and walk-forward search sizes unknown.
