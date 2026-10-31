"""Render the frozen two-profile experiment; never fits or selects a policy."""
from pathlib import Path
import json
import os
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_rl3690996_build"
REPORT = ROOT / "agents/codex/results/rl3690996_build_20261030.md"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/rl3690996_matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/rl3690996_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import metrics as M


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                       "| " + " | ".join(["---"] * len(headers)) + " |"] +
                      ["| " + " | ".join(map(str, row)) + " |" for row in rows])


def money(x):
    return f"${float(x):,.2f}" if pd.notna(x) else "N/A"


def number(x):
    return f"{float(x):.2f}" if pd.notna(x) else "N/A"


def percent(x):
    return f"{float(x):.2%}" if pd.notna(x) else "N/A"


def nw_t(x):
    x = np.asarray(x, float)
    z = x-x.mean()
    n = len(x)
    variance = z@z/n
    for k in range(1, min(5, n-1)+1):
        variance += 2*(1-k/6)*(z[k:]@z[:-k])/n
    return float(x.mean()/np.sqrt(variance/n)) if variance > 0 else 0.


verification = json.loads((OUT / "ledger_verification.json").read_text())
assert verification["all_checks_passed"]
frames = {p: pd.read_csv(OUT / p / "design/summary.csv", index_col=0)
          for p in ("stocks", "futures")}
gates = {p: json.loads((OUT / p / "design/gate.json").read_text()) for p in frames}
# A passing gate requires the later authorized stages before this negative-result renderer applies.
assert all(not gate["primary_design_pass"] for gate in gates.values())

text = ["""# Corrected stock and MNQ RL builds: REJECT tested selectors

Summary: Both requested Python strategies are built and tested with causal fills, integer positions and reconciled costs.
Neither primary quarterly PPO/A2C/DDPG selector passes its frozen design gate; neither earns a trading-plan allocation.
These are corrected adaptations of SSRN3690996, not a replication of the paper's reported return.
The tables below contain observed net returns; later periods, seed confirmations and Apex portfolio simulations were not earned.

Plan: [frozen protocol](../plans/rl3690996_build_20261030.md), committed `30187666db966efde21fdbeb7e2c0bdc69927522`.
Exact tested engine/environment/trainer committed before returns: `5d4af14174e754caa083125fded1808878e8ae87`.
Script: `analysis/codex_rl3690996_train.py`; [build/reproduction guide](../code/rl3690996/README.md).
Output: `analysis/outputs/codex_rl3690996_build/`; postrun reconciliation: `ledger_verification.json`.
Trials: two adaptations, each four candidates + three declared diagnostic controls + one doubled-cost stress = 16 economic series.
One primary seed3690996; 8,192 training steps per algorithm/quarter. No outcome-based tuning, seed replacement or failed-run deletion.

## Rules and mechanism as tested

The proposed mechanism is adaptive exposure to technical trends while reducing exposure during return turbulence.
It is an allocation hypothesis, without a demonstrated forced-flow or liquidity premium. Quarterly selection can also overfit
the preceding validation window. The source paper's13% annual return and Sharpe1.30 are author claims from another protocol.

**Stocks:** $10,000 cash-funded, long-only, static28-name source panel; DD/RTX excluded before returns for unresolved
merger/spin-off accounting. PPO/A2C/DDPG observe close-derived return/MACD/RSI/CCI/ADX, cash and holdings.
Positive normalized action weights are capped at10% per name; residual stays cash. Integer close-sized targets execute at
the following session's raw-open proxy, sells first, fee-inclusive cash clipping. Costs per side:10bp commission +5bp
adverse slippage. A strictly past-calibrated95th-percentile turbulence overlay targets cash. Shares/splits and cost basis
are ledgered; no dividends. PASSIVE is daily equal-weight target, OVERLAY adds turbulence, LINEAR uses positive63-day momentum.

**MNQ:** -1/0/+1 contract on NQ minute bars as an MNQ execution proxy, $2/point. Completed5-minute RTH observations
08:35–14:55 CT execute at the following minute open; final liquidation14:56. Fixed stop .5 prior15-session RTH ATR,
capped by remaining$250 session strategy-loss budget per contract. Entry-minute stops are active; opening gaps fill at
the worse opening price, then adverse slippage. Reversals pay both legs. A loss latch prevents further entries when
remaining budget cannot cover roundtrip costs. Costs per side: $0.62 commission +one adverse tick ($0.50), $2.24 roundtrip.
PASSIVE is long RTH with these stops/latch/flatten; OVERLAY adds turbulence; LINEAR uses MACD sign plus turbulence.
Only complete observed08:31–15:00 sessions are admitted. The$250 strategy budget is not an Apex trailing floor.

For both, expanding fit ends before a63-session validation window. The highest validation daily Sharpe selects the
following quarter's model, ties PPO/A2C/DDPG. Models are fit independently each quarter. Stock trade holdings carry
between quarters; validation starts flat; futures flatten daily. Fit/validation/trade boundaries are recorded in `selections.csv`.
"""]

fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
for ax, (profile, summary) in zip(axes, frames.items()):
    folder = OUT / profile / "design"
    if profile == "futures":
        # Fixed contract exposure: use dollar-P&L Sharpe/Sortino, as in validation selection.
        # Preserve trainer summary.csv verbatim; publish the reporting basis separately.
        for label in summary.index:
            diagnostics = M.perf(pd.read_csv(folder/(label+"_daily.csv")).net)
            summary.loc[label, "sharpe"] = diagnostics["sharpe"]
            summary.loc[label, "sortino"] = diagnostics["sortino"]
    summary.to_csv(folder/"report_metrics.csv")
    daily = pd.read_csv(folder / "SELECTOR_daily.csv")
    start, end = str(daily.date.min()), str(daily.date.max())
    row = summary.loc["SELECTOR"]
    title = "Daily stocks" if profile == "stocks" else "Intraday MNQ"
    text += [f"\n## {title}: {start}–{end}\n",
             f"{len(daily)} admitted sessions. " +
             ("$10,000 starting cash; net marked-to-market price returns, dividends omitted."
              if profile == "stocks" else
              "Fixed1MNQ, no size compounding. Sharpe/Sortino use daily dollar P&L, consistent with validation selection; percentage/CAGR metrics use a$10,000 analytical denominator, not Apex account equity or return on margin. The trainer's original NAV-return Sharpe remains in summary.csv; reporting metrics are retained separately in report_metrics.csv. Its advancement gate uses analytical NAV returns, as recorded below."),
             "\nNet results after the costs above. CAGR uses252 admitted sessions/year; excluded sessions are not imputed.",
             table(["Policy", "Net", "CAGR*", "Sharpe", "Sortino", "Closed PF†", "Calmar", "Ulcer %", "Max DD", "Max DD %"],
                   [[label, money(r.net), percent(r.annual_return), number(r.sharpe), number(r.sortino),
                     number(r.profit_factor), number(r.calmar), number(r.ulcer), money(r.max_dd), percent(r.max_dd_pct)]
                    for label, r in summary.iterrows()]),
             "\n*CAGR is session-annualized research NAV. †Stock PF uses average-cost partial-sale realizations, not independent complete round trips; stock NAV includes unrealized P&L. MNQ PF uses closed intraday round trips.",
             "\nCost bridge on actual executed quantities (gross is a bookkeeping add-back, not a separately rerun frictionless policy):",
             table(["Policy", "Gross", "Commissions", "Slippage", "Net"],
                   [[label, money(r.gross_on_executed_quantities), money(r.fees), money(r.slippage), money(r.net)]
                    for label, r in summary.iterrows()]),
             "\nRealization/trade diagnostics (same PF basis as above; daily t uses dollar P&L and Newey–West5):",
             table(["Policy", "Realizations/trades", "Win rate", "Average realization/trade", "Daily NW5 t"],
                   [[label, int(r.trades), percent(r.win), money(r.avg), number(r.daily_NW5_t)]
                    for label, r in summary.iterrows()])]
    annual = {label: pd.read_csv(folder / (label + "_years.csv"), index_col=0).net for label in summary.index}
    years = pd.DataFrame(annual)
    text += ["\nAnnual net dollars:", table(["Year"] + list(years.columns),
              [[year] + [money(v) for v in values] for year, values in years.iterrows()])]
    try:
        selected_fills = pd.read_csv(folder / "SELECTOR_fills.csv")
    except pd.errors.EmptyDataError:
        selected_fills = pd.DataFrame(columns=["qty"])
    executed_units = float(abs(selected_fills.qty).sum())
    unit = "share-side" if profile == "stocks" else "contract-side"
    headroom = f"${row.net/executed_units:.6f}" if executed_units else "N/A (no fills)"
    text += [f"\nSigned additional-cost headroom on recorded quantities: {headroom} per {unit}. "
             "A negative value means an equal cost reduction would be required to break even on this recorded path; "
             "it is not a rerun with different costs, positions or cash constraints."]
    gate = gates[profile]
    text += ["\nFrozen selector advancement gate:",
             table(["Check", "Outcome"], [[k, "PASS" if v else "FAIL"] for k, v in gate["checks"].items()]),
             f"\nSELECTOR-minus-OVERLAY daily-return Newey–West(5) t={gate['incremental_NW5_t']:.3f}; required >=2.",
             "**Design fails.** No seed17/29 confirmations, reserved-period test, rescue tuning or dependent portfolio/account test."]
    selection = pd.read_csv(folder / "selections.csv")
    text += ["\nQuarterly earlier-window choices: " + ", ".join(f"{r.quarter}: {r.selected}" for r in selection.itertuples()) + "."]
    if profile == "stocks":
        text += ["\nLong-only; shorts N/A. A positive stock price return alone is insufficient: the selector must beat its risk-overlay and passive controls under the preregistered tests."]
    else:
        overlay_daily = pd.read_csv(folder/"OVERLAY_daily.csv")
        dollar_t = nw_t(daily.net.to_numpy()-overlay_daily.net.to_numpy())
        text += [f"\nFixed-size dollar-P&L diagnostic: selector minus overlay net {money(row.net-summary.loc['OVERLAY', 'net'])}, "
                 f"NW5 daily-dollar difference t={dollar_t:.3f}. The frozen gate above uses each strategy's evolving analytical-NAV daily returns; "
                 "its arithmetic-mean ranking can differ from net dollars when capital paths differ. This reporting diagnostic does not replace "
                 "the frozen gate. The selector also fails the passive comparison, doubled-cost and positive-year checks."]
        sides = json.loads((folder / "SELECTOR_sides.json").read_text())
        try:
            closed = pd.read_csv(folder / "SELECTOR_closed.csv")
        except pd.errors.EmptyDataError:
            closed = pd.DataFrame(columns=["date", "side", "net"])
        side_t = {name: nw_t(closed[closed.side == sign].groupby("date").net.sum().reindex(daily.date, fill_value=0))
                  for sign, name in [(1, "long"), (-1, "short")]}
        for sign, name in [(1, "long"), (-1, "short")]:
            d = closed[closed.side == sign].groupby("date").net.sum().reindex(daily.date, fill_value=0).to_numpy()
            eq = 10000+np.cumsum(d)
            peak = np.maximum.accumulate(np.r_[10000., eq])[1:]
            r = sides[name]
            r["max_dd"] = float((peak-eq).max())
            r["ulcer"] = float(np.sqrt(np.mean(((eq/peak-1)*100)**2)))
            r["calmar"] = r["annual"]/r["max_dd"] if r["max_dd"] > 0 else np.nan
        text += ["\nSelected MNQ side attribution (isolated side P&L; Sharpe/Sortino use daily dollars; DD includes initial capital):",
                 table(["Side", "Net", "Trades", "Win rate", "Sharpe", "Sortino", "PF", "Calmar", "Ulcer", "Max DD", "Daily t"],
                       [[side, money(closed.loc[closed.side == (1 if side == "long" else -1), "net"].sum()), r["trades"], percent(r["win"]), number(r["sharpe"]),
                         number(r["sortino"]), number(r["profit_factor"]), number(r["calmar"]), number(r["ulcer"]),
                         money(r["max_dd"]), number(side_t[side])] for side, r in sides.items()])]
        # Raw native position, loss-budget exceptions and adverse observations remain inspectable.
        text += [f"\nWorst completed session: {money(daily.net.min())}; worst minute adverse equity versus session start: {money(daily.adverse.min())}.",
                 f"Sessions below nominal-$250 loss budget: {int((daily.net < -250-1e-7).sum())}. Gap/slippage risk is retained, not clipped from reported losses."]
    for label, style in [("SELECTOR", "-"), ("OVERLAY", "--"), ("PASSIVE", ":"), ("SELECTOR_2X_COST", "-.")]:
        curve = pd.read_csv(folder / (label + "_daily.csv"))
        ax.plot(pd.to_datetime(curve.date.astype(str)), curve.net.cumsum(), style, label=label, linewidth=1.3)
    ax.set(title=title + (" — $10,000 initial cash" if profile == "stocks" else " — fixed1MNQ"), ylabel="Cumulative net P&L ($)")
    ax.axhline(0, color="grey", linewidth=.6)
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=.2)
fig.savefig(OUT / "equity.png", dpi=160)
plt.close(fig)

text += ["""
## Net equity paths

![Selected RL and fixed controls, after costs](../../../analysis/outputs/codex_rl3690996_build/equity.png)

The panels use different periods and exposure, not equal risk. Lines plot cumulative net dollars; the doubled-cost
line is a rerun of the frozen selector without selecting a different model.

## Verification, placebos and account placement

All12 pre-return synthetic mechanics groups pass (`mechanics.json`): next-bar clocks, fee-inclusive cash, integer shares,
split/basis continuity, reversal legs, entry-minute stop/gap, final flatten/latch, missing-bar rejection, causal-feature
prefix invariance and Gym interface bounds. Independent postrun CSV replay verifies every reported policy's fee/slippage,
cash/shares/NAV or native-contract roundtrip/daily P&L and chronological folds/selection (`ledger_verification.json`).
This is implementation verification, not independent economic replication or a live fill certificate.

The declared passive/overlay/linear policies and doubled-cost stress are completed controls. Neither selector passes the
cheap design gate, so random-time/side and random-drop placebos, reserved-period bootstrap, seed confirmations, Apex
Monte Carlo and BASE/ADD/REPLACE/EMPTY account contribution tests are **not run**, following the stop rule. No claim of
measured portfolio harm, diversification, payout benefit or trail safety is made. Four candidates per profile plus all
controls/stress count in the research record. Design significance is not multiplicity-adjusted promotion.

| Home | Stock version | MNQ version |
| --- | --- | --- |
| Personal | No earned place: failed design; data limits remain | No earned place: failed design |
| 50K evaluation | Ineligible cash-stock/overnight instrument | No earned place; account/floor tests not earned |
| 150K evaluation | Ineligible cash-stock/overnight instrument | No earned place;2MNQ sizing/account tests not earned |
| 50K funded | Ineligible cash-stock/overnight instrument | No earned place; payout/contribution tests not earned |
| 150K funded | Ineligible cash-stock/overnight instrument | No earned place; payout/contribution tests not earned |

## What could make these estimates wrong

- Stock data are the author's static historical panel, not a certified point-in-time constituent universe. Dividends
  are missing; unresolved DD/RTX lineages were excluded before outcomes. Known factor-ratio splits are handled, but
  authoritative ex-date cash/merger/rights/auction and settlement accounting are not certified. The panel ends2020-08-17,
  making2023+ stock validation impossible here. Stock2018–2019 is an explicitly narrower design, not a canonical2018–2022 test.
- Futures use a continuous NQ grid as an MNQ proxy, without contract-specific bid/ask/queue/latency certification.
  Across the prepared2017–2026 input97 incomplete RTH sessions were excluded and enumerated. Results condition on
  complete observed sessions, including the design's admitted subset; missing/holiday sessions are not invented zero returns.
- Native stop/gap assumptions and the$250 strategy loss latch do not simulate Apex intraday floors, resets, consistency
  or payouts. Doubled costs rerun the frozen policy's execution but do not retrain or reselect it under stress.
- One seed and a deliberately bounded8,192-step fit per algorithm/quarter do not establish learning convergence or
  a failure of all RL. These results reject these frozen implementations at this compute budget. All predictions are
  historical walk-forward research; previously inspected history is not a fresh prospective holdout.
- The standalone MNQ DDPG diagnostic loses more than the$10,000 normalization capital. Its originally saved evolving-NAV
  return ratios cross zero and are not useful performance measures. This report uses fixed-size dollar-P&L Sharpe/Sortino
  and leaves its CAGR N/A. The experiment is not a solvency/margin-constrained futures account simulation.
- Daily stock open/close marks omit intraday adverse excursions. Stock drawdown is a daily NAV measure; MNQ retained
  minute adverse records are separate from the reported daily-equity drawdown. Size/capital differs, so dollar or
  percentage results do not compare equal risk between the adaptations.

## Code and next action

Both Python strategy environments, learners, selectors and complete ledgers are delivered; model ZIPs/features remain
Git-ignored runtime artifacts with hash-bound cache receipts. The [guide](../code/rl3690996/README.md) gives environment,
raw-input provenance and exact reproduction commands. No PowerLanguage version was made: the financial gate failed,
and translating a neural policy also requires its trained weights/state pipeline. No live/broker/VPS/plan files changed.

Do not allocate these selectors or tune them against the failed design. Tell Claude to independently review
`agents/codex/results/rl3690996_build_20261030.md`. The execution lessons remain under E58 in
[the execution-reference library](../EXECUTION_REFERENCES.md); the original engine audit is retained separately.
"""]
REPORT.write_text("\n\n".join(text).rstrip() + "\n")
print(REPORT)
