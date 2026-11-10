# Five reserved intraday paper slots
Author: dot | 2026-11-10 | Research status: provisional, not five qualified strategies

The original [ten-paper report](dot_ssrn_ten_papers_20261110.md) is complete. These are five additional distinct papers for the requested no-overnight category. None is presently verified as a new, strong, fully specified Apex-compatible implementation. The user has said account-agreement matters are handled; this report therefore focuses on holding window, instrument fit, evidence and missing inputs, without certifying legal/account compliance.

## Slot 11 — Harvesting the Value Area
Mansoor Alqaydi (September 2026), [SSRN7546200](https://ssrn.com/abstract=7546200).

**Source status:** Abstract verified; full PDF not accessible in this review.
**About/finds/mechanism:** NQ/MNQ intraday value-area boundary rejection toward point of control. Author reports 2,921 sessions over9.5years and walk-forward/block-bootstrap analysis; repaired components have profit factors above1.2. Author explicitly identifies unmodeled intraday excursion risk and untested live slippage.
**Build/data:** Exact value-area construction, historical session definition, entry, rejection confirmation, stops, targets, costs and flattening must be recovered. Need transaction-level volume-by-price or an explicitly disclosed approximation; OHLCV alone cannot reconstruct the tape.
**Can code?** Not faithfully yet. Simulated bust probability is unusable for account-survival claims without intraday equity excursions.
**Fit:** Direct eligible-market hypothesis, subject to explicit same-day liquidation. No exact-ID repository match found; this is not approval or a new validated edge. Prior profile research already notes tape-exact value-area data gaps.
**Decision:** Highest priority source audit among these five, not a deployment candidate.

## Slot 12 — Intraday Momentum and Return Predictability: Evidence from the Crude Oil Market
Wen, Gong, Ma and Xu, [SSRN3553682](https://ssrn.com/abstract=3553682); [Economic Modelling publication](https://doi.org/10.1016/j.econmod.2020.03.004).

**Source status:** Abstract and publication information verified; full executable specification/cost tables not verified.
**About/finds/mechanism:** One-minute USO ETF data2006–2018 show previous-close-to-first-half-hour returns predict the final half-hour. Overnight information contributes more than the opening half-hour. Inventory-announcement information does not itself predict the final half-hour.
**Build/data:** Source-window interpretation is signal through10:00ET and holding15:30–16:00ET. Verify before coding. Measuring the previous overnight move does not mean holding overnight. Need native USO minute history for replication; CL would be a separate adaptation.
**Can code?** Hypothesis yes, paper-faithful build no until source rules/costs are complete.
**Fit:** USO is not an Apex futures instrument. A CL adaptation can be intraday but is neither replicated nor known profitable. Same broad family as previously failed equity intraday momentum.
**Decision:** Conditional oil-market adaptation, not a fresh proven non-equity edge.

## Slot 13 — Intra-day Seasonality and Abnormal Returns in the Brent Crude Oil Futures Market
Ewald, Haugom, Ouyang, Smith-Meyer and Størdal, [SSRN5037563](https://ssrn.com/abstract=5037563); [Quantitative Finance2025](https://doi.org/10.1080/14697688.2025.2535479).

**Source status:** Publication/abstract verified. [University record](https://eprints.gla.ac.uk/363707/) restricts accepted full text until6February2027; no restricted download attempted.
**About/finds/mechanism:** ICE Brent tick data2010–October2021, converted to minute data across maturities, show recurring intraday patterns. Authors report positive significant alphas for selected timed trades after costs and margin assumptions.
**Build/data:** Exact time windows, contract selection, costs and distinction between sequential directional trades and simultaneous maturity spreads remain unknown. Requires actual Brent maturity data and legally usable history.
**Can code?** No faithful specification currently. No purchase authorized.
**Fit:** ICE Brent availability is not verified for the user's platform. Neither trading CL instead nor removing a spread leg is a replication. Exact no-overnight cutoff cannot be checked until the source windows are known.
**Decision:** Reserve slot, source/instrument blocked; not counted as a verified Apex candidate.

## Slot 14 — Intraday Price Reversal Patterns in the Currency Futures Market
Rentzler, Tandon and Yu, [SSRN885686](https://ssrn.com/abstract=885686); [university record](https://digitalcommons.montclair.edu/acctg-finance-facpubs/71/).

**Source status:** Primary publication record/abstract verified; exact complete trading specification unavailable.
**About/finds/mechanism:** Seven CME currency futures1988–2003; five exhibit significant intraday reversal after large price changes. GLOBEX reduced errors, while the euro's introduction altered patterns, emphasizing institutional regime dependence.
**Build/data:** Freeze a prior-day/open-gap trigger and same-day exit only after reading the source thresholds and conventions. Requires correct historic session opens, contracts, quotes and cost estimates.
**Can code?** Generic hypothesis feasible; source-faithful contemporary replication not ready.
**Fit:** Certain modern CME FX contracts are listed by Apex, but obsolete historical contracts cannot simply be relabeled. A standalone daytime position avoids overnight holding; actual exit windows still unverified.
**Decision:** Historical research foundation. No contemporary net edge established; existing repo FX gap-fade failures are an adverse comparison, not ignored.

## Slot 15 — Non-Parametric Intraday Price Boundary Detection
Valter Levander (July2026), [SSRN7155458](https://ssrn.com/abstract=7155458).

**Source status:** Abstract verified; full PDF inaccessible.
**About/finds/mechanism:** Level1 tick data in2025–2026 across index, commodity and FX futures. Gaussian KDE volume nodes plus local-extrema gating identify short-lag reversal probabilities. Evidence decays at longer reversal streaks.
**Build/data:** Need trades with sizes/timestamps, causal node estimation, extrema confirmation lag and an executable entry/exit rule. Never use an unconfirmed swing high/low before its confirming bars exist.
**Can code?** Feature prototype possible after source recovery; no demonstrated trading strategy or net P&L yet.
**Fit:** A fixed daytime holding rule would be a new design, not an author-validated result. Exact instruments and source flattening unverified.
**Decision:** Feature-research slot only, not a strong strategy recommendation.

## Why the screen is not padded with familiar papers
Current TIER_LIST and research already cover Gao2440866 (failed NQ/ES), Baltussen3760365 (NQ regression weak), Zarattini4824172 and Chuk7609644 noise bands (existing family, costs/book-fit problems), ORB and VWAP variants, and VIX-ETP4470636 proxy (failed without real demand inputs). FX-fixing3521370 reports negative customer returns after costs. Counting those as new strong independent additions would mislead.

Baltussen's non-equity settlement extension remains a useful comparator: published full paper gives CL/NG/HO14:00–14:30ET, GC13:00–13:30ET, bonds14:30–15:00ET. Main results exclude costs and warn that exploitation may fail. A non-equity extension is one related hypothesis, not multiple new papers.

## Timing context, not account certification
Official pages checked10November2026: evaluation/simulatedPA flat before4:59PMET; liveFAQ4:50PMET; livestockHE/LE/GF2:05PMET and grainsZC/ZW/ZS/ZM/ZL2:20PMET, with earlier holidays possible. No overnight here means same-day holding, stricter than merely remaining within a futures session.
Sources: [trading times](https://apextraderfunding.com/help-center/getting-started/futures-trading-times/), [liveFAQ](https://apextraderfunding.com/help-center/live-prop-trading-program/apex-live-prop-trading-program-faq/), [Rithmic instruments](https://apextraderfunding.com/help-center/rithmic/rithmic-commissions-instruments/), [Tradovate instruments](https://apextraderfunding.com/help-center/tradovate/tradovate-commission-instruments/).
The user's agreement handling is acknowledged. No trading, automation deployment or account changes are requested or performed.

## Status
Five additional papers identified; zero promoted to fully verified strong intraday strategies. Source gaps, data gaps and prior failed families remain real. Further research should prioritize exact source access and data feasibility before any return test. No tests, paid data or schedules run.
