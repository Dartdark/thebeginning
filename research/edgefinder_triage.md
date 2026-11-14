# EdgeFinder (A1 Trading) triage — 2026-11-14

User: "i opened something called the edgefinder ... go through it and see if we can use any of it". A Google Looker Studio
dashboard (no export, no API seen); every section read in the browser. The rule for us: only data with a usable HISTORY can be
tested; a live score with no history can only be forward-logged.

| Section | What it is | History? | Already in our work | Verdict |
|---|---|---|---|---|
| Top Setups / Asset & Forex Scorecards / Top Setups Indicator / Trade Ideas | A composite bias score per asset (NASDAQ, SPX500, DOW, RUSSELL, USOIL, GOLD, BITCOIN, FX...): trend + seasonality + COT + retail sentiment + 14 US / foreign macro releases, each -2..+2 | No (today's snapshot, 1-day change) | Every input is something we test separately | Untestable as is. Only option: forward-log the daily NASDAQ / SPX500 / USOIL / GOLD / BITCOIN scores for 6-12 months |
| COT (latest, history, velocity, trends) | CFTC Commitments of Traders | Yes (CFTC, public, we have it) | Tested 5 ways (Bridge dealer rank, CoT reversal index, hedgers vs speculators, retail-gap COT): weak / F | Nothing new |
| Retail sentiment + history | Broker clients' long / short % per asset, every 30 min | Shallow in the dashboard (default view Sep-Nov 2026; depth unknown) | Not tested (no source with history) | Interesting (contrarian retail positioning on NASDAQ / SPX500 / oil / gold) but needs years of history: forward-log |
| Put-call ratio, net options volume, put / call walls | CBOE options data | Put-call: yes at the source (CBOE) | Not in our data sweep; GEX / DIX are | **Add the CBOE equity / index put-call ratio to the data sweep** |
| AAII sentiment | Weekly bull / bear survey | Yes at the source (AAII, weekly since 1987) | Not in the sweep | **Add to the data sweep** |
| Eco Surprise / Eco Strength Index | Share of recent releases beating forecast, per currency (USD 83% today) | Shallow (1-month default view); needs consensus history we don't have | Event-day strategies (NFP fade etc.) | Forward-log the USD reading, or skip |
| Real yields, credit spreads, BTC / gold ratio, carry scanner | Spreads | Yes | TIP/IEF breakevens, HYG/LQD credit, copper/gold already in the sweep | Nothing new |
| Economic heatmaps / data (US, EU, UK, JP, CA, AU, NZ, CH, CN) | Latest macro releases vs prior / forecast | Releases yes (public); the heatmap scoring no | Macro event strategies tested | Nothing new for intraday NQ / ES |
| Seasonality scanners (annual, monthly) | Average return by month / day of year | We compute our own | Several seasonality rows ranked (mostly F / D) | Nothing new |
| Scenario backtests | Forward returns after events (S&P +3% day, VIX spikes, 3-4 up / down days, new highs) | Computed by them | Streak / VIX-spike / breakout studies done | **Their numbers are broken** (S&P +3% day: '+16.9% average 1-day return, 6,558% positive'): don't use |
| Technical scanners (momentum, volatility heatmaps), market heatmap | Snapshots | No | Our own indicators | Nothing new |
| Geopolitical Risk Tracker | Geopolitical risk reading | The public Caldara-Iacoviello GPR index has daily history since 1985 | Not in the sweep | **Add the public GPR index to the data sweep** |
| AI news feed, economic calendar | Headlines, calendar | No | Calendar-driven pieces already | Nothing new |

## What can help
1. Three PUBLIC series with long histories that EdgeFinder displays but our data sweep lacks: **AAII bull-bear spread (weekly),
   CBOE put-call ratio (daily), Geopolitical Risk index (daily)**. Added to `analysis/data_sweep.py`, they would run through
   `new_data_screen.py` against every plan piece (standing rule 'New data'). Needs the files downloaded from AAII / CBOE /
   matteoiacoviello.com (user's OK for the downloads).
2. A forward log of EdgeFinder's own live scores for our markets (composite bias, retail positioning, USD surprise reading),
   captured once a day from the dashboard; testable in 6-12 months. Only worth it if the user will keep the subscription.
Nothing in the dashboard is a strategy in itself.
