# Heavy-night fade as an ONB loss buffer: TEST

Summary: Re-evaluate the frozen T leg of T_ONESIDE, not its OS momentum leg,
against the seven-piece evaluation book in the joint-loss audit. It may bank
opening reversal profits before ONB's main risk window. Prior standalone and
MultiCharts evidence justifies a bounded re-bench, not an assumption it hedges.

Sources: `checks/candidates/t_oneside/REVIEW.md`, `spec.md`,
`T_ONESIDE_v2.txt`, author's uploaded research note; `analysis/t_oneside_test.py`;
`analysis/active_scan_eval.py`; `agents/codex/results/book_joint_losses.md`.
Source/book snapshot: a5aeffec / joint-loss report 51d0ef8b. No new paper review.
Earlier trials: author settings and 2026-10-24 cells, stops, sizing and benches
remain counted. This is an existing frozen strategy, not a newly discovered edge.

## 1. Who trades and why?

Hypothesis: unusually heavy overnight positioning meets the deeper US cash-open
liquidity, allowing inventory reduction against the overnight direction. The
source's observed heavy-vs-quiet volume contrast supports an empirical opening
reversal, not a demonstrated forced flow. No mandated dollar amount is known.

## 2. Direction, magnitude, timing

Fade the known overnight return only if its volume exceeds 1.4 times the median
of the previous 20 valid nights. Night ends at the bar closing 08:29 CT;
decision at that close, market fill next bar open (08:29 wall clock). Information
is known at submission, but zero-latency filling at that exact open is idealized.
Predeclare a one-minute delayed fill stress; exit fixed at 08:44 wall clock,
stop 0.4 times lagged 20-session RTH range. No true flow-dollar estimate is
possible from unsigned bar volume. Do not invent one.

## 3. Transmission

Trade the NQ signal on MNQ, a direct same-index contract. No cross-market proxy
or fixed short bias; both overnight up and down moves qualify.

## 4. Inputs

Owned NQ day/overnight one-minute OHLCV, 2017-05 to 2026-11; past-only night
volume medians and 20-session range. Grid validated against raw CSV closes in
the preceding audit. Volume field is an imperfect activity proxy; old MC trade
comparisons establish substantial, not perfect, signal parity. Existing MC
report and frozen source enable another parity check, without fetching data.
Baseline: same time/exit fading every valid night; random side on heavy nights.
Volume adds information beyond the direction of the price move.

## 5. Costs and timing fit

Earlier T-leg mean was $239/NQ net at $17.25 costs; this is prior evidence,
not a new result. Test $22.75/NQ equivalent ($2.275 round trip per MNQ, including
one tick per fill and $1.275 commission/fees). Extra $0.55/micro matches the JF
fee convention; actual broker fees remain an assumption. Candidate closes
before most ONB trades, so possible benefit is a realized buffer, not a
continuously opposing position. Test all signals, never only ONB losing dates.

## 6. Power

Prior full-period T leg had 363 trades, roughly 200 expected in 2018-22.
With assumed SD $1,000/NQ, a $141 net mean is needed for t=2 at n=200.
Earlier design mean $197 makes a cheap test plausible. Prior 2023+ results are
already seen and cannot be called a clean holdout. Side-specific samples are
smaller; report their uncertainty, do not pick a side using recent outcomes.

## 7. Duplicates and falsifiers

Earlier evaluation gains were small on old rosters. The 11/12 active scan's
`T_FADE` label loads the full `python_trades_stop.csv` (T + OS); it does not
isolate T. New question: frozen fade-only leg and current seven-piece book,
with shared-loss and early-offset attribution. No threshold optimization.
Reject if standalone design/placebo gates fail, if ONB-loss offsets are absent,
or if paired account comparisons give no robust improvement.

## 8. Failure and diversification

- Marketable entries provide liquidity-taking, not passive maker income.
- Fails when overnight news continues through the open; concentrated macro
  releases at 08:30 can produce slippage, gaps and clustered losses.
- Could lose with JF or on strong continuation mornings. Offset to ONB losses
  is a prediction to test; an early mean-reversion label is not proof.
- Stop active on entry bar; reject missing entry/exit bars rather than assume
  a fill. Gap-through stops fill at the worse opening price.
- Fixed 1 MNQ primary, 2 MNQ size sensitivity. No overnight holds, no netting
  across separate accounts. A candidate loss can reduce room before ONB starts.

Decision: **TEST**, using a committed plan before new returns. This is a frozen
candidate re-bench; past-only inputs and independent eligibility remain required.
