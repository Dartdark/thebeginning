# Possible H08 MCL Sunday sizing: source-only interface and feasibility

Status: **TEST at preregistration preparation only**, subject to the frozen source, risk-accounting and support gates below. This note does not register a configuration or authorize actual input reads. No CSV headers/rows, caches, MC event values, ledgers or returns were opened; no maker was imported or executed. H07 remains closed. Root alone decides the preregistration and later execution. Nomination/eight questions: `agents/codex/research/hunt_v2_mcl_risk_normalization_nomination.md`.

## Exact source scope

Adopted source revision: `d14dc9a153df128aafd3f48d4fea2aa78b88bb28`.

| Source | Git blob | Use |
|---|---|---|
| `funded_strategies/CL_Sunday_Gap_Fade.txt` | `80c08a9aa7eff9d5c0e5712bdeb0d3b415fc301c` | Literal selected PL parent |
| `analysis/cl_sunday_fade_confirm.py` | `96f62653b149e6d41d291af6d969ed51363de513` | Existing clock/parity method, source only |
| `analysis/cl_sunday_fade_bench.py` | `9ec6c2c03f9a1a07cc776ce653ff47dbb8c4bbe1` | Old execution/account interface and selection history |
| `analysis/s_rank_gap_round2_test.py` | `b4f7fb2cc4d3e2cb544aa00c9c5c23e296a44078` | Original selection and cached-frame construction |
| `analysis/grid24.py` | `25bba47db128ca79f09015e4ef3a6be5ed0dd2a7` | Shared native calendar/minute adapter and ATR comparison |
| `analysis/grid.py` | `161570157b5302e869a760474660fe8eddec5bcb` | Shared execution, with explicit overnight/native-contract adapter |
| `analysis/personal_portfolio.py` | `80d90aca24b413957ea32721334bf08191d8f162` | Published one-MCL personal slot and fee convention |

No historical source code should be imported: `cl_forced_flows_test.load` has a broad all-year file pattern and pickle cache; the old main/bench reads financial outcomes and other plan legs. Use the pinned source as a specification only, then an independently reviewed Codex adapter with explicit 2017 warmup and 2018–22 file inventory. Do not load `s_rank_gap2.pkl`, `cl.pkl` or the old maker.

## Literal selected parent, before any sizing change

- Chart: five-minute CL/MCL, NYMEX Eastern exchange time, full session, one-minute Bar Magnifier. Native exports are Central close labels; convert civil timestamps with named zones, without an offset search. This is the selected chart convention, not a new entry-time variant.
- On the first observed Sunday five-minute chart bar, compare that bar's OPEN with `Close[1]`, the preceding observed chart bar's close. Normally these are the Sunday 17:00CT reopen and Friday's final bar. The code does not require that preceding observed bar to carry a Friday date; preserve/audit holiday gaps rather than inventing a Friday-only filter or nearby-clock repair.
- Signal only when gap >=0.10×prior ATR15. Default `FadeDownGaps=false`: SHORT only. Consume the Sunday signal once; no added long, reentry or alternate gap threshold. If the first five-minute reopen bar is 17:00–17:05CT, the decision is its C1705 and next-bar entry is native OPEN1706, wall17:05CT. Do not silently use old native OPEN1705/wall17:04.
- Stop distance is0.75×the signal ATR; no target. The quantity and stop distance are decided from this already-known ATR. Literal PL uses `SetStopContract`/`SetStopLoss(StopPts*BigPointValue)`, which is per-contract and can protect the entry bar. The extra live through-stop guard is a next-bar market fallback; it is not permission to defer a backtest stop until a later bar.
- Surviving position exits on the close of the first weekday chart bar with Time>=1000ET. Under the selected chart timing this is Monday C0900CT. PL does not condition entry on Monday being a full session. It includes Monday holidays and roll weekends. If the scheduled Monday exit is absent, source execution needs an explicit pre-frozen disposition; never forward-fill/back-fill the endpoint or infer an arbitrary favorable later/earlier close.
- Sunday17:00→Monday09:00 is the adopted Sunday exception within Monday's account session. It does not cross the Monday16:00–17:00 break and is before15:59CT. Calendar/source audits must retain holiday Mondays and actual exchange closures; no future full-Monday test may decide a Sunday entry.

## ATR definition must follow the chart, not the old CT shortcut

Literal PL updates `DayHi/DayLo/DayClose` from observed **five-minute Eastern-close-labelled bars**. On a date change, inside the literal `DayClose>0` guard, it scores the completed observed date iff that date was Monday–Friday:

`TR=max(DayHi,PrevDayClose)-min(DayLo,PrevDayClose)`, or high−low without an earlier positive close.

`PrevDayClose` updates for every completed observed date, including Sunday; only weekday TRs enter the15-slot circular buffer. ATR is the arithmetic mean once15 scored dates exist. At Sunday's first bar the completed Friday TR can be inserted, so the reference set is the prior15 stored weekday chart dates, all known then. No Monday price or existence test is needed. Missing/partial observed source dates remain explicit source limits and reference IDs, not fabricated complete daily ranges.

`Grid24.daily_atr(15)` instead aggregates **Central minute-calendar** dates and scores observed weekdays. It is a useful shared-function comparison but is not automatically the literal Eastern five-minute-chart ATR: bars stamped midnight belong to the new chart date, including the preceding minutes in that five-minute bucket. Do not claim parity or substitute the CT series because it is convenient. Freeze a pure Eastern chart-bar ATR adapter and synthetic boundary/holiday fixtures before any actual feature counts. Using the same independently reconstructed parent for q1 and the candidate isolates sizing; differences from published/old-parent execution need separate implementation controls.

## Existing selection and why the old maker is unsuitable

`sunday_frame` derives candidate Sundays from `S.tr` Monday rows and `S.full[Monday]`; `Grid24.trading` requires that day's observed maximum clock>=1100, and `S.full` requires Monday last_j>=1500CT. This conditions Sunday eligibility on future Monday data. It also chooses the first observed reopen OPEN within ten minutes. The old frame takes ATR at the Monday index and computes roll diagnostics from future window observations. These cached frames cannot establish the new causal entry universe.

The selected confirm/bench changed entry to OPEN1706, exit to C0900, and `ROLL_SKIP=False`, but still consumes that cached frame. It forward-fills all closes; it skips an absent entry; a missing stop-bar OPEN falls back to the theoretical stop. Entry slippage is included in the short entry before placing its stop. Preserve these differences as baseline implementation effects; do not call their correction sizing alpha or retroactively remove roll weekends. The original CT ATR versus Eastern PL ATR remains a source distinction even though historical source comments report substantial MC agreement. This note did not open that report or recheck its numbers.

Existing PL `RiskPerTrade(0)` chooses fixed `NumContracts`; positive RiskPerTrade already implements `floor(RiskPerTrade/(StopPts*BigPointValue))`, potentially zero contracts. Existing bench explicitly tries constant q0/1/2/3/5 and cushion levels. Original family selection includes side/gap/exit/entry/stop alternatives. All remain multiplicity/history. The proposed fixed1/2 whole-MCL affordability rule is not the invention of ATR sizing, a fresh standalone entry edge, or a constant-dollar normalized return stream.

## Native MCL cash flows and the proposed extra-lot rule

MCL point value100USD, tick0.01=1USD. Primary research allowance is1.24USD round-trip commission plus one adverse tick on each market/stop fill: **3.24USD/MCL round trip**, before a fixed larger-slippage stress. CL quotes can drive the research signal, but no actual historical MCL fill/liquidity/contract-roll identity is verified by merely multiplying CL price points by100. Do not rescale CL net costs or NQ dollar P&L into the candidate.

Root's proposed fixed research slice is250USD: q2 only when `2*(planned_per_MCL_stop_risk+native_RT_allowance)<=250`, otherwise retain q1. Preregister the native tick rounding of planned stop distance and the exact cost allowance before values. This is **extra-lot affordability**, not a hard250USD risk cap: baseline q1 is retained even if one planned stop exceeds250, and a gap can lose more than its planned stop. No volatility percentile, ATR window or dollar-budget search is justified.

For actual cash flows distinguish quoted/raw entry from executed entry. If a short's stop is anchored to executed OPEN−one tick, its fill-to-stop distance already incorporates that anchor; subtracting another entry tick from that executed-entry-to-stop loss double-charges it. Save raw prices, executed prices, stop anchor, commission, each slippage component and net bridge explicitly. The conservative two-market-fill planning allowance need not equal an actual stop trade's distance-to-executed-stop cash loss; it must not be charged twice. Whole q1/q2 quantities multiply actual native cash flows and paths, never standardized/ATR-rescaled returns.

## Execution and adopted-book interfaces

Shared `grid.execute` takes a single row's minute array, decides at dj and enters dj+1, checks `_walk` starting on the entry bar, fills a later adverse gap at the OPEN, and time-exits at a close. Its defaults are NQ PV20/commission7.25/target-through1point, truncation by last_j, absent-OPEN skips and last-close fallback. Do not use those NQ money fields, per-calendar-day truncation or missing-endpoint fallbacks for this overnight MCL rule.

An explicit private adapter can present each Sunday–Monday window as one chronological2880-minute row, with decision1025, entry1026 and endpoint1440+540. This preserves shared execution/entry-bar protection while avoiding Sunday-row termination. Use native MCL money, no target, conservative tick orders, strict required endpoint/held-source admission and worse-gap fills; disclose any `_walk` override and never mutate shared files. All entry/source/adverse-path gaps must be retained before outcomes, with genuine exchange closures distinguished from unverified feed loss. No invented intraday safety can be inferred from a daily close ledger.

Current personal19 has exactly one `CLSundayFade_perMCL` slot. `analysis/codex_hunt_v2_highwin_bench.py` pins the adopted nineteen-column book and two fee views; the primary baseline is `analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv`, with1.04 diagnostic. Those files were identified from code only, not read. The underlying personal code subtracts native commission minus0.725 from nonzero plan-day returns; original published `EXTRA=.55` implied1.275, and exact per-trade/zero-net-day fee reconciliation remains a disclosed limit. Other-leg reentry/mark/OT-coverage limitations remain unchanged. Existing funded source uses2MCL at full cushion and1 at half/intermediate cushion; it is not the personal one-MCL base or a valid joint account path by itself.

If preparation passes, immediate design bench needs published BASE, EMPTY of the whole one-MCL Sunday slot, a causal protected q1 parent implementation control, and the frozen sizing allocation using the identical causal parent. Separate ADD/REPLACE definitions must state whether the existing published slot is retained. For REPLACE compare both published BASE/EMPTY and q1 replacement; for ADD compare the extra exposure with its unfiltered-parent allocation control. Paired current-book daily histories can assess personal return/DD. The old bench's constant worst-loss proxies are insufficient for funded/evaluation pass/payout or joint breach claims; require valid joint paths or retain a genuine limitation.

## Decision before data

**TEST** is defensible for a bounded allocation experiment with an independently reconstructed, causal observed-source parent and paired q1 control, if Root freezes its exact Eastern ATR, calendar, missing-source, native tick/fee and allocation gates first. There is no known mathematical need for future Monday `trading/full` eligibility, roll deletion, future outcome normalization or source substitution. All prior variants and the affordability rule's inherited parent selection remain recorded.

**NEEDS DATA** applies to any claim of exact live/MCL fill identity, authenticated constituent-contract roll safety, complete independent MC parity, or funded/evaluation improvement without valid joint paths. Do not repair those limitations by a return-selected contract splice, gap threshold or favorable omission. If preregistered source/support gates cannot admit the causal parent, close this hypothesis before gross/economic returns. No implementation or actual data access is authorized by this source note.
