# Lab idea queue

Top `queued` idea runs next (priority 1 first, then order). One idea per line block. Fields: ID, status, priority, source,
market, mechanism (why someone must trade at a bad price), rule sketch, Apex-legal?, data. Runner fills `result:`.
New ideas: append with the next ID; follow-ups from a failure get `parent:` and go to the end.

## Q001 · queued · priority 1
- source: Codex portfolio audit 2026-10-31 (diversify away from NQ: scheduled non-equity events)
- market: CL (MCL)
- mechanism: EIA weekly petroleum status report, Wed 09:30 CT. The first minutes overreact to the headline crude draw/build
  (algos trade the headline); refiners/hedgers trade the details afterward. Test fade vs follow of the 09:30-09:35 move.
- rule sketch: if |CL 09:30->09:35 move| >= 0.15 x 14-day ATR, enter at 09:36 open (V1 fade, V2 follow), stop 0.3 ATR,
  out 10:30 CT. V3: V1 only when the move is against the 08:30-09:30 drift.
- Apex: yes (MCL, intraday). data: data/CL_1min_*.csv (dates: every Wednesday; holiday weeks shift to Thursday 10:00 CT)

## Q002 · queued · priority 1
- source: Codex audit (non-equity); data/treasury_auctions.csv
- market: ZN (10-year note)
- mechanism: dealers must absorb 10-year auction supply; yields tend to rise (ZN falls) into the 12:00 CT auction as
  dealers pre-hedge, then recover after the result (Lou, Yan & Zhang 2013 'Anticipated and repeated shocks in liquid
  markets'). Test short ZN 08:30 -> 11:55 on 10-year auction days; long 12:05 -> 14:00.
- rule sketch: V1 short 08:30->11:55, V2 long 12:05->14:00, V3 both. Stop 0.5 x 14-day ATR.
- Apex: yes (user confirmed 2026-10-31). data: data/ZN_*, data/treasury_auctions.csv

## Q003 · queued · priority 2
- source: lab seed (non-equity, FX fixing flow)
- market: 6E (euro FX)
- mechanism: WM/Reuters 4 pm London fix (10:00 CT; 11:00 CT in DST-mismatch weeks): asset managers' FX hedging is
  executed at the fix, so 6E drifts into it and partly reverses after (Evans 2018; Melvin & Prins 2015 month-end).
- rule sketch: V1 month-end days only: follow the 09:30->09:55 CT move to 10:00, V2 fade 10:01->10:30, V3 V1 on every day.
- Apex: yes, 6E / M6E (user confirmed 2026-10-31). data: data/6E_1min_*.csv

## Q004 · queued · priority 2
- source: lab seed (positioning)
- market: NQ (personal/weekly) or as a filter on ONB / Monday Long
- mechanism: extreme speculator positioning (COT non-commercial net long/short z-score) precedes mean reversion over 1-4
  weeks as crowded positions unwind.
- rule sketch: weekly: COT z(52w) of NQ non-commercial net; V1 long NQ Tue->Tue when z <= -1.5, V2 short when z >= 1.5,
  V3 as a size filter on ONB (2x when aligned). Personal-only for V1/V2 (multi-day).
- Apex: V3 only. data: data/COT_NQ.csv

## Q005 · queued · priority 2
- source: lab seed (gold)
- market: GC (MGC)
- mechanism: COMEX open 07:20 CT: physical/ETF flows hit after the overnight Asian/London price discovery; London PM fix
  (09:00 CT) is a benchmark trade time for bullion dealers. Test drift into the PM fix and reversal after.
- rule sketch: V1 follow the 07:20->08:55 move into 09:00; V2 fade 09:00->10:30; V3 V2 only on days |move| >= 0.3 ATR.
- Apex: MGC yes. data: data/GC_*, scratch gc.pkl

## Q006 · queued · priority 3
- source: lab seed (relative value, lowers net equity beta)
- market: NQ vs ES spread (MNQ/MES)
- mechanism: index arbitrage and rebalancing keep NQ/ES tied intraday; large intraday divergences (ratio z) partly close
  by the close as basket traders rebalance.
- rule sketch: at 12:00 CT if NQ/ES ratio return since 08:30 z(60d) >= 2: short NQ / long ES dollar-neutral to 14:55;
  V2 opposite sign; V3 threshold 1.5.
- Apex: yes (two legs, both intraday). data: g24.pkl, ge.pkl

## Q007 · queued · priority 1
- source: Codex audit 2026-10-31; data supplied by the user 2026-10-31 (NG 1-min 2017-2026, converted ET -> CT)
- market: NG (QG / MNG micro: confirm which NG contract Apex lists)
- mechanism: EIA weekly natural-gas storage report, Thursday 09:30 CT (moved to Wed/Fri in holiday weeks). The first
  minutes react to the headline injection/withdrawal vs consensus; weather-driven hedgers and utilities trade after.
  Volume x10 on the 09:31 bar confirms the timing (2018-01-11). Test fade vs follow of the first 5 minutes.
- rule sketch: if |NG 09:30->09:35 move| >= 0.15 x 14-day ATR, enter at the 09:36 open: V1 fade, V2 follow, stop 0.3 ATR,
  out 10:30 CT; V3 V1 only in the heating season (Nov-Mar). Release days = Thursdays plus holiday shifts (infer from the
  09:31 volume spike when a Thursday is a holiday; never from returns).
- Apex: yes (user confirmed 2026-10-31). data: data/NG_1min_*.csv (CT, bar-end stamps like CL)

## Q008 · blocked · priority 3
- source: Codex audit 2026-10-31
- market: ZC / ZS / ZW (grains)
- mechanism: USDA WASDE monthly 11:00 CT. Blocked: no grain minute data, and Apex eligibility of grains to confirm.
