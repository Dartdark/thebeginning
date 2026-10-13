# Forced flows: when trades have to happen (2026-10-13)

A forced flow is trading that must happen at a known time (or in a known direction) whatever the
price: a contract expires, a fund must match an index at the close, a product must rebalance its
leverage, a risk model sets the size. These have been the best edges in this repo; price-pattern
direction signals have failed out of sample. This map lists the known ones by time, who has to
trade, and what has been tested. Times are CT.

## Every day

| When (CT) | Who has to trade | Why | Status here |
|---|---|---|---|
| 8:30 cash open | Market-on-open orders, overnight hedges, options settling at the open (monthly AM expiries) | Orders priced at the official open | Monthly expiry: **Expiration Open Short (A, in plan)**; Overnight Bias trades the open's position in the overnight range |
| 7:30 / 9:00 data releases | Not forced, but scheduled: algorithms and hedgers re-price at once | Liquidity is thin before 8:30 | **NFP Fade (B, in plan)**; other releases F |
| 13:00 FOMC (8 a year) | Rate-sensitive hedgers | Scheduled shock | D (no reliable direction) |
| ~14:00–15:00 last hour | **Leveraged / inverse ETFs** (TQQQ, SQQQ, SSO...) must rebalance by L(L−1) × assets × the day's return; MOC orders from index funds; 0DTE dealer hedging | Daily-reset leverage; funds track the closing price | **Late-Day Flow (A, in plan)** |
| 14:00–15:00 on vol-spike days | **Volatility-control / risk-parity funds** cut exposure when vol rises (rules known a day ahead) | Exposure = target vol / realized vol | **Vol-Control Sell Flow (B, in plan)** |
| 14:50 MOC imbalance published, 15:00 close | Closing auction: index funds, ETF creations, benchmarked funds | Must trade at the close | Last-30-minute momentum D; needs the imbalance feed (paid) to go further |
| 15:00 settlement → 15:15 | Futures settled at 15:00; hedges against settlement unwind | Daily settlement | Post-settlement reversal D (real, t −4, but ~$12 a trade) |
| 17:00 reopen → overnight | Dealers carrying the day's inventory; Asia / Europe hedging | Paid to hold inventory overnight | Overnight Drift C (backup) |

## Every week

| When | Who | Why | Status |
|---|---|---|---|
| Monday | Weekend inflows (payroll, 401k, retail), dealers re-hedging after the weekend | Cash arrives at the start of the week | **Monday Long (A, in plan)** |
| Friday afternoon | Weekly options expire (PM-settled SPX / NDX / QQQ weeklies): pinning to big strikes, then hedges come off | Expiry at the close | **Untested** (only the monthly AM expiry open is tested) |
| Friday | Pre-weekend de-risking | Risk limits over the weekend | F |
| Monday–Thursday since 2022 | Daily 0DTE options expire at the close | Dealer gamma concentrated in the last hours | Partly inside Late-Day Flow; strike-level data needed for more |
| Wednesday (monthly) | VIX settlement at the 8:30 open (SPX options used to settle VIX) | Expiry at the open | F |

## Every month

| When | Who | Why | Status |
|---|---|---|---|
| 3rd Friday, 8:30 open | Monthly index options settle on the open (SOQ) | AM settlement | **Expiration Open Short (A)** |
| Monday after monthly expiry | Dealer gamma released after expiry ("unpinning") | Hedges reset | Day after triple witching D (quarterly only) |
| Last 3 days / first 3 days | Pension and balanced-fund rebalancing, salary inflows | Monthly rebalance, payday | Month-end fade D; turn of month C |
| 1st Friday 7:30 | Payroll report | Scheduled | NFP Fade (B) |
| Mid-month | Pay days | Inflows | F |

## Every quarter

| When | Who | Why | Status |
|---|---|---|---|
| 3rd Friday of Mar / Jun / Sep / Dec | Triple witching: futures, index options and single-stock options expire together; S&P / Nasdaq-100 quarterly rebalances at the close | Index funds must trade at the close | D / F |
| Week before | Futures roll (ES / NQ rolled to the next quarter) | Contracts expire | Roll-week short D |
| Last business day of the quarter | **JPMorgan Hedged Equity fund collar reset** (sells calls, buys put spreads on SPX, ~$15–20bn): dealers hedge a huge position that resets on a known date | Fund rules | **Untested** |
| Last business day of Feb / May / Aug / Nov | **MSCI quarterly index reviews**: global index funds trade at the close | Index changes effective at the close | **Untested** |
| Quarter end | Pension rebalancing, window dressing | Quarterly rebalance | F |
| Earnings blackout (~2 weeks before earnings) | Company buybacks pause | Rules on insider periods | F |

## Every year

| When | Who | Why | Status |
|---|---|---|---|
| Last Friday of June | Russell reconstitution (the biggest closing auction of the year) | Index change at the close | F (one day a year) |
| 3rd Friday of December | Nasdaq-100 annual reconstitution | Index change at the close | F |
| December | Tax-loss selling, year-end rebalancing | Tax year | Untested (few days, single-stock mostly) |
| Rare | Nasdaq-100 special rebalance (concentration limit), S&P additions of giants | Index rules | Not testable (one event in the data) |

## What is left to test (price data only)

1. **Weekly (PM-settled) options expiry Fridays:** does NQ pin in the afternoon and break out after
   (Friday 13:00–15:00 vs other days; Monday after)? About 40 non-monthly Fridays a year.
2. **MSCI review days** (last business day of Feb / May / Aug / Nov): last-hour direction and size of
   the move into the 15:00 close. About 35 events since 2018.
3. **JPMorgan collar reset** (last business day of each quarter): pinning before the reset and the
   move after (days −3 to +2). About 35 events; the fund's strikes are published, so a "distance to
   the call strike" version is possible later.
4. With paid data only: MOC imbalance (14:50), strike-level open interest (gamma walls), CME large
   open interest by account type.
