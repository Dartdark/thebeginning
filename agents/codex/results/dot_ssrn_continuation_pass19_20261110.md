# dot: sequential oil inventory information
Author: dot. 2026-11-10. Research only; no return tests or trading.

## 58. Market Inefficiencies Surrounding Energy Announcements
Alturki–Kurov, [SSRN 3747330](https://ssrn.com/abstract=3747330), published 2022. [Complete publisher text](https://onlinelibrary.wiley.com/doi/10.1002/fut.22264) inspected, including Tables 2/8, Section 3.7 and Appendix A.2.

**Conditional intraday CL candidate. Potential owned-price-data adaptation, not verified current-data eligibility.**

### Source specification and evidence
Nearby WTI, January 2011–August 2019, 385 Wednesday EIA events. Signal = preceding API actual inventory change minus Bloomberg median **EIA/DOE** inventory-change forecast. Positive: short; negative: long. Enter EIA−60 minutes, exit−1 minute. Table8 annualized Sharpe .67; extreme-decile subset 77 events, 2.10. Annualization uses event frequency, not 252 trading days. Mean trade return/volatility not separately supplied; no cost deduction demonstrated. −90/−120-minute entries weaker. Decile thresholds not documented as prior-only; normalization differs between prediction and trading descriptions. Recursive OOS evaluates forecast errors, not net trading P&L.

Separately, post-API 0–30-minute CL return predicts pre-EIA −60/−1-minute return: coefficient .17, R²4%. The liquidity split uses API-through-EIA information, including the future entry/target window. It is not a causal entry filter. Thursday releases are excluded. Futures inputs are Genesis; consensus Bloomberg; proprietary-data restrictions apply.

### Independent implementation assessment
The information mechanism is more concrete than generic indicator tuning: API data precede EIA, allowing an estimate of unresolved public inventory information. Nonetheless, whether modern traders still leave an exploitable edge is untested here. No portfolio diversification or account-survival claim follows from gross Sharpe. Exiting before the announcement avoids intentional exposure to that jump but does not guarantee exit liquidity, eliminate pre-event volatility, or cover a failed order.

Normal clock: 09:30–10:29 Eastern, 06:30–07:29 Pacific. This meets the requested intraday holding criterion in its ordinary calendar case, not blanket account-rule certification. Native MCL costs are separate from dividing CL P&L by ten.

The lower-input price-sign branch is an **inferred adaptation of a forecast relationship**, not Table8's portfolio. It cannot inherit Sharpe2.10, use ex-post liquidity or silently choose deciles/windows after outcomes. Freeze signal, zero handling, selection, calendar and fills before returns.

### Owned-data admission remains incomplete
[Saved inventory](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/outputs/codex_qj_donchian_20261030/inventory.json) lists CL2017–22 files/hashes, with 1,289 session labels in2018–22; Chicago clock is assumed, native contracts/roll identifiers absent. [Audit](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/qj_donchian_20261030.md) records missing August21–22,2019 and other partial sessions. Required API/EIA observations were **not** freshly inspected.

[Existing EIA intake](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/eia_inventory_input_gate.md) has 261 editions on260 dates, including duplicate June29,2022 editions and unresolved exception clocks. It supplies neither the API-release history nor Bloomberg forecast receipts.

Before admission:
1. Match actual historical API and EIA editions, releases, delays and holidays.
2. Authenticate API16:30–17:00 Eastern observations and last pre-maintenance price. Distinguish start-/end-stamped bars.
3. Verify EIA−60/−1-minute rows, missing/duplicate bars, timezone/DST, contracts, rolls and negative-price handling.
4. Reconcile executable quotes, latency, native commissions/slippage and forced exit.
5. Obtain as-of consensus rights/timestamps for the exact strategy; a website's consensus is not automatically Bloomberg's.

[API official distribution](https://www.api.org/energy-insights/statistics/wsb) and [sample terms](https://www.api.org/-/media/Files/Statistics/SAMPLE_wsb20181102.pdf) show that publicly visible values do not establish unrestricted historical-panel rights. The [2026 API calendar](https://www.api.org/-/media/Files/Publications/WSB%20Schedule%20of%20Releases%202026.pdf) cannot substitute for historical release records.

### Dedup and disposition
No matching3747330 entry found in current index, TIER_LIST or DATA_NEEDED. Existing USO EIA intraday momentum, gas analyst-quality drift and unconditional storage-event trials are different specifications; their failures remain recorded. Priority is a no-return information/row audit, not an authorized return test.

Unnumbered reserves: FX post-FOMC reversal [4386170](https://ssrn.com/abstract=4386170) needs current full source and costs; its12–24-hour horizon is not same-day intraday. Geman–Li crude shocks and Indriawan–Jiao–Tse bond drift lack verified full executable sources/SSRN identities in this pass.
