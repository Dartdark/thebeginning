"""Publish the portfolio audit from reconciled saved outputs; no experiments."""
from codex_portfolio_audit_config import *
import numpy as np
import pandas as pd
import re
os.environ.setdefault("MPLCONFIGDIR",str(RUNTIME/"matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME",str(RUNTIME/"cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def money(x):return f"${float(x):,.0f}" if pd.notna(x) else "N/A"
def num(x):return f"{float(x):.2f}" if pd.notna(x) else "N/A"
def pct(x):return f"{float(x):.1%}" if pd.notna(x) else "N/A"
def table(head,rows):
    return "\n".join(["| "+" | ".join(head)+" |","| "+" | ".join(["---"]*len(head))+" |"]+
                     ["| "+" | ".join(map(str,r))+" |" for r in rows])


verified=json.loads((OUT/"verification.json").read_text());assert verified["all_passed"] and verified["account_identity_and_each_payout_ladder_verified"]
metrics=pd.read_csv(OUT/"baseline_metrics.csv")
accounts=pd.read_csv(OUT/"account_summary.csv")
concentration=pd.read_csv(OUT/"market_concentration.csv")
risk=pd.read_csv(OUT/"personal_bootstrap_corrected.csv")
admission=pd.read_csv(OUT/"admission.csv")
sides=pd.read_csv(OUT/"long_short_attribution.csv")
retention=pd.read_csv(OUT/"trade_coverage_retention.csv")
e=concentration.set_index(["home","market"])
nq50=e.loc[("funded_50","NQ"),"covariance_share_of_daily_portfolio_variance"]
nq150=e.loc[("funded_150","NQ"),"covariance_share_of_daily_portfolio_variance"]
personal_eq=1-e.loc[("personal","CL_only"),"covariance_share_of_daily_portfolio_variance"]

text=[f"""# Current portfolio audit: concentrated equity risk; live-risk certification incomplete

Summary: Native-cost accounting is positive historically, but strategy count overstates market diversification.
NQ supplies{pct(nq50)}/{pct(nq150)} of50K/150K funded daily variance; equity-index sleeves supply{pct(personal_eq)} of personal variance.
Documented rosters and modeled native-cost integer quantities reconcile; missing adverse minutes and source-version/sizing gaps block a certified live-floor claim.
No strategy was added, removed, resized or promoted. The next alpha search should address this concentration with independently evidenced exposure.

Authorization: user requested a portfolio audit. [Evidence](../evidence/portfolio_audit_20261031.md),
[preregistered protocol and implementation corrections](../plans/portfolio_audit_20261031.md), initial commit `671f7f1`.
Source snapshot: Claude `{SOURCE_COMMIT}`. Exact initial audit code committed `e85fc0f` before outcomes;
later accounting/admission/preset corrections are separately committed and failed results retained.
Code: `analysis/codex_portfolio_audit_{{config,prepare,run,verify,diagnostics,report}}.py`.
Outputs: `analysis/outputs/codex_portfolio_audit_20261031/`; metadata, source/settings/cache hashes and parity records included.
New alpha definitions:0. Five existing homes; three declared cost scenarios. No removal/addition/replacement optimization.

## What this audit can establish

These are historical recorded-ledger diagnostics and conditional account-model baselines. They are not verified live
execution returns, a new prospective holdout, current account pass odds or certified Apex breach probabilities.
Main commission is$1.04 per micro round trip: the user reports MNQ measured$0.99–1.08 and uses$1.04; MES/MCL
have never been traded live and$1.04 is assumed. Main slippage is one native tick per market/stop fill, no slipped
target-limit exit. Native point/tick values are MNQ$2/.25, MES$5/.25, MCL$100/.01. Every reentry pays.
Fee sensitivity is$1.24RT/one tick; stress is$2.08RT/two ticks. Neither model quotes nor actual realized slippage are verified.

The earlier stored fund-plan curves often used$7.25/NQ divided by10=$0.725/MNQ; ES used$0.50/MES.
This audit rebuilds native cash/cost arithmetic from the recorded raw fills instead. It does not rescale a
full-contract dollar commission or silently count later missing order-flow signals as no trades.

## Frozen current rosters

Latest source commit6082472 explicitly reverses the funded Swing Target swaps.50K funded is VB2/1 plus T_ONESIDE;
150K is back to Dual Thrust2. Swing Target remains personal. The T_ONESIDE decision row misleadingly says
REVERTED while the current cushion table and NEW_CHAT_BRIEF retain T; this audit follows those explicit current inputs.
No old Swing Target funded allocation was substituted for today's portfolio.
"""]
text += [table(["Home","Frozen full-size inputs"],[[k,", ".join(f"{name}: "+(f"risk${v[1]} / {v[2]}ATR" if isinstance(v,list) else str(v)) for name,v in p.items())] for k,p in ROSTERS.items()]),
         "Personal: the source's19 labels at1micro per sleeve; S30 contains both MNQ and MES, so there are20 contract sleeves:17NQ,2ES,1CL. This is the full research book, not a small-account allocation recommendation.",
         "\n## Common window and admission\n",
         f"{START}–{END}. Start is after the documented ONB-ML warm-up; end is the Overnight Tick order-flow cutoff. The main source grid has2131 trading rows. Already-seen2018–22 and2023+ remain historical observations.",
         table(["Home","Known ledger sessions","Excluded size/fill days","Complete minute-path days"],
               [[r.home,int(r.admitted_sessions),int(r.excluded_sessions),int(r.complete_minute_path_sessions)]
                for r in admission[admission.scenario=="main"].itertuples()]),
         "A known entry/exit ledger can establish recorded close-to-close cash P&L even when an intervening minute is absent. It cannot establish the missing adverse excursion. Account tables below retain sparse observed-bar risk proxies and are conditional model sensitivities. Days with unresolved size/fill/session identity are excluded and enumerated; they are not known zero-return days. The surviving source-ledger samples are not fully current-version-certified.",
         table(["Selected source issue","Count / consequence"],[
             ["Missing CL held-minute OHLC bars",str(int(retention.query("home=='funded_50' and component=='CLS'").trades_missing_any_held_quote.iloc[0]))+" of87 recorded CL trades"],
             ["Missing OT held-minute OHLC bars",str(int(retention.query("home=='funded_50' and component=='OT'").trades_missing_any_held_quote.iloc[0]))+" of516 recorded OT trades"],
             ["Unknown VB single-print size flags","8 recorded VB trade days; funded size branches unknown"],
             ["Bridge price outside inferred chart-bar touch","1 common-window ledger day excluded from all relevant baselines"],
             ["Current calendar exclusions","2 Monday July3/Dec24 records and1 Good Friday NFP record skipped under current code"],
             ["MC open placeholder","1 unfinished ONB-ML row is not treated as a closed trade"]]),
         "Full counts and dates: `coverage_issues.csv`, `trade_coverage_retention.csv`, `source_coverage.csv`. The first all-complete-minute subset was retained separately; it removes almost all CL trades and cannot stand in for the full portfolio.",
         "\n## Current-book historical P&L at full size\n",
         "Actual integer full-size inputs before account cushion scaling, pauses, payout withdrawals or liquidations. Dollars are cumulative/annual cash P&L; PF here is **daily aggregate PF**, not roundtrip PF. Ulcer uses a$10,000 analytical denominator. Different capital/sizing means these rows are not equal-risk alternatives.",
         table(["Home","Sessions","Net","Annualized net","Sharpe","Sortino","Daily PF","Calmar","Ulcer","Max daily DD"],
             [[r.home,int(r.sessions),money(r.net),money(r.annual),num(r.sharpe),num(r.sortino),num(r.profit_factor),num(r.calmar),num(r.ulcer),money(r.max_dd)]
              for r in metrics.query("scenario=='main' and cohort=='all'").itertuples()]),
         "\nRecorded gross-to-net bridge for the four Apex rosters:",
         table(["Home","Recorded gross","Commissions","Slippage","Net"],
             [[r.home,money(r.gross),money(r.fees),money(r.slippage),money(r.net)]
              for r in metrics.query("scenario=='main' and cohort=='all' and home!='personal'").itertuples()]),
         "The personal full-book net combines source daily-marked and exit-booked components with corrected commission counts. A complete native **gross/roll/slippage bridge remains unverified** for its multi-day sleeves; no gross number is invented. Existing roll-jump adjustments do not establish actual contract roll fills or commissions.",
         "\nHistorical splits at the same full-size inputs:",
         table(["Home","Period","Annualized net","Sharpe","Max daily DD"],
               [[r.home,r.cohort,money(r.annual),num(r.sharpe),money(r.max_dd)]
                for r in metrics.query("scenario=='main' and cohort!='all'").itertuples()]),
         "\nYearly results remain in each home's `_years.csv`. Long/short attribution on the actual integer full-size recorded lots (before account scaling):",
         table(["Home","Side","Trades","Win","Annual net","Sharpe","Sortino","Roundtrip PF","Max daily DD"],
             [[r.home,r.side,int(r.trades),pct(r.win),money(r.annualized_native_cash),num(r.sharpe),num(r.sortino),num(r.profit_factor),money(r.max_dd)] for r in sides.itertuples()]),
         "Personal side attribution is not certified across the mixed daily/exit-booked multi-day sleeves; a full marked native ledger is needed. The source-qualified portfolio shorts remain profitable historically; the failed RL short result is not evidence for cutting these different strategies.",
         "\n## What loses together\n",
         "Daily variance attribution is Cov(market P&L,portfolio P&L)/Var(portfolio P&L), not a percentage of notional or capital. It can be negative or exceed100%; the groups reconcile to100%.",
         table(["Home","Market/group","Daily variance attribution"],[[r.home,r.market,pct(r.covariance_share_of_daily_portfolio_variance)] for r in concentration.itertuples()])]
for home in ["funded_50","funded_150","personal"]:
    a=pd.read_csv(OUT/f"{home}_contributions.csv").sort_values("net_on_worst5pct")
    text += [f"\n{home}: largest losses on its own worst5% historical known-ledger days. Dollar column is the sum over those days, not a forecast. This descriptive attribution does not select a removal.",
             table(["Component","Annual net","Net on portfolio worst5% days","Correlation with rest"],
                   [[r.component,money(r.annual),money(r.net_on_worst5pct),num(r.rest_correlation)] for r in a.head(5).itertuples()])]
text += ["A low average correlation does not establish crisis protection. S30's low whole-sample correlation can coexist with a large loss contribution on the personal book's worst days. More NQ strategies can still lose on the same equity-index moves."]

fig,ax=plt.subplots(figsize=(8,3.5),layout="constrained")
homes=["funded_50","funded_150","personal"]
cl=np.array([e.loc[(h,"CL" if h!="personal" else "CL_only"),"covariance_share_of_daily_portfolio_variance"] for h in homes])*100
eq=100-cl
ax.barh(homes,eq,label="Equity-index group",color="#395b8d")
ax.barh(homes,cl,left=eq,label="Crude oil",color="#d5a740")
for i,v in enumerate(eq):ax.text(v/2,i,f"{v:.1f}%",ha="center",va="center",color="white")
ax.set(xlim=(0,105),xlabel="Contribution to historical daily P&L variance (%)",title="Market concentration at current full-size inputs")
ax.legend(loc="upper center",bbox_to_anchor=(.5,-.2),ncol=2,frameon=False)
fig.savefig(OUT/"concentration.png",dpi=160);plt.close(fig)
text += ["![Market concentration](../../../analysis/outputs/codex_portfolio_audit_20261031/concentration.png)",
         "\n## Account-model baselines — conditional, not live probabilities\n",
         "Evaluations use fresh-start21-session historical windows, with every date in each window required to have known ledger/size identity. Starts overlap; they are not independent Bernoulli observations. They do not start from the user's current balance/floor.",
         table(["Home","Costs","Windows","Pass","Floor failure","Timeout","Median pass days"],
               [[r.home,r.scenario,int(r.n),pct(r.pass_rate),pct(r.failure_rate),pct(r.timeout_rate),num(r.median_pass_days)]
                for r in accounts.query("home.str.startswith('evaluation') and cohort=='all'",engine="python").itertuples()]),
         "Funded rows use500 synchronized20-observed-day block histories,500-session horizon, the same history per cost scenario. Source rules:50K/$2k EOD trail/$13k six-payout cap;150K/$4k trail/$20.5k cap. Sizes use source daily cushion scaling, then whole lots. Repository intraday-path account rules are retained; caps/parameters and all payout amounts now independently reconcile.",
         table(["Home","Costs","Year1 mean payout","Year2 mean payout","Year2 p5","Failed by500d","All six","Median sixth day"],
               [[r.home,r.scenario,money(r.y1),money(r.y2),money(r.y2_p5),pct(r.failure_rate),pct(r.all6_rate),num(r.median_sixth_days)]
                for r in accounts.query("home.str.startswith('funded')",engine="python").itertuples()]),
         "Median sixth day includes non-completers as infinity. These ranges and frequencies condition on historical selections, observed prices and inherited rules; they do not include unseen-regime, data, order, model or selection uncertainty. A more expensive fee scenario need not monotonically worsen a stateful path: fees change cushion sizing and payout timing. A few histories' sampling differences are not an execution benefit.",
         "Remaining floor-model limitations: missing adverse minutes; inferred within-bar entry/fill order; source stop/gap behavior; unverified current-version/input parity; broker-level netting/rejections; contract caps; and mutually incompatible per-strategy high/low extrema when NQ longs and shorts overlap. These prevent an unconditional account-safety conclusion."]
for home in ["funded_50","funded_150"]:
    x=pd.read_csv(OUT/f"{home}_exposure.csv").query("market=='NQ'").iloc[0]
    text += [f"{home}: opposite NQ positions appear on{int(x.days_with_opposite_positions)} days / {int(x.opposite_position_minutes):,} inferred held minutes. Summing each side's separate adverse extreme can exaggerate simultaneous NQ risk; daily correlation cannot fix that chronology."]
text += ["\n## Personal-account capital and sizing\n",
         table(["Costs","Median252-session P&L","P&L p5","Daily-equity DD p95","Capital at20% modeled-DD rule"],
               [[r.scenario,money(r.pnl_p50),money(r.pnl_p5),money(r.dd_p95),money(r.capital_at20pct_rule)] for r in risk.itertuples()]),
         "Same5000 source20-day bootstrap draws, now including the initial-equity peak in drawdown. This is a descriptive conditional daily-ledger risk calculation, not margin certification or an executable capital recommendation. No negative sampled years does not establish zero future loss probability. Twin v1/version mismatch, Kusho exit-day booking and unresolved real contract rolls can distort both loss timing and drawdown.",
         "The printed sizing loop `max(1,floor(...))` forces at least1x even when the stated20% risk budget cannot fund1x. It should not be used to size the full19-sleeve book at$10,000. The separate documented ladder uses smaller subsets, but its16-piece core is stale after Swing Target/PAPERTREND additions: today's no-S30 full-book diagnostic has18 strategy labels. Reconcile and revalidate the ladder before treating its capital thresholds as current.",
         "\n## Audit decisions and required repairs\n",
         table(["Home","Audit verdict"],[
             ["50K evaluation","Recorded native-cost historical baseline computed; current live pass odds/floor safety not certified"],
             ["150K evaluation","Same; own risk budget floored before execution, not50K quantities multiplied2.5"],
             ["50K funded","Current VB2/1+T roster audited; no new allocation selected; source/minute-risk certification incomplete"],
             ["150K funded","DT2 roster audited; resolve fractional source sizing intentions versus actual integer full-size inputs"],
             ["Personal","Historical full-book accounting/risk diagnostic computed; current-version/native-roll/margin and updated ladder incomplete"]]),
         "1. **Reconcile the risk baseline before scaling decisions.** Freeze exact MultiCharts versions/inputs, per-trade StopPts/ATR/quantity and native fee/order records. Complete or explicitly certify sparse-bar capture semantics for the listed held minutes. Keep chart-model trades separate from broker fills. Actual quotes or a documented no-trade-minute convention are needed; filling bars without evidence is insufficient.",
         "2. **Resolve150K sizing inputs.** Legacy source uses1.5 for flagged VB/Monday/Bridge. Atf=.75, floor(1.5*.75)=1, whereas an actual full-size input1 gives floor(1*.75)=0. The audit preserves the disclosed source convention; it cannot certify which integer chart setting will be installed. See `fixed_lot_sizing_audit.csv`.",
         "3. **Review the documented thin-cushion policy without silently changing it.** The latest brief reports$1,064 of50K evaluation cushion. VB8 at75points risks$1,200 before costs. On a continuous price path the$1,000 account DLL should pause first, leaving only$64 between that boundary and the floor before costs/gaps. This is a buffer calculation from a dated brief, not a prediction that the next trade must fail or a fresh live balance check.",
         "4. **Update the personal capital ladder and exact-version marked ledgers.** Obtain the literal Twin v2.1 ledger, session-marked Kusho positions and real contract/roll/cost records; rebuild capital/margin checks at actual integer sizes. Do not reuse the stale16-piece core threshold for today's larger book.",
         "5. **Target different market risk in further alpha research.** The concentration result supports looking for independently evidenced non-equity exposures. It does not establish that a particular commodity, short signal, filter or new strategy will improve this portfolio. Existing accepted/rejected research and forward gates still apply.",
         "No strategy was removed based on worst-day attribution, no signal parameters were tuned, and no BASE/ADD/REPLACE/EMPTY allocation search was run. Placebo/promotion tests are not applicable to this accounting audit; any proposed allocation change needs its own frozen comparison. The audit does not override the user's current trading decisions.",
         "\n## Verification and retained implementation failures\n",
         "Seven synthetic finance/clock/sizing groups pass. Independent native unit-ledger, component/daily cost and side totals reconcile. Twenty-four exact finite-state/repository account parity comparisons pass, plus separate account-identity and cumulative payout-ladder checks. Scenario histories are paired by saved dates. Checks establish arithmetic and source-simulator parity, not independent economic review or actual execution certification.",
         "The first preparation stopped on missing single-print flags. Its deterministic admission correction was committed before baseline outputs. The first all-complete-minute diagnostic is archived under `initial_complete_path_subset/` and is unrepresentative of the full CL book. The subsequent first known-ledger run exposed an audit-runner preset bug: `funded_150.endswith('50')` selected50K rules. All those outcomes are retained under `implementation_wrong_150_preset/`; their150K account results are **invalid**. The explicit mapping, source account-start assertions and independent cumulative caps corrected this without changing strategies/costs/history seeds. The initial complete-path subset's150K account outputs share that defect and are invalid too. Use only the verified final root outputs for the tables here.",
         "The shared strategy, loader, account engine, live, VPS and broker files were not edited. All changes are research code/evidence. Exact source/data/code identities are in `preparation.json`, `run_manifest.json` and per-account `_account_rules.json`; the failed-run source hashes remain in their archives. Independent review of this audit remains pending.",
         "For Claude: `agents/codex/results/portfolio_audit_20261031.md`. Useful native-cost, information-clock and account-path lessons are retained in [E09/E43 of the execution-reference library](../EXECUTION_REFERENCES.md). Remaining research-only input needs are in [DATA_NEEDED.md](../DATA_NEEDED.md). No live change is authorized by this report."]

path=ROOT/"agents/codex/results/portfolio_audit_20261031.md"
parts=re.split(r"(`[^`]*`|\[[^\]]*\]\([^)]*\))","\n\n".join(text))
for i in range(0,len(parts),2):
    parts[i]=re.sub(r"(?<=[A-Za-z])(?=\$)"," ",parts[i])
    parts[i]=re.sub(r"(?<=[a-oq-uw-z])(?=\d)"," ",parts[i])
    parts[i]=re.sub(r"(?<=\d)(?=[A-JL-Za-wyz])"," ",parts[i])
path.write_text("".join(parts).rstrip()+"\n")
print(path)
