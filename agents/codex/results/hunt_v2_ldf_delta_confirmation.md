# Hunt v2 H01: LDF delta confirmation — REJECT at stopped design

Summary: Gross passed, but STRICT30 failed the frozen stopped-net filter gate. It kept$3346.58/MNQ
versus BASE$3504.60, removing$158.02of PROFIT. It beat only32.9%of matched random subsets jointly
on profit/DD and had3/5positive years. Close H01; no2023+, account benchmark, nomination of LEGACY,
retuning or PowerLanguage. This failed hypothesis does not stop the bounded v2 hunt.

Mechanism: agents/codex/evidence/hunt_v2_ldf_delta_confirmation.md.
Preregistration: agents/codex/plans/hunt_v2_ldf_delta_confirmation.md, **aa726e2** BEFORE data.
Gross implementation: analysis/codex_hunt_v2_ldf_delta.py, frozen **0a0ac5f** before execution.
Outputs: analysis/outputs/codex_hunt_v2_ldf_delta/; gross_verified_execution.json binds every artifact.
Stopped implementation: analysis/codex_hunt_v2_ldf_delta_design.py, frozen **45e005c** before execution.
Running v2 budget: **3/60 counted evaluations;1/10 hypotheses;1 retained gross screen**.
All3configurations are counted, with1BASEpath replay and2exact-ticket masks;1new strict correction and
2repeated references. The2000matched subset paths are nonexecutable diagnostics, not extra strategies.
Prior t6 history remains65evaluations/63unique rules; its program and old alerts are stopped.

## Mechanism and frozen rule

Daily-reset leveraged/inverse ETFs can require same-direction exposure changes near the close. The
filter asks whether opposing aggressive tape before a LONG LDF ticket weakens its current-book value.
Actual ETF inventory, obligations, hedge fractions and tagged futures orders are unobserved. This is
a disclosed confirmation of the user-named lead selected among roughly40old splits, whose old funded
benchmark failed. It is not a new forced-flow discovery or fresh historical holdout.

The5-minute LDF signal at14:00CT follows a cash-open move>=0.40prior15STOREDweekday ATR. Complete
13:31..14:00OF buy/sell quantities must match native closes within0.25point and exact total volume.
Drop a LONG only on complete negative delta; unknown/zero/positive flow and all SHORTS retain BASE.
STRICT30is a counted completeness correction. LEGACY partial sums with causal as-of existence handling
remain unselectable diagnostics. No clock, threshold, direction or size optimization follows results.

## Actual gross screen,2018-22

RAW_NO_STOP measures signed14:01-labelled minute OPEN (14:00wall time) through14:30CLOSE, no stop,
fees or simulated execution. Later counted design adds the frozen0.25ATRstop, entry-bar protection,
worse gap fills, no target and14:30exit. Gross results cannot substitute for those returns.

| STRICT30population | Events | Gross/MNQ total | Mean gross/MNQ | Gross trade t |
|---|---:|---:|---:|---:|
| BASE |485|5026.50|10.364|3.674|
| Kept |383|4499.50|11.748|3.493|
| Removed |102|527.00|5.167|1.147|

Removed raw-window profit is POSITIVE: the higher kept average alone does not establish filter utility.
The later frozen stopped-net filter gate still requires kept total>=BASE and negative removed net.

| Kept year | Events | Gross/MNQ total | Mean gross/MNQ | Gross t |
|---|---:|---:|---:|---:|
|2018|81|902.00|11.136|2.256|
|2019|67|-424.50|-6.336|-2.026|
|2020|71|416.00|5.859|0.800|
|2021|76|1317.00|17.329|2.014|
|2022|88|2289.00|26.011|2.681|

Kept LONGS159: gross2087.00/MNQ, mean13.126,t2.979. SHORTS224: gross2412.50,mean10.770,t2.229.
All BASE/LEGACY/STRICT populations, years and sides are retained in gross_summary.csv; no diagnostic
winner is substituted. The primary aggregate mean and count pass the fixed gross gate.

## Costs and data clocks

Native MNQ research costs are$1.24RT+$0.50each market/stop fill=$2.24for two fills; gross hurdle2x=$4.48.
They are assumptions, not fresh broker quotes or verified native MNQ prices/fills. The gross screen
deducts none of them. Immediate receipt is assumed; observed historical receipt/spread/roll fidelity is
unverified. No passive target exists, so target-through is inapplicable to the later stopped rule.

Inputs were2018–22NQday+overnight and OF only, with no2017warm-up or2023+files. Native duplicate
conflicts0, OFconflicts0;485eligible held windows all valid. Strict flow was known for456events; unknown
states retained BASE. Metadata dates/clocks pass actual calendar/integer checks; exact past15ATRdate
references and calendar/early-close reasons are saved. No future g.trading membership or later-day OF
availability selects entries. Cash/early-close skips are known before entry; no14:30hold crosses15:59CT.

## Counted stopped design,2018-22

The shared execution engine used the frozen0.25ATRstop rounded UP to0.25points, active on entry,
worse gap fills and no target; stop/time exits cost two market/stop fills. The full daily axis includes
normal and early cash days after2018-01-22warm-up through2022-12-30, with known no-entry days at zero.
All485BASEtickets have complete held paths; zero exits after14:30/15:59CT and no duplicate events.
Source/calendar/ATR bindings and final code hash are preserved in design_verified_execution.json.

| Model | Trades | Net/MNQ | Trade t | Daily NW5 t | PF | Sharpe | Sortino | Calmar | Ulcer% | Max daily DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|BASE|485|3504.60|2.528|2.238|1.405|1.133|1.891|0.447|1.177|1585.10|
|LEGACY,unselectable|376|3627.76|2.856|2.518|1.542|1.276|2.275|0.665|0.831|1103.74|
|STRICT30,primary|383|3346.58|2.575|2.277|1.476|1.152|1.973|0.483|1.043|1402.44|

STRICT30win54.3%; four-tick-fill stress net$2197.58/MNQ. Its stopped gross$4204.50minus$857.92cost
equals$3346.58net. These are NQ-price simulations with independently calculated native MNQ costs,
not verified native MNQ fills. All216model/basis/side/year metric rows remain in design_metrics.csv.

| STRICT30side | Trades | Net/MNQ | Trade t | Daily NW5 t |
|---|---:|---:|---:|---:|
|Long|159|1657.34|2.286|2.283|
|Short|224|1689.24|1.564|1.448|

| STRICT30year | Trades | Net/MNQ | Trade t | Daily NW5 t |
|---|---:|---:|---:|---:|
|2018|81|798.56|2.126|1.828|
|2019|67|-572.08|-2.787|-2.485|
|2020|71|-101.04|-0.182|-0.156|
|2021|76|1251.26|1.976|1.718|
|2022|88|1969.88|2.255|2.120|

The primary removes102profitable BASEtrades: total$158.02,mean$1.549,t0.329. Its1000year/side/hour
matched subsets give32.9%strict joint profit/DD beats, below90%; randomprofit>=actual p0.176.
Selected IDs and every daily diagnostic path are retained. Higher average/PF and lower drawdown do
not rescue lower TOTALprofit or positive removed returns. LEGACY's better selected numbers do not
authorize nominating it; incomplete-window and prior selection limits remain explicit.

## Placebos, book and account disposition

Design_passed=false: three positive years instead of four; kept total<BASE; removed total/mean>0;
matched joint beat fraction<0.90. Therefore the preregistration stops BEFORE2023+or book testing.
No random-time/side promotion placebos, account Monte Carlo, funded bootstrap, evaluation-pass or
independent raw-spec promotion check ran. Their absence is a failed-gate stop, not a passing claim.

The planned current personal19rows remain unrun: BASEcurrent19,ADD1STRICT30micro,EMPTYremoveLDF1,
REPLACELDF1withSTRICT30one. Bench source and synthetic guards were prepared, but no financial bench
read/execution was authorized. STv3/PTv2are adopted, BB_MRMout; no stale-book or empty-slot improvement
is invented. No2023+candidate P&L is available for this hypothesis. No PL draft was written.

Verdict: **REJECT H01; preserve all failures and continue a different v2 hypothesis within57remaining
counted evaluations or9remaining hypotheses. Uploaded templates remain references only.**
