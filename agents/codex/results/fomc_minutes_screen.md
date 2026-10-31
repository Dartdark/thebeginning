# FOMC minutes reaction continuation: REJECT
Summary: One scheduled NQ release trade, restricted to actual intraday gaps, failed its preregistered design gate.
2018–22: 19 trades, +$44.74 gross versus $17.25 costs per NQ; net +$27.49, t=0.14.
Only 2/5 years were profitable; two 2020 trades earned more than the entire strategy. Zero overlapping position-minutes.
Stop: no 2023+ candidate test or funded bench. Keep the roster unchanged; do not promote either side separately.
Plan: `agents/codex/plans/fomc_minutes_screen.md`, commit `f1f720d`   Script: `analysis/codex_fomc_minutes_screen.py`   Output: `analysis/outputs/codex_fomc_minutes_screen/`   Trials run: 1

## Rule (as tested)

On an official minutes-release date, follow NQ's 13:00→13:05 CT change at the next minute's open (13:06 bar).
Stop 0.25 × lagged 15-session daily ATR, rounded up to a 0.25-point tick; no target; exit at the 13:30 close.
Both sides share the rule. Commission $7.25 plus one $5 tick per market/stop fill: $17.25 per full NQ round trip.
The repository's execution walker and slippage helper performed the test; stops are active on the entry bar.

Enter only if **all current roster lines are flat at 13:05**. The occupancy builder uses actual entry/exit intervals,
including overnight Bridge/CL and ES MOC 2 MES. Opposing positions are not netted. No future roster position was
used to select an event. Among 40 releases, 21 were occupied and skipped; all 19 remaining events had complete
data and nonzero signals. There were **0 overlapping minutes out of 433 actual candidate position-minutes**.

The [Fed calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) supplies 2021–22 dates; official
[2017](https://www.federalreserve.gov/monetarypolicy/fomchistorical2017.htm),
[2018](https://www.federalreserve.gov/monetarypolicy/fomchistorical2018.htm),
[2019](https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm) and
[2020](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) archives supply earlier dates.
The [March 2021 meeting page](https://www.federalreserve.gov/monetarypolicy/fomcpresconf20210317.htm) explicitly
records the 14:00 ET / 13:00 CT minutes-release time. The committed snapshot has eight releases per calendar year,
including January releases for prior December meetings, shifted dates, and April 2020's emergency-meeting minutes.
Dates were not inferred from volatility or a fixed 21-day offset.

The hypothesis was that policy-sensitive investors/dealers use NQ to adjust exposure while processing the text,
allowing the first five-minute move to continue. This is **scheduled information flow, not a mandated order**;
the sources establish publication mechanics, not which participants must buy or sell. Statement and press-conference
reaction tests are already F; this was a new event, not a claim to rediscover those tests.

## Results

All numbers are **2018–22 only**, dollars per full NQ. Daily metrics include all 1,289 design trading dates, with
zero on dates without a candidate trade. Long/short breakdowns are descriptive, not additional selected variants.

| Side | Trades | Gross total | Costs | Net total | Gross/trade | Net/trade | Win | t | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Whole | 19 | $850 | $327.75 | $522.25 | $44.74 | $27.49 | 47.4% | 0.14 | 0.064 | 0.093 | 1.084 | 0.041 | 1.471 | $2,488.50 |
| Long | 12 | -$460 | $207.00 | -$667.00 | -$38.33 | -$55.58 | 41.7% | -0.23 | -0.105 | -0.140 | 0.850 | -0.045 | 1.639 | $2,901.25 |
| Short | 7 | $1,310 | $120.75 | $1,189.25 | $187.14 | $169.89 | 57.1% | 0.49 | 0.230 | 0.404 | 1.669 | 0.186 | 0.579 | $1,247.25 |

| Year | Trades | Gross | Net | Long net | Short net |
|---:|---:|---:|---:|---:|---:|
| 2018 | 4 | $425 | $356.00 | $0.50 | $355.50 |
| 2019 | 3 | -$515 | -$566.75 | -$527.25 | -$39.50 |
| 2020 | 2 | $2,570 | $2,535.50 | $827.75 | $1,707.75 |
| 2021 | 5 | -$675 | -$761.25 | -$1,174.00 | $412.75 |
| 2022 | 5 | -$955 | -$1,041.25 | $206.00 | -$1,247.25 |

The gross-versus-cost hurdle passed ($44.74 >= $25.875), as did positive net and >=95% unoccupied minutes.
The other gates failed: 19 trades versus >=20 required, t=0.14 versus >=2, and 2 positive years versus >=3.
The rejection does not rest on being one trade short: statistical support and year-to-year consistency are absent.
2020's two trades earned $2,535.50 against just $522.25 across all five years.

## Placebos and account level

Not run under the registered stop rule. No candidate 2023+ signals/returns, placebos, bootstrap, Monte Carlo or
funded bench were calculated. `decision.json` records those flags. There is no account-level improvement claim.
The planned continuation, had design passed, was addition at 1 MNQ and replacement of LDF with its empty-slot
control on the current paired funded bootstrap. It was not reached. No MultiCharts code was written.

## What could make this wrong (data, fills, look-ahead, multiple testing)

- The usable sample is very small: roughly four trades per year after the flat-entry condition. Positive gross
  does not establish a persistent edge. The short side has only seven trades and was not promoted as a rescue.
- NQ is an execution vehicle for equity policy repricing, but no participant position or signed news-surprise data
  were available. The first five-minute move is an unverified proxy for continuing orders; publication forces no
  directional trade. This is weaker identification than observed mechanical rebalancing demand.
- The gap map is conservative full-planned-size occupancy, not each account's cushion-scaled realization. Eligible
  release dates were 47.5% flat at the decision, less than the generic Wednesday/Thursday 13:00 hour's 56–57%.
- The grid was truncated before 2023 before candidate ATR/signals were calculated. ATR is lagged. Complete-window
  data availability is a backtest quality requirement; it removed no event here. No missing prices were filled.
- The anchor is the close stamped 13:00; all signal inputs are known at 13:05 and entry uses the next bar's open.
  Exact release-second alignment is limited by minute bars. Synthetic checks covered both sides' costs, entry-bar stops, adverse stop gaps, occupancy timing and
  the holdout guard. A separate scalar replay matched all 19 saved trades' sides, entries, exits and net dollars.
- These are continuous-contract one-minute bars and baseline one-tick fills, not native MNQ executions. The
  candidate's afternoon window does not cross the known overnight roll switch; ATR can still inherit roll jumps.
- One new return trial is counted, including this failure. TIER_LIST/WATCHLIST were checked through Claude
  `7bb539a`: obvious expiry, covered-call windows, LETF close-to-close momentum, VIX-ETP proxy momentum and
  roll-week shorts were already tested. No candidate return was calculated for the other ideas considered.

## Differences between the MultiCharts code and the test

No code was written for MultiCharts. No funded roster, live strategy, VPS/broker setting or API key changed.
