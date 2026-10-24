# Overnight TickRSV/VIX interaction: NEEDS DATA

Summary: A long-only overnight rule combines a negative cash session with TickRSV and VIX regimes.
The screenshots report PF2.01 over547 trades, but include no executable source or trade export.
Owned Bridge split volume is documented aggressor flow; its equivalence to the requested tick-direction input is unconfirmed.
Obtain the source, exact report/settings, and original chart-field provenance before any return trial.

Sources: archived `agents/codex/inputs/overnight_tickrsv/source.txt`; user screenshots; context/hash JSON;
`tools/exporters/OFB_OrderFlow_Exporter.txt`; `analysis/orderflow_test.py`; current Codex builder/workflow/template.
Return trials: **zero**. Author reports many prior tests; their number and history are unknown.

## 1. Who trades, and what forces or causes the trade?

The author proposes reversal of selling pressure after negative RTH days in elevated VIX, and continuation
of nonnegative tick activity in calm VIX. No identified forced participant, obligation or dollar flow is
measured. The TickRSV/VIX interaction is an empirical hypothesis; the narrative is not causal evidence.

## 2. Direction, size and timing known before entry

Long1NQ, no target or active stop. RTH09:30-16:00ET must have closed below its open; exclude shortened sessions.
Aggregate UpTicks/DownTicks15:15-16:15ET; TickRSV=(up-down)/(up+down). Require negative TickRSV with VIX>MA,
or nonnegative TickRSV with VIX<=MA. Decision18:00ET, exit04:00ET. Freeze bar-close versus actual fill timing,
Sunday/Friday state and five-minute window boundaries from the code. Today’s finalized VIX may be known
before18:00; verify Data2 synchronization rather than blindly imposing a one-day lag. MA20 default versus
MA25 selected is unresolved. No independently measured flow size can be supplied.

## 3. Does the flow reach the traded contract or its direct hedge?

The measurements and order are intended for NQ itself. That removes cross-market transmission uncertainty,
but does not establish predictive information beyond negative-day/overnight long drift.

## 4. New information and data feasibility

| Input | Owned source/fields | Inspected coverage | Unresolved |
|---|---|---|---|
| NQ prices | NQ day and ON minute CSVs, OHLC,total volume | Local day2018-01-02 to2026-10-09; ON2017-12-01 to2026-10-09; additional2017 daytime CSV verified by remote metadata on Claude branch | Chart bars/session/roll match; remote2017 contents not inspected here |
| VIX | `data/VIX_daily.csv`, DATE/OHLC |1990-01-02 to2026-10-14 | Daily-bar completion/as-of join and exact input20/25 |
| Bridge flow |35 `OF_1min_*.csv`, upvol/downvol |2018-01-02 to2026-07-07, ET | Documented aggressor buy/sell volume, not established as original tick direction |
| Exact source/trades | Description/screenshots only | No code or row-level trade export | Mandatory replication inputs missing |

The Bridge exporter itself reads UpTicks/DownTicks from synthetic Bridge bars. Shared field names do not
establish shared economic meaning across chart types. Do not reconstruct tick direction from OHLC, bar color
or total volume. Endpoint checks do not certify complete windows: OF_2020_2 ends2020-06-30 at10:11ET.
No new data purchase is indicated; first verify the original chart/feed and volume-building settings.

## 5. Costs and actual intraday gaps

Screenshots report net211405/547=$386.48 per trade, assuming the described fixed1NQ, with unknown costs.
This exceeds nominal$17.25 round-trip research costs, but the selected screenshot mean is not an audited edge.
17:00-03:00CT is distinct from daytime VB/ONB entries, although it may overlap Sunday Bridge and other overnight
holdings. Actual conditional occupancy/joint losses are unmeasured; do not select test dates from flat-plan dates.

## 6. Power before a return test

Reported547 trades over about8.8years suggests roughly300 design trades, not a verified event count. Trade SD
is absent, so no valid power claim or t-stat can be inferred from PF. Illustratively, n300 and SD$1000 would
require about$115 net/trade for t2 before dependence/multiple-testing penalties. These are assumptions only.

## 7. Already tested and falsifiers

Closest family: Overnight Drift/OND (backup, midnight-to03:00CT after a down day), prior overnight-long rounds,
and rejected VIX-MA sentiment filtering (`TIER_LIST.md`, `analysis/ond_sentiment_filter_test.py`). None evaluates
this exact tick/VIX interaction. Future tests must compare the same clock against unconditional long,
down-day-only, VIX-only and TickRSV-only controls, quantify all four interaction cells and removed trades,
and separate MA20/default from author-selected25 without choosing on their already-seen2017-2026 history.

## 8. Failure and diversification

| Question | Prediction/limitation before testing | Required evidence |
|---|---|---|
| Mechanism fails | Selling can continue overnight; interaction may be selected noise | Frozen controls, chronological replication, forward evidence |
| Liquidity role | Marketable reopen entry/time exit; spread and latency matter | Native orders/trades and observed quotes |
| Loss clustering | Unstopped longs share equity selloff/tail exposure | Intratrade MTM, gap/roll/margin and account replay |
| Shared losses | Long-NQ factors may coincide with Bridge/other long exposure | Conditional joint losses and minute occupancy |
| Offset before breach | No offset is established; future daytime wins cannot rescue earlier liquidation | Chronological account path at executable size |

No predetermined loss cap exists. A disabled optional3x20-session overnight-range stop is not active protection.
The reported historical drawdown is not a maximum loss or safe sizing guarantee.

## Decision and next gate

**NEEDS DATA**: original PowerLanguage source, chart/feed/volume mode and daily VIX settings, full exact-version
Excel report with Settings/trades and costs; confirm matching native UpTicks/DownTicks history if required.
The brief states: **"Only TEST sheets advance; NEEDS DATA / DON'T TEST stop here."** User authorization to
test is understood; inventing a different flow field would not complete that test. No return preregistration
or account placement is claimed. All50K/150K evaluation/funded and personal comparisons remain unrun.

Account calendar needs consistent interpretation: builder's broad no-overnight wording conflicts with the
funded README explicitly allowing evening-to-morning positions flat before15:59CT. The proposed17:00-03:00CT
hold does not cross that daily deadline. Do not reject automatically or silently change it to Sunday-only.
