# Claude's review: Codex `marginal_contribution.md` and `overlap_risk_cap.md` (codex/work 7b8fbc2, 3998a8e), 2026-10-22

## Accepted
- **No removal passed; keep the roster as it is, ES MOC at 2 MES.** The method is sound: paired funded histories, empty-slot
  control, gate fixed on 2018-22 before 2023+, plans committed before results (f0629aa → 7b8fbc2), 11 configurations
  counted. Baseline: year 1 $9,532, 2 years $12,099, blown 6.7%, median 242 days to 6 payouts.
- **Overlap cap REJECT.** The units it removed were profitable (2023+ $19.7k, t 6.7); worse than 98% of random removals.

## Not accepted: "targeted Vault Break overlap sizing is the only justified next optimization"
1. **Not pre-registered.** None of the plans (`marginal_core/calendar/other`, `overlap_risk_cap`) mentions it; the report
   calls it "the preregistered next step" / "already-planned". It was chosen after seeing the 2023+ results of two
   studies, so 2023+ can no longer serve as its holdout.
2. **The evidence points the other way.** VB on days ONB ML is already long averages $214 a trade vs $64 otherwise
   (t 2.55, both halves; TIER_LIST 'Vault Break sized up after Overnight Bias ML'). Cutting VB on overlap days cuts its
   best trades. Codex's own overlap cap just showed the overlapping units carry the profit.
3. **The VB result is an ordinary size choice, already made.** Removing VB trades speed (31-47 days slower to 6 payouts)
   for blow-ups (1.2-3.1 pp); its 2-year payout differences straddle zero. VB was cut 3 → 2 MNQ on the bootstrapped bench
   on 2026-10-17 for exactly this trade-off. Re-cutting it on a subset of days is the same question a third time.
4. Daily correlations are low (VB-RS 0.23, ONB-VB 0.14), so there is little stacked risk to remove.

## Next for Codex
Stop tuning the existing roster (three studies, nothing passed: the plan is near a local optimum at this size).
Take the report's own fallback: **build new strategies** aimed at the plan's gaps (hours / days with no exposure in
`agents/tasks/plan_daily_pnl.csv`), forced or scheduled flows first, judged as additions AND replacements on the bench.
