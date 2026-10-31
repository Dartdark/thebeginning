"""Render the frozen S03 results; reads saved evidence only, never replays."""
import json
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis/outputs/codex_s03_noisearea"
PREREG="d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad"


def money(x):
    return ("-$" if x<0 else "$")+f"{abs(float(x)):,.0f}"


def table(headers,rows):
    return "| "+" | ".join(headers)+" |\n|"+"|".join("---" for _ in headers)+"|\n"+"\n".join(
        "| "+" | ".join(str(x) for x in row)+" |" for row in rows)


def main():
    metrics=pd.read_csv(OUT/"all_metrics.csv")
    years=pd.concat([pd.read_csv(OUT/f"{s}_yearly.csv") for s in ("design","recent")])
    p=metrics[(metrics.profile=="V2")&(metrics.side=="whole")].set_index("period")
    pair={s:pd.read_csv(OUT/f"diagnostics_{s}/paired_stop_bootstrap.csv").set_index("metric") for s in ("design","recent")}
    ns={s:json.loads((OUT/f"diagnostics_{s}/nulls_summary.json").read_text()) for s in ("design","recent")}
    tail=json.loads((OUT/"diagnostics_recent/V2_tail_concentration.json").read_text())
    bootstrap=pd.read_csv(OUT/"diagnostics_recent/recent_bootstrap.csv",index_col=0)
    fees=pd.read_csv(OUT/"candidate_micro_fee_sensitivity.csv")
    gate=json.loads((OUT/"candidate_gate.json").read_text())
    a,b=p.loc["design"],p.loc["recent"]
    report=["# S03 Noise Area v2: WATCH; risk benefit observed, no validated plan placement", "",
        "Summary: The fixed OHLC reconstruction is profitable in every tested year; source/tick parity is unconfirmed.",
        f"2018-22: {int(a.trades):,} trades, {money(a.avg)}/NQ, PF{a.profit_factor:.2f}; 2023+: {int(b.trades):,}, {money(b.avg)}/NQ, PF{b.profit_factor:.2f}.",
        "The stop roughly halves recent daily drawdown with almost unchanged profit; the formal improvement criterion does not pass.",
        f"Top10 trades supply {tail['top_shares']['10']:.1%} of recent net; DSR{p.loc['2018_plus','dsr']:.3f}<0.95 and actual-fee recent t<2.",
        "Three missing held-price minutes and calendar gaps block all account tests. Keep current allocations; placement remains unknown.",
        "",f"Plan: `agents/codex/plans/s03_noisearea.md`, **{PREREG}**, published before any new signals/returns.",
        "Scripts: `analysis/codex_s03_{calendar,replay,run,stats,diagnostics,accounts,personal,report}.py`.",
        "Output: `analysis/outputs/codex_s03_noisearea/`. Trials: **one idea/four fixed profiles**, all failures included; 400 registered null replays.",
        "", "## Rule (as tested)", "",
        "At half-hour checks10:00-15:30ET, trade beyond the14-prior-full-session same-clock mean absolute open-to-close return band, confirmed by VWAP. "
        "Upper=max(open,prior cash close)*(1+sigma); lower=min(...)*(1-sigma). Both directions share one position; opposite signals reverse. "
        "Band/VWAP trailing exits occur only at checks. Market orders fill at the next observed minute open. V2 fixes a0.4*raw-sigma*signal-close protective stop, "
        "rounded toward raw entry and live on the fill minute. This sigma is mean absolute displacement, not standard deviation or ATR. No profit target. "
        "Normal flat decision16:00ET fills16:01ET=15:01CT, within the account's15:59CT deadline.",
        "",
        "Primary reconstruction uses actual08:30CT cash-open price from the08:31 close-stamped minute, one-minute typical-price/total-volume VWAP, "
        "and the immediately preceding cash-session close (including a legitimate early close). Only prior completed full sessions enter sigma; "
        "past completeness is known after their close. Today's later missing prices never retroactively exclude earlier trades. Known calendar closures/early closes are skipped.",
        "",
        "Frozen profiles: **V2** primary; **V1** identical with protective stop disabled; **C2** one08:30-bar-inclusive anchor sensitivity; "
        "**E2** V2 at three ticks per market/stop fill. C2/E2 are not selectable winners. No stop, weekday, clock, size or direction search followed results. "
        "Standard cost$7.25/NQ RT plus one tick per market/stop fill, ordinarily$17.25 total; source used$15. Net already includes fills and fees once. "
        "Source LucidFlex payout/size assumptions are not used as Apex results.",
        "", "## Results", "", "All amounts in the next tables are **per one NQ**, fixed size, after research costs. 2026 ends October9. "
        "2023+ is selected/previously seen historical replication, not a fresh holdout. These are observed-bar reconstruction results, with the missing-path limitation below.", ""]
    rows=[]
    for profile in ("V2","V1","C2","E2"):
        q=metrics[(metrics.profile==profile)&(metrics.side=="whole")].set_index("period")
        rows.append([profile,int(q.loc['design','trades']),money(q.loc['design','net']),f"{q.loc['design','t']:.2f}",
            int(q.loc['recent','trades']),money(q.loc['recent','net']),f"{q.loc['recent','t']:.3f}",money(q.loc['2018_plus','net'])])
    report += [table(["Profile","2018-22 n","Net","t","2023+ n","Net","t","Full net"],rows), "",
        "Standard whole/long/short metrics (side rows are slices of the shared replay, not newly selected single-side strategies):", ""]
    rows=[]
    for period in ("design","recent","2018_plus"):
        for side in ("whole","long","short"):
            x=metrics[(metrics.profile=='V2')&(metrics.period==period)&(metrics.side==side)].iloc[0]
            rows.append([period,side,int(x.trades),f"{x.win:.1%}",money(x.avg),f"{x.t:.2f}",f"{x.sharpe:.2f}",
                f"{x.sortino:.2f}",f"{x.profit_factor:.2f}",f"{x.calmar:.2f}",f"{x.ulcer:.2f}",money(x.max_dd)])
    report += [table(["Period","Side","n","Win","$/trade","t","Sharpe","Sortino","PF","Calmar","Ulcer%","Daily maxDD"],rows), "",
        "Sharpe/Sortino use the common calendar including zero dates; daily realized totals reconcile exactly because all closed trades are intraday. "
        "Intraday adverse excursions are separately audited; daily maxDD is not the full account breach path. Ulcer uses the repository's$50,000 reference equity.", ""]
    rows=[]
    for year in range(2018,2027):
        q=years[(years.profile=='V2')&(years.year==year)].set_index('side')
        rows.append([year,int(q.loc['whole','trades']),money(q.loc['whole','net']),money(q.loc['long','net']),money(q.loc['short','net']),
            f"{q.loc['whole','profit_factor']:.2f}",f"{q.loc['whole','t']:.2f}"])
    report += [table(["Year","n","Total net","Long net","Short net","PF","t"],rows), "",
        f"Post-source extension,2026-07-08 onward: {int(p.loc['post_source_extension','trades'])} trades, "
        f"{money(p.loc['post_source_extension','net'])}, t={p.loc['post_source_extension','t']:.2f}. This is a short descriptive extension, not independent validation.", "",
        "**The protective-stop claim:** full-history point results improve total net and reduce drawdown, but the registered design/recent criteria do not both support an improvement. "
        "The design V2 maxDD is slightly higher; recent profit is slightly lower. The mechanism is changed re-entry opportunity as well as changed loss size.", ""]
    rows=[]
    for stage in ('design','recent'):
        q=pair[stage]
        for key in ('net_change','sharpe_change','max_dd_reduction'):
            fmt=(lambda v:f"{v:.3f}") if key=='sharpe_change' else money
            rows.append([stage,key,fmt(q.loc[key,'actual']),fmt(q.loc[key,'p5']),fmt(q.loc[key,'p95'])])
    report += [table(["Period","V2 minus V1 metric","Observed","90% low","90% high"],rows), "",
        "For the design's1,073 common entries the stop changes net by−$26,560;293 extra re-entries add$46,010.75. "
        "Recent:767 common entries change−$40,490;246 extra re-entries add$39,226.50. No original entries disappear. "
        "Therefore stop-trade losses alone cannot measure the intervention, and per-trade average alone is misleading.", "",
        "**Actual micro fee arithmetic**, on identical observed V2 fills at fixed1MNQ. This is not a payout/account simulation:", ""]
    q=fees[(fees.period=='recent')&(fees.side=='whole')]
    report += [table(["MNQ round-trip fee","Recent avg/MNQ","Recent t","PF"],
        [[f"${x.fee_MNQ_RT:.2f}",f"${x.avg_MNQ:.2f}",f"{x.t:.3f}",f"{x.profit_factor:.3f}"] for x in q.itertuples()]),
        "", "Repricing credits the original$0.725/MNQ research commission and charges$1.04/$1.24 per actual trade; existing slippage stays included. "
        "At actual micro fees, recent t falls below2. The nominal one-NQ result barely clears2 and the anchor sensitivity does not.",
        "", "## Placebos and account level", "",
        "All400 registered controls were run through the full state engine:100 random-side and100 time-permuted streams per period. "
        "No slow approximate scheduler, future-occupancy count matching or discarded outcomes was used. These controls have important interpretation limits:", "",
        "- Side controls randomize raw check-bar directions; extra reversals change holding time, number of filled trades and costs. This is a joint policy/turnover comparison, not an isolated directional-prediction test.",
        "- Time permutations can move a later signal's direction earlier in the day. They are **future-informed retrospective comparisons**, not causal random-entry policies. Their large profits do not reject the actual entry edge. A clean causal timing test remains open; no new rescue control was chosen after returns.",
        "- Some control paths cross missing bars. All remain visible; p-values on incomplete paths are descriptive under observed-bar execution, not validated executable outcomes.", ""]
    rows=[]
    for stage in ('design','recent'):
        for name in ('side','time'):
            z=ns[stage][name]
            rows.append([stage,name,f"{z['p_net_ge_actual']:.4f}",money(z['null_net_median']),z['actual_filled_count'],z['filled_count_median'],z['complete_paths']])
    report += [table(["Period","Control","Profit p","Median null net","Actual filled","Median null filled","Complete /100"],rows), "",
        f"Recent20-day/3,000-draw bootstrap,90%: net {money(bootstrap.loc['net','p5'])} to {money(bootstrap.loc['net','p95'])}; "
        f"tradePF {bootstrap.loc['profit_factor_trade','p5']:.3f}-{bootstrap.loc['profit_factor_trade','p95']:.3f}; "
        f"Sharpe {bootstrap.loc['sharpe','p5']:.2f}-{bootstrap.loc['sharpe','p95']:.2f}; daily maxDD "
        f"{money(bootstrap.loc['max_dd','p5'])}-{money(bootstrap.loc['max_dd','p95'])}. Whole/long/short bootstrap and drawdown-permutation files are saved.", "",
        f"Recent tail concentration: best trade {tail['top_shares']['1']:.1%}, best10 {tail['top_shares']['10']:.1%}, best25 "
        f"{tail['top_shares']['25']:.1%} of net. Fractions above100% mean the rest lost money; no deletion was used to select a rule. "
        "Recent longs supply$108,965.75; shorts$15,705 with t0.39 and a bootstrap interval crossing zero. No long-only re-optimization or account selection followed.", "",
        "**All account stages stopped at the registered data gate.** Candidate paths contain three unknown held minutes on2024-10-09: "
        "14:47,14:48,14:55CT, within a long entered13:01 and exited15:01. Both current raw NQ exports omit those minutes; file Git blobs and cached finite masks match. "
        "The stop is20362.75, raw entry20399.75; the observed net$1,147.75 cannot establish what happened inside the missing minutes.", "",
        "A structural audit also finds2020-11-30's entire normal cash session absent and a missing12:00 decision on2020-03-18. "
        "The latter may be an exchange halt, but the inherited repository closure mask does not certify it. "
        "Thirteen other flat, nonscheduled-minute gaps are explicitly permitted by the frozen observed-only VWAP rule; they are not mislabelled additional fatal held-path gaps. "
        "All2,290 expected weekday rows are retained. No prices, trades, returns or missing days were invented or silently dropped.", ""]
    report += [table(["Destination","Frozen comparison","Outcome"],[
        ["50K evaluation","BASE / +1MNQ / EMPTY_VB / VB8 replacement","BLOCKED_DATA; no simulation"],
        ["150K evaluation","BASE / +2MNQ / EMPTY_VB / VB20 replacement","BLOCKED_DATA; no simulation"],
        ["50K funded","BASE / +1MNQ / EMPTY_VB / original VB2/1 slot","BLOCKED_DATA; no simulation"],
        ["150K funded","Current DT-inclusive plan; +2MNQ / EMPTY / original VB slot","BLOCKED_DATA; no simulation"],
        ["Personal","Current17 pieces,11 fixed ladders,44 configurations","BLOCKED_DATA; no simulation"]]), "",
        "Account and personal helpers passed synthetic fixtures and current-source provenance checks, but no historical baseline was built and no account/portfolio simulation ran. "
        "No payout, breach, evaluation-pass, marginal portfolio-value or capital-allocation conclusion is inferred from standalone statistics. "
        "The individual manifests record each limiting condition and distinguish unknown contribution from proven no gain.",
        "", "## What could make this wrong", "",
        f"- **Selection:** author's at least12 stop values and walk-forward claims were supplied already selected; source2023+ is not fresh. Our4 profiles were frozen before returns. "
        f"The ranked-item-plus-one t bar is{p.loc['2018_plus','t_bar']:.3f}; full t{p.loc['2018_plus','t']:.3f} clears it but DSR{p.loc['2018_plus','dsr']:.3f} fails0.95. Actual-micro recent t also misses2.",
        "- **Source parity:** no original PowerLanguage signal, s03_engine.py, original OFB bars or tick stop export was supplied. The bulletin's1-minute replica and claimed trade parity are not confirmation of this reconstruction. Its2017 start differs from our2018 start; datasets/clocks/costs differ.",
        "- **Price path:** one-minute OHLC and missing held prices cannot validate tick execution or exact intraday liquidation. Gap stops may fill beyond planned risk. No SetExitOnClose final-price rescue was fabricated.",
        "- **Contract rolls:** the unadjusted data can affect prior-close band references. Known03:32/17:01CT roll jumps lie outside normal RTH holds, so they are not automatically trade profits; a back-adjusted-source comparison was not silently added.",
        "- **Inference:** conditional/future-informed timing controls and different-turnover side controls are not clean proof of executable predictive edge. Resampling selected returns does not remove selection bias or certify account survival.",
        "", "## Differences between the MultiCharts code and the test", "",
        "No new MultiCharts code was written. This is a descriptive-rule reconstruction with explicit cash-open, VWAP, prior-close/calendar, observed-bar gap, "
        "stop-price rounding and shared OHLC-path conventions. No original source code was available to claim exact equivalence. Source costs$15 become research$17.25 and actual/stress micro fees. "
        "Known calendar closures skip entries; missing current data never retroactively deletes an earlier trade. All observed trade nets reconcile to raw/slipped fills and daily totals.",
        "", "## Decision and reproduction", "",
        "**WATCH.** The stop's historical risk effect is useful evidence, but the fixed version has not earned a current plan placement. "
        "Resolving price/source gaps and tick confirmation is a data/validation task; no open-ended stop, clock, side or size search is justified by this report. "
        "The independent review is `agents/codex/results/s03_noisearea_independent_review.md`: implementation checks pass within scope; source/data/causal-placebo concerns remain.", "",
        "Use the configured Python environment and existing cache; do not rebuild grids. Pinned Codex/Claude refs must be available locally. "
        "The prepare commands stage exact source blobs without calculating historical baseline returns. From repository root:", "", "```bash",
        "export PYTHONPATH=analysis", "PY=/workspace/venvs/thebeginning/bin/python",
        f"$PY analysis/codex_s03_run.py --design --prereg-commit {PREREG}",
        "$PY analysis/codex_s03_stats.py --stage design",
        f"$PY analysis/codex_s03_diagnostics.py --stage design --prereg-commit {PREREG} --nulls",
        "$PY analysis/codex_s03_stats.py --certify-design",
        f"$PY analysis/codex_s03_run.py --recent --prereg-commit {PREREG} --gate-file analysis/outputs/codex_s03_noisearea/design_gate.json",
        "$PY analysis/codex_s03_stats.py --stage recent",
        f"$PY analysis/codex_s03_diagnostics.py --stage recent --prereg-commit {PREREG} --gate-file analysis/outputs/codex_s03_noisearea/design_gate.json --nulls",
        "$PY analysis/codex_s03_stats.py --account-gate",
        "$PY analysis/codex_s03_accounts.py --prepare",
        f"$PY analysis/codex_s03_accounts.py --audit-only --prereg {PREREG} --gate analysis/outputs/codex_s03_noisearea/candidate_gate.json --ledger analysis/outputs/codex_s03_noisearea/candidate_V2.csv --held-gaps analysis/outputs/codex_s03_noisearea/candidate_held_gaps.csv",
        "$PY analysis/codex_s03_personal.py prepare",
        "$PY analysis/codex_s03_personal.py --blocked-only --candidate-gate analysis/outputs/codex_s03_noisearea/candidate_gate.json",
        "$PY analysis/codex_s03_stats.py --finalize", "$PY analysis/codex_s03_report.py", "```", "",
        "Account/run commands remain guarded against a false data gate. Source, cache, plan, exact module pins and generated artifact hashes are preserved. "
        "No plan/ranking/live/VPS/broker/API-key changes or external messages occurred.", "",
        "Publication scope approved by the user: scripts, aggregate results, reviews and audit hashes on Dartdark/thebeginning, codex/work. "
        "Detailed trade/order/daily histories and per-draw samples are omitted from the publication, retained in the workspace and reproducible locally.", ""]
    content="\n".join(report)
    replacements={"Top10":"Top 10","DSR0.":"DSR 0.","PF1.":"PF 1.","over14":"over 14","a0.4":"a 0.4",
        "checks10:":"checks 10:","session's15:":"session's 15:","deadline.15:":"deadline. 15:","Source2023":"Source 2023",
        "the14-":"the 14-","open16:":"open 16:","decision16:":"decision 16:","fills16:":"fills 16:",
        "uses actual08:":"uses actual 08:","from the08:":"from the 08:","one08:":"one 08:","cost$":"cost $",
        "ordinarily$":"ordinarily $","used$":"used $","design's1,073":"design's 1,073",";293":"; 293",
        "add$":"add $","Recent:767":"Recent: 767",";246":"; 246","by−$":"by −$","change−$":"change −$",
        "fixed1MNQ":"fixed 1 MNQ","original$":"original $","charges$":"charges $","recent20":"recent 20",
        "best10":"best 10","best25":"best 25","above100":"above 100","supply$":"supply $","shorts$":"shorts $",
        "t0.39":"t 0.39","on2024":"on 2024","entered13:":"entered 13:","exited15:":"exited 15:",
        "is20362":"is 20362","entry20399":"entry 20399","net$":"net $","finds2020":"finds 2020",
        "missing12:":"missing 12:","on2020":"on 2020","All2,290":"All 2,290","least12":"least 12",
        "source2023":"source 2023","Our4":"Our 4","is3.":"is 3.","t3.":"t 3.","fails0.":"fails 0.",
        "misses2":"misses 2","Its2017":"Its 2017","our2018":"our 2018","Known03:":"Known 03:",
        "become research$":"become research $"}
    for a,b in replacements.items():content=content.replace(a,b)
    (ROOT/"agents/codex/results/s03_noisearea.md").write_text(content)
    print("Wrote agents/codex/results/s03_noisearea.md")


if __name__=="__main__":main()
