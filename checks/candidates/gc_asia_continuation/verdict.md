# GC USA -> Asia night continuation: verdict (Claude, 2026-11-01): D; no added variable recommended

User upload 2026-11-01: `Gold_USA_Asia_Continuation_v4_uploaded.txt` and a MultiCharts report. Paper: Wei (2026), "Who Moves
the Price?" (`papers/Wei_2026_who_moves_the_price_gold_silver_sessions.pdf`). The request: one more discriminating variable
that isolates the effect and cuts the drawdown, without curve-fitting.

Rebuild: `analysis/gc_asia_continuation_test.py`. It follows the code bar by bar on our 1-minute GC data (CT, 2017-11 to
2026-10), at our costs of $27.25 per GC round trip. Outputs: `analysis/outputs/gc_asia_continuation_shift-60.txt` (New York
clock) and `..._shift0.txt` (Chicago clock).

## 1. Clock
The code's inputs are meant as CST (UTC-6). Read that way on CT data, the rule loses in 2018-22 (1 GC: PF 0.88, t -0.72).
Read on a New York-time chart, which is how our MultiCharts maps COMEX symbols (MULTICHARTS_PITFALLS), every window moves one
hour earlier. That version comes closest to the report: 2023+ ATR-sized net $94.8k vs the report's $98.0k, PF 1.27 vs 1.31.
2018-22 is $130k vs $197k. Moving the boundary by one hour swings the 2018-22 PF from 0.88 to 1.23, so the result depends on
exactly where the sessions start and end.

## 2. What the "USA up" condition adds (New York clock, 1 GC)

| Long every Asia session | 2018-22, $ a night | 2023+, $ a night |
|---|---:|---:|
| Every night | -$14 | +$132 |
| USA up (the rule) | +$49 (t 1.28) | +$145 (t 0.95) |
| USA down | -$85 (t -1.98) | +$118 |

Continuation was real in 2018-22. Since 2023, nights after a down USA session earn about as much as the rule does: the
out-of-sample profit is Asian-hours gold drift in a bull market, not continuation. That is why the profit factor drops from
1.64 to 1.31 out of sample.

## 3. Drawdown
The 2023+ drawdown is a few extreme nights. At 1 GC: -$17.8k on 2026-04-02, plus about -$5k to -$6k each on 2025-04-25,
2026-02-24, 05-12, 01-07 and 04-21. The risk of 1 GC at 1 x the Asia ATR went from $570 (2018) to $5,680 (2026).

Sizing in MGC doesn't help. The ATR budget then really sizes down, since the code's floor of 1 GC breaks the $6,000 budget
on only 7% of trades. The 2023+ max DD is $37.8k vs $34.2k.

## 4. Candidates (written down before any result; chosen on 2018-22 only; 1 GC)

| Candidate | 2018-22 | 2023+ |
|---|---|---|
| V1 USA close in the upper half of its range | no change | worse |
| V2 last USA hour up | worse | worse |
| V3 dollar not down (6E USA return <= 0) | best (kept $111 vs removed $11, beats 88% of random-removal placebos) | **reverses**: kept $66 vs removed $195 |
| V4 skip Shanghai Gold Exchange holidays (chosen) | kept $60 vs removed -$240 (10 nights) | kept $158 vs removed -$27 (19 nights) |

V4 holds up in both periods but touches only ~5% of trades and doesn't lower the max DD (2023+ $34.2k -> $35.8k). On the
Chicago clock it reverses in 2023+.

No candidate cuts the out-of-sample drawdown, and none holds on both clocks.

## 5. Standard metrics (New York clock, per GC)

| Period | Trades | Avg | PF | Sharpe | Sortino | Calmar | Ulcer | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Whole | 556 | $95 | 1.23 | 0.37 | 0.55 | 0.15 | 8.1 | $34.2k |
| 2018-22 | 288 | $49 | 1.23 | 0.56 | | | | |
| 2023+ | 268 | $145 | 1.22 | 0.41 | | | | $34.2k |

The rule is long only, so longs = whole.
- **Bootstrap, 2023+:** Sharpe p5 -0.44, P(Sharpe <= 0) 22%.
- **Monte Carlo, 1 MGC:** P(total <= 0) 10%; one-year P(EOD $2,000 trail hit) 9%.

## 6. Code review (`Gold_USA_Asia_Continuation_v4_uploaded.txt`)
No logic defect found:
- **Daylight time:** the DST rule (second Sunday in March to the first Sunday in November) is right.
- **Session handling:** the weekend skip (the Friday -> Sunday USA session), the regime and ATR buffers and the fallbacks
  are all causal.
- **Fills:** the entry and the time exit fill at the next bar's open.

Points to check:
- (a) **Chart clock.** If the GC chart is on Exchange time and the feed maps COMEX to New York, every window is one hour
  earlier than intended. That is probably what the report ran.
- (b) **Sizing floor.** The 1-contract floor breaks the risk budget in high-volatility years; MGC lets the sizing work.
- (c) **ATR sizing and the report's dollars.** Sizing by the Asia ATR puts about 7 GC per trade in 2018-22 and 3.6 since
  2023, so the in-sample dollars are inflated relative to 2023+. Compare periods at a fixed size.

## Tier
**D**: as tested, the continuation effect makes about nothing at a fixed size (whole t ~1.1). It is not distinguishable from
Asia-session drift since 2023, and it depends on the session clock. It fits no Apex plan; no plan bench was run, since the
standalone result is far below the bar.
