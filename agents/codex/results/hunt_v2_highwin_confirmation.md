# High-win Morning Momentum E1: CLOSE after frozen personal-book gate fails

Summary: The protected2018–22 design passed statistically:216trades,2,587.16USD/MNQ net,
trade t2.921/dailyNW5t2.720. ADD improved nominal median-return/DD versus BASE and EMPTY, but
missed the prespecified DD95 gate by13.97USD versus BASE; REPLACE also lost paired profit.
Both fixed fees fail the frozen combined gate. Close H05; no2023+, retuning or new PowerLanguage.
The narrow risk-gate failure is not proof of zero economic value; all source/benchmark limits remain.

Plan: `agents/codex/plans/hunt_v2_highwin_confirmation.md`, predata commit **16635fc**.
Mechanism: `agents/codex/research/hunt_v2_next_executable_nomination.md`.
Code: `analysis/codex_hunt_v2_highwin_gross.py` and `codex_hunt_v2_highwin_signal.py`.
Source/synthetic review: `agents/codex/reviews/hunt_v2_highwin_preexecution.md`.
Output: `analysis/outputs/codex_hunt_v2_highwin_confirmation/`.
Running count: **5/60 economic evaluations,5/10 hypotheses,3 gross screens**, plus archived65t6.
H05 adds1hypothesis/1gross screen/**2economic evaluations** (PROTECTED_HW and TIME_CONTROL).
Book allocations, cost diagnostics and all5,000paired paths remain in selection history; they are not new alpha rules.

## Mechanism and exact raw rule

This confirms the existing selected B-rule risk shape, not a new independent signal. The original
Twin MO opening-drive signal could reflect gradual cash/basket and hedge demand, but does not
identify compulsory traders or quantities. Its nine exit/entry variants, combined twelve-variant
MO search, full-history selected exits, longs-only cut, old Apex placement failures and Twin ancestry
remain selection history. Current personal19 contains Twin, not this separate HW bracket.

Rebuild the selected Python observed10-minute MO definition, no BO: EMA21 pivot, RMA14 range,
EMA3 normalized-price oscillator crossing±100, exact10-minute signal bucket08:40..09:30CT,
at least60 observed buckets, first signal/date. Preserve literal row-based midnight/partial-bucket
updates; start state2017-09-01. Shared known full-holiday/early-close exclusions affect entries only.
This is not a claim that the Python bucket sequence equals an ideal complete external chart/MC.

Raw event: side-signed next native minute OPEN to exact native OPEN14:51 (wall14:50), no bracket,
fees or reentry. Native NQ quotes proxy MNQ; USD gross uses actual price difference x2USD/point.
Protected design remains frozen target0.10/stop0.20 shared prior15day ATR, with entry-bar protection,
worse gap stops, conservative ticks, target-through and the same exact time exit. Those returns
were subsequently calculated once, as described below.

## Actual gross execution

One actual run **2026-10-26T22:37:30.998197+00:00 →22:38:15.782421+00:00**.
Marker: `gross_verified_execution.json`; all14 bound artifact hashes and216-event arithmetic
were independently reconciled. Main SHA256 `c1358e141d549be37839c7b22b0b305c3f283b3597bc297ed3cbd59b9083c659`;
signal helper `1e94260caf7d9420653de57a1fc565e3ad8fe72460f33a735a0d9f3ddf2c8ff3`.
Explicit12 DAY/ON annual sources:2017 warmup and2018–22 only. No old financial maker, OF, MC outcome,
broad pickle or2023+ input ran. Author14 and independent9 synthetic groups preceded data.

|2018–22 raw|Events|Gross total USD/MNQ|Gross mean|Gross t|
|---|---:|---:|---:|---:|
|Both|216|10,494.50|48.59|2.991|
|Long|117|4,646.50|39.71|2.435|
|Short|99|5,848.00|59.07|1.981|

|Year|Events|Gross total USD/MNQ|Gross mean|Gross t|
|---|---:|---:|---:|---:|
|2018|51|1,900.50|37.26|2.064|
|2019|46|−430.50|−9.36|−0.679|
|2020|27|1,195.50|44.28|0.942|
|2021|46|2,509.50|54.55|1.423|
|2022|46|5,319.50|115.64|2.136|

Full year-by-side count/mean/SD/SE/t/totals are retained in `gross_summary.csv`, events in
`gross_events.csv`. The native market-RT assumption is1.24USD commission + two adverse0.50USD
market fills =2.24USD/MNQ; gross hurdle2x=4.48USD. These are cost assumptions, not verified broker
quotes or identical MNQ liquidity. No costs were subtracted from the table and no stop/target shaped it.

## Protected design and immediate book result

Design implementation frozen at **9d75a733bcd2a3e6f237654a8a63c26619844390**, after source/synthetic
review. Separate ATR admission preceded outcomes: all216 events admitted, with **28 source-limit
events retained**. Exact15 past stored-date reference IDs and previous-close IDs are saved. A missing
normal RTH date can still have overnight observations and a stored partial-date range; no denominator
repair, price splice or profitable event deletion was used. Statistical passage never clears this limitation.
The actual `--prereg HEAD` argument resolved to that same full commit in both phases; the original
markers remain untouched and `design_invocation_binding.json` records that resolution honestly.

|2018–22,1MNQ|Trades|Win|Net total USD|Mean net|Trade t|Daily NW5t|Sharpe|Sortino|PF|Calmar|Ulcer|MaxDD USD|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|Protected HW|216|74.5%|2,587.16|11.98|2.921|2.720|1.265|1.749|1.617|0.851|0.321|586.90|
|HW longs|117|76.1%|1,364.42|11.66|2.161|1.925|0.936|1.293|1.635|0.624|0.271|422.44|
|HW shorts|99|72.7%|1,222.74|12.35|1.959|1.906|0.850|1.180|1.599|0.682|0.298|346.04|
|TIME control,unselectable|216|56.9%|10,010.66|46.35|2.853|3.213|1.237|1.999|1.781|1.463|0.862|1,321.36|

Protected net by year:2018 **−153.24**,2019 **128.96**,2020 **247.52**,2021 **963.46**,2022 **1,400.46**
USD/MNQ. Four years positive and every leave-one-year total positive: the frozen cheap design gate passes.
Both models' complete side/year metrics and daily reconciliation are saved in `design_metrics_side_year.csv`.
Protected gross2,991.00 less267.84commission and136.00slippage =2,587.16net. TIME gross10,494.50 less
267.84commission and216.00slippage =10,010.66net. Net profit per trade is the additional all-in cost
that would exhaust the observed mean; declared costs are separately retained in `design_cost_bridge.json`.

The executable adapter uses shared grid.execute privately, stops active on entry, STOP-first ambiguity,
worse gap stops, conservative quarter-point brackets and1point target-through. Time exits scan through
native890 and fill exact OPEN891, without consuming its later high/low. The original source started
protection after entry, filled targets on touch and could fall back over gaps; those results are not
nominated. The predata review also corrected time-gap excursion reporting before actual stopped returns.
All216 dates pass the shared full/early-holiday entry calendar; normal time exits are wall14:50CT,
with no exit after15:59CT. This is still a source-price/MNQ-cost replay, not verified live MNQ liquidity.

Book implementation frozen at **5c011f33b984239cb5daa937d6ff9c72782c6569** after independent source/
synthetic review, then run immediately after design passage, before extra robustness. Currentpersonal19,
whole-contract1MNQ HW,2018–22only, exactly5,000 shared252-day/20-day-block histories, seed2026102605.
Return/DD means median annual profit / median maxDD. EMPTY/REPLACE remove the **entire Twin BO+MO slot**.

|Primary fee1.24|Median annual profit USD|Median DD USD|DDp95 USD|Return/DD|
|---|---:|---:|---:|---:|
|BASE|34,650.68|4,490.17|7,182.01|7.717|
|ADD HW1MNQ|35,039.39|4,423.41|7,195.97|7.921|
|EMPTY Twin|32,633.41|4,172.42|7,376.12|7.821|
|REPLACE Twin with HW1|33,057.44|4,211.23|7,361.94|7.850|
|TIME_ADD,unselectable|36,399.54|4,608.41|7,416.59|7.899|
|TIME_REPLACE,unselectable|34,400.59|4,373.93|7,538.35|7.865|

ADD improves nominal median-return/DD against both controls, and its paired median annual-profit
increment versus BASE is **+475.58USD** (not the difference between marginal medians). Its DDp95 is
**+13.97USD** versus BASE, so it fails the predeclared nonworse-DD95 requirement. REPLACE has paired
median annual-profit change **−1,519.65USD** and DDp95 **+179.93USD** versus BASE. Both pass their
comparisons to EMPTY but not the required comparison to BOTH references. At1.04fee, ADD DDp95 is
+22.26USD and REPLACE paired profit −1,535.61USD/DDp95+189.10USD versus BASE: neither passes.

The ADD risk miss is small (about0.19% of BASE DDp95), conditional on a finite historical simulation;
it is not evidence the true risk difference is nonzero. Do not change the risk gate, repeat seeds,
resize, drop a side or nominate TIME after observing this. Retain the nominal ratio gain alongside
the failed combined gate. Joint correlations/losses, both fees, all allocation rows, historical
intervals, paired effect intervals and every resampling ID/path are saved under `personal19_design/`.

Inherited daily fee-count/reentry approximations, Twin markedv1 versus currentv2.1, exit-booked Kusho
and MOC/S30 accounting lack a supported complete implementation envelope. Even a nominal survivor
would therefore be LIMITED, not certified book improvement. These caveats do not rescue this failed
gate. Daily MC is not a valid joint funded/evaluation path; no pass, payout or live-account claim.

## Source, clocks and remaining gates

Zero invalid native OHLCV, conflicting duplicate keys or unresolved eligible entry/held/endpoint
events. All216 held paths are complete through the fixed endpoint. One normal RTH date has no
observations; it is retained as NO_OBSERVATIONS coverage under the pre-frozen observed-data rule,
not filled, deleted after P&L or declared a known ideal-chart state. Every partial/midnight bucket,
source duplicate ID and calendar date is retained. Past missing ideal minutes do not justify an
invented infinite ideal-state veto, nor does this observed replay certify the complete market feed.

Nominal feature availability is the native bucket close, followed by the next native OPEN; historical
local receipt and identical MNQ fills are unverified. Native contract/roll provenance, observed versus
ideal chart definition and the missing exact HW MC list remain limitations. No favorable roll-jump
deletion or native gap splice was used. ATR was not required/calculated by the raw screen; its exact
past-only source-reference admission must precede stopped outcomes, without a new denominator.

The protected design and immediate personal bench are now complete; their full ledgers, marker hashes,
source flags and controls are retained. No2023+ or full-history net t/DSR was calculated for H05.
Random-time/side placebos, additional dependence/selection checks, delay/cost stress, standalone MC,
fresh independent raw-spec strategy checking and any PowerLanguage/MC draft are **NOT RUN**, because
the frozen book gate failed. The preexecution source/synthetic reviews are not a substitute for those
later strategy checks. No source uncertainty is declared resolved and no new variant is authorized.

**Verdict: CLOSE H05 after its frozen book-risk gate fails.** The nominal ADD return/DD improvement
is retained honestly, but it is not a qualifying piece, permission to trade or a reason to weaken a
prespecified gate. Continue a distinct registered question; do not pause the bounded hunt or restartt6.
