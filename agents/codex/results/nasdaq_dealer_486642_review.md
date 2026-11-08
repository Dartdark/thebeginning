# Nasdaq dealer competition: retain execution reference; no futures strategy

Summary: Historical Nasdaq stock-dealer concentration is associated with wider effective spreads.
Authors estimate8.76cents/0.5434% of price as a concentration-related spread component, not realized profit.
Reported20.3-month half-life is conditional on stocks reaching the halving threshold within the sample.
Retain concentration, quote-clock and censoring lessons; no NQ/ES signal, return test or allocation follows.

Source: Youngsoo Kim and Vikas Mehrotra, *Competition and Market Structure of NASDAQ*, September2003 preliminary draft, SSRN486642;30 PDF pages, posted February8,2004 per [primary metadata](https://ssrn.com/abstract=486642). Reviewed November7,2026 (America/Los_Angeles).
[Uploaded PDF](../inputs/nasdaq_dealer_486642/ssrn-486642.pdf) · [complete text](../inputs/nasdaq_dealer_486642/full_text.txt).
Scope: main narrative, references, tables and figure material inspected; printed Equation5/p.8 visually verified. Printed body page numbers lag PDF pages by two. Graph coordinates and original dealer/TAQ data not independently reproduced.
Plan: source/arithmetic review only; no economic preregistration warranted. [Evidence](../evidence/nasdaq_dealer_486642.md).
Script: [reproducible arithmetic/fixtures](../../../analysis/codex_nasdaq_dealer_486642_audit.py) · [source receipt/hashes](../../../analysis/outputs/codex_nasdaq_dealer_486642/source_audit.json). Financial return trials and account simulations: zero.

## Five questions

1. **What is it about?** Whether Nasdaq stock dealers possess market power despite many nominal competitors, and how persistent that power is. It combines monthly dealer-by-stock trading volumes with trade/quote observations, measuring concentration with the Herfindahl–Hirschman Index(HHI) and regressing effective spreads on concentration plus stock/trading controls. Nasdaq National Market stocks are the subject, not NQ index futures.
2. **What does it find?** Authors report a positive HHI coefficient across all68monthly full-sample regressions from May1995–December2000. Their regression-attributed average spread component is8.76cents per share,0.5434% of price. Table5 gives a20.3-month average time to halving for the79.4% of stocks that reached that threshold; the remainder did not do so in sample. Less-liquid stocks carry higher percentage estimates. These are historical author estimates, not our replicated profits, modern spreads or trading-strategy results.
3. **Why does it make money, if it does?** The proposed dealer advantage is access to order flow and information that entrants cannot immediately replicate, permitting wider spreads. That could create economic rents for incumbent dealers, but the paper infers rent from a regression rather than measuring net dealer cash profits. It does not show how a retail futures trader can capture that component. Quoted/effective spread compensation must still cover adverse selection, inventory risk, operating costs and fees.
4. **Can we build on it?** Yes as an execution-measurement reference: distinguish nominal participant counts from actual concentration, measure effective spread using correctly timed quotes, and handle incomplete halving observations explicitly. The historical coefficient cannot calibrate our NQ/MNQ costs. Smallest justified future use is checking the existing fill/quote accounting at an already-authorized execution review; concentration analysis requires genuine participant-level data and a modern independent research question. No new alpha/data priority established.
5. **Can a strategy code be made?** **Research diagnostics: yes. A directional trading strategy: no rule is supplied.** HHI, effective-spread estimates, cross-sectional regressions and a censor-aware persistence analysis are implementable with identified dealer volumes and synchronized trade/quote records. The paper supplies no trade side, entry, holding period, stop, size or expected-return rule. A market-making simulator would additionally need queue, fills, adverse selection, fees and inventory accounting. Coding feasibility does not establish profitable market making or justify MultiCharts trading code.

## Study and result details

The dataset excludes Nasdaq SmallCap stocks and NNM stocks below the source's price and dollar-volume criteria. Dealer volumes were supplied by Nasdaq and trades/quotes came from TAQ. Monthly samples range from3,180to3,623stocks. The principal sample is68months, not eight years despite an introductory description. Narrativep.5 also says2002for a price observation that Table1 correctly labels2000.

Effective spread is `2*abs(trade_price - quote_midpoint)`, divided by midpoint for the percentage measure. This is a **full effective spread**, not the one-way distance from midpoint, nor a realized-spread or net-profit measure. The source uses quotes at least five seconds old under its historical timestamp convention. That lag must not become a default for modern CME data.

HHI is the sum of squared percentage market shares, on the0–10,000scale. With fractional shares it is `10000*sum(s_j**2)`. Four equal-share dealers give2,500; the source's mean2,133corresponds to about4.69equal-share dealers, versus13.2nominal active dealers on average. Active-dealer counting uses a0.1%volume-share threshold; a replication must distinguish all-share HHI construction from thresholded headcounts and preserve the volume denominator.

Monthly regressions control for log dollar trade size, log trade count, midpoint-based price variability, inverse price and dealer count. Table3's average HHI/1,000 coefficient is0.257percentage points. The source example—a1,000-point HHI reduction at a$17.92price—implies4.60544cents less effective spread, about15%of the30.75cent average spread. Our arithmetic reproduces that example; it does not establish a causal saving or new trade result.

## What limits the conclusions

| Issue | Assessment |
|---|---|
| Regression-attributed “rent” | Defined as coefficient×HHI/1,000, converted to cents using each stock's price. It is not a directly observed dealer profit, return on capital or customer opportunity. Extrapolation to HHI=0 is not a feasible fixed-dealer-count benchmark: the lower bound withNdealers is10,000/N. |
| Correlation versus causal market power | Concentration, spreads, order-flow arrangements, dealer quality, inventory and information risk may be jointly determined. Controls and the1997reform discussion do not by themselves establish an exogenous causal effect for the reported full-sample slope. |
| Persistence definition | First time a three-month moving average of percentage rent halves, averaged over stocks with observed crossings.20.6%never crossed during the window. This is not an AR/exponential-decay parameter or a forecast that a tradable spread will halve after20months. IPO groups also have differing observation windows. |
| Quote-variance Equation5 | Printed numerator uses the **sum** of squared quote midpoints minus squared mean, without dividing the sum by quote count. On three constant100quotes it returns2instead of0. This is a confirmed printed normalization issue; unavailable implementation may have used the correct variance. Its empirical impact is unmeasured. Prose also describes a denominator differently from the rendered squared-mean expression. |
| Group definitions | Main text and Table5 place the top200stocks in Group3; Table4's caption reverses Group1/3. Preserve the explicit membership rule rather than trusting the label. This is not evidence that the regressions used reversed samples. |
| HHI units and averages | The HHI variance identity requires population variance of **fractional** shares when multiplied by10,000. Dollar-rent averages need not equal average percentage rent times average price because averaging products differs from multiplying averages. No arithmetic error inferred from that difference. |
| Availability | A stock's completed monthly dealer market shares and same-month regression coefficients cannot become an earlier intramonth input. Original release/receipt times and lagged estimation are prerequisites to a prospective feature. |
| Market/era transfer | This is a1995–2000stock-dealer market. Dealer identity/concentration is not reconstructed from anonymous futures candles, tick volume or book imbalance; stock cents and percentage-spread estimates cannot be scaled into NQ/MNQ execution costs. |
| Statistical interpretation | Stock-month rows and persistent monthly coefficients are dependent. Source significance is not trading significance or independent strategy observations. No raw-data clustered/dependence-aware replication was run here. |

## Relevance and next action

Retain the lesson in [EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md): **more nominal participants need not imply lower executable costs, and a spread-based rent estimate is not net P&L.** Existing E10/E56 and diagnostic-data rows D42–D45 in [DATA_NEEDED.md](../DATA_NEEDED.md) already cover relevant quotes, fees and fill-clock prerequisites. No new worthwhile strategy lead is established, so no TODO/data-register shopping entry is added merely because dealer data are absent.

No original dealer/TAQ panel found in the bounded owned-filename inventory; the study supplies no replication code/panel in the upload. No paid data, external contact or broad acquisition effort pursued because no trading hypothesis earned that stage. The exact research replication would require dealer identifiers/volumes, historical membership/IPO records, original trade/quote clocks and resolved variance/group conventions.

**REFERENCE / DON'T TEST as a standalone NQ/ES strategy.** Neither the four Apex homes nor personal portfolio receives a candidate. No entry/exit/stop invented, no historical-return/placebo/holdout/account stage run, no MultiCharts code written. Trading metrics are not applicable rather than zero. Independent empirical verification remains pending.

The document's request not to quote is source text, not a user instruction or an authorization requirement. This review paraphrases findings; no author contact, external notification or live-system action was taken.

For Claude: `agents/codex/results/nasdaq_dealer_486642_review.md` — historical concentration/cost reference; censored half-life and printed variance cautions; zero return trials.
