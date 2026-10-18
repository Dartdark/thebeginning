FAIL (gates 5/7: G1 significance and G8 regime fail). The flag is clean, replicates 100% and leaks nothing. The edge is plausible but has not shown the strength needed for promotion.

**Replication.** `replica.py` takes the 1-min bars stamped 08:31-15:00 CT from `NQ_1min_20*.csv` (= the 30-min bars closing 9:00-15:00; early-close days keep their short range). It finds NR7 as range <= min of the previous 6 sessions and flags the next session. It agrees with `flagged` on **942/942 trade days (100%)** and all 1,743 trades. Other definitions also agree: including the 08:30 bar 99.7%, strict `<` 99.8%, ending at 15:15 98.4%. So the spec is not ambiguous in any way that matters. The base trades come from MultiCharts and the checker cannot rerun MultiCharts. So `vb_replica.py` builds a rough Python Vault Break from `NQ_Vault_Break.txt` on g24, with $7.25 + 1 tick per market/stop fill. It gives 1,734 trades (MC 1,743), 93.5% day overlap and **daily P&L correlation 0.964**. On that list NR7 still helps but by less: **$185 vs $62, t 2.16; 2018-22 t 2.09, 2023-26 t 1.07**.

**Gates (maker list, kept = flagged; N = 239, t_threshold 3.53).**
- G1 FAIL: $217.2 (n 240) vs $60.3 (n 1,503), t 2.81 < 3.53. The pre-registered route is closed because 4 variants > 3. A Bonferroni test over just the 4 trials would pass (p about 0.01), but the checker's rule does not allow that.
- G2 PASS: +$174 (2018-22), +$140 (2023-26).
- G3 PASS: flagged beats the rest in 6/9 years (loses in 2019, 2021 and 2026 YTD, where it is -$153).
- G5 PASS: labels shuffled within years, p 0.0045.
- G6 PASS: 2023+ P(Sharpe<=0) 0.020.
- G7 PASS: 240 vs MinTRL 50.
- G8 FAIL: rho 0.55 < 0.60 (yearly Sharpe 2019 -1.0, 2026 -0.6).
- Replica folders: `vb_nr7_sizing_replica` gives the same result (identical flags). `vb_nr7_sizing_replica_pyvb` also scores 5/7 with the same two failures: G1 t 2.16, G5 p 0.037, G6 0.050, G8 0.55.

**Leak and trap checks.**
- Look-ahead: none. The flag uses only completed earlier sessions, and Monday uses Friday.
- Entries are all on :00/:30 between 10:30 and 14:30, long only.
- Costs: the net values cap at $775.5 and floor at -$1,524.5, which matches the stated $24.50 round trip. That is more conservative than the standard.
- Concentration: dropping the best 5/10/20 flagged days alone cuts t to 2.06/1.28/-0.19. Trimming the best 5-15% of days in BOTH groups keeps t at about 2.8. So the effect is spread across the distribution (stop-outs 12% vs 20%, win rate 73% vs 65%), not a few outliers.
- Day clustering: on per-day sums t is 2.52 (135 vs 807 days), a little weaker than the per-trade 2.81.
- Half-day artefact: 32 flagged trades come after an early-close session, whose short range makes NR7 almost automatic. They average -$136. Without them the effect is $272 vs $56 (t 3.80), but that is a post-hoc cut and must not be used to rescue the result.
- Neighbours: NR6-NR10 all give t 2.4-2.8, while NR4-NR5 give t of about 1.25. The effect is smooth, with no sharp peak at 7.
- Sizing: the 1x/3x choice was fitted afterwards on the bench, which is an extra degree of freedom. The spec also says MC "traded 2 contracts" while the sizing is 3. That is harmless for the per-contract test but should be fixed.

**What would change my mind.**
1. 2026-27 out-of-sample flagged trades beating the rest with day-clustered t >= 2 as the list grows. 2026 YTD is negative.
2. A ruling that the 4 pre-registered trials can be judged at t >= 2.0 with Bonferroni over 4 (both lists pass G1 at that bar), together with G8 above 0.60 on a longer sample.
3. The 2023-26 holdout is weak on both lists: t 1.57 on the MC list (2018-22 t 2.50) and t 1.07 on the Python list. A holdout t >= 2 on either would ease this; a lower one would confirm the edge is fragile.
