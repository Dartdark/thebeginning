"""Render the frozen OB v2 experiment from saved replay/diagnostic/account outputs.

No strategy execution, parameter search, or portfolio simulation occurs here.
Decision booleans implement preregistration 7d7714b without selecting a new rule.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_ob_v2_plan_test"
REPORT = ROOT / "agents/codex/results/ob_v2_plan_test.md"


def read(part, name):
    return pd.read_csv(OUT / part / name)


def money(v):
    return f"${v:,.0f}"


def pct(v):
    return f"{100*v:.1f}%"


def pp(v):
    return f"{100*v:+.2f}pp"


def number(v):
    return f"{v:.2f}"


def table(frame, columns, formats=None):
    formats = formats or {}
    lines = ["| " + " | ".join(columns.values()) + " |",
             "| " + " | ".join("---" for _ in columns) + " |"]
    for _, r in frame.iterrows():
        values = []
        for c in columns:
            v = r[c]
            if pd.isna(v):
                text = "—"
            elif c in formats:
                text = formats[c](v)
            elif isinstance(v, (float, np.floating)):
                text = f"{v:g}"
            else:
                text = str(v)
            values.append(text.replace("|", "/"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def difference(frame, config, ref, metric, period=None):
    q = frame[(frame.config == config) & (frame.reference == ref) & (frame.metric == metric)]
    if period is not None:
        q = q[q.period == period]
    if len(q) != 1:
        raise ValueError((config, ref, metric, period, len(q)))
    return q.iloc[0]


def decision_rules(funded, fd, evaluation, ed, fs, es):
    checks = []
    f = funded.set_index("config")
    stress_f = fs.set_index("config")
    e = evaluation.set_index(["period", "config"])
    stress_e = es.set_index(["period", "config"])
    b, sb = f.loc["BASE"], stress_f.loc["BASE"]
    for config in ("REPLACE_OBV2", "ADD_OBV2", "REPLACE_BRIDGE100"):
        a, sa = f.loc[config], stress_f.loc[config]
        p1 = difference(fd, config, "BASE", "year1")
        blown = difference(fd, config, "BASE", "blown")
        empty = difference(fd, config, "EMPTY_ONB", "year1")
        replacement = config.startswith("REPLACE")
        route_a = dict(year1_gain_250=a.year1-b.year1 >= 250,
                       year1_CI_lower_positive=p1.lo > 0,
                       year2_not_100_worse=a.year2 >= b.year2-100,
                       blown_not_1pp_worse=a.blown-b.blown <= .01)
        route_b = dict(year1_not_100_worse=a.year1 >= b.year1-100,
                       year2_not_100_worse=a.year2 >= b.year2-100,
                       blown_reduction_2pp=b.blown-a.blown >= .02,
                       blown_CI_upper_negative=blown.hi < 0,
                       days6_not_10_slower=a.days6 <= b.days6+10)
        versus_empty = not replacement or empty.lo > 0
        # Preserve the direction in the relevant route, without claiming stress
        # must independently clear the primary route's numerical/significance bar.
        stress_a = sa.year1-sb.year1 > 0 and sa.year2 >= sb.year2-100 and sa.blown-sb.blown <= .01
        stress_b = sa.year1 >= sb.year1-100 and sa.year2 >= sb.year2-100 and sa.blown < sb.blown
        if replacement:
            stress_a = stress_a and sa.year1 > stress_f.loc["EMPTY_ONB", "year1"]
            stress_b = stress_b and sa.year1 > stress_f.loc["EMPTY_ONB", "year1"]
        passed = versus_empty and ((all(route_a.values()) and stress_a) or
                                    (all(route_b.values()) and stress_b))
        checks.append(dict(account="funded", config=config,
                           route_a={k:bool(v) for k,v in route_a.items()},
                           route_b={k:bool(v) for k,v in route_b.items()},
                           replacement_beats_empty=bool(versus_empty),
                           stress_direction_route_a=bool(stress_a), stress_direction_route_b=bool(stress_b),
                           pass_review=bool(passed)))
        primary = e.loc[("full", config)]
        base = e.loc[("full", "BASE")]
        ci = difference(ed, config, "BASE", "pass_rate", "full")
        recent = e.loc[("2023_plus", config), "pass_rate"] - e.loc[("2023_plus", "BASE"), "pass_rate"]
        empty_delta = primary.pass_rate-e.loc[("full", "EMPTY_ONB"), "pass_rate"]
        stress_direction = stress_e.loc[("full", config), "pass_rate"] > stress_e.loc[("full", "BASE"), "pass_rate"]
        if replacement:
            stress_direction = stress_direction and stress_e.loc[("full", config), "pass_rate"] > stress_e.loc[("full", "EMPTY_ONB"), "pass_rate"]
        parts = dict(pass_gain_2pp=primary.pass_rate-base.pass_rate >= .02,
                     paired_CI_lower_positive=ci.lo > 0,
                     recent_pass_not_worse=recent >= 0,
                     blown_not_1pp_worse=primary.blown-base.blown <= .01,
                     replacement_beats_empty=not replacement or empty_delta > 0,
                     stress_direction=bool(stress_direction))
        checks.append(dict(account="evaluation", config=config, checks={k: bool(v) for k,v in parts.items()},
                           pass_review=bool(all(parts.values()))))
    return checks


def main():
    m = read("diagnostics", "metrics.csv")
    filt = read("diagnostics", "filter_kept_removed_metrics.csv")
    nulls = read("diagnostics", "matched_random_removal_summary.csv")
    controls = read("diagnostics", "random_side_time_summary.csv")
    mc = read("diagnostics", "standalone_1mnq_montecarlo.csv")
    boot = read("diagnostics", "recent_bootstrap.csv")
    f = read("accounts", "funded_primary_summary.csv")
    fd = read("accounts", "funded_primary_paired_differences.csv")
    fs = read("accounts", "funded_stress_summary.csv")
    e = read("accounts", "evaluation_primary_summary.csv")
    ed = read("accounts", "evaluation_primary_paired_differences.csv")
    es = read("accounts", "evaluation_stress_summary.csv")
    dm = json.loads((OUT/"diagnostics/diagnostics_metadata.json").read_text())
    decisions = decision_rules(f, fd, e, ed, fs, es)
    (OUT/"decision_checks.json").write_text(json.dumps(decisions, indent=2)+"\n")
    candidate = any(x["pass_review"] for x in decisions if x["config"] != "REPLACE_BRIDGE100")
    verdict = "CANDIDATE" if candidate else "WATCH"
    mainrow = m[(m.ledger == "OBV2") & (m.period == "full") & (m.side == "all")].iloc[0]
    fr = f.set_index("config")
    eb = e.set_index(["period", "config"])
    removed = filt[(filt.ledger=="removed") & (filt.period=="full") & (filt.side=="all")].iloc[0]
    timing = controls[(controls.control=="random_entry_time") & (controls.period=="full")].iloc[0]
    parity = json.loads((OUT/"accounts/real_funded_parity.json").read_text())
    synthetic = json.loads((OUT/"accounts/synthetic_parity.json").read_text())
    selfcheck = json.loads((OUT/"replay/execution_selfcheck.json").read_text())
    execution_flags = 0
    for ledger in ("OBV2", "BRIDGE100"):
        a = read("replay", f"{ledger}_full_execution_audit.csv")
        execution_flags += int(a[["delayed_entries","delayed_flats","unfilled","flat_unexecutable",
                                 "partial_native_bars","both_exit_minute","entry_minute_gap_stop"]].sum().sum())
    lines = [f"# OB v2 against the current plans: {verdict}",
      "Summary: Test the submitted ATR-regime ORB as an ONB replacement and a 1-MNQ addition.",
      f"Standalone replay: {int(mainrow.trades)} trades, {money(mainrow.avg)}/NQ net, PF {mainrow.profit_factor:.2f}, t {mainrow.t:.2f}.",
      f"Funded BASE → replacement → addition: year-1 payouts {money(fr.loc['BASE','year1'])} → {money(fr.loc['REPLACE_OBV2','year1'])} → {money(fr.loc['ADD_OBV2','year1'])}.",
      f"Evaluation pass: {pct(eb.loc[('full','BASE'),'pass_rate'])} → {pct(eb.loc[('full','REPLACE_OBV2'),'pass_rate'])} → {pct(eb.loc[('full','ADD_OBV2'),'pass_rate'])}.",
      "Independent review is warranted only for configurations passing every registered account gate." if candidate else
      "No OB v2 configuration clears the registered account gates; keep the current plans.",
      "", "Plan: `agents/codex/plans/ob_v2_plan_test.md`, commit `7d7714b` (pushed before returns).",
      "", "Scripts: `analysis/codex_ob_v2_{replay,accounts,diagnostics,report}.py`.",
      "",
      "Outputs: `analysis/outputs/codex_ob_v2_plan_test/`. Two fixed strategy ledgers; five fixed configurations per account; trial accounting below.",
      "", "## Rule (as tested)", "",
      "User authorized assuming matching data. OBV2 retains the submitted 0.6–1.2 ATR15/ATR100 RTH ratio, ADX(16) ≥20, midnight-to-08:30 overnight bias, 08:30–08:45 opening range, close-confirmed breakout, OR/exhaustion gates, four-entry cap, signal-close 0.30 RTH-ATR stop and 3R target. Signals end at noon; flatten decision 14:30 CT. End-stamped 09:00 signals fill at the open of the minute labeled 09:01.",
      "", "The existing plan's half-day overlay is explicit: no new signals at/after 11:00 CT and 11:30 flatten decision. This differs from the uploaded fixed-time source. BRIDGE100 disables only the ratio and retains identical 100-session warm-up and execution. It is a diagnostic comparator, never an alternative selected from results.",
      "", "The 2017 May–December RTH export seeds indicators in memory; original cached indices and caches stay unchanged. Both ledgers run on common 2018-01-02–2026-10-09 history. Commission is $7.25/NQ RT, one adverse tick per market/stop fill, one-point target trade-through, gap-aware stops including entry minute, stop-first if both exits occur in one minute. Nominal stop-distance risk sizing preserves source-close anchors; actual entry gap risk can differ.",
      "", "The 2018–22 cheap gate passed before any recent returns: 293 trades, $77,284.65 NQ net, PF 1.598, gross $280.75/trade versus $16.98 modeled costs, five profitable years. Longs: 154/$249.04 average; shorts: 139/$280.09. No side or parameter was selected. 2023+ is historical replication: the author had already used it when selecting the filter.",
      "", "## Results", "",
      "Dollar metrics below are per one NQ, after the stated costs. Daily risk ratios include zero-trade trading sessions. DSR uses the current ranked-item count; it does not erase original-author selection exposure.", ""]
    cols = dict(ledger="Ledger",period="Period",side="Side",trades="n",win="Win",avg="$/trade",total="Net",t="t",sharpe="Sharpe",sortino="Sortino",profit_factor="PF",calmar="Calmar",ulcer="Ulcer",max_dd_initial_zero="Max DD",dsr_items="DSR")
    fm = dict(win=pct,avg=money,total=money,t=number,sharpe=number,sortino=number,profit_factor=number,calmar=number,ulcer=number,max_dd_initial_zero=money,dsr_items=number)
    lines += [table(m[m.period.isin(["full","design","recent"])], cols, fm), "",
              "By year, including each side:", "",table(m[~m.period.isin(["full","design","recent"])],cols,fm),"",
              "Max DD above includes the initial zero-equity peak (`resampling.max_dd`). The CSV also retains the unmodified `metrics.perf` convention. Recent block-bootstrap 5/95 bands:","",
              table(boot,dict(ledger="Ledger",side="Side",metric="Metric",actual="Actual",p5="5%",p50="50%",p95="95%")),"",
              "## Placebos and account level", "", "### Filter diagnostics", "",
              "OBV2 is an exact subset of BRIDGE100 at the common warm-up; kept trades have identical fills and exits. The removed trades test the bad-trade-removal claim separately from whether less exposure improves payouts.","",
              f"The filter reduces drawdown, but the {int(removed.trades)} removed trades earned {money(removed.avg)} each (t {removed.t:.2f}). It does not meet the development process's requirement that removed trades lose money; improved average profit alone does not establish a useful filter. The pre-registered account tests were still completed to assess its exposure reduction.","",
              table(filt[(filt.side=="all") & filt.period.isin(["full","design","recent"])],dict(ledger="Group",period="Period",trades="n",avg="$/trade",total="Net",t="t",max_dd_initial_zero="Max DD"),fm),"",
              "Each null uses 1,000 fixed-seed draws per period. Trade drops preserve year/side retained counts; event-day drops preserve yearly retained-day counts and entire within-day sequences. Lower tail probabilities below mean the actual filter beat more random drops; joint dominance is descriptive.","",
              table(nulls,dict(period="Period",kind="Null",actual_total="Actual net",random_total_p50="Null median net",actual_max_dd="Actual DD",random_max_dd_p50="Null median DD",p_random_total_ge_actual="P(null profit ≥ actual)",p_random_dd_le_actual="P(null DD ≤ actual)"),dict(actual_total=money,random_total_p50=money,actual_max_dd=money,random_max_dd_p50=money,p_random_total_ge_actual=pct,p_random_dd_le_actual=pct)),"",
              "Random side and random entry time use 100 replays each, fixed observed event days and stop distances. One-position collisions can reduce counts, so effective counts and total net accompany averages. No control becomes a selected strategy.","",
              f"The precise breakout timing is not supported by this timing null: {round(timing.p_random_total_ge_actual*100)}/100 random-time paths exceeded actual full-period total profit despite fewer effective trades. This is descriptive and conditional on observed event days, not an independently validated replacement rule.","",
              table(controls,dict(control="Control",period="Period",actual_trades="Actual n",effective_trades_min="Min n",effective_trades_median="Median n",effective_trades_max="Max n",actual_total="Actual net",total_p50="Null median net",p_random_total_ge_actual="P(null profit ≥ actual)"),dict(actual_total=money,total_p50=money,p_random_total_ge_actual=pct)),"",
              "Standalone 1-MNQ daily Monte Carlo (5,000 ten-day-block paths, 252-session horizon):", "",
              table(mc[mc.kind=="daily_block"],dict(ledger="Ledger",period="Period",cost="Cost",pnl_p5="P&L 5%",pnl_p50="P&L 50%",pnl_p95="P&L 95%",dd_p95="DD 95%",p_trail_hit="EOD trail hit"),dict(pnl_p5=money,pnl_p50=money,pnl_p95=money,dd_p95=money,p_trail_hit=pct)),"",
              "This existing standalone tool checks EOD equity only. The account comparisons below use minute adverse equity and daily limits. Primary MNQ costs scale NQ costs by 0.1; the mandatory stress adds $1.275/MNQ RT to challenger trades only ($2 commission plus existing slippage). It is an adverse sensitivity, not verified native MNQ accounting.","",
              "### Current funded plan", "",
              "Roster: VB normal 2/flagged 1 MNQ, ONB ML risk $400, Monday 1, EOS risk $700, LDF 2, NFP risk $500, Bridge Monday 1, CL Sunday 2 MCL, ES MOC 2 MES, RS longs 1 MNQ. Existing cushion factor clips to [0.5,1], full size at $1,500 cushion, then floors whole micros. A 1-MNQ addition therefore trades zero when the floored scaled size is below one.","",
              "1,000 paired 500-session circular histories, 20-day blocks, seed 1. Same complete days for all configurations. Days to six uses infinity for noncompletion; outcome bands describe histories, whereas paired intervals estimate mean differences. Baseline differs slightly from the earlier FC 2B table because that run pooled four worker seeds; this preregistration fixes one 1,000-history seed-1 sample.","",
              table(f,dict(config="Configuration",year1="Year 1",year1_p5="Y1 5%",year1_p95="Y1 95%",year2="Year 2",year2_p5="Y2 5%",year2_p95="Y2 95%",blown="Blown",all6="Six payouts",days6="Days to six"),dict(year1=money,year1_p5=money,year1_p95=money,year2=money,year2_p5=money,year2_p95=money,blown=pct,all6=pct)),"",
              "Paired differences, 95% intervals from 5,000 resamples (seed 902); dollar rows use dollars, blown rows use proportions:","",
              table(fd[(fd.config!="BASE") & ((fd.reference=="BASE") | ((fd.reference=="EMPTY_ONB") & fd.config.str.startswith("REPLACE")))],dict(config="Configuration",reference="Reference",metric="Metric",delta="Difference",lo="95% low",hi="95% high")),"",
              "Challenger-only higher-cost sensitivity:","",
              table(fs,dict(config="Configuration",year1="Year 1",year2="Year 2",blown="Blown",all6="Six payouts",days6="Days to six"),dict(year1=money,year2=money,blown=pct,all6=pct)),"",
              "### Current evaluation plan", "",
              "VB 8 MNQ, ONB ADX30 risk $1,100, Bridge Monday 2, EOS risk $500. $3,000 target, $2,000 EOD trail, $1,000 daily limit, 21-session window. All full-length starts are included. The legacy truncated-tail convention is recorded separately. Period labels identify start dates; a late-2022 start can finish in 2023.","",
              table(e,dict(period="Start period",config="Configuration",n="Starts",pass_rate="Pass",blown="Blown",timeout="Timeout",median_pass_days="Median pass days"),dict(pass_rate=pct,blown=pct,timeout=pct)),"",
              "Paired pass-rate differences (95% intervals from 5,000 circular 60-start-block resamples, seed 903):", "",
              table(ed[(ed.metric=="pass_rate") & (ed.config!="BASE") & ((ed.reference=="BASE") | ((ed.reference=="EMPTY_ONB") & ed.config.str.startswith("REPLACE")))],dict(period="Start period",config="Configuration",reference="Reference",delta="Difference",lo="95% low",hi="95% high"),dict(delta=pp,lo=pp,hi=pp)),"",
              "Challenger-only higher-cost sensitivity:","",
              table(es,dict(period="Start period",config="Configuration",pass_rate="Pass",blown="Blown",timeout="Timeout",median_pass_days="Median pass days"),dict(pass_rate=pct,blown=pct,timeout=pct)),"",
              "### Frozen decision", "",
              "Funded route A needs ≥$250 year-1 gain with positive paired lower bound, year-2 no worse than −$100 and blown increase ≤1pp. Route B needs both payout means within $100, ≥2pp lower blown with negative paired upper bound, and days-to-six within +10. Replacements must beat the empty slot with positive year-1 lower bound. Evaluation needs ≥2pp pass gain, positive paired lower bound, nonnegative recent gain, blown increase ≤1pp, and improvement over the empty slot. The direction must survive higher challenger costs.",""]
    for d in decisions:
        if d["account"] == "funded":
            failed_a = ", ".join(k for k,v in d["route_a"].items() if not v) or "none"
            failed_b = ", ".join(k for k,v in d["route_b"].items() if not v) or "none"
            lines.append(f"- Funded {d['config']}: {'PASS for review' if d['pass_review'] else 'FAIL'}. Route A failed: {failed_a}; route B failed: {failed_b}; beats empty gate={d['replacement_beats_empty']}; stress route A/B={d['stress_direction_route_a']}/{d['stress_direction_route_b']}.")
        else:
            failed = ", ".join(k for k,v in d["checks"].items() if not v) or "none"
            lines.append(f"- Evaluation {d['config']}: {'PASS for review' if d['pass_review'] else 'FAIL'}. Failed: {failed}.")
    lines += ["", "A small observed gain is no demonstrated improvement, not proof that portfolios are equivalent. No current plan changes follow from this report.","",
              "## What could make this wrong", "",
              "- Matching market data is the user's assumption. No native OB v2 MultiCharts trade-by-trade pairing or broker fill validation was performed. Target trade-through, same-minute stop priority and source-close brackets are explicitly modeled.",
              "- 2023+ was already observed by the original filter designer. Unknown prior filter trials, platform/feed differences and the existing full-sample-fitted funded ML comparator limit causal/out-of-sample claims. No new parameters were chosen here.",
              "- Whole-day block resampling preserves contemporaneous strategy dependence and short clusters; it cannot create unseen regimes. Paired confidence intervals are conditional on the historical sample and the model.",
              "- Existing CL whole-Monday constant adverse paths and MOC close-only paths remain unchanged. Existing account simulators do not enforce combined position tier caps. Existing evaluation same-minute target/breach ties award the target first. These are account-model limitations, not deployment permission.",
              "- Native MNQ commissions and execution are not established by dividing NQ costs by ten. The challenger-only higher-cost test is deliberately unfavorable to OB v2, while retaining baseline costs for paired comparability.","",
              "### Validation and trial accounting", "",
              f"The current tier parser counts {dm['trials']['ranked_items']} ranked items / {dm['trials']['ranked_variants']} logged variants; promotion t threshold {dm['trials']['promotion_t_threshold']:.3f}. TRIALS.csv separately contains {dm['trials']['trial_csv_items']} rows; it was read, never rebuilt. Two frozen rule ledgers are this experiment's research candidates. The bridge diagnostic is not eligible for post-result selection.","",
              f"Diagnostic evaluations: {dm['matched_removal_samples']} matched-removal draws across two families/three periods; 100 random-side and 100 random-time paths ({dm.get('random_control_period_evaluations',0)} period evaluations); {dm['statistical_evaluations']['bootstrap_series']} recent bootstrap/permutation series; {dm['statistical_evaluations']['mc_evaluations']} standalone MC evaluations. Account tests: five configurations × two cost conventions × two account types; duplicate BASE/EMPTY results reused, 1,000 paired funded histories per configuration, evaluation every full-length start. No best control/stress path is selected.","",
              "The finite-quantity funded acceleration enumerates every reachable daily whole-micro vector and preserves sorted-key sums and the original account state machine. `synthetic_parity.json` and `real_funded_parity.json` record exact equality for all five original simulator outputs, on synthetic fixtures and fixed real histories at 250/500-session horizons. Execution audit CSVs retain missing-bar/flat/gap flags; the cached grid was not rebuilt.","",
              f"Validation: {len(parity)}/{len(parity)} real-history five-output comparisons and {synthetic['exact_original_five_output_checks']} synthetic comparisons match exactly; {synthetic['quantity_checks']:,} quantity probes pass. All {len(selfcheck)} execution branch self-checks pass. Combined historical execution-warning count is {execution_flags}. A separate two-trade fixture verifies that stress fees affect both open risk and realized paths at the correct entries/exits.","",
              "## Differences between the MultiCharts code and the test", "",
              "No new trading code was written. The replay uses the declared half-day overlay, common 100-session warm-up for its unfiltered diagnostic, account risk sizing instead of source fixed contracts, and the frozen execution/cost conventions. The uploaded source's chart IOG settings, bracket activation and `SetExitOnClose` behavior were not independently verified in MultiCharts. No live, VPS, broker, trading-plan or TIER_LIST files were changed.","",
              "Reproduce with the configured Python environment:","", "```bash",
              "/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_replay.py --phase design",
              "# Only after confirming design_summary.json passes the committed gate:",
              "/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_replay.py --phase recent --authorize-recent",
              "/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_replay.py --selfcheck",
              "/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_accounts.py --stage synthetic-parity",
              "/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_accounts.py --stage all --gate-passed",
              "/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_diagnostics.py --obv2 analysis/outputs/codex_ob_v2_plan_test/replay/OBV2_design_trades.csv analysis/outputs/codex_ob_v2_plan_test/replay/OBV2_recent_trades.csv --bridge100 analysis/outputs/codex_ob_v2_plan_test/replay/BRIDGE100_design_trades.csv analysis/outputs/codex_ob_v2_plan_test/replay/BRIDGE100_recent_trades.csv --days analysis/outputs/codex_ob_v2_plan_test/replay/trading_days.csv --generate-controls --allow-return-analysis --design-gate-passed",
              "/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_report.py", "```", ""]
    REPORT.write_text("\n".join(lines))
    print(json.dumps(dict(report=str(REPORT),verdict=verdict,decisions=decisions),indent=2))


if __name__ == "__main__":
    main()
