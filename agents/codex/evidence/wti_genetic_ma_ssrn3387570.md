# WTI genetic MA: NEEDS SOURCE SPECIFICATION; no return test admitted

Summary: Chronological two-month train/one-month test is a useful design feature,
but ten cost-unclear test months and an unresolved futures ledger do not establish
a robust new strategy. Required source settings are missing; do not invent them
or run an independent genetic search and call it this paper's reproduction.

Source: Aragón, Mejía & Zapata (2018), SSRN3387570, DOI10.18601/17941113.n15.05.
PDF/hash: `agents/codex/inputs/ssrn3387570/`.
Review: `agents/codex/results/wti_genetic_ma_ssrn3387570.md`.
Return trials: **0**. Recalculation of published table statistics is a source audit.

## 1. Mechanism

Trend continuation inferred from price-only simple-moving-average crosses.
No forced participant, supply/hedging deadline or source-specific economic
explanation for incremental profit. Personal-account trend research is allowed,
but this short source example supplies neither broad net evidence nor a validated
new implementation. Genetic search is optimization, not an economic mechanism.

## 2. Direction, size and clock

Trade long on short-MA crossing above long-MA; short on the reverse, with crosses
also closing positions. Source formula averages preceding closes. Table 2 swaps
the m1/m2 short/long naming used in the prose/Figure 7. The decision/fill price,
reversal versus close-only details, session/time zone, warmup/month-boundary
handling, random seed and exact implementation are not fully specified.
Source calls quantity 2,000 WTI futures contracts on $2m; its printed P&L formula
does not show a contract multiplier. Signed native quantities remain unresolved.

## 3. Instrument fit

Bloomberg generic first-position WTI, 15-minute closes, August 2017–July 2018.
No NQ/ES transmission is proposed. CL could diversify a portfolio, but this source
does not measure contribution or establish daily flattening for Apex.

## 4. Data and missing inputs

Owned CL minute files include the source period and later dates; price data are
not the primary blocker. Exact Bloomberg splice/roll/session conventions and
source Python/Go code, position ledger, fees and execution clock are missing.
No source code link was found in the uploaded article. Searching new settings or
substituting our conventions would define a new strategy, not exact replication.
Do not acquire more prices or invent source settings to bypass this gate.

## 5. Costs and occupancy

No disclosed commission, spread/slippage, cost bridge or roll cashflow is applied
to the displayed strategy results. SMA crosses do not ensure flat by 15:59 CT;
adding a flatten/stop changes the strategy and needs a separate protocol.
No gross edge per trade, native micro size or actual plan gap can be established
without a trade ledger. No account bench is earned before source reconciliation.

## 6. Power and multiple testing

Ten test months, seven positive; mean +1.071%, sample SD 1.973% from rounded Table 2.
An illustrative unadjusted independent-month mean t is only about 1.72, with 95%
mean interval crossing zero. This is not independent replication or a valid
search-adjusted inference. GA population 60, 1,000 generations each rolling run;
actual unique fitness evaluations/restarts are unknown and must not count as a
single searched pair. We have no per-trade sample/power estimate.

## 7. Existing work and falsifiers

No exact SSRN hit found. Related repo negatives include Carver/EWMAC MA crosses,
MACD/indicator families, and MaxAI's RL/GA NQ black box; these do not directly
disprove CL's exact rule. A fair future experiment would need a frozen fixed-MA
and matched passive/trend baseline, design-only selection, native costs, multiple
regimes, trial accounting and untouched subsequent data. Failure does not justify
optimizing the windows again on observed losses.

## 8. Failure and diversification

Whipsaws, persistent adverse trends/roll jumps, changing volatility and heavy
turnover can dominate a selected MA pair. Missing stops, intraday loss paths,
margin and native contract units prevent account survival or hedge claims.
No joint-loss evidence or offset before an Apex floor touch exists here.

## Decision

**NEEDS SOURCE SPECIFICATION; no new return test.** This is a completed review,
not a promising-strategy queue nomination: the current evidence does not justify
a replication or GA search budget. Reconsider only with unambiguous code/clocks,
native trade/cost/roll ledger and materially stronger independent net evidence.
No parameter invention, new trial, portfolio change, live change or tier.
