# Davey-inspired ES momentum/Keltner reconstruction: TEST — bounded diagnostic

Summary: Can a fixed, explicitly reconstructed trend/pullback rule clear ES trading costs?
The user supplied a screenshot/transcript and authorized discretionary completion of missing settings.
No forced trader or independent flow measurement is identified; prior related price-pattern tests are weak.
Use one frozen 30-minute/20-bar/threshold-50 rule, one contract, and a cheap 2018–22 screen.
A failure applies to this reconstruction; it cannot reproduce or refute the author's unspecified settings.

Sources: user upload `file_00000000878881f98abb4738093c6348`, preserved in
`agents/codex/inputs/davey_keltner/transcript.txt`; user screenshot transcribed alongside it.
Repository snapshot before this work: `f69ab0d`. Return trials examined before this sheet: **zero**.

## 1. Who trades, and what causes the trade?

The source proposes buying a short pullback within a longer uptrend and selling a rally within a downtrend.
It does not identify a mandatory participant, deadline, dollar flow or price-insensitive counterparty.
Temporary liquidity pressure followed by trend resumption is a hypothesis, not an established mechanism.
The transcript says ES development used 2007–June 2021 and subsequent performance began July 2021;
the plotted ledger and original optimization history are unavailable. That claim is not audited live fills.
This is the user's requested bounded source reconstruction, not a new forced-flow discovery.

## 2. Direction, size and timing known before entry

Choose 30-minute daytime ES bars, 20 completed observed bars for each momentum lookback, and threshold 50.
Twenty bars spans ten trading hours; the five-bar channel spans 2.5 hours. Fifty is its midpoint, chosen for
symmetry rather than from returns. With symmetric bands, this threshold is simply close versus the channel
center: changing the channel width does not change the direction test when ATR is positive.
One ES, no compounding. All decisions use the completed bar, orders fill at the following minute's open.
Central exchange time observes DST; input minute timestamps are CLOSE stamps. No external publication delay.
Flat at the open of the minute stamped 15:00 (14:59 CT), or 11:30 (11:29 CT) on repo-calendar early closes.

## 3. Does the flow reach the contract or direct hedge?

ES is the source instrument and the test instrument. No unobserved stock/ETF flow is assigned to it.
There is no incremental input beyond ES OHLC. This does not assume ES and MES executable fills/costs match.
At the later portfolio stage ES remains correlated index risk; a different contract alone does not diversify.

## 4. New information and data feasibility

| Input | Source/fields | Coverage / warm-up | Point-in-time limitations | Cost |
|---|---|---|---|---|
| ES minutes | Owned `data/ES_1min_2017.csv` through `2022.csv`, date/time/OHLCV | 2017 warm-up, 2018–22 design; 2017-01-02 through 2022-12-30 | CT close stamps; continuous contract roll/adjustment provenance unverified | Already owned |
| Code/rules | User screenshot and transcript, 3:30–6:40 | Channel 5, ±0.5 ATR; stop 15-bar ATR, long 4 / short 1 | Momentum values, threshold, chart interval/session and engine settings omitted | User supplied |
| Early closes | `analysis/replica.is_early_close` | Deterministic calendar, pinned by code hash | Conservative 11:29 flatten, including holidays; no retrospective choice based on P&L | Owned |

Data audit reads 2017–22 only, checks OHLC validity and duplicates; no return replay precedes the plan commit.
Require all 30 underlying minutes for a decision bar; incomplete bars produce no signal and are not filled.
Indicators span completed observed RTH bars across sessions, including the previous RTH close in true range.
No public quote data, original TradeStation workspace or official platform parity is claimed.

## 5. Costs and actual intraday gaps

One ES: $50/point, .25 tick. Repo assumption $5 round-trip commission plus one adverse tick per market/stop
fill = **$30 total**, or .60 point. Two ticks each way = $55; doubled total primary costs = $60.
The cheap gate requires average gross >=$45 and positive totals under both stronger cost assumptions.
These are research assumptions, not verified broker fees/spreads. The source's roughly 70% win rate alone
does not determine expectancy, especially with an asymmetric and potentially widening long stop.

Saved occupancy map `analysis/outputs/codex_flow_evidence_sheets/window_occupancy_summary.csv` shows the
funded roster is flat on 86.5% of 08:15 decisions and about 71.9% of minutes 14:32–14:49, 2018–22.
This reconstruction's first entry is 09:00, so it does **not** directly target the empty pre-09:00 window.
Those figures concern the pinned old roster/windows, not this candidate's event-level overlap. Expect overlap
with Vault Break/ONB long index exposure and ES MOC Follow; actual common losses remain unmeasured.
Test every eligible signal; never select observations because the plan happened to be flat.

## 6. Power before a return test

The no-return audit finds **5,311** long/short opportunities at pre-flat decisions, not independent filled
trades: repeated signals while a position is open will be blocked. There are **1,297** weekday sessions,
15,172 eligible decisions, and no missing activation minute at these opportunities.
The first eligible feature is in 2017, so the supplied ES warm-up covers the design start.
An assumed 500 completed trades with trade SD $300–$600 requires net mean about **$27–$54**, or gross
**$57–$84** including $30 costs, for naive t≈2. At only 100 trades that gross hurdle is $90–$150.
These are explicitly assumed SD/support values. Intraday dependence lowers effective support; also require
daily t>=2 and report 10-session-block uncertainty. `planning_power.csv` preserves the arithmetic.
No measured edge or adequate-power claim is inferred from opportunity counts.

## 7. Already tested and falsifiers

TIER_LIST has ES mean-reversion families, Bollinger reversal tests and NarangBlackBox (EMA/ADX/Bollinger):
weak/failed at costs. The separate uploaded RSI/Bollinger test failed its GC and NQ design gates; this is
not that code. No exact `KeltnerStochastic` / `MomLengthL` hit was found before this work.
Incremental structure: 20-bar momentum plus five-bar channel-center pullback, market entry, asymmetric
moving stops. It is related to those known families, not independent institutional evidence.
Falsifiers: no $30 cost-clearing gross edge; insufficient trade/day support; weak net t; large cost sensitivity;
direction no better than the predeclared conditional random-side controls; or unresolved causal/fill errors.
Failure does not authorize changing the bar size, momentum, threshold, direction or session.

## 8. Failure and diversification

| Question | Prediction before results | Evidence needed / falsifier |
|---|---|---|
| What breaks it? | Pullback becomes persistent reversal; repeated trend changes; cost drag | Full fixed-rule net outcomes and cost stresses |
| Liquidity role? | Marketable entries/exits consume liquidity, even though the hypothesis buys pullbacks | Broker quotes/fills later; no passive-fill benefit credited |
| Loss clustering? | Trend reversals can cluster long losses; ATR increases can widen stops | Chronological and side-specific daily/trade drawdowns; count stop widening |
| Common losses? | ES longs may share equity shocks with VB/ONB and other index longs; shorts may whipsaw together | Event-level joint losses at a later account gate |
| Offset before breach? | None promised; no hedge, account guard or offset is supplied | Later timed portfolio replay; correlation alone is insufficient |

Maximum concurrent exposure is one ES, never pyramided. Initial stop is 4×15-bar ATR long / 1× short, reset
at later bar decisions as shown in the source. It can widen and is not a fixed dollar-risk limit.
Scheduled flattening bounds the holding session; stops still have gap/slippage risk. Missing entry minute
cancels the new entry, existing protective stops remain active on observed data, and unavailable scheduled
exit quotes are reported as late-flat errors that fail the gate. No claim this size fits an Apex account.

## Decision and next gate

**TEST, diagnostic only**, under the user's instruction to fill the missing settings. The source contains
enough structure and owned data for one cheap frozen reconstruction; economic evidence remains weak.
Commit `agents/codex/plans/davey_keltner_screen.md` before any returns. At most two execution variants;
no parameter search. A fail stops optimization, 2023+ and account work. A pass is at most WATCH pending
implementation review; the source already used much of 2018–22, and 2023+ is already-seen historical
replication, never a fresh holdout. A later account stage needs base/addition/replacement/empty-slot tests,
independent review and a separately frozen forward log before any trading decision.
