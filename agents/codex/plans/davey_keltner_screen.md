# Davey-inspired ES momentum/Keltner: frozen 2018–22 reconstruction screen

This plan is committed BEFORE the first return replay. Evidence:
`agents/codex/evidence/davey_keltner.md` (TEST, user-requested bounded diagnostic).
User authorizes discretionary completion of missing settings, not a search for the best settings.
Source: preserved screenshot transcription and video transcript in `agents/codex/inputs/davey_keltner/`.
This is our reconstruction, not verification of Davey's unknown inputs or reported equity curve.

## Mechanism and fixed assumptions

Trend resumption after a short pullback. No forced participant or external-flow observation is established.
Trade ES, fixed **one full contract**. **30-minute bars, MomLengthL=20, MomLengthS=20, Threshold=50**.
Twenty bars is ten hours of observed daytime trading; channel length five is 2.5 hours. Fifty is the natural
midpoint; identical momentum lengths avoid an invented side-specific fit. No compounding, equity sizing,
leverage adjustment, pyramiding, discretionary weekday filter or portfolio-flat selection.

Use RTH minutes after 08:30 through 15:00 CT. Bars close at 09:00, 09:30, …15:00. A full 30-minute bar
requires all its underlying minute observations. Incomplete chart bars provide no decision and are not
forward-filled; indicators use the completed observed bars, carrying history across RTH sessions. No night
bars contribute. Early-close dates use `replica.is_early_close`, end RTH at 11:30 CT. This is a conservative
calendar convention, not a claim about the source workspace's session.

Keltner center = SMA(C,5), bands center ±0.5×SMA(TrueRange,5). TrueRange uses the prior observed RTH close;
ATR(15) = SMA(TrueRange,15). These explicitly fixed EasyLanguage-style definitions are not an official engine
parity claim. No Wilder smoothing or modern EMA20 Keltner substitution. K=100×(C−lower)/(upper−lower),
zero if equal; not clipped to [0,100]. At threshold 50, K<50 / >50 equals C<SMA5 / >SMA5 when ATR>0:
channel width cancels. Require positive finite ATR15 and 20 prior observed bars before a decision.

Long when C>C[20] and K<50. Short when C<C[20] and K>50. Long exit K>50; short exit K<50. Equalities do
nothing. Decisions use the completed chart bar; market orders execute at the next minute's open. One position
at a time; ignore same-direction entries while held. A contrary entry closes and reverses at that open.
An intrabar stop permits a new signal only at a subsequent completed-bar decision. A position still held at
a decision cannot create a fresh same-direction entry because its stop happens to gap at the following open.

## Stops, scheduled exits and fill assumptions

At entry, stop 4×ATR15 below the long reference entry / 1×ATR15 above the short entry. Update the stop from
the same entry and latest completed ATR15 at each subsequent decision. It may widen: no entry-freeze or
monotone trailing modification. Tick-round stop prices to nearest .25 with NumPy rounding.
Provide protection from the first entry minute, an explicit executable adaptation of the screenshot's
conditional `MarketPosition` stop calls. Exact source entry-bar behavior is unverified.

Extend repository `grid._walk` for moving stops and next-open indicator/reversal exits. There is no target.
Handle opening gaps explicitly before traversing the minute; fill a breached carried stop at the observed open,
not its stale stop level. No intraminute order priority can manufacture a better fill. Costs are deducted from
raw-open/stop reference prices, following repo convention; stop anchoring does not shift by charged slippage.

Scheduled market flatten is the OPEN of the minute stamped **15:00** (actual14:59 CT), early **11:30**
(actual11:29). The last possible normal decision is14:30; early11:00. No new trade at the flatten boundary.
No overnight carry. The final minute contributes no future high/low to an exit filled at its open. Source has
no such time exit; this openly tests the intraday adaptation suitable for later Apex evaluation.

Missing activation minute cancels a NEW entry, never queues it. A held indicator exit waits for the first
observed minute in its following chart interval; stop-gap risk remains. Missing scheduled exit data waits
for the first same-day observed open and records a late-flat error; any such event fails the data gate.
If none exists that day stop the run rather than inventing a fill. Never choose an earlier exit after discovering
that later data are missing. Record skipped partial bars/missing opportunities; no trade-outcome-based deletion.

## Data boundary, power and two variants

Use only ES2017 (warm-up) and ES2018–2022 CSVs with `Grid24`; no shared-cache construction or 2023+ reads.
Validate observed OHLC, duplicates, close stamps and source hashes. Signals from2017 do not produce returns.
Read no strategy P&L in the eligibility audit. The audit counts5,311 signal opportunities, not filled trades;
1,297 weekday dates and15,172 eligible decisions. Some holidays have no RTH; no signal is fabricated.

Assumed n500 and trade SD$300–$600 implies net mean$27–$54 (gross$57–$84 at baseline costs) for naive t2.
At100 trades the gross hurdle is$90–$150. Actual dependence can raise these hurdles. Report measured support,
trade SD, daily t and10-session-block uncertainty, not the opportunity count as independent observations.

1. **Primary:** $5 ES round-trip commission plus one tick each market/stop fill; total **$30/trade**.
2. **Execution stress:** same trades and prices, two adverse ticks each fill; **$55/trade**.

Also report primary at double total cost **$60/trade** as one analytic cost rescore, not another path/rule.
Count two market/execution variants, one additional analytic rescore; no parameter trials hidden by the word
"stress". Do not run other timeframes, instruments, momentum lengths, thresholds or side-only rescues.

## Pass/fail and stop rule

Require ALL for the combined primary strategy: >=100 completed trades; net per-trade t>=2; net daily t>=2;
gross mean >=$45 (1.5×baseline costs); >=3 positive design calendar years; positive total at$55 and$60 costs;
conditional random-side p<=.05; all causal/execution checks pass; zero late-flat errors. Long/short results
are diagnostics, not grounds to change the frozen combined strategy.

Any failed requirement means **REJECT this reconstruction and stop**: no optimization,2023+, micro-sizing,
funded bench or live code. Passing means at most **WATCH pending independent implementation review**;
do not automatically open2023+. Source development already included most2018–22, so neither this cheap
screen nor selected video claims establish independent validation. Future historical replication must be
labeled already-seen history; source/parameter changes after results require a new counted trial.
Promotion aboveC would still need the repo multiple-testing bar/DSR or an eligible documented exception,
clean replication/placebos, independent checking and account-level evidence. No strong-mechanism exception
is assumed merely because we chose defaults before seeing their results.

## Controls, verification and reporting

Before return output check: exact next-open fill, long/short entry-minute protection, carried gap stop,
moving-stop widening only after the decision, indicator next-open exit, reversal/no pyramiding, canceled
missing activation, early scheduled flatten, historical-prefix feature invariance and $30/$55 ES arithmetic.

After primary replay run1,000 seed530251 conditional random-side controls: randomize direction at all original
nonzero signal-opportunity decisions and replay the same asymmetric stops, Keltner exits, session, costs and
single-position blocking. Each side retains its own exit condition. These controls can change trade count;
they assess direction conditional on the original opportunity clock, not independent entry-time skill. No
random entry-time optimization or placebo-selected rule. A poor result cannot be rescued by the controls.

Use `metrics.perf` (with initial zero for drawdown) and `resampling.bootstrap`/`permutation`:2,000 runs,
10-session blocks, seed530251, combined/long/short. Daily P&L includes all observed design trading dates,
zero on no-trade dates. Trades are intraday, so no multi-day mark attribution is needed. Report by year and
side; no2023+ table if not opened. Use `param_clusters.trade_net`'s market/stop slippage convention with
the hardcoded NQ tick debit explicitly scaled from$5 to$12.50, then ES commission$5.

Most likely overlap: VB/ONB index longs, and ES MOC Follow by instrument/late-day exposure. No independently
verified portfolio benefit is claimed. Only after later passes compare base/addition/replacement/empty-slot
at actual micro costs and timed exposure; do not run a funded bench on a failed cheap screen.

Report format is BUILDER_BRIEF, Summary<=5 lines. Preserve all trials, source/data/code hashes, missing-data
audit, stop-widening counts and reproduction commands. No MultiCharts/live strategy code is written for a
failed/unreviewed candidate. Work and push onlycodex/work, no live/VPS/broker/account/keys, purchases or email.
