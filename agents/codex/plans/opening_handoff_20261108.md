# Opening handoff: frozen two-candidate combination screen

Summary: Test continuation and reversal confirmation combinations against the same-window opening-drive parent.
Five cases total: parent, two candidates, and each candidate delayed one minute. No optimization.
2018–22 first; only a passing, frozen candidate earns already-seen 2023–2026-10-09 replication.
No native up-tick volume reconstruction or full-history fitted ML score. No plan/live change.

## Exact information, execution and universe

Source: evidence `agents/codex/evidence/opening_handoff_20261108.md`; preceding ingredient study at `6ba29cd`.
NQ 1-minute bars, Chicago close stamps. 09:00 close is the decision; 09:01-labelled OPEN is executable next
bar (09:00 civil CT), delayed OPEN09:02 (09:01 civil). No feature from the future entry bar or later.

night_direction = sign(C08:29 − first observed bar OPEN in the interval from previous calendar date17:01
through current08:29), with a finite ending anchor and >=30 observed night bars, matching T's first-observed
reopen convention. ONB range high/low uses previous23:01 through current08:30. Cash-open = O08:31;
location = (cash_open − overnight_low)/(overnight_high − overnight_low).
bias = +1 at location>=2/3, −1 at<=1/3, else0. First15-minute opening range = H/L08:31–08:45.
drive = sign(C09:00 − O08:31). breakout confirmation = C09:00 above first15 high for long, below low for short,
strict inequality. ADX = source continuous Wilder14 on15-minute bars, at the09:00 completed bar, gate >30.
All prices/indicators available by09:00; no model fitting or volume series in the rule.

Common research universe: weekdays2018–22 (2017 for warm-up), observed first-night/end anchors/positive range,
>=30 finite night closes, all first30 cash bars, finite source ADX, >=20 preceding RTH sessions, nonzero drive.
As a causal conservative seam precaution, skip dates5–21 of March/June/September/December. It is a declared
calendar restriction, not a retrospectively identified largest roll-gap adjustment. Residual seam risk remains.
Require observed OHLC09:01 through scheduled14:59 OPEN (11:31 on source early-close days); delayed entry uses
the same admitted calendar. Missing future execution-path rejection is research data admission, not live prediction.
Use all eligible events regardless of portfolio occupancy. Save every exclusion/reason before pricing.

## Five fixed economic cases

1. **Parent:** all eligible nonzero first30-minute drives, follow drive at09:01.
2. **Continuation:** Parent when drive == night_direction == ONB bias, ADX>30 and breakout confirmation.
3. **Reversal:** Parent when drive == −night_direction, ONB bias == night_direction, ADX>30 and breakout confirmation.
   This combines T's fade direction with ONB location/confirmation and FC's opening-drive entry/exits.
4. **Continuation_delay1m:** same decision/date/side, enter09:02; risk anchored to actual filled entry.
5. **Reversal_delay1m:** same delay stress for Reversal. Neither delay case can become the selected rule.

Common exact FCv2 exit replica:100-point entry-bar protective stop;150-point trailing stop posted next bar,
through-close raised-stop market fallback; break-even DISABLED (BER=0 guarded by BER>0), no target.
Trail high/low initializes at decision close, source update chronology unchanged. Flatten signal14:58 -> next
observed bar OPEN14:59; source early-close11:30 ->11:31. Full observed path prevents accidental halt carry.
No source trade-list/event outcomes used to admit candidates. NQ$20/point, $7.25 commission +1tick per fill;
nativeMNQ$2/point, $1.25commission +1tick per fill. Also report another1tick per leg on the same fixed trades;
it changes costs only, not stop path. Slippage is a cash bridge, source raw-price order levels unchanged.

## Before returns

Verify exact committed plan/script/dependency SHA, raw Git-blobs and configured Python versions. Reuse source
in-memory grid loader and independent FCv2 exit function; no new full-grid cache. Synthetic cases cover long/
short entry stops, adverse gaps, next-bar trail, through-close fallback, no-BE, normal/early flatten, one-minute
entry delay and native costs. Save count/power receipt and features/exclusions BEFORE market trade replay.
Both candidates must be pure date subsets with identical common-date side/entry/exit/net versus Parent.
Stop on failed implementation/cash parity, with no rescue economic parameters. Never revise a case after returns.

## Design gates / selection / stop

Each candidate must meet ALL on2018–22:
- >=30 trades, positive gross/net, trade t>=2, PF>=1.2, >=3 profitable years;
- total net > Parent, daily realized DD<=Parent and Sharpe>=Parent;
- pure nested filter; removed Parent trades negative total and t<=−1;
- 1000 within-year equal-count random subsets: profit exceedance<=5% AND DD-no-worse share<=5%;
- paired20-session moving-block bootstrap1000 seed20261108: candidate-minus-Parent annual P5>0;
- delayed counterpart net>0 and extra1tick/leg cost net>0.

Judge total profit, not only mean or ratios. These deliberately demand evidence the added filters improve the
parent; risk concentration alone is recorded but does not bypass the registered filter gates. A positive
standalone strategy that fails is WATCH/REJECT for this proposed combination, not a recommendation to trade it.
If neither passes, stop recent/placebo/account/MultiCharts and save completed negative design results.
If both pass, select higher design Calmar, then higher net, then Continuation on an exact tie. Freeze selection
in a committed design receipt before reading recent minute data. No post-result candidate/clock/threshold rescue.

## Earned later gates only

Selected original plus Parent and its fixed delay on2023-01-01–2026-10-09 once; same gates with>=20 trades,
>=half available years positive. Already-seen history is replication. Full-trade t must also clear
metrics.t_threshold(max(500,current TIER items+5)), and DSR>=.95; prior ingredient looks remain disclosed.
Same-entry random-side control (1000, actually replay both directions with same exits) must be beaten at95th
percentile; this is a control, not a selectable rule. Use standard whole/long/short/year results,5000-run10-day
recent bootstrap, permutation and nativeMNQ Monte Carlo. No claimed independent economic verification.
After earned independent/native parity review, actual current-book BASE/ADD/REPLACE/EMPTY at1MNQ first for
eval/funded50K/150K and personal, replacing ONB or FC/T according to measured overlap (read then-current books).
Report payout/risk/timing and chronological joint exposure before suggesting any place. A failed stage stops
its dependent stages. No account benefit inferred from standalone net, DD or apparent low correlation.

Run identity/code/dependency versions, counts, exclusions, gross-cost-native cash bridge and all5cases saved.
Do not modify trading plans, TIER, live/VPS/broker/API keys, other branches, scout history/schedules, or buy data.
User handoff includes direct results plus the report for Claude; push only codex/work.

## Adapter amendment after aborted run99d6209, before corrected market replay

The first attempt required an exact17:01 bar, contrary to T source's first-observed reopening bar. The
no-return receipt admitted35sessions (Continuation3/Reversal0), rejecting1013 dates for missing that minute.
The run priced Parent35 and Continuation3 plus its3 delay trades in memory, then failed normalizing an empty
Reversal dataframe; no candidate economic summary was printed or inspected. These partial looks are retained
as prior execution history, not erased or claimed zero. This is a source-adapter/data-universe correction;
its economic rule, exits, thresholds, five case definitions and gates are unchanged. Exact-night admission
and traceback remain in the aborted_exact_anchor directory. Empty numeric columns now retain float dtype.

Source fidelity changes the research universe materially, so this amendment explicitly precedes the corrected
returns. It is not a newly optimized17:02 anchor or a change selected from P&L. No other first-bar cutoff is
tested. The initial17:01 protocol is abandoned for missing-data/source mismatch, not economic performance.

## Final reporting denominator supplement (no rule/selection change)

Original gates used research-admitted dates. Preserve them; after the failed gate, restore all source trading
dates from features plus exclusions when reporting annualized ratios from the frozen saved cash ledgers.
Skipped roll-calendar/data dates carry zero cash, rather than shortening elapsed time. No new return replay,
threshold, classification or gate reopening; original conditional metrics/intervals remain auditable.
