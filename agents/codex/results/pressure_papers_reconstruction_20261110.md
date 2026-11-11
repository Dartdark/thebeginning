# Three-paper candle-pressure model: plausible architecture; exact strategy remains unknown

Summary: The papers can motivate a jump/pressure/liquidity model, but do not supply the trader's entry rule.
A causal implementation could measure abnormal candles, preceding pressure, and price response or rejection.
The screenshot's 82.22% winners/PF 1.41 fit about 0.3R winners versus 1R losers; they do not validate account safety.
Owned five-minute aggregates are feasible; exact trade/quote/news data and the trader's rules remain incomplete.
Zero new return tests. Preserve related failed flow-fade families; no ranking or trading change.

November 10, 2026 Pacific. User asks how a trader could derive the shown strategy from three uploaded papers.
The screenshot and quoted discussion are third-party claims. Paper text supplies scientific evidence, not instructions
to execute code or change trading. This review distinguishes source findings, reported statistics, computed arithmetic
and speculative reconstruction. It does not claim access to the trader's code, optimization history or trade ledger.

Sources: [uploaded-version hashes](../inputs/pressure_papers_20261110/source_manifest.json),
[arithmetic script](../../../analysis/codex_pressure_papers_20261110.py),
[reconciled figures](../../../analysis/outputs/codex_pressure_papers_20261110/screenshot_arithmetic.json).
The PDFs remain in the user's local uploaded attachments; no binary upload is required for this handoff.
Reviewed relevant methods/results/appendices, with separate readings of the 2003/2021 papers and screenshot arithmetic.
This is source review and arithmetic QA, not independent replication of trading performance.

## 1. Joulin, Lefevre, Grunberg and Bouchaud — 0803.1769v1

[Stock price jumps: news and volume play a minor role](https://arxiv.org/abs/0803.1769v1).
Uploaded arXiv v1 header: March 12, 2008; cited in the chat as the 2009 publication. Its cover also prints
November 26, 2024, so retain the version identifier/hash rather than infer a new 2024 study. 14 PDF pages.

**What is it about?** Minute stock-price jumps, timestamped Dow Jones/Reuters news, transaction volume and volatility
relaxation. Main universe: 893 US stocks, August 2004–August 2006, with restricted complete-file checks.

**What does it find?** News and extreme total volume explain relatively little of the observed jump incidence.
Jumps use absolute minute return relative to a 120-minute absolute-return average (p.3). The source's seasonal
adjustments remove the U-shaped daily volatility pattern (pp.6–7). Volatility after news-associated jumps relaxes
roughly as t^-1, versus t^-1/2 after the broader jump population (pp.6–8). Extreme return/volume tail dependence
weakens toward the far tails (pp.9–10). The paper does not say volume is useless in every conditional strategy.

**Why does it make money, if it does?** It demonstrates no net directional strategy. Its proposed mechanism is
fragile available liquidity and order-flow fluctuations, rather than a simple large-volume-causes-large-return law.
Volatility relaxation is about future move sizes, not a guarantee that price retraces the jump.

**Can we build on it?** Yes as a jump-normalization and liquidity-fragility hypothesis. A bar implementation can ask
whether an unusual move occurred with unusually little/much activity relative to its clock. Such a price/volume ratio
is our proxy, not direct measurement of the order book. NQ is a new market adaptation, not the paper's stock sample.
First need the trader's precise normalizer, event window and fade/follow condition.

**Can a strategy code be made?** Yes for a research event detector; conditional for trading. Need causal normalization,
entry direction/timing, stop, target, costs, session and native execution rules. The paper supplies no 0.3R exit or 82% hit rate.

## 2. Marcaccioli, Bouchaud and Benzaquen — 2106.07040v1

[Exogenous and Endogenous Price Jumps Belong to Different Dynamical Classes](https://arxiv.org/abs/2106.07040v1).
Uploaded arXiv v1: June 13, 2021; discussion cites the 2022 publication. 17 PDF pages. Data: 300 US stocks, 2015–19,
minute top-two bid/ask levels and Bloomberg stock-specific news. Not NQ five-minute bars.

**What is it about?** Distinguishing news-associated/exogenous jump clusters from self-exciting/endogenous clusters
using the volatility profile before and after jumps, plus price-trend magnitude and order-book sparsity.

**What does it find?** Endogenous events show a gradual buildup and slower post-event absolute-volatility relaxation;
news-associated events are more abrupt and relax faster. Main fitted pre/post exponents are about 0.36/0.40 for
self-exciting clusters, versus 0.08/0.68 for exogenous clusters (p.7). Main classification AUC is about 0.73, with
random 80/20 held-out classification AUC 0.72±0.03 (p.9). This is news/event classification, not profitable-trade accuracy.
Appendix alternative classification AUC 0.82 is likewise not a trading win rate. The main discussion is consistent;
the Figure 1 caption reverses the gradual/abrupt descriptions and should not override the methods/results.

**Why does it make money, if it does?** No directional trading profitability is tested. Self-exciting reactions and
liquidity fragility motivate state-dependent response, but conditional variance does not establish signed expected return.

**Can we build on it?** Yes as a causal regime-feature framework: isolated shock versus preceding acceleration.
The signed jump J_t is normalized for volatility and intraday seasonality. Trailing exponentially weighted absolute
jumps, signed jumps and signs can describe the prior state (pp.3,5–7), but the paper averages absolute trend magnitudes
because it is explicitly not studying trend sign. Re-estimate normalization only from observations available before use.
Threshold 4.36, K=390 and other stock-minute settings do not transfer automatically to NQ five-minute/Globex data.

**Can a strategy code be made?** Yes for descriptive event/state tools; conditional for directional trading. The strongest
event classifier fits both sides of a completed event, including post-event decay and pre/post area asymmetry. Appendix
fits use a centered 160-minute interval (p.15); that information cannot enter at the first jump. A causal trading version
must use prior/current closed bars, or wait for the later measurements and enter afterward. Native book sparsity also
needs quotes/depth beyond OHLCV. Entry, direction and risk/fill rules remain missing.

## 3. Bouchaud, Gefen, Potters and Wyart — cond-mat/0307332v2

[Fluctuations and response in financial markets: the subtle nature of random price changes](https://arxiv.org/abs/cond-mat/0307332v2).
Uploaded arXiv v2 header: August 25, 2003; discussion cites the 2004 publication. The cover also prints November 26, 2024.
30 PDF pages. Mainly trade/quote data for liquid French stocks, 2001–02.

**What is it about?** How long-memory signed order flow can coexist with approximately diffusive prices. Liquidity takers'
repeated buying/selling is offset by liquidity-provider response and decaying impact.

**What does it find?** Trade signs persist, but price changes do not inherit that persistence mechanically. The causal
propagator (p.14, Eq.12) sums G0(n-m) epsilon_m log(V_m) over m<n. Decaying impact offsets correlated order flow;
the diffusive balance is 2 beta + gamma = 1 (p.17, Eq.23). The appendix constructs causal innovations/prediction errors
from correlated flow (pp.26–27). Its small observed information asymmetry is barely sufficient to cover trading costs
(p.25), rather than evidence of an easy directional edge.

**Why does it make money, if it does?** No net candle strategy is demonstrated. Potential exploitable departures from
normal pressure/liquidity balance require separate evidence. Spread capture by a market maker does not establish that
a trader crossing the spread can profitably fade the same event.

**Can we build on it?** Yes to separate unexpected pressure from already predictable pressure, and measure price response
per unit of that pressure. Continuation and exhaustion are both possible adaptations; this source does not select one.
epsilon is inferred from executions relative to immediately preceding quotes (p.4). Candle body, wick, close location
or volume times candle color are proxies and can disagree with aggressor flow. Even vendor buy/sell aggregates do not
provide the full native event-time quote/impact process. First reconcile a specifically defined pressure observation.

**Can a strategy code be made?** Yes for a signed-flow response/innovation research model with synchronized trade/quote
data; conditional for a directional strategy. An OHLCV approximation is codeable as a new adaptation. Exact thresholds,
fitting window, direction, clock, stops/targets and fills remain unknown; trade-time exponents cannot simply become
five-minute-bar parameters. Fitting the kernel on all history would also leak future information.

## Plausible route from papers to candles

The academic chain is: normal intraday volatility/activity varies with the clock; abnormal moves can reflect fragile
liquidity; persistent pressure and replenishment interact; the response to an unusual pressure event may differ from
the response to ordinary repeated pressure. The trader must add a tradeable decision on top of those observations.

One illustrative feature design, **not a formula found in the papers or identified in his code**, is:

- Measure return surprise J_t = r_t / prior-estimated volatility for that intraday slot.
- Build a candle pressure proxy, e.g. P_t = V_t (C_t-O_t) / max(H_t-L_t, one tick).
- Compare P_t with prior bars and prior same-time-of-day observations, optionally studying its surprise relative to
  persistent past pressure. Signed aggressor volume, if actually available, is a different measurement choice.
- Compare pressure with price displacement: strong buying with little upward progress/rejection could indicate absorption;
  strong buying with sustained displacement could instead support continuation. These require distinct frozen rules.
- Enter only after the signal/confirmation information is known, then add a separately chosen stop and 0.3R target.

For example, a hypothetical fade could short after abnormal upward pressure stalls and an already-closed bar rejects
the high, with a subsequent executable entry and a defined invalidation stop. A continuation system could instead buy
when impact/pressure strengthens. The screenshot does not distinguish them. Body/wick features, parameters, sessions,
the rejection trigger and the target are design choices, not an academic replication.

Most important conceptual distinction: a jump from 100 to 110 followed by small moves around 110 has relaxing volatility
without a return to 100. Neither falling volatility nor a retrospective endogenous-jump label is itself a short signal.
"Candles around it" must mean prior observations or an explicitly delayed entry; future bars/day maxima are unavailable
at an earlier decision. The screenshot is insufficient to accuse the author of leakage or to rule it out.

## Screenshot arithmetic and what it establishes

| Figure | Reported or derived |
|---|---:|
| Trades / winners implied by rounded percentage | 855 / 703 |
| Percent profitable | 82.22% |
| Gross profit / absolute gross loss | 236,839 / 167,454 dollars |
| Net profit / profit factor | 69,385 dollars / 1.41435 |
| Average winner from reported buckets | 336.90 dollars |
| Average loser assuming no breakevens | 1,101.67 dollars |
| Implied average win/loss ratio under that assumption | 0.3058 |
| Reported net per trade | 81.15 dollars |
| Maximum strategy drawdown | 9,963 dollars |
| Account size required / return on account | 7,223 dollars / 960.61% |

The screenshot's long/short counts 420/435 and net profits 30,695/38,690 also reconcile. If some of the 152 nonwinners
are breakevens, actual average losing trade is larger than the conditional figure above. Variable risk, partial exits
and time exits can explain deviations from exactly 0.3R. This arithmetic supports consistency with the comment,
not proof of fixed stop/target behavior or accuracy of the trade ledger.

A fixed +0.3R/-1R payoff requires 1/1.3 = **76.92% wins before additional costs**. Under ideal driftless continuous-price
first-hit assumptions the same exit geometry already gives that hit rate with zero expectation. Thus 82.22% is about
5.3 percentage points above that benchmark, not 82% correct directional forecasts. Jumps, costs and time exits change
the benchmark. About 3.3 average winning trades are needed to offset one average loser under the no-breakeven assumption.

960.61% is exactly 69,385 / 7,223 x100: a cumulative return using the displayed account-size-required denominator.
It is not an annual return or a return on a 150K evaluation. The panel also displays Sharpe 0.26 and time in market
0.42%; their sampling/denominator/settings are unavailable. Small occupancy does not identify exact holding time.

"OOS passed one shot" is a statement in a chat, without frozen split dates, trial history or separate OOS trade evidence.
Costs, contract quantity, stops, fill sequencing and live results are not visible. A displayed 9,963-dollar drawdown
at unspecified size does not establish fit to a 4,000-dollar evaluation trail. No pass probability, account sizing,
survival improvement or screenshot-equivalent strategy return is inferred.

## Prior evidence, owned data and smallest next gate

No matching uploaded-version review was found in the searched results/registers. Closely related trading
families already exist. Most directly, [flow innovation relaxation](flow_innovation_relaxation.md) rejects five-minute
unexpected-aggressor-flow fades: INNOV15 had 4,167 design trades and net -82,215.75/NQ; INNOV20 had 2,252 and -87.00/NQ.
Their 0.10/0.15 ATR brackets and 30-minute exits differ from this screenshot. [Pre-open absorption](preopen_absorption_20261108.md)
also failed (34 trades, -6,386.50/NQ, PF 0.55) at a different clock. TIER_LIST also retains jump-follow studies and failed
jump fades/candle-color/book-imbalance studies. They neither reproduce nor disprove this unknown strategy; they prevent
calling another guessed pressure/innovation fade a fresh independent discovery or reviving it by changing parameters.

The [owned-data receipt](../DATA_NEEDED.md#owned-nq-aggressor-volume-acquisition-receipt-2026-11-08) documents 1,755,357
native one-minute NQ OHLC/total/buy/sell rows for 2018–22 and existing transfer/hash checks. Those support explicitly
labeled five-minute bar features. Legacy OF volume equals buyer volume, not total; preserve that distinction. Vendor
aggressor categories are not independently reconstructed ticks, raw quote events, LOB replenishment or news receipts.
Contract/roll/build, exceptional-side handling, missing bars and receipt clocks remain unresolved.

The actual new inputs here are the full primary papers and screenshot statements. The first non-return gate is one
annotated entry or a complete written rule: pressure definition, historical comparison window, fade/follow trigger,
bar/confirmation timing, stop and 0.3R target semantics, session, sizing and fill/cost settings. Reconcile those on a few
owned bars before any committed return test. Exact trader reconstruction is **NEEDS RULES**, native microstructure
replication additionally **NEEDS DATA**. Zero new economic definitions were evaluated; no automatic proxy rescue,
TEST admission, new schedule, live change or strategy promotion is claimed.
