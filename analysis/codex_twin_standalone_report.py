"""Render and verify the frozen standalone replay artifacts; runs no further strategy tests."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis/outputs/codex_twin_standalone"


def table(frame, formats=None):
    x=frame.copy()
    for col,fmt in (formats or {}).items():
        if col in x:
            x[col]=x[col].map(lambda v:fmt.format(v) if pd.notna(v) else "—")
    return "| "+" | ".join(x.columns)+" |\n|"+"|".join(["---"]*len(x.columns))+"|\n"+"\n".join("| "+" | ".join(map(str,r))+" |" for r in x.to_numpy())


def main():
    manifest=json.loads((OUT/"manifest.json").read_text())
    metrics=pd.read_csv(OUT/"metrics.csv")
    control=pd.read_csv(OUT/"conditional_placebo.csv")
    mc=pd.read_csv(OUT/"monte_carlo.csv")
    boot=pd.read_csv(OUT/"bootstrap_seen_2023.csv")
    allrows=metrics[(metrics.period=="primary_all")&(metrics.side=="all")]
    trade_summary=[]; attribution=[]; validation=[]; percent=[]
    for name in manifest["configurations"]:
        t=pd.read_csv(OUT/f"trades_{name}.csv"); p=t[t.primary]
        s=allrows[allrows.variant==name].iloc[0]
        assert len(p)==int(s.trades) and np.isclose(p.net.sum(),s.total)
        assert np.allclose(p.net,p.pts*20-p.repo_cost)
        assert not p[["entry_date","entry_time_ct","setup","side"]].duplicated().any()
        assert (pd.to_datetime(p.exit_stamp)>=pd.to_datetime(p.entry_stamp)).all()
        d=pd.read_csv(OUT/f"daily_{name}.csv").iloc[:,1]
        assert np.isclose(d.sum(),p.net.sum())
        c=control[control.variant==name].iloc[0]
        assert c.same_side_max_error<1e-8 and int(c.same_side_exact_count)==len(p)
        trade_summary.append(dict(variant=name,all_2018_rows=len(t),all_2018_total=t.net.sum(),
                                  primary_rows=len(p),excluded_early_rows=len(t)-len(p)))
        z=p.net/(p.entry*20)*100
        percent.append(dict(variant=name,mean_net_percent_of_entry_notional=z.mean(),
                            t_net_percent_of_entry_notional=z.mean()/z.std()*np.sqrt(len(z))))
        validation.append(dict(variant=name,trade_count_matches=True,daily_sum_matches=True,
                                costs_match=True,unique_entry_keys=True,conditional_same_side_matches=True))
        if name=="combined":
            for setup,g in p.groupby("setup"):
                attribution.append(dict(setup=setup,trades=len(g),mean=g.net.mean(),total=g.net.sum()))
    assert manifest["fresh_combined_rows"]==manifest["matched_prior_entry_keys"]==manifest["prior_replica_rows"]
    assert manifest["matched_net_max_error"]<1e-8
    pd.DataFrame(percent).to_csv(OUT/"price_normalized_diagnostics.csv",index=False)
    (OUT/"verification.json").write_text(json.dumps(dict(checks=validation,
        prior_replica_all_entries_match=True,all_2018_sensitivity=trade_summary,
        primary_combined_attribution=attribution,performance_optimization=False),indent=2)+"\n")
    cols=["variant","side","trades","win","avg","t","profit_factor","sharpe","sortino","calmar","ulcer","max_dd"]
    fmt={"trades":"{:.0f}","win":"{:.1%}","avg":"${:,.0f}","t":"{:.2f}","profit_factor":"{:.2f}",
         "sharpe":"{:.2f}","sortino":"{:.2f}","calmar":"{:.2f}","ulcer":"{:.2f}","max_dd":"${:,.0f}"}
    primary=metrics[metrics.period=="primary_all"][cols]
    periods=metrics[metrics.period.isin(["2018-22","2023+_seen"])][["variant","period","side","trades","avg","t","profit_factor","sharpe","max_dd"]]
    years=metrics[(metrics.side=="all")&metrics.period.str.match(r"^20\d{2}(?:_partial)?$")]
    years=years.pivot(index="period",columns="variant",values="total").reset_index()
    summary=allrows[["variant","trades","win","avg","profit_factor","max_dd"]]
    b=boot[(boot.side=="all")&(boot.metric=="sharpe")][["variant","actual","p5","p95"]]
    risk=mc[mc.view=="one_year_daily_blocks"].pivot(index="variant",columns="size",values="p_trail_hit").reset_index()
    controls=control[["variant","actual_mean","conditional_mean","p95","p_ge_actual"]]
    report="""# Uploaded Twin Continuation standalone: WATCH for further verification; REJECT as pasted for Apex
Summary: Exact-default standalone replay is historically profitable: 1,030 primary trades, $330/NQ per trade, PF 1.65.
Realized daily max drawdown is $16,141 at 1 NQ; the worst trade is -$11,717 and four trades cross a flatten deadline.
BO-only and MO-only are profitable separately; these are independent opportunity sets, not summed portfolio results.
No parameters changed. All 1,075 full-2018 replay entries/P&L match the prior independent replica.
Keep the pasted version off Apex; platform/session parity and forward evidence remain unresolved.

Plan: `agents/codex/plans/twin_uploaded_standalone.md`, **8d661f1**. Evidence: `agents/codex/evidence/twin_uploaded_standalone.md`.
Scripts: `analysis/codex_twin_standalone.py`, `analysis/codex_twin_standalone_report.py`.
Output: `analysis/outputs/codex_twin_standalone/`. Replayed configurations **3**; optimized rules **0**.

## Rule (as tested)

The upload's executable code is identical to `checks/candidates/twin_continuation/Twin_Continuation.txt`; only a comment
differs. The preserved upload is `agents/codex/inputs/twin_continuation_uploaded.txt`; hashes are in the manifest.
This is a user-requested replication of an already-ranked strategy, not discovery of a new edge. Nothing was deployed.

NQ, one contract, close-stamped one-minute bars. Combined Twin permits one position and runs confirmed 6h swing
breakouts with opposite-swing stops and 2×15-minute ATR targets, plus 10-minute morning oscillator crossings at
08:40–09:30 CT, 75-point stops and 14:51 exits. BO_MaxStopMult stays **0**. BO-only disables MO; MO-only disables BO.
Each component-only run can take entries that combined Twin blocks while occupied, so their totals are not additive.

The existing independent simulator was imported unchanged. It interprets SetExitOnClose at the **stated 16:00 CT
session end**. Actual chart-session definitions can change this; the historical MC v2 export also contains holiday
inputs absent from the upload. This is a faithful replay of that documented model, not new exact MultiCharts confirmation.

Owned grid: 2017-12-01 through 2026-10-09, 3,105,552 observed minute bars. Six calendar months of warm-up gives
**2018-06-01** as the preregistered main start. No shared caches were rebuilt or data spliced. Full early 2018 is
reported only as short-warm-up sensitivity. 2023+ is previously seen history, not a fresh holdout. All times below are CT.

## Results

All dollar performance below is **per 1 NQ**, after $7.25 commission and one tick per market/stop fill; limit exits have
no slippage. One MNQ is one-tenth these modeled dollars, with a separate real micro fee schedule still needed.

"""
    report+=table(summary,fmt)+"\n\nWhole, longs and shorts, primary window:\n\n"+table(primary,fmt)
    report+="\n\n2018–22 begins June 2018; 2023+ ends at available October 2026 data:\n\n"+table(periods,fmt)
    report+="\n\nAnnual net dollars, 2018 partial and 2026 year-to-date:\n\n"+table(years,{c:"${:,.0f}" for c in years.columns if c!="period"})
    report+="\n\nThe full-2018 sensitivity includes 1,075 combined trades, versus 1,030 after the registered warm-up exclusion. "
    report+=f"Its total is ${trade_summary[0]['all_2018_total']:,.0f}; the primary total is ${allrows.iloc[0].total:,.0f}. "
    report+="All 1,075 entries and their net P&L match the archived independent replica to floating-point precision. "
    report+="The later start improves the total because the excluded period lost money; it was fixed from warm-up requirements, not selected here from returns.\n\n"
    report+="Within combined Twin, BO contributes 692 trades at $222 each and MO 338 at $550 each. Those are attribution "
    report+="figures; the independently traded legs above have different opportunities. Separate year/side metrics and price-normalized t diagnostics are saved.\n\n"
    report+="## Placebos and account level\n\nSeen-2023+ Sharpe moving-block-bootstrap 90% intervals (2,000 samples):\n\n"
    report+=table(b,{c:"{:.2f}" for c in ["actual","p5","p95"]})
    report+="\n\nRandom-side conditional controls, 1,000 assignments:\n\n"
    report+=table(controls,{"actual_mean":"${:.0f}","conditional_mean":"${:.0f}","p95":"${:.0f}","p_ge_actual":"{:.3f}"})
    report+="\n\nBoth directions were executed from each actual entry with mirrored stop/target distances and the source time exits. "
    report+="The actual-side reconstruction matches every primary trade in all three runs. These controls support direction value "
    report+="**conditional on the actual entries**; flipped trades can overlap or change later opportunities, so this is not a "
    report+="full-system placebo. Archived full-system/independent placebo evidence remains historical context. Bootstrap and "
    report+="drawdown-permutation results for all sides are in the output CSVs.\n\n"
    report+="One-year daily block-bootstrap probability of hitting a $2,000 EOD floor (5,000 samples):\n\n"
    report+=table(risk,{c:"{:.1%}" for c in risk.columns if c!="variant"})
    report+="\n\nThis is a **standalone risk diagnostic, not an Apex eligibility or payout simulation**. It uses realized exit-date "
    report+="P&L, so open losses, daily loss limits, account liquidation, fees at the real micro rate and holiday restrictions "
    report+="are not fully represented. A low number does not make the source legal or safe. At 1 MNQ, combined realized daily "
    report+="drawdown is about $1,614; its 95th-percentile one-year block-bootstrap drawdown is about $2,353. "
    report+="Sequential closed-trade drawdown is larger than daily-netted drawdown; both views are saved.\n\n"
    report+="The user requested individual testing, so no addition/replacement, portfolio optimisation or funded-payout bench was run. "
    report+="No account-scale recommendation follows from this report.\n\n"
    report+="## What could make this wrong\n\n"
    report+="- **Actual platform/session behavior:** SetExitOnClose can fire at midnight on a differently configured chart. "
    report+="The related MC v2 report has UseHolidayTimes/EarlyFlatten inputs not present in the upload. Neither its entries "
    report+="nor its returns are substituted for the literal uploaded-code replay. No new MultiCharts report was produced.\n"
    report+="- **Protection and fills:** with IOG off and exits issued only after MarketPosition changes, the entry minute "
    report+="has no protective order. The port preserves that exposure. Stop/target conflicts use the existing conservative "
    report+="intrabar convention; targets fill at touch and calculated ATR targets can be fractional ticks. Tick rounding, "
    report+="limit queue, adverse selection and the source's lack of live stop guards remain concerns.\n"
    report+="- **Sizing:** median initial BO stop risk is $6,290/NQ, largest $39,945; worst realized trade is -$11,717. "
    report+="At one MNQ the largest nominal stop risk is still about $3,995, above a $2,000 trail. The supplied Qty=1 means "
    report+="one NQ in these tables, not one MNQ.\n"
    report+="- **Calendar:** combined has 48 calendar-midnight crossings and four flatten-deadline breaches; those are "
    report+="different classifications. The breaches are BO on 2018-11-23, 2020-05-25, 2021-09-06 and MO on 2024-07-04. "
    report+="The last MO-only breach persists when that leg trades alone. All actual exits, including seven weekend BO "
    report+="exits, remain in the daily series; annualized metrics use the repository's 252-observation convention. "
    report+="This is realized accounting, not marked-to-market equity.\n"
    report+="- **Concentration and reused history:** the best 5% of combined trades supply about 71% of net dollars; "
    report+="2019 loses and 2026 contributes a large share. BO alone has weak 2018–22 evidence (t 1.52). MO-only short "
    report+="2023+ evidence is weak (t 1.29). Nothing was filtered or tuned after seeing these differences. "
    report+=f"DSR uses N={manifest['multiple_testing_n']}; combined full-primary DSR is {allrows.iloc[0].dsr:.3f}. "
    report+="Repeated historical success does not supply new forward validation.\n"
    report+="- **Costs:** source's $6 total/NQ convention gives combined $339/trade; repository costs give $330, and one "
    report+="additional tick on each fill gives $320. Better historical costs do not fix the path/implementation issues.\n\n"
    report+="## Differences between the MultiCharts code and the test\n\n"
    report+="No PowerLanguage changes were written. The upload is preserved unchanged. The Python engine is the prior "
    report+="independent replica, with the stated 16:00 session-close interpretation and documented minute-path assumptions. "
    report+="It is not a licensed MultiCharts execution engine. The six-month warm-up changes the primary evaluation "
    report+="window, not the trading rules; old short-warm-up history remains a labeled sensitivity. Simulated cost deductions "
    report+="do not move the raw entry prices or recompute exit distances from slipped fills.\n\n"
    report+="**Decision:** historical standalone edge remains credible enough for WATCH and further platform/forward "
    report+="verification. **Reject the pasted defaults for Apex use.** No new strategy, deployment or portfolio change is "
    report+="approved here. Tell Claude: review `agents/codex/results/twin_uploaded_standalone.md`; exact-code replication "
    report+="matched, with standalone BO/MO diagnostics and unresolved execution/account constraints.\n"
    path=ROOT/"agents/codex/results/twin_uploaded_standalone.md"
    path.write_text(report)
    print(path.relative_to(ROOT))


if __name__=="__main__":
    main()
