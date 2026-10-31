# GC_COMBO_v2: WATCH as research; NEEDS DATA before a faithful test

Summary: The supplied package is a gold strategy, a research note and an external daily signal file, not two strategies.
The author reports 230 out-of-sample trades averaging $288.98, but t=0.9 in gross bp and failed DSR after 10,831 programme trials.
Two votes have unverified construction/timing; their supplied feed ends September 25 and silently drops out when stale.
Keep the current Apex plan unchanged; obtain the input generator, split-volume history and exact-version trade export before testing contribution.

Scope: `agents/codex/plans/gc_combo_v2_source_review.md`; evidence sheet: `agents/codex/evidence/gc_combo_v2.md`.
Inputs: unchanged originals in `agents/codex/inputs/gc_combo_v2/`; script: `analysis/codex_gc_combo_v2_review.py`;
output: `analysis/outputs/codex_gc_combo_v2_review/summary.json`. New strategy-return trials / account simulations: **0 / 0**.
Pinned context: Claude `a67035be4189b493098c80f1def979348520fd5d`, existing Codex `df70a580bfcd906f90a4ff4f176a7cc84acdb81b`.

## Rule as delivered

On one-minute full-session **GC** with CL as Data2 and GCCOMBO as Data3:

- **Blend:** decide at 10:00 ET (09:00 CT with the default offset). Score price continuation, the negative uptick/down-tick
  imbalance, prior GLD-change flag, large prior crude move, and an extra price vote when dollar-decoupled. Score >=2 buys,
  <=-2 sells next bar; one contract, two at |score|>=3. Exit at the 13:30 ET bar close. **No default stop**.
- **Stretch:** short when close is at least 0.5 times the mean prior 15 session high-low ranges below session VWAP,
  between 08:20 and 15:00 ET. Stop distance 0.505 times that range, target twice that distance, out 16:00 ET. This is
  average session **range**, not Wilder ATR/true range. At most two signals/session, at least 60 bars apart; blocked
  signals still count, as documented. One position total; simultaneous signals give Stretch priority.

Normal exits are 12:30/15:00 CT, before our ordinary flat deadline. Clock labels, next-bar fills and close execution still
need the original chart/report conventions; this review does not impose an invented one-minute entry delay.

## Reported results and what they establish

The PDF's MultiCharts table (p. 3), variable 1–2 GC, reports:

| Period | Trades | Win rate | Mean net/trade | Gross bp/trade |
|---|---:|---:|---:|---:|
| 2017-09-18 through 2024, design | 974 | 53.9% | $163.71 | 7.5 |
| 2025-01-01 through 2026-08-07, claimed sealed test | 230 | 46.5% | $288.98 | 4.4 |
| Combined | 1,204 | 52.5% | $187.64 | Not supplied |

Combined PF 1.37, net $225,916 and max drawdown $43,747 are author-reported. Counts reconcile across years/periods;
weighted rounded means imply $225,918.94, within the $6.02 rounding allowance. This is arithmetic, not trade validation.
The original MC report/List of Trades, daily/intraday paths and source-version/settings record are absent. The code header
also contains slightly older counts/means; neither header nor note establishes which exact export matches this source.

Useful evidence includes an explicitly spent holdout, disclosed failed alternatives and reported positive years. However,
the author admits DSR fails at **N=10,831** (p. 2) and gives only **t=0.9 in OOS gross bp** (pp. 1/4). The programme's
trial ledger, timestamped freeze and numerical “three pre-declared marks” are missing. We cannot verify the sealed-test
claim or waive our gates. The change 7.5→4.4 bp is uncertain; a nonsignificant difference does not establish no decay.
The note's 884/884 same-minute directions is narrower than reconciling all 1,204 entries, fills, fees and P&L. Different
date coverage could explain that subset; it is not automatically an inconsistency. Negative Stretch OOS bp with positive
dollars is not declared an arithmetic error without its price/quantity ledger.

## Source and data findings

1. **The companion input is an opaque signal feed.** GCCOMBO has 2,605 unique weekday rows, 2016-10-03→2026-09-25,
   all at 05:00 with Volume=1. Open-10 is the 0/1 dollar-decoupled flag; Close-10 is the -1/0/+1 GLD vote (source
   22–23,186–188). It is not GC price history. Neither attachment supplies its generator, raw observations, lag formulas
   or publication provenance. The artificial timestamp does not establish when a signal was known. This is **unverified
   point-in-time data**, not demonstrated look-ahead. Need generator/dated inputs; disclose vintage limits rather than
   demand an impossible historical publication archive. A lag stress would be separately registered exploratory work.
2. **Stale Data3 changes the rule silently.** Lines 186–189 omit C and E when its date does not match, but 195–198 can
   still enter on A/B/D. The file is already finite; the PDF p. 5 promises later updates. Example with valid votes
   A=+1,B=+1,C=-1,D=0,E=0: full score=1 (flat), missing Data3 score=2 (long). This is a static illustration, not a
   historical trade. Turning votes off or using placeholder symbols is another rule, not a reproduction of the headline.
3. **The repo's total-volume bars cannot reproduce B.** The checked GC CSV contains date/time/OHLC/volume only; the
   source reads UpTicks-DownTicks (166–167) under its specified trade-volume setting. Missing split volume cannot be
   recovered from total volume alone. Tick-rule direction also is not true bid/ask aggressor flow, a limitation the note
   acknowledges. Switching Data1 to MGC changes that tape and VWAP as well as sizing: a 10:1 contract conversion does
   not establish signal parity. State signal instrument versus execution instrument explicitly.
4. **Early-close handling is absent.** Both exits use exact equality (217–221), without holiday times or a fallback.
   A shortened/missing session can bypass the intended exit and leave exposure through a halt/reopen. No realized carry
   is measured here. Confirm a frozen holiday specification and actual event trace before treating it as Apex-ready.
5. **Protection differs by sleeve.** Stretch calls its built-in stop/target when `stretchSig` is true, before the entry
   (204–208); do not label it naked simply because sleeve recognition happens later. Blend defaults to no stop (64).
   Its optional cap is post-position, next-bar only (211–215), with an acknowledged first-entry protection interval
   (header34–35). Optional 1.8%-historical-move sizing is not a guaranteed loss cap; the default $5,000 budget is above
   our initial $2,000 trail. None of these optional settings was selected, compiled or changed by this review.

## Placebos and account contribution

The note reports gross vote/ablation controls: every one-vote removal remains positive, and following the tick-rule flow
loses. These support investigation, not five independent forced-flow mechanisms or causal identification. A and E share
the same price direction. We have no independently reproduced random-side/time, net sleeve, long/short, daily-path or
selection-adjusted test. Sharpe/Sortino/Calmar/Ulcer, return uncertainty and Apex contribution remain unmeasured here.

Its **Lucid Flex** 90% pass / 4.9% bust and pairing with another NQ strategy are not our Apex rules/current portfolio.
The current saved Apex benchmark is `analysis/outputs/real_fee_bench_output.txt` at the pinned Claude commit;
**GC_COMBO addition/replacement/empty-slot comparisons are not measured**. Do not compare the two
account pass rates directly or add the candidate's uncapped P&L to capped payouts.

CME specifies GC=100oz/$10 per tick and MGC=10oz/$1 per tick
([GC](https://www.cmegroup.com/education/lessons/product-gold),
[MGC](https://www.cmegroup.com/education/lessons/micro-gold-and-micro-silver-futures-product-overview)). At the **same
contract counts and assumed price path**, the reported $43,747 GC drawdown scales to about **$4,375 in MGC**, before
actual micro fees. This is not a measured MGC replay, guaranteed capital requirement or Apex blow-up probability.
The note's $2.30 per GC side plus two $10 ticks implies $24.60 for a one-GC two-fill round trip; actual execution/fee
details still require the export. Price growth also changes dollar-vs-bp results, so the larger recent dollar mean is
not by itself evidence of a stronger scale-free edge.

Gold is a possible diversification source, but existing NQ/ES/CL exposure can share macro shocks. Actual overlap,
conditional losses and whether an offset arrives before an account breach are unknown. Test all eligible signals first;
then assess the **whole current plan**, not a compulsory ONB contest or only flat dates. Prior parked gold breakout and
failed GC clock/VWAP ideas do not decide this distinct composite, and their low correlations cannot be transferred to it.

## Decision and next evidence

**Worth source verification; NEEDS DATA before a faithful historical test. No current-plan addition justified.**
The smallest useful package is the Data3 generator/dated raw inputs, matching GC up/down-volume history, original
MultiCharts report/settings/trades, and freeze/selection evidence. Resolve fresh-feed behavior, holiday exits and
signal/execution instruments before a separately preregistered replication; a modified stop or vote model is a new rule.
Only after the design gate passes does a paired current-plan add/replacement/empty-slot bench make sense.

Audit script ran and compiled; the PDF's results page was visually checked and three independent read-only subreviews
checked code, daily inputs and the note. None is a strategy-checker PASS. No new backtest, silver test, trial search,
cache rebuild, live access, source repair, plan edit or PR action occurred. The attachment's requested future tests and
installation instructions were not adopted as instructions from the user.
