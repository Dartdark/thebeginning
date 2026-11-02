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

## Q009 · done · priority 2
- source: follow-up of Q007 (parent: Q007, depth 1)
- market: NG (QG)
- mechanism: pre-announcement drift: traders who must be flat or hedged into the storage number (utilities, weather funds
  cutting risk) trade before it, so NG drifts in a consistent direction 08:00 -> 09:29 CT on release days (event-risk premium,
  cf. Lucca & Moench 2015 pre-FOMC drift); different from Q007 (which traded the reaction).
- rule sketch: release days found by the 09:31 volume spike (as Q007). V1 long 08:00 -> 09:29, V2 short, V3 follow the
  overnight 17:00 -> 07:59 move into 09:29. Stop 0.3 x 14-day ATR. Placebo: same window on non-release weekdays.
- Apex: yes. data: data/NG_1min_*.csv (scratch ng.pkl)
- result: FAIL stage 1 (2026-11-01). 2018-22, 254 release days: V1 long -$116 (t -3.4, 0/5 yrs), V2 short +$13 (gross $38,
  PF 1.08, t 0.36), V3 follow the overnight -$44 (t -1.2); non-release days -$2 (placebo p 0.33). Holdout not opened.
  `analysis/lab_Q009.py`. No follow-ups.

## Q010 · done · priority 2
- source: follow-up of Q003 (parent: Q003, depth 1)
- market: 6E (M6E)
- mechanism: month-end FX hedge rebalancing (Melvin & Prins 2015): foreign holders of US equities hedge the dollar; when
  US stocks rose over the month their hedge is too small, so they sell USD (buy EUR) into the month-end fix. The direction
  is known ex ante from the equity move, not from the 30-minute pre-fix price move Q003 used.
- rule sketch: last 6E session of the month, side = sign(ES month-to-date return at 08:30 CT); V1 enter 08:30, out at the
  fix (10:00 / 11:00 CT); V2 enter at fix-30, out at the fix; V3 V1 on the last 2 sessions. No stop. Placebo: same rule
  mid-month (15th or next session).
- Apex: yes. data: data/6E_1min_*.csv, ge.pkl (ES)
- result: FAIL stage 1 (2026-11-01). 2018-22: V1 08:30 -> fix -$47 (t -0.9), V2 fix-30 -> fix -$12 (t -0.3), V3 last 2
  sessions +$5 (gross $23, PF 1.05, t 0.17; longs +$15, shorts -$15); mid-month control -$31; placebo p 0.13. Holdout not
  opened. `analysis/lab_Q010.py`. No follow-ups (depth limit reached for a strong mechanism).

## Q011 · blocked · priority 1
- source: lab refill 2026-11-01 (non-NQ scheduled flow; TIER_LIST has no NG expiry item)
- market: NG (QG)
- mechanism: NG final settlement (last trade = 3 business days before the 1st of the delivery month, settles 13:30 CT on
  the 13:00-13:30 VWAP) sets the price of monthly-index physical gas ("bidweek"); utilities and marketers who buy or sell
  next month's gas at index must hedge into that window, and the expiring contract's volume rolls to the next. Test the
  settlement-window drift and the reversal after, on the front contract.
- rule sketch: expiry day from the CME rule (3 business days before the 1st, NYMEX holidays): V1 follow the 08:00 -> 12:55
  move 13:00 -> 13:29; V2 fade it 13:31 -> 14:30 (next contract only if the data has rolled; check first); V3 V1 on the
  day before expiry. Stop 0.3 ATR.
- Apex: yes (check the contract roll in data/NG_1min_*: unadjusted front month?). data: data/NG_1min_*.csv
- result: BLOCKED 2026-11-01 (no returns run). data/NG_1min_* rolls to the next contract at the evening open before
  the expiry session: expiry-day 08:00-13:30 volume 4.9x the day before (median, 107 expiries), evening-open gap 0.038 vs
  0.017 ATR normally. The expiring contract's 13:00-13:30 settlement is not in the data; needs a contract-specific export
  (NGx expiring month, 1-min, last 5 days) from MultiCharts.

## Q012 · done · priority 2
- source: lab refill 2026-11-01 (ECB not in TIER_LIST)
- market: 6E (M6E)
- mechanism: ECB policy decision (07:15 CT since 2022, 06:45 CT before) and press conference (+30 min): FX order flow
  after scheduled macro news keeps moving the price for hours as real-money accounts reposition (Evans & Lyons 2008:
  order flow carries news slowly); the press-conference move is the information, the decision headline mostly priced.
- rule sketch: ECB days inferred from the 6E volume spike at the decision minute on Thursdays (never from returns; ~8 a
  year). V1 follow decision -> press-conference end (+90 min) into 10:30 CT; V2 fade it; V3 follow the press-conference
  part only (+30 -> +90). Stop 0.3 ATR. Placebo: same clock on other Thursdays. Event study: >= 40 trades needs 2018-22's ~40.
- Apex: yes. data: data/6E_1min_*.csv
- result: FAIL stage 1 (2026-11-01). Amended calendar (13:45 Berlin before 2022-07, 14:15 after; volume >= 5x finds 33 of
  ~40 meetings 2018-22): V2 fade +$31 (gross $49, PF 1.18, t 0.40, 4/5 yrs), V3 +$27 (t 0.37), V1 -$34; other Thursdays
  -$11, placebo p 0.19; first (ADP-contaminated) run: V2 +$37, t 0.59. Holdout not opened. `analysis/lab_Q012.py`.

## Q013 · done · priority 2
- who_pays: information: slower FX participants (European real-money hedgers) act on the payrolls news hours after it prints
- tier_check: master 2026-11-01, dupcheck 'NFP 6E': only the F-ranked 6E London-fix reversal (different event); clear
- source: lab refill 2026-11-01 (NFP on 6E untested; NQ NFP fade is a plan strategy, 6E is not)
- market: 6E (M6E)
- mechanism: US payrolls (07:30 CT, first Friday) reprice the dollar; FX order flow after macro news persists (Evans &
  Lyons 2008), and European real-money hedgers act after their lunch, before the London close (10:00 CT fix).
- rule sketch: NFP days from the plan's NFP calendar (NFP_Fade). V1 follow the 07:30 -> 07:45 move from 07:46 to 09:55 CT;
  V2 fade it; V3 V1 only when |move| >= 0.3 ATR. Stop 0.3 ATR. Placebo: same clock on other Fridays.
- Apex: yes. data: data/6E_1min_*.csv
- result: FAIL stage 1 (2026-11-01). 62 NFP days 2018-22 (volume >= 5x at 07:31; 12-14 a year, a few may be CPI Fridays):
  V1 follow -$47 (t -1.2, 0/5 yrs), V2 fade -$8 (gross +$10, t -0.2), V3 big moves follow -$36 (17 trades); other Fridays
  -$27, placebo p 0.23. Holdout not opened. `analysis/lab_Q013.py`. No follow-ups.

## Q014 · done · priority 2
- who_pays: structural: Chinese physical buyers are absent while Shanghai is closed, so London / US selling meets fewer bids
- tier_check: master 2026-11-01, dupcheck 'golden week' / 'lunar new year': only an unrelated gold-valuation paper; clear
- source: lab refill 2026-11-01 (not in TIER_LIST: no Golden Week / Lunar New Year item)
- market: GC (MGC)
- mechanism: Chinese physical gold demand (SGE, the largest physical market) is absent while China is closed for Lunar
  New Year and the October Golden Week; dealers' Asian bids that normally absorb London / US selling are missing, so
  gold drifts weaker on those days and recovers after Shanghai reopens.
- rule sketch: SGE closure days from the official holiday calendar (hard-code 2018-26 from the SGE notices; no returns
  used). V1 short GC 07:20 -> 12:25 CT on each closure weekday; V2 long the first 2 sessions after the reopening;
  V3 V1 only on the first 3 closure days. Stop 0.3 ATR. Placebo: same clock on random non-closure weekdays.
- Apex: yes (MGC). data: data/GC_1min_*.csv; SGE holiday dates (to build, write data/sge_holidays.csv first)
- result: FAIL stage 1 (2026-11-02). Calendar data/sge_holidays.csv (97 weekdays 2018-26). 2018-22: V1 short closure days
  52 trades -$80 (t -0.85, 1/5 yrs), V2 long reopen -$81 (20 trades), V3 short first 3 days -$251 (t -2.1, 0/5: gold ROSE,
  opposite sign; 30 trades, not flipped post hoc). Placebo p 0.62. Holdout not opened. `analysis/lab_Q014.py`. No follow-ups.

## Q015 · queued · priority 3
- who_pays: structural: TAS orders and dealers' basis / roll hedges must trade at the ZN settlement window, whatever the price
- tier_check: master 2026-11-01, dupcheck 'ZN settle': no ZN settlement row (CL / GC settlement are F, per its source line); clear
- source: lab refill 2026-11-01 (ZN daily settlement not in TIER_LIST; CL / GC settlement versions are F)
- market: ZN
- mechanism: Treasury futures settle on the 13:59-14:00 CT window; TAS orders and hedgers marking books to settlement
  trade into it, and dealers' basis / roll hedges are executed against it daily. Test follow into and fade after.
- rule sketch: V1 follow the 12:00 -> 13:55 move 13:56 -> 14:00; V2 fade the 12:00 -> 14:00 move 14:01 -> 15:00; V3 V2 only
  when |move| >= 0.3 ATR. Stop 0.3 ATR. Power: ~250 trades a year. Cost warning: ZN round trip $36.25 vs a typical
  1-hour ZN move of ~4 ticks: stop at stage 1 unless gross > $50.
- Apex: yes. data: data/ZN_1min_*.csv

## Q016 · done · priority 1
- source: scout 2026-11-01: Kurov, Sancetta, Strasser & Wolfe, 'Price Drift before U.S. Macroeconomic News: Private
  Information about Public Announcements?' (ECB WP 1901 / JFQA 2019; `papers/ecb-wp1901-kurov-predrift.pdf`). Not in
  TIER_LIST (only the CL EIA pre-release drift is ranked).
- market: ES and ZN (MES / ZN)
- mechanism: for 7 of 21 market-moving releases (2008-14) ES and ZN start moving in the eventual direction ~30 minutes
  before the 09:00 CT release and the pre-move is about half the total reaction; the authors trace it to leakage and to
  traders who collect proprietary data and must act before the number (someone trades early at the informed side's
  price). Test whether the pre-move still predicts the post-release continuation in 2018-22 (leakage may have fallen
  after the 2013-15 SEC / lock-up changes; a fail is informative).
- rule sketch: release days from fixed calendar rules, no returns used: ISM Manufacturing (1st business day, 09:00 CT)
  and Conference Board consumer confidence (last Tuesday, 09:00 CT); confirm each date by the 09:00 volume spike, drop
  days with a 07:30 release in the same session. Signal = sign of the 08:35 -> 08:58 move (skip if < 0.05 x 14-day ATR).
  V1 ES follow from the 08:59 open to 09:10; V2 ES follow to 09:30; V3 = V1 on ZN. Stop 0.3 ATR. Placebo: same clock on
  non-release weekdays. Power: ~24 events a year, ~120 in 2018-22.
- Apex: yes (intraday). data: data/ES_1min_*.csv, data/ZN_1min_*.csv
- result: FAIL stage 1 (2026-11-01). Amended day selection (calendar only; the ES 09:00 volume confirm kept 13 days):
  95 design days, 75 ES trades: V1 to 09:10 +$36 (gross $66, PF 1.28, t 0.76, 2/5 yrs: 2022 = +$3,140 of +$2,670),
  V2 to 09:30 +$50 (t 0.73, 4/5), V3 ZN -$35 (gross +$2, t -2.1); non-release days -$22, placebo p 0.06. First run
  (10 trades) V2 t 1.49. Holdout not opened. `analysis/lab_Q016.py`. No follow-ups.

## Q017 · queued · priority 2
- who_pays: structural: trend-following funds (CTAs) rebalance on fixed turn-of-month dates, trading size in the trend direction
- tier_check: master 2026-11-01, dupcheck 'turn of the month': C equity calendar row + D personal overnight round (ES/NQ TOM long); trend-direction commodity TOM is new; clear
- source: scout 2026-11-01: Van Hemert, 'MOM-TOM: Momentum and the Turn of the Month' (2014 working paper; SSRN PDF not
  in repo, summaries via Quantpedia / CXO): 90% of the Newedge trend index return came on the 3 turn-of-month days
  2000-14, partly reversed after, strongest in less liquid commodities. Not in TIER_LIST (its 'Turn of the month' rows
  are long-equity calendar trades, not trend-direction flow in commodities).
- market: CL, NG, GC, ZN, 6E (micros), pooled at equal ATR risk
- mechanism: CTA fund flows arrive at month-end and are invested at the turn of the month in the direction of each
  market's trend, so trend-direction buying / selling is concentrated on known days; it is price pressure (partly
  reverses), so the trade is in the flow's direction on those days only.
- rule sketch: TOM days = last business day + first 2 business days of each month. Side per market = sign of its
  63-day return at the prior close. Hold each market's day session: open (CL / NG 08:00, GC 07:20, ZN 07:20, 6E 07:20 CT)
  to 13:25 CT, no overnight. V1 all 5 markets pooled; V2 CL + NG only (least liquid, per the paper); V3 252-day trend
  instead of 63. Stop 0.5 x 14-day ATR per market. Placebo: same rule on days 10-12 of each month. Power: ~36 days a year
  x 5 markets.
- Apex: yes (all intraday). data: data/{CL,NG,GC,ZN,6E}_1min_*.csv (24 h files; roll weeks excluded as usual)

## Q018 · queued · priority 3
- who_pays: risk premium: holders of gold through the Asian / London session (less liquid hours) are paid for carrying it; plus Asian physical demand
- tier_check: master 2026-11-01, dupcheck 'gold overnight' / 'GC night': Nocturne (C) and the overnight round (D) are NQ/ES only; GC overnight untested; clear
- source: scout 2026-11-01: Blose, Gondhalekar & Kort (2018, COMEX gold front month and GLD 1985-2012: overnight returns
  significantly positive, day returns significantly negative; cited in Branch & Ma, SSRN 3259614; the basis of the
  Nocturne note, which tested NQ only). GC itself not in TIER_LIST.
- market: GC (MGC)
- mechanism: Asian and London physical buying (SGE, jewellery and central-bank demand, London AM fix) prices gold in the
  US night, while US-hours futures selling (hedgers, ETF creation / redemption) meets thin buyers; a time-zone clientele
  split, the same family as the equity overnight effect but with a physical-demand reason.
- rule sketch: V1 long GC 17:00 -> 07:15 CT (inside one Apex day), every night; V2 short GC 07:20 -> 12:25 CT, every day;
  V3 V1 only after a down US session (07:20 -> 12:25 return < 0). No stop for V1 (overnight gaps; note E30), 0.5 ATR for
  V2. Placebo: random 14-h windows; compare with GC's buy-and-hold drift over the same hours.
- Apex: yes (overnight within one Apex day). data: data/GC_1min_*.csv

## Q019 · queued · priority 2
- tier_check: master 2026-11-01, dupcheck 'ICT' / 'manipulation' / 'sweep': F 'ICT Accumulation-Manipulation-Distribution / Power of 3 on NQ' tested the London sweep of the Asia range (no direction, t -1.0); the 4H candle chain and the 8:30 news fake-out are untested; queued as a distinct test, expect weak
- who_pays: structural: traders with stop orders resting beyond the previous 4H candle's high / low; large orders fill against their stops when price runs them, then price reverses
- source: user 2026-11-01, 'If and Then price theory' sheet (ICT 4H profiling: 2AM / 6AM / 10AM EST candles; 'IF a candle manipulates THEN the next continues')
- market: NQ (MNQ); ES (MES) as V2
- mechanism: a 4H candle that takes out the prior 4H candle's high (low) and closes back inside its range has swept resting stops; the next 4H candle continues the other way.
- rule sketch (definition fixed, CT clock: 4H candles start 17:00, 21:00, 01:00, 05:00, 09:00 CT): 'manipulates' = the candle's
  high > prior candle's high and its close < prior candle's high (bearish sweep), or low < prior low and close > prior low
  (bullish). Trade the NEXT candle in the reversal direction: enter at its open, stop beyond the sweep candle's extreme
  (+1 tick), exit at that candle's close (flat by 15:55 CT). V1 NQ, only the 01:00 / 05:00 / 09:00 CT sweep candles
  (= the sheet's 2AM / 6AM / 10AM EST); V2 same on ES; V3 NQ 8:30 CT 'red folder' days (CPI, NFP, PPI, retail sales): if
  07:30-08:30 CT sweeps the 06:30-07:30 range and closes back inside, trade 08:31-09:30 CT in the reversal direction.
- Apex: yes (intraday). data: data/NQ_1min_*, data/ES_1min_*; release calendar from the NFP / CPI files used by the plan.

## Q020 · queued · priority 2
- who_pays: structural: 2x / -2x natural-gas ETFs (BOIL / KOLD, plus 3x ETNs abroad) must buy after up days and sell after down days to reset daily leverage, trading near the 13:30 CT settlement whatever the price; their size is large relative to NG volume, unlike CL's
- tier_check: scout 2026-11-02, dupcheck 'NG settlement' / 'natural gas settle' / 'BOIL': no NG settlement row (D: equity post-settlement reversal; F: CL settlement follow / fade in 'CL forced flows'); NG daily-settlement LETF flow is new; clear
- source: scout 2026-11-02: Todorov, 'Passive Funds Actively Affect Prices: Evidence from the Largest ETF Markets' (2019,
  SSRN; summary via CXO Advisory): in VIX and commodity futures incl. natural gas, the rebalancing needed to keep constant
  daily leverage is the largest of three ETF price-impact channels (roll, flows, leverage). Caution: the CL settlement
  follow / fade is already F, so the test must show NG is different (larger LETF share).
- market: NG (QG / MNG)
- mechanism: leveraged ETFs' end-of-day rebalancing demand is proportional to (leverage^2 - leverage) x AUM x the day's
  return, so on big-move days they buy (sell) into the settlement window in the move's direction, then the pressure eases.
- rule sketch: move = NG 08:00 -> 13:15 CT return; ATR = 14-day. V1 follow the move 13:16 -> 13:29 when |move| >= 0.5 ATR;
  V2 same on all days with |move| >= 0.2 ATR; V3 fade 13:31 -> 14:15 when |move| >= 0.5 ATR (pressure released). Stop
  0.3 ATR. Exclude NG expiry week (our series rolls the evening before expiry, Q011 lesson). Placebo: same windows shifted
  one hour earlier (12:16 -> 12:29 / 12:31 -> 13:15). Power: ~250 days a year (V2), ~60 a year (V1 / V3). Costs $5 + 1 tick
  a side; stop at stage 1 unless gross per trade > 2x cost.
- Apex: yes (intraday). data: data/NG_1min_*.csv (CT)
