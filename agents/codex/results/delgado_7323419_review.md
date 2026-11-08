# “Beat the Market” revisited: useful audit; no new portfolio placement

Summary: Independent author replication supports the historical SPY noise-band/VWAP result, not permanent alpha.
Author reports19.6%annual/Sharpe1.317for2007–24, but−8.1%/Sharpe−0.461inSeptember2025–August2026.
The selected overlays improve historical Sharpe/drawdown after80adaptive SPY alternatives, without a clean holdout.
Our related futures family already has weak/rejected placement results; those are not tests of this SPY candidate.
No admitted native SPY minute panel/package: retain a low-priority data lead, build no planner, change no allocations.

Source: José Enrique Delgado, *“Beat the Market” Revisited: An Independent Replication and Statistical Audit of an
Intraday Momentum Strategy*, August20,2026;23pages, [SSRN7323419](https://ssrn.com/abstract=7323419),
postedAugust21,2026. ReviewedNovember8,2026(America/Los_Angeles).
[Archived upload](../inputs/delgado_7323419/ssrn-7323419.pdf) ·
[full extracted text](../inputs/delgado_7323419/full_text.txt) ·
[free source/data receipt](../inputs/delgado_7323419/free_data_gate.md).
Scope: full text including the replication, recent-window reconciliation, selected rules, statistical audit and appendices.
Source claims are not independently reproduced by us. The document's prospective protocol is source material,
not an instruction to launch a monitor, contact anyone or change our research/trading process.

Script: [claim/arithmetic/prior-input audit](../../../analysis/codex_delgado_7323419_audit.py) ·
[JSON receipt](../../../analysis/outputs/codex_delgado_7323419/source_audit.json).
New economic trials/account simulations:0/0. No strategy/planner or MultiCharts code built.

## Five questions

1. **What is it about?** Independently reproducing Zarattini/Aziz/Barbon's SPY intraday momentum strategy,
   checking post-publication performance, and auditing a subsequent adaptive search for risk/sizing improvements.
2. **What does it find?** The historical result is closely reproduced on another vendor after matching typical-price
   VWAP and VWAP entry confirmation. Performance initially remains strong after publication, then weakens sharply.
   Selected overlays yield a smoother but lower-return historical portfolio. Those overlays were selected with
   recent history visible; they are not prospectively validated. Cross-asset results are mixed.
3. **Why does it make money, if it does?** The proposed mechanism is sustained intraday price persistence beyond
   normal time-of-day movement, possibly linked to underreaction/slow portfolio adjustment. The entry follows
   that move and band/VWAP exits attempt to retain trend-day exposure. No compelled participant or measured
   order imbalance establishes causality. Historical profit is author evidence; reversals, repeated stops, costs and
   concentration in strong trends can erode it. VWAP confirmation does not itself prove executable alpha.
4. **Can we build on it?** Yes as qualified evidence for the existing intraday trend family and as an execution/
   research-audit reference. A literal SPY personal study is conditional on usable minute/corporate-action inputs
   and an authenticated engine/ledger. It does not justify reopening failed NQ overlays, assuming ETF costs on
   futures, or changing our current book. Preserve prior negative account evidence and compare any genuinely
   eligible candidate against BASE/ADD/REPLACE/EMPTY at actual size before promotion.
5. **Can a strategy code be made?** **Yes:** this is a mechanical directional intraday strategy, with explicit
   noise/VWAP entry rules and frozen overlay formulas. Exact reproduction still needs signal/fill/stop/minimum-fee/
   dividend/session conventions and the source package. A valid personal backtest requires actual SPY minute
   data and native share/cash/borrow/margin costs. No code is built while that gate fails; feasibility is not profit.

## Historical profitability actually reported

All numbers in this table are **Delgado's reported simulations**, not our returns or a personal recommendation.

| Rule/window | Return | Sharpe | Maximum drawdown | Interpretation |
|---|---:|---:|---:|---|
| Original-rule replication,May2007–April2024 |19.6%annual;1,989%total |1.317 |−24.5% | Closest paper match; omits dividend adjustment |
| Exact post-publication,May13,2024–August29,2025 |+23.3%total |1.284 |−9.4% | Supports initial persistence after publication |
| September2,2025–August14,2026 |−8.1%total |−0.461 |−17.4% | Later weakness; not proof of permanent decay |
| Full baseline,2000–August2026 |14.7%CAGR |0.996 |−24.6% | Broader history is weaker than selected paper window |
| Final selected candidate,2000–August2026 |12.4%CAGR |1.274 |−14.8% | Retrospective selection, not a fresh holdout |

The original paper claims1,985%/Sharpe1.33; Delgado reports1,989%/1.317on another vendor. Matching the
published code's dividend convention instead gives approximately1,965.4%/1.314. This unresolved paper/code
convention is disclosed, not evidence of fabricated performance. Those results use different engine conventions
from the final candidate; do not combine its leverage/fee/calendar corrections with the old replication label.

May1,2024is a monthly-comparison start that predates the original May10publication. Delgado explicitly
separates it from the exact May13post-publication start. The pooledMay2024–August2026Sharpe0.35hides
the initially strong and subsequently weak intervals. Neither window is clean OOS for the later selected overlays.

## Source rule and selected additions

- Mean absolute move from the cash open at each same-time checkpoint over14prior sessions; gap-aware bands
  use max/min(today's open, dividend-convention prior close). This estimator is not SD/ATR.
- Half-hour decisions, long above upper band **and** VWAP, short below lower band **and** VWAP. VWAP uses
  cumulative minute typical price `(H+L+C)/3` times total volume. Dynamic exit levels use max(upper,VWAP)
  for longs and min(lower,VWAP) for shorts. Exact fill and stop sampling require the source engine.
- Base leverage targets2%daily volatility from prior14daily returns, capped4x. Source base commission
  is$0.0035/share plus$0.001/share slippage **per side**; final minimum commission amount is not specified here.
- Final source settings: long band multiplier1.3, short1.6, short size0.75; cumulative relative-volume sizing
  clipped0.5–1.5against14prior same-time cumulative volumes; size0.7when the noise band binds the exit,
  otherwise1. A30-day lagged **overlay-free shadow** return sum sets size0.9after positive performance,
  1.1otherwise, neutral during warmup. Apply an actual4xcap **after every multiplier**, with dividend-aware
  anchors, minimum commission and early-close liquidation.

The shadow strategy must remain separate from overlay-scaled realized P&L. Substituting the latter changes
the feedback rule. A checkpoint-close feature cannot justify filling at the same observed close without an
executable protocol. Share rounding, open orders, marked leverage, borrow/cash and early closes still matter.

## Statistical scope and transfer limits

The129-rowledger contains80selection-relevant SPY alternatives:31before VWAP correction,49after. Only70
daily return series are reconstructed;10missing alternatives still count. The25-point sensitivity grid uses
the **pre-correction** engine. Its38.49%/40.87%PBO uses10blocks/252splits and changes with warmup/sample
convention. It is not a40%probability that the final80-trial selected strategy is false or will lose money.
Our script checks only percentage/count arithmetic; no CSCV ranking or DSR is reproduced without raw series.

The selected99.999986796%DSR retains80trials, estimating Sharpe dispersion from78comparable full-history
observations. It is not a probability of future profitability, market stability or personal-account survival.
The author acknowledges adaptive search, missing series, engine changes and an already-inspected2024–26window.
The paper does not report one valid full80-alternativePBO. Near-perfect DSR and unstable parameter selection
answer different questions and can coexist. Preserve all failed definitions and actual return-valid start dates.

Cross-asset author evidence is particularly relevant: QQQ base Sharpe0.987falls to0.809with SPY ConfigJ,
0.913with SPY volume sizing and0.967with the SPY performance overlay. QQQ base works historically, yet
the SPY-selected improvements do not improve its Sharpe. IWM base Sharpe is only0.450. Neither proves what
happens on NQ/MNQ; the paper does not independently reproduce the original authors'33-futures claim.

## Our existing evidence and account decision

Read existing evidence, not rerun or newly selected:

| Existing study | Relevant established result | Limit |
|---|---|---|
| [ES-as-SPY proxy](../../../analysis/outputs/beat_the_market_es_test_output.txt) | LB14Sharpe1.30at SPY-style costs versus0.83at modeled futures costs | ES/10proxy, historical fill/fill-in assumptions and fractional sizing; not native personal or Delgado replication |
| [S03v2 completed placement](s03_v2.md) |50Kfunded ADD1year1−$348.5; full-personal equal-DD gain−$484 | Different NQ stop/version and historical portfolio; does not reject every SPY rule |
| [S03 independent reconstruction review](s03_noisearea_independent_review.md) | Declared implementation consistency passed; source/tick/data/causal timing concerns remain | Different reconstruction; account tests there blocked, not the completed S03v2study |
| [Revised15-minute noise band](noise15_20261103.md) | Both fixed definitions fail design advancement | Different source; no rescue search authorized |

The old ES proxy's code fills missing minute prices and includes signal-close fill variants. Its saved Sharpe
is contextual evidence, not a newly audited executable result. No import/run of that script occurred. Keep
prior studies separate by rule, version, cost model and actual admitted sample rather than pooling their metrics.

| Home | Verdict for this upload |
|---|---|
| Personal | No placement earned; exact SPY test NEEDS DATA AND SPECIFICATION |
|50K evaluation | No placement; SPY ETF is not the account's futures instrument; no validated native port |
|150K evaluation | No placement; same instrument/mapping limit; no simulated result inferred from50K |
|50K funded | No placement; exact candidate untested; related NQ placement disappoints |
|150K funded | No placement; exact candidate untested; no payout/risk improvement established |

No new BASE/ADD/REPLACE/EMPTY, long/short/year return table, bootstrap, placebo or account simulation was
eligible after the input gate. Missing inputs do not prove loss; related failures are retained rather than renamed.
The70trial series are needed to reproduce the author's statistical audit, not as an extra requirement for any
independent strategy test. A valid free minute panel plus frozen explicit execution/cost interpretations could
support a new independent replay without proprietary author code. No such native panel was admitted here.
Only genuine new native data/package evidence reopens admission. Free-source findings and smallest next checks
are retained in[D55](../DATA_NEEDED.md). No synthetic trading planner, schedule, live or allocation change.

Execution/research lessons saved in[EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md): match VWAP
price basis and entry gate, cap actual exposure after every overlay, preserve engine/search history and real
warmup dates, and distinguish replication from new validation. No measured execution savings reproduced.

Tell Claude: review `agents/codex/results/delgado_7323419_review.md`; historical SPY replication supports the
family, recent performance/transfer are weak, exact personal replay is data-blocked and no new code/allocation.
