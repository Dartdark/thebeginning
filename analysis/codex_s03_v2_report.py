"""Assemble the S03v2 decision report from saved outputs, without new trials."""
from pathlib import Path
import json
import hashlib
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"analysis/outputs/codex_s03_v2"
DEST=ROOT/"agents/codex/results/s03_v2.md"


def n(x,d=0):return "N/A" if pd.isna(x) else "∞" if np.isinf(x) else f"{x:,.{d}f}"


def table(headers,rows):
    return "\n".join(["|"+"|".join(headers)+"|","|"+"|".join(["---"]*len(headers))+"|"]+
        ["|"+"|".join(map(str,row))+"|" for row in rows])+"\n"


def main():
    stats=pd.read_csv(BASE/"diagnostics/standard_stats.csv")
    s=stats[(stats.fee_micro==1.04)&stats.model.isin(["v2_raw","v1_raw"])]
    both=s[s.group=="both"]
    v2=both[(both.model=="v2_raw")&(both.period=="2018_plus")].iloc[0]
    v1=both[(both.model=="v1_raw")&(both.period=="2018_plus")].iloc[0]
    trials=json.loads((BASE/"diagnostics/trial_counts.json").read_text())
    funded=pd.read_csv(BASE/"accounts/funded_summary.csv")
    fd=pd.read_csv(BASE/"accounts/funded_paired_differences.csv")
    ev=pd.read_csv(BASE/"accounts/evaluation_summary.csv")
    ed=pd.read_csv(BASE/"accounts/evaluation_paired_differences.csv")
    body=[f"""# S03 noise-area momentum v2: REJECT current-plan promotion
Summary: V2 is profitable and improves v1's risk profile, but earns no qualifying allocation under the current gates.
Full v2: {int(v2.trades)} trades, ${v2.avg:.2f}/NQ, PF{v2.profit_factor:.3f}; DD falls {100*(1-v2.max_dd_including_start/v1.max_dd_including_start):.1f}% versus no stop.
t={v2.t:.2f} clears {trials['t_threshold']:.2f}, but DSR={v2.dsr_conservative_latest:.3f} misses0.95. Funded placement disappoints; personal gains require more capital.
Some starter-personal gains and a tiny150K evaluation gain are plausible, not promotion evidence. Keep the current plans; move on.

Plan: `agents/codex/plans/s03_v2.md`, **54bbba745006f1d20805ef9daab0d130abf4e6fe**, committed before returns.
Source: unchanged `agents/codex/inputs/s03_v2/source.txt` (user's v2 code.txt), SHA256
`08cac31254f8494415e522c086fd37ece5f34a0b43ae11f4fe4bf8ed51d0d758`.
Scripts: `analysis/codex_s03_v2_replay.py`, `_portfolio.py`, `_diagnostics.py`, `_check.py`, `_exposure.py`, `_report.py`.
Outputs: `analysis/outputs/codex_s03_v2/`. Four fixed streams; no search, parameter rescue or side selection.
Latest Claude **760df4273f039beab7be62d789df97935f65c64c**: all47 baseline dependencies unchanged; existing caches reused.

## What was tested

This upload is **S03 noise-area intraday momentum**, not R2Vault and not the earlier CODE.txt implementation.
NQ one-minute full-session bars; New York signals converted to CT. RTH open08:30CT, prior accepted close15:00CT.
At09:00,09:30,...14:30CT, a close above the upper noise band and VWAP buys; below the lower band and VWAP sells short.
Noise is the mean absolute same-minute move from the open over14 previously accepted sessions. Bands account for
the opening gap. Band/VWAP exits are checked at the same30-minute decision closes, not continuous trailing stops.
Orders fill at the next observed bar's open. Opposite entries reverse once: one old exit plus one new unit.

V2 adds a protective stop of **0.4 × raw sigma at signal × signal close**, anchored at the actual fill. It is active
on the entry minute. SourceQty1 and SetStopContract make the dollar loss per contract; BigPointValue correctly scales
NQ versus MNQ. No target. V1 sets StopSigma=0. No long-only rescue or alternative stop size was tested.

The code prearms its built-in stop. Official [SetStopLoss documentation](https://www.multicharts.com/trading-software/index.php?title=SetStopLoss)
supports intrabar/entry-bar exits; [SetStopContract](https://www.multicharts.com/trading-software/index.php?title=SetStopContract)
sets the per-contract basis. This is not evidence of a missing entry-bar stop. Tick/platform fill parity remains unverified.

The four registered streams are v2_raw, v2_apex, v1_raw, v1_apex. The Apex version adds a15:55CT/early11:30CT fallback.
**Raw and Apex fills are identical in this run**: the source's15:00CT EOD exit already closes every trade intraday.
There are zero final open positions. Four streams are counted conservatively; identical guards are not independent evidence.

## Costs, assumptions and source fidelity

Main standalone tables are per **one NQ**, using$1.04/MNQ-equivalent round-trip commission ($10.40/NQ) plus one tick
per market/stop fill ($10/NQ total). Fee stress is$1.24/MNQ, applied to both plan and candidate. Personal fee is$1.275/MNQ,
plus the same slips. Every round trip pays, including reentries and reversals. Commission is reserved at entry.

Stop prices round away from entry to the valid0.25tick, a conservative declared proxy. Opening gaps use the opening
price; adverse paths stop at the actual exit, excluding later minute extremes. Source EOD orders use next observed
open. The modeled Default/CME16:00CT SetExitOnClose fallback executed no actual trades, so it does not explain the result.
Volume is interpreted as total minute volume; an MC chart using up-volume/tick volume can differ.

The supplied ring buffer is reproduced literally. A day is accepted when its15:00CT close exists and its calendar
predicate permits it; earlier missing minutes can leave zero history cells. There are163 v2 and134 v1 trades using
at least one such prior session. Those trades are retained and labeled, not repaired or selected away. One held
quote-gap trade occurs in each version. Raw results retain it; account comparisons exclude the affected day.

## Standalone, whole/long/short

2018–2026-10-09;2023+ is already examined history, not a fresh untouched holdout. No2017 RTH reproduction.
Dollar profits/DD here are NQ research units, not proposed NQ sizing. Ulcer uses the repository$50K reporting-capital convention.
"""]
    q=s[s.period=="2018_plus"]
    body.append(table(["Version","Side","n","Win%","$/trade","PF","t","DSR","Sharpe","Sortino","Calmar","Ulcer%","Daily DD"],
        [[r.model,r.group,int(r.trades),n(r.win*100,1),n(r.avg,2),n(r.profit_factor,3),n(r.t,2),n(r.dsr_conservative_latest,3),
          n(r.sharpe,2),n(r.sortino,2),n(r.calmar,2),n(r.ulcer,2),n(r.max_dd_including_start)] for r in q.itertuples()]))
    body.append("\nDesign/recent results, closed trades by entry date; all trades close the same date:\n")
    q=s[s.period.isin(["2018_22","2023_plus"])]
    body.append(table(["Version","Side","Period","n","$/trade","Net","t"],
        [[r.model,r.group,r.period,int(r.trades),n(r.avg,2),n(r.total_nq),n(r.t,2)] for r in q.itertuples()]))
    body.append("\nAnnual whole-strategy net per NQ (2026 partial):\n")
    body.append(table(["Year","v1 no stop","v2 sigma stop"],[[yr]+[n(both[(both.model==m)&(both.period==yr)].total_nq.iloc[0])
        for m in("v1_raw","v2_raw")] for yr in map(str,range(2018,2027))]))
    boot=pd.read_csv(BASE/"diagnostics/bootstrap2023_mean_total_ci95.csv")
    q=boot[(boot.fee_micro==1.04)&boot.model.isin(["v2_raw","v1_raw"])]
    body.append("\n2023+ marked net,20-day-block95% intervals,5,000 resamples:\n")
    body.append(table(["Version","Side","Actual net","95% total interval"],
        [[r.model,r.group,n(r.total_actual),f"[{n(r.total_ci95_lo)}, {n(r.total_ci95_hi)}]"] for r in q.itertuples()]))
    body.append(f"""
Full v2 t clears the known-trial threshold; DSR does not. Known lower bound is **{trials['effective_n']}**
({trials['ranked_items']} ranked +17 prior unranked +4 streams). Unknown author stop/WFO searches add uncertainty.
The code's claimed0.4 walk-forward selection/plateau was not independently supplied or verified. No published-SPY
exemption is used for this selected NQ adaptation. The original [author description](https://concretumgroup.substack.com/p/beat-the-market-with-intraday-momentum)
concerns SPY; it does not establish this NQ stop extension. Recent shorts are weak; they were reported, not dropped.

## What the stop actually changes

Reexecuting both versions matters. All1,844 original v1 entries remain in v2, plus525 additional entries after stopouts.
At the common entries, v2 net is$196,127 versus v1$259,897; extra v2 entries contribute$80,680. The full net improvement
is$16,910. Since2023, common-entry profit falls$38,740 and new entries recover$36,869: **recent total profit is$1,871 lower**.
Thus v2 improves drawdown/Sharpe, but it is not a free increase in profits or a fixed-trade stop overlay. In particular,
do not attribute the entire change to cutting losing original trades. Full attribution is in `diagnostics/stop_attribution.csv`.

## Placebos and standalone Monte Carlo

1,000 conditional random-side and1,000 independent random-time/side paths per stream, same sigma/no-stop and future
band/VWAP/EOD exits. One position; skip a later source event if the prior null is held at its signal close. Time controls
choose one of12 fixed check times/day and independent50/50 side, only from the coverage/calendar eligible universe;
there is no conditioning on whether the actual strategy subsequently trades. Eventcounts differ. Nulls are falsifiers,
not optimized alternative strategies. Control DD is closed-trade equity, not intraday account risk.
""")
    placebo=pd.read_csv(BASE/"diagnostics/placebo_summary.csv")
    q=placebo[placebo.model.isin(["v2_raw","v1_raw"])&(placebo.period=="2023_plus")&
        (((placebo.control=="random_side")&(placebo.reference_scope=="all_source_closed_entries"))|
         ((placebo.control=="random_time")&(placebo.reference_scope=="actual_entry_days_in_control_calendar")))]
    body.append(table(["Version","Null","Actual $/trade","Null median $/trade","p(total)","p(expectancy)"],
        [[r.model,r.control,n(r.actual_avg_nq,2),n(r.null_expectancy_p50,2),n(r.p_null_total_ge_actual,3),n(r.p_null_expectancy_ge_actual,3)] for r in q.itertuples()]))
    mc=pd.read_csv(BASE/"diagnostics/standalone_mc.csv")
    q=mc[(mc.model=="v2_raw")&(mc.group=="both")&(mc.fee_micro==1.04)&(mc.period=="2018_plus")]
    body.append("\nV2 standalone one-year daily bootstrap (5,000 histories); EOD risk approximation only:\n")
    body.append(table(["MNQ","Median profit","DDp95","P(loss)%","EOD trail hit%"],
        [[r.size_mnq,n(r.daily_pnl_p50),n(r.daily_dd_p95),n(r.daily_p_loss*100,1),n(r.daily_p_trail_hit*100,1)] for r in q.itertuples()]))
    body.append("""
The actual-side fixed-entry walker reproduces all8,426 recorded exits across the four streams. This checks two
chronological formulations, but both share features and rounding; it is not an independent platform replication.
Recent side/time controls support momentum value. That does not override the DSR requirement or account results.

## Funded plans: addition, replacement and empty-slot control

1,000 paired L20 whole-day histories (seeds1..4),250/500days; current full50K/150K rosters, integer cushion sizing,
refs$1,500/$3,000. Matched fee1.04 results below; all sizes, controls, fee1.24 and five cohorts are saved.
""")
    q=funded[(funded.fee==1.04)&(funded.cohort=="2018_plus")&(~funded.config.str.startswith("v1"))]
    body.append(table(["Account","Allocation","1y payout mean","2y mean","Blown%","Median days to6"],
        [[r.context,r.config,n(r.year1,1),n(r.year2,1),n(r.blown*100,1),n(r.days6,1)] for r in q.itertuples()]))
    q=fd[(fd.fee==1.04)&(fd.cohort=="2018_plus")&(fd.config=="v2_apex__ADD1")&(fd.reference=="BASE")&fd.metric.isin(["year1","year2","blown"])]
    body.append("\nPaired ADD1 effects versus BASE; intervals measure MC sampling precision conditional on observed history:\n")
    body.append(table(["Account","Metric","Change","95% interval"],
        [[r.context,r.metric,n(r.delta,3 if r.metric=="blown" else 1),f"[{n(r.lo,3 if r.metric=='blown' else 1)}, {n(r.hi,3 if r.metric=='blown' else 1)}]"] for r in q.itertuples()]))
    body.append("""
V2 beats the no-stop challenger on funded risk, but that is not the decision benchmark. It fails to improve BASE
and EMPTY consistently. Since2025, the2MNQ VB replacement loses$3,363 versus50K BASE and$3,544 versus EMPTY;
150K loses$278 versus BASE (CI crosses zero) and$1,086 versus EMPTY (CI stays negative). No funded place is established.
Payout quantiles, six-payout probabilities and the separate fee stress are in `accounts/`. Quantiles include all histories;
outcomes below p5 remain possible, including zero. Censored six-payout times are infinity, not omitted failures.

## Evaluations: real21-session windows

Full windows must lie inside their cohort, with no calendar compression across unknown days. Existing50Kpass-first /
150Kbreach-first same-minute conventions remain. Actual150K dollar risks are scaled before integer flooring.
""")
    q=ev[(ev.fee==1.04)&(ev.cohort=="2018_plus")&(~ev.config.str.startswith("v1"))]
    body.append(table(["Account","Allocation","Pass%","Fail%","Median pass days"],
        [[r.context,r.config,n(r.passed*100,2),n(r.failed*100,2),n(r.median_pass_days,1)] for r in q.itertuples()]))
    row=ed[(ed.fee==1.04)&(ed.cohort=="2018_plus")&(ed.context=="150K_evaluation")&
           (ed.config=="v2_apex__ADD2")&(ed.reference=="BASE")&(ed.metric=="passed")].iloc[0]
    body.append(f"""
50K additions reduce pass rate.150K ADD2 gains only{row.delta*100:.2f}percentage points,95%interval
[{row.lo*100:.2f}, {row.hi*100:.2f}]points: no established improvement. Replacements remain below BASE.

## Personal plan and A/B/C/D ladder

The full14-piece published baseline and all ladder stages are retained.1/2MNQ adds and VB-empty/replacement1MNQ give
21 configurations per version.5,000 paired252day L20 histories, full and2025+; no Apex rules. Personal fees/slip are
$2.275/MNQ round trip. Daily positions are marked at16CT when needed, not lumped at entry.
""")
    effects=pd.read_csv(BASE/"personal/v2_raw/paired_effects.csv")
    q=effects[(effects.cohort=="2018_plus")&effects.config.str.endswith("ADD_1")&effects.reference.str.endswith("BASE")]
    body.append(table(["Stage","Median profit Δ","DDp95 Δ","Equal-DD profit Δ","Historical annual mean95%CI"],
        [[r.config,n(r.profit_p50_delta),n(r.dd_p95_delta),n(r.same_dd95_median_profit_delta),
          f"[{n(r.historical_annual_mean_delta_ci95_lo)}, {n(r.historical_annual_mean_delta_ci95_hi)}]"] for r in q.itertuples()]))
    pm=pd.read_csv(BASE/"personal/v2_raw/mc_summary.csv")
    q=pm[(pm.cohort=="2018_plus")&(pm.group=="FULL")]
    body.append("\nFull personal levels for v2:\n")
    body.append(table(["Allocation","Median annual profit","DDp95","Capital at20%DD","Median profit/DDp95"],
        [[r.config,n(r.profit_p50),n(r.dd_p95),n(r.capital_20pct),n(r.median_profit_over_dd95,3)] for r in q.itertuples()]))
    body.append("""
The positive incremental historical profit is real in this sample; its interval does not cross zero. Still, FULL ADD1
requires about$3,651 more capital at the20% drawdown rule for about$2,906 more median annual profit. At the same DD
budget it is about$484 worse. FULL replacement is essentially tied at equal DD. StageA's equal-DD benefit is about$265,
with smaller gains elsewhere; this is the most plausible research use, but DSR/platform/independent-review gates block
promotion. Equal-DD scales are continuous diagnostics, not executable integer allocations. MC mean CIs are simulation
precision, not future-edge confidence. All v1 and2025+ comparisons remain saved.

## Overlap, gaps and validation limits

- Closest overlap is VaultBreak. Both-side minute overlap and gross VB-plus-candidate quantities are in
  `minute_VB_overlap.csv`; this measures that leg, not whole-account exposure. About33% of v2 held minutes overlap
  VB on the50K funded complete calendar. Daily correlations/joint-loss cash are also saved. Offsets after an adverse
  move are not presumed to rescue a prior account breach; the joint minute simulators govern account risk.
- Accounts share2,243/2,262 dates;19 exclusions include several March2020 stress sessions. This is conditional on
  coverage and cannot certify the omitted days. Candidate quote gaps are not automatically proof of feed failure.
- Baseline cache's inherited pause marks and small prior50K published-baseline mismatch remain. Neither cached
  paths nor price data were silently rebuilt. Personal's inherited day-based fee approximation can undercharge VB
  reentries; MOC has a lower inherited fee and Twin uses its published v1 ledger. Daily personal DD omits margin risk.
- Source calendar/ring-buffer behavior, total-volume VWAP, stop rounding and simulated stop fills need original
  MultiCharts/tick confirmation. The source's claimed anchoredWFO/plateau and full search registry are unverified.
- The self-audit recomputes2,369 distinct sigma/VWAP checks by direct historical sums,8,426 trade records,84 personal
  MC rows from saved paths,180 funded/180 evaluation rows and360production/100synthetic original-simulator comparisons.
  **This is a maker self-audit, not an independent reviewer PASS. Claude/strategy-checker review is pending.**
- Four fixed source/control streams, no added long-only/short-only version, nearby sigma search, new live code or forward-log
  entry. Statistical promotion requires both tbar andDSR>=0.95 under the latest brief, plus checker/MC/account gates.

## Claimed-source comparison and handoff

The upload claims v2:2,497 trades/$283.1K/PF1.36/DD$22.2K over2017-05..2026-07 at$5NQcommission+two ticks.
At that cost on our **available2018..July2026** period:2,339 trades/$273,055/PF1.340/DD$21,715. V1 available-period
result:1,820/$252,150/PF1.290/DD$40,870. Broadly similar risk direction is not exact report/WFO parity; dates, warm-up,
data, volume and rounding differ. Main plan decisions use actual micro fee assumptions, not the cheaper source claim.

The related noise-area/noise-band family is already ranked in the repo, but those old numbers were not substituted
for this code's tests. The earlier CODE.txt source-only review is a different implementation and is not this test.
Legacy personal CSV label`2018_24_author_IS` is an inherited helper label, not a claim of author-declared IS for this upload.

Run the committed scripts with the existing scientific Python environment and cached inputs:

```text
python analysis/codex_s03_v2_replay.py
python analysis/codex_s03_v2_portfolio.py --phase personal
python analysis/codex_s03_v2_portfolio.py --phase accounts
python analysis/codex_s03_v2_diagnostics.py --phase all
python analysis/codex_s03_v2_check.py
python analysis/codex_s03_v2_exposure.py
python analysis/codex_s03_v2_report.py
```

Claude handoff: `agents/codex/results/s03_v2.md`. Review/rank the exact source; no current-plan promotion is proposed.
No live trading, VPS, broker/API settings or PR2 were touched. The supplied source was archived unchanged.
""")
    text="\n".join(body)
    # Readable numeric prose without rewriting model names, paths or hashes.
    for a,b in {"misses0.95":"misses 0.95","tiny150K":"tiny 150K","all47":"all 47","over14":"over 14",
        "open08:30CT":"open 08:30 CT","close15:00CT":"close 15:00 CT","At09:00":"At 09:00",
        "14:30CT":"14:30 CT","prior close15":"prior close 15","first14":"first 14",
        "PF1.":"PF 1.","about33%":"about 33%","fee1.04":"fee 1.04","fee1.24":"fee 1.24",
        "refs$":"refs $","(seeds1..4),250/500days":"(seeds 1..4), 250/500 days",
        "full14":"full 14","parent14":"parent 14","SourceQty":"Source Qty",
        "on2018":"on 2018","available2018":"available 2018","over2018":"over 2018",
        "drawdown rule":"drawdown rule","t=3.73":"t=3.73",
        "same30":"same 30","a15:55":"a 15:55","declared24":"declared 24","valid0.25":"valid 0.25",
        "Default/CME16":"Default/CME 16","no2017":"no 2017","No2017":"No 2017","over2017":"over 2017",
        "supplied0.4":"supplied 0.4","claimed0.4":"claimed 0.4","All1,844":"All 1,844","plus525":"plus 525",
        "since2023":"since 2023","Since2023":"Since 2023","and1,000":"and 1,000","of12":"of 12",
        "independent50/50":"independent 50/50","all8,426":"all 8,426","full50K":"full 50K",
        "Same150":"Same 150","all sizes":"all sizes","both tbar":"both the trial threshold",
        "the20%":"the 20%","StageA":"Stage A","requires about$":"requires about $","for about$":"for about $",
        "about$":"about $","at16CT":"at 16:00 CT","and2025":"and 2025","1/2MNQ":"1/2 MNQ",
        "14-piece":"14-piece","full14":"full 14",".1/2":". 1/2",".5,000":". 5,000",
        "share2,243":"share 2,243",";19":"; 19","the50K":"the 50K","prior50K":"prior 50K",
        "on the50K":"on the 50K","complete calendar":"complete calendar","andDSR":"and DSR",
        "per contract":"per contract","+-4":"+- 4","counter.4":"counter. 4",
        "full50":"full 50","and360":"and 360","360production":"360 production","100synthetic":"100 synthetic",
        "4 fixed":"4 fixed","MC rows":"MC rows","50Kpass":"50K pass","150Kbreach":"150K breach",
        "Actual150K":"Actual 150K",".150K":". 150K","150K ADD2":"150K ADD2","only0.":"only 0.",
        "increases$":"increases $","SourceQty1":"Source Qty1","perNQ":"per NQ","$/NQ":"$/NQ"}.items():text=text.replace(a,b)
    DEST.write_text(text,encoding="utf-8")
    inputs=[BASE/p for p in("context.json","replay/manifest.json","diagnostics/standard_stats.csv",
        "diagnostics/trial_counts.json","diagnostics/bootstrap2023_mean_total_ci95.csv","diagnostics/placebo_summary.csv",
        "diagnostics/standalone_mc.csv","diagnostics/stop_attribution.csv","diagnostics/source_claim_cost_stats.csv",
        "accounts/funded_summary.csv","accounts/funded_paired_differences.csv","accounts/evaluation_summary.csv",
        "accounts/evaluation_paired_differences.csv","personal/v2_raw/mc_summary.csv","personal/v2_raw/paired_effects.csv",
        "minute_VB_overlap.csv","self_check.json")]
    (BASE/"report_manifest.json").write_text(json.dumps(dict(report_sha256=hashlib.sha256(DEST.read_bytes()).hexdigest(),
        assembler_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),new_returns=False,
        inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        preregistration="54bbba745006f1d20805ef9daab0d130abf4e6fe"),indent=2)+"\n")
    print(DEST)


if __name__=="__main__":main()
