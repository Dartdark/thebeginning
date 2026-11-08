# S30 / S47 / Kusho: TEST for bounded ingredient attribution

Summary: User explicitly requests these three existing families for the next ingredient round.
S30 is tested on NQ and ES; S47 uses v2 and Kusho uses roll-adjusted v9.
This tests dependence on rules, not a new strategy or portfolio allocation.

1. **Observation:** current source reviews report low-cash-close reversal for S30, cross-session momentum for
   S47, and pullback-limit entries in Kusho. Earlier author searches, source rebuilds and ablations are known.
2. **Mechanism:** liquidity normalization, cross-session information continuation and pullbacks within a trend
   are proposed explanations. Index drift and weekend risk-bearing are competing explanations. These bars do
   not identify forced actors; neither a wick nor London agreement establishes a causal flow.
3. **Information:** S30 uses the completed 08:30–15:00 cash session; S47 completed London and Chicago windows,
   past overnight range and actual timezone mapping; Kusho completed 15-minute bars, EMA and prior-day regime.
   Source roll detection is retrospective price-jump QA, not authenticated point-in-time contract metadata.
4. **Why money might remain:** exposure to undesirable inventory/overnight risk and different trading horizons
   are plausible. They do not establish persistent alpha or explain every historical profit.
5. **Costs and failure:** no-stop S30 carries large multiday risk. Kusho has unprotected fill bars, path-dependent
   break-even and possible weekend holds. S47's source also leaves the entry bar unprotected. Keep these defects
   visible rather than silently fixing them in an attribution experiment.
6. **Smallest falsifier:** five fixed definitions per family, changing entry selection, direction or an exit component;
   test total net and marked risk in both eras, preserving costs and state. S30 has two instrument replications,
   so 20 market/rule combinations, not 15. No selection among new optimized settings.
7. **Next use:** component evidence only, independently reviewed. Any changed or combined rule needs its own
   protocol, native fill/roll checks and current-book addition/replacement/empty comparisons before allocation.

S30 and Kusho share long-index/overnight risk with personal holdings; S47 overlaps morning NQ strategies such as
FC2B and RS. NQ/ES S30 legs are not presumed independent. A booked profit or unrelated later offset does not prove
survival before an account floor. No new target, stop, schedule, live deployment or account sizing is authorized here.

Verdict: **TEST — attribution only**, following the paired committed plan. No scout/trial-history reset.
