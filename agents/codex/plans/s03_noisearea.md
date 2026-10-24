# S03 Noise Area v2: frozen OHLC reconstruction, 2026-10-24

Summary: Test the supplied fixed protective-stop claim and current-plan contribution on owned NQ minute data.
Primary V2 and three fixed controls/stresses are specified now; no optimizing the author's selected parameters.
Commit before any new market-data signals, returns or account calculations; synthetic fixtures are allowed.
Run 2018-22 first, then frozen seen-history replication and the account stages only after their gates pass.
No trading, plan, ranking, broker/VPS settings or code deployment changes.

## Sources and scope

Evidence `agents/codex/evidence/s03_noisearea.md` is TEST for reconstruction, not exact source validation.
HTML SHA256 `05a176b0c4f6804d48d427ad484175076d125a61b62122736c34c6797c0d2b52`.
Codex context `541d1117683294cc3949d13e7260272eba5a20b8`; Claude current-plan context
`e4399c8e235ee26674c88a439d4c9926b5731af4`; builder blob `22c4c28bd39c140ec2a19a60e6296c9019c7de43`;
standing workflow blob `11d532bd92264f6ecb00774ffc34e5ac2ab995e7`. Preserve concurrent work on codex/work.
The source supplies a chosen StopSigma0.4, at least12 previously examined values and selected2017-2026 results.
No fresh holdout is claimed. Missing actual PL/s03_engine/OFB file/tick tape is disclosed. Bounded assumptions
below are fixed before returns. Existing caches/helpers are reused; no build_lab or broad research scans.

## Fixed rule and reconstruction assumptions

Both sides, one position, one-NQ geometry. Times below Central (ET is one hour later). Use calendar-normal
cash sessions only; skip preknown cash holidays, existing early-close dates and2018-12-05/2025-01-09 mourning.
Calendar helper `analysis/codex_s03_calendar.py` uses repository early-close logic and deterministic cash dates.
Never decide whether TODAY was tradable by inspecting its later price completeness or P&L.

Primary RTH starts at the open of the08:31 end-stamped minute (actual08:30 cash open); alternate anchor below
uses08:30 bar inclusive. End15:00. For each check, sigma is mean(abs(close_at_same_minute/past_cash_open-1))
over the PREVIOUS14 completed FULL normal sessions. A past session qualifies only after its close, with all
anchor-through15:00 native OHLCV observed; current day is never included. No future fills/forward fill in sigma.
Previous cash close means the immediately preceding cash session, including legitimate early close12:00CT;
holidays/weekends do not update it. Missing expected prior endpoint leaves prior close unavailable.

Upper=max(today_open,prior_cash_close)*(1+sigma); lower=min(...)*(1-sigma). VWAP is cumulative one-minute
typical price(H+L+C)/3 times TOTAL volume from the selected anchor, no up-volume substitution. Nonpositive
cumulative volume or invalid features block a new signal. Long C>upper and C>VWAP; short C<lower and C<VWAP.
Decision closes09:00,09:30,...14:30 inclusive. Opposite signal reverses; same direction adds nothing. At the
same checks, long C<max(upper,VWAP) exits, short C>min(lower,VWAP) exits. Market fills next observed native
minute open. One position at a time; no artificial daily attempt cap.

Entry stop distance=0.4*raw_sigma_at_signal*signal_close, not an ATR or statistical standard deviation.
Freeze that distance for the trade; anchor at raw entry price. Round stop PRICE toward entry: long ceil to
0.25, short floor. Prearmed on fill minute. Scan shared `grid._walk` OHLC ordering, stop gaps at actual open.
If gap stop and pending exit share the opening price, attribute stop first, cancel redundant close, retain
an independently scheduled opposite reversal once. Reversal closes and new entries pay their own trade costs.

At15:00 observed close schedule next-observed-minute market flat, normally15:01. If15:00 bar is absent, the
first subsequent actual native close>=15:00 may schedule catch-up; do not create a missing bar/price. Pending
markets wait for the next observed open within the same date up to15:59, with delays audited. Missing endpoint
holdings are censored and listed, never marked into a last-price fictitious trade. Monitor stops through the
actual held interval. Unknown held-minute OHLC, illegal carry, unmatched orders or censored positions block
account scoring; closed ledgers alone are not proof of complete paths. Do not exclude a gap day in advance.

Our standard cost is$7.25/NQ RT plus1 adverse tick on EACH market/stop fill ($17.25 ordinary round trip).
No target. E2 uses3 ticks each fill, same raw stops/entries. Slipped entry/exit and net are final; set slips0
for account helper protection, never apply trade_net twice. Account MNQ preserves price geometry at$2/point,
reprices exact trades to fee$1.04 RT and stress$1.24, not one fee per nonzero day. Source Lucid terms are not used.

## At most four fixed return profiles

| ID | Rule | Purpose |
|---|---|---|
| V2 | StopSigma0.4, actual cash-open anchor08:31, current costs | Primary, chosen before returns |
| V1 | V2 with StopSigma0 only | Matched no-protective-stop control; full re-entry replay |
| C2 | V2 with08:30-bar-inclusive open/VWAP/noise history | Clock/anchor uncertainty, never selectable |
| E2 | V2 with3 ticks per market/stop fill | Execution stress, never selectable |

No sweep, alternate stop, selected long-only/short-only, weekday deletion, alternate size or re-fit. Long/short
statistics are slices of the same full replay; they do not become new independently selected portfolios.
Tail concentration and historical winner-removal diagnostics are descriptions, never candidate rules.

## Stage1:2018-22 design and cheap screen

First run all four streams for2018-22 ONLY. Reuse December2017 cache history where available; otherwise report
warm-up loss. No2017 author parity target. Save trades/orders, raw/slipped prices, sigma/stop/clock, calendar
and missing-minute audits. Daily MTM must reconcile to net trades including fees and roll/gap changes.

Design gate for fixed V2: >=100 completed trades; net>0; trade t>=2 (mean/sampleSD*sqrt(n)); >=3/5 positive
calendar years; E2 net>0; synthetic and independent replay/accounting checks clear; no material censoring.
If any fail, STOP with REJECT for this trial: no recent returns, Monte Carlo or account simulation.
Otherwise save an explicit passing gate before opening Stage2. Do not select a different profile.

Assess the protective stop by total net, Sharpe and maxDD against V1 on identical dates. Match common entry
decision/side and identify extra/missing re-entries. This is an EXIT intervention, not a simple trade filter;
do not present removal of losses or higher mean alone as causal proof. Daily paired20-session bootstrap,
3,000 draws, seed20261024 gives90% net-change/Sharpe/DD intervals. Support "improves" only if maxDD lower and
net higher, with positive lower90% net-change bound OR positive lower90% Sharpe-change bound; otherwise state
the risk/return trade-off. Account gains, rather than this standalone comparison, decide a placement.

Random side/time controls use100 fixed seeds each, unchanged brackets/trailing/flatten/cost and stateful
re-entry execution. Side control randomizes raw entry signal directions at their scheduled check bars.
Time control permutes raw proposed entry signals/directions among that date's eligible check bars, keeping
proposed count/date; actual filled count can differ due to occupancy and is reported. No future-occupancy
feasibility selection or claim of matched actual counts. Same-calendar active-date conditioning is disclosed.
No parameter/clock/size choice may use these controls. Root RNG20261024; side +10000, time +20000.

## Stage2: frozen recent replication

After saved design PASS run the SAME four profiles once from2023 to existing cache end2026-10-09. Seen2023+
is historical replication; also describe the predeclared post-source extension2026-07-08 onward separately,
without calling it a clean independent holdout. No new rule selected from either interval. Repeat standard
whole/long/short metrics, year tables, matchedV1comparison and placebos. Bootstrap recent daily20-day blocks
3,000 draws, seed20261024, including zero dates; report net, PF, Sharpe, drawdown intervals and permutations.
Describe source tail risk: best1/10/25 trades' net share, year/side and largest losses, no deletions to select
a rule. Latest ranked-item count+this idea and conservative+four profiles for multiple-testing/DSR.

## Stage3: account gates and all destinations

Additional account gate: V2 recent net>0, all native/no-trade dates covered, zero unknown held paths, no illegal
carry/censoring, verified daily/trade/fee reconciliation. If paths fail, report specific dates/rows and STOP
account simulations, not drop/impute them. Independent review with open source/tick concerns prevents promotion,
but a disclosed, data-complete OHLC candidate can still receive research account comparisons.

Refresh current sources at Claude e4399c8, hash inputs and verify canonical baseline parity on SAME saved
histories/paths before any candidate claim. Current50K funded10legs includes ES MOC2MES and RS longs1MNQ.
150K follows current documented quantities: base50K legs×1.5 before actual cushion-floor, RS both1 replaces
RS longs, plus DualThrustv4 at2MNQ.50K evaluation VB8/ONB ADX30risk1100/Bridge2/EOSrisk500;150K evaluation
VB20/ONB risk2750/Bridge5/EOSrisk1250, recomputing risk quantities rather than multiplying floored quantities.

For EACH of50K/150K evaluation/funded, only BASE; ADD_V2 at1MNQ(50K)/2MNQ(150K); EMPTY_VB; REPLACE_VB.
Replacement uses the original VB slot quantities and single-print flags: funded50K normal2/flag1;150K
normal3/flag1.5 BEFORE canonical cushion/floor; evaluation8/20. Do not choose a better quantity afterward.
Funded paired1,000 histories,20-day blocks,H500 with year1/2 checkpoints, both2018+ and2023+ pools; use current
canonical histories/seeds1-4×250 where that is the established engine, save exact indices. Evaluation uses
the existing21-trading-day chronological full-calendar model. Fees1.04 and1.24 share identical histories.
Report payouts, breaches, time to six payouts, pass rate/speed, concurrent exposure and paired90%/95% CIs.
Memory guard<4GB; stream/chunk histories, reuse tensors and never rebuild research grids.

Personal: use CURRENT17-piece portfolio and current11 documented ladder rows: A/B/C/D;13 withoutDT;14 without
Kusho/S47;Core16(noS30);Full17;Core×2+S30×1;Core×4+S30×1;Core×10+S30×3. Fixed ADD_V2 equals the core micro
multiplier(1 for first8 rows, then2/4/10); replacement equals existing VB unit. A/B have no VB, so EMPTY=BASE
and replacement is N/A, never invent that slot. Compare BASE/ADD/EMPTY/REPLACE at both fixed fees; repricing
uses exact trade counts. Reuse corrected S30 daily/trade reconciliation; mark Twin/Kusho/S30 overnight paths
causally where source ledgers support it. Record canonical-versus-corrected accounting deltas, not rule changes.
If exact baseline accounting cannot be reproduced, report the limiting condition rather than a fabricated gain.
Paired1,000 circular20-day,H252 bootstraps seed20261024, both2018+ and2023+ pools, same indices across configs.
Report annual return, Sharpe, P95DD, return/P95DD, capital needed=P95DD/0.20, and covariance/joint loss timing.

Meaningful Apex improvement: positive lower90% paired CI for funded year1 OR year2 payout (or evaluation pass),
no year2 payout deterioration, breach rise>1pp or median six-payout slowdown>5days; replacement must also beat
EMPTY. For personal: positive lower90% annual-return gain AND point return/P95DD no lower than baseline,
or lower90% CI of paired per-history maxDD reduction>0 with mean paired annual-return change>=0; replacement
must also beat EMPTY. Mixed/noisy
effects are trade-offs/no demonstrated gain, not selectable winners. No account/live allocation changes.

## Deliverables, trial count and stop

Whole and separate long/short: count,win,net/trade,total,t,Sharpe,Sortino,PF,Calmar,Ulcer,maxDD; byyear and periods;
recent bootstrap/permutation; stop-off comparisons, execution costs, nulls, all4profiles including failures,
exact source/cache hashes, source-vs-reconstruction differences and independent checker. Count one idea/four
return profiles, no cleanholdout claim; source's at least12 prior stop variants remain a selection warning.
No above-C/live recommendation without the applicable multiple-testing, replication, clean checks, MC source
confirmation and current account-gain requirements. Author's selected sweep/MonteCarlo is not validation here.

Report `agents/codex/results/s03_noisearea.md`, Summary<=5lines. Scripts `analysis/codex_s03_*.py`, outputs
`analysis/outputs/codex_s03_noisearea/`. Publish only this task's files on codex/work, preserving others.
If gates fail, give a concrete result/limiting condition for every destination and move on; no rescue search.
