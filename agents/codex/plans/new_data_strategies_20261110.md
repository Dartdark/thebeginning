# Frozen new-data strategy batch: funding stress and delayed front-end fear

User request November9,2026Pacific: test the newly owned datasets for a strategy. Priority: improved evaluation
book, including a VB replacement. Existing Twin2/DT2/finish mode are baseline. No live, VPS or shared plan edits.
Evidence: `agents/codex/evidence/new_data_strategies_20261110.md`; source cutoff Claude08544017.
Commit exact code/plan before returns. This manual task does not resume/reset any scout/lab/global trial history.

## Fixed rules, budget and clocks

Two hypotheses, three candidate arms, six candidate/price-only definitions, up to two selected-parent null
definitions = **at most8economic definitions**; no further thresholds, times, directions or grids.

FUND_SHORT: SOFR−EFFR≥0.05percentage points (5bp), short at09:01open, close10:00CT.
FUND_CONTROL: same short window/bracket on every day with known funding data.

FEAR_EARLY: VIX9D/VIX>1 from the exact date two completed NQ sessions earlier, AND07:30close<00:01open;
long07:31open→08:29closeCT. FEAR_MORNING: same information, long09:01open→10:00closeCT.
Each has its own price-only control: identical overnight decline and known ratio, ignoring the ratio>1 gate.

All: one trade/day, one integerMNQ, fixed50point stop/100point target live from entry minute, target requires
1point through, gap stop fills at open. Reuse `grid._walk`; its nearest-extreme convention determines ambiguous
minute order. Expected entry→scheduled-exit OHLC must be finite; retain rejected/missing-day counts, no price fill.
Known early-close days skip to avoid exceptional sessions. Prior ATR is not needed for price/size.
Skip any scheduled holding window spanning a quarterly NQ roll date (third-Friday minus8days); same for controls.
Features require finite exact source/price timestamps. All flat long before15:59CT.

Clock admission from saved primary policy: core `percentRate` only, same effective date for both rates;
available3pmEastern on next observed reference-rate business date, age≤7calendar days. No data from the
effective date may be used on that effective morning. Source percentiles/volumes remain unadmitted.
Fear index uses two-session delay; exact missing Cboe source date→unknown, not OFF. Do not use same-day closes.
Preserve original source files/blank clocks; emit a derived feature/availability ledger. Prefix checks before returns.

Use NQ raw snapshotfe35af99 via `/workspace/vb_loss_split_source` (already exact-byte isolated tree), no shared
cache rewrite. MNQ native fee1.25RT,1adverse tick per market/stop leg. Stress fee2.50RT and2ticks per such leg;
same raw trades. Gross/fees/slippage/net and day sums must reconcile. Quote/feed uncertainty remains explicit.

## Standing data screen, then cheap design test

New-state screens use the available19-piece daily reference panel plus frozen FINRA andZT ledgers from
Claude08544017, and evaluationONBADX30. These22reference streams cover the strategy names, not every current
sizing/version. Report source/version/calendar limits. For BOTH derived states, split active reference days only
on **known** feature dates. 44comparisons, corrected bar `metrics.t_threshold(44)`, design-only. No outcome-selected
entry/filter follows that exploratory screen; original candidate rules remain frozen. Later histories stay unopened
for new candidate outcomes until earned. No claim that this daily panel certifies intraday evaluation protection.

Candidate design2018–22; 2017is warmup. Whole/long/short separately, per year, all ratio metrics, gross-to-net,
trade counts, missing paths and eligible frequency. Funding active-era concentration must be explicit.
For each arm cheap gate:≥60trades, positive total, PF≥1.20,t≥2.5, at least3positive design years, stress total>0.
Also report total net of its full price-only control and the removed trades' mean/t; the proposed data gate's
removed entries must lose money (mean<0). No requirement to preserve the prior evaluation book's profit.
Failing arms STOP; no2023+run, reparameterization, changed sign or market substitution.

For each surviving family choose at most one arm by highest design Calmar, tie by fixed orderFUND/EARLY/MORNING.
Then matched random-drop1000runs: keep same number from its price-only pool; candidate total must exceed95th
percentile of random totals and candidate DD≤median randomDD. Selected-parent random-side1000runs recompute
the exact same entry dates/brackets; candidate total must exceed95th percentile. Both must pass.
Each null is conditional on existing observations; neither guarantees future stability. Count conditional null
definitions and earlier Claude searches. No independent alpha/promotion claim based only on this small batch.

## Only survivors advance

Frozen2023+ historical replication (already seen history), same costs/rules; require positive net, PF≥1.2,t≥2,
positive recent bootstrap net lower90%bound (ten-session blocks,2000draws,seed20261110), stress net>0.
Report standard metrics/year/side, trade reshuffle and annual block-bootstrap trail risk via repository tools.

Only a survivor earns current150K/50K evaluation BASE,ADD,REPLACE_VB,EMPTY_VB on common source coverage,
integer risk250/100per entry capped4/2MNQ respectively; risk based on the fixed$100nominal stop perMNQ,
thus2/1contracts. Include existing per-account finish quantities,30calendar days,native fees,continuingEODtrail,
intradayfloor,adverse DLL/entry-exit stress. Candidate must improve paired recent passes with lower90%band>0
and avoid increased failures under adverse fills. If no qualifying book placement, no adoption.
Inherited source path defects/UNKNOWN coverage prohibit verified live claims. Independent/native review and
forward observation remain prerequisites. No platform code before these gates, no funded/personal expansion
unless separately justified by a passing candidate. No purchases, external contacts or background schedules.
