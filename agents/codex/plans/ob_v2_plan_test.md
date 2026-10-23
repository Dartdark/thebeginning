# OB v2 against the current 50K plans — frozen preregistration

Written 2026-10-23 before new strategy returns. User: "assume matching data, test it against our plan".
Evidence sheet: `agents/codex/evidence/ob_v2_plan_test.md` (TEST under that assumption).
Work only on codex/work; no live/VPS/broker/API/strategy-plan changes. This plan must be committed before returns.

## Question and immutable rules

Does the submitted OB v2 improve current evaluation or funded account outcomes, at fixed stated sizes?
Mechanism is an inventory/continuation hypothesis with a volatility-risk gate, not an established forced flow.
Closest overlap: evaluation ONB ADX30 and funded ONB ML; retain other plan lines exactly.

Two rule ledgers only, no search:
1. OBV2: uploaded rule, ATR15/ATR100 in [0.6,1.2], lookbacks 15/100, ADX(16)>=20, midnight ON range,
   08:30-08:45 OR, source OR-size/exhaustion gates, close-confirmed breakout, up to four entries, 0.30 RTH ATR
   stop/3R target anchored on signal close, normal last signal noon and 14:30 flatten decision.
2. BRIDGE100: same exact engine and 100-session warm-up with ratio filter disabled. Diagnostic comparator only.

Both receive the **existing plan operational half-day overlay**: use our ONB early-close calendar, no new signal
at/after 11:00 CT, flatten decision 11:30. This is separately declared from the uploaded fixed-14:30/SetExitOnClose
source. It makes the account experiment eligible; do not call it native uploaded-source parity. No other repair,
ML gate, ADX change, lookback choice, side selection or risk/size optimization is authorized by this test.

Use existing `grid24`, Bridge replay/helpers, metrics/resampling, portfolio paths and account simulators. Extend
only in analysis/codex_*.py where functionality is missing. Never execute helper scripts that launch unrelated
research/scoring runs. Any exact simulator acceleration must first match funded_sim outputs on fixed histories.

## Data and execution frozen before inspection

Cache: scratch_data/g24.pkl and lab.pkl, common trading dates 2018-01-02 through last cached date 2026-10-09.
Warm-up: fetched Claude e7c394f data/NQ_1min_2017.csv, copied byte-for-byte into
agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv (SHA256
`b4005cfcd7ea021174b1eb14534b473ee5d2e4014319f991e9c34b0619bfde8d`).
Use May-December RTH rows to seed indicators in memory; no cache rebuild or loss of early-2018 opportunities.
Record the actual input hash; if this transcription differs, correct it before returns, not by altering input data.

Bars are end-stamped CT. A signal at 09:00 fills at the next actual minute open (bar labeled 09:01).
Adverse one tick for each market/stop fill; $7.25/NQ round-trip commission. Targets require one-point trade-through,
with opening price improvement when appropriate. Stops fill at the adverse open when gapped, including entry
minute gaps; if both exits are possible within one minute, stop first. The entry block's bracket is modeled active
in the entry minute, as its preissued orders intend. Preserve raw/slipped prices and signal-close stop anchors.
Do not use the old replay's silent last-available-close fallback to hide half-day carries; apply the stated overlay.
If a scheduled flat cannot be executed because no next bar exists before the halt, flag the event and disclose
any explicit conservative handling rather than silently treating it as an ordinary valid fill.

Account comparison primary uses the same scaled-NQ cost convention as the baseline. Mandatory adverse-cost
sensitivity adds **$1.275/MNQ RT to challenger ledgers only**, taking their modeled commission from $0.725 to
$2/MNQ (plus the existing tick slippage). Baseline stays unchanged, deliberately disadvantaging challengers.
This is not verified actual micro accounting; no winning conclusion permits deployment without real fees.

## Cheap design gate — stop before 2023+ if it fails

Compute OBV2 and BRIDGE100 on 2018-22 first. OBV2 proceeds only if: at least 100 trades; total net > 0;
average gross >= 1.5 times its actual modeled mean round-trip costs; PF >= 1.15; at least 3/5 years net positive.
Report each side; do not drop a weak side. This is a design-cost feasibility gate, not promotion or t significance.
If it fails, report REJECT and stop; no alternate threshold or half-day policy. Otherwise open 2023+ once under
the same frozen rules, label it historical replication because its selection history is already seen, then run accounts.

## Account portfolios — maximum five fixed configurations per account, no sizing search

Current funded roster (from latest FC/S47 bench construction, Claude e7c394f): VB_N2/VB_F1, ONB_ML2_MC risk$400,
MON_MC1, EOS risk$700, LDF_MC2, NFP risk$500, MON_BR_MC1, CLS2 MCL, MOC_MES2, RS_L1.
Keep existing cushion scaling f clipped [.5,1], full size at $1,500 cushion; floor to whole micros.
Funded portfolios: BASE; EMPTY_ONB; replace ONB ML with OBV2 at $400 stop risk; BASE+OBV2 at 1 MNQ maximum;
replace ONB ML with BRIDGE100 at $400. All risk quantities use the candidate's own stop distance.

Evaluation roster: VB8, ONB ADX30 risk$1,100, Bridge Monday2, EOS risk$500. Portfolios: BASE; EMPTY_ONB;
replace ADX30 with OBV2 at $1,100; BASE+OBV2 at 1 MNQ; replace ADX30 with BRIDGE100 at $1,100.
Same 50K $3,000 target, $2,000 EOD trail and $1,000 daily limit, 21-trading-day window as current simulator.
Use full-length eligible historical starts; report any differing existing end-window convention separately.

Funded: 1,000 paired circular block histories, 500 days, L20, seed1, identical histories for every configuration;
one/two-year payouts, 5/95 outcome bands, blown, all-six, median days to six with noncompletion=inf.
Report paired 95% intervals for mean payout differences and blown differences (5,000 paired resamples, seed902).
Evaluation: every full 21-day start, full/design/2023+; pass/blow/timeout and days; paired 95% difference bands
from circular 60-start blocks (5,000 resamples, seed903) to respect overlapping windows. No independent-binomial CI.
Run primary and challenger-cost stress; no post-result choice between them.

## Fixed decision rule

Funded candidate is worth independent promotion review only if it beats BASE and, for replacement, EMPTY_ONB:
either (a) year1 payout gain >= $250 with paired 95% lower bound >0, year2 >= BASE-$100 and blown increase <=1pp;
or (b) both payout means >= BASE-$100, blown falls >=2pp with 95% upper difference bound <0, and days-six no
more than 10 days slower. Replacement must also improve year1 versus EMPTY with paired lower bound >0.
The direction must survive challenger-only extra cost; report failures of individual criteria, not a composite score.

Evaluation: full-sample pass gain >=2pp and paired 95% lower bound >0, 2023+ pass delta >=0, with no materially
higher failure rate (blown delta <=1pp). Replacement must beat EMPTY; direction must survive extra cost.
Otherwise no plan change recommended. Tiny gains/ties are no demonstrated benefit, not proof of equivalence.
If an addition wins while replacement does not, report that exact configuration; no new size search.

## Required diagnostics and reporting

Whole/side/year/design/recent metrics: n, win, mean/total NQ net, t, Sharpe, Sortino, PF, Calmar, Ulcer, DD and
DSR with current ranked-item count; 2023+ bootstrap intervals using existing resampling, plus standalone daily
Monte Carlo at one MNQ with the accounting limitation. Report filtered kept and removed control trades' mean,
t and total; do not call positive removed trades a bad-trade filter. Matched random removals: 1,000 year/side
stratified fixed-count trade drops, and a whole-day selection null with matching yearly retained event-day counts;
judge total net and DD, not average alone. Full-day filter makes included-day trades nested after shared warm-up.
Random side and random entry time controls: 100 fixed-seed runs each, same event days/count and exit distances;
report effective counts if one-position collisions reduce them. No control is selected as a strategy.

Count both fixed rule ledgers and every diagnostic/stress evaluation; list prior selection exposure. Preserve
eligible-day ratio/warm-up flags, trade ledgers, inputs/hashes, timings/overlap and any source/replay differences.
Account engines retain baseline CL/MOC path approximations, disclosed rather than silently changed. Store
reproducible scripts/results only under allowed Codex paths. Summary at most five lines. Commit/push results
to codex/work and give Claude the report path. No ML/plan/live change or new forward rule is authorized here.
