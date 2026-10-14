# S-rank program: one S strategy per symbol (started 2026-10-14)

**Goal (user, 2026-10-14):** one S-rank strategy on each symbol we have data for, ready by the time the first live
combine account passes, so the funded accounts can trade several uncorrelated markets from day one. Different symbols
in one account share the $2,000 trailing drawdown, so a second market with its own edge lowers the blow-up risk more
than anything else can.

## The S bar, per symbol

The tier list's S (written for NQ) scaled so it means the same thing on every contract:

| Requirement | Bar |
|---|---|
| t-stat (per trade, 2018–2026) | ≥ 4.5 |
| Profit factor | ≥ 2.0 (≥ 1.6 if 500+ trades) |
| Years positive | ≥ 8 of 9 (BTC: ≥ 7 of 8) |
| Holdout 2023–2026 | positive, bootstrap Sharpe 5th percentile > 0 |
| Profit a year per full contract | ≥ ~5% of the contract's average notional (NQ: $20k on ~$400k) |
| Mechanism | a forced or scheduled flow with a placebo that fails at other times / days |
| Tradable on Apex | liquid hours, market / stop entries, flat by 15:59 CT, micro available |

Contracts (full / micro; costs per round trip + 1 tick per market or stop fill):

| Symbol | Point value | Tick | Costs used | Micro | Data |
|---|---|---|---|---|---|
| NQ | $20 | 0.25 ($5) | $7.25 | MNQ | 2018–2026, `scratch_data/g24.pkl` |
| ES | $50 | 0.25 ($12.50) | $5.00 | MES | 2017–2026, `ge.pkl` |
| YM | $5 | 1 ($5) | $5.00 | MYM | 2017-12 → 2026, `gy.pkl` |
| GC | $100 | 0.10 ($10) | $7.25 | MGC | 2017-11 → 2026, `gc.pkl` |
| CL | $1,000 | 0.01 ($10) | $7.25 | MCL | 2017-11 → 2026, `cl.pkl` |
| BTC (as 1 BTC = 10 MBT) | $1 | 5 ($5) | $25 (10 MBT × $2.50) | MBT | 2018-12 → 2026, `btc.pkl` |

## Status

| Symbol | Best so far | Tier | Round 1 |
|---|---|---|---|
| NQ | Overnight Bias ML v2 | **S** (done) | — |
| ES | Plan ports PF 1.01–1.13; forced flows same sign as NQ, weaker (EOS t 1.6, LDF 1.5) | C/D | running |
| YM | Every plan strategy ≈ 0 | F | running |
| GC | Asian-range breakout, filter B + 12:00 exit (+0.091 R, t 2.2) | C | running |
| CL | Index-roll front-run, short business days 1–4 (t 1.4) | D | running |
| BTC | Momentum file t 1.3; ETF close / BRR settlement no edge | D/F | running |

## Round 1 hypotheses (forced or scheduled flows native to each market)

Already tested and excluded: the NQ plan's strategies on every symbol; CL EIA / settlement / expiry / weekday; BTC
spot-ETF last hour and BRR monthly settlement; NQ–ES / NQ–YM pairs; cross-asset overnight filters and lead-lag.

**ES**
1. VIX expiration Wednesday: VIX settles on a special opening quotation of SPX options at the 8:30 CT open, 30 days
   before the next SPX expiry, so VIX hedgers must trade SPX options at that open (an EOS-like flow on a different day).
2. Overnight Bias with an ES-trained ML filter (the NQ S strategy's recipe, `analysis/ml_filter_test.py`, refit on ES).
3. SPX 0DTE gamma: SqueezeMetrics GEX (`data/DIX.csv`) as a regime for ES (negative GEX → follow the morning;
   positive → fade), then the MOC auction follow (NQ C, watchlist #10) on ES, where NYSE imbalances are larger.
4. EOS on ES with SPX's AM settlement (t 1.6 now): refine with VIX / GEX regime.

**YM**
1. Overnight Bias ML refit on YM; 2. MOC auction follow on YM; 3. YM–ES 1-day relative reversal (price-weighted Dow vs
cap-weighted S&P) only as a filter; 4. a generic forced-flow battery (open, expiry, month-end, quarter-end) to see if
anything is YM-specific.

**GC**
1. LBMA gold price auctions: AM 10:30 London (4:30 CT) and PM 15:00 London (9:00 CT, 10:00 CT in the DST-mismatch
   weeks — a natural experiment): pre-auction drift, post-auction reversal.
2. Shanghai Gold Exchange benchmark (10:15 / 14:15 Beijing ≈ 20:15–21:15 / 00:15–01:15 CT) and the Shanghai open:
   Chinese demand at fixed times (may be what the Asian-range breakout is picking up).
3. COMEX delivery cycle: long liquidation before first notice day of the active months (Feb / Apr / Jun / Aug / Oct /
   Dec) and COMEX options expiry (4 business days before the end of the prior month).
4. Reaction to 7:30 CT US data (NFP / CPI) follow or fade; COMEX settlement 12:30 CT.

**CL**
1. API inventory report Tuesday 15:30 CT (Globex): follow / fade.
2. WTI options expiry and futures last-trade day (TAS / settlement flows) refined; the GSCI / BCOM roll window
   (business days 5–9) instead of 1–4.
3. Sunday-open gap (weekend OPEC / geopolitics news): fade or follow to Monday.
4. Baker Hughes rig count Friday 12:00 CT; Overnight Bias ML refit on CL.

**BTC**
1. CME weekend gap: CME closes Friday 16:00 → Sunday 17:00 CT while spot trades; follow / fade the Sunday gap into
   Monday (exit by 15:59 CT).
2. Intraday seasonality since the spot ETFs (Jan 2024): fixed windows (US open, ETF NAV 14:00–15:00 CT, Asian open),
   year by year, with placebo.
3. Ports of the NQ engines to BTC (Vault Break, Overnight Bias, Late-Day Flow): BTC trends more than any equity index.
4. NQ-session spillover: does BTC follow a big NQ morning (correlation 0.4–0.6 since 2024) with a lag on hourly bars?

## Protocol (`DEVELOPMENT_PROCESS.md`)

Design 2018–22 (BTC 2019–22), holdout 2023–26, picked by design-period t; |t| ≥ 2.5 with the same sign in both
periods to advance; placebo (other times / days / random sides); longs and shorts separately; full metrics (Sharpe,
Sortino, PF, Calmar, Ulcer) and bootstrap / permutation on 2023+ for anything that advances; then the funded bench with
the trades converted to MNQ-equivalent dollars, and a MultiCharts version only for S / A candidates. Every tested item
goes in `TIER_LIST.md`.

Round 1 scripts: `analysis/s_rank_<symbol>_round1_test.py` (+ `_output.txt`).
