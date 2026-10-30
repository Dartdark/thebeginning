"""Render source/arithmetic/data-gate findings; no strategy return calculation."""
from pathlib import Path
import hashlib,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/qj_donchian_20261030'
OUT=ROOT/'analysis/outputs/codex_qj_donchian_20261030'
REPORT=ROOT/'agents/codex/results/qj_donchian_20261030.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def table(head,rows):return '\n'.join(['| '+' | '.join(head)+' |','|'+'---|'*len(head)]+['| '+' | '.join(map(str,r))+' |' for r in rows])
def money(x):return f'${x:,.2f}'
def main():
    f=json.loads((INPUT/'published_facts.json').read_text());a=json.loads((OUT/'arithmetic_audit.json').read_text());inv=json.loads((OUT/'inventory.json').read_text())
    size=pd.read_csv(OUT/'sizing_bounds.csv');mv=pd.read_csv(OUT/'published_multiplier_check.csv')
    sizes=table(['Contract','Min NAV from25%notional cap','Max contracts at$50K','Max contracts at$150K'],[[r.symbol,money(r.min_nav_one_contract_notional_only),r.notional_only_ceiling_50000,r.notional_only_ceiling_150000] for r in size.itertuples()])
    mismatch=table(['Contract','Reported signed market value','Quantity×price×multiplier','Missing factor'],[[r.symbol,money(r.reported_market_value),money(r.signed_notional_expected),f'{r.multiplier_ratio:g}×'] for r in mv.itertuples()])
    inventory=table(['Market','2018–22session labels','First17:01bar present','16:00close present'],[[z['market'],z['session_labels'],z['opening_minute_present'],z['standard_close_present']] for z in inv['market_summary']])
    text=f'''# QuantJourney 55-day Donchian: WATCH — data/accounting blocked; no plan admission

Summary: A daily cross-asset trend example, structurally incompatible with all four Apex plans as written.
Published results claim CAGR{f['cagr']:.2%},Sharpe{f['sharpe']:.2f},DD{f['max_drawdown_pct']:.2%} on$2million; these are not our backtest results.
Verified reporting issue: open-position market values omit contract multipliers; the packet fails its own sanity checks.
No personal admission: contract-aware reconciliation and executable roll data are missing; no independent return trial ran.

Evidence:[NEEDS DATA sheet](../evidence/qj_donchian_20261030.md).
Plan: no strategy preregistration admitted; source/data gate did not pass.
Scripts:[audit](../../../analysis/codex_qj_donchian_audit_20261030.py),[report](../../../analysis/codex_qj_donchian_report_20261030.py).
Output:[arithmetic](../../../analysis/outputs/codex_qj_donchian_20261030/arithmetic_audit.json),
[timestamp inventory](../../../analysis/outputs/codex_qj_donchian_20261030/inventory.json).
Own return trials:0. No parameter search, source-strategy return run, own2023+return run, portfolio simulation or MC code.

## Rule (as supplied, not a return replication)

Markets MES/MNQ/**CL/GC**, daily. Close above the previous55rows' highest high goes long; below their lowest low
goes short; otherwise retain the sign of the existing position. The current row is excluded from the channel.
ATR is a20-row simple mean of true ranges including today's bar. There is no ATR stop or other protective exit.
An existing position persists until opposite breakout or target-size reduction, potentially for months.

Every day, recompute whole contracts separately for each market:

```
min(floor(0.005 NAV / (ATR × multiplier)),
    floor(0.25 NAV / (price × multiplier)),
    floor(0.15 NAV / reference initial margin))
```

Submit target-current quantity as a market order, after the daily bar closes. The archived public engine describes
next-bar execution and the source packet says open. Do not backfill an order at its signal-day close.
A pending active order skips that symbol. No fresh breakout is necessary for daily resizing. When size reaches zero,
the implementation has no retained directional state; it stays flat inside the channel until another breakout.
Reversals must count both closing and opening contracts. The ATR sizing fraction is **not a maximum loss bound**.

Source cost model:1basis point adverse fill price plus$2.50/contract/side with$2.50minimum/order. Not tick-rounded.
Reference margins MES1584/MNQ2100/CL7000/GC10000 are constants from the public registry, not live broker requirements.
The example models full-notional cash and an additional reference-margin cap; it explicitly omits dated rolls,
variation margin and current buying-power enforcement. Those omissions matter for a real futures account.

## Results — author claims versus our checks

| Metric | Published packet,2019-05-06→2025-12-31 | Independent return replication |
|---|---:|---|
|Starting capital|$2,000,000|Not run|
|Total return|{f['total_return']:.2%}|Not run|
|CAGR|{f['cagr']:.2%}|Not run|
|Sharpe / Sortino|{f['sharpe']:.2f}/{f['sortino']:.2f}|Not run|
|Maximum DD / Calmar|{f['max_drawdown_pct']:.2%}/{f['calmar']:.2f}|Not run|
|Reported win rate / PF|{f['reported_win_rate']:.2%}/{f['reported_profit_factor']:.2f}|Trade analytics require reconciliation|
|Fill events / matched FIFO lots|{f['fill_events']}/{f['matched_fifo_lots']}|Not independent directional bets|
|Average / median lot holding days|{f['average_lot_holding_days']:.1f}/{f['median_lot_holding_days']}|Overnight/multiweek rule confirmed in code|

These modest risk-adjusted returns do not justify promoting the example. Low reported SPY beta could be useful
for diversification, but it does not measure correlation or incremental contribution to our19-piece personal book.
The screenshot says its curve was traced from a published chart; pixel paths are not a reproducible daily ledger.
The source uses a2%risk-free rate; our standard zero-rate Sharpe is not directly comparable without recalculation.

### Verified accounting problem, without overstating it

The hosted[JSON](https://backtester.quantjourney.cloud/strategies/example-orders-20-futures-donchian-contracts/performance_report.json)
uses quantity×price in its open-position market-value field; contract multipliers are missing:

{mismatch}

Its separate margin/exposure table correctly incorporates multipliers. Thus a reporting layer can be wrong while
another layer is contract-aware. **This does not establish that the headline NAV curve is wrong.** It does prevent
trusting unreconciled position/FIFO/profit-factor diagnostics. Open P&L fields show the same multiplier omission.
The[text report](https://backtester.quantjourney.cloud/strategies/example-orders-20-futures-donchian-contracts/performance_report.txt)
also flags volume consistency0.19 and failed sanity checks. Daily resizing can legitimately produce a FIFO-count
mismatch; that warning alone is not proof of an economic error. Realized/NAV profit gaps need opening/closing cash,
fees and remaining positions reconciled, not an assumption that every gap is invalid.

## Sizing and account placement

At the packet's **2025-12-31prices**, a single contract needs NAV≥4×price×multiplier solely because of the25%cap:

{sizes}

These are necessary bounds and upper quantity ceilings, **not actual allocated positions**. ATR/margin/direction
can reduce quantity further. They describe those prices, not every historical day or today's market.
The source's$2million return/DD cannot be divided proportionally into a$10K/$50K/$150Kstrategy. Replacing CL/GC
with MCL/MGC, relaxing the cap or forcing daily liquidation defines a new strategy; none was silently tested.

| Current home | Verdict | Basis and benchmark status |
|---|---|---|
|50K evaluation|No place as written|Multiweek holds violate intraday boundary; no account bench run|
|150K evaluation|No place as written|Same rule mismatch; no inferred pass rate|
|50K funded|No place as written|Same boundary; no payout/blow-up/timing claims|
|150K funded|No place as written|Same boundary; no150K payout comparison|
|Personal A–D/core/full|Unverified/data-blocked; no addition earned|Needs contract-correct cashflows/rolls and actual-capital BASE/ADD/REPLACE/EMPTY tests|

No independent whole/long/short,yearly,design/recent,t-stat or portfolio-return table is available; filling these
with the hosted results or an unadjusted splice backtest would invent validation. Current rosters were checked
against the existing[six-plan snapshot](../inputs/greenorb/plan_snapshot/manifest.json); nothing is changed.

## Data feasibility and why a new economic screen stopped

Owned OHLC exists for every market. A timestamp-only inspection of2017–22files produced:

{inventory}

These counts use an **assumed**17:01previousdate→16:00sessiondate CT aggregation. Raw CSVs have no contract or
timezone fields; this is not proof of the author's provider session or exact daily-open clock. Late first observations
and partial/missing sessions cannot be treated as verified next-open fills or silently compressed55session history.
Examples: all four2020-11-30sessions end around18:00the previous evening; CL2019-08-21/22are absent.
Most ES/NQ observed session starts lack the17:01close-stamped minute; filling at the first observed bar is an approximation.

The decisive carry-data limit is[NEW_CHAT_BRIEF](../../../NEW_CHAT_BRIEF.md)'s explicit statement that these
continuous series are unadjusted. They omit dated-contract identity and roll cashflows. A multiweek position spanning
a splice can acquire fictitious price-change P&L. Removing one roll minute does not recover the missing roll transactions.
No valid as-written multiweek carry return replication is supported by these exports alone. An intracontract or
roll-excluded partial study would answer a narrower question; silently truncating the position changes this rule.

Warm-up clarification: the stale shared checkout and codex branch lack NQ daytime2017, but the file **does exist**
on pinned Claude7a42ea(2017-05-01→12-29);[remote receipt](../inputs/qj_donchian_20261030/nq2017_remote_receipt.json).
We checked that before calling it missing. Its existence does not supply the executable roll chain, full overnight
history or the source's daily-data payload. No blanket claim that the repository lacks2017daytime is made.

### Exact source-engine access

The public v0.10.0[source contract](https://github.com/QuantJourneyOrg/quantjourney-bt/blob/v0.10.0/backtester/core.py#L898)
establishes next-bar timing. The[SDK data path](https://github.com/QuantJourneyOrg/quantjourney-bt/blob/v0.10.0/backtester/mixins/sdk_client.py#L177)
shows`source=yfinance`still uses authenticated QuantJourney preparation. Public code is not the full hosted reporting
build; original data hash/payload is absent. We inspected public sources and free packet artifacts; no account access,
API-key lookup, paid data or synthetic-sample substitution was attempted. The missing artifact is research data/code,
not permission to access live trading or credentials.

## Verification performed and retained lessons

**{a['count']}checks PASS**, using reviewed pure definitions on synthetic arrays/inert order stubs. They cover
ATR column alignment/simple averaging; invalid inputs and the three independent sizing caps;55prior-row channel
exclusion; daily carry/resizing; zero-position direction loss; reverse-order quantities; pending-order handling;
and all four published multiplier omissions. No `_credentials`,`main`,Backtester engine or authenticated API ran.
These checks validate specific mechanics/arithmetic, not profitability or an economic replication.

The[run manifest](../../../analysis/outputs/codex_qj_donchian_20261030/manifest.json) hashes original code,
selected source facts, archived public files, scripts and outputs. The source's2019–25results are already seen;
any subsequent test remains historical validation with family selection history, not a pristine holdout.

Prior family: TIER_LIST's weekly six-market momentum and Turtle review, plus the public-repositories Donchian baseline
review, already describe related approaches. A55-day rule is not a new forced-flow mechanism. Missing inputs alone do
not establish a promising strategy, so this example is retained as an accounting/execution reference rather than a
duplicate promising-alpha queue entry. Any future economically warranted personal test must be preregistered after
the data gate; no scout reservation, trial history or automation was changed.

Smallest justified next check: reconcile a closed lot for each market and aggregate contract-weighted realized/open
P&L,fees and daily NAV; then obtain a dated-contract roll ledger. Only after that, freeze a single actual-capital
personal definition and perform the cheap design screen. Do not optimize a screenshot or scale its CAGR mechanically.
Execution lessons retained in[EXECUTION_REFERENCES.md,E09](../EXECUTION_REFERENCES.md).

## Differences between MultiCharts code and the test

No MultiCharts implementation or new historical return test was produced because the input gate failed.
No live/VPS/broker/plan settings, credentials, ranking or allocations were changed.

For Claude: review`agents/codex/results/qj_donchian_20261030.md`, especially multiplier diagnostics versus headline NAV.
'''
    # Formatting only; the source snapshot and audit outputs remain the evidence.
    swaps={'CAGR4.67%':'CAGR 4.67%','Sharpe0.30':'Sharpe 0.30','DD16.70%':'DD 16.70%',
      'on$2million':'on $2 million','Source/helper':'Source/helper','Evidence:[':'Evidence: [',
      'Scripts:[':'Scripts: [','Output:[':'Output: [','trials:0':'trials: 0','own2023+return':'own 2023+ return',
      'previous55rows':'previous 55 rows','a20-row':'a 20-row','model:1basis':'model: 1 basis','plus$2.50':'plus $2.50',
      'with$2.50minimum/order':'with $2.50 minimum/order','MES1584/MNQ2100/CL7000/GC10000':'MES $1,584 / MNQ $2,100 / CL $7,000 / GC $10,000',
      'packet,2019':'packet, 2019','our19-piece':'our 19-piece','consistency0.19':'consistency 0.19',
      '**2025-12-31prices**':'**2025-12-31 prices**','the25%cap':'the 25% cap',"source's$2million":"source's $2 million",
      'a$10K/$50K/$150Kstrategy':'a $10K/$50K/$150K strategy','no150K':'no 150K','short,yearly,design/recent,t-stat':'short, yearly, design/recent, t-stat',
      'of2017–22files':'of 2017–22 files','**assumed**17:01previousdate→16:00sessiondate':'**assumed** 17:01 previous date → 16:00 session date',
      'compressed55session':'compressed 55-session','four2020-11-30sessions':'four 2020-11-30 sessions','around18:00the':'around 18:00 the',
      'CL2019-08-21/22are':'CL 2019-08-21/22 are','the17:01close-stamped':'the 17:01 close-stamped',
      'daytime2017':'daytime 2017','Claude7a42ea':'Claude 7a42ea','lacks2017daytime':'lacks 2017 daytime',
      'shows`source=yfinance`still':'shows `source=yfinance` still','**17checks PASS**':'**17 checks PASS**',
      'caps;55prior-row':'caps; 55 prior-row','`_credentials`,`main`,Backtester':'`_credentials`, `main`, Backtester',
      "source's2019–25results":"source's 2019–25 results",'A55-day':'A 55-day','P&L,fees':'P&L, fees',
      'in[EXECUTION':'in [EXECUTION','review`agents':'review `agents',
      '%,Sharpe':'%, Sharpe','%,DD':'%, DD','),[report]':'), [report]',
      'hosted[JSON]':'hosted [JSON]','The[text':'The [text','from25%notional':'from 25% notional',
      'at$50K':'at $50K','at$150K':'at $150K','existing[six':'existing [six','2018–22session':'2018–22 session',
      'First17:01bar':'First 17:01 bar','16:00close':'16:00 close','is[NEW_CHAT':'is [NEW_CHAT',
      '7a42ea(2017':'7a42ea (2017','12-29);[remote':'12-29); [remote','v0.10.0[source':'v0.10.0 [source',
      'The[SDK':'The [SDK','The[run':'The [run','a2%risk-free':'a 2% risk-free'}
    for old,new in swaps.items():text=text.replace(old,new)
    REPORT.write_text(text)
    files=sorted(p for p in INPUT.rglob('*') if p.is_file())+sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json')+[Path(__file__),ROOT/'analysis/codex_qj_donchian_audit_20261030.py',REPORT,ROOT/'agents/codex/evidence/qj_donchian_20261030.md']
    manifest=dict(status='Data/accounting gate stopped economic testing',own_return_trials=0,synthetic_checks=a['count'],
        account_simulations_run=False,source_claims_not_replicated=True,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in files])
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(report=str(REPORT),checks=a['count'],return_trials=0),indent=2))
if __name__=='__main__':main()
