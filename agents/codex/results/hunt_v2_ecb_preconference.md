# H06 ECB first-five-minute direction: REJECT at the gross cost gate

Summary: the frozen first-five-minute EURUSD direction did not carry enough gross movement into the preconference window. On40 scheduled2018–22 meetings, FOLLOW5 averaged **$0.859375 per M6E, gross t0.319496**, versus the preregistered **$9.98** hurdle. Close this hypothesis without stopped, validation or account tests; continue the bounded hunt.

Plan: `agents/codex/plans/hunt_v2_ecb_preconference.md`, preregistration **3b995614ea4a38e53ad3d7cc33cf28b87b0df49d**. Script: `analysis/codex_hunt_v2_ecb_gross.py`, SHA256 `93f9f509054859db5790f09c5261dbffd2400e0b7a11d2cbeb2b52ccf8acc2a3`. Calendar admission and implementation commit **2d0a14dd34b38dfccdf4830b6b4e932b4740d480**. Outputs: `analysis/outputs/codex_hunt_v2_ecb_preconference/`. This hypothesis:1 gross screen,0 counted economic evaluations. **Running budget:5/60 economic evaluations,6/10 hypotheses,4 gross screens, plus archived65 t6 evaluations.** This does not reset selection history or restart t6.

## Mechanism and rule as tested

The before-data eight-question sheet is `agents/codex/research/hunt_v2_ecb_release_source.md`, committed16635fc. Dealers and institutional EUR risk books might adjust exposure after scheduled ECB information; the prediction was continuation after the first complete five-minute reaction and before the press conference. No compulsory hedge volume, policy surprise or measured net flow was claimed. US macro overlaps, immediate incorporation and reversal were known competing explanations.

Use Berlin civil time: release13:45/conference14:30 before2022-07-21; release14:15/conference14:45 afterward, converted with zoneinfo to Chicago and UTC. FOLLOW5 takes the sign of OPEN[R+1] to CLOSE[R+5], waits another five minutes, enters exact native OPEN[R+11] at wallR+10 and exits OPEN[P] at wallP−1. Holds are34/19 minutes. Flat reactions skip both models; none occurred. LONG_CALENDAR is an unselectable long reference on the identical40 events and endpoints. No alternate window, sign, bank, side or era was selected.

Raw gross is `side * (exit_open-entry_open) * 12500` directly in M6E dollars using owned6E quotes. This is an unprotected raw effect screen, not an executable stopped-strategy return. No costs were subtracted. Native M6E assumptions are$1.24 round-trip commission, one adverse$1.25 tick per market fill, and at most$1.25 additional round-trip adverse micro-grid quantization: upper cost$4.99, twice-cost hurdle$9.98. The earlier source nomination omitted quantization; the increase was frozen before6E returns. This is not a broker quote or verified M6E liquidity.

## Saved gross results

All dollars below are **gross per one M6E**, before commission, slippage or grid rounding. Full side-by-year rows for both definitions are retained in `gross_summary.csv`.

|FOLLOW5 period/side|Events|Total gross|Mean gross|Trade t|
|---|---:|---:|---:|---:|
|2018–22 both|40|34.375|0.859375|0.319496|
|Long|22|−13.125|−0.596591|−0.154729|
|Short|18|47.500|2.638889|0.702776|
|2018|8|60.625|7.578125|2.131041|
|2019|8|40.625|5.078125|0.934544|
|2020|8|−31.250|−3.906250|−0.748212|
|2021|8|−8.125|−1.015625|−0.216191|
|2022|8|−27.500|−3.437500|−0.353293|

LONG_CALENDAR:40 long events, total−$60.625, mean−$1.515625, t−0.565038; no short events. It is context, not a fallback candidate. Neither a favorable individual year nor the short-only mean clears the primary full-design cost gate.

## Calendar, clocks and source audit

The one pinned calendar is chris-cheshire/project-midas-mk7@f9e756cbbca3a0576178412a48e1e374c9c76cfe, `midas/data/calendar/ecb.txt`,3650 bytes, Git blob68cba6e08e80c47c7476277f07caeec320ef9995. Byte/blob proof and unique monotonic weekday dates passed:8 scheduled dates per year,40 total. Calendar marker SHA256: `12f2dc97cfb60ef542888bf39d0ef7ea10025ea2821c7e91b01c45b7731a82bb`. Root's committed admission and independent review accepted a source-limited scheduled-public-event research use before opening6E prices. The archive compilation date is not the event knowledge time. Original per-date receipt and primary-date authentication remain unverified. The clock notice was read as attributed primary text; uninspected citations were not treated as independently confirmed.

Only explicit native6E2018–22 files were used. Metadata audits preceded price conversion:1,735,775 source/unique rows, zero duplicate excess, conflicting keys, invalid OHLCV or off-tick rows at the declared floating tolerance. All40 reaction, waiting, held-minute and exact endpoint windows were complete; no eligible event was deleted and no source gap filled. All40 were normal calendar sessions, with zero holiday/early-close skips. Morning endpoints are before15:59CT; no protected-strategy holiday behavior was tested. No future prices, old-strategy maker or external strategy code ran. Continuous-contract/exporter/receipt and M6E versus6E execution assumptions remain limits.

Actual raw execution was2026-10-26T23:56:29.804967Z through23:56:40.466211Z, original preregistration3b9956, implementation2d0a14d. `gross_verified_execution.json` binds code, calendar and saved artifacts. The immutable `gross_gate.json` retains a stale cosmetic `reason` string saying raw endpoints are still gated; its authoritative phase, raw_returns_calculated=true, gross_screen_runs=1, economic_evaluations=0, numeric results and passed=false record the actual completed **gross failure**. The original file is preserved, not rewritten or rerun.

## Downstream work and limitations

The failed cheap gross gate stops H06. Protected net design, daily Newey–West, Sharpe/Sortino/PF/Calmar/Ulcer,2023+ historical validation, full2018–26 promotion, random-time/random-side placebos, dependence/selection resampling, plan-size Monte Carlo and BASE/ADD/REPLACE/EMPTY benches were **NOT RUN**. No funded/evaluation pass or payout improvement, independent raw-spec promotion pass, PowerLanguage draft or trading approval is claimed. The source/synthetic and saved-artifact audits are narrower reviews.

Only40 independent scheduled events limit power; minute rows are not additional observations. Preserve related macro/FX-family ancestry and the unexpected external preview of a different105-minute/4-hour ECB scan read after this first-five/preconference question was proposed. No external performance was borrowed. Native cost and source limits would still require review had the raw screen passed.

**Verdict: reject the frozen ECB preconference hypothesis at its gross cost gate; retain its evidence and continue a distinct v2 question.**
