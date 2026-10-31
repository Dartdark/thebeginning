# Swing Target NQ: frozen uploaded-code replication and placement screen

Date: 2026-10-25. Commit before real-data returns. Evidence: `../evidence/swing_target.md`.
User wants a backtest and potential place in 50K/150K evaluation/funded and personal plans, not just source review.
Unknown chart template: user selected a clearly labeled full-CME-session proxy. Both BE/no-BE explicitly authorized.

## Fixed models and chronology

Two economic models only: **CODE** literal uploaded defaults, and **CODE_BE** identical with a causal entry-price stop
after favorable excursion of .30 × the same prior average range. CODE_BE isolates the missing BE rule; it does not silently
repair the other source/prose discrepancies. No side/volatility/regime/timing optimization, no proposed rescue filters.
Source header and prose claims have been seen; author trial count is unknown. Previously seen 2023+ is historical validation.

Initialize stored history from cached data before 2018. Run 2018–22 design summaries before either model's 2023+ replay.
Both models are declared source versions, not selected in-sample winners; run each once on 2023–2026-10-09 after saving design.
Report combined/long/short, every year, design/validation/all, and author's February2018–July2026 slice without using it to select.
Freeze .35 target / .70 stop ×20 prior stored RTH ranges, lookback2, one trade/day. Prior session state follows the uploaded
exact 08:31 reset /15:00 storage. Inclusive opening boundaries; strict >/< early invalidation through08:45.
Orders placed at08:45 close become active next available bar (normally08:46 close-stamp); inclusive14:29 submission can fill
14:30-labeled bar. 14:59 market exit fills next available bar open (normally15:00-labeled bar). Labels are not wall-time opens.
Protective built-in target/stop are active on entry bar. Source does not implement holiday handling: retain and inventory its
missing-storage, deferred-order and overnight consequences rather than fix them after seeing returns. No live/source-file edits.

Stop entries gap at open if worse. Both entry orders OCO after first crossing. Walk each minute chronologically using the repo's
nearer-extreme OHLC path convention; only post-entry path contributes to target/stop and MAE. Targets need1point through;
stops/BE at trigger or worse gap. Track cross-date exits, missing held minutes and minute-phase adverse endpoints.
The shared market-entry engine cannot model paired stop entry/causal BE, so extend it in a new `codex_swing_engine.py` and say so.
Fixed execution diagnostics, not selectable models: opposite first-extreme path; extra adverse tick; author's $1/MNQ zero-slippage
cost comparison. No favorable level fills through gaps. If path/coverage failure makes replication non-identifiable, say so.

## Metrics, nulls and cheap gate

Costs primary: $7.25 RT/NQ plus one tick per market/stop fill. Native MNQ primary $1.24 RT, sensitivity$1.04, plus .50 per market/stop
fill. Entry stop always pays slippage; target exit no extra slip. Report gross, costs, net, full standard repo metrics, t, DSR and
t_threshold(current ranked items+2), plus source exit counts, win/loss mix, trade/EOD DD and open MAE. No scaled-mini fees for micros.
5,000 ten-session block bootstraps and5,000 permutations on validation/full and both sides; seed20261025. Initial zero counts in DD.
Use500 deterministic random-time and500 random-side placebos on the same eligible trade days, with same bracket/BE/time exits.
Random-time entries draw a minute from08:46..14:30, side from actual trade; random-side keeps actual entry timing and flips randomly.
These are matched-exit nulls, not realizable alternate stop-entry strategies, and do not establish the early-time filter's incremental edge.
No original unfiltered-v1 test is added. A new filtering hypothesis would need its own preregistration and random-drop controls.

Cheap gross/net screen: model net>0 in both eras, designPF>=1.20, full trade t>=2 and validation positive after extra tick.
No passing model => stop before expensive accounts and record a limiting condition for every requested plan.
A source version with an open position crossing the Apex flat deadline/session closure cannot be placed on Apex as supplied;
do not remove those trades or quietly repair it. Report account incompatibility, while personal comparison may still be possible.
Strict promotion still requires t>=multiple-testing bar or DSR>=.95, execution/parity checks, independent review and forward evidence.

## Conditional portfolio/account contrasts

Pin latest fetched Claude plan snapshot (currently62e82a0); preserve existing work. Refresh current funded OT changes and current
personal18-leg roster rather than calling old14-leg adapters current. Use reviewed repo engines, extended only in new allowed files.
For each cheap-pass, operationally eligible model, fixed contrasts: current plan, +candidate, replace VB with candidate, VB empty.
Candidate fixed size:50K eval1MNQ,150K eval2MNQ,50K funded1MNQ,150K funded1MNQ. No sizing optimization.
Use paired1,000-path ten-session block bootstraps,252/504-session funded horizons; evaluation existing21-session horizon.
Keep current plan's account risk caps/payouts; do not infer150K from50K. Native fees apply consistently to baseline and candidate.
Personal: current starter laddersA–D and full18-leg book, with candidate at the common leg scale, same four contrasts wherever VB exists.
Report dollar/percentage drawdowns, incremental return and common losses, including equity-index concentration; common source coverage
is explicit. If model/source/baseline data or engine chronology prevents a valid comparison, give that concrete limitation for each plan.
Preserve published OT baseline approximation as a diagnostic only if needed; no material account-benefit claim from invented simultaneous
night/day adverse exposure. Missing source dates are not no-signal zeros.
No ranking, trading allocation, live platform/VPS/broker/API changes. User explicitly requested adding the pending VB rerun to TODO.md;
that narrow to-do edit is authorized despite normal builder file boundaries.

## Deliverables

Preserve uploaded code under `agents/codex/inputs/swing_target/`, scripts `analysis/codex_swing_*.py`, outputs
`analysis/outputs/codex_swing_target/`, concise `agents/codex/results/swing_target.md` with Summary<=5lines and per-plan verdict.
Commit and push only codex/work; no PR#2 review/merge or other-agent branch push. No cache rebuild or package installation.
