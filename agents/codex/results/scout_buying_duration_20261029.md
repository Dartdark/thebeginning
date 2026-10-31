# Buying Duration: WATCH / NEEDS DATA; source triage, full text unavailable

Summary: This paper links government-bond month-end returns to index-duration demand.
Its abstract reports 1.19 bp on the last trading day versus 0.07 bp otherwise; these are author claims.
Our earlier ZN month-end test failed, but its fixed 13:59 CT exit misses the later US index snapshot after January 2021.
A primary-source clock audit warrants completing source review; no new return test or allocation follows yet.

Source: Amar Soebhag, Patrick Verwijmeren and Fabio Martinetti, *Buying Duration: Index Rebalancing and Price Pressure in Government Bond Markets*, written 2026-10-12, posted 2026-10-14, SSRN 7601879, 60 pages advertised.
[SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7601879) · [DOI](https://doi.org/10.2139/ssrn.7601879).
Review date: 2026-10-29. Repository context: `codex/work` at `49b48b8064a57a13fd114ee9d527c69cc7c58f0a`.
**Access: indexed SSRN metadata/abstract inspected; paper PDF not obtained or read. No paper SHA256 is claimed.**
New return trials: **0**. No source-parity strategy or economic preregistration exists for this paper.

## 1. What is it about?

The authors examine whether benchmark-driven purchases of duration at fixed-income index rebalances move government-bond futures. The advertised study connects month-end demand to a pricing deadline and subsequent reversal. This is a potential scheduled-flow mechanism in rates, rather than a demonstrated ES/NQ directional signal.

## 2. What does it find?

| Claim visible in the authors' abstract | Verification boundary |
|---|---|
| Duration-scaled futures: 1.19 bp on the last trading day versus 0.07 bp on other days. | Not reproduced. Duration scaling, contracts, exact return interval and net costs are unknown here. |
| Month-end contributes 47% of average monthly returns. | A return-attribution share, not an implementable account return or win rate. |
| Pressure concentrates near the index snapshot, partly reverses afterward, and strengthens with larger extensions and rates volatility. | Table-level significance, conditioning definitions and real-time feature availability have not been inspected. |
| The effect moves when Bloomberg changes its pricing time. | The rule change is independently corroborated below; the paper's return response is not. |

The full paper's sample, exclusions, dependence adjustments, trading-cost assumptions, exact timestamps, instrument weights and supplementary evidence remain unreviewed. Secondary recaps advertise US/German futures over 2003–2024; that is a lead, not a primary-text-confirmed sample in this report.

### Independent source check: a real clock change

[Bloomberg's October 15, 2024 methodology](https://data.bloomberglp.com/professional/sites/27/Fixed-Income-Index-Methodology.pdf), Appendix 4, printed p.80, specifies US Treasury index pricing at **16:00 New York from January 14, 2021**, previously **15:00**. Ordinary-day equivalents are **15:00 CT** and **14:00 CT**. Use `America/New_York` and `America/Chicago`, rather than treating the document's occasional EST label as a fixed UTC offset.

The same page and footnote 97 distinguish early closes: **13:00 New York**, with **14:00 New York during January 14–November 25, 2021**. Calendar exceptions must be dated explicitly. Provider cash-bond marks are not executable futures fills.

[Dyer, Fleming and Shachar, New York Fed, September 22, 2026](https://libertystreeteconomics.newyorkfed.org/2026/09/treasury-trading-at-the-close/) independently describe Treasury trading activity shifting to the new strike time. This corroborates a volume/clock mechanism, not this paper's profits or our ability to capture them. We inspected the primary publications; we did not independently reproduce their market observations.

## 3. Why does it make money, if it does?

A benchmark manager can face tracking-error costs for missing the pricing deadline, while another participant can accept inventory risk before that deadline. Coordinated demand can create temporary pressure even without news about fundamental value. This is the authors' proposed explanation; no net executable profit available to us has been verified.

Anticipation, competing arbitrageurs, cash/futures basis, changing duration demand, spreads and adverse fills can consume the premium. A partial reversal does not automatically supply a second profitable short. Do not convert the paper's duration-scaled basis points into dollars per ZN without its normalization and contract specification.

## 4. Can we build on it?

**Yes: finish a bounded clock-aware source and data audit. A return test is premature.**

The mechanism is already in the repository. [TIER_LIST](../../../TIER_LIST.md) records the October 17 ZN index-extension test; [script](../../../analysis/zn_month_end_test.py) and [saved output](../../../analysis/outputs/zn_month_end_test_output.txt) were inspected, not rerun:

| Existing protocol, one ZN | Archived full-period average net | Archived t | Archived 2023+ average net |
|---|---:|---:|---:|
| A: last business day, 07:21–13:59 CT | −$31.0 | −1.4 | −$79.7 |
| B: preceding business day, same hours | −$22.9 | −0.9 | −$9.4 |
| C: last business day, 12:00–13:59 CT | −$55.8 | −4.0 | −$84.3 |

These negatives remain valid records for those protocols. Their fixed endpoint is about an hour before the ordinary US snapshot after the documented change. Therefore they do **not** establish source parity for a snapshot-centered 2021+ rule. Conversely, that mismatch does not overturn their losses or establish that a later entry/exit makes money.

The old script selects month-end from eligible observed data dates and forward-fills closes within each row. Its main printed line has 105 nonmissing trades while the shared table displays 106; it also charges commission on each of two fills. A future comparison must audit calendar exclusions, unresolved bars and costs, preserving the original outcome rather than silently repairing it. These are code-inspection observations, not a fresh data or accounting certification.

The smallest justified next check is to obtain a lawful full-text copy, pin its version/hash, and extract exact source clocks and a no-return event/input census. [Evidence sheet](../evidence/scout_buying_duration_20261029.md) records the gates. Establish the relevant index calendar, dated snapshot regimes, actual contracts/rolls, and pre-entry vintages of duration-extension forecasts; final month-end extension cannot stand in for a forecast available earlier. A timed calendar baseline and a forecast-conditioned candidate must be distinguished before any plan.

No entry offset, threshold, stop, reversal, new contract universe or configuration count is selected here. Later adaptation would require an evidence sheet marked TEST, a committed bounded preregistration, the cheap 2018–22 screen and all existing validation/account gates. Previously seen 2023+ remains historical validation. ZN is a relevant rates instrument, but native sizing, contract costs and simultaneous plan losses remain unaudited; there is no established place in either evaluation, funded plan or the personal portfolio.

## Access attempts and retained sources

- The direct [SSRN delivery URL](https://papers.ssrn.com/sol3/Delivery.cfm/7601879.pdf?abstractid=7601879&mirid=1) returned **403 Forbidden** through the web reader on 2026-10-29. Its indexed content was metadata/abstract, not PDF text. No access control was bypassed.
- Exact-title/PDF and author/institution searches found SSRN and recaps, but no accessible alternative full-text copy. The [Tinbergen author profile](https://tinbergen.nl/index.php/person/1228/amar-soebhag) and [Erasmus Martinetti profile](https://pure.eur.nl/en/persons/fabio-martinetti/) were opened; neither supplied this manuscript.
- [QuantSeeker recap](https://www.quantseeker.com/p/weekly-research-recap-02f) and [Alpha in Academia recap](https://www.alphainacademia.com/p/recent-academic-research-de8?action=share) are discovery leads only; neither substitutes for methods/tables in the paper.
- Bloomberg methodology: printed pp.45–46 for duration-extension definitions and forecast publications; p.80 for US pricing eras. These sections were inspected, not the entire methodology.
- Owned/free acquisition follow-up: local ZN minute CSVs for2018–22 exist (19.6–21.5MB each; header/date fields inspected,
  no returns computed). The provider methodology advertises pre-month-end forecasts through INP on Bloomberg Terminal.
  Public search found a [four-page March2020 provider report on a public mirror](https://archr.com/wp-content/uploads/2020/03/2020-03-30-Summary_Mar_Index_Duration_Changes_and_.pdf),
  inspected via the connected reader. It contains forecast-duration fields and duration as of2020-03-27. This establishes
  an example, not a complete historical panel or its real-time publication/receipt evidence. No local PDF hash, licensed
  access or reconstructed forecasts are claimed. [Access/inventory receipt](../research/scout/runs/20261029_initial_access.json).

## Decision

**WATCH / NEEDS DATA.** The specific merit is the independently corroborated snapshot change absent from the old fixed-clock baseline, coupled with the authors' claimed timing evidence. Keep a clock-aware extension check for later verification; do not repeat the unconditional month-end long or tune around its losses. Reopen only after full-text/source parity and point-in-time feasibility are established. No return test, new trial budget, PowerLanguage, plan or live-system change occurred.

For Claude: `agents/codex/results/scout_buying_duration_20261029.md`.
