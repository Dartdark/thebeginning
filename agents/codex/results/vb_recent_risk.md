# Vault Break: WATCH — weak recent backtest; no bracket change passes

Summary: August 25–October 9 net is -$3,169.25/NQ over 33 trades; requested coverage after October 9 is missing.
Losses this bad occur in 8.5–10.6% of registered historical resamples: plausible drawdown, deterioration inconclusive.
The 75-point stop versus 40-point target needs a high win rate; recent win rate is 54.5%, versus 65.2% overall.
All four fixed bracket alternatives fail the 2018–22 improvement gate; stop before alternative validation/full bench.
Actual-account performance remains unknown without verified fills and fees. No supported setting change follows.

Plan: [vb_recent_risk.md](../plans/vb_recent_risk.md), committed **832f277** before new returns.
Scripts: `analysis/codex_vb_recent_risk.py`, `analysis/codex_vb_recent_risk_report.py`.
Outputs: `analysis/outputs/codex_vb_recent_risk/`. Economic models: **5 total = existing BASE + 4 alternatives**.

## Rule and scope

Unchanged long-only NQ VB: midnight open + .30 × prior ATR15 SMA noise band, midnight VWAP,
30-minute decisions from 10:00 CT, last/flat 14:30 CT, next-minute-open entry, maximum three/day.
Early-close last 11:00 / flat 11:30. BASE target 40 / stop 75 points. Recompute exits and re-entries for every bracket.
One NQ pays $7.25 RT plus one adverse tick at entry and at stop/time exit; target exits have no extra slippage.
Research targets require a full point through. All/long results are identical; **shorts: 0 trades, ratios N/A**.

Requested dates are August 25–October 25. The complete cached day/overnight history ends **October 9**.
Local day-only NQ extends to October 21, but overnight data ends October 9; midnight anchors prevent a valid partial patch.
No unobserved session is zero-filled. The secondary 42-session window ends October 9 and is a different date window.
Stored MC SP report has TargetPts=40, StopPts=75, NumContracts=1, FlaggedContracts=-1; it is the unfiltered reference.
Its nominal end setting is 2026-10-15 09:30:00, but its last observed trade is 2026-10-06.
Neither field establishes complete native-bar coverage after October 9. This is not an audit of every deployed sizing/filter configuration.

## Recent results

All monetary results here are after stated costs per fixed one NQ, unless labeled MNQ or chart gross.

| Window | First | Last | Sessions | Trades | Win | Net/NQ | PF | Trade DD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| requested_partial | 2026-08-25 | 2026-10-09 | 34 | 33 | 54.5% | -$3,169.25 | 0.82 | $5,460.25 |
| last42_available | 2026-08-13 | 2026-10-09 | 42 | 36 | 55.6% | -$3,111.00 | 0.84 | $5,460.25 |

Primary gross -$2,690.00 less $479.25 costs = -$3,169.25 net.
Average winner $787.75, average loser $1,156.58; 18 targets,
9 stops, 6 time exits; longest losing streak 3.
In-window EOD DD is $5,460.25. Carrying the earlier equity peak into the window gives
$6,179.25 maximum DD; starting carried DD was
$719.00, ending carried DD $3,888.25.

| Calendar month | Observed sessions | Trades | Win | Net/NQ | Trade DD |
| --- | --- | --- | --- | --- | --- |
| 2026-08 | 21 | 14 | 64.3% | $243.50 | $4,483.00 |
| 2026-09 | 22 | 26 | 61.5% | $1,361.50 | $3,118.50 |
| 2026-10 | 7 | 5 | 40.0% | -$1,496.25 | $1,554.50 |

October is **October 1–9 only**. August and September above cover their whole observed months.
August 25–31 alone contributes -$3,034.50; September was positive. The requested-window loss does not mean two consecutive losing calendar months.

The stored unfiltered MC report gives -$2,381.50 over 34 trades on the same verified calendar,
versus -$3,169.25 / 33 in the stricter research replay. Both show weakness. Existing fill/parity differences remain;
the earlier .25-point reconstruction passed the original parity gate, while 1 point remains the research rule.
Neither chart-backtest figure is realized account P&L.

## Is this a normal drawdown or deterioration?

Compare the **34 observed sessions** with prior pools only. Each pool supplies 5,000 ten-session block-bootstrap paths,
seed 20261025 plus fixed pool offset; use the first 34 cumulative observations. Net tail means P(resampled net <= recent net);
DD tail means P(resampled in-window EOD DD >= recent DD). Tail estimates include the registered +1 correction.
The mean-difference interval resamples both recent and earlier data, reporting recent minus earlier dollars per session.

| Earlier pool | Sessions | Net lower tail | DD upper tail | Mean difference 90% CI / NQ/day |
| --- | --- | --- | --- | --- |
| design_2018_2022 | 1289 | 8.5% | 9.1% | [-$327.30, $214.76] |
| all_pre_window | 2228 | 10.6% | 16.6% | [-$334.90, $198.45] |

Both 90% mean-difference intervals include zero. Neither adverse tail crosses the registered 5% threshold.
Registered verdict: **within historical range; deterioration inconclusive**. Overall stays WATCH because the current period/account cannot be completed.
This is roughly one equally bad or worse net result per 9–12 comparable historical resamples, conditional on those distributions.
It is not the probability the strategy is healthy. A permanent regime change can remain undetectable in this short sample.
Overlapping actual historical-window net tail fractions are 6.0% / 9.0%;
DD fractions are 5.3% / 16.4%.
Those windows overlap and are descriptive, not independent tests.

## Why the stops feel large

The fixed bracket deliberately risks **75 points to win 40**: one full stop consumes 1.875 full gross targets.
Before costs, full-bracket break-even win rate is 65.22%. At stated NQ costs it is
65.82% (full win $787.75, full loss $1,517.25).
Time exits and gaps change realized payoff, so that bracket threshold must not be applied as the break-even rate of every trade.
The recent realized average win/loss mix implies 59.5% break-even, versus 54.5% realized wins.

At **8 MNQ**, a full bracket is $640 target versus $1,200 stop **before costs**. The archived chart rows show that scale;
they do not verify broker outcomes. A smaller contract count scales dollar exposure without changing the point payoff.
The table below reprices the same recent BASE ledger for **one MNQ** using native fees, not one tenth of NQ commissions.
These $1.04 / $1.24 RT fees are inherited research assumptions; actual fees are unverified. Micro fills may also differ from NQ.

| RT fee/MNQ | Recent net / 1 MNQ | Recent trade DD / 1 MNQ | Full target net | Full stop loss |
| --- | --- | --- | --- | --- |
| $1.04 | -$327.32 | $548.86 | $78.46 | $152.04 |
| $1.24 | -$333.92 | $550.66 | $78.26 | $152.24 |

This is a risk illustration, not a chosen size or funded/evaluation account recommendation. Other strategies, simultaneous losses,
intraday mark-to-market, trailing limits and payout rules are outside this standalone table.

## Bounded optimization: all four alternatives fail

Only **2018–22** alternative returns were computed. Gate: positive net, t>=2, PF>=1.20, >=4 positive years,
Calmar >=BASE, plus either DD <=85% BASE with net >=95%, or net >=115% BASE with DD <=105%.
Gate DD is trade-level; Calmar uses daily EOD DD. All five models have five positive design years.

| Model | Target | Stop | Trades | Win | Design net/NQ | PF | t | Trade DD | Net vs BASE | DD vs BASE | Calmar | Gate result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BASE | 40 | 75 | 861 | 63.3% | $65,787.75 | 1.24 | 2.71 | $10,544.75 | 0.0% | 0.0% | 1.22 | reference |
| S60 | 40 | 60 | 882 | 61.3% | $67,240.50 | 1.25 | 2.91 | $12,283.50 | 2.2% | 16.5% | 1.07 | Calmar lower; trade DD higher |
| S50 | 40 | 50 | 914 | 58.3% | $53,363.50 | 1.19 | 2.39 | $10,973.00 | -18.9% | 4.1% | 0.95 | PF <1.20; Calmar lower; no material gain |
| T50 | 50 | 75 | 790 | 60.9% | $51,387.50 | 1.18 | 2.01 | $8,990.25 | -21.9% | -14.7% | 1.12 | PF <1.20; Calmar lower; net falls 22% |
| T60 | 60 | 75 | 756 | 59.5% | $64,444.00 | 1.23 | 2.42 | $10,675.50 | -2.0% | 1.2% | 1.26 | No material risk or reward gain |

A 60-point stop slightly increases net but makes historical trade DD worse; a 50-point stop cuts profit and PF.
Larger targets also fail the fixed improvement gate. **No supported optimization among these changes.**
The top-20% cluster contains one setting; it cannot establish a stable plateau. Three overlapping design-fold summaries
are retained in `design_folds.csv`, with no fold-driven selection. No alternative 2023+ replay, recent-window rescue,
extra grid, placebo search, execution-stress extension or full funded bench was run after this cheap-screen failure.

## Historical baseline context

| Period | Trades | Win | Net/NQ | Net/trade | t | Sharpe | Sortino | PF | Calmar | Ulcer | EOD DD | Trade DD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018-22 | 861 | 63.3% | $65,787.75 | $76.41 | 2.71 | 1.17 | 1.77 | 1.24 | 1.22 | 3.74 | $10,512.00 | $10,544.75 |
| 2023+ | 881 | 67.1% | $76,427.75 | $86.75 | 2.66 | 1.26 | 1.91 | 1.22 | 1.42 | 5.56 | $13,905.50 | $15,802.25 |
| all | 1742 | 65.2% | $142,215.50 | $81.64 | 3.78 | 1.20 | 1.81 | 1.23 | 1.14 | 3.47 | $13,905.50 | $15,802.25 |

| Period | Trades | Win | Net/NQ | Net/trade | t | Sharpe | Sortino | PF | Calmar | Ulcer | EOD DD | Trade DD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | 135 | 58.5% | $3,916.25 | $29.01 | 0.49 | 0.46 | 0.65 | 1.11 | 0.50 | 4.51 | $7,711.75 | $7,711.75 |
| 2019 | 121 | 56.2% | $2,742.75 | $22.67 | 0.47 | 0.48 | 0.69 | 1.12 | 0.53 | 3.14 | $4,995.50 | $5,123.75 |
| 2020 | 201 | 63.7% | $22,087.75 | $109.89 | 1.83 | 1.90 | 3.03 | 1.34 | 2.58 | 3.77 | $8,323.00 | $8,323.00 |
| 2021 | 189 | 65.1% | $23,054.75 | $121.98 | 1.99 | 1.98 | 3.12 | 1.40 | 4.00 | 2.58 | $5,613.25 | $5,613.25 |
| 2022 | 215 | 68.4% | $13,986.25 | $65.05 | 0.96 | 0.87 | 1.30 | 1.16 | 1.39 | 6.42 | $9,815.25 | $10,544.75 |
| 2023 | 217 | 68.2% | $24,261.75 | $111.81 | 1.80 | 1.67 | 2.70 | 1.32 | 3.37 | 4.01 | $7,033.75 | $7,651.50 |
| 2024 | 214 | 65.4% | $11,843.50 | $55.34 | 0.83 | 0.77 | 1.15 | 1.13 | 0.88 | 10.25 | $13,054.25 | $13,403.75 |
| 2025 | 226 | 69.0% | $30,871.50 | $136.60 | 2.16 | 1.92 | 2.90 | 1.37 | 5.50 | 3.93 | $5,483.75 | $7,730.50 |
| 2026 | 224 | 65.6% | $9,451.00 | $42.19 | 0.61 | 0.65 | 0.95 | 1.09 | 1.10 | 8.53 | $10,756.50 | $10,756.50 |

Shorts are N/A for every row. Daily ratios include non-trading strategy days on the verified session calendar;
an initial zero is prepended so an immediate loss counts in DD. Ulcer uses the repo's $50,000 reference capital.
Trade DD includes closed-trade sequence, not open-position excursions. **2026 ends October 9.**
2026 year-to-date PF is 1.09 versus 1.23 overall:
the cushion is thin, even though the recent diagnostic does not establish a permanent decline.

Reuse the prior unchanged BASE 2023+ ten-session/5,000-run bootstrap rather than recomputing it:

| Metric (daily PF) | Actual | 90% bootstrap interval |
| --- | --- | --- |
| sharpe | 1.26 | 0.46 to 2.09 |
| sortino | 1.91 | 0.65 to 3.36 |
| pf_day | 1.35 | 1.12 to 1.65 |
| calmar | 1.42 | 0.29 to 2.79 |
| ulcer | 5.56 | 3.29 to 16.75 |
| max_dd | 13905.50 | 10,414.95 to 29,388.64 |
| annual | 19794.24 | 7,047.71 to 32,386.07 |

Source: `analysis/outputs/codex_vb_parity_stress/VB_research_baseline_bootstrap.csv`, hash recorded in `report_sources.json`.
That existing bootstrap omits the extra initial-zero metric observation; its point estimates differ slightly from the table above.
Previously examined 2023+ history is historical validation, not fresh holdout or forward evidence.

## Actual-account audit and missing inputs

Available archived VB logs are only October 20–21: 142 raw rows, 98 after exact deduplication, six chart closes
across VB / VB-2 account copies and **three shared entry labels**. Separate gross chart sums are -$1,760 / -$1,752;
they must not be added as independent evidence or called executed net losses. The prior order audit has an October 20
rejected entry despite a chart CLOSE row. No complete broker exit/fee ledger exists here.
**Actual-account verdict: INSUFFICIENT VERIFIED FILLS.** No actual/backtest ratio or actual-account deterioration claim.

Needed to finish both sides through October 23:

- Broker execution/trade export for August 25–October 23, including fills, exits, quantity, fees, account/strategy mapping and timezone.
- Complete matching NQ day **and overnight** minute exports through October 23, plus current MC strategy report/settings
  identifying the deployed variant, size and single-print filter configuration. Broker credentials are not needed.
- If available, the account equity/drawdown export to reconcile overlapping strategy positions and account limits.

## Trials, checks and limitations

Four new bracket alternatives; BASE is an unchanged repeat. Prior VB work includes 720 parameter combinations and 314
robustness stresses. Identical engineering reruns do not create new selected models. Current ranked-item count is
274; item count plus four is 278, t bar **3.57**.
Design DSRs and t statistics at that count are saved in `multiple_testing.json`; none promotes a replacement.
The ranked-item count does not capture every unpublished historical search. No shared trial/ranking file was edited.

Verification: all **1,742** BASE trades reproduce the saved ledger (dates, entries, exits, direction, kind, gross and net).
Independent ledger checks reconcile totals/costs and initial-zero DD, restrict every alternative to pre-2023, confirm the stop gate,
separate account copies and verify source hashes. Synthetic checks cover initial losses, streaks and changed-exit re-entry eligibility.
Missing held-minute inventory: 2 historical trades / 3 minutes; **none in this recent window**.
Those historical gaps remain in the baseline; no favorable deletion or cache repair. Fills, source adjustments, one-minute path assumptions,
small recent sample and incomplete current coverage can all affect the conclusion.

No PowerLanguage, live strategy, account/VPS setting or logger changed. No cache rebuilt or package installed.
This audit supports completing current data/fill reconciliation before considering another optimization family.

Reproduce using the installed scientific Python environment (manifest records the exact interpreter):

```powershell
$vbPython = 'C:\Users\dmoto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $vbPython -B analysis/codex_vb_recent_risk.py --phase design
& $vbPython -B analysis/codex_vb_recent_risk.py --phase validation
& $vbPython -B analysis/codex_vb_recent_risk_report.py
```

Claude review path: `agents/codex/results/vb_recent_risk.md`.
