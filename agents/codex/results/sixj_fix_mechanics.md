# 6J Tokyo fixing flow: mechanics coherent; NEEDS DATA / SOURCE CONFIRMATION

The user's existing 6J access is unavailable for export now. This requested
manual follow-up tested bookkeeping, clocks and data-failure behavior using
invented fixtures only. **20 revised synthetic checks passed**, with an
independent reviewer also passing three additional fill-clock cases. No edge,
strategy returns, correlation or book benefit was measured. Worth considering
a small later source/gross screen; a full export is not justified by this story
alone, and there is no reason to obtain data urgently.

Test contract/code committed before first checks: `d143a80`; exact-scheduled-fill
correction committed before revised checks: `4c09e21`.
Plan: [mechanics test contract](../research/sixj_fix_mechanics_test_plan.md).
Script: `analysis/codex_sixj_fix_mechanics.py`.
Output: `analysis/outputs/codex_sixj_fix_mechanics/synthetic_checks_v2.json`.

**Economic running totals remain 10/10 hypotheses, 5/60 model evaluations,
4 gross screens, plus the separately archived 65 t6 evaluations.** This manual
synthetic task adds zero to each. The hunt and its continuation remain completed
and paused. No t6 research or watcher resumes. The user's reply authorizes these
mechanical checks, not empirical H11 or an extension of the completed budget.

## What a trade would depend on

The inherited premise is commercial importers buying USD for settlement before
a 09:55 Asia/Tokyo fixing, particularly around gotobi dates. Importers have real
payment objectives, but an obligation to settle is not proof of a compulsory
net market order in a particular minute. Exporters, bank internal netting,
dealer prehedging and other investors can offset or reverse the net demand.
The signed size and actual deadline have not been authenticated here. A calendar
flag measures dates, not dollars of orders or price impact.

If residual USD buying pushes USD/JPY up, USD-per-JPY falls: the inherited
pre-fix direction is **SHORT 6J**. A post-fix long needs additional evidence
that pressure is temporary. Permanent repricing and advance dealer hedging do
not imply an automatic reversal. No favorable side, entry window, stop or target
was selected from data, and no complete executable strategy was frozen.

The nominal fixing clock converts to **00:55 UTC, 18:55 CST / 19:55 CDT on
the previous Chicago civil date**. Tokyo Monday maps to Chicago Sunday.
Named-zone checks covered winter/summer, both US DST transition weeks and year
rollover. These conversions validate the arithmetic of the inherited time;
they do not verify every bank's historical fixing/deadline convention.

## What the synthetic checks establish

|Area|Result and boundary|
|---|---|
|Quote inversion|USD/JPY up/down/flat gives opposite/zero reciprocal change. Toy spot inversion is not a futures execution or carry/basis model.|
|Net flow|Arbitrary importer/exporter/prehedge scenarios can produce zero or negative residual demand. Actual quantities and price impact are unmeasured.|
|Post-fix path|Both lasting and assumed reversing impacts are possible. A fixing does not establish reversal.|
|Clocks|Seven explicit named-zone cases pass, preserving the preceding CT date. This is not a historical event-calendar reconstruction.|
|Calendar failure|Unknown remains UNKNOWN; a deliberately fictional closure fixture shifts and deduplicates nominal events. No Japanese holiday convention was applied. Invalid February30 is rejected.|
|Fill clock|A price-observation order waits until after receipt. An absent exact scheduled open cannot use a later observation or forward-filled price. A prearranged calendar order is a different protocol and need not wait for a price signal.|
|Cost arithmetic|Both market fills incur the assumed friction; fee and slippage are separate. Actual native specifications, fee schedule, spreads and available size remain unadmitted.|

The first run's 19 tests passed, but independent review found an insufficient
missing-open fixture: it could let a later supplied open replace a missing
scheduled open. That first output is retained as `synthetic_checks.json` and
does not constitute full clearance. Revised code requires the exact timestamp
and adds the adversarial gap case. The 20-check result supersedes it; these are
implementation checks, not 39 independent economic trials.

The harness has no market-input or network interface. It contains no historical
return calculation, signal selection, grid backtest, stop/target engine, account
simulator or performance estimator. Active entry-bar protection, worse gap
fills, target-through, exchange holidays and session flat rules remain for a
later complete spec and shared execution engine. This review is not an
independent raw-spec financial promotion check.

## Conditional cost illustration, not an actual fee quote

An **assumed** 12,500,000-JPY multiplier and 0.0000005 price tick produce
$6.25 per tick. With an **assumed** $4 round-trip fee and one adverse tick per
market fill, round-trip cost is $16.50 and the hunt's 2x gross screen would
require $33 per trade. Two adverse ticks per fill raise those numbers to
$29 and $58. These are illustrative assumptions, not newly admitted product
specifications or realistic fill measurements for this venue/hour.

At an invented USD/JPY starting quote of150, $33 on that assumed multiplier
corresponds to about5.9424 spot pips under exact reciprocal arithmetic. This is
not a forecast, a measured average, or a tradable futures/spot identity. Spread
and impact would have to be calibrated without double counting the adverse
fill allowance. No standard-contract result is scaled into claimed micro
execution, liquidity or profitability. Freeze the actual native product,
multiplier/tick, fee and observed evening execution conditions before any hurdle.

## Prior history, book fit and failure risks

Connected GitHub at Claude source head
`6416de2dd39782eb4a43bd665c866409da4deb70` confirms the Tokyo idea and ranking
blobs are unchanged from the prior admitted source. The known NQ Tokyo/gotobi
proxy failed, and the prior recent hourly USD/JPY check's reported sign opposed
the importer-demand premise. Those are selected prior summaries, not newly
reproduced native 6J results. The original script was read only; it was not
imported/executed and its Yahoo request was not retried.

This is a direct-instrument readiness question in an already selected family,
not a newly discovered forced flow. A different ticker cannot erase the old
selection. A 6E port or a convenient hourly spot inversion would not validate
native yen-futures fills, costs or account paths.

The time lies in the **evening**, not the book's Tue–Fri01:00–03:00CT empty
slot. Actual exposure on candidate dates and correlation with VB/DT/RS are
unknown. Yen/risk-off exposure and existing evening legs could share losses;
a different ticker does not prove diversification. Thin-hour spread, stale
prints, persistent USD demand, bank/dealer netting, prehedging and event-clock
errors can eliminate the effect. Neither stop protection nor timely account
offsets have been established.

## Missing evidence and cheapest next gate

The user reports existing access, not presently exportable. Coverage, native
product, individual-contract/roll handling, timestamps and bar labels have not
been inspected or certified. No purchase or new account is needed or requested.
Before asking for substantial data effort, establish an authoritative historical
bank/fixing and settlement-day convention and credible evidence that residual
net demand reaches this contract in the proposed interval. Importers are a
plausible participant class, not a measured flow-size estimate.

If those facts support the question and existing data later becomes convenient,
propose a small documented native2018–22 windowed gross screen with ordinary-day
controls, full eligible-event accounting and exact realistic native costs. Freeze
the rule, selection history and decision before prices; do not collect only
favorable example dates. A low gross mean stops it before net design. Any such
empirical work needs separately authorized bounded scope and preregistration;
none runs automatically after this manual mechanics check.

Gross mean/t, native-cost net trade t, dailyNW5t, DSR, by-year/long-short metrics,
Sharpe/Sortino/PF/Calmar/Ulcer, placebos, MC and BASE/ADD/REPLACE/EMPTY benches:
**NOT MEASURED**, not zero and not passed. No PowerLanguage draft or trading
approval. Completed hunt counts and pause remain unchanged.

**Verdict: mechanical consistency PASS within the stated toy scope; hold at
NEEDS DATA / SOURCE CONFIRMATION. Do not prioritize a full export yet.**
