# 6E cross-asset package: WATCH — useful diversification hypothesis, unverified implementation

Summary: Worth a bounded personal-account replication; no demonstrated placement yet.
Reported Sharpe 1.63 and NQ correlation +0.06 are author claims, not independently verified.
First audit synchronized clocks, integer M6E sizing, native costs and actual contract rolls.
The proposed daily-only MultiCharts chart cannot reproduce the intraday euro-reaction branch.
Original Python and reconciled trade/daily ledgers are the next prerequisite; no returns computed here.

Plan: source/evidence review only, no strategy return preregistration or trial yet.
Script: `analysis/codex_six_e_claims_audit.py`.
Output: `analysis/outputs/codex_six_e_cross_asset_20261027/claims_audit.json`.
Evidence: `agents/codex/evidence/six_e_cross_asset_20261027.md`. New return trials: **0**.
Source archive: `agents/codex/inputs/six_e_cross_asset_20261027/research_note.txt`.
Current repository snapshot: Claude `6416de2dd39782eb4a43bd665c866409da4deb70`.

## Rule and evidence supplied

The six components are macro-price momentum, macro-conditioned RSI/weekly entries,
and next-day ZN/euro-reaction, equity and gold shock follows. They trade 6E/M6E
from a 16:00 ET decision, holding one or multiple days. This is personal-account
research. A matching six-leg implementation/ledger was not found in the inspected
repository tree. The note and screenshot alone cannot verify any return claim.

The research direction is useful: another market, both directions and a longer
horizon may diversify the equity-heavy book. Low correlation is more valuable
than finding another opening-hour NQ breakout, if it survives execution and a
comparison against the **current** personal book. It does not make this S rank.

## Highest-priority checks and improvements

### 1. Prove the information and execution clocks

Build a table for every series: timezone/session, bar interval, event time,
available_at, decision time and first executable fill. Align all markets as-of
16:00 America/New_York, with holiday/DST handling. A default full-session daily
bar may contain prices after the proposed decision; settlement and last-trade
close are not interchangeable. This is a potential issue, not a confirmed leak.
Compute the signal, then use a later executable price; observing the close does
not guarantee obtaining that close. The one-day-late Macro result is reassuring
about that component's delay sensitivity but does not certify other legs.

16:00 ET is a custom cut: CME's normal FX session ends at 16:00 CT = 17:00 ET.
The proposed daily Data1 M6E / Data2–5 ZN, CL, ES, GC chart cannot itself compute
the 08:29–09:30 ET euro reaction. Use the required intraday series or a separately
timestamped input, with faithful timing. No replacement proxy is silently allowed.
A single portfolio signal must also retain each leg's virtual position/exit state
and reconcile its aggregate target with broker net quantity.

### 2. Make the M6E sizing and cost bridge executable

[CME's current product guide](https://www.cmegroup.com/markets/fx/fx-product-guide)
specifies M6E as EUR 12,500 with a 0.0001 price tick ($1.25).
[Full 6E](https://www.cmegroup.com/markets/fx/g10/euro-fx/specs) has a 0.00005 tick.
Consequently a scaled 6E half-pip print is not automatically an executable M6E price.
One native adverse tick per side is **$2.50 per M6E round trip**, before any fees
not already included. That is a stress illustration, not measured slippage.

Explain whether $1.20 means per filled contract side, full round trip, or all-in
execution. Charge actual unit turnover: a +2 to −2 reversal exchanges four
contracts. Include vol-target rebalances and each roll. Resolve spread versus
slippage accounting rather than double charging the same friction.

The 5% annual vol target and 1.5x cap need a capital/notional reference. A two-M6E
label can hide fractional targets after averaging signs and vol scaling. Show
actual signed integer quantities, the rounding rule, idle days, net/gross exposure
and margin use. Do not assume fractional exposure earned by a unit backtest is
available at the proposed small account size.

### 3. Reconcile rolls and daily accounting before portfolio claims

Preserve individual-contract IDs, roll decisions known at the time, executable
old/new prices, commissions and slippage. Back-adjusted prices are useful signal
inputs; they are not a complete cash/roll ledger. Audit predictor rolls too: a
ZN/CL/ES/GC stitch jump could become a false shock. Specify treatment of negative
crude prices, percentage returns and volatility in 2020. Reconcile daily marked
P&L to completed trades plus open P&L and explicit rolls/fees, to the cent.

Local 6E headers/first-last timestamps were inspected without reading price
values. They have no contract-ID field; the 2017 export begins December 1.
This is not enough by itself to establish the author's back-adjusted individual
contracts or a full 63-session January warm-up. Actual source history and first
valid signal dates can resolve it; the plot's initial flat period is not an error.

### 4. Tighten the statistical interpretation

- **A failed ML model does not show that the selected rules avoided data mining.**
  Count the failed own-6E families, cross-asset signs, lookbacks, thresholds,
  holding periods, leg selections and package weights. They are part of the search.
- **Annual refits are not independent validation if the structure used later data.**
  A genuine frozen-2018–21 design evaluated without redesign afterward is useful;
  provide its timestamped definition, exact fit/label boundaries and per-fold results.
  Already-seen 2023+ is historical evidence, not a fresh holdout for new decisions.
- **Positive parameter plateaus are encouraging but correlated.** Twenty nearby
  threshold/hold variants do not provide twenty independent replications.
- **Use stronger matched controls.** Preserve event counts, calendar/volatility
  regimes, side mix, holds and costs; randomize trigger/date or sign appropriately.
  Compare shock follow with EUR's own momentum at the same entry/exit and control
  common-dollar exposure. Ensure random signal shifts do not wrap future signals
  into a supposed causal historical rule. Correct for the selection procedure.
- **The own-euro reaction branch is an own-price signal.** Separate it from ZN
  events and report their overlap/priority. “Every strategy uses other markets”
  is inaccurate for this branch and for the RSI/weekly timing rules.

On the author's reported evidence, Macro Momentum, Macro-Shock and Gold-Shock
deserve attention first. RSI's recent Sharpe 0.05 and Stock-Shock's walk-forward
0.31 justify scrutiny. Keep the full package as the frozen reference; preregister
any ablations and do not turn a hindsight deletion into a newly validated rule.
The literature is motivation; fixed ES signs need their own evidence at each horizon.

### 5. Measure the contribution to the actual personal portfolio

The current documented personal book has 19 pieces, including multi-day and
overnight strategies; it is not merely the intraday NQ comparator in this note.
Use common dates and marked-to-market accounting, then compare the frozen package
as an addition, an ex-ante replacement and against an empty slot. Assess total
profit, p95 drawdown, capital/margin, stressed costs, and joint worst days/weeks/
months. A +0.06 average correlation is useful preliminary information, not proof
of tail protection. All six legs trade the same EUR/USD risk, and shock triggers
can reflect one common dollar/rates event even with low average pair correlations.
The observed $1,840 drawdown is not a p95 future-drawdown capital requirement.

## Answers to the note's three feedback questions

1. **Live M6E fills:** no firsthand fills or verified live execution sample was
   supplied, so this review cannot report live experience. Log native M6E bid/ask,
   last trade, order time, quantity and fill around the fixed decision. Compare
   arrival-mid implementation shortfall, quoted spread and native-tick stresses.
   Paper fills can diagnose availability but do not establish live queue performance.
   Liquid 6E history alone does not validate the quoted M6E cost.
2. **Bund / Euro Stoxx:** FGBL is a sensible *new* rates input because US yields
   alone omit the euro side. Compare synchronized, duration/vol-normalized bond
   signals or comparable yields, not raw ZN minus Bund prices. FESX versus ES is
   another hypothesis, with separate trial accounting and common-clock data.
   [Eurex](https://www.eurex.com/ex-en/markets/idx/stx/euro-stoxx-50-derivatives/products/EURO-STOXX-50-Index-Futures-34652)
   distinguishes settlement and session close. [ECB daily yield curves](https://data.ecb.europa.eu/methodology/yield-curves)
   offer a public proxy route, not a Bund-contract history or automatically a
   German/US differential. Verify source publication timing/vintages; do not
   presume every daily mirror is available same day.
3. **6J / 6B / 6A basket:** a useful transfer experiment once the EUR mechanics
   are verified. Freeze one rule and the complete currency set before returns;
   normalize quotes and risk, retain failures and avoid per-currency tuning.
   These contracts share a USD leg, so assess aggregate dollar exposure and
   crisis co-losses. The EUR oil/risk signs need not apply mechanically to yen,
   sterling and Australian dollar. No evidence of successful transfer is supplied.

## Literature: what it supports

- [Dahlquist & Hasseltoft, 2020](https://research.hhs.se/esploro/outputs/journalArticle/Economic-momentum-and-currency-returns/991001480359106056)
  study trends in economic-activity/inflation fundamentals. This package uses
  traded-market prices; it is inspired by the paper, not a direct replication.
- [Pitkäjärvi, Suominen & Vaittinen, 2020](https://research.aalto.fi/en/publications/cross-asset-signals-and-time-series-momentum/)
  document bond/equity predictability. The abstract does not establish these
  one-day EUR shock thresholds or the chosen macro signs.
- [Evans & Lyons, 2002](https://www.journals.uchicago.edu/doi/10.1086/324391)
  motivate order flow's role in FX prices; persistent impact is different from
  proving a profitable delayed follow after the shock is publicly observed.
- [Ranaldo & Söderlind's published abstract](https://academic.oup.com/rof/article-abstract/14/3/385/1592162)
  emphasizes CHF/JPY safe-haven behavior. It cannot alone justify a uniform EUR
  risk-on sign, nor the same directions across an FX basket.

These are limited source/abstract checks, not full independent replications of
the papers. Cite them at the scope they actually establish.

## Arithmetic, account scope and next action

The nine supplied annual amounts sum to **$23,595**; 2022 contributes **29.2%**.
The weighted rounded per-leg annual figures total **$2,670**, consistent with
the reported ~$2,680 rounding. No obvious aggregate arithmetic contradiction was
found; this does not validate return generation, Sharpe or drawdown.
The audit script also records approximate event-count/power illustrations.

| Destination | Status |
|---|---|
| 50K evaluation | Outside the supplied multi-day specification; no bench or rule conversion |
| 150K evaluation | Outside the supplied multi-day specification; no bench or rule conversion |
| 50K funded | Outside the supplied multi-day specification; no bench or rule conversion |
| 150K funded | Outside the supplied multi-day specification; no bench or rule conversion |
| Current personal portfolio | **NEEDS DATA**: no reproduced edge or marginal contribution yet |

Next prerequisite: original Python, settings/data provenance and a ledger with
signal/decision/order/fill times, contract, side, integer quantity, entry/exit,
fees/rolls, plus daily marked P&L by leg and package. Audit the existing result
before building a faithful MC port or adding data/parameters. Any new return
study gets its own committed plan and gates. No strategies were backtested,
ranked, promoted or changed by this review.

For Claude: `agents/codex/results/six_e_cross_asset_review_20261027.md`.
