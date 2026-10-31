# IFT_NQ5_Flow_Signal: NEEDS DATA — exact directional-volume input unavailable

Summary: Complete 5-minute NQ rule supplied, plus candid but unverified research claims and a screenshot.
Native full-Globex up/down volume and the original MultiCharts trade list are missing.
Owned OF files cover 09:30–16:15 ET only; NQ price exports contain total Ticks, not the required directional split.
Do not substitute total volume or fill missing overnight flow with zero. No return test is earned yet.
Next: obtain the matching native chart export and report, then commit the frozen return-test protocol.

Return trials: 0. No numeric profitability rank assigned.
Input code/research note: agents/codex/inputs/ift_nq5_flow/.
Data audit: analysis/codex_ift_nq5_data_audit.py; analysis/outputs/codex_ift_nq5_flow/data_audit.json.
Repo source context: Claude 92b1d4cde768bcfce019cf9a95944158dd0ebba3; Codex 7d1e6a295aca16c8204c45e9c5a7146b3e49c77e.

## 1. Participant/mechanism
Hypothesis is continuation after up-volume acceleration, strong candle direction and EMA alignment, with separate morning-long/overnight-short regimes.
This is an observable-price/volume hypothesis, not a measured institutional parent order or forced transaction.
No evidence identifies a buyer/seller who must continue to transact, or why pressure remains after the close. The supplied author explicitly lacks an up-volume mechanism.
The strategy can still merit a bounded empirical replication; calling it institutional flow does not establish causality.

## 2. Information and clock
Source assumes NQ 5-minute, CT Exchange time, full Globex, native trade-volume Up/Down fields, Classic mode with 1-minute Bar Magnifier.
Signal at completed bar close; next-bar market entry. Long window08:35–11:00; short23:00–08:30 inclusive.
Ratio uses the current bar's up-volume divided by its20-bar SMA, including current bar. Rank compares against the prior500 stored ratios before replacing the ring slot.
Long ratios>=1.5, rank>=95, EMA9>21, positive candle/body>=40%, volume>prior; short ratios>=2.5, rank>=80, EMA9<13, negative candle/body>=40%, (Up-Down)/Up<=-0.35.
The short ratio means Down>=1.35×Up, not a conventional total-normalized delta of−35%.
Stops and targets are computed from the *signal close*, before the actual next-open fill. Actual fill risk/R multiples can differ; the2.5ATR cap is not a guarantee on realized entry risk.
Source protects entry only after its first5-minute bar closes. TP2 and breakeven are staged after the program observes the first partial exit; freeze the platform recalculation settings before porting.
No learned label at this stage. Future fitting requires mature labels, purging where outcomes overlap, train-only transformations, fixed model/price baselines and run manifests per RESEARCH_CONTROLS.md.

## 3. Transmission
Trades NQ directly, with minimum exact scale-out Qty2. No separate upstream flow estimate or notional demand size is supplied.
Do not infer urgency or parent-order size from a large up-volume bar alone.

## 4. Data gate
| Input | Owned / missing | Timing and semantics |
|---|---|---|
| Native 5-minute O/H/L/C/Volume/UpTicks/DownTicks, full Globex | Missing | Preserve dxFeed chart's exact classification and volume settings, CT timestamps and prior warm-up |
| Existing NQ 1-minute price bars | Owned,19 files | Headers contain volume only; exporter writes Ticks, not separate up/down |
| Existing OF 1-minute directional volume | Owned,35 files/876,077 rows | Entire observed span09:30–16:15 ET, no earlier/later-session rows; different source from native chart |
| MC detailed trade list/settings | Missing | Screenshot insufficient for parity, leg grouping or fee reconciliation |
| Claimed Python port, yearly WF selected settings and training schedule | Missing | Note's claims cannot be independently verified |
| Native history before September2018 | Author says unavailable | Treat as unavailable; do not silently prepend a different directional-volume construction |

The long also needs full-session data: its20-bar ratio,500-bar rank and EMA/ATR inherit overnight history. An RTH-only long is a different strategy.
Up/down tick-volume classification is not automatically identical to aggressor buy/sell classification. Prior strategy-specific parity does not prove this field match for every overnight bar.
Data collection requirements are listed in results/ift_nq5_flow_review.md. No data purchased or live exporter modified.

## 5. Costs, liquidity and overlap
Author claims $15/NQ RT including two ticks; that budget implies $5 commission if every trade is market/stop both sides. Partial passive exits need an explicit per-fill fee/slippage ledger.
Native MNQ costs cannot be inferred by dividing NQ commission by10.
Morning longs overlap RS/FC2B/ONB/VB; overnight shorts can overlap Overnight Tick/VIX in opposite directions and carry into morning.
OnePos is live-only; historical results do not apply that same gate. No empty intraday gap is established.
Quotes/fills are required to measure overnight slippage; owned OF spread data cover only the cash-session window.

## 6. Power
Author's reported~407 positions across~8years provides limited independent events after splitting sessions/sides; partial exits are not independent observations.
No observed per-position variance/trade list is supplied, so t-stat/power cannot be inferred from PF/win rate alone.
Illustrative n=200, SD=$1,000 per2-NQ position would require net mean about$141 for t2; actual inputs must be measured in a preregistered design screen.
~6,000 short configurations plus774 annual parameter candidates and additional structure/ablation looks create substantial selection risk. Count family/design looks; do not present a new preregistration as undoing prior selection.

## 7. Prior work and falsifiers
Related FC2B, ONB/VB and generic volume/momentum features; overnight structure is not automatically independent portfolio exposure.
No exact IFT match found in the inspected repository tree.
Stop if data semantics do not reconcile; an apparently positive proxy cannot validate this source.
Reject a later design if costs/executable initial protection erase edge, incremental up-volume fails comparable price/session baselines, or plausible delays destroy it.
No threshold/clock search is authorized by this evidence sheet.

## 8. Failure/diversification
Continuation can reverse sharply; overnight market/stop fills have gap/spread risk. First-bar unprotected losses are not bounded by the planned stop.
Source Qty2 exits one contract at TP1, remainder at TP2/ribbon; Qty1 removes the runner. Changing Qty changes the scale-out fractions because TP1 remains one contract.
An annual/daily correlation cannot show whether offsets arrive before a trailing breach. Full account chronology is necessary.
No live change proposed. Protected entry, gap-aware dollar sizing and cross-strategy position gating need separately frozen protocols before testing.

## Decision / destinations
NEEDS DATA. 50K evaluation,150K evaluation,50K funded,150K funded and personal portfolio are each blocked before return testing by the same missing native full-session inputs.
No account pass-rate, payout, drawdown improvement or placement claim was produced.
Once data reconcile, preregister <=5 variants with exact parent-bar order timing, initial protection, costs and cheap design stop before new returns.

