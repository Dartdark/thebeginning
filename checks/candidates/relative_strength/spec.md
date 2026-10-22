# Candidate: Relative Strength NQ / ES (user's RelStrength_v3), intraday, long and short

**Kind:** strategy. The full rules are the PowerLanguage code `RelStrength_v3.txt` in this folder (the user's code,
unchanged): that file IS the spec. The user's research note (`Relative_Strength_research_note.pdf`) describes the
MultiCharts run (1,290 trades 2017-26, PF 1.37 before costs) and the inputs: decide 09:00 CT, |Z| >= 1.25, beta / variance
20 days, stop 0.6 x and target 1.0 x the 20-day average 08:30-15:00 range, flat 15:00 CT. Inputs were chosen by the user
on 2017-2022 (one dial at a time; the note lists the sweeps), 2023-26 kept as the out-of-sample check: NOT pre-registered,
about 12 variants looked at.

**Data / conventions:** NQ and ES continuous 1-minute bars, CT, close-stamped. Grids `scratch_data/g24.pkl` (NQ) and
`scratch_data/ge.pkl` (ES) (grid24.Grid24; rows = calendar dates, column j = bar closing at 00:00 + j min). Not
back-adjusted (all trades are inside 09:01-15:00, clear of the 03:30 / 17:00 roll jumps). Days skipped: the code's NYSE
holiday / early-close lists, plus days without NQ / ES data through 15:00. 2018-01 onward.

**Costs in trades.csv (`net`, $ per 1 NQ):** $7.25 commission + 1 tick ($5) per market or stop fill (entry, stop, 15:00
flat); target limits fill at the limit (on touch) with no slippage. Stop and target in the same minute: stop first.
Stop / target active from the 09:02 bar (MultiCharts sets them on the bar after the fill).

**trades.csv columns:** date, side (+1 / -1), net, kind (stop / target / flat), entry (09:01 open), exit, z (the signal).

**Things the maker is unsure about:** the exponential averages' start (replayed from 2017-09; the code starts at the
chart's first bar), whether MultiCharts' EWMA skips minutes where one series has no bar (the maker skips those minutes),
and the entry bar (09:01) carrying no stop.
