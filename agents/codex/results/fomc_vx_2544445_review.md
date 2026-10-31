# SSRN2544445: specific FOMC-volatility lead; NEEDS DATA AND SPECIFICATION

Summary: Donninger proposes shorting nearby VX before scheduled FOMC decisions and covering35minutes after the announcement.
The author reports34selected2010–14trades,+28.68%total return,Sharpe1.085and0.7%drawdown; none is independently reproduced.
This is worth retaining as a conditional personal-research lead, but exact contract/clock definitions and intraday dated VX inputs are missing.
Public/provider checks found matching product descriptions; sample attempts did not yield an admitted price/quote panel.
No spot-VIX, daily-VX or ES proxy backtest; no plan placement or return trial.

Source: Chrilly Donninger, *Trading the patience of Mrs. Yellen. A short VIX-Futures strategy for FOMC announcement days*, December2014, Revision1 January5,2015. [SSRN](https://ssrn.com/abstract=2544445); [archived user upload](../inputs/papers/ssrn-2544445.pdf). All four pages read and charts on pages2–4rendered. [Evidence gate](../evidence/fomc_vx_2544445.md), [actual acquisition/settings record](../inputs/fomc_vx_2544445/data_gate.md), [source-unit audit](../../../analysis/outputs/codex_ssrn2544445_review/source_audit.json), [audit script](../../../analysis/codex_ssrn2544445_audit.py). The audit checks source arithmetic/metadata only, not economic returns.

## 1. What is it about?

A scheduled-event short-volatility strategy. At11:00on a scheduled FOMC announcement day, short a nearby VIX futures contract, skip if its price exceeds25, use a5%adverse-price stop, and cover35minutes after the actual announcement. The paper discusses historically different release times, including12:30ETand approximately14:00/14:15ETeras. The intended civil timezone, receipt/fill convention and treatment of delayed releases are not fully specified.

Baseline quantity is `−floor(equity × 0.60 / (VX price × 1000))`. Initial capital is$500,000; atVX20this gives15shortVX. The source assumes$60round-trip cost perVX, comprising$50spread and$10fees. It also compares longES, double leverage and price-independent point-exposure sizing. Those are source-explored alternatives, not independent confirmations.

## 2. What does it find?

| Source-selected strategy,2010–14 | Cumulative return | Sharpe | Reported maximum drawdown |
| --- | ---: | ---: | ---: |
| ShortVX, baseline60%sizing | +28.68% | 1.085 | 0.7% |
| LongES comparator, source6×factor | +22.90% | 0.821 | 2.6% |

The author says34trades were taken and6omitted by the price filter; the5%stop never triggered. These are author claims from a small selected history without a trade ledger, by-year/side tables, modern validation or native-fill reconciliation. **28.68%is a five-year total, not an annual return or win rate**; a nominal exactly-five-year compound conversion is about5.17%a year, without claiming exact sample-date annualization.

The source's more favorable sizing results were chosen after comparing outcomes. Entry time, exit time, price/maturity filters and leverage were also examined; total prior trial count is unknown. Repeated timing variants are not independent replications. The ES quantity multiplier was chosen to produce comparable return magnitude, not a prespecified equal-risk allocation or a hedge.

The cited academic event study is distinct. Its [AUT repository abstract](https://openrepository.aut.ac.nz/items/d00cffe2-0802-401c-a0c5-27890e64f442) reports VIX/VX falling for roughly45minutes after announcements and a separate full-day strategy. That corroborates a research question; this task did not independently audit its full PDF, and it does not validate Donninger's exact filters/sizing or today's performance.

### Material specification findings

- **Hidden maturity setting:** all three chart interfaces show`min-Maturity=5`. The prose only says“most nearby.” Whether5means calendar or trading days, whether near-expiry events are skipped or a farther contract is selected, and the precise expiry/selection clock are not defined. A naive nearest-expiry implementation would not necessarily reproduce the charts. Modern weekly contracts also make a monthly-only source universe materially different from “nearest listed contract.”
- **Signed quantity conflict:** equation3is`−floor(equity × leverage / 1000)`but prose specifies leverage−3.5%and says the result is−17. Literal floor arithmetic gives **+18**, a long position. The chart shows positive3.5; using that positive magnitude gives−17and agrees with the short example. This is a source sign/convention conflict verified visually; do not silently run the literal long version as the intended strategy.
- **Sample drawdown is not stop risk:** atVX20,the5%trigger is one full VX point=$1000/contract. The15VXexample therefore risks$15,000before costs at that trigger, or$15,900/3.18%of source capital including its$900round-trip cost, assuming an exact stop fill. That exceeds the reported0.7%/$3500sample drawdown; a gap can be worse. An untriggered stop was not tested by the sample.
- **Sharpe denominator:** the author calls zero-return months a reason its monthly Sharpe understates performance. Inactive months remain part of calendar-time capital performance; removing them does not provide a fair like-for-like Sharpe improvement.

## 3. Why might it make money?

A plausible interpretation is compensation for bearing pre-decision uncertainty, followed by reduced demand for volatility protection as scheduled information arrives. This is event/volatility-risk compensation, not a guaranteed forced order or arbitrage. A surprising decision or press conference can increase uncertainty and hurt a shortVXposition.

The economic exposure is directly in tradable VX, not spotVIX. The source's threshold25is a futures-price filter and must not be evaluated on a back-adjusted continuous level or substituted spot index. Negative ES/VXcorrelation neither establishes an identical opportunity nor proves diversification from our equity-heavy book.

The communication environment also changed. [Powell's June2018transcript](https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20180613.pdf) announces press conferences after every scheduled meeting fromJanuary2019; [Kansas City Fed](https://www.kansascityfed.org/research/economic-review/estimating-the-effects-of-monetary-policy-an-ongoing-evolution/) describes the usual14:00ETstatement/14:30ETconference sequence. A35-minute cover crosses that second event. A2010–14parameter choice is not automatically a modern executable edge.

## 4. Can we build on it?

**Potentially, after the source/data gate clears.** The event is scheduled, the instrument is tradeable, and the hypothesized uncertainty decline is economically intelligible. However, qualifying evidence is missing before returns, so the completed work here is a source/feasibility screen, not a backtest.

Owned files provide daily VIX/VIX3M/VIXY and prior Calvados daily datedVXmetadata. None supplies this strategy's intraday eligibility price, entry/cover, stop path and quotes. The prior failed Calvados naked component is a different basis/multiday definition; it does not reject this FOMC trade. Earlier weak/negative ES/NQFOMC strategies in `TIER_LIST.md` are also different exposures.

Actual acquisition work:

- [Cboe CFE Futures Trades](https://datashop.cboe.com/cfe-futures-trades) advertises March2018–present; [legacy VX Trades/Quotes](https://datashop.cboe.com/cfe-vix-volatility-index-futures-trades-quotes) advertises April2004–February2018. Correct products were located after two inaccessible guessed paths. The public current-product ZIP sample failed in the connected reader due to unsupported compressed content; no bytes were acquired. Final price not obtained.
- [FirstRate VX](https://firstratedata.com/i/futures/VX) advertises individual intraday contracts fromVXZ08. Its public ZIP sample also failed due to unsupported compressed content. [FAQ](https://firstratedata.com/about/FAQ) documents Eastern local time/DST and start-of-bar labels, but no sample metadata was verified. Full-history price was not exposed in the retrieved page.
- [Portara VX](https://portaracqg.com/futures/int/vx/) advertises individual-contract1-minute history from2004. Its sample control returned an interactive page rather than a data file. Provider search-index text displayed a$220special offer/usual$330, but the dynamic page did not expose a final quote; this remains an unconfirmed advertised lead, not a purchase recommendation.

No subscription, purchase, login, external message or access workaround occurred. Availability at product-page level is real progress, but it is not an acquired/admitted historical panel. Detailed URLs, outcomes, schema clocks and limitations are retained in the data gate.

Next check when matching inputs/source clarification arrive: reconcile one FOMC event, selected dated contract, the5-unit maturity rule, entry timezone/DST, announcement availability,35-minute cover and a hypothetical stop/gap. Then preregister a bounded2018–22cheap screen with ordinary-day short-VXrisk and random-side controls, costs and explicit no-rescue rules. Only passing design results earn later historical validation and personal BASE/ADD/REPLACE/EMPTY comparisons. No regime/expiry/clock interpretation is selected using returns here.

The power screen is conditional:8meetings/year×5years suggests40opportunities before filters; n=34and SD=$500perVXwould require about$171.50net/trade for t≥2, or$231.50gross at source costs. Neither trade SD nor modern filter pass rate has been estimated. Source$60cost requires.06VXpoint gross; an alternative one-outright-tick-per-fill plus$10fees assumption totals$110and needs.11point. Those are transparent assumptions, not measured slippage or permission to double-count spread.

## Placement and retention

| Home | Verdict |
| --- | --- |
| 50K evaluation | No admission; VXeligibility, native sizing, floors and account contribution unverified |
| 150K evaluation | No admission; same unresolved prerequisites |
| 50K funded | No admission; no paired payout/intraday-path evidence |
| 150K funded | No admission; no paired payout/intraday-path evidence |
| Personal | Conditional research lead; source specification, intraday data and native risk remain unverified |

The rule's intraday holding window is potentially time-compatible with Apex, but that does not certify instrument permission or account survival. Do not copy the source$500kleverage into our plans or invent prelaunch micro-VXhistory.

Retained in TODO's **Promising strategies awaiting verification** queue and as a follow-up to [execution reference E51](../EXECUTION_REFERENCES.md). No strategy rank, portfolio allocation or live change. Return trials/account simulations0. Arithmetic assertions and source-figure inspection pass; exact-source reproduction, statistical validity and account benefits remain unverified.

For Claude: `agents/codex/results/fomc_vx_2544445_review.md`.
