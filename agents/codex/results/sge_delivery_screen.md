# Shanghai delivery-deadline continuation: REJECT
Summary: Test a current gold delivery/deferral deadline in a verified intraday gap, using one preregistered design screen.
2018-22: 1,031 trades, -$3.89 gross per GC versus $27.25 round-trip costs; net -$31.14, t=-6.40.
There were zero overlapping position-minutes, but every design year lost after costs. A gap alone does not create an edge.
Stop here: 2023+ remains unopened; no candidate placebos, Monte Carlo or funded bench were run. Keep the roster unchanged.
Plan: `agents/codex/plans/sge_delivery_screen.md`, commit `a161117`   Script: `analysis/codex_sge_delivery_screen.py`   Output: `analysis/outputs/codex_sge_delivery_screen/`   Trials run: 1

## Rule (as tested)

On a Shanghai daytime trading date, follow GC's 15:00-15:15 Shanghai move into the 15:30 delivery deadline. Enter at
the next minute's open, only if the current roster has no open position at the decision minute. Stop 0.25 previous-15-
weekday ATR, rounded up to $0.10 GC ticks; no target. Both sides share the same rule. Costs are $7.25 commission plus
one $0.10 tick per market/stop fill: $27.25 per GC. No signal, exit or stop variants were searched.

The clock is 01:15-01:30 CT in US winter and 02:15-02:30 in summer, converted from `Asia/Shanghai` by date. GC is $100
per point; all results below are per full GC, not per NQ or MGC. Prospective plan size was 1 MGC, subject to validation.

SGE's Au(T+D) holders must close, tender delivery or roll with the contractual deferred fee; tendering runs 15:00-15:30
and equalizer tenders follow 15:31-15:40. That is a current obligation. The tested prediction—that net pressure revealed
in the first half continues into the deadline and transmits to GC—is an unproven proxy hypothesis. Local signed delivery
imbalances are absent from our data. These sources establish mechanics, not a profitable forecast:

- [SGE margin-trading mechanics](https://en.sge.com.cn/eng_trading_matchingMarket_MarginTrading)
- [SGE product rules](https://en.sge.com.cn/upload/file/202005/27/aUVlC5IOb7NU48Rj.pdf)
- [2026 deferred-contract risk-control notice](https://en.sge.com.cn/eng_news_Announcement/10002700)
- [CME discussion of cross-market gold arbitrage](https://www.cmegroup.com/education/articles-and-reports/trading-comex-gold-and-silver)

Prior gold research tested the Shanghai open and 10:15/14:15 auctions, not this physical tender deadline. CME's daily
Asia marker is informational; the twice-yearly NYAuTN cash settlement was not misrepresented as a mandatory daily flow.

## Results

The actual-position audit used trade entry/exit intervals, current full-size planned quantities, actual overnight Bridge
and CL report times, and ES MOC intervals. It did not infer flatness from zero daily P&L or from accumulated P&L paths.
Full-size occupancy is conservative versus cushion scaling, which can switch some positions off.

| Design dates | 01:00-02:00 CT minutes flat | 02:00-03:00 CT minutes flat | 10:00-11:00 CT minutes flat |
|---|---:|---:|---:|
| Monday | 45.3% | 46.5% | 8.1% |
| Tuesday | 100% | 100% | 60.2% |
| Wednesday | 100% | 100% | 58.4% |
| Thursday | 100% | 100% | 58.3% |
| Friday | 100% | 100% | 62.5% |

The rule checks flatness at entry only; later roster entries are not suppressed. Across **15,446 actual candidate
position-minutes, none overlapped an existing gross position**. The recorded activity therefore confirms a real intraday
gap, even though the strategy failed. Full minute/weekday and hourly occupancy tables are saved for future idea selection.

| Side | Trades | Gross total | Costs | Net total | Gross/trade | Net/trade | Win | t | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Whole | 1,031 | -$4,010 | $28,095 | -$32,105 | -$3.89 | -$31.14 | 38.6% | -6.40 | -2.82 | -3.54 | 0.563 | -0.195 | 35.45 | $32,108 |
| Long | 540 | -$3,440 | $14,715 | -$18,155 | -$6.37 | -$33.62 | 38.1% | -5.39 | -2.35 | -2.84 | 0.514 | -0.196 | 22.11 | $18,155 |
| Short | 491 | -$570 | $13,380 | -$13,950 | -$1.16 | -$28.41 | 39.1% | -3.76 | -1.65 | -2.17 | 0.615 | -0.195 | 13.70 | $13,985 |

| Year | Trades | Whole gross | Whole net | Long net | Short net |
|---:|---:|---:|---:|---:|---:|
| 2018 | 209 | -$1,060 | -$6,755 | -$2,626 | -$4,130 |
| 2019 | 195 | +$1,610 | -$3,704 | -$3,051 | -$653 |
| 2020 | 208 | -$2,100 | -$7,768 | -$7,049 | -$719 |
| 2021 | 203 | -$1,350 | -$6,882 | -$3,057 | -$3,824 |
| 2022 | 216 | -$1,110 | -$6,996 | -$2,371 | -$4,625 |

The registered gate required >=100 trades, gross average >=$40.875 (1.5 times costs), positive net, t>=2, >=3 positive
years and >=95% of position-minutes unoccupied by the roster. Only sample size and non-overlap passed. Cheap fills
would not fix a negative gross return. No settings were changed and the opposite direction was not searched.

## Placebos and account level

Not run. The user's review explicitly requested a cheap design gross-versus-cost check and funded simulation only after
the design gate passes. The preregistered stop rule also defers holdout, placebos, bootstrap and Monte Carlo on failure.
`decision.json` records `holdout_opened: false` and `funded_bench_run: false`. There is no candidate account claim.

The plan specifies that a passing screen would require a separately committed validation plan with design-only
replacement-slot selection, re-executed random-side/time controls, and current/addition/empty-slot/replacement funded
comparisons. This rule never reached that stage. The whole, long and short tables above are design results only.

## What could make this wrong (data, fills, look-ahead, multiple testing)

- The screen uses the XSHG daytime calendar as an SGE holiday proxy. Its 2022 sessions exactly match the official
  [SGE 2022 notice](https://en.sge.com.cn/eng_news_Announcement/10000677). Other years were not independently checked
  against every SGE announcement; the committed calendar snapshot fixes the exact dates used. `exchange-calendars`
  4.13.2 was added to the configured Python environment to generate that snapshot; reruns use the committed snapshot.
- The audit skipped 128 dates with an existing position, 86 Chinese-market closure dates, 42 unchanged signals and
  two missing signal/ATR dates. No missing entries or planned exits occurred among the 1,031 trades. Five stops fired.
- GC is an indirect hedge for Shanghai physical gold. Without local prices, FX basis and tender imbalance, the signed
  price proxy may fail even if the deadline generates real local trading. Do not claim the obligation itself is absent.
- Continuous-contract rolls can distort ATR. These intraday windows do not span the known 03:32 CT or 17:00 roll
  transitions, but prior-day ATR can still inherit roll jumps. Native MGC execution was not tested.
- CL and Bridge report exits are conservatively kept active through their stamped minute. The occupancy table uses
  accepted source trades at maximum planned size; it is not a replay of every realized account's cushion state.
- One screen is one trial, including its failure. Entry flatness is known at the decision; later overlap is measured
  for the gate rather than used to filter dates. No 2023+ candidate returns entered selection.
- Synthetic checks passed Shanghai/Chicago DST, Sunday exits versus Monday carry, inclusive midnight intervals, GC
  dollar/cost arithmetic and stops active on the entry bar. The existing `grid.execute` walker performed all executions.

## Differences between the MultiCharts code and the test

No MultiCharts code was written. No live strategy, broker/VPS setting or API key was changed.
