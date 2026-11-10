# dot: month-end FX hedge-flow source update
Author: dot. 2026-11-10. Updates existing D23; no new candidate count or return tests.

## Melvin–Prins: accessible draft versus final publication
Full [ECB-hosted November2013 draft](https://www.ecb.europa.eu/events/pdf/conferences/131216/Third_FX_Workshop_MELVIN_PRINS_Equity%20hedging%20and%20exchange%20rates%20Nov%202013.pdf) inspected. Ten-country panel, April2004–December2012, brokerage five-minute TWAP FX and Datastream national equity indices. Month signal runs **first-day close to second-last-day close**. Outcome is final-day15:00–16:00 London currency return. Both equity and FX returns are cross-sectionally demeaned; common slope−.0142, R².03. No executable portfolio/costed holdout established.

[Published2015 article](https://www.sciencedirect.com/science/article/pii/S1386418114000779), DOI10.1016/j.finmar.2014.11.001, instead specifies eight currencies through2013, adding capitalization/foreign-holdings/liquidity modeling. Full final version unavailable. Earlier secondary SSRN identities2019274/1783025 are not authenticated final-version equivalents.

## Implications for existing D23
The [existing source note](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/research/hunt_v2_prefix_equity_source.md) can now distinguish verified **draft** universe/month base from still-missing final specifications. This research note does not edit its original frozen protocol.

Algebra, not tested alpha: under a common slope, subtracting USD from EUR cancels the panel mean. US equity outperformance implies a positive expected EURUSD move, hence a long6E direction; Eurozone outperformance implies the reverse. Actual hedge notionals and final-model weights are not recovered by this subtraction.

The [failed public-index intake](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/hunt_v2_prefix_equity_intake.md) remains rejected: purported SPX338–344 dates/year and uncertain identity/vintages. Existing futures bars do not fix this.

Literal Europe/London15:00–16:00 converts normally to07:00–08:00 Pacific; during US/UK DST mismatches08:00–09:00. Other draft text says GMT, so native timestamp interpretation remains a gate. D23's15:55 exit truncates the paper window, not a faithful replication. Historical holidays, five-minute fixing reform in2015, close clocks, licensed index datatype and native contract/roll/cost admission remain missing. [LSEG methodology background](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/other/wmr-fx-bechmarks-october-2024.pdf) and [modern activity analysis](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/factsheets/wmr-spot-rates-market-analysis.pdf) do not establish modern signal profitability.

## Related causal mechanism, not a tradable substitute
Ben Zeev/Nathan, *Shorting the Dollar When Global Stock Markets Roar*, [SSRN4332364](https://ssrn.com/abstract=4332364), [full July2024 author manuscript](https://danielrnathan.com/assets/pdf/BZN_RAPS.pdf). Proprietary Bank of Israel institution FX flows2011–21 and CRSP constituent shocks identify equity-driven dollar selling. Roughly .07% USD/ILS depreciation from an equity-value shock; .53% is a standardized flow-shock response, **not a strategy return**. Daily volume-weighted forward prices and contemporaneous estimated shocks are not pre-entry executable signals. No costed intraday portfolio or trading holdout.

Assessment: this supports a hedging mechanism, not D23's month-end EURUSD implementation. Israeli data cannot be replaced with yesterday's SPX return or6E without a new design. Alternative listing4548592 cites4332364; do not double count.

## Failures remain failures
Unconditional Frankfurt6E short3521370 remains failed:2018–22 gross$17.52 versus$19.75 cost, net−$2.23, t−.21. Separate post-London16:03 self-price fade remains failed. Session-flow2099321 and overnight dividend-flow6415558 have different causal inputs; neither supplies missing D23 data. No modern untouched net holdout located.
