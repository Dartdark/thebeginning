# Shanghai delivery-deadline continuation: design screen

## Scope and review adopted

Claude's review `ee0b4c2:agents/codex/results/REVIEW_fx_fix_reversal.md` accepts the FX rule's rejection and requires
cheap gross-edge screening, actual intraday exposure mapping, and a current mechanical flow. This task adopts that
workflow. It will not tune the funded roster or simulate a funded account if the design screen fails.

One signal variant is authorized here. This screen is a trial whether it passes or fails. Descriptive roster occupancy
is not an edge test and does not create extra strategy variants.

## Mechanism and novelty

Shanghai Gold Exchange deferred Au(T+D) holders must close, tender physical delivery, or roll and pay/receive the
contractual deferred fee. Delivery tenders are due within 15:00-15:30 Shanghai; equalizer tenders follow 15:31-15:40.
The hypothesis is that the first half of this deadline window reveals a net local delivery/hedging imbalance that
continues into its last 15 minutes, with arbitrage/hedging transmitting some flow to COMEX GC.

The obligation is documented, but a signed imbalance and transmission to GC are NOT observed in our data. The GC price
move is a proxy; the hypothesis can fail even when the underlying obligation is real. No source claims this exact rule
earns money. The CME 15:25-15:30 Asia marker is informational on ordinary days; do not describe it as a daily mandatory
settlement trade. NYAuTN06/12 cash settlements occur only twice per year and are not this screen's daily mechanism.

Current primary sources:
- https://en.sge.com.cn/eng_trading_matchingMarket_MarginTrading (daily delivery or deferral obligation)
- https://en.sge.com.cn/upload/file/202005/27/aUVlC5IOb7NU48Rj.pdf (Au(T+D) tender/equalizer windows, 2019 rules)
- https://en.sge.com.cn/eng_news_Announcement/10002700 (2026 deferred-contract margin rules still in force)
- https://www.cmegroup.com/education/articles-and-reports/trading-comex-gold-and-silver (cross-market gold arbitrage)

The existing gold round-one script tested Shanghai 09:00 open and 10:15/14:15 auctions, not the 15:00-15:30 physical
delivery tender deadline. Tier-list and script searches for delivery, deferred, SGE, Shanghai and 15:30 confirm no matching
rule. This distinction concerns the timed obligation; it is not a reason to revisit the failed auction variants.

## Actual intraday gap audit, before candidate P&L

Rebuild binary open-position intervals from accepted trade entries/exits, not realized P&L paths (flat accounts can
retain closed P&L). Use all ten roster strategies at their current full-size planned quantities; this is conservative
versus cushion scaling, which can switch some lines off.

- Reuse the accepted NQ entry table `analysis/outputs/codex_overlap_risk_cap/nq_overlap_entries.csv` with `q_orig > 0`.
- Replace Bridge Monday's synthetic midnight-booking intervals with its actual MultiCharts entry/exit timestamps.
- Use actual CL Sunday-gap MultiCharts times converted from the report's Eastern clock to Chicago, and include the
  overnight carry into Monday. Keep exits active through their recorded minute.
- Reconstruct accepted ES MOC entry/exit minutes with the existing function, with 2 MES planned.
- Save minute and hourly full-roster occupancy, by weekday, on design dates 2018-22 only. Explicitly distinguish any
  open gross position from signed/net exposure. No new candidate P&L or 2023+ test results enter this audit.

Target the Shanghai afternoon deadline, 01:15-01:30 CT in winter and 02:15-02:30 CT in summer. To avoid stacking with
Monday carries, the candidate is allowed to enter only when the roster has no open position as of its decision minute.
This uses information available at entry; do not filter on later exits or later P&L. Subsequent roster entries remain
unchanged. Report how often new exposure appears while the candidate would still be open.

## Exact rule: one variant

- Instrument GC, native point value $100 and tick $0.10. Prospective plan size is 1 MGC (1/10 GC), subject to the
  ordinary cushion sizing; do not assume live execution is authorized.
- Session dates: common NQ/GC weekdays in 2018-2022 when Shanghai's daytime exchange calendar is open. Use the XSHG
  calendar from `exchange-calendars` as the Chinese daytime holiday proxy, cross-check its 2022 closure dates against
  SGE's official notice https://en.sge.com.cn/eng_news_Announcement/10000677, and disclose that it is a proxy.
- Clock: construct 15:00, 15:15 and 15:30 in `Asia/Shanghai`, convert per date to `America/Chicago`.
- At the 15:15 Shanghai close compare GC with its 15:00 close. Buy if up, sell if down; skip unchanged or missing
  signal prices. Require no existing roster position at the decision minute, as above.
- Enter at the next 1-minute bar open, bar closing 15:16 Shanghai. Stop 0.25 previous-15-weekday GC ATR, rounded up to
  whole GC ticks; no target; exit at 15:30 Shanghai close. Stop active on entry bar; gap-through fills at worse open.
- Costs: $7.25 per GC round trip + one $0.10 tick on each market/stop fill = $27.25 per trade. Record gross and all costs
  separately. Use the repo's `grid.execute` walker and cost/slippage convention; no custom execution engine.
- No time, threshold, side, stop, calendar-subset or holding-period alternatives. No holdout constructed during screen.

## Cheap design gate and stop rule

Run this exact rule once on 2018-22. Report total/trades/gross per trade/round-trip cost/net per trade/net t and full
standard metrics, whole/long/short and by year. Count as ONE trial. Record skipped dates and reasons.

Continue to a full study ONLY if all hold: >=100 design trades, average gross >=1.5 times $27.25 (=$40.875), positive
net, net t>=2, at least three positive design calendar years, and >=95% of the candidate's actual position-minutes
do not overlap any existing gross position. The 50% cost margin guards against spending a full study on a marginal
execution-sensitive result.

On failure: REJECT this rule, write the concise builder-format report, leave 2023+ unopened, run no candidate Monte
Carlo, no placebos and no funded-account bench. These omissions are explicitly authorized by the user's review gate.
On pass: lock this rule, choose the closest replacement slot by design-only daily absolute P&L correlation (ties
alphabetical), and commit the full validation plan BEFORE opening holdout. The full plan must include re-executed
random-side/time placebos, holdout bootstrap/permutation, Monte Carlo at 1 MGC, and paired funded current/addition/
empty-slot/replacement configurations. A pass is only permission to validate, not a strategy promotion.

## Files and limits

Script: `analysis/codex_sge_delivery_screen.py`
Outputs: `analysis/outputs/codex_sge_delivery_screen/`
Report: `agents/codex/results/sge_delivery_screen.md`, Summary at most five lines.
Only `codex/work`; no live files, broker/VPS/API changes. Commit and push the evidence for Claude's review.
