# Agricultural cointegration pairs: DON'T TEST

Summary: Source review finds months-long trades, only two/three completed trading-period
trades per selected pair, ignored costs and inconsistent direction specifications.
No demonstrated economic convergence mechanism or credible executable accounting.
Neither an Apex strategy nor a sufficiently supported personal-account candidate.

Source: Cüneyt Ungever (2015), *Pairs Trading to the Commodities Futures Market
Using Cointegration Method*, SSRN2896370, printed pp.25–38.
Owned PDF and hash: `agents/codex/inputs/ssrn2896370/`.
Review: `agents/codex/results/agri_cointegration_ssrn2896370.md`.
Return trials: zero. This is a source/evidence gate, not a failed empirical replication.

## 1. Who trades, and what causes the trade?

The proposed trader fades a fitted log-price residual. The paper explicitly does
not identify the source of profitability (p.34). No common delivery, substitution,
mandated rebalance or identifiable forced trader connects cotton with coffee or
live cattle. Statistical cointegration alone does not establish that link.

## 2. Direction, size and timing known before entry

Proposed signal: residual crosses ±1.5 standard deviations; close on return to
mean. Daily closes, formation 2004-12-01–2011-12-01, trading
2011-12-02–2015-05-01. A close-based signal must fill after its availability;
the paper does not establish an executable decision-to-fill clock. Direction
prose and profit equations disagree. It states $100,000 long/short position
values but does not supply a reproducible native-contract hedge or trade ledger.
No forced-flow size/volume estimate is available.

## 3. Transmission to traded contracts

The proposed assets are commodity futures themselves. There is no claimed direct
NQ/ES flow, nor evidence permitting a transfer to those instruments. Personal
commodity trading is conceptually possible, but requires its own evidence and
contract-level risk. It is not rejected solely for being outside index futures.

## 4. New information and data feasibility

Only historical prices and fitted residuals; no independent flow input. Source
uses Bloomberg rolled daily futures, forward-fills holiday closes, and gives a
roll rule without a complete adjustment/contract ledger. Local filename search
found no cotton, coffee or live-cattle price histories in `data/` or Codex inputs.
No free substitute was acquired: the source-quality and mechanism gates already
fail; missing data is not the sole reason to stop. Other tickers, ETFs or price
ratios would define a different experiment rather than reproduce this source.

## 5. Costs and actual intraday gaps

Source ignores transaction costs (p.27); both legs and every roll must incur their
actual costs. Holds average 159/142 days in the trading sample, with no specified
stop or maximum divergence. This violates Apex's daily flatten requirement and
does not occupy an intraday plan gap. An intraday conversion would change the
strategy. No positive executable move-versus-cost estimate can be established.

## 6. Power before returns

Only two coffee–cotton and three cotton–cattle completed trades are reported in
the 859-observation trading period. No per-trade ledger or variance estimate is
supplied. Daily marks of the same multi-month position are not independent trade
opportunities. We cannot justify a 2018–22 opportunity count or power calculation
from these observations; treating the author's headline annualizations as evidence
of statistical power would be circular.

## 7. Already tested and falsifiers

No exact SSRN2896370 hit found. Related existing TIER_LIST negatives include the
*Beta from A to Z* NQ–ES/NQ–YM pairs recipe, signature-filtered intraday pairs,
and Asian ADR/SPY overnight pairs. These do not disprove agricultural pairs;
they prevent transferring a generic pairs claim to already-rejected index rules.
Refutation would include unstable past-only coefficients, no gross convergence,
negative net execution, or no place against BASE/ADD/REPLACE/EMPTY. Those tests
are not earned by the current evidence gate.

## 8. Failure and diversification

Supply/weather/disease shocks, delivery cycles and persistent relative trends can
break statistical relationships and cluster losses. A two-leg label establishes
neither market neutrality nor a hedge arriving before the account floor is touched.
Marketable two-leg execution adds asynchronous fills/roll risk; order types are
unspecified in the source. Cotton is common to both proposed pairs, so two pairs
are not two independent diversifiers. Joint losses with the personal book are
unmeasured. No stop, native integer size or account protection is verified.

## Decision and next gate

**DON'T TEST this source-defined strategy.** No economic-return trials, placement
bench, PowerLanguage, tier change or promising-candidate queue entry. Reconsider
only with an unambiguous direction/hedge/return specification, dated contract
ledger and materially stronger independent net evidence. Preserve the useful
execution lesson separately in EXECUTION_REFERENCES.
