# Lab idea queue

Top `queued` idea runs next (priority 1 first, then order). One idea per line block. Fields: ID, status, priority, source,
market, mechanism (why someone must trade at a bad price), rule sketch, Apex-legal?, data. Runner fills `result:`.
New ideas: append with the next ID; follow-ups from a failure get `parent:` and go to the end.

## Q001 · done · priority 1
- source: Codex portfolio audit 2026-10-31 (diversify away from NQ: scheduled non-equity events)
- market: CL (MCL)
- mechanism: EIA weekly petroleum status report, Wed 09:30 CT. The first minutes overreact to the headline crude draw/build
  (algos trade the headline); refiners/hedgers trade the details afterward. Test fade vs follow of the 09:30-09:35 move.
- rule sketch: if |CL 09:30->09:35 move| >= 0.15 x 14-day ATR, enter at 09:36 open (V1 fade, V2 follow), stop 0.3 ATR,
  out 10:30 CT. V3: V1 only when the move is against the 08:30-09:30 drift.
- Apex: yes (MCL, intraday). data: data/CL_1min_*.csv (dates: every Wednesday; holiday weeks shift to Thursday 10:00 CT)
- result: skipped 2026-10-31, not tested: duplicate of the F-ranked 'CL forced flows' item in TIER_LIST.md
  (`analysis/cl_forced_flows_test.py`: follow +$11..21, fade -$65, t -2.5). Rule: never re-queue a D/F item.

## Q002 · done · priority 1
- source: Codex audit (non-equity); data/treasury_auctions.csv
- market: ZN (10-year note)
- mechanism: dealers must absorb 10-year auction supply; yields tend to rise (ZN falls) into the 12:00 CT auction as
  dealers pre-hedge, then recover after the result (Lou, Yan & Zhang 2013 'Anticipated and repeated shocks in liquid
  markets'). Test short ZN 08:30 -> 11:55 on 10-year auction days; long 12:05 -> 14:00.
- rule sketch: V1 short 08:30->11:55, V2 long 12:05->14:00, V3 both. Stop 0.5 x 14-day ATR.
- Apex: yes (user confirmed 2026-10-31). data: data/ZN_*, data/treasury_auctions.csv
- result: skipped 2026-10-31, not tested: duplicate of the D-ranked 'Treasury auction price pressure' item
  (`analysis/treasury_auction_test.py`: 10-year both legs +$38 gross vs $77 cost; rebound absent).

## Q003 · done · priority 2
- source: lab seed (non-equity, FX fixing flow)
- market: 6E (euro FX)
- mechanism: WM/Reuters 4 pm London fix (10:00 CT; 11:00 CT in DST-mismatch weeks): asset managers' FX hedging is
  executed at the fix, so 6E drifts into it and partly reverses after (Evans 2018; Melvin & Prins 2015 month-end).
- rule sketch: V1 month-end days only: follow the 09:30->09:55 CT move to 10:00, V2 fade 10:01->10:30, V3 V1 on every day.
- Apex: yes, 6E / M6E (user confirmed 2026-10-31). data: data/6E_1min_*.csv
- result: FAIL stage 1 (2026-10-31). 2018-22: V1 month-end follow into the fix 58 trades +$14.6 net (gross $32, PF 1.34,
  t 0.85, 3/5 yrs); V2 month-end post-fix fade -$6 (t -0.3); V3 every day -$15 (gross +$2, t -7.3). Month-end beats the
  same clock on other days (placebo p 0.000) but too few trades for t 2. Holdout not opened. `analysis/lab_Q003.py`.

## Q004 · done · priority 2
- source: lab seed (positioning)
- market: NQ (personal/weekly) or as a filter on ONB / Monday Long
- mechanism: extreme speculator positioning (COT non-commercial net long/short z-score) precedes mean reversion over 1-4
  weeks as crowded positions unwind.
- rule sketch: weekly: COT z(52w) of NQ non-commercial net; V1 long NQ Tue->Tue when z <= -1.5, V2 short when z >= 1.5,
  V3 as a size filter on ONB (2x when aligned). Personal-only for V1/V2 (multi-day).
- Apex: V3 only. data: data/COT_NQ.csv
- result: skipped 2026-11-01, not tested: same signal as the ranked COT items (Bridge COT Dealer Rank weekly hold C,
  as a day trade / plan filter F; CoT reversal index gate F). A z-score instead of a rank is a parameter tweak.

## Q005 · done · priority 2
- source: lab seed (gold)
- market: GC (MGC)
- mechanism: COMEX open 07:20 CT: physical/ETF flows hit after the overnight Asian/London price discovery; London PM fix
  (09:00 CT) is a benchmark trade time for bullion dealers. Test drift into the PM fix and reversal after.
- rule sketch: V1 follow the 07:20->08:55 move into 09:00; V2 fade 09:00->10:30; V3 V2 only on days |move| >= 0.3 ATR.
- Apex: MGC yes. data: data/GC_*, scratch gc.pkl
- result: skipped 2026-11-01, not tested: duplicate of F items (Antigravity edges: GC follow 7:20->8:30 and the PM fix
  8:45->9:00 to 10:30, t -0.5 / -0.8; S-rank round 1 LBMA AM / PM follow; LBMA auction short D).

## Q006 · done · priority 3
- source: lab seed (relative value, lowers net equity beta)
- market: NQ vs ES spread (MNQ/MES)
- mechanism: index arbitrage and rebalancing keep NQ/ES tied intraday; large intraday divergences (ratio z) partly close
  by the close as basket traders rebalance.
- rule sketch: at 12:00 CT if NQ/ES ratio return since 08:30 z(60d) >= 2: short NQ / long ES dollar-neutral to 14:55;
  V2 opposite sign; V3 threshold 1.5.
- Apex: yes (two legs, both intraday). data: g24.pkl, ge.pkl
- result: skipped 2026-11-01, not tested: duplicate of F items (decoupled NQ-ES mornings follow / fade t <= 0.6;
  NQ-ES Kalman pairs 17/18 versions lose, divergences keep widening from |z| >= 2).

## Q007 · done · priority 1
- source: Codex audit 2026-10-31; data supplied by the user 2026-10-31 (NG 1-min 2017-2026, converted ET -> CT)
- market: NG (QG / MNG micro: confirm which NG contract Apex lists)
- mechanism: EIA weekly natural-gas storage report, Thursday 09:30 CT (moved to Wed/Fri in holiday weeks). The first
  minutes react to the headline injection/withdrawal vs consensus; weather-driven hedgers and utilities trade after.
  Volume x10 on the 09:31 bar confirms the timing (2018-01-11). Test fade vs follow of the first 5 minutes.
- rule sketch: if |NG 09:30->09:35 move| >= 0.15 x 14-day ATR, enter at the 09:36 open: V1 fade, V2 follow, stop 0.3 ATR,
  out 10:30 CT; V3 V1 only in the heating season (Nov-Mar). Release days = Thursdays plus holiday shifts (infer from the
  09:31 volume spike when a Thursday is a holiday; never from returns).
- Apex: yes (user confirmed 2026-10-31). data: data/NG_1min_*.csv (CT, bar-end stamps like CL)
- result: FAIL stage 1 (2026-10-31). 2018-22, 131 trades: V1 fade -$82 net (t -1.5, 1/5 yrs), V2 follow -$5 (t -0.1;
  gross +$20 < $25 cost), V3 fade Nov-Mar -$2 (38 trades). Holdout not opened. `analysis/lab_Q007.py`.

## Q008 · blocked · priority 3
- source: Codex audit 2026-10-31
- market: ZC / ZS / ZW (grains)
- mechanism: USDA WASDE monthly 11:00 CT. Blocked: no grain minute data, and Apex eligibility of grains to confirm.

## Q009 · running · priority 2
- source: follow-up of Q007 (parent: Q007, depth 1)
- market: NG (QG)
- mechanism: pre-announcement drift: traders who must be flat or hedged into the storage number (utilities, weather funds
  cutting risk) trade before it, so NG drifts in a consistent direction 08:00 -> 09:29 CT on release days (event-risk premium,
  cf. Lucca & Moench 2015 pre-FOMC drift); different from Q007 (which traded the reaction).
- rule sketch: release days found by the 09:31 volume spike (as Q007). V1 long 08:00 -> 09:29, V2 short, V3 follow the
  overnight 17:00 -> 07:59 move into 09:29. Stop 0.3 x 14-day ATR. Placebo: same window on non-release weekdays.
- Apex: yes. data: data/NG_1min_*.csv (scratch ng.pkl)

## Q010 · queued · priority 2
- source: follow-up of Q003 (parent: Q003, depth 1)
- market: 6E (M6E)
- mechanism: month-end FX hedge rebalancing (Melvin & Prins 2015): foreign holders of US equities hedge the dollar; when
  US stocks rose over the month their hedge is too small, so they sell USD (buy EUR) into the month-end fix. The direction
  is known ex ante from the equity move, not from the 30-minute pre-fix price move Q003 used.
- rule sketch: last 6E session of the month, side = sign(ES month-to-date return at 08:30 CT); V1 enter 08:30, out at the
  fix (10:00 / 11:00 CT); V2 enter at fix-30, out at the fix; V3 V1 on the last 2 sessions. No stop. Placebo: same rule
  mid-month (15th or next session).
- Apex: yes. data: data/6E_1min_*.csv, ge.pkl (ES)
