# Hypotheses waiting on data, and where to get it (2026-11-01)

Prices are approximate, from memory as of 2026: **not checked live. Get a quote before buying.** Free first, always.

| # | Hypothesis (where it lives) | Data needed | Best source | Cost (approx) |
|---|---|---|---|---|
| 1 | **NG settlement window / bidweek** (lab Q011, priority 1) | Expiring NG contract 1-min, last 5 days before each expiry, 2018-2026 (our continuous file rolls too early) | **MultiCharts export** of each expiring month (NGF18 ... NGZ26) from your feed | **Free** (your data feed) |
| 2 | **LDF sized by leveraged-ETF dollar flow** (`agents/claude_evidence/1_letf_dollar_flow.md`, rank 1) | Daily AUM / shares outstanding + NAV for TQQQ, SQQQ, QLD, QID, SPXL, SPXS, UPRO, SPXU, 2018-2026 | Issuer history pages (ProShares, Direxion) for recent; **ETF shares-outstanding history**: Nasdaq Data Link / Stooq / yfinance (`sharesOutstanding` is spotty) | Free (patchy) to ~$30-50/mo for a clean ETF-fundamentals feed (e.g. EODHD) |
| 3 | **Real NYSE / Nasdaq closing auction imbalances** (evidence sheet rank 2; upgrades ES MOC) | Historical imbalance messages (15:50-16:00 ET), 2018-2026 | NYSE Order Imbalances (NYSE Data) / Nasdaq NOII; cheaper: **Databento** (pay per GB, Nasdaq TotalView/imbalance feeds) | Exchange direct: thousands. Databento: likely ~$100-500 for a few years of imbalance-only messages; **free $125 credit** on signup covers a pilot |
| 4 | **0DTE gamma-flip items** (WATCHLIST 1, 5, 15; FORCED_FLOWS 0DTE row) | Updated daily/1-min gamma (GEX) file, plus strike-level open interest for more | **Re-export `GEX_1min_<year>.csv`** from your current source; strike-level: SpotGamma / Unusual Whales / CBOE DataShop | Re-export free; SpotGamma ~$90-300/mo; CBOE DataShop OI history: hundreds+ |
| 5 | **WASDE on corn / soybeans** (lab Q008; MARKET_PROFILES review) | ZC / ZS 1-min 2018-2026; confirm Apex lists grains | **MultiCharts export** (same as NG); else FirstRate Data or Databento CME | Free via your feed; FirstRate ~$100-200 a bundle; Databento CME 1-min ~tens of $ |
| 6 | **Kusho FAR v9 / C03** (Codex review c03, WATCH / NEEDS DATA) | The author's native MultiCharts reports (.xlsx) + C03 settings | **The author / you** | Free |
| 7 | **EOS sized by VIX** (WATCHLIST 14) and **Overnight TickRSV/VIX** | Daily VIX (have), live VIX feed on the VPS | CBOE daily VIX CSV (`tools/vix_update.ps1`, already set up) | Free |

## Cheapest order to unblock
1. **Free, today:** NG expiring-month exports (#1, top-priority lab idea) and grains (#5) from MultiCharts; GEX re-export (#4).
2. **Free/cheap:** LETF shares outstanding (#2), try free sources first; buy only if they have gaps.
3. **Paid, quote first:** auction imbalances (#3) via the Databento free credit as a pilot before any purchase.

Saving money is making money: nothing paid until a free pilot shows the effect is worth chasing.
