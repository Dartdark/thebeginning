"""Reproduce the concise research report/spec/figure from committed Flow Six outputs.

No strategy replays or searches. Run only after design, validation, diagnostics.
"""
from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_nq_day_flow6 as F


def table(frame, columns, formats=None):
    formats = formats or {}
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for _, row in frame.iterrows():
        cells = [formats[c](row[c]) if c in formats else str(row[c]) for c in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def money(x):
    return f"${x:,.0f}"


def two(x):
    return f"{x:.2f}"


def main():
    out = F.OUT
    m = pd.read_csv(out / "metrics.csv")
    primary = m[(m.period == "full") & (m.side == "all")].iloc[0]
    fees = pd.read_csv(out / "cost_sensitivity.csv")
    boot = pd.read_csv(out / "bootstrap.csv")
    risks = json.loads((out / "risk.json").read_text())
    personal = pd.read_csv(out / "personal_comparison.csv")
    target = json.loads((out / "target_result.json").read_text())
    binding = json.loads((out / "source_binding.json").read_text())
    trials = json.loads((out / "trial_accounting.json").read_text())
    exposure = json.loads((out / "exposure.json").read_text())
    dt, dd = F.read_phase("design")
    vt, vd = F.read_phase("validation")
    t, d = pd.concat([dt, vt], ignore_index=True), pd.concat([dd, vd])
    violations = t[(t.source_exit_stamp.dt.hour*60+t.source_exit_stamp.dt.minute)>959]
    F.save_csv(out / "flat_deadline_exceptions.csv", violations)
    metadata = []
    for name, filename in F.REPORTS.items():
        path = F.ROOT / "mc_reports" / filename
        s = pd.read_excel(path, sheet_name="Settings", header=None)
        mapping = dict(zip(s.iloc[:,0].astype(str),s.iloc[:,1].astype(str)))
        metadata.append(dict(sleeve=name, settings={k:v for k,v in mapping.items() if k in
            ("Compression","Bar Magnifier","Backtesting Assumptions","Commission","Slippage","Start Date","End Date")}))
    F.save_json(out / "report_settings.json", metadata)
    specs = dict(name="NQ Day Flow Six", status="historical_t6_pass_execution_not_cleared",
        prereg=binding["prereg"], primary_fee_RT_MNQ=1.24, slippage_per_market_stop_fill_ticks=1,
        alternative_fee_RT_MNQ=1.04, primary_price_source="NQ continuous, not native MNQ quotes",
        selection="One precommitted combination; no weight search. Constituents previously selected.",
        source_ref="41a0ae6", current_plan_ref="afde088 / 94a1627",
        sleeves=[dict(sleeve=k, intended_micro_contracts=1, source=F.SOURCES[k],
            source_sha256=binding["inputs"][F.SOURCES[k]], report="mc_reports/"+F.REPORTS[k],
            overrides={"NumContracts":1,**({"RiskPerTrade":0} if k!="VB" else {})},
            remaining_inputs="Source defaults; exact report/source parity still requires combined-platform check") for k in F.REPORTS],
        manager_policy="Own each sleeve's virtual target separately; actual account target = sum. Exit only its sleeve; reconcile actual net delta.",
        allowed_virtual_targets=[-1,0,1], theoretical_gross_cap=6, observed_proxy_gross_max=exposure["max_virtual_gross"],
        statistical_target=target["target_tests"], reference_manager="analysis/codex_nq_day_flow6.py:VirtualSleeves",
        blockers=["MON 2023-07-03 holds to 17:05", "NFP 2023-04-07 holds to Sunday 17:05",
                  "No combined native MC virtual-order/netting parity", "No fresh holdout/forward evidence",
                  "Reference lacks ticket-generation IDs and actual broker fill state"],
        runnable_scope="Offline MC-ledger composition and virtual-target accounting only; no broker or live adapter")
    F.save_json(F.ROOT / "agents/codex/inputs/nq_day_flow6/strategy_spec.json", specs)
    formats = {k:two for k in ("sharpe","sortino","profit_factor","calmar","ulcer","t_trade","t_daily","t_nw5","t_nw20")}
    formats.update({k:money for k in ("annual","max_dd","total","avg","dd95","mean_year","incremental_mean")})
    formats["win"] = lambda x: f"{x:.1%}"
    formats["trades"] = lambda x: str(int(x))
    formats["median_profit_dd95"] = two
    metrics = table(m[m.period.isin(["2018-22","2023+","full"])],
        ["period","side","trades","win","avg","annual","sharpe","sortino","profit_factor","calmar","ulcer","max_dd","t_trade","t_daily","t_nw5"], formats)
    years = table(m[(m.side=="all") & ~m.period.isin(["2018-22","2023+","full"])],
        ["period","trades","total","sharpe","profit_factor","max_dd"], formats)
    sensitivity = table(fees[fees.period=="full"],["case","total","t_trade","t_daily","t_nw5"],formats)
    b = boot[(boot.side=="all") & (boot.period=="2023+") & boot.metric.isin(["sharpe","sortino","pf_day","max_dd","annual"])]
    uncertainty = table(b,["metric","actual","p5","p95"],{c:two for c in ["actual","p5","p95"]})
    riskrows = pd.DataFrame([r for r in risks if r["kind"]=="EOD_only_year" and r["side"]=="all"])
    riskformats = {"p_trail_hit":lambda x:f"{x:.1%}","p_loss":lambda x:f"{x:.1%}","dd_p95":money,"pnl_p50":money,"trail":money}
    risk_table = table(riskrows,["period","trail","pnl_p50","dd_p95","p_loss","p_trail_hit"],riskformats)
    pc = personal[(personal.cohort=="FULL") & (personal.period=="2023+")]
    personal_table = table(pc,["contrast","mean_year","dd95","median_profit_dd95","incremental_mean"],formats)
    audit = json.loads((out / "design_audit.json").read_text()) + json.loads((out / "validation_audit.json").read_text())
    missing = sum(r["observed_held_missing_minutes"] for r in audit)
    held_gaps = sum(r["observed_held_missing_minutes"] for r in audit if r["sleeve"] != "NFP")
    sig = pd.read_csv(out / "significance.csv")
    dsr = sig[(sig.period=="full") & (sig.side=="all") & (sig.trial_lower_bound==10000)].iloc[0].dsr_daily
    report = f"""# NQ Day Flow Six: WATCH — historical t6 achieved, execution not cleared

Summary: One fixed six-leg NQ composite reaches net trade t {primary.t_trade:.2f}, daily t {primary.t_daily:.2f}, Newey-West(5) t {primary.t_nw5:.2f}.
At one MNQ per sleeve: {int(primary.trades):,} tickets, {money(primary.annual)}/year, PF {primary.profit_factor:.2f}, closed-EOD DD {money(primary.max_dd)}.
2023+ adjusted daily t is 5.21; four-tick stress reduces full adjusted t to 5.89.
Two inherited holiday/session holds and unconfirmed combined netting block an Apex-ready or deployable claim.
Known-signal recombination, not new independent alpha; no ranking, allocation, live action or new PowerLanguage.

Plan: `agents/codex/plans/nq_day_flow6.md`, committed **{binding['prereg']}** before composite returns.
Design saved in **e1e924b** before validation. Scripts: `analysis/codex_nq_day_flow6.py` and `_report.py`.
Outputs: `analysis/outputs/codex_nq_day_flow6/`. Specification: `agents/codex/inputs/nq_day_flow6/strategy_spec.json`.
Trials: **one new combination**; no weight/parameter search. Source selections and earlier portfolio tests are prior trials.

## Rule as tested

Run the existing **Vault Break, ONB ML v2, Monday Long, Expiration Open Short, Late-Day Flow and NFP Fade**
as six virtual sleeves. Each source trade gets **one MNQ**, with the existing direction, stop, target and time exit.
For source inputs use `NumContracts=1`, and `RiskPerTrade=0` where present. Exact source/report hashes and defaults
are in the specification; this is an offline composition of actual MC tickets, not a new independent signal-engine rebuild.
The six intraday systems were taken from the prior seven-leg alpha study; overnight Bridge Monday was excluded in advance.

The broker target in a future combined manager is the sum of virtual targets, rather than independently submitted
chart positions. Opposing sleeves can coexist virtually with zero actual net exposure. Every sleeve retains ownership
of its stop/exit; repeated exits cannot create a new position. Reference target accounting passes synthetic checks.
It is intent arithmetic only: a delayed old-ticket exit can erase a new same-sleeve intent because the reference
lacks ticket-generation IDs and confirmed broker fill state. The independent review identifies this execution blocker.
Observed minute-grid maximum: **{exposure['max_virtual_gross']:.0f} gross / {exposure['max_net']:.0f} net MNQ**, versus a theoretical six-contract cap;
{exposure['sessions_with_opposing_sleeves']} sessions contain opposing virtual sleeves. Exact same-minute order sequence is not independently verified.

## Results

Window: **2018-01-01 through 2026-10-09**, {int(primary.days):,} repository-calendar sessions.
Primary cost is **$1.24 per MNQ round trip plus $0.50 for each market/stop fill**. Targets have no extra exit slip.
Charge every virtual ticket even when a net order manager might save fees. Gross ${primary.gross:,.2f}, costs ${primary.costs:,.2f}, net ${primary.total:,.2f}.
Native MNQ fills are not observed: this reprices NQ source prices with independently modeled micro fees.
All annual figures use 252 sessions/year. DD is closed/EOD, includes the initial zero, and excludes intraday open-equity DD.

{metrics}

Trade t treats tickets independently and is secondary to the daily statistics; same-day clustering is preserved
by daily aggregation and the daily Newey-West figures. Full NW(20) t is {primary.t_nw20:.2f}.
The design screen passed before validation; 2023+ is historical validation already used by the constituent research,
not an untouched holdout. T>=6 is an observed full-sample statistic, not an expected forward statistic.

{years}

2018 loses money; no year or side was removed. 2026 is partial through October 9.

## Costs, uncertainty and prior selection

{sensitivity}

Four adverse ticks per slipped fill still leave positive returns but **fail the adjusted t6 target**.
2023+ 90% ten-session/5,000-path bootstrap intervals:

{uncertainty}

Both sides' bootstrap/permutation results are saved. The 10,000-trade bootstrap is descriptive because
the tickets overlap; daily block resampling is the main uncertainty measure.
Latest tier parser counts **{trials['prior_ranked_items']} prior ranked items**, plus this combination; parsed variants
are {trials['parsed_prior_variants']:,}, an incomplete lower bound. Daily DSR at the 10,000-search sensitivity is {dsr:.5f}.
Neither DSR nor t removes constituent-selection bias. Existing VB parameter searches, ONB model/filter selection,
and earlier books have already used these years. No claim of six newly independent alpha discoveries.

The 2,000 session-level gross-sign-flip null is exceeded in every draw in full and 2023+ (corrected p=1/2001).
It preserves dependence across same-day sleeves and subtracts fees, but is **not an executable random-entry or
random-side bracket placebo**. Individual source studies supply earlier execution-placebo evidence; this study
does not newly establish those results. No filter/random-drop search was introduced.

## Account and portfolio context

Standalone one-year EOD-only simulations, 5,000 ten-session paths, fixed one-MNQ sleeve quantities:

{risk_table}

These omit intraday liquidation, daily loss stops, payout/qualification rules and combined fills. They are not
evaluation pass rates or funded-account blow-up probabilities. In particular, $2k EOD-trail risk is material.
All four requested Apex contexts (50K/150K evaluation/funded) are **not cleared**: the frozen report tickets contain
session-hold violations, and current-book ADD/REPLACE/EMPTY account claims also lack causal joint overnight baselines.
No full current-account bench was invented from daily/proxy paths.

Current personal FULL19 at afde088, 2023+ pool, 1,000 paired 252-session ten-day histories:

{personal_table}

BASE contains these same six legs. ADD doubles their exposure; REPLACE substitutes the basket for those six;
EMPTY removes them. The roughly $67 annual REPLACE difference is source/fee/bookkeeping reconciliation,
**not new alpha**. ADD's modest profit/DD point gain is not an allocation recommendation. Starter A-D controls
are saved separately; replacing only their present matching legs also changes which signals they contain.
The full-book correlation is {pc.iloc[0].correlation:.2f}; candidate net on book-loss days is {money(pc.iloc[0].candidate_on_book_loss)}.
This is equity-index exposure, not protection. No missing personal dates or candidate money were silently remapped.
Baseline inherited fee, overnight-marking, and missing OT-history limits remain; daily DD does not verify margin safety.

## Execution failures and evidence limits

- **MON:** July 3, 2023 08:35 entry label, exit **17:05 that day**, after the shortened cash session and CME break.
- **NFP:** April 7, 2023 07:50 entry label, exit **Sunday April 9 at 17:05**. Both losing tickets remain in every total.
- 17:00+ exits are booked to the next CME date (July 4 / April 10), with original price-date stamps retained.
- {missing:,} unobserved held minutes in aggregate: most are the NFP holiday/weekend span, not verified feed failures;
  other sleeves contribute {held_gaps:,}, including MON's shortened session/break. No absent price was fabricated or gap trade deleted.
- All six reports say one-minute Bar Magnifier enabled. `report_settings.json` records each source fill-through,
  commission and slippage setting. Our costs are applied explicitly rather than accepting the reports' zero costs.
- Source limit fills, minute ordering, current source-file parity, roll-switch handling and native MNQ queues remain
  execution assumptions. The combined manager was not run in MultiCharts, and the target-position reference is not
  a complete signal generator, order router, calendar fix or deployable strategy file.

## Independent check and next step

Independent ledger/statistics review: `agents/codex/results/nq_day_flow6_independent_review.md`;
checker script/output: `analysis/codex_nq_day_flow6_checker.py`, `analysis/outputs/codex_nq_day_flow6_checker/`.
Verdict: **PASS WITH CONCERNS for historical accounting only**; all 3,615 tickets and 2,262 daily totals reconcile.
This is independent workbook arithmetic and inference, not a second raw-signal reconstruction or platform confirmation.

The requested **historical t6 composite exists**. Its constituents already belong to the research book; do not add
it on top automatically. Recommended next step: freeze a separate operational calendar/netting implementation,
then verify its changed trade list in a research MultiCharts run and a prospective paper log before any trading decision.
This frozen study retains its original rule and exceptions; no after-results repair, weight search or deployment was run.

Reproduce with the existing cloud interpreter, from the repository root:

```bash
/workspace/venvs/thebeginning/bin/python -B analysis/codex_nq_day_flow6.py --phase design --prereg d27cda2
/workspace/venvs/thebeginning/bin/python -B analysis/codex_nq_day_flow6.py --phase validation --prereg d27cda2
/workspace/venvs/thebeginning/bin/python -B analysis/codex_nq_day_flow6.py --phase diagnostics --prereg d27cda2
/workspace/venvs/thebeginning/bin/python -B analysis/codex_nq_day_flow6_report.py
```

Writes are exclusive and compare pre-existing bytes; original artifacts are preserved. Bookkeeping fixes for the
observed cross-date/after-reopen report exits changed neither source tickets nor weights. No scientific package or
shared price/account cache was installed/rebuilt, no root/shared plan edited, no other branch pushed.
Claude review path: `agents/codex/results/nq_day_flow6.md`.
"""
    F.save_bytes(F.ROOT / "agents/codex/results/nq_day_flow6.md", report.encode())
    make_figure(d)
    artifacts = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "final_manifest.json")
    artifacts += [F.ROOT / "analysis/codex_nq_day_flow6.py", Path(__file__),
        F.ROOT / "analysis/codex_nq_day_flow6_checker.py",
        F.ROOT / "agents/codex/results/nq_day_flow6.md",
        F.ROOT / "agents/codex/results/nq_day_flow6_independent_review.md",
        F.ROOT / "agents/codex/inputs/nq_day_flow6/strategy_spec.json"]
    F.save_json(out / "final_manifest.json", dict(prereg=binding["prereg"],
        artifacts={str(p.relative_to(F.ROOT)):F.digest(p) for p in artifacts},
        scope="Historical one-variant composite; independent ledger check; execution not cleared"))
    print(f"Report: agents/codex/results/nq_day_flow6.md; full NW5 t={primary.t_nw5:.4f}")


def make_figure(d):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    equity = d.total.cumsum()
    peak = np.maximum.accumulate(np.r_[0.,equity.to_numpy()])[1:]
    fig, axes = plt.subplots(2,1,figsize=(10,5.5),sharex=True,gridspec_kw={"height_ratios":[2,1]})
    axes[0].plot(equity.index,equity,color="#116466",linewidth=1.4)
    axes[0].set_title("NQ Day Flow Six · one MNQ per sleeve · historical composition")
    axes[0].set_ylabel("Cumulative net ($)")
    axes[1].fill_between(equity.index,equity-peak,0,color="#a94e42",alpha=.7)
    axes[1].set_ylabel("Closed/EOD DD ($)")
    for ax in axes:
        ax.axvline(pd.Timestamp("2023-01-01"),color="#777777",linestyle="--",linewidth=.8)
        ax.grid(alpha=.2)
    fig.text(.11,.01,"$1.24/MNQ round trip + 1 tick per slipped fill. Existing selected signals; two source session holds; no combined execution clearance.",fontsize=8)
    fig.tight_layout(rect=[0,.035,1,1])
    buf = BytesIO()
    fig.savefig(buf,format="png",dpi=150)
    plt.close(fig)
    F.save_bytes(F.OUT / "equity_drawdown.png",buf.getvalue())


if __name__ == "__main__":
    main()
