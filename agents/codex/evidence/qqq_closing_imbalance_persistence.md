# QQQ closing-imbalance persistence → final-minute NQ: NEEDS DATA

Summary: Yes: the supplied Nasdaq FAQs support a specific closing-flow hypothesis, not a demonstrated trading edge.
Test whether large QQQ auction imbalances surviving late liquidity provision predict same-direction final-minute NQ moves.
The existing map estimates about 65% unoccupied minutes here; this overlaps ES MOC and is not a clean new gap.
An illustrative 124-event screen needs $71–125 gross/NQ per trade for t=2 under the stated SD assumptions.
Verdict: NEEDS DATA—historical QQQ NOII and synchronized quotes; no backtest, purchase or live change authorized here.

User request: evaluate the two supplied FAQs and fill an evidence sheet for market-closing research.
Plan: `agents/codex/plans/nasdaq_closing_faq_evidence.md`, **499f12f**, clarified before inventory at **10bd236**.
Script: `analysis/codex_nasdaq_close_faq_inventory.py`.
Output: `analysis/outputs/codex_nasdaq_close_faq/`. Catalogue snapshot: Claude **b2c8d74**. Return trials **0**.

2026-10-22 supplement: failure/diversification review and public sample feasibility under
`agents/codex/plans/chan_research_framework.md`, **daf9acf**. See
[`results/chan_research_framework.md`](../results/chan_research_framework.md) for the source links and sample limits.
The illustrative rule and all previously reported numerical inventory results below are unchanged.

## Source documents and the important historical distinction

Both uploaded PDFs were read in full and preserved unchanged, with text extractions and SHA256 hashes:

| Source | What it establishes | What it cannot establish |
|---|---|---|
| [openclose_faqs.pdf](../inputs/nasdaq_closing_faqs/openclose_faqs.pdf), 2018, 4 pages | Single-price opening/closing auctions; imbalance fields; liquidity offsets; Closing Cross at 16:00 ET; full closing dissemination from 15:55 ET in this version | A profitable NQ signal, current rules for every detail, or an actual historical imbalance dataset |
| [ClosingCrossfaq.pdf](../inputs/nasdaq_closing_faqs/ClosingCrossfaq.pdf), 2019, 2 pages | Early abbreviated disclosure at 15:50 ET, full disclosure at 15:55; MOC/LOC deadlines; why late LOC/IO liquidity can absorb an imbalance | The amount of remaining NQ hedging or how long an informational advantage survives |

These are Nasdaq documents, not NYSE/NYSE Arca rules. They do not provide the SPY data discussed earlier.
Their contact/subscription suggestions are source text, not user authorization to contact anyone, subscribe or buy.

The differences are historical, not a reason to blend the clocks:

- **Before 2018-10-29:** the preceding schedule had MOC entry cutoff 15:50 ET, LOC entry until 15:55, and a different
  publication cadence. Nasdaq's [2018-82 implementation alert][2018-change] documents the transition.
- **From 2018-10-29:** that alert moves full NOII to 15:55, MOC entry cutoff to 15:55 and LOC to 15:58, with full
  dissemination every second. This explains the 2018 FAQ's version.
- **From 2019-11-04:** [2019-66][2019-change] adds 15:50 early disclosure every ten seconds and earlier cancellation
  restrictions; full near/far prices remain available from 15:55. Early near/far fields are zero placeholders, not
  meaningful zero-dollar indicative prices. This matches the 2019 FAQ.
- **For trading today:** check [Nasdaq Rules 4702/4754][rules], not only either old PDF. The current book retains
  MOC/LOC entry deadlines, describes legitimate-error exceptions to some cancellation restrictions, and allows some
  residual LOC interest into Extended Trading Close. Thus not every leftover share necessarily disappears at 16:00.
  Halt/LULD crosses and exceptional close procedures require separate treatment. Only exceptions known before the
  decision may determine eligibility; later halts cannot be used to delete an adverse trade retrospectively.

The proposed observations are after 15:55 across regimes; even so, rule regimes must be recorded and checked
separately. A fixed observation clock does not make the underlying order constraints historically identical.

## 1. Who trades, and what causes or forces the trade?

Close-benchmarked investors and index funds send MOC/LOC orders to obtain the official closing price. The exchange
matches eligible auction and continuous-book interest at a scheduled close. Cancellation restrictions make some
on-close instructions more committed than ordinary resting quotes; **new offsetting liquidity can still arrive**.
MOC execution is not guaranteed (2018 FAQ question 14); LOC execution depends on price. The auction itself does not
force somebody to buy or sell NQ.

**Hypothesis:** when QQQ still has a large same-direction unpaired auction imbalance after the late LOC entry cutoff,
liquidity provision/hedging is not fully complete. Some incremental Nasdaq-100 exposure trading persists into the
final cash minute, creating a small tradable same-direction NQ move after a realistic decision delay.

That persistence and transmission are predictions, not facts established by the PDFs. The opposite outcome is
plausible: IO/continuous-book liquidity absorbs the imbalance, the price has already adjusted, or no NQ hedge is used.
The 2019 FAQ's page-2 example explicitly shows a buy imbalance being absorbed and the auction clearing below its
earlier indication. It is not a promise that a buy imbalance makes the underlying or futures rise.

## 2. Direction, size and timing known before entry

One illustrative future rule, **not a return-test preregistration**:

1. QQQ only; regular 16:00-ET cash closes. No current-constituent basket backfilled into 2018 and no half-day clock port.
2. Take the latest valid QQQ closing NOII messages **received by** 15:55:10 and 15:58:10 ET, rejecting stale observations.
   The buffer avoids assuming the first full 15:55 message arrived at exactly its exchange publication instant.
3. Require nonzero imbalance with the same sign at both observations and positive paired shares. Define the late
   intensity as `R = |imbalance shares| / (paired shares + |imbalance shares|)`.
   This is a bounded unmatched/paired measure, **not** a measure of all auction orders. Require R in the top fifth
   relative to previous sessions only, using a trailing-year rank and a predeclared minimum warm-up. A full first-year
   design evaluation needs 2017 messages too. No percentile is estimated from the complete historical sample.
4. Buy NQ for a buy imbalance, sell for a sell imbalance. Decision is 14:58:10 CT; illustrative entry **14:59:00 CT**,
   exit **15:00:00 CT**. This is a 50-second decision-to-entry delay. On close-stamped minute data, the execution
   interval is the bar **closing at 15:00**, not a 14:59 bar whose open preceded the decision.

The eventual plan must freeze exact stale-message rules, ranking support, fill/stop assumptions, latency stress,
exclusions and a design stop gate before returns. This sheet does not authorize scanning alternatives or testing the
opposite side if the stated prediction fails. No candidate signals were calculated.

Observable auction-side dollars would be `D = imbalance side × imbalance shares × current reference price`.
Changing the reference price can change the reported imbalance without new orders. D is therefore a priced
imbalance observation, **not** a guaranteed residual market order or an observed NQ demand forecast.

For scale only: a hypothetical **$100m** QQQ imbalance at an assumed NQ level **20,000** corresponds to **250 NQ**
contracts if fully hedged, **62.5** if one quarter is hedged, and **0** if absorbed elsewhere. The reported NQ volume
in the proposed minute has a **4,965-contract median** across available design dates. Those scenarios are about
**5.0%, 1.3% or 0%** of median volume. None of the imbalance dollars, hedge fractions or price impacts is observed here;
net market participation could be zero or have a different timing. Verify the export's volume definition before
treating it as exchange-complete participation. There is no evidence-based expected gross move yet.

## 3. Does the flow reach NQ directly?

[QQQ tracks the Nasdaq-100][qqq]; NQ represents the same broad exposure, so it is a plausible direct hedge.
A liquidity provider selling QQQ into closing buy demand could buy NQ to manage the short exposure. But a seller
already holding QQQ can simply reduce inventory; basket trades, options, netting and existing hedges can absorb it.
One ETF's imbalance also need not represent aggregate Nasdaq-100 demand. The same-direction NQ response must be
demonstrated, rather than inferred solely from common benchmark exposure.

## 4. New information, exact data, history, timing and cost

**New input:** actual equity-auction imbalance shares/side, paired shares and reference/indicative prices. This can
change while the prior NQ move is unchanged. It differs from inferring an auction imbalance from futures momentum
or futures book delta. It still requires controls for the preceding NQ move, QQQ price/basis and reference-price
changes to establish anything incremental.

| Needed | Have it? / availability |
|---|---|
| Historical QQQ full closing NOII with original exchange time/sequence and historical schemas | **No.** Nasdaq documents NOII-only historical files from 2010 and older full ITCH history; actual QQQ 2017–22 coverage/retention has not been verified by downloading files |
| Point-in-time receipt timing or defensible documented feed latency | **No.** An exchange timestamp is not proof that the particular vendor/customer received the message then |
| QQQ synchronized intraday quotes and auction-status/results messages | **No.** Needed for basis, price controls, late publication, halts and validation; final auction results cannot be used before they existed |
| NQ price data | Owned minute data exists for a coarse later screen; **no NQ price fields or returns were read here**. Quote/spread data is still needed for reliable executable costs |
| Cost | PDFs and this inventory are free. Complete historical NOII access and a live entitlement are **not verified free**; current QQQ-only price/sample availability is unquoted |

[Nasdaq's historical-product notice][history] distinguishes original intraday messages from **T+1 file delivery**.
T+1 packaging can support replay of a legitimately available real-time feed, but using the historical download itself
as that day's live input would look ahead. Its statement that NOII costs no *additional* fee **for existing subscribers**
does not mean the underlying historical subscription is public/free. The [current product landing route][ntv]
requires JavaScript in the research browser; no priced order, license terms or full-coverage download was verified.

If a denominator based on actual previous auction volume is later preferred, the NOII-only legacy file subset is not
automatically sufficient: its documented messages do not include all final cross-trade information. That is why this
sheet uses the paired/unmatched fraction instead. Schema/version changes, corrections and split consistency remain
data-gate work. The current NOII real-time feed must not be confused with a free historical sample or generic depth.

**No purchases or vendor contacts were made.** With the standing free/owned-data budget, this stays blocked unless
a suitable existing entitlement or genuinely free permitted archive/sample can be established.

**Sample-feasibility update, 2026-10-22:** Nasdaq's public [NOII sample directory][noii-sample] lists
`S050922-v50-NOII.txt.gz`, apparently for 2022-05-09. The listing is accessible without an account; file contents,
QQQ closing-message coverage, encoding and receipt timestamps have **not** been verified. This is a route to a
format check, not an established free historical panel. Databento also documents QQQ in `XNAS.ITCH` with schema
`imbalance`; account credits and an advertised dataset start do not establish complete QQQ history or our 2017
warm-up. The linked supplement report records the exact fields and no-return sample audit required next.

## 5. Can it beat costs in an actual gap?

Baseline full-NQ round trip: **$17.25 = 0.8625 point**, using repository commission plus one tick per market fill.
The cheap-screen 1.5× cost floor would be **$25.875 = 1.29375 points gross**, before statistical requirements.
Closing spreads, latency and actual micro fees can raise that bar. The FAQs contain no expected-return estimate.

The saved funded-roster map, including **ES MOC at 2 MES**, gives these flat endpoint-minute estimates for 14:59–15:00 CT:

| Monday | Tuesday | Wednesday | Thursday | Friday |
|---:|---:|---:|---:|---:|
| 24.0% | 74.1% | 74.4% | 74.7% | 74.7% |

Weighting weekday rates by regular-close cash sessions gives about **65.0%**; native saved-map weighting gives **64.4%**.
These are weekday-marginal, conservative inclusive-endpoint averages, **not candidate-event flat fractions or the joint
probability of an entirely flat window**. Candidate extreme imbalances may occur disproportionately on existing MOC
trade days, so actual overlap may be worse. No events are selected by whether the account is flat.

This is not a strong empty-hours candidate. Its most relevant funded comparison is **ES MOC Follow**, as a possible
data-informed replacement/upgrade rather than automatically adding another correlated position. LDF shares the broad
closing-flow family but exits earlier. An account-level addition/replacement comparison comes only after a valid edge
passes design review; none was run here.

## 6. Numerical power check

There are **1,259** 2018–22 cash sessions in the calendar, of which **1,249** have regular 16:00-ET closes; ten half days
are excluded in this illustration. By year the regular-close counts are **248/249/251/251/250**. These are calendar
opportunities, not observed signal events. The raw export has the final-minute volume bar on **1,248** of those days;
**2020-11-30** lacks it. Missing inputs cannot be treated as zero pressure or a zero return.

An assumed **20% event frequency** gives approximately **249** events; if half also pass persistence/support,
approximately **124** remain. Neither fraction is measured. A trailing-window top-fifth threshold does **not** guarantee
a 20% realized event rate when regimes cluster; 249 is a planning reference, not an upper bound. Missing messages,
warm-up and other data gates reduce support; autocorrelation reduces effective n.

| Planning case | n | Assumed trade SD/NQ | Net mean for t=2 | Gross mean including $17.25 costs | Gross NQ points |
|---|---:|---:|---:|---:|---:|
| Assumed 20% event-frequency case | 249 | $300 | $38.02 | $55.27 | 2.76 |
| Same, higher-volatility sensitivity | 249 | $600 | $76.05 | $93.30 | 4.66 |
| Half also pass persistence/support | 124 | $300 | $53.88 | $71.13 | 3.56 |
| Same, higher-volatility sensitivity | 124 | $600 | $107.76 | $125.01 | 6.25 |

Formula: `2 × assumed SD / sqrt(n)`; gross adds round-trip costs. SDs are explicit planning assumptions for volatile
closing events, not measured candidate SDs. These are optimistic single-trial screening hurdles, not the multiple-test
promotion standard. Needing several gross points **after** a 50-second delay makes the economic gate demanding.
Nothing in the PDFs establishes that magnitude. Count real event frequency first, then stop if plausible effects
cannot clear costs and power; do not widen the window after looking at returns.

## 7. Already tested, falsifiers and decision

Catalogue checks: existing NQ/ES/YM MOC follow rules use futures price momentum; `analysis/moc_orderflow_test.py`
uses NQ futures order flow and did not establish an incremental auction signal. Earlier Codex
`agents/codex/results/flow_evidence_sheets.md` already proposes **SPY/ES post-auction reversal**; changing its ticker
alone would not create a fresh mechanism. This sheet instead specifies a **pre-close QQQ auction-state persistence
input** within that same auction family. It does not claim independent diversification or rediscover generic MOC follow.

Claude's existing `agents/claude_evidence/2_auction_imbalances.md` and `PAID_DATA_LIST.md` at **b2c8d74** already
identify real auction data and Nasdaq NOII as a route to upgrading price proxies. This sheet narrows that earlier
research direction to QQQ, a specific late observation pair and an execution delay. It is a refinement of shared
auction research, **not a newly independent flow family**. No prior exchange-NOII return test was identified.

Reject the hypothesis if the QQQ readings are usually tiny or stale, the late signal is already fully priced before
entry, apparent revisions are reference-price artifacts, actual liquidity absorption eliminates the pressure, the
effect exists only in QQQ's premium rather than NQ, or it vanishes after price/basis controls. Failure after the
registered latency/cost/power hurdle is a stop, not permission to test the opposite direction or new clocks.

## 8. Failure and diversification — predictions before returns

| Question | This candidate's prediction / failure | Evidence needed later |
|---|---|---|
| What stops the mechanism? | IO/continuous-book liquidity absorbs the imbalance; providers hedge before our entry; reference-price changes mimic demand; hedging occurs elsewhere | Message/quote alignment, imbalance revisions and controls for preceding price/basis moves; then the registered net-cost design test |
| What liquidity do our orders supply or consume? | Illustrative next-minute market entries/exits consume liquidity, even though the story concerns other participants providing auction liquidity | Executable NQ quotes/spreads and measured or documented delays; no passive-fill assumption or maker rebate |
| How can losses cluster? | Buy pressure is absorbed just before entry, the move reverses, a news shock dominates, or spreads/data delays worsen around the close | Predeclared delay/slippage stress, missing-data rules and protected execution at actual micro size, all frozen in the later strategy plan |
| Which plan strategy might lose with it? | ES MOC Follow is the closest concurrent closing-flow exposure; same-direction equity repricing could hurt both. Monday holdings can also overlap. These are predictions, not measured correlations | Candidate-event overlap and conditional joint losses after the edge passes, using the existing funded roster and an empty-slot control |
| Can it protect before a breach? | No protection established. A 14:59 CT entry cannot rescue an account already stopped or breached earlier that day; an annual offset is insufficient | Chronological account replay under actual EOD trail/daily-limit rules, real entry eligibility and same-symbol netting |

The one-minute illustrative time exit is not a complete risk specification. Before a return test, freeze stop or
other maximum-loss handling, concurrent exposure and stale-feed handling; a time exit or stop cannot guarantee a
fill. Do not increase size because a short sample appears smooth. No risk sizing or protective behavior is inferred
from Chan's fund example, and this same-direction candidate is not labelled a tail hedge.

**Post-close reversal remains separate.** Temporary pressure could reverse after an auction, but the previously
proposed SPY/ES post-auction reversal is already in this research family. No QQQ reversal rule, clock or variant was
added here. A failure of persistence must not be reused to select a reversal on the same outcomes.

## 9. Decision and next gate

**NEEDS DATA.** The documents are useful mechanism evidence and support filling this sheet. They do not supply a
tradable historical signal, a profitable edge or a free licensed dataset. The cheapest next step is to check any
already-owned Nasdaq NOII entitlement and a small permitted QQQ sample **without NQ returns**, auditing coverage,
timestamps, schemas, imbalance size/persistence and quote alignment. No purchase is proposed. If no permitted data
source exists within budget, park it; do not substitute another price-pattern backtest.

Only after that data gate and Claude's review should a single hypothesis receive a separate return-test
preregistration and cheap 2018–22 screen. Previously seen 2023+ history and a forward log come later if justified.
Research trials, candidate backtests, portfolio changes, live changes and purchases in this task: **zero**.

[2018-change]: https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2018-82
[2019-change]: https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2019-66
[rules]: https://listingcenter.nasdaq.com/rulebook/Nasdaq/rules/Nasdaq%20Equity%204/block/EQUALS/
[history]: https://www.nasdaqtrader.com/TraderNews.aspx?id=dtn2009-059
[ntv]: https://data.nasdaq.com/databases/NTV
[qqq]: https://www.invesco.com/qqq-etf/en/home.html
[noii-sample]: https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/NOII/
