# NQ Day Flow Six: TEST for a fixed historical composite

Summary: The user requested t >= 6 and explicitly accepts a composite of existing signals.
Test the six already confirmed intraday NQ legs at one MNQ each, without choosing weights from new returns.
This is a recombination of known edges, not a new independent discovery or fresh holdout.
The numeric target must survive daily clustering and native fees; execution and account suitability are separate gates.

Sources: repository at 41a0ae6; Claude plans at 94a1627 (same adopted plan as afde088).
`TIER_LIST.md`, `DEVELOPMENT_PROCESS.md`, `analysis/plan_alpha_test.py`, `analysis/build_lab.py`,
the six MultiCharts workbooks named in the plan, and original strategy files.
New composite return trials so far: zero. Existing seven-leg plan-alpha study is explicitly prior evidence.

## 1. Participants and mechanism

This combines the existing intraday plan's six NQ systems: Vault Break, ONB ML v2, Monday Long,
Expiration Open Short, Late-Day Flow and NFP Fade. Opening inventory/momentum, option-expiration
hedging, leveraged-product closing demand and payroll repricing are the existing hypotheses.
Vault Break and ONB in particular use price proxies, not measured compulsory orders.
Diversification across their decisions may strengthen aggregate evidence; no new causal story is claimed.

## 2. Information, direction, size and clocks

Use unchanged confirmed source rules and their historical MC executions. One MNQ per sleeve, including
ONB/EOS/NFP instead of their dollar-risk sizing. Prior public information and source decisions remain
unchanged; the ML model is already fitted and selected. No flow-size estimate independent of price
is available; do not invent one. Central exchange clock, normal and early-close source exits.
Replay ends October 9, 2026 because that is the available joint NQ price cutoff.

## 3. Transmission

All six trade NQ directly; MNQ has the same index exposure and independent micro fees.
Offsetting sleeve positions must net on one account. Six tickets are not six independent observations
when the same session drives them. This construction is neither a hedge nor a new asset class.

## 4. Inputs and feasibility

| Input | Available evidence | Limitation |
|---|---|---|
| Six MC List of Trades workbooks | Committed, 2018 through October 2026; each says one-minute Bar Magnifier enabled | Individual confirmations are not confirmation of a combined order manager |
| NQ day and overnight minute CSVs | Committed 2017-2026, last date October 9 | Not back-adjusted; missing native bars and exact intraminute order remain concerns |
| Current personal daily baseline | Committed 19-leg fee-1.24 snapshot, pinned afde088 | Inherited booking/fee approximations; no margin simulation |
| Current Apex plans | Read from Claude 94a1627 | Existing joint overnight baseline paths remain unavailable |

All inputs are owned repository material; no purchase, network data request, key or account needed.
Historical MC fills are an execution-conditioned replication input, not signals available to a live trader.

## 5. Costs and overlap

Primary MNQ commission $1.24 round trip, plus $0.50 per slipped fill; $1.04 fee sensitivity.
NQ reference $7.25 plus $5 per slipped fill. Market/stop entry slips once; target exit none;
stop/time exit once. Charge every sleeve ticket even where account netting could save fees.
No presumed fee savings or favorable netting fills. The same legs already occupy the plan's
daytime hours; this is a possible alternative organization/weighting, not an empty-slot diversifier.

## 6. Power

Planning assumptions only: roughly 2,200 daily observations, aggregate daily SD $150 per six-MNQ basket.
Mean required for daily t=6 is about $19.2/day (6*150/sqrt(2200)); t=2 about $6.4/day.
These are not forecasts. Actual t must also be calculated with Newey-West lags 5 and 20.
Published whole-plan work already gives reason to test aggregation; do not call that prior work unseen.

## 7. Prior trials and falsifiers

The six components and earlier portfolio studies were searched/selected on this history. The prior VB
720-cell search, ONB ML/filter research, and other component searches remain prior selection.
Use the latest ranked-item count plus this composite as a lower-bound DSR sensitivity, also report
10,000-search sensitivity; neither supplies a complete prior trial census. One fixed composite only.
Failure of the committed design screen stops validation. Failure of t6 does not authorize weight fitting.

## 8. Failure, exposure and next gate

All signals can share NQ trend/reversal losses. Marketable/stop orders can suffer adverse selection;
targets can miss. Six virtual one-MNQ sleeves cap gross intended exposure at six contracts and net
exposure at six, but do not impose a fixed dollar loss cap. Each sleeve retains its existing stop and
time exit. An exit must be attributed to its own virtual sleeve; a stale exit cannot open a position.
No cross-account hedge. Data failure in a future manager must block new orders; its safe close behavior
and source protective orders require platform confirmation before use.

TEST means historical composition is feasible. A statistical pass does not establish new alpha,
MC netting parity, t6 forward, or Apex suitability. The preregistration fixes the stop rule and controls.
