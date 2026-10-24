"""Assemble the R2Vault report from saved results; calculates no new returns."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"analysis/outputs/codex_r2vault"
REPORT=ROOT/"agents/codex/results/r2vault.md"


def num(x,d=0):
    return "N/A" if pd.isna(x) else "∞" if np.isinf(x) else f"{x:,.{d}f}"


def table(headers,rows):
    return "\n".join(["|"+"|".join(headers)+"|","|"+"|".join(["---"]*len(headers))+"|"]+
                      ["|"+"|".join(map(str,r))+"|" for r in rows])+"\n"


def main():
    stats=pd.read_csv(DATA/"diagnostics/standard_stats.csv")
    trials=json.loads((DATA/"diagnostics/trial_counts.json").read_text())
    funded=pd.read_csv(DATA/"accounts/funded_summary.csv")
    fd=pd.read_csv(DATA/"accounts/funded_paired_differences.csv")
    ev=pd.read_csv(DATA/"accounts/evaluation_summary.csv")
    ed=pd.read_csv(DATA/"accounts/evaluation_paired_differences.csv")
    null=pd.read_csv(DATA/"diagnostics/placebo_summary.csv")
    models=["et_raw","et_apex","ct_raw","ct_apex","et_daily_reset_raw"]
    s=stats[(stats.group=="both")&(stats.fee_micro==1.04)]
    ct=s[(s.model=="ct_raw")&(s.period=="2018_plus")].iloc[0]
    text=[f"""# R2Vault: REJECT for current-plan promotion
Summary: Built the PDF rules and completed all five plan contexts; no version qualifies for promotion.
CT raw is the strongest: full t={ct.t:.2f}, DSR={ct.dsr_conservative_latest:.3f}, below {trials['t_threshold']:.2f}/0.95; recent returns and nominal placebos are positive.
Evaluation additions reduce pass rates; funded effects fail consistent base/empty-slot benefit. Personal CT gains are small at equal drawdown; source promotion and execution gates remain unmet.
Move on without changing the trading plan. This is a frozen reconstruction, not verified author-platform parity.

Plan: `agents/codex/plans/r2vault.md`, **a973f0779b6e10d9c3c29adc6748ed5eba0d5f92**, before returns.
Calendar clarification: **dab01a8**, also before returns. Implementation: `analysis/codex_r2vault_replay.py`.
Adapters/checks: `analysis/codex_r2vault_*.py`. Outputs: `analysis/outputs/codex_r2vault/`.
Trials: **five fixed rule models**, with declared fee stresses/account sizes; no threshold or source-clock selection.
Known multiple-test lower bound **{trials['effective_n']}**:294 ranked+7 prior Codex+5 concurrent NQDB2+5 R2Vault; original author search unknown.
The frozen context172322e was rechecked against newer Claude1f2d1ff: all47 baseline dependency blobs remain unchanged.
The existing prepared baseline was reused. Exact rosters/sizing and inherited limits are in `r2vault_plan_context.md`.

## Rule and what was built

Five-minute NQ, long only. Standard OLS on576 observed closes; if R²<=0.030, the current candle's high/low replace
the vault. With positive slope, next-bar buy-stop at vault high+20%range, rounded upward to0.25; maximum3 actual
entries/CTcalendar date. Fixed75point stop/40point target anchored at actual fill; protection active on entry.
Break-even is off. The PDF's R² exit threshold2.00 cannot trigger on standard[0,1]R².

Source clock09:30–15:30 lacks a timezone. ET means08:30–14:30CT; CT means09:30–15:30CT. Both use full24h observed
576-bar history and persistent vaults. Raw models carry positions; Apex versions flatten at15:55CT/11:30 early
(next-minute opening fill). The fifth daily-reset ET model is standalone diagnostic only. No fifth-model placement selection.

One-minute execution uses the repository causal OHLC path: high first when H−O<=O−L, otherwise low first.
Opening gaps precede segments; only prices after entry/before exit contribute adverse exposure. Targets require
one-point trade-through; stops can gap. Queued Apex market flatten takes priority at its opening minute.
These are explicit reconstruction assumptions. The PDF does not specify history template, clock, vault reset,
order lifecycle, quantity or execution settings; its exact trading ledger and continuous-contract roll treatment are unavailable.

Dollar stops are interpreted for oneNQ:75/40points becomes **$150/$80 perMNQ**, not$1500/$800 on a micro.
Tables below use Apexfee$1.04/MNQ RT, $0.50 entry slip, $0.50 stop/market exit slip, zero target exit slip.
Personal portfolios use their frozen$1.275/MNQ fee convention. Full RTfee is reserved at entry; no duplicate charge.

## Standalone results

All amounts here are **per1NQ** after the declared$1.04/MNQ fee-equivalent costs. Whole strategy=longs; **zero shorts**
(short metrics N/A; explicit empty-short rows remain in CSVs). Daily risk metrics use16CT observable MTM,
not profit lumped at entry. 2026 endsOctober9; repository2023+ is seen historical replication.
"""]
    full=s[s.period=="2018_plus"].set_index("model")
    text.append(table(["Model","n","Win%","$/trade","PF","t","DSR311","Sharpe","Sortino","Calmar","Ulcer%","Daily DD"],
        [[m,int(r.trades),num(r.win*100,1),num(r.avg,2),num(r.profit_factor,3),num(r.t,2),num(r.dsr_conservative_latest,3),
          num(r.sharpe,2),num(r.sortino,2),num(r.calmar,2),num(r.ulcer,2),num(r.max_dd_including_start)] for m,r in full.iterrows()]))
    text.append("\nDesign/recent cohorts (entry-date closed-trade statistics):\n")
    rows=[]
    for m in models:
        for period in ("2018_22","2023_plus","2025_plus"):
            r=s[(s.model==m)&(s.period==period)].iloc[0]
            rows.append([m,period,int(r.trades),num(r.avg,2),num(r.t,2),num(r.total_nq)])
    text.append(table(["Model","Period","n","$/trade","t","Net"],rows))
    text.append("""
CT raw had one position open at the design split; its later exit belongs to the full entry cohort but was not
known in the original design run. `staged_design_closed_trade_stats.csv` preserves the1306 closed+1open stage;
the combined entry-cohort table has1307 design entries. Daily MTM splits strictly by calendar without future prices.

Annual net per NQ by trade entry year (same costs; 2026 partial):
""")
    text.append(table(["Year"]+models,[[yr]+[num(s[(s.model==m)&(s.period==yr)].total_nq.iloc[0]) for m in models]
                                        for yr in map(str,range(2018,2027))]))
    boot=pd.read_csv(DATA/"diagnostics/bootstrap2023_mean_total_ci95.csv")
    text.append("\n2023+20-day-block95% intervals for total marked net,5000 resamples:\n")
    text.append(table(["Model","Actual","95% interval"],[[r.model,num(r.total_actual),f"[{num(r.total_ci95_lo)}, {num(r.total_ci95_hi)}]"]
        for r in boot[(boot.group=="both")&(boot.fee_micro==1.04)].itertuples()]))
    text.append("""
CT raw's recent edge is more credible than ET's; it still fails the required full t/DSR gate. Its Apex adaptation
has recent t<2 as well. Higher fees do not repair either failure. This is not a claim that every source interpretation loses.
Full2018–24, exact author OOS dates, years, fee stresses, daily/trade t and all metrics are in `diagnostics/standard_stats.csv`.

## Placebos and standalone risk

1000 random-side and1000 random-time draws per main model. Side draws condition on actual source entry events and
skip overlaps after re-executed exits; they are falsifiers, not an executable alternative. Time controls plan one
long decision/day using an independent coverage calendar, skip missing decision/open quotes, and never condition on
whether the actual strategy later trades. Source max3/day versus control max1/day differs; compare both total and expectancy.
Recent results below use same-calendar actual entries for time controls, all source events for side controls.
""")
    q=null[(null.period=="2023_plus")&(((null.control=="random_time")&(null.reference_scope=="actual_entry_days_in_control_calendar"))|
          ((null.control=="random_side")&(null.reference_scope=="all_source_closed_entries")))]
    text.append(table(["Model","Null","Actual $/trade","Null median $/trade","p(total)","p(expectancy)"],
        [[r.model,r.control,num(r.actual_avg_nq,2),num(r.null_expectancy_p50,2),num(r.p_null_total_ge_actual,3),num(r.p_null_expectancy_ge_actual,3)] for r in q.itertuples()]))
    text.append("""
CT nominal control passes are favorable evidence, not a bypass around multiple testing/source uncertainty. ET time
controls do not support timing value. Null DD is chronological closed-trade equity; main risk/account tables use
MTM/minute paths. Terminal unclosed/unpriced/unknown-held events are counted separately, not forced into fake exits.
Fixed-long null walkers reproduce every main source event's exit exactly. Standalone daily/trade Monte Carlo at1/2MNQ
is saved in `diagnostics/standalone_mc.csv`; its EOD trailing approximation is not the funded-account risk model.

## Evaluation: both sizes, additions and replacements

Real21-session windows, with the whole window inside its cohort; unknown-day windows are excluded without compressing
the calendar.50K retains pass-first and150K breach-first same-minute tie conventions. Correct150K risk scaling floors
after scaling dollar risk; no fractional-contract shortcut. Full-cohort primary-fee results:
""")
    e=ev[(ev.fee==1.04)&(ev.cohort=="2018_plus")]
    text.append(table(["Account","Allocation","Pass%","Fail%","Median pass days"],
        [[r.context,r.config,num(r.passed*100,2),num(r.failed*100,2),num(r.median_pass_days,1)] for r in e.itertuples()]))
    text.append("""
Every full-cohort addition lowers pass rate at both sizes/clocks. No replacement beats BASE. Empty-slot comparisons,
all five cohorts, fee1.24 and chronological-block intervals remain in `accounts/evaluation_*`.

## Funded: joint minute risk, not end-of-day standalone profit

1000 paired circular20day histories,seeds1..4;250/500day horizons. Counts undergo the same cushion sizing and integer
floor as the plan. Both clocks/allocations share2242/2262 complete days. Internal100 synthetic+360 production records
match the original state machines on all five outputs. Full-cohort primary-fee results:
""")
    f=funded[(funded.fee==1.04)&(funded.cohort=="2018_plus")]
    text.append(table(["Account","Allocation","1y payout mean","2y mean","2y p5–p95","Blown%","Median days to6"],
        [[r.context,r.config,num(r.year1),num(r.year2),f"{num(r.year2_p5)}–{num(r.year2_p95)}",num(r.blown*100,1),num(r.days6,1)] for r in f.itertuples()]))
    text.append("\nRecent2023+ ADD1 paired effects versus BASE,95% MC sampling intervals conditional on observed history:\n")
    a=fd[(fd.fee==1.04)&(fd.cohort=="2023_plus")&(fd.reference=="BASE")&fd.config.str.endswith("ADD1")&(fd.metric=="year2")]
    text.append(table(["Account","Allocation","2y payout change","95% interval"],
        [[r.context,r.config,num(r.delta,1),f"[{num(r.lo,1)}, {num(r.hi,1)}]"] for r in a.itertuples()]))
    text.append("""
The favorable-looking150K CT replacement2025+ is mixed:1y beats BASE and EMPTY, but2y fails to beat EMPTY reliably.
Full paired results below expose that empty-slot control rather than crediting removal of VB to the candidate:
""")
    a=fd[(fd.fee==1.04)&(fd.context=="150K_funded")&(fd.cohort=="2025_plus")&
         (fd.config=="ct_apex__REPLACE_VB2")&fd.metric.isin(["year1","year2","blown"])]
    text.append(table(["Reference","Metric","Change","95% interval"],
        [[r.reference,r.metric,num(r.delta,3 if r.metric=="blown" else 1),f"[{num(r.lo,3 if r.metric=='blown' else 1)}, {num(r.hi,3 if r.metric=='blown' else 1)}]"] for r in a.itertuples()]))
    text.append("\nFee1.24 full-cohort ADD1 effects versus BASE (same stress on both sides):\n")
    a=fd[(fd.fee==1.24)&(fd.cohort=="2018_plus")&(fd.reference=="BASE")&fd.config.str.endswith("ADD1")&(fd.metric=="year2")]
    text.append(table(["Account","Allocation","2y payout change","95% interval"],
        [[r.context,r.config,num(r.delta,1),f"[{num(r.lo,1)}, {num(r.hi,1)}]"] for r in a.itertuples()]))
    text.append("""
The 5–95% quantiles use all histories; outcomes below p5, including zero payout, remain possible. Median time to6 treats incomplete histories as infinity. MC mean intervals
describe simulation precision, not certainty about future markets. Multiple account/allocation comparisons are descriptive;
they are not independent confirmations of an edge. All180 funded and180 evaluation rows remain saved, including failures.

## Personal: complete14-piece plan and A/B/C/D ladder

Published baseline, raw carry retained,16CT daily MTM; no Apex drawdown/payout rules.5000 paired252day L20 histories,
seed1, full and2025+ cohorts.21 configurations per clock include1/2MNQ adds and VB-empty/replacement where present.
Full-cohort ADD1 effects below; equal-DD figures are continuous research risk budgets, not executable contract counts.
""")
    rows=[]
    for m in ("et_raw","ct_raw"):
        p=pd.read_csv(DATA/f"personal/{m}/paired_effects.csv")
        for group in ("A","B","C","D","FULL"):
            r=p[(p.cohort=="2018_plus")&(p.config==group+"__ADD_1")&(p.reference==group+"__BASE")].iloc[0]
            rows.append([m,group,num(r.profit_p50_delta),num(r.dd_p95_delta),num(r.same_dd95_median_profit_delta),
                         f"[{num(r.historical_annual_mean_delta_ci95_lo)}, {num(r.historical_annual_mean_delta_ci95_hi)}]"])
    text.append(table(["Model","Plan","Median profit Δ","DDp95 Δ","Equal-DD median profit Δ","Historical annual mean95%CI"],rows))
    text.append("\nFull personal portfolio primary MC levels (perMNQ costs$1.275):\n")
    rows=[]
    for m in ("et_raw","ct_raw"):
        p=pd.read_csv(DATA/f"personal/{m}/mc_summary.csv")
        for r in p[(p.cohort=="2018_plus")&(p.group=="FULL")].itertuples():
            rows.append([m,r.config,num(r.profit_p50),num(r.dd_p95),num(r.capital_20pct),num(r.median_profit_over_dd95,3)])
    text.append(table(["Model","Allocation","Median profit","DDp95","Capital at20%DD","Median profit/DDp95"],rows))
    text.append("""
CT personal has a plausible incremental return; do not call it an unequivocal portfolio failure. Its full-plan
ADD1 equal-DD gain is small. Its historical annual mean effect is positive (95% block interval$570–$2951), while
source significance still fails the mandatory multiple-test/DSR promotion gate. Replacing VB is nearly flat versus BASE and adds little risk-adjusted value versus EMPTY.
The ET version worsens risk efficiency. All42 allocations across both clocks,2025+ cases, paired downside and historical
intervals are saved under `personal/`; no clock/size was selected afterward for promotion.

## Overlap, data and execution limitations

- No exogenous forced flow is identified: this remains a price-based breakout hypothesis. Daily correlation is not a hedge.
- Source ET raw has2289/3037 already-crossed signal-stop entries,312 cross-date trades and326 trades with unknown held
  quote gaps. CT has2093/2760,441 and440 respectively. Neither version has a final open trade. Already-crossed buy-stop
  acceptance/conversion needs platform validation; this replay assumes an opening fill as frozen before returns.
- The Apex shared universe omits20dates, including several March2020 stress sessions. Saved date lists make that
  selection visible; account estimates are conditional on the covered universe and cannot certify omitted-day risk.
- Pre2021-06-28,15:16–15:30 close-stamped minutes correspond to a documented exchange pause. They are stale-marked,
  not filled; post-change missing minutes are not presumed closed. The dated [CME notice](https://www.cmegroup.com/notices/electronic-trading/2021/06/20210621.html)
  governs this boundary, rather than a generic stale FAQ. No synthetic regression bars were added.
- Inherited baseline pause handling can substitute entry price in Monday19pauses/Bridge63pauses; preserved cache
  convention is disclosed. It affects early history, not2023+/2025+. The small prior50K published-baseline mismatch
  also remains; candidate effects use a matched frozen baseline, not a claim of exact published payout parity.
- Personal baseline day-based fee adjustments undercount some VB reentries, MOC has a lower inherited fee, and Twin
  uses the published v1 ledger. Personal daily DD omits intraday margin/liquidation exposure.
- Ulcer% uses the repository metrics' $50,000 reporting-capital convention; it is not an account-sizing recommendation.
- `minute_occupancy.csv`, `VB_low_timing.csv`, `overlap_daily.csv` and personal joint-loss files expose simultaneous
  NQ exposure and loss timing. Full-size occupancy is an upper-bound description before cushion reductions; winning
  closes after a VB low are not assumed to rescue a previously breached account. Joint minute account paths govern risk.
- All five models share unverified full-session history and roll conventions; an RTH-only or original-code implementation
  might differ. Such a change would require a new preregistration/trial, not a retroactive explanation that validates these results.

## PDF reconciliation and independent review

The author reports2518trades/$265780, including2017 unavailable here; exact platform/settings/cost parity is unverified.
For2025-01-15 through2026-08-31, the PDF reports564trades/$88675; costed ET raw has685/−$32889 and CT raw635/$67711
at fee1.04. Different counts/timezone/fills prevent claiming an exact replication. The PDF's$190300.45 adjusted profit
matches a win/loss-count statistical adjustment, not a verified commission/slippage deduction. Its seven residual trades
reflect nonmatching displayed date partitions, not automatically an arithmetic error. See `r2vault_source_audit.md`.

Independent adapter reviews are `r2vault_personal_review.md`, `r2vault_personal_checker.md`, `r2vault_accounts_review.md`
and `r2vault_diagnostics_review.md`. Review independence is scoped: different agents checked source, adapters and saved arithmetic; the replay
author checked others' adapters. This is not a fresh blind Claude/strategy-checker PASS or MultiCharts confirmation.

The Python build is the research deliverable. No PowerLanguage/live strategy was added because the validation gates
failed. No parameter rescue, forward-log entry, live-plan change, VPS/broker/API action or PR2 action was taken.

## Reproduce and hand off

Use the configured scientific Python environment, existing ignored caches and pinned baseline snapshots. In this
Windows checkout the bundled Python plus `agents/codex/runtime/or_pullback_python` supplies the dependencies.
From the repository root with `analysis` and that dependency directory on PYTHONPATH:

```text
python -c "from codex_r2vault_replay import run_cached; run_cached()"
python analysis/codex_r2vault_personal.py
python analysis/codex_r2vault_accounts.py --prereg a973f0779b6e10d9c3c29adc6748ed5eba0d5f92
python analysis/codex_r2vault_diagnostics.py --phase all
python analysis/codex_r2vault_personal_check.py
python analysis/codex_r2vault_accounts_check.py
python analysis/codex_r2vault_diagnostics_check.py
python analysis/codex_r2vault_report.py
```

Input/ledger/script hashes, sample definitions, gap calendars, fixed histories and all trial models are in the component
manifests. Do not rebuild market caches just to rerun this report assembler. Claude handoff: review/rank
`agents/codex/results/r2vault.md`; no current-plan promotion is supported.
""")
    prose="\n".join(text)
    # Spacing for research shorthand in the explanatory prose. Explicit
    # replacements preserve model identifiers, paths, hashes and table inputs.
    spacing={"on576":"on 576","maximum3":"maximum 3","per1NQ":"per 1 NQ",
        "perNQ":"per NQ","perMNQ":"per MNQ","oneNQ":"one NQ","CTcalendar":"CT calendar",
        "Fixed75point stop/40point target":"Fixed 75-point stop/40-point target",
        "threshold2.00":"threshold 2.00","[0,1]R²":"[0,1] R²","clock09:30":"clock 09:30",
        "means08:30":"means 08:30","means09:30":"means 09:30","full24h":"full 24-hour",
        "576-bar":"576-bar","at15:55CT":"at 15:55 CT","/11:30 early":"/11:30 CT early",
        "75/40points":"75/40 points","RTfee":"round-trip fee","fee$":"fee $",
        "at entry+":"at entry +","high+20%range":"high + 20% of range","to0.25":"to 0.25",
        "16CT":"16:00 CT","observed2023":"observed 2023","here.2026":"here. 2026",
        "All180":"All 180","all180":"all 180","All42":"All 42","all47":"all 47",
        "fixed14":"fixed 14","complete14":"complete 14","baseline172":"baseline 172",
        "recent2023":"recent 2023","Recent2023":"Recent 2023","full2018":"full 2018",
        "Full2018":"Full 2018","for2025":"for 2025","reports2518":"reports 2,518",
        "reports564":"reports 564","raw635":"raw 635","raw685":"raw 685",
        "threeMNQ":"three MNQ","at1/2MNQ":"at 1/2 MNQ","1/2MNQ":"1/2 MNQ",
        "same2242":"same 2,242","share2242/2262":"share 2,242/2,262",
        "50K retains":"50K retains","rules.5000":"rules. 5,000","histories,seeds":"histories, seeds",
        "day histories,seeds":"day histories, seeds","of2018":"of 2018","per clock.21":"per clock. 21",
        "Plan: `":"Plan: `","Pre2021":"Before 2021","1000 ":"1,000 ","5000 ":"5,000 ",
        "Real21":"Real 21",";250/500day":"; 250/500-day","circular20day":"circular 20-day",
        "same-minute tie conventions. Correct150K":"same-minute tie conventions. Correct 150K",
        "window.50K":"window. 50K","50K retains":"50K retains","and150K":"and 150K",
        "raw has2289/3037":"raw has 2,289/3,037","and326":"and 326","has2093/2760":"has 2,093/2,760",
        "and440":"and 440","omits20dates":"omits 20 dates","MON285":"MON 285",
        "Monday19pauses/Bridge63pauses":"Monday 19 pauses/Bridge 63 pauses",
        "15:16–15:30 close-stamped":"15:16–15:30 close-stamped","the20%":"the 20%",
        "initial100":"initial 100","Internal100":"Internal 100","+360":" + 360",
        "treats incomplete histories":"treats incomplete histories","to6":"to 6",
        "CT replacement2025+":"CT replacement 2025+","Full CT":"Full CT"}
    for old,new in spacing.items():
        prose=prose.replace(old,new)
    REPORT.write_text(prose,encoding="utf-8")
    inputs=[DATA/x for x in ("diagnostics/standard_stats.csv","diagnostics/trial_counts.json",
        "diagnostics/bootstrap2023_mean_total_ci95.csv","diagnostics/placebo_summary.csv",
        "accounts/funded_summary.csv","accounts/funded_paired_differences.csv","accounts/evaluation_summary.csv")]
    for m in ("et_raw","ct_raw"):
        inputs.extend(DATA/f"personal/{m}/{f}" for f in ("mc_summary.csv","paired_effects.csv"))
    manifest=dict(report=str(REPORT.relative_to(ROOT)),sha256=hashlib.sha256(REPORT.read_bytes()).hexdigest(),
                  assembler_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                  new_strategy_returns=False)
    (DATA/"report_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(str(REPORT))


if __name__=="__main__":
    main()
