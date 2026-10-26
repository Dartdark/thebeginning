# Sunday Opening: REJECT — fails the frozen design screen

Summary: The uploaded Sunday after-down-week long does not clear the cheap 2018–22 screen.
Next-open proxy: 112 trades, $2.92 per MNQ, PF 1.12, t 0.44; 2021–22 loses $321 per MNQ.
Its drawdown beats only 50.2% of matched random removals; historical close fills are similarly weak.
Eight primary holding paths contain missing minutes, including March 2020; estimates remain conditional.
Stop this configuration. 2023+ and all account benches remain unopened under the committed gate.

Plan: agents/codex/plans/sunday_opening.md, committed/pushed **2378ca37c244fcc7bc68dd0ccd8901555bc6c567** before returns.
Evidence: agents/codex/evidence/sunday_opening.md.
Scripts: analysis/codex_sunday_opening_inventory.py; analysis/codex_sunday_opening_screen.py.
Output: analysis/outputs/codex_sunday_opening/design_summary.json and design_metrics.csv.
Return configurations: **5**, fixed in advance; 1,000 random-removal controls; no parameter selection.
Source SHA256: e1d51b7fc4013e6af03002a48d1b47e9dffb93f87c86fb934857425b9f4bcff5.

## Rule as tested

NQ/MNQ 1-minute, Central/calendar dates. Source compares the most recent completed session close with the sixth stored close, five session intervals earlier.
This normally maps Friday-to-Friday but is not a calendar-week formula. Eligibility uses only known completed closes.
Long at the first eligible Sunday close in 17:17–17:22 inclusive; stop 80 points, target 50, time-exit decision at first available close >=19:12.
One attempt per Sunday. No new rule or clock is chosen after seeing returns.

The source uses historical `this bar on close`. V0 reproduces that *fill convention with modeled slippage*, not a MultiCharts trade-list parity claim.
Primary V1 fills at the next observed minute open plus one tick, with brackets anchored to that actual simulated entry; time exit also fills at the next observed open.
Targets need one point through, simultaneous minute stop/target crossings use stop first, and stop gaps fill at the observed open.
Both source and primary protect a close entry only after that close; its earlier high/low cannot trigger an exit.

## Design results — 2018–22 only

Common table uses dollars per NQ-equivalent. V1–V4 scale native MNQ fees/slippage by ten for comparison; V0 instead uses legacy full-NQ costs.
This makes V0 a diagnostic, not the native-MNQ baseline.

| Fixed configuration | Trades | Mean net $/NQ-equiv | t | PF | Total net $/NQ-equiv |
|---|---:|---:|---:|---:|---:|
| V0 source close / legacy fee | 112 | 31.90 | 0.48 | 1.13 | 3,573.00 |
| **V1 next-open primary / native fee** | **112** | **29.24** | **0.44** | **1.12** | **3,275.20** |
| V2 one extra tick per market/stop fill | 112 | 21.21 | 0.32 | 1.09 | 2,375.20 |
| V3 all Sundays, common eligible universe | 253 | 5.94 | 0.16 | 1.03 | 1,503.80 |
| V4 removed positive-week Sundays | 141 | −12.56 | −0.31 | 0.93 | −1,771.40 |

**At one MNQ**, V1 totals $327.52 over the design period, mean $2.92, observed-path max drawdown $895.10.
Gross before execution costs averages $4.89/MNQ; mean modeled costs $1.96/MNQ.
Costs: native MNQ $1.04 round trip plus $0.50 per market/stop fill. Actual-fill anchoring means the target requires the entry slippage to be recovered before it is reached; slippage is never charged twice.
V0 is already weak, so the failure is not explained solely by substituting next-open fills.

Primary standardized daily metrics (NQ-equivalent dollars, $50k reference capital, zero-trade days included):
win 58.0%, Sharpe 0.196, Sortino 0.257, PF 1.121, Calmar 0.072, Ulcer 4.793, maxDD $8,951/NQ-equiv.
Ulcer's capital-dependent value here is not the Ulcer of one MNQ on a $50k account.
Longs = whole strategy. Shorts = N/A; no short candidate was tested.
Of 112 exits, 85 are time exits, 17 targets and 10 stops.

| Year | Trades | Net at 1 MNQ |
|---|---:|---:|
| 2018 | 25 | $184.00 |
| 2019 | 16 | −$91.14 |
| 2020 | 23 | $555.58 |
| 2021 | 20 | $122.70 |
| 2022 | 28 | −$443.62 |

2018–20: +$648.44/MNQ. **2021–22: −$320.92/MNQ**.
Every resolved trade is assigned to its following Monday account date; daily totals reconcile exactly to trade totals.
These figures are historical simulations on observed bars, not claimed executable fills through missing intervals.

## Frozen gate and placebos

Failed: t>=2; PF>=1.20; positive in both subperiods; profit and drawdown exceeding 95% of matched random removals.
Passed: >=80 trades; positive total; extra-tick version positive; removed mean negative.
The removed group is not convincingly negative (t −0.31); its negative point estimate does not establish a useful filter.

Year-matched retained-count random removals, 1,000 draws, seed261026:
- Profit beaten: **79.1%**; plus-one upper-tail p=0.210, below the required 95% beat rate.
- Drawdown beaten: **50.2%**; plus-one lower-tail p=0.499, essentially the middle of the controls.
- No superior timing or direction is selected from the controls.

One up-week opportunity, **2020-11-29**, has no resolved exit in the same Sunday row and is explicitly unresolved. It is absent from V3/V4 valid-return statistics, not assigned zero profit.
Thus these control results condition on 253 resolved opportunities rather than the full 254 entry-window opportunities. This weakens inference further; it is not a strategy improvement.
V3 shares six-session warm-up with V1 for a common comparison even though source WeekFilter=0 itself bypasses that guard.

## Coverage and implementation limitations

No-return inventory found 260 design Sundays, 254 with an entry-window bar and 112 down-week eligible.
Two design entry dates lack exact17:17 bars; 2020-03-22 uses the permitted17:18 close.
Eight primary holding paths contain missing minutes: 2018-06-24,07-22,07-29,08-19; 2019-05-26; 2020-03-15,03-22; 2022-06-05.
No bars were invented and these stress dates were not removed to improve results.

On 2020-03-15, missing19:12 means the first observed exit-decision bar is19:21 and its next available fill bar is stamped19:35.
Holding gaps can conceal bracket events, so the reported observed-path outcome is not a verified fill.
Missing bars may reflect halts, feed/export gaps or inactivity; no cause is invented here.
These coverage limits independently block promotion; resolving them cannot substitute for passing the committed return gate.

The source reset depends on the observed modulo-clock decreasing; one >24-hour gap in late2020 does not trigger that decrease.
Across the full *no-return* inventory, 29 Sunday filter anchor pairs differ from calendar Friday-to-Friday. No 2023+ trade returns were computed to establish this timestamp fact.
The strategy observes no forced buyer or measured flow; a Sunday recovery story remains a hypothesis.
Parameter-selection history, chart IOG/magnifier/target-fill settings, and MultiCharts trade report are unavailable.

An independent source/implementation audit checked chronology, bracket anchors, complementary controls, daily reconciliation and synthetic edge cases.
Two replay issues were fixed **before the first candidate run**: resolving an early bracket exit must not require later time-exit data; a delayed entry cannot occur at/after the exit threshold.
A later metadata-only rerun added delay flags and conditional account-status wording; all trade metrics, gates and placebo numbers remained identical.
This audit is not a full strategy-checker PASS.

Arithmetic correction to the initial evidence budget: for a one-tick native-MNQ entry with brackets anchored to its actual fill, target net is $98.96 and an ordinary stop nets −$161.54; bracket-only break-even is about62.0%, not62.2%. Actual time exits/gaps make that approximation inapplicable to the full strategy. No tested rule or gate changed.

## Account placement — each requested destination

| Destination | Concrete result / limiting condition |
|---|---|
| 50K evaluation | Not run: frozen design gate failed. No pass-rate improvement is claimed. |
| 150K evaluation | Not run independently for the same precommitted stop; no inference from a 50K simulation. |
| 50K funded | Not run: gate failed before addition / Overnight Tick-VIX replacement / empty-slot bootstrap. |
| 150K funded | Not run independently under the same gate; no payout or speed improvement is claimed. |
| Personal ladder and full portfolio | Not run: gate failed before capital/size and addition/replacement/empty-slot comparisons. |

No 2023+ validation returns, forward-log promotion, Monte Carlo adoption claim or account-level test was earned.
This rejects further development of the **submitted configuration under its registered screen**; it does not prove every Sunday strategy is unprofitable.
Stop here; no clock/stop/target rescue search, trading-plan edits, live changes or automatic rank assignment.
Claude reviews this report and decides the repository grade; the user decides trading.

