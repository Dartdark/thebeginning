# NQ Opening Pressure Consensus: TEST

Summary: A new raw-price entry asks whether persistent cash-open order pressure across three indices
predicts continuation in NQ. It is not Relative Strength's NQ-minus-ES excess or Twin's oscillator.
Related opening-drive/MA-agreement results were weak; cross-index pressure adds an unproven hypothesis.

1. Actor/mechanism: institutional cash-index programs and risk transfers span Nasdaq, S&P and Dow.
   Directionally persistent price paths in all three may reveal unfinished demand rather than stock-specific news.
   Actual program orders/compulsion are unobserved. This is a testable inference, not an identified forced flow.
2. Known inputs: completed 5- or 15-minute closes from08:30 to09:00CT and current exact cash opens.
   Directional efficiency=absolute net change / sum absolute bar-close increments, including open-to-first-close.
   No full-day realized trend feature. All entries are next native minute open after09:00.
3. Transmission: trade NQ alone in the common direction. ES/YM only generate contemporaneous features;
   no old strategy ledgers, copied trades, portfolio combination, fitted hedge ratio or second traded leg.
4. Data: committed NQ day/night, full-day ES/YM nativeCT minute OHLCV2018-2026. Complete first30minutes
   on all instruments, no forward fill; conflicting duplicate keys block. Prior shared15weekday ATR each symbol.
   Same data mask on controls, no paid data/credentials needed. Roll/splice distortions can affect ATR.
5. Costs/overlap: NQ$7.25RT plus1tick per market/stop fill,1point target-through. NativeMNQ$1.24RT plus
   $0.50/fill separately. Overlaps RS/Twin/VB cash momentum; no new account hedge or empty slot assumed.
6. Power: several hundred design days expected rather than a rare three-bar pattern. At500trades andSD$800,
   t6 needs roughly$215net/event; at1,000,$152. These are feasibility assumptions, not expected earnings.
7. Prior evidence: TIER_LIST opening drive t~1.7; intraday-up/down faded; MA agreement failed. RS t~4 and
   Twin t~5 use other entries; cannot count them as this strategy. Program15models plus unknown older trials.
   Sources: analysis/candidates.py opening_drive, index_ma_agreement_test.py, relative_strength_test.py,
   session_efficiency_check.py. This exact opening path/common-pressure entry has not been found.
8. Failure/risk: cash-open reversal, globally informed wrong-side liquidity, clustered NQ-plan trend losses,
   2020limit/gap execution and higher vol. Stop0.15ATR,target0.60,flat14:55,one trade/day. Native stops may gap;
   no before-breach offset. Both sides must be reported even if one fails.

TEST only2018-22 first. No change to old entry or copied trade list. Continue distinct hypotheses after failure.
