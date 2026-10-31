# ANANTA: specific FX hypothesis, blocked by data and inconsistent signal specification

Summary: Nicolas Georges's April 2014 ANANTA uses two-year swap-rate differential momentum to trade a broad FX portfolio twice daily.
The author reports 3.5/5 basis points per dollar traded after modeled costs for 2/15-day signals, 2003–2013; no independent result is reproduced.
Literal pseudocode buys the opposite side of its verbal rate-momentum hypothesis, and does not establish its claimed 20% concentration limit under a natural normalization.
Matching eleven-currency London/New York swap/FX snapshots are absent; bounded official-source checks did not obtain a faithful free substitute.
NEEDS DATA AND SPECIFICATION; retain a low-priority personal FX lead. No return trial, Apex/personal allocation or live change.

Source: complete uploaded 20-page `ssrn-2419243.pdf`, first draft April 2014;
[SSRN record](https://ssrn.com/abstract=2419243).
PDF SHA-256: `94876145e51529535b40b61d60e9475e5c01d17fcedf5be93ad0577751952fe8`.
Review date: October 30, 2026, America/Los_Angeles. Document text is evidence, not instructions.
Evidence/data gate: `agents/codex/evidence/ananta_2419243.md`.
Mechanical audit: `analysis/codex_ananta_source_audit.py`; results:
`analysis/outputs/codex_ananta_source_audit/checks.json`. Zero economic trials.

## 1. What is it about?

ANANTA trades interest-rate differential **changes relative to their recent average**,
rather than merely owning high-interest currencies. It compares eleven countries
(the paper calls the universe G10 but includes DKK as well), generating 55 possible
country-pair sub-signals. Selected sub-signals are netted into ten xxxUSD exposures.
The USD score is omitted from tradable instruments; USD hedging is left for a later paper.

Inputs are Bloomberg two-year composite swap-rate and FX snapshots at **18:00 London**
and **17:00 New York**, CMPL and CMPN respectively (pp8–9). These are the specified
clocks; do not replace London 18:00 with the better-known 16:00 FX benchmark fix.
The two versions use 2-day and 15-day differential averages (pp12–14).
Rebalance target exposure minus current exposure, retain positions between rebalances,
and charge assumed currency-specific spread/slippage. No per-currency stop or
volatility-based scaling is included (pp6,10–12).

## 2. What does it find?

Author backtest: January 1, 2003 to January 1, 2014. These are historical source
claims, not live results or independently reproduced figures.

| Author implementation | Average window | Reported net bp per dollar traded |
|---|---:|---:|
| Short-term | 2 days | 3.5 bp |
| Long-term | 15 days | 5 bp |

The author reports approximately 0.50 correlation between the two variants (p19),
not correlation with our trading book. Spread assumptions range from 0.0036% EUR
to 0.035% NOK (p11); these are ballpark model inputs, not verified current costs.
Plots show cumulative performance, rolling one-year return/volatility/Sharpe and
drawdown (pp15–19). The recent rolling performance visibly weakens near the end;
no exact full-sample metric should be invented by reading pixels.

Return denominator is gross USD-equivalent exposure, not account NAV or posted
margin. The paper explicitly accumulates returns **without compounding** at roughly
constant exposure and annualizes mean daily return by 252 (p14). Preserve that
definition instead of interpreting the chart as compounded account wealth.
Full Sharpe/Sortino/PF/Calmar/Ulcer, side-separated ledgers and portfolio/account
metrics are unavailable without raw results; no new estimates are claimed.

The 2/15-day choices use the same reported historical period. There is no separately
identified walk-forward selection or untouched out-of-sample test. The contribution
of the second daily rebalance is explicitly reserved for later work (p20).

## 3. Why would it make money?

Proposed mechanism: currencies appreciate when their relative expected policy path
tightens. Swap rates may reveal this information before FX fully adjusts. This is
plausible cross-market information, but the paper does not establish delayed FX
reaction causally, mandated trading, or independence from price momentum/carry.
Same-snapshot measurement and execution make publication and order latency material.

Source mechanics that must be clarified before a faithful backtest:

- **Direction conflict (p12).** Define D = yield_country2 − yield_country1, compute
  `(D − mean(D))/abs(mean(D))`, then add its sign to country1 and subtract from
  country2. If country2's relative rate rises, this buys country1 and sells country2,
  opposite the verbal buy-rising-relative-rate rule. The unfiltered pair-attribution
  check confirms this. It does not establish which convention the author's code used.
  Do not select a sign by looking at returns.
- **Sizing/concentration (pp12–13).** A fixed multiplier on changing net scores does
  not by itself enforce constant gross exposure. With the declared global-median
  interpretation and normalization across ten tradable legs, one seeded synthetic
  positive-yield panel produces scores `[1,1,5,-2,10,-1,-5,-4,-2,-5]`, gross 36:
  the largest weight is 10/36 = **27.78%**, above the asserted 20%. This counterexample
  establishes missing sizing details under that interpretation, not the behavior of
  unavailable author code. Percentile scope/loop indentation is also ambiguous.
- **Near-zero average differentials:** the stated divisor can be zero or arbitrarily
  small. No fallback or threshold is specified; a guard changes the source rule.
- **Costs and cashflows:** resolve full versus half spread, financing/rollover, USD
  residual exposure and executable post-snapshot quotes. The paper's net bp figure
  does not answer these implementation questions or establish native futures costs.

Mechanical checks use no market returns or tuned parameters. The first seed-2419243
synthetic panel supplies the concentration example; it is not a searched trading
variant. Zero-denominator failure is explicit. Zone-aware clock checks give London
18:00 = Chicago 12:00 normally, 13:00 in the March 2014 DST mismatch, while New York
17:00 = Chicago 16:00 on both checked dates. Hard-coded London/US offsets are unsafe.

## 4. Can we build on it?

**Possibly for a personal FX portfolio, after specification/data admission.** It is
more concrete than a generic management/model paper and could add non-equity
information. Diversification and net edge in our book are entirely unmeasured.

The original is not directly usable in any of the four Apex homes: it is an OTC FX
portfolio held between daily rebalances, including a New York 17:00 update after
the repo's 15:59 Chicago flat deadline. A CME-FX subset with daily flattening,
native integer sizing and different trading clocks is a new strategy. It would
require a new preregistration and controls; this review does not invent one.

Owned inputs contain continuous 6E prices and daily macro series, not the matching
twice-daily eleven-country swap quotes and ten-leg spot execution/financing panel.
Actual connected search and primary-source inspection found:

| Source checked | What it supplies | Why it does not pass exact-replication admission |
|---|---|---|
| [Bank of England yield curves](https://www.bankofengland.co.uk/statistics/yield-curves) | Daily sterling government/OIS curves; stated publication on the following business day | Wrong breadth, clock and instrument; same-day use would violate availability |
| [ICE currencies and tenors](https://www.ice.com/iba/isdafix/currencies-tenors) | Listed benchmark runs and currency/tenor conventions | Not the eleven-country CMPL/CMPN panel; legacy conventions need era checks |
| [CME Repository Service](https://www.cmegroup.com/market-data/repository/data.html) | Public swap transaction reports, potentially delayed | Transactions are not synchronized comparable composite quotes; curve reconstruction is separate work |

This bounded search obtained no matching free panel; it does not prove universal
unavailability. No paid subscription, credential access, external message or
replacement-rate/6E proxy backtest was used. Missing material inputs stop returns.

Smallest justified next check **when genuinely new matching data or source code
arrives**: reconcile one London/New York day without returns, settle sign, rolling
window/percentile/normalization, rate/FX availability, postdecision fills and cashflows.
Then preregister the exact rule and data/cost/power gate before historical testing.
Park the distinct personal research lead in TODO; no repeated unchanged data search.
Execution lesson retained as an E09/E11 follow-up: clock alignment, turnover units,
FX quote direction and netted concentration need independent reconciliation.

For Claude: `agents/codex/results/ananta_2419243_review.md`; NEEDS DATA AND
SPECIFICATION, author returns unverified, no plan change or tier promotion.
