# The two-strategy plan: Vault Break + Overnight Bias

One Apex 50K account, both strategies on MNQ, each on its own chart with the CME
24-hour session (Exchange time zone). All times are Central (CT).

> **Update 2026-10-13: Overnight Bias now runs with `ADXMin` 30 and `StopAtrPct` 0.25**
> (`NQ_Overnight_Bias_ADX30.txt`, MultiCharts-confirmed: 676 trades, PF 1.66, 9/9 years; 675 of 676 match
> Python). Challenge with Vault Break 8 MNQ: pass **46.9% vs 42.8%** (2023-26 51.1% vs 44.4%), same median
> 6 days; cost per funded account about $107 vs $117 at $50 a challenge. RiskPerTrade stays 1100. Details:
> `../analysis/onb_adx30_confirm.py`.

## Vault Break (`NQ_Vault_Break.txt`)

**Chart:** 30-minute MNQ, 24-hour session. **Size:** `NumContracts` 8 (8 MNQ).

**Rules**
- Noise level = the day's opening price at midnight + 30% of the average daily
  range of the last 15 weekdays (ATR).
- VWAP is calculated from midnight.
- Longs only. Up to 3 trades a day, one at a time.

**Entry**
- At the close of any 30-minute bar from 10:00 to 14:00: if the close is above the
  noise level **and** above VWAP, buy at the next bar's open.

**Exits**
- Target 40 points (8 MNQ: $640).
- Stop 75 points (8 MNQ: $1,200).
- Otherwise flat at the close of the 14:30 bar.
- Holiday half-days: no entries from 11:00, flat at 11:30.

**Backtest** (MultiCharts, 1 NQ, 2018–2026, after $7.25 costs): 1,743 trades, 66%
winners, $99 average trade, profit factor 1.28, profitable every year.

**Why it works**
- Price moves a little away from the open on most days for no reason ("noise"). A
  close beyond 30% of the normal daily range is a move bigger than the usual noise,
  and moves like that tend to keep going for the rest of the session. This is the
  intraday momentum effect that the noise-level idea is built on.
- Requiring price above VWAP means the average buyer of the day is in profit, so
  buyers are in control.
- Longs only matches NQ's long-term upward drift. The mirror-image short side was
  tested and lost money from 2023 on.
- The target is closer than the stop, so it wins often (66%). The losses are bigger
  but rarer, and the 14:30 exit avoids late-day reversals.

## Overnight Bias (`NQ_Overnight_Bias_ADX30.txt` since 2026-10-13; ADX > 30, stop 0.25 ATR)

**Chart:** 15-minute MNQ, 24-hour session. **Size:** `RiskPerTrade` 1100,
`NumContracts` 1, `ExitTime` 1430, `EarlyExitTime` 1130. The code works out the
contracts so a stop-out costs about $1,100: currently 3–4 MNQ.

**Rules**
- Overnight range = high and low from 23:00 (previous evening) to 8:30.
- Bias, from where the 8:30 open sits in that range:
  - top third (or above the overnight high): **longs only**
  - bottom third (or below the overnight low): **shorts only**
  - middle third: **no trade that day**
- Opening range = the high and low of the 8:30–8:45 bar.
- One trade a day.

**Entry**
- From the 8:45 bar close until 14:00, while ADX(14) on the 15-minute chart is
  above 20:
  - long bias: buy stop at the opening-range high
  - short bias: sell-short stop at the opening-range low
- It fills the moment price breaks the level.

**Exits**
- Stop = 30% of the average daily range of the last 15 weekdays.
- Target = 3 × the stop.
- Otherwise flat at the close of the 14:30 bar.
- Holiday half-days: no entries from 11:00, flat at 11:30.

**Backtest** (MultiCharts, 1 NQ, 2018–2026, after costs): 997 trades, 49% winners,
$278 average trade, profit factor 1.39, profitable every year. Monte Carlo: 95%
range of the average trade $147–$416; chance the edge is luck about 1 in 10,000.

**Why it works**
- Where the market opens within the overnight range shows which side the overnight
  traders pushed. An open near the overnight high means buyers were in control
  overnight (and the mirror for sellers).
- A break of the first 15 minutes' range in that same direction confirms that the
  day session agrees, which is how trend days often start.
- ADX above 20 skips choppy, directionless sessions.
- The stop and target grow and shrink with the market's daily range, so the
  strategy fits both quiet and wild markets.
- Wins are much bigger than losses (3:1 target). It wins less than half the time
  but makes its money on the trend days, mostly by holding to 14:30.

## Together in one account

| | Vault Break | Overnight Bias | Together |
|---|---|---|---|
| Days with a trade | 42% | 44% | both on the same day: 21% |
| Pass rate, own account | 41% (12 MNQ) | 37% ($1,100 risk) | **44%** (8 MNQ + $1,100) |
| Typical days to first funded account | 19 | 20 | **12** |
| Average cost to first funded account | $158 | $122 | **$117** |

- Daily P&L correlation 0.25. They mostly trade on different days.
- When both trade, they move together (correlation 0.50), and Overnight Bias's
  short days are independent of Vault Break.
- On a day both lose, the $1,000 daily loss limit can be hit. That closes everything
  for the day but does not fail the challenge, and it is included in the 44%.

## Caveats

- The explanations above are the most likely reasons for the results; the backtests
  show that the patterns held in 2018–2026, not that they will continue.
- Live trading is usually a bit worse than backtests (slippage, news days). In the
  stress test, each extra point of slippage per trade cost about 1 point of
  Overnight Bias's pass rate.
- Run both on a simulation account first and compare each trade with the backtest.
