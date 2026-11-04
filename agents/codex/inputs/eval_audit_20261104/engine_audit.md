# Evaluation engine audit: inherited pass rates require a corrected replay

Summary: The previous replay is not a reliable optimizer for the current EOD evaluations.
It applies a PA floor lock to evaluation accounts, substitutes threshold fills for DLL liquidation, and uses21sessions instead of the purchased30calendar-day clock.
The50K/150K engines disagree about same-minute target/risk ties; synthetic examples change pass/fail outcomes.
A research-only chronological replacement and35synthetic checks are supplied; no historical strategy or account outcomes were calculated by this subtask.
Actual purchased product, expiry, fees and installed target-guard settings still require account-specific confirmation before a native-performance claim.

## Scope and evidence

Read-only Claude source pin: `13e29ca7b45daabeb0ed2d8c286448610f594dab`.
The latest sizing study is `analysis/eval_sizing_bench.py`; the native common-path builder is
`analysis/codex_eval_paths_20261104.py`, supplied by the separate path-builder subtask.
This audit does not change trading plans, installed strategies or shared legacy engines.
Public primary-source access receipts are in `primary_rule_receipts.json`.
They describe currently published product rules; they do not prove an individual account's purchased contract,
the historical product rules at purchase, dashboard expiry or actual broker fills.

## Current public EOD evaluation rules

|Rule|50K|150K|Implication|
|---|---:|---:|---|
|Net profit target|$3,000|$9,000|Commissions and actual liquidation costs count.|
|Initial EOD trailing allowance|$2,000|$4,000|Initial floors$48,000/$146,000; touching the operative floor intraday fails.|
|Fixed daily loss limit|$1,000|$2,000|Realized plus unrealized; prevailing-market liquidation and pause, not automatically account failure.|
|Aggregate max position|6mini/60micro|12mini/120micro|Across instruments; an excess order is rejected.|
|Trading-day minimum|None|None|A one-day pass is permitted.|
|Access|30continuous calendar days|30continuous calendar days|Use explicit purchase/expiry, not a21trading-session surrogate.|

The EOD floor is recalculated at16:59:59Eastern, applied next session and never moves down. Before target,
it is the highest achieved closing balance less the trailing allowance. The official floor explanation
specifically distinguishes **PA** lock at starting balance+$100 from **evaluation** treatment:
Rithmic/WealthCharts evaluation floors cap at the target balance; Tradovate evaluation floors keep trailing.
For a policy that stops after a valid net pass, both evaluation versions are unbounded before target.
Consequently the inherited$50,100/$150,100 cap understates evaluation risk once EOD profits ratchet above it.

DLL resets at18:00Eastern/17:00Chicago and does not reset a previously increased EOD floor.
The official DLL page expressly permits the realized liquidation balance to finish below the DLL threshold
because of market movement and fills. Crossing the actual EOD floor during liquidation still fails.
Billing says30days from purchase and17:00Chicago Day30expiry. The modeled helper exposes its date+30close
convention; an actual dashboard expiry overrides it. The simulation requires an explicit expiry epoch.
The evaluation purchase fee is not implied by the account's nominal balance. The latest source study's
single`FEE=249` for both sizes is an assumption, not a verified50Kprice receipt.

## Material inherited defects and limitations

|Implementation|Finding|Effect on interpretation|
|---|---|---|
|`analysis/combine_levers_test.py:challenge`|50K target wins same-minute target/floor ties; PA-like floor cap; DLL snaps balance to limit; fixed21sessions.|Not a conservative chronological evaluation replay.|
|`analysis/plan_150k_test.py:evaluation`|150K floor wins equal-index ties, unlike50K; same wrong eval cap, exact-DLL fills and21session clock.|The two published pass rates do not share one timing model.|
|`analysis/portfolio.py:paths`|Missing adverse marks can be replaced by entry; independently adverse sleeve paths are summed.|Missing held prices can disappear; opposite same-asset sleeves can suffer mutually impossible simultaneous extremes.|
|`analysis/funded_lab.py:with_slippage`|Moves entry/market-stop slippage into exit adjustment.|Final trade dollars can reconcile while pre-exit adverse equity omits native entry costs.|
|`analysis/account_tools.py:pass_odds`|Daily-only equity, no intraday DLL/floor enforcement; fallback60day horizon.|Useful daily proxy only; not exact evaluation pass odds or a selection objective.|
|`analysis/eval_sizing_bench.py` at the source pin|Uses the inherited engines/paths; studies reduced current-sleeve sizes and a loss cap.|Its findings cannot establish optimality across strategies, integer admissions or current evaluation rules.|
|Prior evaluation Bridge adapter|Monday starts omit Sunday19:00→midnight marks.|Reported bridge gains cannot justify deleting its Sunday adverse exposure.|
|Prior funded OT/CLS adapters|Whole-day adverse proxies and incomplete source history.|Cannot infer native exposure collisions or extend missing OT coverage with zero returns.|

Whole-book continuous multipliers can also turn already-quantized strategy quantities into fractional micros.
This is unsuitable for the actual-size account comparison. Reusing exact source entry/exit ledgers does not
establish original quote chronology: some saved report-to-minute timestamps are first-touch inferences.
Crossing midnight is not by itself illegal: the permitted Sunday reopen→Monday exposure must stay in its
17:00→16:00account session and carry the entire observed risk path.

The corrected replay must retain actual opening cash and floor; starting every failed account at nominal
ignores its accumulated floor/cushion. Four account-specific forensic records are a separate subtask.
The original cached`g24`/extended account-path pickles were absent at audit start. Existing research ledgers
and owned raw minute files must be rebuilt deterministically; absent caches are not execution evidence.

## Replacement core and integration contract

`analysis/codex_eval_engine_20261104.py:simulate` accepts:

```python
simulate(prices, times, sessions, trade_events, point_values,
         commission_per_side, slippage_points, cutoff_times, expiry_time,
         rules=EOD50, initial_equity=None, initial_floor=None,
         risk_fraction=0, aggregate_stop_fraction=1,
         cushion_buffer=0, aggregate_stop_reserve=True,
         block_key_after_rejection=True,
         node_rows=None, segment_min=None, segment_max=None,
         segment_missing=None, record_logs=False)
```

`prices[N,A]` is one common executable-reference mark per asset/event. Events contain row,tradeID,keyID,
assetID,action,side,rawfill,source-known-stop-distance,requested-integer-micros,fillkind.
The caller owns source clocks, sampled-history masks, source stop definitions, conditional OHLC ordering,
hard fill mismatches and actual account starts. The core does not regenerate strategy entries after a
rejected source entry and does not backfill missing marks or invent native fills.

The core maintains net broker exposure and aggregate basis per asset. Opposing virtual positions therefore
share one price. Even with zero net exposure and different opening prices, their locked basis profit remains
known when a quote is absent. Source trades retain individual stops/exits; fees are charged on their orders.
An account-wide forced flatten uses one net liquidation order per asset. Broker-net-flat equity can meet
the realized target even with opposing virtual tickets still open; clearing that locked-basis bookkeeping
requires no market order or extra liquidation fee. Excess requested position rejects the order; quantities
never become fractional. A zero-allocation source key requires no quote. Raw fill NaNs remain in the tape;
they produce account UNKNOWN only when their nonzero requested entry or active exit is actually reached.

Every common mark checks inclusive floor before target. DLL then closes at that mark with native configured
costs; it never snaps to an ideal threshold. Already-active source exits precede discretionary new entries
at an identical event; a same-event own entry/exit executes entry then its own exit. Other ambiguous timing
is caller-declared. Missing held net prices, unmatched nonzero-allocation source fills, active positions past
an unquoted daily-flat deadline or session boundary return UNKNOWN.

The optional governor caps each new trade by all of:

1. `risk_fraction × remaining floor headroom`, after the frozen cushion buffer;
2. `aggregate_stop_fraction × headroom − open nominal-stop reserve`;
3. `remaining daily-loss room − open nominal-stop reserve`.

Round-trip native fees/slippage enter the per-contract new risk allowance; existing reserve uses current
mark to the original source-known stop plus exit costs. No-stop trades reject in the governed profiles;
their stop is never inferred from a later losing exit. Static profiles preserve their requested sizes.
Rejected trades can block the same key until next account session, a frozen allocator assumption that avoids
phantom conditional re-entries. This reserve is conservative admission logic, not an assumption that opposite
sleeves simultaneously realize their individual adverse extreme. Actual account equity still uses net price.

Performance uses builder event/session/cutoff nodes and fixed-position segment bounds only to **prove** a
segment cannot cross any operative floor, DLL, target or clock boundary. Potential crossings walk the same raw
common-price tape. Output`minimum_equity` is exact over visited nodes/potential-risk segments in fast mode;
`minimum_equity_lower_bound` is a conservative bound and is not exact joint drawdown. Exact excursion reporting
must rewalk the frozen survivors without skipping. Logs are optional and scale with events/sessions, not raw ticks.

## Remaining material assumptions

- The builder's common OHLC phase sequence is conditional intraminute reconstruction. It does not recover
  the order of real quotes or simultaneous cross-asset events. Results require phase sensitivity or uncertainty
  disclosure; an artifact PASS is not independent economic verification.
- The modeled account target guard flattens the net account at an observed guard crossing and charges market
  liquidation costs. It is not a trade match to the source's per-chart, next-bar limit orders. Source
  `Apex_Target_Guard_v2.txt` defaults to$53,050/$159,050, but its header says NOT INSTALLED YET. Actual installation,
  account equity reporting, other-chart positions and live input thresholds are not established here.
- A source ledger is conditional on its own entry/exit logic. Skipping an entry, changing order size or sharing
  a broker position can change later chart behavior. The research allocation/blocking policy must be frozen
  and any native chart/account differences disclosed.
- Per-key source coverage is mandatory. A holiday/closed exchange is not a missing tradable quote, while
  missing prices during held tradable time are not a no-trade/zero-return observation. The builder/calendar
  audit must preserve observed reopening gaps and stop clocks without filling closed intervals.
- Source fees, purchase date/expiry, platform/product and account-specific current floor need explicit receipts.
  For the prospective sizing research, register assumptions and sensitivity; do not present them as verified
  historical account facts or automatically revise installed settings.

## Synthetic evidence and recommendation

Run:

```sh
/workspace/venvs/thebeginning/bin/python analysis/codex_eval_engine_fixtures_20261104.py
```

`engine_fixtures.json` records35checks, including100random raw-walk/segment-skip parity tapes. Fixtures cover
native costs, net target, inclusive floor, DLL gap/secondary floor failure, proper EOD ratchet, opposing/net-zero
basis, max-contract rejection, integer floor+DLL governor, unknown-stop rejection, missing quotes/fills, deadlines,
zero-allocation/NaN handling, broker-net-flat target realization and same-time exits/own roundtrips. They also isolate legacy function bodies without
loading market data: one same-minute tie passes in the50Kfunction but times out in the150Kfunction under the
same parameters; one four-day synthetic sequence passes under the PA lock but fails under the eval floor.
These are rule/correctness demonstrations, not investment performance or calibrated pass probabilities.

Use the new research core with the frozen native-ledger/common-price builder after the parent preregistration.
Retain old results as legacy-model selection history, not erased trials or current optimality evidence.
Independent economic/source/fill review is still pending; this subtask's35synthetic checks are not that review.
