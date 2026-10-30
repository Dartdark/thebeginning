"""Render the source/mechanics review from archived claims and executed traces."""
from pathlib import Path
import datetime,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/qj_stop_limit_20261030'
OUT=ROOT/'analysis/outputs/codex_qj_stop_limit_20261030'
REPORT=ROOT/'agents/codex/results/qj_stop_limit_20261030.md'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |'for r in rows])

def main():
    r=json.loads((OUT/'synthetic_results.json').read_text());c=json.loads((INPUT/'published_claims.json').read_text())
    assert r['scenario_count']==8 and not r['historical_backtest_run'] and r['economic_definitions']==0
    assert all(s['expectation_reproduced']for s in r['scenarios'])
    assert c['total_trade_events']==c['buy_events']+c['sell_events']
    assert c['closed_long_round_trips']==c['sell_events']
    assert c['closed_short_round_trips']==0
    for p,digest in r['source_hashes'].items():assert sha(ROOT/p)==digest
    commit=subprocess.check_output(['git','rev-parse','7ae772d'],cwd=ROOT,text=True).strip()
    receipt=dict(date_local='2026-10-30 America/Los_Angeles',pretest_commit=commit,
        command='/workspace/venvs/thebeginning/bin/python analysis/codex_qj_stop_limit.py',process_exit_code=0,
        completed_log_utc=datetime.datetime.fromtimestamp((OUT/'run.log').stat().st_mtime,datetime.timezone.utc).isoformat(),
        scope='8 synthetic execution scenarios;0 strategy-return trials',independent_review='pending',
        source_main_executed=False,credential_helpers_executed=False,account_tests_run=False,
        synthetic_result_sha256=sha(OUT/'synthetic_results.json'))
    save(OUT/'run_receipt.json',receipt)
    save(OUT/'trial_ledger.json',dict(task='user pasted strategy code',candidate='QJ O08 stop-limit protection',
        evidence_gate='DONT_TEST returns',economic_definitions=0,synthetic_scenario_groups=8,
        historical_validation_or_account_tests=0,shared_selection_history_preserved=True,scout_budget_changed=False,
        parameter_search_or_futures_adaptation=False,disposition='execution reference only; no eligible plan placement'))
    metrics=table(['Published statistic, 2001–2025','Value','Evidence'],[
        ['Total return',f"+{c['total_return_pct']:.2f}%",'Author packet/screenshot'],
        ['CAGR',f"{c['cagr_pct']:.2f}%",'Author packet/screenshot'],
        ['Sharpe / Sortino',f"{c['sharpe']:.2f} / {c['sortino']:.2f}",'Author packet; configured risk-free rate 2%'],
        ['Maximum drawdown',f"{c['max_drawdown_pct']:.2f}%",'Author packet/screenshot'],
        ['Trade events / closed long round trips',f"{c['total_trade_events']} / {c['closed_long_round_trips']}",'379 is not the independent closed-trade count'],
        ['Average closed holding period',f"{c['avg_holding_days']:.1f} days",'Author packet'],
        ['SPY total return',f"+{c['benchmark_SPY_return_pct']:.2f}%",'Full exposure; not a risk-matched comparison'],
        ['Average gross exposure',f"{c['average_gross_exposure_pct']:.2f}%",'Author packet'],
        ['Configured costs',f"{c['configured_one_way_slippage_bps']} bps one-way; ${c['commission_per_share']}/share, minimum ${c['minimum_commission_per_order']}/order",'Source settings, equity units']])
    scenarios=table(['Scenario','Actual synthetic behavior','Interpretation'],[
        ['Entry protection','Buy fills at $100.05; entry bar reaches $90 before protection is submitted','Separate daily callback leaves entry day unprotected'],
        ['Bearish crossing while arming','Only stop-limit submitted; previous signal becomes 0; next bearish callback sends no market exit','The one-off bearish crossing can be lost'],
        ['Gap below sell limit','Stop $96/limit $95.50 triggers; prices $90 then $80 leave 100 shares unfilled','Limit price is not a maximum-loss guarantee'],
        ['Recovery after trigger','Later recovery fills 100 shares at $95.50, $1 commission','Gross price bound respected; net proceeds $95.49/share'],
        ['Protective-order rejection','Rejected stop, no pending order; protection flag staysTrue; no next-callback retry','Boolean does not reconcile actual order state'],
        ['Ordinary bearish exit','Existing stop is cancelled, market sell of 100 shares queued','Expected ordinary transition works'],
        ['Partial protection','10 shares fill, 90 remain; cancel stop remainder and queue market sell of 90','Actual remaining quantity retained in this sequence'],
        ['Stop-out above SMA','No immediate reentry; a new down/up crossing later queues a buy','This is the declared crossover rule']])
    homes=table(['Home','Verdict','Measured account contribution'],[
        ['50K evaluation','Ineligible as written: daily ETF shares and multiday holding','Not run'],
        ['150K evaluation','Ineligible as written: daily ETF shares and multiday holding','Not run'],
        ['50K funded','Ineligible as written: daily ETF shares and multiday holding','Not run'],
        ['150K funded','Ineligible as written: daily ETF shares and multiday holding','Not run'],
        ['Personal portfolio','No eligible addition earned: weak source evidence and unsafe protection assumptions','Not run; no BASE/ADD/REPLACE/EMPTY claim']])
    text=f'''# QuantJourney stop-limit protection: REJECT as a plan candidate; retain execution reference

Summary: This is an educational daily-ETF order example, not demonstrated futures alpha.
Published CAGR {c['cagr_pct']:.2f}%, Sharpe {c['sharpe']:.2f}, DD {c['max_drawdown_pct']:.2f}% are author results, not our backtest.
Eight executed synthetic scenarios reproduced delayed protection, a lost bearish exit and stale protection state after rejection.
A stop-limit can remain unfilled through a large gap; its sell-price floor does not cap the position's loss.
No new return trial or account comparison passed the evidence gate; no place earned in any of the five homes.

Evidence: [pretest sheet](../evidence/qj_stop_limit_20261030.md). Plan:
[execution-only diagnostic](../plans/qj_stop_limit_mechanics_20261030.md), pretest commit `{commit}`.
Code: [mechanics harness](../../../analysis/codex_qj_stop_limit.py), [report](../../../analysis/codex_qj_stop_limit_report.py).
Outputs: [scenario traces](../../../analysis/outputs/codex_qj_stop_limit_20261030/synthetic_results.json),
[run receipt](../../../analysis/outputs/codex_qj_stop_limit_20261030/run_receipt.json),
[zero-return-trial ledger](../../../analysis/outputs/codex_qj_stop_limit_20261030/trial_ledger.json).

## Four source questions

1. **What is it about?** A QuantJourney daily-bar educational example for SPY, QQQ and IWM shares. Enter when
   SMA20 crosses above SMA50, allocate15% of NAV per new position, then submit a sell stop-limit with trigger4%
   and limit4.5% below the average entry. A bearish crossing submits a market exit when its branch is reached.
   This is code/documentation, not an academic paper; the author explicitly does not present it as optimized alpha.
2. **What does it find?** The screenshot and public packet report +{c['total_return_pct']:.2f}% over January2001–December2025,
   CAGR{c['cagr_pct']:.2f}%, excess-return Sharpe{c['sharpe']:.2f} and {c['max_drawdown_pct']:.2f}%DD. Those figures were
   checked against the published packet, not independently reproduced from market data. Our own evidence is
   eight synthetic order tests, including three implementation hazards, not a new profitable backtest.
3. **Why could it make money?** Long US equity exposure during SMA uptrends can participate in market gains.
   No forced participant, independent flow input or incremental alpha is identified. A stop-limit changes which
   prices can execute, at the expense of sometimes failing to execute; it does not create a positive edge or a
   bounded loss. Positive nominal dollars over25years are insufficient evidence of useful excess return.
4. **Can we build on it?** Retain the execution lessons, but **do not pursue a new strategy or add it to a plan**.
   Four intraday futures homes do not accept this daily ETF-share strategy as written. A personal ETF sleeve is
   possible in principle, but useful incremental contribution is unverified and this source does not earn that stage.
   No SMA optimization, futures substitution or stop-market rescue is justified by this example.

## Published results: source evidence, not independent replication

{metrics}

The reported379trade events comprise191buys and188sells; the closed sample is188long round trips and zero shorts.
Selling a long is an exit, not evidence of a short strategy. The average holding period is77.2days, so this is
not an intraday candidate. Full SPY exposure and average25.35% strategy exposure are unequal; underperforming SPY
alone is not a fair risk-matched alpha test. Nevertheless Sharpe0.02 relative to the packet's2% risk-free rate
is weak positive evidence. No current-portfolio benefit can be inferred from these statistics.

The dashboard's3.99% volatility is a rolling-window value; its run log reports4.91% full-sample annual volatility.
Those are different statistics. We do not replace either with an independently calculated estimate.
The supplied configuration uses$100,000 initial capital,5bps one-way slippage and equity commissions of$0.005/share,
minimum$1/order. Do not translate percentage allocations or these fees directly to native MNQ/MES contracts.

Primary sources:
[public example packet](https://backtester.quantjourney.cloud/strategies/example-orders-08-stop-limit-protection),
[structured source report](https://backtester.quantjourney.cloud/strategies/example-orders-08-stop-limit-protection/performance_report.json),
[pinned strategy](https://github.com/QuantJourneyOrg/quantjourney-bt/blob/4f403d853833e1daa6de01c5b6c6cb3983dc0044/strategies/example_orders_08_stop_limit_protection.py).
The public report was generated2026-07-11 and inspected2026-10-30. Archived
[claims](../inputs/qj_stop_limit_20261030/published_claims.json) preserve attribution.

## What we actually executed

Pinned public source: QuantJourneyOrg/quantjourney-bt commit
`4f403d853833e1daa6de01c5b6c6cb3983dc0044`, current public version0.12.5. The packet names0.10.0+private;
we did **not** establish version parity with that historical engine. The canonical upstream strategy class matches
the pasted logic; source hashes and Apache license are archived. A disconnected base supplies feature tables and
average entry prices. AST extraction executes only the strategy class. The four reviewed pure execution modules
(orders, fill engine, slippage, commissions) run unchanged; the SDK/API package initializer, credential helper,
source main and simulator/core are not executed. Core/simulator source was inspected to confirm scheduling.

The reviewed public simulator fills prior pending orders before calling the strategy after each daily close.
An order submitted at that callback first becomes eligible on the next daily bar. There is no source entry-fill
hook to arm an attached protective child during the entry bar. Our delayed-protection result applies to this
explicit schedule; it is not a claim that every stop-limit implementation has this delay.

{scenarios}

All eight assertions reproduced their predeclared expectations. **That is a diagnostic success, not a safety PASS.**
Prices/dates in fixtures are invented, not observations of those dates. The rejected-order reason is injected;
no broker rejection frequency is estimated. Partial fills in scenario7 use a1% prior-volume participation cap
to expose the state transition; this is not the source's historical fill rate or a new strategy variant.

The bearish-exit issue is stronger than a one-bar delay: the `elif pos>0 and not has_stop` branch submits the
stop and then saves the new bearish signal. If the next signal remains bearish, `prev` is already0, so the
market-exit branch does not fire. The normal bearish transition works after protection is already flagged.
Likewise, `_has_stop_limit=True` is set after submission without checking rejection status. In the forced
rejection fixture, no actual protective order remains, yet the next callback sees the flag and does not retry.
These are source/harness implementation findings; they do not quantify financial damage in the published run.

## Why no new historical return or portfolio test ran

The pretest evidence sheet is **DON'T TEST economic returns**: this is a generic SMA/order demonstration with
weak reported excess return, no new economic mechanism, direct account incompatibility and unresolved exact
historical engine/data provenance. The instruction to backtest uploads does not bypass that evidence gate.
The completed work here is source verification and executed execution-mechanics tests, **not a return backtest**.

A bounded owned/free check was still completed. No verified owned SPY/QQQ/IWM OHLC set was found. The existing
`data/SPY_daily.csv` is close-only with index/futures-scale numbers, so it was not treated as native ETF prices.
Yahoo's public SPY chart request returned a proxy-tunnel403; that endpoint was not retried or bypassed. A public
GetPriceData repository contained scripts but no archived CSV panel. QuantJourney's credential-free sample data
are deterministic generated prices, so they cannot validate historical profitability. No fictitious opens/highs/lows,
missing returns, guaranteed limit fills or futures proxies were manufactured. See the
[access receipt](../inputs/qj_stop_limit_20261030/access_receipt.json).

No2018–22 design return series,2023+ validation, confidence interval, random-return placebo, Monte Carlo return
simulation, native fill saving or independent raw-spec economic check exists for our work. Their values are
unavailable, not zero. A new future question would need a distinct justified hypothesis and its own complete
evidence/preregistration; this review is not an invitation to keep optimizing these SMA periods.

## Explicit placement in all five homes

Read-only plan sources refreshed at Claude `7ce07ece525fa16e95ac2221a27521d317b2b05c`:
[snapshot manifest](../inputs/qj_stop_limit_20261030/plan_snapshot/manifest.json).

{homes}

No ADD/REPLACE/EMPTY benchmark was earned. Lack of admission is not measured harm to all five portfolios.
No baseline payouts, pass rates, blowup rates or personal-capital changes are inferred from ETF daily returns.
No shared plan, ranking, live strategy, account setting, key, VPS or automation was modified. No PowerLanguage
or platform installation was attempted. Independent verification remains pending.

## Retained reference and next action

Save the order lesson in [EXECUTION_REFERENCES E36](../EXECUTION_REFERENCES.md#e36--stop-limit-protection-price-control-is-not-a-loss-cap),
cross-linked to E03/E05/E18. A stop-limit exchanges execution certainty for a price constraint; protective-order
state must follow actual acknowledgements/status, and a fill-to-protection gap must be explicit. No new execution
policy was installed. No TODO promising-strategy entry: missing inputs and educational examples alone do not
establish merit for that queue. **Move on as a strategy candidate.**

Reproduce the finite mechanics and report from repository root:
```
/workspace/venvs/thebeginning/bin/python analysis/codex_qj_stop_limit.py
/workspace/venvs/thebeginning/bin/python analysis/codex_qj_stop_limit_report.py
```
For Claude: `agents/codex/results/qj_stop_limit_20261030.md` — source/order review; eight synthetic groups;
zero economic return trials or current-portfolio simulations. Do not describe it as independently backtested alpha.
'''
    # Normalize specific prose tokens without touching identifiers, hashes or URLs.
    replacements={'allocate15%':'allocate 15%','trigger4%':'trigger 4%','limit4.5%':'limit 4.5%',
        'January2001–December2025':'January 2001–December 2025','CAGR1.99%':'CAGR 1.99%',
        'Sharpe0.02':'Sharpe 0.02','14.18%DD':'14.18% DD','over25years':'over 25 years',
        'reported379trade':'reported 379 trade','comprise191buys':'comprise 191 buys','and188sells':'and 188 sells',
        'is188long':'is 188 long','is77.2days':'is 77.2 days','average25.35%':'average 25.35%',
        "packet's2%":"packet's 2%",'dashboard\'s3.99%':"dashboard's 3.99%",'reports4.91%':'reports 4.91%',
        'uses$100,000':'uses $100,000',',5bps':', 5 bps','of$0.005':'of $0.005','minimum$1':'minimum $1',
        'generated2026':'generated 2026','inspected2026':'inspected 2026','version0.12.5':'version 0.12.5',
        'names0.10.0':'names 0.10.0','scenario7':'scenario 7','a1%':'a 1%','already0':'already 0',
        'No2018':'No 2018',',2023+':', 2023+','188long':'188 long','379 is':'379 is'}
    for old,new in replacements.items():text=text.replace(old,new)
    REPORT.write_text(text)
    save(OUT/'artifact_manifest.json',dict(pretest_commit=commit,mechanics_code_sha256=sha(ROOT/'analysis/codex_qj_stop_limit.py'),
        report_code_sha256=sha(__file__),report_sha256=sha(REPORT),
        files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p))for p in OUT.iterdir()if p.is_file()and p.name!='artifact_manifest.json']))
    print('PASS:8 synthetic expectations, frozen source hashes and event/round-trip arithmetic; report saved:',REPORT)

if __name__=='__main__':main()
