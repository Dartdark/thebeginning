# Asset-weighted LETF sizing of existing Late-Day Flow

Summary: Free issuer NAV/assets history exists; historical publication and revision evidence remains unresolved.
This is an upgrade to existing LDF exposure, not a new gap-filling strategy or an observed residual-order signal.
The proposed score isolates asset-weighted pressure per fixed benchmark move, using lagged liquidity only.
Power is borderline; the committed inventory uses entry dates and an assumed SD, never candidate returns.
Verdict: NEEDS DATA — historical availability/revision evidence; the requested protocol is conditional, not permission to test.

Date: 2026-10-22. Branch: `codex/work`. Return trials: **0**.

## 1. Who trades and why

Daily-reset TQQQ (+3), SQQQ (-3), QLD (+2), QID (-2) target leverage to the Nasdaq-100.
With fixed capital and a small benchmark return r, the modeled reset notional is
`r * sum[L*(L-1)*prior_assets]`. This creates a potential hedge demand for counterparties.
Execution instrument, timing, pre-hedging and capital flows are not observed in NAV history.
Ivanov and Lenkey's capital-flow-offset result is counterevidence, not a detail to ignore.
This protocol tests incremental sizing information; it cannot identify a causal mechanism.

Sources: [CME explanation](https://www.cmegroup.com/trading/equity-index/files/Leveraged_ETFs.pdf),
[Ivanov/Lenkey author abstract](https://pure.psu.edu/en/publications/do-leveraged-etfs-really-amplify-late-day-returns-and-volatility/).
The earlier evidence report records the scope of source inspection; no new paper replication is claimed.

## 2. Direction, magnitude and timing before entry

LDF supplies its established direction at 14:00 CT. Let
`K = 6*A_TQQQ + 12*A_SQQQ + 2*A_QLD + 6*A_QID`.
For a fixed 1% Nasdaq move, modeled notional is `0.01*K`, in the direction of that move.
Claude reports yearly median magnitudes of approximately $0.34bn in 2018 to $2.61bn in 2026,
versus about $24bn of NQ 14:00-15:00 notional in 2023-25. These are his descriptive estimates,
not independently reproduced here, and do not establish participation in an execution window.
Actual remaining reset orders and creations/redemptions remain unknown.

The sizing score divides `0.01*K` by a trailing 20-session median of completed NQ last-hour
notional, then compares with its own preceding 252-session distribution. No same-day future volume.
This is pressure capacity conditional on a fixed move, not an estimate of the entire day's actual reset.

## 3. Transmission

Nasdaq-100 exposure can be hedged directly in NQ/QQQ or the basket; the split is unobserved.
Claims that all modeled fund demand reaches NQ, or remains unexecuted at 14:00, are unsupported.

## 4. Data, novelty, timing and cost

Issuer files: `https://accounts.profunds.com/etfdata/ByFund/<TICKER>-historical_nav.csv`.
Claude's immutable input snapshot and audit: commit `c23fc02`, `data/letf/` and
`agents/claude_evidence/LETF_DATA_FEASIBILITY.md`; inventory script reads blobs without importing another branch.
Direct AUM is split-invariant; shares are in thousands. Use NAV*shares*1000 as a consistency check only.
Scope quality checks to 2017 warmup onward. The first inventory attempt found 140 zero-share rows in
SQQQ's 2010 history (positive NAV/assets), outside all proposed inputs; do not claim all-history share consistency.
Historical split-adjusted share changes are not themselves proof of creations/redemptions.

Price: free history; no paid product needed for these four funds. NQ minute OHLCV already exists.
Missing: historical publication-time policy/vintages and revision evidence; cost of resolving these unknown.
The audit's opening claim that the data is point-in-time is stronger than its later timing caveats support.
Using the previous NAV date reduces same-day leakage but cannot establish when it was published or undo revisions.
No forward-fill across an unexplained missing cash-session row; no backfill or day-D NAV at day-D entry.

New information is K relative to expected liquidity, rather than another threshold on price momentum.
Growth over calendar time is a confounder; rolling ranks, within-year controls and matched placebos are mandatory.

## 5. Costs, occupancy and account fit

The funded baseline already carries LDF at 2 MNQ, about 14:01-14:30 CT, including its existing stop.
This deliberately overlaps that line; it does not fill a new occupancy gap. Evaluate every accepted LDF entry,
regardless of other open positions, then evaluate portfolio interactions at account level.
Baseline research costs: $17.25 per full NQ round trip; $1.725/MNQ by proportional research convention,
not a verified micro fee schedule. Each extra contract incurs costs and risk; resizing is not costless.
No expected incremental edge is claimed. Standard 1/2/3 MNQ sizing will be compared with 2 MNQ.

## 6. Power and stopping

Planning assumption from Claude: per-trade SD about $810 per full NQ, not estimated anew here.
For roughly 450-500 design entries, extreme thirds contain approximately 150-166 observations each.
IID t=2 requires roughly $178-$187 high-minus-low mean difference per full NQ; approximately
80% power requires about $249-$262. These are separate concepts, and both bounds are optimistic.
Actual counts and formulas are saved by `analysis/codex_ldf_flow_prereg_inventory.py` after the protocol commit.
Missing inputs, clustering and controls reduce power further. No enlarging to 2023+ to rescue a failed design.

## 7. Prior catalog and verdict

Already tested: LDF itself; momentum threshold/exit variants; order-flow filters; ridge meta-labeling (F);
OU-regime sizing (WATCH, no funded gain); gamma-flip sizing (WATCH, in-sample); generic LETF reversal (F).
Relevant files: `analysis/letf_rebalance_test.py`, `analysis/ldf_meta_label_test.py`,
`analysis/ou_ldf_bench.py`, `analysis/ldf_gamma_sizing_check.py`, TIER_LIST and WATCHLIST.
No asset-weighted, lagged-liquidity-normalized LDF sizing counterpart found in those sources.

**NEEDS DATA (historical availability/revision evidence, cost unknown).** The user requested a pre-registration
now, so `agents/codex/plans/ldf_flow_sizing.md` freezes a conditional protocol. This does not advance the
builder brief's evidence gate to TEST. Strict validation waits for that gate; a snapshot-assumption study must
be labeled exploratory/WATCH and cannot be promoted by historical results. No returns are authorized in this task.
