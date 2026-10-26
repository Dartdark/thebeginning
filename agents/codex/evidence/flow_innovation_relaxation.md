# NQ Flow Innovation Relaxation: TEST

Summary: Test whether unexpected aggressive pressure has temporary impact that relaxes after a receipt delay.
The signal is a conditional signed-FLOW residual; no prior strategy ticket or return predictor enters it.
Available Bridge quantities support a bounded test; informed permanent impact could make the fade lose.
Freeze two candidates and three unselectable controls before design returns. TEST is research eligibility.

Sources: tools/exporters/OFB_OrderFlow_Exporter.txt; analysis/orderflow_test.py;
analysis/bridge_filter_scan.py; analysis/bridge_large_trade_test.py; analysis/bridge_liquidity_test.py;
agents/codex/plans/{flow_absorption,participation_resumption,opening_path_persistence,closing_auction_curvature}.md.
Bounded definition-only novelty and quantity preflights inspected no price outcomes or return ledgers.
New return trials:0. Prior program:60 evaluations/58 unique rules, plus unknown larger repository searches.

## 1. Participant and cause

Marketable buying/selling consumes liquidity. A flow innovation relative to its own recent conditional
distribution could contain temporary liquidity demand, followed by price-impact relaxation as liquidity
suppliers redistribute risk. The prediction is to FADE that innovation, not follow a predicted flow sign.
Neither dealer inventory, an actual metaorder, a hedge mandate nor compulsory covering is observed.
An informed innovation can have permanent impact and invalidate this hypothesis. This is a weak prior,
not evidence of a known forced order or of a profitable forecast.

## 2. Direction and clock known before entry

Use complete five-minute aggressor buy/sell quantities and their previous same-session bar. Estimate an
intercept/AR coefficient once before each date from exact prior-calendar-session slots, using FLOW targets
only. Fade the current conditional residual beyond the fixed training-scale threshold. No price-direction,
opening-path, VWAP-acceptance or old-entry gate determines the side. No dollar-demand estimate is claimed.

Source labels are Eastern bar closes; subtract60minutes for Central labels, including common DST changes.
Decision at close j; skip the immediately following native minute and enter the open of row j+2. For a
09:00 close decision this is the09:02-labelled minute, whose open is09:01 wall time. This is an assumed
whole-minute receipt/order allowance, not measured historical receipt. No same-close fill or delayed retry.

## 3. Transmission

The observed aggressive quantities and traded contract are both NQ. There is one standalone position,
not a cross-market basket. The export has no individual contract identifiers; native close/quantity agreement
and conservative roll handling limit mismatches but do not establish original feed or micro-contract parity.

## 4. Available data and incremental information

| Input | Source and fields | Use and limitation |
|---|---|---|
| Per-minute aggressor flow | data/OF_1min_*.csv:upvol/downvol, source close | Buy/sell quantities, not cumulative-day/profile fields; actual receipt/contract mapping unverified |
| Native execution/risk | data/NQ_1min_*.csv; Grid24 | Complete native OHLCV and shifted prior ATR; continuous-contract and halt-calendar limits retained |
| Calendar | codex_s03_calendar and codex_cash_open_repair helpers | Native CT labels, normal cash days, predeclared roll guard; missing bars are not certified closures |

The exporter documents per-bar aggressor quantities. OF `volume` is BUY volume, not total: reconstruct
total=upvol+downvol and signed fraction=(upvol-downvol)/total. Do not difference cum_delta or manufacture
bars with NaN sums. The new study requires every input minute to have valid OHLCV, valid quantities,
native/source close agreement within one tick and exact native volume=buy+sell. Conflicting duplicates
block intake; failures remain audited. Data masks must be identical for candidates/controls.

The residual varies conditionally on past FLOW, rather than raw flow alone or a price pattern. It becomes
raw demeaned flow at coefficient0 and centered flow change at coefficient1. Controls and degeneracy/equality
audits are necessary; AR terminology does not itself establish novelty. No exact matching entry was found
in the bounded source-definition audit, which is not proof of exhaustive novelty.

## 5. Costs and plan overlap

Use existing research assumptions: NQ7.25USD round trip plus5USD per market/stop fill; MNQ1.24USD plus
0.50USD per market/stop fill, calculated separately. Two market fills require0.8625 NQ points or1.12 micro
points gross. These are repository fee/slippage assumptions, not newly verified broker quotes. Require
four-tick-fill stress too. NQ bars do not establish native MNQ fills; prelisting micro-sized history is
hypothetical. No proxy-derived account result or actual micro execution is claimed.

No empty plan window is established. This daytime rule can share NQ trend/reversal losses with Vault Break,
Overnight Bias, MOC and other daytime entries. Test all eligible events first; do not choose dates from
current plan flatness. Later whole-contract BASE/ADD/replacement/EMPTY tests need valid joint account paths.

## 6. Power and cheapest next step

The allowed window has many five-minute opportunities, but warm-up, strict input agreement, overlapping
holds and the four-ticket cap reduce effective observations. No signal frequency or point-profit estimate
is inferred from innovation magnitude. For assumed trade SD s and effective count n, t2/t6 require net
means2*s/sqrt(n) and6*s/sqrt(n), before adding costs to form a gross hurdle. Daily dependence and the
larger search can make that requirement harder. A bounded design screen is justified; there is no claim
that plausible volume surprises necessarily pay for even the two-fill cost.

## 7. Prior work and falsifiers

Flow Absorption requires price acceptance against raw delta. Participation Resumption uses three OHLCV
bars. Opening Path Persistence uses opening price-path efficiency; it remains below t6 and is not retuned.
Closing Auction Curvature uses scheduled price curvature. Older OF studies use raw/opening delta, book
levels, large prints, price-reaction regressions or strategy-return targets. All remain related prior searches.

Here the side comes only from a flow-only conditional residual. The planned raw and flow-change controls
are unselectable. Failed innovation fades do not authorize reversing into continuation, changing a window,
renominating a control or retuning a rejected family. Reject on the frozen design gate or data falsifiers.

## 8. Failure and executable risk

| Risk question | Pre-return prediction/limit |
|---|---|
| Why it fails | Permanent information, weak flow predictability, quote adjustment before entry, stale/mismatched exports |
| Liquidity role | Market entries and stops consume liquidity; target queue/order sequence remains reconstructed |
| Loss clustering | Persistent informed trends, rapid repricing, rolls, missing minutes and common plan exposures |
| Stops/holding | 0.10 prior ATR stop,0.15 target, entry-bar protection, worst gap fills,30-minute maximum from signal, flat14:55CT |
| Exposure | One position, max4/day; no overnight, BE, trailing, size fit or signals queued while invested |
| Before-breach offset | None established; only later chronological joint account replay can demonstrate timing |

**TEST** the separately committed <=5-configuration plan on2018–22 only. Historical2023+ is previously seen;
run only a frozen selected candidate and its matched base once after design selection is committed. A
promising result still requires dependence/selection/placebo checks and a fresh raw-spec checker before
promotion/accounts. No PowerLanguage on a failed gate and no trading/deployment authorization.
