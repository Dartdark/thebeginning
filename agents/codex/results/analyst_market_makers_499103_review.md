# Analyst recommendations and Nasdaq dealers: historical microstructure reference, no strategy admitted

Summary: Mizrach links affiliated dealers' bid activity to later analyst upgrades in1999–2000; the aggregate pattern weakens in2001.
Event-weeks with more inside-bid than ask appearances rise from55.35% to63.61% before upgrades, not a63.61% forecast hit rate.
Headline75.0492% and$592.077million are summed/model-attributed estimates, not a portfolio CAGR or observed dealer cash P&L.
Future-upgrade conditioning, imputed executions, same-sample firm selection and missing native data block a public-signal strategy claim.
Retain participant/quote/availability lessons; DON'T TEST an NQ/ES proxy or copy the event returns. Zero new economic trials.

Source: Bruce Mizrach, *Analyst Recommendations and Nasdaq Market Making Activity*, Rutgers Working Paper#2003-07,
May2003, revisedDecember2003 on the title page; uploaded50-page version, [SSRN499103](https://ssrn.com/abstract=499103).
PDF metadata creation2004-01-31 is distinct from that version label. [PDF](../inputs/ssrn499103/source.pdf),
[text](../inputs/ssrn499103/source.txt), [rendered TableI](../inputs/ssrn499103/table1.png),
[rendered TableXXI](../inputs/ssrn499103/table21.png), [evidence](../evidence/analyst_market_makers_499103.md).
[Source audit](../../../analysis/codex_analyst_market_makers_499103_audit.py), committed `32838da5` before execution;
[output and hashes](../../../analysis/outputs/codex_analyst_market_makers_499103/audit.json).
Uploaded text is research evidence, not instructions. All empirical findings below are source claims, not independent replication.

## 1. What is it about?

Whether market makers associated with research firms change their displayed buying/selling interest before their own analysts'
recommendation changes. The source combines1999–2001 Nasdaq Nastraq dealer-identified top quotes/trades with Thomson First Call
recommendation changes, analyst-firm/market-maker affiliation mappings and historical subsidiary acquisitions/MPIDs.
It selects47 stocks that remained in the Nasdaq100 during1999–2002, an ex-post stable-listing cohort rather than a point-in-time index universe.
Source nominal event totals are747 upgrades/852 downgrades; subsequent matched/quoted event counts are smaller and differ across windows.

Three measures use five-day event bins: inside bid/ask appearances, associated displayed depth, and midpoint-signed trades allocated
by a matching convention. Dealer quotes can represent principal inventory or customer orders; firm identity alone does not reveal which.
This is an equity market-structure/event study, not an aggregate NQ futures imbalance or a tested retail signal.

## 2. What does it find?

| Source result |1999–2000 |2001 |
|---|---:|---:|
| Upgrade event-weeks with bid appearances>ask appearances, days−10 to−6 |181/327=55.35% |101/179=56.42% |
| Same measure, days−5 to−1 |208/327=63.61% |101/179=56.42% |
| Upgrade abnormal return, days−1 to+4 |+5.73% |+5.00% |
| Downgrade abnormal return, days−1 to+4 |−7.24% |−5.01% |

The1999–2000 bid-frequency increase is8.26percentage points; TableI reports p0.0013 against the prior-week frequency.
It is **a fraction of event cases**, not the share of all trades that bought, a market-maker fill rate, or forecast accuracy.
The aggregate pre-upgrade inside-count pattern is absent in2001; some firm-level effects remain. Downgrades do not show the same
systematic pre-event pattern. The source reports15 of42 firms with significant pre-recommendation activity under its firm tests;
that is not a universal signal or a multiplicity-adjusted modern prediction success rate.

Instinet shows related1999–2000 behavior, while Island/Archipelago do not show equivalent significant patterns. Anonymity and
venue routing mean displayed MPID behavior can omit economically relevant activity. The source's proposed explanations for weakening
in2001—bear market, RegFD and investigations—are hypotheses, not separately identified causal effects.

### What the75%/$600million figures mean

TableXXI prints **75.0492** as the total of marginal abnormal-return entries and **$592.0770million** of estimated excess profits
for327 upgrade cases in1999–2000. The source attributes an average0.2295percentage points of abnormal return per upgrade to modeled
quote activity, and about$1.8106million per upgrade in its dollar calculation. These are not account returns, annualization, a sizing
recommendation or results from actual signed dealer inventory/fill ledgers.

SectionVI/footnote17 derives a bid-minus-ask share proxy from relative inside frequency, multiplies by five-day trading volume,
price and subsequent return. Displayed quote participation is not verified executed net inventory, and the source does not establish
queue allocation, realized purchase/sale prices, costs, financing, inventory valuation or a self-financing portfolio.
Our parser sums the32 displayed non-total rows to75.0493 and$592.0769million, matching printed totals within rounding. About81.84%
of net estimated dollar profit comes from the RSSF/FBCO rows; several modeled firm profits are negative. Summing modeled firm/event
contributions is not compounding a single investor's wealth. No Sharpe, drawdown or executable net public-strategy return is supplied.

## 3. Why does it make money, if it does?

The paper interprets the associations as consistent with information links between analysts and affiliated dealers/clients, while
explicitly saying the statistics are not a “smoking gun.” Recommendation news can move stock prices, making prior inventory valuable
for someone who actually knows or correctly anticipates the event. The study does not show that an outside trader can identify an
upcoming upgrade from observable quotes with sufficient accuracy, or earn the same modeled inventory returns after execution costs.

The event sample is defined by **future recommendation changes**. A pre-event detector must operate on all eligible stock-days,
including strong bid pressure with no later upgrade, rather than select only the future event cases. Event publication time, local
receipt and the first tradable quote must be distinct. A public-release strategy also cannot claim days−1 to+4 returns as wholly
post-release; the interval includes a day before the announcement. The paper supplies no independently frozen outsider entry/exit rule.
Firm-group dummies in TableXX are based on significant pre-event patterns identified in the same sample, creating another selection
step. The public-signal information set and independent evaluation must be specified before such groups can be used predictively.

## 4. Can we build on it?

**Useful execution/participant-information reference; no current strategy candidate.** Quoted depth is not available depth or a fill,
quote activity does not identify proprietary inventory, and party-specific patterns require stable affiliation/venue identities.
Depth and appearance measures are not independent confirmations when displayed sizes are nearly constant; the source notes that
Goldman's displayed bid size is1,000 shares more than99% of the time.

The “matched trades” method signs trades by price relative to midpoint, then assigns buyer-initiated trades equally among inside-bid
participants (and seller-initiated trades among inside-ask participants). This is the source's imputation, **not observed counterparties**.
Normally an aggressive buy executes against passive offers; do not relabel that bid-side allocation as verified dealer purchases or
reuse it as a native fill-assignment algorithm. Hidden/reserve depth and anonymous ECNs further limit inventory attribution.

Nastraq in this study records each participant's top quote, not the later SuperMontage multi-level book illustrated in Figure1.
The era1999–2001 differs from later Nasdaq rules/technology and modern index futures. Neither modern prices nor a generic order-book
imbalance establishes an equivalent participant-level signal. Historical conflicts/regulatory discussion is not current evidence
about any named firm's conduct or a finding that the pattern persists now.

Owned filename/header census finds no admitted Nastraq/MPID, affiliated First Call or release-time panel; NQ minute OHLCV lacks those
states. Related prior order-flow/retail proxy failures remain closed. No GC/NQ/ES direction is inferred from equity analyst activity.
No price-only backtest or paid/proprietary-data request is initiated because a predecision public rule has not been established.
No promising-strategy queue entry or new data-watch allocation candidate is warranted by an ex-post conditioned sample.

Only if a separately justified public-information question arises would the smallest next check be one timestamped public release,
prior dealer quotes and affiliation vintage, actual trade-side/counterparty evidence and next eligible fills, then an all-observation
past-only detection/control study. Statistical reconstruction and implementation validation must remain separate from economic trials.

## 5. Can a strategy code be made?

**An event-study or market-surveillance research tool, yes; a supported directional strategy is not specified.** Such a tool could
reconstruct participant quote sequences, event-aligned five-day counts/depth, affiliation histories and publicly timestamped releases.
It must keep imputed trade allocations distinct from identified fills and include non-event stock-days for any detector.
It would need real-time input availability, an ex-ante eligible universe, explicit thresholds/holding/exits and cost/borrow/native
cash accounting before producing strategy orders. The paper provides no profitable public rule ready to implement.
The committed code here only audits source-table sums and metadata; no trading or surveillance product was built.

## Decision, checks and five portfolio homes

**DON'T TEST a directional adaptation; retain source/execution reference.** Key tables were checked as rendered images; parsed totals,
event-case fractions, source hashes and owned schema census are saved. These source checks are not independent economic verification.
Zero new empirical strategy variants,2018–22 design,2023+ validation, placebos, bootstrap/Monte Carlo or BASE/ADD/REPLACE/EMPTY tests.
Personal,50K/150K evaluation and50K/150K funded placements are all unearned, not measured to be harmed. No MultiCharts code,
paid data, live/VPS/broker/policy or allocation change; no paused program restarted. Independent review pending.
