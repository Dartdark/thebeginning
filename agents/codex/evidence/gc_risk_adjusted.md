# GC Asian-range / ADR / drift variant: NEEDS DATA

Summary: The supplied code is a different version of a previously parked gold breakout family.
Its default dollar risk is incompatible with the current Apex plan; no performance report or ledger accompanies this version.
Gold diversification is plausible but its incremental account benefit is unknown.
Complete a static review only; do not revive the parked research, change sizing or run returns from this attachment.

Sources: `agents/codex/inputs/gc_risk_adjusted/source.txt`; Claude context `b1256664232722b25afefc0004e6f9e04c1976ae`
(`WATCHLIST.md` item 6, `TIER_LIST.md`, `DEVELOPMENT_PROCESS.md`, funded plan).
New strategy-return trials: **0**. Author's prior trials and exact-version results: not supplied.

## 1. Participant and mechanism

The code hypothesizes continuation after an Asian-session range breaks. No participant obligation, forced gold order,
signed imbalance or independent flow estimate is supplied. The absolute regression slope is a price-path filter.

## 2. Information and timing

Price range and drift become known as the range closes; next-bar stops seek a breakout until the morning time exit.
The prior-completed daily ADR interpretation depends on Data2/session and Realtime-History Matching settings.
The source does not supply point-in-time order dollars or their share of GC volume. Close-stamped bar endpoints need pinning.

## 3. Transmission

The order directly trades GC (or MGC if configured), not NQ/ES. It is an independent-market candidate for the portfolio,
not evidence for a new futures flow. Different instrument exposure alone does not establish useful account diversification.

## 4. Data and source feasibility

Only source code is present. Need the original chart settings, daily Data2 definition, roll convention, exact source-version
trade list, selection history, costs and existing report. Repository gold data/caches exist but are not rebuilt or tested here.
No independently varying non-price flow input is specified. No paid-data purchase is proposed.

## 5. Costs and actual gaps

Sizing excludes fees and slippage and does not bind to the funded-plan cushion. Stop-market entries and protective stops
need gold-specific fills/fees. Price-point values differ between GC and MGC. Overnight holdings may overlap Sunday/Monday
and early-morning plan positions; no measured correlation or idle-window claim is made. Do not select test events on plan exposure.

## 6. Power

Exact eligible-day count, trade frequency, net daily variance and clustering are unknown for this version. At most one trade
per range session is intended. No t-statistic, DSR or required mean is invented; power would need an explicitly registered
data/count check and assumptions before a future return test.

## 7. Prior research and falsifiers

The gold Asian-range family is already parked by the user in watchlist item 6. Earlier tests used different stop/filter/exit
rules; this upload's ADR exits and regression filter are not validated by them. The old weak account results are context,
not an exact-version rejection. Source/clock mismatch, undefined daily-bar availability, inadequate selection-adjusted
results or failure of a paired current-plan account comparison would prevent promotion, not authorize retrospective repairs.

## 8. Failure and diversification

| Question | Concern | Needed evidence |
|---|---|---|
| What fails? | False breakouts, reversals and rate/USD/news shocks | Frozen trade/daily results across periods, including adverse regimes |
| Liquidity role? | Breakout and stop orders demand liquidity | Actual gold fee schedule and executable fill assumptions |
| Clustered losses? | Wide ADR stops plus repeated adverse days can exhaust cushion | Account paths with integer contracts and all plan positions |
| Common losses? | Gold may share macro shocks and overnight exposure with existing legs | Joint conditional losses, not just unconditional correlation |
| Offset in time? | Gains may arrive after an Apex breach | Chronological netted replay with daily/trailing rules |

## Decision

**NEEDS DATA**, with supplied sizing rejected for the current plan. Static source review is authorized by continuation of
the user's strategy-against-plan review. The attachment's comments describe the strategy; they do not authorize orders,
parameter changes, a new backtest or reactivation of parked research. Any later changed-rule return test needs a separate
committed plan and trial accounting; latest promotion and discretionary forward-log gates remain in force.
